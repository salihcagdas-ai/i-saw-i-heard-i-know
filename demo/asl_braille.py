"""Tek fotoğraftan ASL parmak alfabesi harfi ve Unicode Braille hücresi."""

import argparse
import string
import sys
from pathlib import Path

import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision
from PIL import Image, ImageOps


DEFAULT_MODEL = (
    Path(__file__).resolve().parents[1] / ".demo-cache" / "gesture_recognizer_asl_0.task"
)
BRAILLE = dict(zip(string.ascii_uppercase, "⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚⠅⠇⠍⠝⠕⠏⠟⠗⠎⠞⠥⠧⠺⠭⠽⠵", strict=True))
STATIC_LETTERS = set(string.ascii_uppercase) - {"J", "Z"}


def recognize_photo(recognizer, path: Path, min_score: float) -> str:
    with Image.open(path) as source:
        photo = ImageOps.exif_transpose(source).convert("RGBA")
        white = Image.new("RGBA", photo.size, "white")
        rgb = Image.alpha_composite(white, photo).convert("RGB")

    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(rgb))
    result = recognizer.recognize(image)
    if not result.hand_landmarks:
        return "El bulunamadı."
    if len(result.hand_landmarks) > 1:
        return "Birden fazla el bulundu. Tek eli kadraja al."
    if not result.gestures or not result.gestures[0]:
        return "Harf tanınamadı."

    candidate = max(result.gestures[0], key=lambda category: category.score)
    label = (candidate.category_name or "").upper()
    if label not in STATIC_LETTERS:
        return "Harf tanınamadı."
    if candidate.score < min_score:
        return f"Model skoru düşük (%{candidate.score * 100:.1f})."

    return f"{label} → {BRAILLE[label]} (model skoru %{candidate.score * 100:.1f})"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("photos", nargs="+", type=Path, help="Her fotoğrafta bir sabit harf")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="ASL .task dosyası")
    parser.add_argument("--min-score", type=float, default=0.75, help="0–1 arası kabul eşiği")
    args = parser.parse_args()
    if not 0.0 <= args.min_score <= 1.0:
        parser.error("--min-score 0 ile 1 arasında olmalı.")
    if not args.model.is_file():
        parser.error(f"Model dosyası bulunamadı. Kurulum adımları README.md içinde. {args.model}")

    try:
        options = vision.GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_buffer=args.model.read_bytes()),
            running_mode=vision.RunningMode.IMAGE,
            num_hands=2,
        )
        recognizer = vision.GestureRecognizer.create_from_options(options)
    except (OSError, RuntimeError, ValueError) as error:
        parser.error(f"Model açılamadı. {error}")

    exit_code = 0
    with recognizer:
        for photo in args.photos:
            try:
                output = recognize_photo(recognizer, photo, args.min_score)
            except (OSError, ValueError, RuntimeError, Image.DecompressionBombError) as error:
                print(f"{photo.name} · Görüntü işlenemedi. {error}", file=sys.stderr)
                exit_code = 1
                continue
            print(f"{photo.name} · {output}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
