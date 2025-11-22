"""
음성 면접 파이프라인 오케스트레이터

STT → LLM → TTS 전체 흐름 관리
"""

import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from clients.base import STTClient, LLMClient, TTSClient
from models import (
    InterviewSession,
    InterviewQuestion,
    InterviewVideo,
    InterviewTranscript,
    Portfolio
)
from utils.audio_utils import save_upload_file, convert_to_wav, get_audio_duration
from services.question_generator import QuestionGenerator


class VoiceInterviewOrchestrator:
    """
    음성 면접 전체 파이프라인 관리

    흐름:
    1. 오디오 파일 저장 및 변환 (webm → wav)
    2. STT: 음성 → 텍스트
    3. DB 저장: InterviewVideo, InterviewTranscript
    4. LLM: 포트폴리오 + 답변 기반 꼬리질문 생성
    5. TTS: 꼬리질문 → 음성
    6. 응답 반환
    """

    def __init__(
        self,
        stt_client: STTClient,
        llm_client: LLMClient,
        tts_client: TTSClient,
        db: Session
    ):
        self.stt = stt_client
        self.llm = llm_client
        self.tts = tts_client
        self.db = db
        self.question_gen = QuestionGenerator()

    async def process_answer(
        self,
        session_id: str,
        question_id: str,
        audio_file: UploadFile,
        turn_type: str  # "main" or "followup"
    ) -> Dict[str, Any]:
        """
        답변 처리 전체 파이프라인

        Args:
            session_id: 세션 ID
            question_id: 현재 질문 ID
            audio_file: 녹음된 음성 파일
            turn_type: "main" (메인 질문 답변) or "followup" (꼬리질문 답변)

        Returns:
            {
                "answer_text": "...",
                "metrics": {...},
                "next_question": {...}
            }
        """
        # 1. 세션 정보 가져오기
        session = self.db.query(InterviewSession).filter_by(id=session_id).first()
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # 2. 오디오 파일 저장 및 변환
        upload_dir = Path("uploads/audio")
        upload_dir.mkdir(parents=True, exist_ok=True)

        original_path = str(upload_dir / f"{uuid.uuid4()}_{audio_file.filename}")
        await save_upload_file(audio_file, original_path)

        # webm → wav 변환
        wav_path = convert_to_wav(original_path)
        duration = get_audio_duration(wav_path)

        # 3. STT: 음성 → 텍스트
        transcript_text = await self.stt.transcribe(wav_path, language="ko")

        # 4. DB 저장: InterviewVideo
        video = InterviewVideo(
            user_id=session.user_id,
            session_id=session_id,
            question_id=question_id,
            video_url=original_path,  # 원본 파일
            audio_url=wav_path,       # 변환된 WAV
            duration_sec=duration
        )
        self.db.add(video)
        self.db.flush()  # ID 생성

        # 5. DB 저장: InterviewTranscript
        transcript = InterviewTranscript(
            video_id=video.id,
            text=transcript_text,
            language="ko"
        )
        self.db.add(transcript)

        # 6. 다음 질문 생성
        next_question = await self._generate_next_question(
            session, question_id, transcript_text, turn_type
        )

        # 7. 다음 질문 DB 저장
        if next_question["type"] != "end":
            question = InterviewQuestion(
                session_id=session_id,
                text=next_question["text"],
                type=next_question["question_type"],
                source="llm" if next_question["question_type"] == "followup" else "predefined",
                order=next_question["order"]
            )
            self.db.add(question)
            next_question["id"] = question.id

        self.db.commit()

        # 8. 응답 구성
        return {
            "answer_text": transcript_text,
            "metrics": {
                "duration_sec": duration,
                "word_count": len(transcript_text.split()),
                "avg_wpm": (len(transcript_text.split()) / duration * 60) if duration > 0 else 0
            },
            "next_question": next_question
        }

    async def _generate_next_question(
        self,
        session: InterviewSession,
        current_question_id: str,
        user_answer: str,
        turn_type: str
    ) -> Dict[str, Any]:
        """
        다음 질문 생성 (꼬리질문 or 다음 메인 질문)

        Args:
            session: 면접 세션
            current_question_id: 현재 질문 ID
            user_answer: 사용자 답변 텍스트
            turn_type: "main" or "followup"

        Returns:
            다음 질문 딕셔너리
        """
        # 메인 질문에 대한 답변 → 꼬리질문 생성
        if turn_type == "main":
            return await self._generate_followup_question(
                session, current_question_id, user_answer
            )
        # 꼬리질문에 대한 답변 → 다음 메인 질문
        else:
            return await self._get_next_main_question(session)

    async def _generate_followup_question(
        self,
        session: InterviewSession,
        current_question_id: str,
        user_answer: str
    ) -> Dict[str, Any]:
        """
        LLM으로 꼬리질문 생성

        포트폴리오 정보 + 현재 질문 + 사용자 답변 → 꼬리질문
        """
        # 포트폴리오 정보 가져오기
        portfolio_text = ""
        if session.portfolio_id:
            portfolio = self.db.query(Portfolio).filter_by(id=session.portfolio_id).first()
            if portfolio and portfolio.parsed_text:
                portfolio_text = portfolio.parsed_text

        # 현재 질문 텍스트
        current_question = self.db.query(InterviewQuestion).filter_by(
            id=current_question_id
        ).first()
        current_question_text = current_question.text if current_question else ""

        # 프롬프트 생성
        from clients.gemini_client import GeminiClient
        if isinstance(self.llm, GeminiClient):
            prompt = self.llm.build_followup_prompt(
                portfolio_text=portfolio_text,
                current_question=current_question_text,
                user_answer=user_answer
            )
        else:
            # A6000 클라이언트도 같은 메서드 있음
            prompt = self.llm.build_followup_prompt(
                portfolio_text=portfolio_text,
                current_question=current_question_text,
                user_answer=user_answer
            )

        # LLM으로 꼬리질문 생성
        followup_text = await self.llm.generate(prompt, max_tokens=150)

        # TTS로 음성 생성
        audio_url = await self.tts.synthesize(
            text=followup_text,
            speaker="KR",
            speed=1.0
        )

        return {
            "id": f"followup_{uuid.uuid4()}",
            "text": followup_text,
            "audio_url": audio_url,
            "type": "question",
            "question_type": "followup",
            "order": 0  # 꼬리질문은 순서 없음
        }

    async def _get_next_main_question(
        self,
        session: InterviewSession
    ) -> Dict[str, Any]:
        """
        다음 메인 질문 가져오기

        세션의 현재 진행 상황을 보고 다음 메인 질문 반환
        """
        # 세션에 몇 개의 메인 질문이 있었는지 확인
        main_questions_count = self.db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == session.id,
            InterviewQuestion.source == "predefined"
        ).count()

        # 다음 메인 질문 가져오기
        next_question_data = self.question_gen.get_main_question(main_questions_count)

        # 종료 질문인 경우
        if next_question_data["type"] == "end":
            return {
                "id": "end",
                "text": next_question_data["text"],
                "audio_url": "",
                "type": "end",
                "question_type": "end",
                "order": 999
            }

        # TTS로 음성 생성
        audio_url = await self.tts.synthesize(
            text=next_question_data["text"],
            speaker="KR",
            speed=1.0
        )

        return {
            "id": next_question_data["id"],
            "text": next_question_data["text"],
            "audio_url": audio_url,
            "type": "question",
            "question_type": "main",
            "order": next_question_data["order"]
        }
