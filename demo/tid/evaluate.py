import argparse
import json
from pathlib import Path

import sentencepiece as spm
import torch
from safetensors.torch import load_model
from torch.utils.data import DataLoader

from model import ModelConfig, SignTranslator
from train import as_examples, collate, evaluate, load_corpus


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("features", type=Path)
    parser.add_argument("run", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--min-tokens", type=int, default=0)
    args = parser.parse_args()
    config = ModelConfig(**json.loads((args.run / "config.json").read_text(encoding="utf-8")))
    if not 0 <= args.min_tokens < config.max_tokens - 1:
        parser.error("--min-tokens must fit the decoder window")
    torch.set_num_threads(2)
    samples = load_corpus(args.features)
    model = SignTranslator(config)
    load_model(model, args.run / "model.safetensors")
    tokenizer = spm.SentencePieceProcessor(model_file=str(args.run / "turkish.model"))
    metrics = {"min_tokens": args.min_tokens}
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "predictions.jsonl").open("w", encoding="utf-8") as file:
        for split in ("test", "conversation"):
            examples = as_examples(samples[split], tokenizer, config)
            if not examples:
                raise ValueError(f"No test clips in {split}")
            loader = DataLoader(examples, batch_size=16, collate_fn=collate)
            metrics[split] = {
                mode: evaluate(model, loader, tokenizer, torch.device("cpu"), file, split, mode, args.min_tokens)
                for mode in ("video", "shuffled", "blank")
            }
    (args.output / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics))


if __name__ == "__main__":
    main()
