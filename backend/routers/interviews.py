from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db
from models import (
    InterviewSession,
    InterviewQuestion,
    InterviewVideo,
    InterviewTranscript,
    NonverbalMetrics,
    NonverbalTimeline,
    Feedback,
    User
)
from schemas import (
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewQuestionCreate,
    InterviewQuestionResponse,
    InterviewVideoCreate,
    InterviewVideoResponse,
    InterviewTranscriptCreate,
    InterviewTranscriptResponse,
    NonverbalMetricsCreate,
    NonverbalMetricsResponse,
    NonverbalTimelineCreate,
    NonverbalTimelineResponse,
    FeedbackCreate,
    FeedbackResponse
)

router = APIRouter()


# Interview Session endpoints
@router.post("/sessions", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
def create_interview_session(
    session: InterviewSessionCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Create a new interview session"""
    # Verify user exists
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db_session = InterviewSession(
        user_id=user_id,
        title=session.title,
        portfolio_id=session.portfolio_id,
        job_posting_id=session.job_posting_id,
        status=session.status
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/sessions/{session_id}", response_model=InterviewSessionResponse)
def get_interview_session(session_id: str, db: Session = Depends(get_db)):
    """Get interview session by ID"""
    db_session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    return db_session


@router.get("/sessions/user/{user_id}", response_model=List[InterviewSessionResponse])
def list_user_interview_sessions(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all interview sessions for a user"""
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == user_id
    ).offset(skip).limit(limit).all()
    return sessions


@router.patch("/sessions/{session_id}/complete", response_model=InterviewSessionResponse)
def complete_interview_session(session_id: str, db: Session = Depends(get_db)):
    """Mark interview session as completed"""
    db_session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    db_session.status = "completed"
    db_session.completed_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(db_session)
    return db_session


# Interview Question endpoints
@router.post("/sessions/{session_id}/questions", response_model=InterviewQuestionResponse, status_code=status.HTTP_201_CREATED)
def create_interview_question(
    session_id: str,
    question: InterviewQuestionCreate,
    db: Session = Depends(get_db)
):
    """Create a new interview question for a session"""
    # Verify session exists
    db_session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )

    db_question = InterviewQuestion(
        session_id=session_id,
        text=question.text,
        type=question.type,
        source=question.source,
        order=question.order
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


@router.get("/sessions/{session_id}/questions", response_model=List[InterviewQuestionResponse])
def list_session_questions(session_id: str, db: Session = Depends(get_db)):
    """List all questions for a session"""
    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session_id
    ).order_by(InterviewQuestion.order).all()
    return questions


# Interview Video endpoints
@router.post("/sessions/{session_id}/videos", response_model=InterviewVideoResponse, status_code=status.HTTP_201_CREATED)
def create_interview_video(
    session_id: str,
    user_id: str,
    video: InterviewVideoCreate,
    db: Session = Depends(get_db)
):
    """Create a new interview video"""
    # Verify session exists
    db_session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )

    db_video = InterviewVideo(
        user_id=user_id,
        session_id=session_id,
        question_id=video.question_id,
        video_url=video.video_url,
        audio_url=video.audio_url,
        duration_sec=video.duration_sec
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video


@router.get("/videos/{video_id}", response_model=InterviewVideoResponse)
def get_interview_video(video_id: str, db: Session = Depends(get_db)):
    """Get interview video by ID"""
    db_video = db.query(InterviewVideo).filter(InterviewVideo.id == video_id).first()
    if not db_video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview video not found"
        )
    return db_video


# Transcript endpoints
@router.post("/videos/{video_id}/transcript", response_model=InterviewTranscriptResponse, status_code=status.HTTP_201_CREATED)
def create_transcript(
    video_id: str,
    transcript: InterviewTranscriptCreate,
    db: Session = Depends(get_db)
):
    """Create transcript for a video"""
    # Verify video exists
    db_video = db.query(InterviewVideo).filter(InterviewVideo.id == video_id).first()
    if not db_video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview video not found"
        )

    db_transcript = InterviewTranscript(
        video_id=video_id,
        text=transcript.text,
        language=transcript.language
    )
    db.add(db_transcript)
    db.commit()
    db.refresh(db_transcript)
    return db_transcript


# Nonverbal Metrics endpoints
@router.post("/videos/{video_id}/metrics", response_model=NonverbalMetricsResponse, status_code=status.HTTP_201_CREATED)
def create_nonverbal_metrics(
    video_id: str,
    metrics: NonverbalMetricsCreate,
    db: Session = Depends(get_db)
):
    """Create nonverbal metrics for a video"""
    # Verify video exists
    db_video = db.query(InterviewVideo).filter(InterviewVideo.id == video_id).first()
    if not db_video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview video not found"
        )

    db_metrics = NonverbalMetrics(
        video_id=video_id,
        center_gaze_ratio=metrics.center_gaze_ratio,
        smile_ratio=metrics.smile_ratio,
        nod_count=metrics.nod_count,
        wpm=metrics.wpm,
        filler_count=metrics.filler_count,
        primary_emotion=metrics.primary_emotion
    )
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics


# Nonverbal Timeline endpoints
@router.post("/videos/{video_id}/timeline", response_model=NonverbalTimelineResponse, status_code=status.HTTP_201_CREATED)
def create_nonverbal_timeline(
    video_id: str,
    timeline: NonverbalTimelineCreate,
    db: Session = Depends(get_db)
):
    """Create nonverbal timeline for a video"""
    # Verify video exists
    db_video = db.query(InterviewVideo).filter(InterviewVideo.id == video_id).first()
    if not db_video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview video not found"
        )

    db_timeline = NonverbalTimeline(
        video_id=video_id,
        timeline_json=timeline.timeline_json
    )
    db.add(db_timeline)
    db.commit()
    db.refresh(db_timeline)
    return db_timeline


# Feedback endpoints
@router.post("/videos/{video_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    video_id: str,
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """Create feedback for a video"""
    # Verify video exists
    db_video = db.query(InterviewVideo).filter(InterviewVideo.id == video_id).first()
    if not db_video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview video not found"
        )

    db_feedback = Feedback(
        video_id=video_id,
        level=feedback.level,
        title=feedback.title,
        message=feedback.message,
        severity=feedback.severity,
        start_sec=feedback.start_sec,
        end_sec=feedback.end_sec
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


@router.get("/videos/{video_id}/feedback", response_model=List[FeedbackResponse])
def list_video_feedback(video_id: str, db: Session = Depends(get_db)):
    """List all feedback for a video"""
    feedback = db.query(Feedback).filter(Feedback.video_id == video_id).all()
    return feedback
