from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import numpy as np
import mediapipe

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


def compute_pose_outlier_ratio(timeline: List[Dict[str, Any]], 
                                 yaw_thresh: float = 60, 
                                 pitch_thresh: float = 45, 
                                 roll_thresh: float = 40) -> float:
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
        
        # Flag as outlier if any angle exceeds thresholds
        if abs(yaw) > yaw_thresh or abs(pitch) > pitch_thresh or abs(roll) > roll_thresh:
            outliers += 1
    
    return outliers / len(valid) if valid else 0.0


def compute_confidence_stats(timeline: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Compute confidence statistics from timeline.
    Returns mean and std for face_presence and landmark_confidence if available.
    """
    valid = [x for x in timeline if x.get("valid")]
    
    face_presence_scores = [x.get("face_presence") for x in valid if x.get("face_presence") is not None]
    landmark_confidence_scores = [x.get("landmark_confidence") for x in valid if x.get("landmark_confidence") is not None]
    
    stats = {}
    
    if face_presence_scores:
        stats["face_presence_mean"] = float(np.mean(face_presence_scores))
        stats["face_presence_std"] = float(np.std(face_presence_scores))
    
    if landmark_confidence_scores:
        stats["landmark_confidence_mean"] = float(np.mean(landmark_confidence_scores))
        stats["landmark_confidence_std"] = float(np.std(landmark_confidence_scores))
    
    # Gaze and emotion confidence (proxy: valid frame ratio)
    stats["gaze_confidence_mean"] = len(valid) / len(timeline) if timeline else 0.0
    stats["gaze_confidence_std"] = 0.0  # Placeholder
    
    return stats


def compute_metadata(
    timeline: List[Dict[str, Any]],
    fps_analyzed: float,
    smile_threshold: Optional[float],
    nod_pitch_threshold: float,
    whisper_model_size: str = "base",
    duration_sec: Optional[float] = None,
    yaw_thresh: float = 60,
    pitch_thresh: float = 45,
    roll_thresh: float = 40
) -> Dict[str, Any]:
    """
    Compute comprehensive metadata for reproducibility.
    REMOVES policy/evaluation criteria ("우수", "보통", etc.) - only logs observations.
    
    Args:
        timeline: Full frame-by-frame analysis results
        fps_analyzed: FPS used for frame extraction
        smile_threshold: Threshold used for smile detection (or None if adaptive)
        nod_pitch_threshold: Pitch delta threshold for nod detection
        whisper_model_size: Whisper model size used for STT
        duration_sec: Video duration in seconds
        yaw_thresh, pitch_thresh, roll_thresh: Pose outlier thresholds
    
    Returns:
        Dictionary with all metadata fields (structured for reproducibility)
    """
    valid = [x for x in timeline if x.get("valid")]
    
    # Frame counts
    frame_count_total = len(timeline)
    frame_count_valid = len(valid)
    frame_count_expected = int(duration_sec * fps_analyzed) if duration_sec else frame_count_total
    
    # Thresholds (structured with formula + value)
    thresholds = {
        "smile_threshold": {
            "type": "adaptive" if smile_threshold is not None else "none",
            "formula": "mean + 0.5*std" if smile_threshold is not None else None,
            "value": float(smile_threshold) if smile_threshold is not None else None
        },
        "gaze": {
            "method": "mediapipe_center + iris_yaw_check",
            "center_range_deg": [-15, 15]  # Approximate range for CENTER classification
        },
        "nod_pitch_delta_threshold": float(nod_pitch_threshold),
        "nod_min_interval_sec": None,  # Not implemented yet, placeholder
        "pose_outlier_thresholds": {
            "yaw": float(yaw_thresh),
            "pitch": float(pitch_thresh),
            "roll": float(roll_thresh)
        }
    }
    
    # Models and versions
    try:
        mediapipe_version = mediapipe.__version__
    except:
        mediapipe_version = "unknown"
    
    models = {
        "vision_model": "MediaPipe FaceMesh",
        "vision_version": mediapipe_version,
        "vision_config": {
            "refine_landmarks": True,
            "min_detection_confidence": 0.5,
            "min_tracking_confidence": 0.5
        },
        "emotion_model": "rule-based landmarks/blendshapes",
        "emotion_version": "1.0",  # Internal version
        "stt_model": f"openai-whisper-{whisper_model_size}",
        "stt_version": "20250625"  # From requirements.txt
    }
    
    # Confidence stats
    confidence_stats = compute_confidence_stats(timeline)
    confidence = {
        "valid_frame_ratio": frame_count_valid / frame_count_total if frame_count_total > 0 else 0.0,
        **confidence_stats
    }
    
    # Outlier flags
    outlier_ratio = compute_pose_outlier_ratio(timeline, yaw_thresh, pitch_thresh, roll_thresh)
    outlier_flags = {
        "pose_outlier_ratio": outlier_ratio,
        "pose_outlier_rule": f"abs(yaw)>{yaw_thresh} or abs(pitch)>{pitch_thresh} or abs(roll)>{roll_thresh}"
    }
    
    metadata = {
        "fps_analyzed": float(fps_analyzed),
        "duration_sec": float(duration_sec) if duration_sec else None,
        "frame_count_total": frame_count_total,
        "frame_count_valid": frame_count_valid,
        "frame_count_expected": frame_count_expected,
        "thresholds": thresholds,
        "models": models,
        "confidence": confidence,
        "outlier_flags": outlier_flags
    }
    
    return metadata
