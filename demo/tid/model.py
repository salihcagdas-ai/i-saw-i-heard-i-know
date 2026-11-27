from dataclasses import asdict, dataclass

import torch
from torch import nn
from torch.nn import functional as F


PAD, BOS, EOS = 0, 1, 2
FRAME_WIDTH = 340


@dataclass(frozen=True)
class ModelConfig:
    vocab_size: int
    width: int = 128
    heads: int = 4
    layers: int = 2
    max_frames: int = 192
    max_tokens: int = 96


class SignTranslator(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        width = config.width
        self.input = nn.Sequential(nn.Linear(FRAME_WIDTH, width), nn.LayerNorm(width), nn.GELU())
        self.temporal = nn.Conv1d(width, width, kernel_size=5, stride=2, padding=2)
        self.frame_position = nn.Embedding((config.max_frames + 1) // 2, width)
        self.embedding = nn.Embedding(config.vocab_size, width, padding_idx=PAD)
        self.text_position = nn.Embedding(config.max_tokens, width)
        args = dict(
            d_model=width, nhead=config.heads, dim_feedforward=width * 3,
            dropout=0.15, activation="gelu", batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(**args), config.layers, norm=nn.LayerNorm(width),
            enable_nested_tensor=False,
        )
        self.decoder = nn.TransformerDecoder(
            nn.TransformerDecoderLayer(**args), config.layers, norm=nn.LayerNorm(width),
        )
        self.output = nn.Linear(width, config.vocab_size)

    def encode(self, frames, lengths):
        input_valid = torch.arange(frames.size(1), device=frames.device)[None, :] < lengths[:, None]
        hidden = self.input(frames) * input_valid.unsqueeze(-1)
        hidden = self.temporal(hidden.transpose(1, 2)).transpose(1, 2)
        positions = torch.arange(hidden.size(1), device=hidden.device)
        padding = positions[None, :] >= ((lengths[:, None] + 1) // 2)
        return self.encoder(hidden + self.frame_position(positions), src_key_padding_mask=padding), padding

    def decode(self, tokens, memory, padding):
        positions = torch.arange(tokens.size(1), device=tokens.device)
        target = self.embedding(tokens) + self.text_position(positions)
        causal = positions[None, :] > positions[:, None]
        hidden = self.decoder(
            target, memory, tgt_mask=causal, tgt_key_padding_mask=tokens.eq(PAD),
            memory_key_padding_mask=padding,
        )
        return self.output(hidden)

    def forward(self, frames, lengths, tokens):
        return self.decode(tokens, *self.encode(frames, lengths))

    @torch.inference_mode()
    def generate(self, frames, lengths, min_tokens=0):
        memory, padding = self.encode(frames, lengths)
        tokens = torch.full((frames.size(0), 1), BOS, device=frames.device)
        complete = torch.zeros(frames.size(0), dtype=torch.bool, device=frames.device)
        for _ in range(self.config.max_tokens - 1):
            logits = self.decode(tokens, memory, padding)[:, -1]
            logits[:, :EOS] = -torch.inf
            if tokens.size(1) <= min_tokens:
                logits[:, EOS] = -torch.inf
            next_token = torch.where(complete, EOS, logits.argmax(-1))
            tokens = torch.cat((tokens, next_token[:, None]), dim=1)
            complete |= next_token.eq(EOS)
            if complete.all():
                break
        return tokens.cpu().tolist()

    def configuration(self):
        return asdict(self.config)


def clip_losses(logits, labels):
    token_loss = F.cross_entropy(
        logits.transpose(1, 2), labels, ignore_index=PAD, label_smoothing=0.05, reduction="none",
    )
    return token_loss.sum(1) / labels.ne(PAD).sum(1).clamp_min(1)


def translation_loss(logits, labels):
    return clip_losses(logits, labels).mean()
