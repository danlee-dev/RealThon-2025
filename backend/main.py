from fastapi import FastAPI
from pathlib import Path


app = FastAPI()

VIDEO_PATH = Path("video/interview.mp4")  # <- mov로 변경

@app.get("/")
def root():
    return {"ok": True}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "video_exists": VIDEO_PATH.exists(),
        "video_path": str(VIDEO_PATH.resolve())
    }