from fastapi import FastAPI
from pathlib import Path
import soundfile as sf

from pipeline.video_io import extract_frames_opencv, extract_audio_ffmpeg
from pipeline.vision_mediapipe import build_timeline_from_frames, save_timeline
from pipeline.metrics import (
    center_gaze_ratio, smile_ratio, nod_count, emotion_distribution
)
from pipeline.audio_analysis import transcribe_whisper, compute_wpm, compute_filler_count



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


def generate_feedback(m: dict):
    fb = []

    # ---- gaze ----
    if m["center_gaze_ratio"] >= 0.8:
        fb.append(f"카메라 응시 비율이 {m['center_gaze_ratio']:.0%}로 매우 안정적이다. 정면 시선 유지가 잘 된다.")
    elif m["center_gaze_ratio"] >= 0.5:
        fb.append(f"카메라 응시 비율이 {m['center_gaze_ratio']:.0%}로 대체로 양호하다. 핵심 답변 구간에서 조금 더 유지하면 좋다.")
    else:
        fb.append(f"카메라 응시 비율이 {m['center_gaze_ratio']:.0%}로 낮다. 정면 시선을 더 의식해보면 신뢰감이 올라간다.")

    # ---- smile ----
    if m["smile_ratio"] >= 0.3:
        fb.append(f"미소/긍정 표정 비율이 {m['smile_ratio']:.0%}로 자연스럽다. 친근한 인상을 준다.")
    elif m["smile_ratio"] >= 0.1:
        fb.append(f"미소 비율이 {m['smile_ratio']:.0%}로 약간 적을 수 있다. 시작/마무리에서 가볍게 웃어보면 좋다.")
    else:
        fb.append(f"미소 비율이 {m['smile_ratio']:.0%}로 낮다. 표정이 딱딱하게 보일 수 있어 의도적으로 부드러운 표정을 넣어보자.")

    # ---- nod ----
    if m["nod_count"] == 0:
        fb.append("고개 끄덕임이 거의 감지되지 않는다. 공감/리스닝 제스처가 약해 보일 수 있다.")
    elif m["nod_count"] <= 2:
        fb.append("끄덕임이 과하지 않고 적절하다. 경청하는 인상을 준다.")
    else:
        fb.append("끄덕임이 많은 편이다. 과도하면 불안해 보일 수 있으니 속도를 조금 줄여도 좋다.")

    # ---- speech ----
    if m["wpm"] > 190:
        fb.append(f"말 속도가 WPM {m['wpm']:.0f}로 빠른 편이다. 문장 사이에 짧은 호흡을 넣어 전달력을 높여라.")
    elif m["wpm"] < 100:
        fb.append(f"말 속도가 WPM {m['wpm']:.0f}로 느린 편이다. 핵심 문장은 조금 더 자신 있게 속도를 줘도 좋다.")
    else:
        fb.append(f"말 속도(WPM {m['wpm']:.0f})가 안정적이다. 듣기 편한 템포다.")

    if m["filler_count"] > 6:
        fb.append(f"필러(음/어/uh 등)가 {m['filler_count']}회로 잦다. 답변 전 1초만 생각하고 말하면 훨씬 줄어든다.")
    else:
        fb.append(f"필러 사용({m['filler_count']}회)이 과도하지 않다. 전반적으로 유창하다.")

    return fb


@app.post("/api/analyze")
def analyze():
    # 1) frames
    frames = extract_frames_opencv(
        VIDEO_PATH, fps=5.0, out_dir=Path("artifacts/frames")
    )

    # 2) vision timeline
    timeline = build_timeline_from_frames(frames)
    save_timeline(timeline, Path("artifacts/timeline.json"))

    # 3) audio
    wav = extract_audio_ffmpeg(VIDEO_PATH, Path("artifacts/audio.wav"))
    audio, sr = sf.read(str(wav))
    duration_sec = len(audio) / sr
    stt = transcribe_whisper(wav, model_size="base")
    text = stt["text"]

    # 4) metrics (smile auto-threshold)
    metrics = {
        "center_gaze_ratio": center_gaze_ratio(timeline),
        "smile_ratio": smile_ratio(timeline, threshold=None),
        "nod_count": nod_count(timeline),
        "emotion_distribution": emotion_distribution(timeline),
        "wpm": compute_wpm(text, duration_sec),
        "filler_count": compute_filler_count(text),
    }

    # 5) feedback
    feedback = generate_feedback(metrics)

    return {**metrics, "feedback": feedback}