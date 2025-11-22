from pathlib import Path
import re
import whisper

# Korean + English fillers
FILLERS = [
    "음", "어", "그", "저", "아", "뭐", "막",
    "uh", "um", "erm", "like", "you know"
]

def transcribe_whisper(wav_path: Path, model_size: str = "base"):
    """
    Returns Whisper transcription dict with:
      - text
      - segments (each has start/end/text)
    """
    model = whisper.load_model(model_size)
    result = model.transcribe(str(wav_path))
    return result

def compute_wpm(transcript_text: str, duration_sec: float):
    """
    Simple WPM based on whitespace token count.
    """
    words = re.findall(r"\b[\w가-힣']+\b", transcript_text)
    minutes = max(duration_sec / 60.0, 1e-6)
    return len(words) / minutes

def compute_filler_count(transcript_text: str):
    """
    Count filler occurrences using regex word boundaries where possible.
    """
    text = transcript_text.lower()
    count = 0
    for f in FILLERS:
        # Korean doesn't have strict word boundaries so simple count is ok
        if re.search(r"[가-힣]", f):
            count += text.count(f)
        else:
            count += len(re.findall(rf"\b{re.escape(f)}\b", text))
    return count
