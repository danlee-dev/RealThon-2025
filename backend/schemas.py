from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# Portfolio Schemas
class PortfolioBase(BaseModel):
    filename: str
    file_url: str


class PortfolioCreate(PortfolioBase):
    parsed_text: Optional[str] = None
    summary: Optional[str] = None


class PortfolioResponse(PortfolioBase):
    id: str
    user_id: str
    parsed_text: Optional[str] = None
    summary: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# JobPosting Schemas
class JobPostingBase(BaseModel):
    company_name: str
    title: str
    raw_text: str
    source_url: Optional[str] = None


class JobPostingCreate(JobPostingBase):
    parsed_skills: Optional[str] = None


class JobPostingResponse(JobPostingBase):
    id: str
    user_id: str
    parsed_skills: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# InterviewSession Schemas
class InterviewSessionBase(BaseModel):
    title: Optional[str] = None
    portfolio_id: Optional[str] = None
    job_posting_id: Optional[str] = None


class InterviewSessionCreate(InterviewSessionBase):
    status: str = "in_progress"


class InterviewSessionResponse(InterviewSessionBase):
    id: str
    user_id: str
    status: str
    created_at: str
    completed_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# InterviewQuestion Schemas
class InterviewQuestionBase(BaseModel):
    text: str
    type: str
    source: str


class InterviewQuestionCreate(InterviewQuestionBase):
    order: int


class InterviewQuestionResponse(InterviewQuestionBase):
    id: str
    session_id: str
    order: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# InterviewVideo Schemas
class InterviewVideoBase(BaseModel):
    video_url: str
    audio_url: Optional[str] = None
    duration_sec: Optional[float] = None


class InterviewVideoCreate(InterviewVideoBase):
    question_id: str


class InterviewVideoResponse(InterviewVideoBase):
    id: str
    user_id: str
    session_id: str
    question_id: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# InterviewTranscript Schemas
class InterviewTranscriptBase(BaseModel):
    text: str
    language: Optional[str] = None


class InterviewTranscriptCreate(InterviewTranscriptBase):
    pass


class InterviewTranscriptResponse(InterviewTranscriptBase):
    id: str
    video_id: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# NonverbalMetrics Schemas
class ThresholdConfig(BaseModel):
    """Threshold configuration with formula and actual value"""
    type: Optional[str] = None  # e.g., "adaptive", "fixed"
    formula: Optional[str] = None  # e.g., "mean + 0.5*std"
    value: Optional[float] = None  # actual computed value


class GazeConfig(BaseModel):
    """Gaze detection configuration"""
    method: str  # e.g., "mediapipe_center + iris_yaw_check"
    center_range_deg: Optional[list] = None  # e.g., [-15, 15]


class PoseOutlierThresholds(BaseModel):
    """Head pose outlier detection thresholds"""
    yaw: float
    pitch: float
    roll: float


class ThresholdsMetadata(BaseModel):
    """All thresholds used for metric computation"""
    smile_threshold: ThresholdConfig
    gaze: GazeConfig
    nod_pitch_delta_threshold: float
    nod_min_interval_sec: Optional[float] = None  # minimum interval between nods
    pose_outlier_thresholds: PoseOutlierThresholds


class ModelConfig(BaseModel):
    """Model configuration with versions"""
    vision_model: str
    vision_version: Optional[str] = None
    vision_config: dict
    emotion_model: str
    emotion_version: Optional[str] = None
    stt_model: str
    stt_version: str


class ConfidenceMetrics(BaseModel):
    """Confidence and quality metrics"""
    valid_frame_ratio: float
    face_presence_mean: Optional[float] = None
    face_presence_std: Optional[float] = None
    landmark_confidence_mean: Optional[float] = None
    landmark_confidence_std: Optional[float] = None
    gaze_confidence_mean: Optional[float] = None
    gaze_confidence_std: Optional[float] = None
    emotion_confidence_mean: Optional[float] = None
    emotion_confidence_std: Optional[float] = None


class OutlierFlags(BaseModel):
    """Outlier detection results"""
    pose_outlier_ratio: float
    pose_outlier_rule: str


class MetricsMetadata(BaseModel):
    """Computation metadata for reproducibility and debugging"""
    # Frame analysis info
    fps_analyzed: float
    duration_sec: float
    frame_count_total: int  # actual frames extracted
    frame_count_valid: int  # frames with successful analysis
    frame_count_expected: int  # expected frames (duration * fps)
    
    # Computation thresholds and rules
    thresholds: ThresholdsMetadata
    
    # Models and versions
    models: ModelConfig
    
    # Confidence and quality metrics
    confidence: ConfidenceMetrics
    
    # Outlier detection
    outlier_flags: OutlierFlags


class NonverbalMetricsBase(BaseModel):
    center_gaze_ratio: Optional[float] = None
    smile_ratio: Optional[float] = None
    nod_count: Optional[int] = None
    nod_rate_per_min: Optional[float] = None  # NEW: normalized nod rate
    wpm: Optional[float] = None
    filler_count: Optional[int] = None
    primary_emotion: Optional[str] = None


class NonverbalMetricsCreate(NonverbalMetricsBase):
    metadata_json: Optional[str] = None  # JSON string of MetricsMetadata


class NonverbalMetricsResponse(NonverbalMetricsBase):
    id: str
    video_id: str
    created_at: str
    metadata: Optional[MetricsMetadata] = None  # Parsed from metadata_json

    model_config = ConfigDict(from_attributes=True)


# NonverbalTimeline Schemas
class NonverbalTimelineBase(BaseModel):
    timeline_json: str


class NonverbalTimelineCreate(NonverbalTimelineBase):
    pass


class NonverbalTimelineResponse(NonverbalTimelineBase):
    id: str
    video_id: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# Feedback Schemas
class FeedbackBase(BaseModel):
    level: str
    title: str
    message: str
    severity: str
    start_sec: Optional[float] = None
    end_sec: Optional[float] = None


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackResponse(FeedbackBase):
    id: str
    video_id: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)
