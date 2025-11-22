#video analyze
(generate virtual environment)
pip install -r requirements.txt
brew install ffmpeg
ffmpeg -version

#mediapipe python 버전 문제
mediapipie: brew install python@3.12
(Python 3.9~3.12까지만 휠이 제공/테스트)

# RealThon-2025 Backend – Nonverbal Interview Analysis Pipeline (MVP)

This README documents the backend pipeline we built so far for analyzing interview videos at ~5 FPS (configurable), extracting nonverbal cues (gaze, smile, head motion) and verbal cues (WPM, filler words) and returning metrics + feedback through a FastAPI endpoint.

> **Current status:** End-to-end MVP working on macOS with a local virtual environment named `bevenv`.  
> You can call `/api/analyze` and receive JSON including `center_gaze_ratio`, `smile_ratio` (adaptive threshold), `nod_count`, `wpm`, `filler_count`, and rule-based feedback.

---

## 0. Project structure (current)

```
backend/
  main.py
  requirements.txt
  bevenv/                 # local venv (not committed)
  video/
    interview.mp4         # input video (with audio)
  artifacts/
    frames/               # extracted frames at 5 FPS
      000000.jpg
      ...
    audio.wav             # extracted mono 16k WAV
    timeline.json         # per-frame vision timeline
  pipeline/
    __init__.py
    video_io.py           # frame/audio extraction helpers
    vision_mediapipe.py   # FaceMesh + headpose + gaze + smile
    audio_analysis.py     # Whisper STT + WPM + filler
    metrics.py            # aggregated metrics
```

---

## 1. Environment setup (macOS)

### 1.1 Create virtual environment `bevenv`
From `backend/`:

```bash
python3 -m venv bevenv
source bevenv/bin/activate
```

If you see `((bevenv) )` in your shell prompt, it usually means you activated venv **inside another already-activated environment** (e.g., conda base).  
To fix, deactivate the outer one first:

```bash
deactivate   # if in venv
conda deactivate  # if in conda
source bevenv/bin/activate
```

### 1.2 Install dependencies

**Important note:** `mediapipe` does not currently publish wheels for Python 3.13.  
Use Python 3.11–3.12 for this project.

```bash
pip install -r requirements.txt
```

Example `requirements.txt` we used:

```txt
fastapi
uvicorn
opencv-python
numpy
python-dotenv
mediapipe
openai-whisper
soundfile
```

---

## 2. Step-by-step pipeline

### Overview

1. **Video I/O**
   - Extract frames at `fps=5.0` using OpenCV
   - Extract audio to `artifacts/audio.wav` (mono, 16 kHz) using ffmpeg
2. **Vision analysis (per frame)**
   - MediaPipe FaceMesh landmarks
   - Head pose (yaw/pitch/roll) via solvePnP
   - Smile proxy via mouth width / interocular distance
   - Gaze estimation:
     - Iris-based method was too stable (ratio std ~0.01)
     - Fallback to yaw-based gaze classification
3. **Audio analysis**
   - Whisper STT
   - Compute WPM
   - Count filler words
4. **Metrics aggregation**
5. **Rule-based feedback generation**
6. **FastAPI endpoint** returns JSON

---

## 3. Video I/O (implemented)

### 3.1 `pipeline/video_io.py`

Key helpers:

- `extract_frames_opencv(video_path, fps, out_dir)`
- `extract_audio_ffmpeg(video_path, wav_out)`

**Frames extraction behavior**
- Uses OpenCV `VideoCapture`
- Saves frames as JPG in `artifacts/frames/`
- Returns a list of `(timestamp_sec, frame_path)`

**Audio extraction behavior**
- Uses ffmpeg:
  - `-vn` (no video)
  - `-ac 1` mono
  - `-ar 16000` 16k sampling
- If the input has **no audio stream**, ffmpeg errors. We fixed by re-downloading a mp4 with audio.

### 3.2 Manual test

```bash
python - <<'PY'
from pathlib import Path
from pipeline.video_io import extract_frames_opencv, extract_audio_ffmpeg

video = Path("video/interview.mp4")

frames = extract_frames_opencv(video, fps=5.0, out_dir=Path("artifacts/frames"))
print("num_frames:", len(frames))
print("first frame:", frames[0])

wav = extract_audio_ffmpeg(video, Path("artifacts/audio.wav"))
print("wav:", wav, "exists:", wav.exists())
PY
```

---

## 4. Vision analysis (implemented)

### 4.1 Why these landmark indices?

These are **fixed MediaPipe FaceMesh landmark IDs**.  
They refer to the same anatomical locations across *all* videos and people (not video-specific).

```python
# Mouth corners / lips
MOUTH_LEFT = 61
MOUTH_RIGHT = 291
LIP_UP = 13
LIP_DOWN = 14

# Eye corners
R_EYE_OUTER = 33
R_EYE_INNER = 133
L_EYE_INNER = 362
L_EYE_OUTER = 263

# Iris landmarks (refine_landmarks=True)
LEFT_IRIS  = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

# Head pose indices
POSE_IDXS = [1, 152, 33, 263, 61, 291]
```

### 4.2 `pipeline/vision_mediapipe.py` – core logic

**Per-frame output dataclass**

```python
@dataclass
class FrameResult:
    t: float
    valid: bool
    gaze: Optional[str]   # LEFT/CENTER/RIGHT
    smile: Optional[float]
    yaw: Optional[float]
    pitch: Optional[float]
    roll: Optional[float]
```

**Head pose**
- Uses 6 canonical 3D points + solvePnP
- Outputs yaw/pitch/roll in degrees
- **Angle wrapping** added to keep pitch in human-friendly range

```python
yaw_deg   = wrap_angle(yaw_deg)
pitch_deg = wrap_angle(pitch_deg)
roll_deg  = wrap_angle(roll_deg)

if pitch_deg < -90: pitch_deg += 180
elif pitch_deg > 90: pitch_deg -= 180
```

**Smile proxy**
- Uses normalized mouth width:
  - `mouth_width / interocular_distance`
- Lightly gated by lip opening so closed lips dampen smile score

**Gaze estimation history**
1. Iris-based ratio initially:
   - avg_ratio std ~0.01, min/max ~0.48–0.55
   - Could not reliably separate LEFT/RIGHT
2. **Yaw-based fallback** (current)
   - If yaw in ±8° → CENTER
   - yaw > +8° → RIGHT
   - yaw < −8° → LEFT

### 4.3 Build timeline

```bash
python - <<'PY'
from pathlib import Path
from pipeline.video_io import extract_frames_opencv
from pipeline.vision_mediapipe import build_timeline_from_frames, save_timeline

video = Path("video/interview.mp4")
frames = extract_frames_opencv(video, fps=5.0, out_dir=Path("artifacts/frames"))
timeline = build_timeline_from_frames(frames)
save_timeline(timeline, Path("artifacts/timeline.json"))

print("timeline_len:", len(timeline))
print("first:", timeline[0])
print("last:", timeline[-1])
PY
```

Example output:

```json
{
  "t": 0.0,
  "valid": true,
  "gaze": "CENTER",
  "smile": 0.4167,
  "yaw": 0.14,
  "pitch": 81.33,
  "roll": -2.48
}
```

---

## 5. Audio analysis (implemented)

### 5.1 `pipeline/audio_analysis.py`

Functions:

- `transcribe_whisper(wav_path, model_size="base")`
- `compute_wpm(transcript_text, duration_sec)`
- `compute_filler_count(transcript_text)`

**Filler list**
- Korean: `"음", "어", "그", ...`
- English: `"uh", "um", "like", ...`

### 5.2 Manual test

```bash
python - <<'PY'
from pathlib import Path
import soundfile as sf
from pipeline.audio_analysis import transcribe_whisper, compute_wpm, compute_filler_count

wav = Path("artifacts/audio.wav")
audio, sr = sf.read(str(wav))
duration_sec = len(audio) / sr
print("duration_sec:", duration_sec)

stt = transcribe_whisper(wav, model_size="base")
text = stt["text"]
print("text_snippet:", text[:200])

print("wpm:", compute_wpm(text, duration_sec))
print("filler_count:", compute_filler_count(text))
PY
```

> Whisper CPU warning `FP16 is not supported on CPU` is expected; it uses FP32 on CPU.

---

## 6. Metrics aggregation (implemented)

### 6.1 `pipeline/metrics.py`

Metrics:

- `center_gaze_ratio`
- `smile_ratio` (**adaptive threshold**)
- `nod_count`
- `emotion_distribution` (placeholder for now)

**center_gaze_ratio**
```python
center_gaze_ratio = (# CENTER frames) / (# valid frames)
```

**smile_ratio (adaptive)**
```python
threshold = mean(smile_scores) + 0.5 * std(smile_scores)
smile_ratio = (# frames with score > threshold) / (# valid smile frames)
```

**nod_count**
- Uses smoothed pitch series
- Counts large up/down threshold-crossing cycles

### 6.2 Example metrics output

```json
{
  "center_gaze_ratio": 0.9341,
  "smile_ratio_auto": 0.3533,
  "nod_count": 1,
  "wpm": 119.1,
  "filler_count": 4
}
```

---

## 7. FastAPI integration (implemented)

### 7.1 `main.py`

Endpoints:
- `GET /health`
- `POST /api/analyze`

`/api/analyze` flow:
1. Extract frames (5 FPS)
2. Build + save timeline
3. Extract audio
4. Whisper transcription
5. Compute metrics
6. Generate rule-based feedback
7. Return JSON

### 7.2 Run server

```bash
uvicorn main:app --reload
```

### 7.3 Call API

```bash
curl -X POST http://127.0.0.1:8000/api/analyze
```

**Example response**
```json
{
  "center_gaze_ratio": 0.9341,
  "smile_ratio": 0.3533,
  "nod_count": 1,
  "emotion_distribution": {},
  "wpm": 119.1,
  "filler_count": 4,
  "feedback": [
    "카메라 응시 비율이 93%로 매우 안정적이다. 정면 시선 유지가 잘 된다.",
    "미소/긍정 표정 비율이 35%로 자연스럽다. 친근한 인상을 준다.",
    "끄덕임이 과하지 않고 적절하다. 경청하는 인상을 준다.",
    "말 속도(WPM 119)가 안정적이다. 듣기 편한 템포다.",
    "필러 사용(4회)이 과도하지 않다. 전반적으로 유창하다."
  ]
}
```

---

## 8. Known limitations (current)

1. **Emotion distribution** is empty:
   - We have not integrated a FER model yet.
2. **Hand gestures** not integrated yet:
   - Need MediaPipe Hand Landmarker / Gesture Recognizer.
3. **Gaze using yaw fallback**:
   - Works for interview-style frontal videos.
   - For more dynamic videos, may want hybrid iris+yaw or re-calibration.
4. **Speed**
   - Whisper on CPU can be slow for long videos.
5. **Threshold tuning**
   - Smile uses adaptive threshold per video (good for generalization).
   - Nod pitch threshold may need slight tuning depending on camera angle.

---

## 9. Next steps (planned)

1. **Emotion model**
   - Integrate lightweight FER to fill `emotion_distribution` and per-frame `emotion`.
2. **Hand gesture analysis**
   - Use MediaPipe Hands / Gesture Recognizer.
   - Produce metrics such as `hand_gesture_rate`, `self-touch_count`, etc.
3. **Prosody features**
   - Pitch range, intensity, pause ratio.
4. **UI**
   - Render timeline plots and highlight weak segments.
5. **FPS parameterization**
   - Make FPS configurable per request (`10fps` planned).
6. **Batch processing**
   - Analyze multiple videos in a directory and output CSV summary.

---

## 10. Troubleshooting

### mediapipe install fails
- Ensure Python <= 3.12
- Recreate venv with correct python

### ffmpeg says “Output file does not contain any stream”
- Input has no audio track
- Re-download video with audio (mp4)

### `asdict()` TypeError
- Happens if `analyze_frame` returns non-dataclass
- Ensure `analyze_frame` returns `FrameResult(...)`

---

If you want this README to be expanded with the new FER/hand-gesture additions, we will append sections 4/6/7 accordingly.
