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
class MetricsMetadata(BaseModel):
    """Computation metadata for metrics transparency and debugging"""
    # Frame analysis metadata
    fps_analyzed: Optional[float] = None
    frame_count_total: Optional[int] = None
    frame_count_valid: Optional[int] = None
    
    # Thresholds used
    thresholds: Optional[dict] = None  # e.g., {"smile_threshold": 0.5, "gaze_center_range": [0.35, 0.65], ...}
    
    # Models and versions
    models: Optional[dict] = None  # e.g., {"vision_model": "MediaPipe FaceMesh", "stt_model": "whisper-base", ...}
    
    # Confidence scores
    confidence: Optional[dict] = None  # e.g., {"gaze_confidence_mean": 0.95, ...}
    
    # Outlier detection
    outlier_flags: Optional[dict] = None  # e.g., {"pose_outlier_ratio": 0.02, ...}


class NonverbalMetricsBase(BaseModel):
    center_gaze_ratio: Optional[float] = None
    smile_ratio: Optional[float] = None
    nod_count: Optional[int] = None
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
