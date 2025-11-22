#!/usr/bin/env python
"""간단한 MeloTTS FastAPI 서버"""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
MELO_REPO_PATH = BACKEND_ROOT / "third_party" / "MeloTTS"
sys.path.insert(0, str(MELO_REPO_PATH))

import asyncio
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from melo.api import TTS

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
OUTPUT_DIR = BACKEND_ROOT / "tmp" / "tts_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
model = None


class TTSRequest(BaseModel):
    text: str
    speaker: str = "KR"
    speed: float = 1.0


class TTSResponse(BaseModel):
    audio_url: str


@app.on_event("startup")
async def startup():
    global model
    print("🔊 Loading Korean TTS model...")
    model = TTS(language="KR", device="cpu")
    print("✅ Model loaded!")


@app.get("/")
async def root():
    return {"status": "ok", "message": "MeloTTS Server"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/tts")
async def tts(request: TTSRequest):
    # 파일명 생성
    output_filename = f"{uuid.uuid4().hex}.wav"
    output_path = OUTPUT_DIR / output_filename

    # TTS 생성 (별도 스레드에서 실행)
    loop = asyncio.get_event_loop()
    speaker_id = model.hps.data.spk2id[request.speaker]

    await loop.run_in_executor(
        None,
        model.tts_to_file,
        request.text,
        speaker_id,
        str(output_path),
        request.speed
    )

    return {"audio_url": f"/audio/{output_filename}"}


# 정적 파일 제공
app.mount("/audio", StaticFiles(directory=str(OUTPUT_DIR)), name="audio")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting TTS server on http://0.0.0.0:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
