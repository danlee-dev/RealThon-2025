#!/usr/bin/env python
"""MeloTTS FastAPI 서버 - startup 블록 없이"""

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
MELO_REPO_PATH = BACKEND_ROOT / "third_party" / "MeloTTS"
sys.path.insert(0, str(MELO_REPO_PATH))

import asyncio
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경변수로 OUTPUT_DIR 설정 (도커용)
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(BACKEND_ROOT / "tmp" / "tts_outputs")))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 모델은 나중에 로드
_model = None


def get_model():
    """Lazy loading - 첫 요청 때 모델 로드"""
    global _model
    if _model is None:
        print("🔊 Loading TTS model...")
        try:
            from melo.api import TTS
            _model = TTS(language="KR", device="cpu")
            print("✅ Model loaded!")
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    return _model


class TTSRequest(BaseModel):
    text: str
    speaker: str = "KR"
    speed: float = 1.0


@app.get("/")
async def root():
    return {"status": "ok", "message": "MeloTTS Server"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/tts")
async def tts(request: TTSRequest):
    try:
        model = get_model()

        # 파일명 생성
        output_filename = f"{uuid.uuid4().hex}.wav"
        output_path = OUTPUT_DIR / output_filename

        # speaker ID 가져오기
        speaker_ids = model.hps.data.spk2id
        if request.speaker not in speaker_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Speaker '{request.speaker}' not found. Available: {list(speaker_ids.keys())}"
            )

        speaker_id = speaker_ids[request.speaker]

        # TTS 생성 (별도 스레드)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            model.tts_to_file,
            request.text,
            speaker_id,
            str(output_path),
            request.speed
        )

        return {"audio_url": f"/audio/{output_filename}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


# 정적 파일
app.mount("/audio", StaticFiles(directory=str(OUTPUT_DIR)), name="audio")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8004"))
    print(f"🚀 Starting TTS server on http://0.0.0.0:{port}")
    print("⚠️  Model will load on first request (lazy loading)")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
