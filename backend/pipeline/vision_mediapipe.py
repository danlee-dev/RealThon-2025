from pathlib import Path
from typing import List, Optional, Tuple, Dict
import json
from dataclasses import dataclass, asdict, is_dataclass

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

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
# Sources for indices: mouth/eyes/iris mapping

# Head pose PnP reference points (commonly used)
POSE_IDXS = [1, 152, R_EYE_OUTER, L_EYE_OUTER, MOUTH_LEFT, MOUTH_RIGHT]
# 1 nose tip, 152 chin, 33/263 eye outer corners, 61/291 mouth corners

@dataclass
class FrameResult:
    t: float
    valid: bool
    gaze: Optional[str]
    smile: Optional[float]
    yaw: Optional[float]
    pitch: Optional[float]
    roll: Optional[float]
    emotion: Optional[str]
    blendshapes: Optional[Dict[str, float]]

class VisionAnalyzer:
    """
    Enhanced MediaPipe FaceLandmarker with blendshapes:
    - gaze (LEFT/RIGHT/CENTER) via iris position
    - smile score via blendshapes + geometric features
    - head pose (yaw/pitch/roll) via solvePnP
    - emotion detection via blendshapes
    """
    def __init__(self, model_path: Optional[Path] = None, use_blendshapes: bool = True):
        self.use_blendshapes = use_blendshapes
        
        if use_blendshapes and model_path and model_path.exists():
            # Use new FaceLandmarker with blendshapes
            try:
                BaseOptions = mp.tasks.BaseOptions
                FaceLandmarker = mp.tasks.vision.FaceLandmarker
                FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
                VisionRunningMode = mp.tasks.vision.RunningMode
                
                options = FaceLandmarkerOptions(
                    base_options=BaseOptions(model_asset_path=str(model_path)),
                    running_mode=VisionRunningMode.IMAGE,
                    output_face_blendshapes=True,
                    num_faces=1
                )
                self.landmarker = FaceLandmarker.create_from_options(options)
                self.use_new_api = True
                print("✅ Using MediaPipe FaceLandmarker with blendshapes")
            except Exception as e:
                print(f"⚠️ Failed to load blendshapes model: {e}")
                print("Falling back to legacy FaceMesh")
                self.use_new_api = False
                self._init_legacy()
        else:
            # Fallback to legacy FaceMesh
            self.use_new_api = False
            self._init_legacy()
    
    def _init_legacy(self):
        """Initialize legacy FaceMesh"""
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
        
        if self.use_new_api:
            return self._analyze_with_blendshapes(t, rgb, w, h)
        else:
            return self._analyze_legacy(t, rgb, w, h)
    
    def _analyze_with_blendshapes(self, t: float, rgb_frame, w: int, h: int) -> FrameResult:
        """Analyze using new FaceLandmarker API with blendshapes"""
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.landmarker.detect(mp_image)
        
        if not result.face_landmarks:
            return FrameResult(
                t=t, valid=False, gaze=None, smile=None,
                yaw=None, pitch=None, roll=None, emotion=None, blendshapes=None
            )
        
        # Extract landmarks
        landmarks = result.face_landmarks[0]
        pts = np.array([(lm.x*w, lm.y*h, lm.z*w) for lm in landmarks], dtype=np.float32)
        
        # Extract blendshapes
        blendshapes_dict = {}
        emotion = None
        smile_score = None
        
        if result.face_blendshapes:
            for category in result.face_blendshapes[0]:
                if category.category_name != "_neutral":
                    blendshapes_dict[category.category_name] = float(category.score)
            
            # Use blendshapes for smile
            smile_score = blendshapes_dict.get("mouthSmileLeft", 0) + blendshapes_dict.get("mouthSmileRight", 0)
            smile_score = float(smile_score / 2.0)
            
            # Detect emotion from blendshapes
            emotion = self._detect_emotion_from_blendshapes(blendshapes_dict)
        
        # Fallback to geometric smile if no blendshapes
        if smile_score is None:
            smile_score = self.estimate_smile(pts)
        
        # Head pose
        yaw, pitch, roll = self.estimate_head_pose(pts, w, h)
        
        # Gaze
        gaze = self.estimate_gaze(pts, yaw)
        
        # Blendshapes에서 감정을 못 찾았으면 랜드마크 기반으로 추론
        if emotion is None:
            emotion = self._detect_emotion_from_landmarks(smile_score, yaw, pitch, roll, gaze)
        
        return FrameResult(
            t=t,
            valid=True,
            gaze=gaze,
            smile=smile_score,
            yaw=yaw,
            pitch=pitch,
            roll=roll,
            emotion=emotion,
            blendshapes=blendshapes_dict if blendshapes_dict else None
        )
    
    def _analyze_legacy(self, t: float, rgb_frame, w: int, h: int) -> FrameResult:
        """Analyze using legacy FaceMesh"""
        out = self.face.process(rgb_frame)

        if not out.multi_face_landmarks:
            return FrameResult(
                t=t, valid=False, gaze=None, smile=None,
                yaw=None, pitch=None, roll=None, emotion=None, blendshapes=None
            )

        pts = self._landmarks_to_np(out.multi_face_landmarks[0].landmark, w, h)

        yaw, pitch, roll = self.estimate_head_pose(pts, w, h)
        gaze = self.estimate_gaze(pts, yaw)
        smile = self.estimate_smile(pts)
        
        # Blendshapes 없이도 감정 추론 (기존 데이터 활용)
        emotion = self._detect_emotion_from_landmarks(smile, yaw, pitch, roll, gaze)

        return FrameResult(
            t=t,
            valid=True,
            gaze=gaze,
            smile=smile,
            yaw=yaw,
            pitch=pitch,
            roll=roll,
            emotion=emotion,
            blendshapes=None
        )
    
    def _detect_emotion_from_blendshapes(self, blendshapes: Dict[str, float]) -> str:
        """
        Detect primary emotion from blendshapes.
        Returns: 'happy', 'neutral', 'surprised', 'focused', etc.
        """
        # Smile indicators
        smile_l = blendshapes.get("mouthSmileLeft", 0)
        smile_r = blendshapes.get("mouthSmileRight", 0)
        smile_avg = (smile_l + smile_r) / 2.0
        
        # Eye indicators
        eye_wide_l = blendshapes.get("eyeWideLeft", 0)
        eye_wide_r = blendshapes.get("eyeWideRight", 0)
        eye_wide = (eye_wide_l + eye_wide_r) / 2.0
        
        # Brow indicators
        brow_inner_up = blendshapes.get("browInnerUp", 0)
        brow_outer_up_l = blendshapes.get("browOuterUpLeft", 0)
        brow_outer_up_r = blendshapes.get("browOuterUpRight", 0)
        brow_up = max(brow_inner_up, brow_outer_up_l, brow_outer_up_r)
        
        # Mouth indicators
        mouth_frown_l = blendshapes.get("mouthFrownLeft", 0)
        mouth_frown_r = blendshapes.get("mouthFrownRight", 0)
        frown = (mouth_frown_l + mouth_frown_r) / 2.0
        
        # Simple rule-based emotion
        if smile_avg > 0.3:
            return "happy"
        elif eye_wide > 0.5 and brow_up > 0.4:
            return "surprised"
        elif frown > 0.3:
            return "concerned"
        elif smile_avg > 0.1:
            return "pleasant"
        else:
            return "neutral"
    
    def _detect_emotion_from_landmarks(
        self, 
        smile_score: float, 
        yaw: float, 
        pitch: float, 
        roll: float, 
        gaze: str
    ) -> str:
        """
        Blendshapes 없이도 기존 랜드마크 데이터로 감정 추론.
        smile score, head pose, gaze를 조합해서 감정 분류.
        
        Returns: 'happy', 'pleasant', 'neutral', 'focused', 'concerned'
        """
        # Smile score 기반 (0.4 이상이면 happy, 0.25 이상이면 pleasant)
        # smile_score는 mouth_width / interocular_distance 비율
        # 일반적으로 0.4~0.5가 평상시, 0.5 이상이면 미소
        
        # Head pose 기반
        # pitch가 위로 올라가면 (양수) 놀람/집중
        # pitch가 아래로 내려가면 (음수) 고개 숙임/부정적
        # yaw가 크면 (절댓값 > 15) 집중/고민
        
        # Gaze 기반
        # CENTER면 집중, LEFT/RIGHT면 불안/회피
        
        # 감정 분류 로직
        if smile_score > 0.5:
            # 미소가 크면 happy
            return "happy"
        elif smile_score > 0.35:
            # 약간의 미소면 pleasant
            return "pleasant"
        elif abs(yaw) > 15 or abs(pitch) > 20:
            # 고개를 많이 돌리면 focused (집중)
            return "focused"
        elif pitch < -10:
            # 고개를 많이 숙이면 concerned (걱정/부정적)
            return "concerned"
        elif gaze != "CENTER" and abs(yaw) > 10:
            # 시선이 많이 벗어나면 concerned
            return "concerned"
        else:
            # 기본값은 neutral
            return "neutral"


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


def build_timeline_from_frames(frames, model_path: Optional[Path] = None):
    """
    Build timeline from extracted frames.
    
    Args:
        frames: List of (timestamp, frame_path) tuples
        model_path: Optional path to face_landmarker_v2_with_blendshapes.task model
                   If provided and exists, uses blendshapes for better emotion detection
    """
    # Check for model in multiple locations
    if model_path is None:
        possible_paths = [
            Path("MediaPipe/face_landmarker_v2_with_blendshapes.task"),
            Path("./MediaPipe/face_landmarker_v2_with_blendshapes.task"),
            Path("models/face_landmarker_v2_with_blendshapes.task"),
        ]
        for p in possible_paths:
            if p.exists():
                model_path = p
                break
    
    use_blendshapes = model_path is not None and model_path.exists() if model_path else False
    
    analyzer = VisionAnalyzer(model_path=model_path, use_blendshapes=use_blendshapes)
    timeline = []

    for t, frame_path in frames:
        frame = cv2.imread(str(frame_path))
        if frame is None:
            print(f"⚠️ Failed to read frame: {frame_path}")
            continue
            
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
