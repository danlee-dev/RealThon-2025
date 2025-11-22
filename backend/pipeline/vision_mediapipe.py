from pathlib import Path
from typing import List, Optional, Tuple
import json
from dataclasses import dataclass, asdict, is_dataclass

import cv2
import numpy as np
import mediapipe as mp

# ---- MediaPipe face landmark indices (verified) ----
# Mouth corners / lips
MOUTH_LEFT = 61
MOUTH_RIGHT = 291
LIP_UP = 13
LIP_DOWN = 14
GAZE_DEBUG = []
# Eye corners
R_EYE_OUTER = 33
R_EYE_INNER = 133
L_EYE_INNER = 362
L_EYE_OUTER = 263

# Iris landmarks (FaceMesh refine_landmarks=True)
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]
# Sources for indices: mouth/eyes/iris mapping :contentReference[oaicite:0]{index=0}

# Head pose PnP reference points (commonly used)
POSE_IDXS = [1, 152, R_EYE_OUTER, L_EYE_OUTER, MOUTH_LEFT, MOUTH_RIGHT]
# 1 nose tip, 152 chin, 33/263 eye outer corners, 61/291 mouth corners :contentReference[oaicite:1]{index=1}

@dataclass
class FrameResult:
    t: float
    valid: bool
    gaze: Optional[str]
    smile: Optional[float]
    yaw: Optional[float]
    pitch: Optional[float]
    roll: Optional[float]

class VisionAnalyzer:
    """
    FaceMesh-based frame analyzer:
    - gaze (LEFT/RIGHT/CENTER) via iris position
    - smile score via mouth width normalized by inter-ocular distance
    - head pose (yaw/pitch/roll) via solvePnP
    """
    def __init__(self):
        self.mp_face = mp.solutions.face_mesh
        self.face = self.mp_face.FaceMesh(
            static_image_mode=True,
            refine_landmarks=True,
            max_num_faces=1,
            min_detection_confidence=0.5
        )

    def _landmarks_to_np(self, landmarks, w, h):
        pts = np.array([(lm.x*w, lm.y*h, lm.z*w) for lm in landmarks], dtype=np.float32)
        return pts

    def analyze_frame(self, t: float, frame_bgr) -> FrameResult:
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        out = self.face.process(rgb)

        if not out.multi_face_landmarks:
            return FrameResult(t=t, valid=False, gaze=None, smile=None,
                            yaw=None, pitch=None, roll=None)

        pts = self._landmarks_to_np(out.multi_face_landmarks[0].landmark, w, h)

        yaw, pitch, roll = self.estimate_head_pose(pts, w, h)
        gaze = self.estimate_gaze(pts, yaw)
        smile = self.estimate_smile(pts)

        return FrameResult(
            t=t,
            valid=True,
            gaze=gaze,
            smile=smile,
            yaw=yaw,
            pitch=pitch,
            roll=roll
        )


    # ---------- Gaze ----------
    def _iris_center(self, pts, iris_idx_list):
        iris_pts = pts[iris_idx_list, :2]
        return iris_pts.mean(axis=0)

    def estimate_gaze(self, pts, yaw_deg: Optional[float]) -> str:

        """
        Simple iris-horizontal-ratio gaze:
        ratio = (iris_x - outer_x) / (inner_x - outer_x)
        avg of both eyes:
          ~0.5 => CENTER
          small => toward outer corners
          large => toward inner corners
        NOTE: LEFT/RIGHT naming may be flipped depending on camera mirroring.
        """
        # Right eye
        r_outer = pts[R_EYE_OUTER, :2]
        r_inner = pts[R_EYE_INNER, :2]
        r_iris = self._iris_center(pts, RIGHT_IRIS)

        r_width = (r_inner[0] - r_outer[0])
        r_ratio = (r_iris[0] - r_outer[0]) / (r_width + 1e-6)

        # Left eye
        l_outer = pts[L_EYE_OUTER, :2]
        l_inner = pts[L_EYE_INNER, :2]
        l_iris = self._iris_center(pts, LEFT_IRIS)

        l_width = (l_inner[0] - l_outer[0])
        l_ratio = (l_iris[0] - l_outer[0]) / (l_width + 1e-6)

        avg_ratio = float((r_ratio + l_ratio) / 2.0)
        GAZE_DEBUG.append(avg_ratio)

        # iris ratio가 거의 안 움직이면 yaw로 fallback
        if yaw_deg is None:
            return "CENTER"

        yaw_thresh = 8.0  # degree
        if -yaw_thresh <= yaw_deg <= yaw_thresh:
            return "CENTER"
        elif yaw_deg > yaw_thresh:
            return "RIGHT"   # 필요하면 나중에 좌우 flip
        else:
            return "LEFT"

    # ---------- Smile ----------
    def estimate_smile(self, pts) -> float:
        """
        Smile proxy:
        mouth_width / interocular_distance,
        lightly gated by lip opening to avoid false positives.
        """
        mouth_left = pts[MOUTH_LEFT, :2]
        mouth_right = pts[MOUTH_RIGHT, :2]
        lip_up = pts[LIP_UP, :2]
        lip_down = pts[LIP_DOWN, :2]

        mouth_width = np.linalg.norm(mouth_right - mouth_left)
        lip_gap = np.linalg.norm(lip_down - lip_up)

        eye_r = pts[R_EYE_OUTER, :2]
        eye_l = pts[L_EYE_OUTER, :2]
        interocular = np.linalg.norm(eye_l - eye_r)

        smile_score = (mouth_width / (interocular + 1e-6))

        # Small gating: if lips closed too much, dampen
        if lip_gap < 0.01 * interocular:
            smile_score *= 0.7

        return float(smile_score)

    # ---------- Head Pose ----------
    def estimate_head_pose(self, pts, w, h) -> Tuple[float, float, float]:
        """
        solvePnP with 6 canonical points.
        Returns yaw, pitch, roll in degrees.
        """
        image_points = np.array([pts[i, :2] for i in POSE_IDXS], dtype=np.float64)

        # Generic 3D face model points (approx. mm in a canonical face space)
        model_points = np.array([
            (0.0,   0.0,   0.0),     # nose tip
            (0.0, -63.6, -12.5),     # chin
            (-43.3, 32.7, -26.0),    # right eye outer (from person's POV)
            (43.3,  32.7, -26.0),    # left eye outer
            (-28.9,-28.9, -24.1),    # mouth left
            (28.9, -28.9, -24.1),    # mouth right
        ])

        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)

        dist_coeffs = np.zeros((4, 1))  # assume no lens distortion

        success, rvec, tvec = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        if not success:
            return 0.0, 0.0, 0.0

        rmat, _ = cv2.Rodrigues(rvec)
        sy = np.sqrt(rmat[0,0]**2 + rmat[1,0]**2)
        singular = sy < 1e-6

        if not singular:
            pitch = np.arctan2(rmat[2,1], rmat[2,2])
            yaw   = np.arctan2(-rmat[2,0], sy)
            roll  = np.arctan2(rmat[1,0], rmat[0,0])
        else:
            pitch = np.arctan2(-rmat[1,2], rmat[1,1])
            yaw   = np.arctan2(-rmat[2,0], sy)
            roll  = 0

        yaw_deg = float(np.degrees(yaw))
        pitch_deg = float(np.degrees(pitch))
        roll_deg = float(np.degrees(roll))

        # ---- wrap to [-180, 180] ----
        def wrap_angle(a):
            return (a + 180) % 360 - 180

        yaw_deg = wrap_angle(yaw_deg)
        pitch_deg = wrap_angle(pitch_deg)
        roll_deg = wrap_angle(roll_deg)

        # pitch 뒤집힘 방지: 사람 기준 [-90, 90] 쪽으로 fold
        if pitch_deg < -90:
            pitch_deg += 180
        elif pitch_deg > 90:
            pitch_deg -= 180

        return yaw_deg, pitch_deg, roll_deg


def build_timeline_from_frames(frames):
    analyzer = VisionAnalyzer()
    timeline = []

    for t, frame_path in frames:
        frame = cv2.imread(str(frame_path))
        res = analyzer.analyze_frame(t, frame)

        if is_dataclass(res):
            timeline.append(asdict(res))
        else:
            # res가 dict이면 그대로 넣기
            timeline.append(res)

    return timeline

def save_timeline(timeline: List[dict], out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)
