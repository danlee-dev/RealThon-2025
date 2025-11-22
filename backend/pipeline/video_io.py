import subprocess
from pathlib import Path
import cv2

def extract_frames_opencv(video_path: Path, fps: float, out_dir: Path):
    """
    Extract frames at target fps using OpenCV.
    Saves frames as JPG into out_dir.
    Returns list of (timestamp_sec, frame_path).
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    src_fps = cap.get(cv2.CAP_PROP_FPS)
    if src_fps <= 0:
        raise RuntimeError("Source FPS not detected.")

    step = max(int(round(src_fps / fps)), 1)

    frames = []
    idx = 0
    saved = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if idx % step == 0:
            t = idx / src_fps
            frame_path = out_dir / f"{saved:06d}.jpg"
            cv2.imwrite(str(frame_path), frame)
            frames.append((t, frame_path))
            saved += 1

        idx += 1

    cap.release()
    return frames

def extract_audio_ffmpeg(video_path: Path, out_wav: Path):
    """
    Extract mono 16k wav for Whisper.
    """
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn", "-ac", "1", "-ar", "16000",
        str(out_wav)
    ]
    subprocess.run(cmd, check=True)
    return out_wav
