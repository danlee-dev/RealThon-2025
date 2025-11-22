from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import numpy as np

def load_timeline(path: Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def center_gaze_ratio(timeline: List[Dict[str, Any]]) -> float:
    valid = [x for x in timeline if x.get("valid")]
    if not valid:
        return 0.0
    center = sum(1 for x in valid if x.get("gaze") == "CENTER")
    return center / len(valid)

def smile_ratio(timeline, threshold=None):
    """
    Adaptive smile ratio.
    If threshold is None, use per-video adaptive threshold:
      threshold = mean + 0.5*std
    """
    valid = [x for x in timeline if x.get("valid") and x.get("smile") is not None]
    if not valid:
        return 0.0

    scores = np.array([x["smile"] for x in valid], dtype=np.float32)

    if threshold is None:
        threshold = float(np.mean(scores) + 0.5 * np.std(scores))

    smiling = np.sum(scores > threshold)
    return float(smiling / len(scores))

def nod_count(timeline: List[Dict[str, Any]], pitch_thresh_deg: float = 8.0) -> int:
    """
    Count nod events from pitch time series:
    - smooth a bit
    - count threshold-crossing up/down cycles
    """
    pitch = [x["pitch"] for x in timeline if x.get("valid") and x.get("pitch") is not None]
    if len(pitch) < 3:
        return 0

    pitch = np.array(pitch, dtype=np.float32)

    # simple smoothing (EMA-like)
    alpha = 0.2
    smoothed = [pitch[0]]
    for i in range(1, len(pitch)):
        smoothed.append(alpha * pitch[i] + (1 - alpha) * smoothed[-1])
    smoothed = np.array(smoothed)

    # detect peaks/valleys by thresholded derivative sign changes
    nods = 0
    direction = 0  # -1 down, +1 up
    last_extreme = smoothed[0]

    for v in smoothed[1:]:
        diff = v - last_extreme
        if direction <= 0 and diff > pitch_thresh_deg:
            direction = 1
            last_extreme = v
        elif direction >= 0 and diff < -pitch_thresh_deg:
            direction = -1
            last_extreme = v
            nods += 1

    return nods

def emotion_distribution(timeline: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate emotion distribution from timeline.
    If blendshapes-based emotion is available, use it.
    """
    valid = [x for x in timeline if x.get("valid")]
    emo = [x.get("emotion") for x in valid if x.get("emotion")]
    
    if not emo:
        return {}
    
    counts = {}
    for e in emo:
        counts[e] = counts.get(e, 0) + 1
    
    total = len(emo)
    distribution = {k: v / total for k, v in counts.items()}
    
    return distribution


def get_primary_emotion(timeline: List[Dict[str, Any]]) -> Optional[str]:
    """
    Get the most frequent emotion from timeline.
    """
    dist = emotion_distribution(timeline)
    if not dist:
        return None
    return max(dist.items(), key=lambda x: x[1])[0]
