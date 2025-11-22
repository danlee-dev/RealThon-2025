"""Run a local STT→LLM→TTS loop on a given wav file.

This script is for quick sanity checks. It loads the local Whisper model to
transcribe the provided audio (default: backend/tts_0000.wav), feeds the text
into Gemini with a fixed prompt, then synthesizes the response via Melo TTS and
saves the output wav file.
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import sys
from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
for path in (str(BACKEND_ROOT), str(REPO_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

load_dotenv(BACKEND_ROOT / ".env")

from clients.whisper_client import WhisperLocalClient
from clients.gemini_client import GeminiClient
from clients.melo_tts_client import MeloTTSLocalClient


DEFAULT_AUDIO = Path("/Users/heejae/Developer/RealThon-2025/backend/tts_0000.wav")
DEFAULT_OUTPUT = Path("tmp/pipeline_test.wav")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run dummy STT→LLM→TTS pipeline")
    parser.add_argument(
        "--audio",
        type=Path,
        default=DEFAULT_AUDIO,
        help=f"Input wav file (default: {DEFAULT_AUDIO})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output wav file (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--speaker",
        default="KR",
        help="Melo speaker id (default: KR)",
    )
    parser.add_argument(
        "--prompt",
        default="테스트입니다:",
        help="Override LLM prompt text",
    )
    parser.add_argument(
        "--fallback-answer",
        default="테스트",
        help="Fallback answer when LLM blocks the response",
    )
    return parser.parse_args()


async def run_pipeline(
    audio_path: Path,
    output_path: Path,
    speaker: str,
    prompt_text: str,
    fallback_answer: str,
) -> None:
    stt = WhisperLocalClient(model_size="base", device="cpu")
    transcript = await stt.transcribe(str(audio_path), language="ko")
    print("[STT]", transcript)

    llm = GeminiClient()
    prompt = f"{prompt_text}\n테스트라고 답변하세요."
    try:
        llm_response = await llm.generate(prompt, max_tokens=32, temperature=0)
        text = llm_response.strip() or fallback_answer
    except Exception as exc:  # pylint: disable=broad-except
        print("[LLM] generation failed, falling back to default.", exc)
        text = fallback_answer
    print("[LLM]", text)

    tts = MeloTTSLocalClient()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audio_url = await tts.synthesize(text=text, speaker=speaker, speed=1.0, output_path=str(output_path))
    print("[TTS] Saved to:", audio_url)


def main() -> None:
    args = parse_args()
    asyncio.run(
        run_pipeline(
            args.audio,
            args.output,
            args.speaker,
            prompt_text=args.prompt,
            fallback_answer=args.fallback_answer,
        )
    )


if __name__ == "__main__":
    main()
