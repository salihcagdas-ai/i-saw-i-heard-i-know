import argparse
import collections
import json
import random
import re
import shutil
import statistics
import time
import unicodedata
from itertools import islice, zip_longest
from pathlib import Path

import numpy as np
import sentencepiece as spm
import torch
from safetensors.torch import load_model, save_file
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader

from model import BOS, EOS, FRAME_WIDTH, PAD, ModelConfig, SignTranslator, clip_losses, translation_loss


def normalize_text(text):
    text = unicodedata.normalize("NFC", text).translate(str.maketrans("Iİ", "ıi")).lower()
    return " ".join(re.sub(r"[^\w\s]", " ", text).split())


def load_corpus(directory):
    samples = collections.defaultdict(list)
    groups = collections.defaultdict(set)
    for path in sorted(directory.glob("*.json")):
        course = json.loads(path.read_text(encoding="utf-8"))
        split = course["split"]
        groups[course["group"]].add(split)
        with np.load(path.with_suffix(".npz"), allow_pickle=False) as arrays:
            for entry in course["segments"]:
                text = normalize_text(entry["text"])
                if not text:
                    continue
                frames = arrays[entry["key"]]
                if frames.ndim != 2 or frames.shape[1] != FRAME_WIDTH or not np.isfinite(frames).all():
                    raise ValueError(f"Invalid landmarks in {path.name}")
                samples[split].append((course["id"], frames, text))
    overlaps = [group for group, splits in groups.items() if len(splits) > 1]
    if overlaps:
        raise ValueError(f"Groups cannot span data splits: {overlaps}")
    return samples


def make_tokenizer(train, run):
    prefix = run / "turkish"
    spm.SentencePieceTrainer.train(
        sentence_iterator=(text for _, _, text in train), model_prefix=str(prefix),
        vocab_size=512, hard_vocab_limit=False, model_type="bpe", character_coverage=1.0,
        pad_id=PAD, bos_id=BOS, eos_id=EOS, unk_id=3, split_digits=True,
        num_threads=2, shuffle_input_sentence=False, minloglevel=2,
    )
    return spm.SentencePieceProcessor(model_file=str(prefix.with_suffix(".model")))


def as_examples(samples, tokenizer, config):
    results = []
    for source, frames, text in samples:
        if len(frames) > config.max_frames:
            indices = np.linspace(0, len(frames) - 1, config.max_frames).round().astype(int)
            frames = frames[indices]
        tokens = [BOS, *tokenizer.encode(text), EOS]
        if len(tokens) > config.max_tokens:
            continue
        results.append((torch.from_numpy(frames), torch.tensor(tokens), source, text))
    return results


def collate(items):
    frames, tokens, sources, references = zip(*items)
    landmark_batch = pad_sequence(frames, batch_first=True)
    token_batch = pad_sequence(tokens, batch_first=True, padding_value=PAD)
    # Bucket shapes to reuse the same MPS graphs across batches.
    landmark_padding = -landmark_batch.size(1) % 32
    token_padding = -token_batch.size(1) % 16
    return (
        torch.nn.functional.pad(landmark_batch, (0, 0, 0, landmark_padding)),
        torch.tensor([len(clip) for clip in frames]),
        torch.nn.functional.pad(token_batch, (0, token_padding), value=PAD),
        sources, references,
    )


def levenshtein(source, target):
    previous = list(range(len(target) + 1))
    for index, item in enumerate(source, start=1):
        row = [index]
        for target_index, token in enumerate(target, start=1):
            row.append(min(row[-1] + 1, previous[target_index] + 1, previous[target_index - 1] + (item != token)))
        previous = row
    return previous[-1]


def load_gloss_targets(path, training):
    annotated = json.loads(path.read_text(encoding="utf-8"))
    sources = {source for source, _, _ in training}
    sequences = {
        source: normalize_text(annotated[source]).split()
        for source in sources & annotated.keys()
    }
    frequencies = collections.Counter(token for sequence in sequences.values() for token in sequence)
    tokens = {word: index for index, word in enumerate(sorted(word for word, n in frequencies.items() if n >= 2), 2)}
    sequences = {
        source: [tokens.get(token, 1) for token in sequence]
        for source, sequence in sequences.items() if sequence
    }
    if not sequences or not tokens:
        raise ValueError("No recurring sign labels overlap the prepared training clips")
    return sequences, len(tokens) + 2


def gloss_alignment(layer, targets, sources, memory, padding):
    included = [(index, targets[source]) for index, source in enumerate(sources) if source in targets]
    if not included:
        return memory.new_zeros(())
    indices, label_lists = zip(*included)
    positions = torch.tensor(indices, device=memory.device)
    logits = layer(memory.index_select(0, positions)).log_softmax(-1).transpose(0, 1)
    lengths = (~padding.index_select(0, positions)).sum(1).cpu()
    targets = torch.tensor([token for row in label_lists for token in row])
    target_lengths = torch.tensor([len(row) for row in label_lists])
    # MPS does not implement all CTC kernels. This copy preserves the gradient.
    return torch.nn.functional.ctc_loss(
        logits.cpu(), targets, lengths, target_lengths, zero_infinity=True,
    ).to(memory.device)


@torch.inference_mode()
def validation_loss(model, loader, device):
    model.eval()
    mean = []
    for frames, lengths, labels, _, _ in loader:
        frames, lengths, labels = frames.to(device), lengths.to(device), labels.to(device)
        mean.append(translation_loss(model(frames, lengths, labels[:, :-1]), labels[:, 1:]).item())
    return statistics.mean(mean)


@torch.inference_mode()
def evaluate(model, loader, tokenizer, device, file, split, mode, min_tokens):
    model.eval()
    rng = torch.Generator().manual_seed(26)
    word_errors = words = char_errors = chars = exact = clips = 0
    for frames, lengths, _, sources, references in loader:
        if mode == "shuffled":
            for index, length in enumerate(lengths.tolist()):
                frames[index, :length] = frames[index, torch.randperm(length, generator=rng)]
        if mode == "blank":
            frames.zero_()
        generated = model.generate(frames.to(device), lengths.to(device), min_tokens)
        for source, reference, tokens in zip(sources, references, generated):
            stop = tokens.index(EOS) if EOS in tokens else len(tokens)
            hypothesis = normalize_text(tokenizer.decode(tokens[1:stop]))
            word_errors += levenshtein(reference.split(), hypothesis.split())
            char_errors += levenshtein(reference, hypothesis)
            words += len(reference.split())
            chars += len(reference)
            exact += int(reference == hypothesis)
            clips += 1
            file.write(json.dumps({
                "split": split, "mode": mode, "source": source,
                "reference": reference, "hypothesis": hypothesis,
            }, ensure_ascii=False) + "\n")
    return {
        "clips": clips, "wer": round(word_errors / words, 4), "cer": round(char_errors / chars, 4),
        "exact": exact,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("features", type=Path)
    parser.add_argument("run", type=Path)
    parser.add_argument("--epochs", type=int, default=24)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--device", default="cpu", choices=("cpu", "mps", "cuda"))
    parser.add_argument("--train-limit", type=int, help="Use this exact number of usable training clips")
    parser.add_argument("--contrastive", type=float, default=0.0)
    parser.add_argument("--min-tokens", type=int, default=0)
    parser.add_argument("--glosses", type=Path)
    parser.add_argument("--gloss-weight", type=float, default=0.3)
    parser.add_argument("--patience", type=int, default=6)
    parser.add_argument("--initialize-from", type=Path)
    parser.add_argument("--learning-rate", type=float, default=4e-4)
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1 or args.contrastive < 0:
        parser.error("Expected positive --epochs and --batch-size and nonnegative --contrastive")
    if not 0 <= args.min_tokens < ModelConfig.max_tokens - 1:
        parser.error("--min-tokens must fit the decoder window")
    if args.gloss_weight < 0:
        parser.error("--gloss-weight must be nonnegative")
    if args.patience < 1 or args.learning_rate <= 0:
        parser.error("Expected positive --patience and --learning-rate")
    if args.train_limit is not None and args.train_limit < 1:
        parser.error("--train-limit must be positive")
    if args.device == "cuda" and not torch.cuda.is_available():
        parser.error("CUDA is unavailable in this PyTorch environment")
    random.seed(26)
    torch.manual_seed(26)
    torch.set_num_threads(3)
    samples = load_corpus(args.features)
    if not all(samples[name] for name in ("train", "dev", "test", "conversation")):
        raise ValueError("The run requires training, validation, held-out video and conversation samples")
    if args.train_limit is not None and len(samples["train"]) < args.train_limit:
        raise ValueError(f"Only {len(samples['train'])} training clips for --train-limit {args.train_limit}")
    args.run.mkdir(parents=True, exist_ok=False)
    if args.initialize_from:
        config = ModelConfig(**json.loads((args.initialize_from / "config.json").read_text(encoding="utf-8")))
        for name in ("turkish.model", "turkish.vocab"):
            shutil.copyfile(args.initialize_from / name, args.run / name)
        tokenizer = spm.SentencePieceProcessor(model_file=str(args.run / "turkish.model"))
    else:
        tokenizer = make_tokenizer(samples["train"], args.run)
        config = ModelConfig(tokenizer.vocab_size())
    examples = {name: as_examples(split, tokenizer, config) for name, split in samples.items()}
    if not all(examples.values()):
        raise ValueError("A split has no valid tokenized clips")
    if args.train_limit is not None:
        by_video = collections.defaultdict(list)
        for example in examples["train"]:
            by_video[example[2]].append(example)
        if len(examples["train"]) < args.train_limit:
            raise ValueError(f"Only {len(examples['train'])} usable training clips for --train-limit {args.train_limit}")
        balanced = (
            example for round_of_clips in zip_longest(*by_video.values())
            for example in round_of_clips if example is not None
        )
        examples["train"] = list(islice(balanced, args.train_limit))
    print(json.dumps({"clips": {name: len(split) for name, split in examples.items()}, "device": args.device}), flush=True)
    loaders = {
        name: DataLoader(
            split, batch_size=args.batch_size, shuffle=name == "train", collate_fn=collate,
            generator=torch.Generator().manual_seed(26),
        )
        for name, split in examples.items()
    }
    device = torch.device(args.device)
    model = SignTranslator(config).to(device)
    if args.initialize_from:
        load_model(model, args.initialize_from / "model.safetensors")
    (args.run / "config.json").write_text(json.dumps(model.configuration()), encoding="utf-8")
    parameters = list(model.parameters())
    gloss_head = None
    if args.glosses:
        glosses, label_count = load_gloss_targets(args.glosses, samples["train"])
        gloss_head = torch.nn.Linear(config.width, label_count).to(device)
        parameters.extend(gloss_head.parameters())
        print(json.dumps({"training_clips_with_glosses": len(glosses), "gloss_classes": label_count}), flush=True)
    optimizer = torch.optim.AdamW(parameters, lr=args.learning_rate, weight_decay=0.02)
    schedule = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epochs, eta_min=args.learning_rate / 10,
    )
    best, best_epoch = float("inf"), 0
    if args.initialize_from:
        best = validation_loss(model, loaders["dev"], device)
        shutil.copyfile(args.initialize_from / "model.safetensors", args.run / "model.safetensors")
        print(json.dumps({"initialized_validation_loss": round(best, 4)}), flush=True)
    for epoch in range(1, args.epochs + 1):
        start = time.monotonic()
        model.train()
        losses = []
        for frames, lengths, labels, sources, references in loaders["train"]:
            frames, lengths, labels = frames.to(device), lengths.to(device), labels.to(device)
            points = frames.reshape(*frames.shape[:2], -1, 4)
            points[..., :3] += 0.015 * torch.randn_like(points[..., :3]) * points[..., 3:4]
            optimizer.zero_grad(set_to_none=True)
            decoder_input, target = labels[:, :-1], labels[:, 1:]
            memory, padding = model.encode(frames, lengths)
            positive = clip_losses(model.decode(decoder_input, memory, padding), target)
            loss = positive.mean()
            if gloss_head is not None:
                loss = loss + args.gloss_weight * gloss_alignment(gloss_head, glosses, sources, memory, padding)
            if args.contrastive > 0 and len(frames) > 1:
                offset = random.randrange(1, len(frames))
                unmatched = torch.tensor(
                    [text != references[(index - offset) % len(frames)] for index, text in enumerate(references)],
                    device=device,
                )
                negative = clip_losses(model(frames.roll(offset, 0), lengths.roll(offset, 0), decoder_input), target)
                margin = torch.relu(0.4 + positive - negative) * unmatched
                loss = loss + args.contrastive * margin.mean()
            if not torch.isfinite(loss):
                raise ValueError("The model produced a non-finite training loss")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(parameters, 1.0)
            optimizer.step()
            losses.append(loss.item())
        schedule.step()
        score = validation_loss(model, loaders["dev"], device)
        if score < best:
            best, best_epoch = score, epoch
            checkpoint = args.run / "model.next.safetensors"
            save_file(
                {name: weight.detach().cpu().contiguous() for name, weight in model.state_dict().items()},
                checkpoint,
            )
            checkpoint.replace(args.run / "model.safetensors")
        print(json.dumps({
            "epoch": epoch, "train_loss": round(statistics.mean(losses), 4), "validation_loss": round(score, 4),
            "seconds": round(time.monotonic() - start, 2),
        }), flush=True)
        if epoch - best_epoch >= args.patience:
            break
    load_model(model, args.run / "model.safetensors")
    evaluation_device = torch.device("cpu")
    model.to(evaluation_device)
    metrics = {"best_epoch": best_epoch, "min_tokens": args.min_tokens}
    with (args.run / "predictions.jsonl").open("w", encoding="utf-8") as file:
        for split in ("test", "conversation"):
            metrics[split] = {
                mode: evaluate(model, loaders[split], tokenizer, evaluation_device, file, split, mode, args.min_tokens)
                for mode in ("video", "shuffled", "blank")
            }
    (args.run / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics), flush=True)


if __name__ == "__main__":
    main()
