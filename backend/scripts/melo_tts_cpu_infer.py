#!/usr/bin/env python
"""Utility script for CPU-based MeloTTS inference.

This script loads the cloned MeloTTS library from `backend/third_party/MeloTTS`
and synthesizes a single utterance to the requested output path.  It keeps the
interface small on purpose so backend developers can quickly verify the local
TTS pipeline without spinning up the full FastAPI server.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
MELO_REPO_PATH = REPO_ROOT / "third_party" / "MeloTTS"

if not MELO_REPO_PATH.exists():
    raise RuntimeError(
        "MeloTTS repository not found. Clone it into backend/third_party/MeloTTS "
        "before running this script."
    )

# Ensure the MeloTTS package is importable without installing it globally.
sys.path.insert(0, str(MELO_REPO_PATH))

try:
    from melo.api import TTS
except ImportError as exc:  # pragma: no cover - depends on local env
    raise RuntimeError(
        "Failed to import MeloTTS. Did you install its dependencies?"
    ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MeloTTS inference on CPU")
    parser.add_argument("text", help="Text to synthesize")
    parser.add_argument(
        "--language",
        default=os.getenv("MELO_TTS_LANGUAGE", "KR"),
        help="Language code supported by MeloTTS (default: KR)",
    )
    parser.add_argument(
        "--speaker",
        default=os.getenv("MELO_TTS_SPEAKER", "KR"),
        help="Speaker id within the selected language (default: KR)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=float(os.getenv("MELO_TTS_SPEED", "1.0")),
        help="Playback speed multiplier (default: 1.0)",
    )
    parser.add_argument(
        "--device",
        default=os.getenv("MELO_TTS_DEVICE", "cpu"),
        help="Inference device, e.g. cpu/cuda/mps (default: cpu)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./melo_output.wav"),
        help="Destination wav file (default: ./melo_output.wav)",
    )
    parser.add_argument(
        "--ckpt-path",
        type=Path,
        default=_default_ckpt_path(),
        help="Optional local checkpoint path (default: MeloTTS/melo/pretrained/G_0.pth)",
    )
    return parser.parse_args()


def _default_ckpt_path() -> Optional[Path]:
    candidate = MELO_REPO_PATH / "melo" / "pretrained" / "G_0.pth"
    if candidate.exists():
        return candidate
    env_override = os.getenv("MELO_TTS_CKPT_PATH")
    return Path(env_override) if env_override else None


def synthesize(
    text: str,
    language: str,
    speaker: str,
    speed: float,
    device: str,
    output_path: Path,
    ckpt_path: Optional[Path],
) -> Path:
    """Run a single inference and return the saved path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model_kwargs = {}
    if ckpt_path is not None:
        model_kwargs["ckpt_path"] = str(ckpt_path)
    model = TTS(language=language, device=device, **model_kwargs)
    speaker_ids = model.hps.data.spk2id
    if speaker not in speaker_ids:
        available = ", ".join(sorted(speaker_ids.keys()))
        raise ValueError(
            f"Speaker '{speaker}' not available for language {language}. "
            f"Available speakers: {available}"
        )

    model.tts_to_file(text, speaker_ids[speaker], str(output_path), speed=speed)
    return output_path


def main() -> None:
    args = parse_args()
    saved_path = synthesize(
        text=args.text,
        language=args.language,
        speaker=args.speaker,
        speed=args.speed,
        device=args.device,
        output_path=args.output,
        ckpt_path=args.ckpt_path,
    )
    print(f"Saved MeloTTS audio to {saved_path}")


if __name__ == "__main__":
    main()
