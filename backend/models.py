from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "user"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String)  # 'ROLE_FE' | 'ROLE_BE' | 'ROLE_AI'
    level = Column(String)  # 'LEVEL_JUNIOR' | 'LEVEL_MID' | 'LEVEL_SENIOR'
    github_username = Column(String)  # GitHub username
    github_token = Column(String)  # GitHub personal access token (optional)
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())

    # Relationships
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    job_postings = relationship("JobPosting", back_populates="user", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    interview_videos = relationship("InterviewVideo", back_populates="user", cascade="all, delete-orphan")


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    file_url = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    parsed_text = Column(Text)
    summary = Column(Text)
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())

    # Relationships
    user = relationship("User", back_populates="portfolios")
    interview_sessions = relationship("InterviewSession", back_populates="portfolio")


class JobPosting(Base):
    __tablename__ = "job_posting"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    source_url = Column(String)
    raw_text = Column(Text, nullable=False)
    parsed_skills = Column(Text)
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())

    # Relationships
    user = relationship("User", back_populates="job_postings")
    interview_sessions = relationship("InterviewSession", back_populates="job_posting")


class InterviewSession(Base):
    __tablename__ = "interview_session"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    portfolio_id = Column(String, ForeignKey("portfolio.id", ondelete="SET NULL"))
    job_posting_id = Column(String, ForeignKey("job_posting.id", ondelete="SET NULL"))
    title = Column(String)
    status = Column(String, nullable=False)  # 'in_progress' | 'completed' | 'failed'
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())
    completed_at = Column(String)

    # Relationships
    user = relationship("User", back_populates="interview_sessions")
    portfolio = relationship("Portfolio", back_populates="interview_sessions")
    job_posting = relationship("JobPosting", back_populates="interview_sessions")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    videos = relationship("InterviewVideo", back_populates="session", cascade="all, delete-orphan")


class InterviewQuestion(Base):
    __tablename__ = "interview_question"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("interview_session.id", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # 'intro' | 'portfolio' | 'job' | ...
    source = Column(String, nullable=False)  # 'portfolio' | 'job_posting' | 'combined' | 'manual'
    parent_question_id = Column(
        String,
        ForeignKey("interview_question.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())

    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
    videos = relationship("InterviewVideo", back_populates="question", cascade="all, delete-orphan")
    parent_question = relationship(
        "InterviewQuestion",
        remote_side=[id],
        backref=backref("followup_questions"),
        foreign_keys=[parent_question_id]
    )


class InterviewVideo(Base):
    __tablename__ = "interview_video"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String, ForeignKey("interview_session.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String, ForeignKey("interview_question.id", ondelete="CASCADE"), nullable=False)
    video_url = Column(String, nullable=False)
    audio_url = Column(String)
    duration_sec = Column(Float)
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())

    # Relationships
    user = relationship("User", back_populates="interview_videos")
    session = relationship("InterviewSession", back_populates="videos")
    question = relationship("InterviewQuestion", back_populates="videos")
    transcript = relationship("InterviewTranscript", back_populates="video", uselist=False, cascade="all, delete-orphan")
    nonverbal_metrics = relationship("NonverbalMetrics", back_populates="video", uselist=False, cascade="all, delete-orphan")
    nonverbal_timeline = relationship("NonverbalTimeline", back_populates="video", uselist=False, cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="video", cascade="all, delete-orphan")


class InterviewTranscript(Base):
    __tablename__ = "interview_transcript"

    id = Column(String, primary_key=True, default=generate_uuid)
    video_id = Column(String, ForeignKey("interview_video.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    language = Column(String)
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())

    # Relationships
    video = relationship("InterviewVideo", back_populates="transcript")


class NonverbalMetrics(Base):
    __tablename__ = "nonverbal_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    video_id = Column(String, ForeignKey("interview_video.id", ondelete="CASCADE"), nullable=False)
    
    # Core metrics
    center_gaze_ratio = Column(Float)
    smile_ratio = Column(Float)
    nod_count = Column(Integer)
    nod_rate_per_min = Column(Float)  # NEW: normalized nod rate
    wpm = Column(Float)
    filler_count = Column(Integer)
    primary_emotion = Column(String)
    
    # Computation metadata (JSON stored as Text)
    metadata_json = Column(Text)  # Stores: fps, frame counts, thresholds, models, confidence, outliers
    
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())

    # Relationships
    video = relationship("InterviewVideo", back_populates="nonverbal_metrics")


class NonverbalTimeline(Base):
    __tablename__ = "nonverbal_timeline"

    id = Column(String, primary_key=True, default=generate_uuid)
    video_id = Column(String, ForeignKey("interview_video.id", ondelete="CASCADE"), nullable=False)
    timeline_json = Column(Text, nullable=False)
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())

    # Relationships
    video = relationship("InterviewVideo", back_populates="nonverbal_timeline")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=generate_uuid)
    video_id = Column(String, ForeignKey("interview_video.id", ondelete="CASCADE"), nullable=False)
    level = Column(String, nullable=False)  # 'video' | 'segment'
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, nullable=False)  # 'info' | 'warning' | 'suggestion'
    start_sec = Column(Float)
    end_sec = Column(Float)
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())

    # Relationships
    video = relationship("InterviewVideo", back_populates="feedbacks")


class CapabilityEvaluation(Base):
    """
    포트폴리오별 역량 평가 (6개 역량 통합)

    각 포트폴리오(Portfolio)에 대해 직무별 6개 역량을 평가하고 점수, 피드백 저장
    Gemini를 통해 portfolio.summary를 분석하여 자동 생성
    """
    __tablename__ = "capability_evaluation"

    id = Column(String, primary_key=True, default=generate_uuid)
    portfolio_id = Column(String, ForeignKey("portfolio.id", ondelete="CASCADE"), nullable=False, unique=True)
    role = Column(String, nullable=False)  # 'ROLE_FE' | 'ROLE_BE' | 'ROLE_AI'

    # 역량 1
    capability1_name_en = Column(String, nullable=False)  # 예: "Technical Skills"
    capability1_name_ko = Column(String, nullable=False)  # 예: "기술 역량"
    capability1_score = Column(Float, nullable=False)     # 0-100
    capability1_reason = Column(Text)                     # 점수를 준 이유
    capability1_feedback = Column(Text)                   # 개선 피드백

    # 역량 2
    capability2_name_en = Column(String, nullable=False)
    capability2_name_ko = Column(String, nullable=False)
    capability2_score = Column(Float, nullable=False)
    capability2_reason = Column(Text)
    capability2_feedback = Column(Text)

    # 역량 3
    capability3_name_en = Column(String, nullable=False)
    capability3_name_ko = Column(String, nullable=False)
    capability3_score = Column(Float, nullable=False)
    capability3_reason = Column(Text)
    capability3_feedback = Column(Text)

    # 역량 4
    capability4_name_en = Column(String, nullable=False)
    capability4_name_ko = Column(String, nullable=False)
    capability4_score = Column(Float, nullable=False)
    capability4_reason = Column(Text)
    capability4_feedback = Column(Text)

    # 역량 5
    capability5_name_en = Column(String, nullable=False)
    capability5_name_ko = Column(String, nullable=False)
    capability5_score = Column(Float, nullable=False)
    capability5_reason = Column(Text)
    capability5_feedback = Column(Text)

    # 역량 6
    capability6_name_en = Column(String, nullable=False)
    capability6_name_ko = Column(String, nullable=False)
    capability6_score = Column(Float, nullable=False)
    capability6_reason = Column(Text)
    capability6_feedback = Column(Text)

    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())

    # Relationships
    portfolio = relationship("Portfolio", backref=backref("capability_evaluation", uselist=False, cascade="all, delete-orphan"))
