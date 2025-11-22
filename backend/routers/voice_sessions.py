"""
음성 면접 세션 API 라우터

/api/voice/session/start - 세션 시작
/api/voice/answer/complete - 답변 처리
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import InterviewSession, User, Portfolio
from clients import get_stt_client, get_llm_client, get_tts_client
from services.voice_orchestrator import VoiceInterviewOrchestrator
from services.question_generator import QuestionGenerator


router = APIRouter()


@router.post("/session/start")
async def start_voice_session(
    user_id: str = Form(...),
    portfolio_id: Optional[str] = Form(None),
    job_posting_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    음성 면접 세션 시작

    Args:
        user_id: 사용자 ID
        portfolio_id: 포트폴리오 ID (옵션)
        job_posting_id: 공고 ID (옵션)

    Returns:
        {
            "session_id": "...",
            "question": {
                "id": "...",
                "text": "...",
                "audio_url": "...",
                "type": "main"
            }
        }
    """
    # 사용자 확인
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 세션 생성
    session = InterviewSession(
        user_id=user_id,
        portfolio_id=portfolio_id,
        job_posting_id=job_posting_id,
        title="음성 면접",
        status="in_progress"
    )
    db.add(session)
    db.flush()

    # 첫 번째 메인 질문 가져오기
    question_gen = QuestionGenerator()
    first_question = question_gen.get_main_question(0)

    # TTS로 음성 생성
    tts_client = get_tts_client()
    audio_url = await tts_client.synthesize(
        text=first_question["text"],
        speaker="KR",
        speed=1.0
    )

    # 질문 DB 저장
    from models import InterviewQuestion
    question = InterviewQuestion(
        session_id=session.id,
        text=first_question["text"],
        type=first_question["type"],
        source="predefined",
        order=first_question["order"]
    )
    db.add(question)
    db.commit()

    return {
        "session_id": session.id,
        "question": {
            "id": question.id,
            "text": first_question["text"],
            "audio_url": audio_url,
            "type": "main"
        }
    }


@router.post("/answer/complete")
async def complete_answer(
    session_id: str = Form(...),
    question_id: str = Form(...),
    turn_type: str = Form(...),  # "main" or "followup"
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    답변 완료 처리

    Args:
        session_id: 세션 ID
        question_id: 현재 질문 ID
        turn_type: "main" (메인 질문 답변) or "followup" (꼬리질문 답변)
        audio_file: 녹음된 음성 파일

    Returns:
        {
            "answer_text": "...",
            "metrics": {
                "duration_sec": 18.2,
                "word_count": 45,
                "avg_wpm": 150
            },
            "next_question": {
                "id": "...",
                "text": "...",
                "audio_url": "...",
                "type": "followup" | "main" | "end"
            }
        }
    """
    # 세션 확인
    session = db.query(InterviewSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Orchestrator 초기화
    orchestrator = VoiceInterviewOrchestrator(
        stt_client=get_stt_client(),
        llm_client=get_llm_client(),
        tts_client=get_tts_client(),
        db=db
    )

    # 전체 파이프라인 실행
    try:
        result = await orchestrator.process_answer(
            session_id=session_id,
            question_id=question_id,
            audio_file=audio_file,
            turn_type=turn_type
        )

        # 세션 종료 처리
        if result["next_question"]["type"] == "end":
            session.status = "completed"
            from datetime import datetime
            session.completed_at = datetime.utcnow().isoformat()
            db.commit()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )


@router.get("/session/{session_id}/status")
async def get_session_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    세션 상태 조회

    Returns:
        {
            "session_id": "...",
            "status": "in_progress" | "completed",
            "total_questions": 5,
            "answered_questions": 3
        }
    """
    session = db.query(InterviewSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    from models import InterviewQuestion
    total_questions = db.query(InterviewQuestion).filter_by(
        session_id=session_id
    ).count()

    from models import InterviewVideo
    answered_questions = db.query(InterviewVideo).filter_by(
        session_id=session_id
    ).count()

    return {
        "session_id": session.id,
        "status": session.status,
        "total_questions": total_questions,
        "answered_questions": answered_questions
    }
