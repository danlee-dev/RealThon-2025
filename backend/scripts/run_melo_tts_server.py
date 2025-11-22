#!/usr/bin/env python
"""
MeloTTS FastAPI 서버

로컬 CPU에서 MeloTTS를 실행하는 간단한 HTTP 서버입니다.
클라이언트가 POST /tts로 요청하면 음성 파일을 생성하고 URL을 반환합니다.

Usage:
    python scripts/run_melo_tts_server.py --host 0.0.0.0 --port 8001 --device cpu
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import uuid
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# MeloTTS 경로 설정
BACKEND_ROOT = Path(__file__).resolve().parents[1]
MELO_REPO_PATH = BACKEND_ROOT / "third_party" / "MeloTTS"

if not MELO_REPO_PATH.exists():
    raise RuntimeError(
        f"MeloTTS repository not found at {MELO_REPO_PATH}. "
        "Clone it with: git clone https://github.com/myshell-ai/MeloTTS.git backend/third_party/MeloTTS"
    )

sys.path.insert(0, str(MELO_REPO_PATH))

try:
    from melo.api import TTS
except ImportError as exc:
    raise RuntimeError(
        "Failed to import MeloTTS. Install dependencies with: "
        "pip install -r backend/third_party/MeloTTS/requirements.txt"
    ) from exc


# 전역 변수
app = FastAPI(title="MeloTTS Server")
models: dict[str, TTS] = {}
OUTPUT_DIR = BACKEND_ROOT / "tmp" / "tts_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class TTSRequest(BaseModel):
    text: str
    speaker: str = "KR"
    speed: float = 1.0


class TTSResponse(BaseModel):
    audio_url: str


def init_models(device: str = "cpu"):
    """TTS 모델 초기화"""
    global models
    print(f"Loading MeloTTS models on device: {device}")

    # 한국어 모델만 로드 (필요시 다른 언어 추가)
    models["KR"] = TTS(language="KR", device=device)
    print("✓ Korean model loaded")

    # 영어 모델도 로드 (선택사항)
    try:
        models["EN"] = TTS(language="EN", device=device)
        print("✓ English model loaded")
    except Exception as e:
        print(f"⚠ Failed to load English model: {e}")


@app.post("/tts", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """
    텍스트를 음성으로 변환

    Args:
        text: 음성으로 변환할 텍스트
        speaker: 화자 ID (KR, EN-US 등)
        speed: 속도 배율 (0.1 ~ 10.0)

    Returns:
        audio_url: 생성된 음성 파일의 URL
    """
    import asyncio

    try:
        # 언어 감지 (speaker로부터)
        language = request.speaker.split("-")[0] if "-" in request.speaker else request.speaker

        if language not in models:
            raise HTTPException(
                status_code=400,
                detail=f"Language '{language}' not supported. Available: {list(models.keys())}"
            )

        model = models[language]
        speaker_ids = model.hps.data.spk2id

        # 화자 ID 확인
        if request.speaker not in speaker_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Speaker '{request.speaker}' not found. Available: {list(speaker_ids.keys())}"
            )

        # 음성 생성 (동기 함수를 별도 스레드에서 실행)
        output_filename = f"{uuid.uuid4().hex}.wav"
        output_path = OUTPUT_DIR / output_filename

        # run_in_executor로 블록킹 작업을 비동기로 실행
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: model.tts_to_file(
                request.text,
                speaker_ids[request.speaker],
                str(output_path),
                speed=request.speed
            )
        )

        # URL 반환 (정적 파일 제공)
        audio_url = f"/audio/{output_filename}"

        return TTSResponse(audio_url=audio_url)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "models": list(models.keys()),
        "output_dir": str(OUTPUT_DIR)
    }


# 정적 파일 제공 (생성된 오디오)
app.mount("/audio", StaticFiles(directory=str(OUTPUT_DIR)), name="audio")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MeloTTS FastAPI Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind")
    parser.add_argument("--device", default="cpu", help="Device (cpu/cuda/mps)")
    return parser.parse_args()


def main():
    args = parse_args()

    # 모델 초기화
    init_models(device=args.device)

    # 서버 실행
    print(f"\n🚀 Starting MeloTTS server at http://{args.host}:{args.port}")
    print(f"📁 Audio files will be saved to: {OUTPUT_DIR}")
    print(f"🔊 Test: curl -X POST http://localhost:{args.port}/tts -H 'Content-Type: application/json' -d '{{\"text\": \"안녕하세요\", \"speaker\": \"KR\", \"speed\": 1.0}}'")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
