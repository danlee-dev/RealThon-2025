from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import aiohttp
import whisper
import os
import tempfile
from pathlib import Path
from database import get_db
from auth import get_current_user
from models import (
    InterviewSession,
    InterviewQuestion,
    InterviewVideo,
    InterviewTranscript,
    NonverbalMetrics,
    NonverbalTimeline,
    Feedback,
    InterviewAnswer,
    User,
    Portfolio,
    JobPosting
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
    FeedbackResponse,
    InterviewAnswerCreate,
    InterviewAnswerResponse
)
from services.llm_analyzer import LLMAnalyzer

router = APIRouter()
llm_analyzer = LLMAnalyzer()


# Interview Session endpoints
@router.post("/sessions", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
def create_interview_session(
    session: InterviewSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new interview session and generate initial questions automatically.
    """
    db_session = InterviewSession(
        user_id=current_user.id,
        title=session.title,
        portfolio_id=session.portfolio_id,
        job_posting_id=session.job_posting_id,
        status=session.status
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    # --- 초기 질문 자동 생성 로직 시작 ---
    try:
        # 포트폴리오 조회
        portfolio_text = "포트폴리오 없음"
        portfolio = None

        if session.portfolio_id:
            # portfolio_id가 명시적으로 제공된 경우
            portfolio = db.query(Portfolio).filter(Portfolio.id == session.portfolio_id).first()
        else:
            # portfolio_id가 없으면 사용자의 가장 최근 포트폴리오 자동 조회
            portfolio = db.query(Portfolio).filter(
                Portfolio.user_id == current_user.id
            ).order_by(Portfolio.created_at.desc()).first()

        if portfolio:
            portfolio_text = portfolio.parsed_text or portfolio.summary or "내용 없음"
            # 세션에 포트폴리오 ID 자동 설정
            if not session.portfolio_id:
                db_session.portfolio_id = portfolio.id
                db.commit()

        # 직무 공고 조회
        job_posting_text = "직무 공고 없음"
        if session.job_posting_id:
            job_posting = db.query(JobPosting).filter(JobPosting.id == session.job_posting_id).first()
            if job_posting:
                job_posting_text = job_posting.raw_text

        # LLM으로 질문 생성
        generated_questions = llm_analyzer.generate_initial_questions(portfolio_text, job_posting_text)
        
        # 생성된 질문을 DB에 저장
        for idx, q in enumerate(generated_questions):
            question_type = q.get("type", "general")
            question_text = q.get("text", "")
            
            db_question = InterviewQuestion(
                session_id=db_session.id,
                text=question_text,
                type=question_type,
                source="llm",  # Unified with followup questions
                order=idx + 1
            )
            db.add(db_question)
        
        db.commit()
        
    except Exception as e:
        print(f"⚠️ Failed to generate initial questions automatically: {e}")
        # 질문 생성 실패가 세션 생성 실패로 이어지지 않도록 함 (선택 사항)
        # 필요하다면 여기서 기본 질문을 넣거나, 에러를 로깅만 하고 넘어감

    # --- 초기 질문 자동 생성 로직 끝 ---

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


@router.post("/sessions/{session_id}/questions/generate", response_model=List[InterviewQuestionResponse])
def generate_initial_questions(session_id: str, db: Session = Depends(get_db)):
    """
    세션의 포트폴리오와 직무 공고를 기반으로 초기 질문 3개를 생성합니다.
    """
    # 세션 조회
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    # 포트폴리오 조회
    portfolio_text = "포트폴리오 없음"
    if session.portfolio_id:
        portfolio = db.query(Portfolio).filter(Portfolio.id == session.portfolio_id).first()
        if portfolio:
            # 파싱된 텍스트나 요약 사용
            portfolio_text = portfolio.parsed_text or portfolio.summary or "내용 없음"

    # 직무 공고 조회
    job_posting_text = "직무 공고 없음"
    if session.job_posting_id:
        job_posting = db.query(JobPosting).filter(JobPosting.id == session.job_posting_id).first()
        if job_posting:
            job_posting_text = job_posting.raw_text

    # LLM으로 질문 생성
    try:
        generated_questions = llm_analyzer.generate_initial_questions(portfolio_text, job_posting_text)
    except Exception as e:
        print(f"Failed to generate questions: {e}")
        # 실패 시 기본 질문 반환 로직은 LLMAnalyzer 내부에 있음
        generated_questions = []

    # 생성된 질문을 DB에 저장
    saved_questions = []
    for idx, q in enumerate(generated_questions):
        question_type = q.get("type", "general")
        question_text = q.get("text", "")
        
        # 같은 세션, 같은 order가 있으면 삭제 (재생성 시)
        existing = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == session_id,
            InterviewQuestion.order == idx + 1
        ).first()
        if existing:
            db.delete(existing)
        
        db_question = InterviewQuestion(
            session_id=session_id,
            text=question_text,
            type=question_type,
            source="llm",
            order=idx + 1
        )
        db.add(db_question)
        saved_questions.append(db_question)
    
    db.commit()
    for q in saved_questions:
        db.refresh(q)
        
    return saved_questions


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
    video: InterviewVideoCreate,
    current_user: User = Depends(get_current_user),
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
        user_id=current_user.id,
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


# Answer endpoints
@router.post("/questions/{question_id}/answers", response_model=InterviewAnswerResponse, status_code=status.HTTP_201_CREATED)
def create_answer(
    question_id: str,
    answer: InterviewAnswerCreate,
    db: Session = Depends(get_db)
):
    """
    질문에 대한 답변 저장

    Args:
        question_id: 질문 ID
        answer: 답변 데이터 (text, audio_url)
    """
    # 질문 존재 확인
    question = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # 답변 저장
    db_answer = InterviewAnswer(
        question_id=question_id,
        text=answer.text,
        audio_url=answer.audio_url
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer


@router.get("/questions/{question_id}/answers", response_model=List[InterviewAnswerResponse])
def get_question_answers(question_id: str, db: Session = Depends(get_db)):
    """질문에 대한 모든 답변 조회"""
    answers = db.query(InterviewAnswer).filter(
        InterviewAnswer.question_id == question_id
    ).all()
    return answers


# Followup question endpoint
@router.post("/questions/{question_id}/followup", response_model=InterviewQuestionResponse)
def generate_followup_question(
    question_id: str,
    answer_text: str,
    db: Session = Depends(get_db)
):
    """
    답변 기반 꼬리 질문 생성

    Args:
        question_id: 원래 질문 ID
        answer_text: 지원자의 답변 텍스트
    """
    # 원래 질문 조회
    parent_question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id
    ).first()

    if not parent_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent question not found"
        )

    # 꼬리 질문 생성
    try:
        followup_text = llm_analyzer.generate_followup_question(
            parent_question.text,
            answer_text
        )
    except Exception as e:
        print(f"Failed to generate followup question: {e}")
        followup_text = "방금 말씀하신 부분에 대해 좀 더 구체적으로 설명해주시겠어요?"

    # 꼬리 질문 DB에 저장
    # order는 parent + 0.5 (예: parent가 1이면 1.5, 2면 2.5)
    followup_order = parent_question.order + 0.5

    db_followup = InterviewQuestion(
        session_id=parent_question.session_id,
        text=followup_text,
        type="followup",
        source="llm",
        order=int(followup_order * 10),  # 정수로 변환 (15, 25, ...)
        parent_question_id=question_id
    )
    db.add(db_followup)
    db.commit()
    db.refresh(db_followup)

    return db_followup


# TTS endpoint
@router.get("/questions/{question_id}/tts")
async def get_question_tts(question_id: str, db: Session = Depends(get_db)):
    """
    질문을 음성으로 변환

    Args:
        question_id: 질문 ID

    Returns:
        음성 파일 URL 또는 Base64 인코딩된 오디오
    """
    # 질문 조회
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # MeloTTS 서버 호출 (Docker 컨테이너, port 8010)
    tts_url = os.getenv("MELO_TTS_BASE_URL", "http://localhost:8010")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{tts_url}/tts",
                json={
                    "text": question.text,
                    "speaker": "KR",
                    "speed": 1.0
                }
            ) as resp:
                if resp.status != 200:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="TTS generation failed"
                    )

                result = await resp.json()
                audio_path = result.get("audio_url", "")

                # MeloTTS 서버의 전체 URL로 변환
                if audio_path and not audio_path.startswith("http"):
                    audio_url = f"{tts_url}{audio_path}"
                else:
                    audio_url = audio_path

                return {
                    "question_id": question_id,
                    "audio_url": audio_url,
                    "text": question.text
                }

    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS service error: {str(e)}"
        )


# STT endpoint
@router.post("/stt")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    음성을 텍스트로 변환 (Whisper 사용)

    Args:
        audio: 오디오 파일 (.wav, .mp3, .webm 등)

    Returns:
        변환된 텍스트
    """
    # 임시 파일 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio.filename).suffix) as tmp_file:
        content = await audio.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    try:
        # Whisper 모델 로드 및 transcribe
        model = whisper.load_model("base")
        result = model.transcribe(tmp_file_path, language="ko")

        return {
            "text": result["text"],
            "language": result.get("language", "ko")
        }

    except Exception as e:
        print(f"STT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"STT failed: {str(e)}"
        )

    finally:
        # 임시 파일 삭제
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
