from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
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
    Returns: (ratio, threshold_used)
    """
    valid = [x for x in timeline if x.get("valid") and x.get("smile") is not None]
    if not valid:
        return 0.0, None

    scores = np.array([x["smile"] for x in valid], dtype=np.float32)

    if threshold is None:
        threshold = float(np.mean(scores) + 0.5 * np.std(scores))

    smiling = np.sum(scores > threshold)
    return float(smiling / len(scores)), threshold

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


def compute_pose_outlier_ratio(timeline: List[Dict[str, Any]]) -> float:
    """
    Compute proportion of frames with physically implausible head poses.
    Heuristic: extreme yaw/pitch/roll values likely indicate solvePnP instability.
    """
    valid = [x for x in timeline if x.get("valid")]
    if not valid:
        return 0.0
    
    outliers = 0
    for frame in valid:
        yaw = frame.get("yaw")
        pitch = frame.get("pitch")
        roll = frame.get("roll")
        
        # Skip if pose data missing
        if yaw is None or pitch is None or roll is None:
            continue
        
        # Flag as outlier if any angle exceeds reasonable bounds
        # Typical human head pose: yaw ±90°, pitch ±60°, roll ±45°
        # Use more conservative thresholds to catch solvePnP failures
        if abs(yaw) > 60 or abs(pitch) > 45 or abs(roll) > 40:
            outliers += 1
    
    return outliers / len(valid) if valid else 0.0


def compute_gaze_confidence(timeline: List[Dict[str, Any]]) -> Optional[float]:
    """
    Placeholder for gaze confidence.
    Currently MediaPipe doesn't provide explicit confidence scores for gaze,
    but we can infer from landmark detection stability.
    Returns average "confidence" proxy (1.0 if valid, 0.0 otherwise).
    """
    if not timeline:
        return None
    valid_count = sum(1 for x in timeline if x.get("valid"))
    return valid_count / len(timeline)


def compute_metadata(
    timeline: List[Dict[str, Any]],
    fps_analyzed: float,
    smile_threshold: Optional[float],
    nod_pitch_threshold: float,
    whisper_model_size: str = "base",
    duration_sec: Optional[float] = None
) -> Dict[str, Any]:
    """
    Compute comprehensive metadata for metrics transparency.
    
    Args:
        timeline: Full frame-by-frame analysis results
        fps_analyzed: FPS used for frame extraction
        smile_threshold: Threshold used for smile detection (or None if adaptive)
        nod_pitch_threshold: Pitch delta threshold for nod detection
        whisper_model_size: Whisper model size used for STT
        duration_sec: Video duration in seconds
    
    Returns:
        Dictionary with all metadata fields
    """
    valid = [x for x in timeline if x.get("valid")]
    
    metadata = {
        "fps_analyzed": fps_analyzed,
        "frame_count_total": len(timeline),
        "frame_count_valid": len(valid),
        "thresholds": {
            "smile_threshold": smile_threshold if smile_threshold is not None else "adaptive (mean + 0.5*std)",
            "gaze_center_range": "CENTER classification from MediaPipe",  # Could be more specific
            "nod_pitch_delta_threshold": nod_pitch_threshold,
            "pose_outlier_thresholds": {"yaw": 60, "pitch": 45, "roll": 40}
        },
        "models": {
            "vision_model": "MediaPipe FaceMesh",
            "vision_config": {
                "refine_landmarks": True,
                "min_detection_confidence": 0.5,
                "min_tracking_confidence": 0.5
            },
            "emotion_model": "rule-based from landmarks + blendshapes (if available)",
            "stt_model": f"openai-whisper-{whisper_model_size}",
            "stt_version": "20250625"  # From requirements.txt
        },
        "confidence": {
            "gaze_confidence_mean": compute_gaze_confidence(timeline),
            "valid_frame_ratio": len(valid) / len(timeline) if timeline else 0.0
        },
        "outlier_flags": {
            "pose_outlier_ratio": compute_pose_outlier_ratio(timeline),
            "pose_outlier_description": "Proportion of frames with extreme head pose angles (likely solvePnP errors)"
        }
    }
    
    # Add duration if available
    if duration_sec is not None:
        metadata["duration_sec"] = duration_sec
    
    return metadata
