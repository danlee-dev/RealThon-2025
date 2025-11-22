"""
CV 분석 서비스

유저의 CV 파일을 분석하여 역량 평가 및 강점/약점 분석
"""

import os
import json
from typing import Dict, Any
from io import BytesIO
from sqlalchemy.orm import Session
from PIL import Image

from models import User, Portfolio
from rag.utils import get_competency_matrix
from .gemini_service import GeminiService


class CVAnalyzer:
    """CV 분석 클래스"""

    def __init__(self):
        self.gemini_service = GeminiService()

    def extract_text_from_file(self, file_path: str) -> str:
        """
        파일에서 텍스트 추출 (이미지 또는 PDF)

        Args:
            file_path: 파일 경로

        Returns:
            추출된 텍스트
        """
        import PyPDF2

        # 파일 확장자 확인
        file_ext = os.path.splitext(file_path)[1].lower()

        # PDF 파일인 경우
        if file_ext == '.pdf':
            # 파일 읽기
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            # PyPDF2로 텍스트 추출 시도
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                text = text.strip()

                # 텍스트가 충분히 추출된 경우 반환
                if text and len(text) > 100:
                    return text
            except Exception:
                pass

            # PyPDF2 실패 시 Gemini Vision 사용 (이미지 기반 PDF)
            return self._extract_with_gemini_vision_pdf(file_path)

        # 이미지 파일인 경우
        else:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            return self._extract_with_gemini_vision(file_bytes)

    def _extract_with_gemini_vision_pdf(self, file_path: str) -> str:
        """
        Gemini Vision API를 사용하여 PDF에서 텍스트 추출

        Args:
            file_path: PDF 파일 경로

        Returns:
            추출된 텍스트
        """
        import google.generativeai as genai

        try:
            # PDF 파일 업로드
            file = genai.upload_file(file_path, mime_type="application/pdf")

            # Gemini API로 텍스트 추출
            prompt = """
            이 PDF는 개발자의 이력서(CV)입니다.
            PDF에서 모든 텍스트를 정확하게 추출하여 일반 텍스트 형식으로 변환해주세요.

            다음 정보를 포함해주세요:
            - 이름, 이메일, GitHub, 블로그 등 개인 정보
            - 경력 사항 (회사명, 기간, 업무 내용)
            - 프로젝트 경험
            - 기술 스택
            - 학력
            - 수상 경력
            - 커뮤니티 활동
            - 발표/기고/출판/교육 경험

            한글과 영문을 정확하게 읽어주세요.
            불필요한 마크다운 형식은 제거하고 순수 텍스트로만 반환해주세요.
            """

            response = self.gemini_service.model.generate_content([prompt, file])
            return response.text.strip()

        except Exception as e:
            raise Exception(f"Gemini Vision으로 PDF 텍스트 추출 실패: {str(e)}")

    def _extract_with_gemini_vision(self, file_bytes: bytes) -> str:
        """
        Gemini Vision API를 사용하여 이미지에서 텍스트 추출

        Args:
            file_bytes: 이미지 파일 바이트 데이터

        Returns:
            추출된 텍스트
        """
        try:
            img = Image.open(BytesIO(file_bytes))

            prompt = """
            이 이미지는 개발자의 이력서(CV)입니다.
            이미지에서 모든 텍스트를 정확하게 추출하여 일반 텍스트 형식으로 변환해주세요.

            다음 정보를 포함해주세요:
            - 이름, 이메일, GitHub, 블로그 등 개인 정보
            - 경력 사항 (회사명, 기간, 업무 내용)
            - 프로젝트 경험
            - 기술 스택
            - 학력
            - 수상 경력
            - 커뮤니티 활동
            - 발표/기고/출판/교육 경험

            한글과 영문을 정확하게 읽어주세요.
            불필요한 마크다운 형식은 제거하고 순수 텍스트로만 반환해주세요.
            """

            response = self.gemini_service.model.generate_content([prompt, img])
            return response.text.strip()

        except Exception as e:
            raise Exception(f"Gemini Vision으로 이미지 텍스트 추출 실패: {str(e)}")

    def analyze_cv(
        self,
        portfolio_id: str,
        user_id: str,
        db: Session,
        role: str = None,
        level: str = None
    ) -> Dict[str, Any]:
        """
        CV 분석 메인 함수

        Args:
            portfolio_id: 포트폴리오 ID
            user_id: 사용자 ID
            db: 데이터베이스 세션
            role: 직무 (선택, 기본값: User.role)
            level: 경력 레벨 (선택, 기본값: User.level)

        Returns:
            분석 결과
            {
                "portfolio_id": "...",
                "user_id": "...",
                "role": "ROLE_FE",
                "level": "LEVEL_MID",
                "extracted_text": "...",
                "possessed_skills": [...],
                "missing_skills": [...],
                "strengths": [...],
                "weaknesses": [...],
                "overall_score": 85,
                "summary": "..."
            }
        """
        # 1. DB에서 Portfolio, User 조회
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise ValueError(f"Portfolio not found: {portfolio_id}")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User not found: {user_id}")

        # 2. role, level 기본값 설정
        if not role:
            role = user.role
        if not level:
            level = user.level

        # 3. 파일 경로 확인
        file_url = portfolio.file_url
        # /static/uploads/FE.pdf -> backend/static/uploads/FE.pdf
        file_path = os.path.join(os.path.dirname(__file__), "..", file_url.lstrip("/"))

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CV 파일을 찾을 수 없습니다: {file_path}")

        # 4. 텍스트 추출
        print(f"[INFO] Extracting text from {file_path}...")
        extracted_text = self.extract_text_from_file(file_path)

        if not extracted_text:
            raise ValueError("텍스트 추출에 실패했습니다.")

        print(f"[INFO] Extracted {len(extracted_text)} characters")

        # 5. RAG 역량 매트릭스 조회
        print(f"[INFO] Fetching competency matrix for {level}, {role}...")
        try:
            competency_matrix = get_competency_matrix(level, role)
        except Exception as e:
            raise ValueError(f"역량 매트릭스 조회 실패: {str(e)}")

        # 6. Gemini로 분석
        print(f"[INFO] Analyzing CV with Gemini API...")
        analysis_result = self.gemini_service.analyze_cv_with_competency(
            cv_text=extracted_text,
            role=role,
            competency_matrix=competency_matrix
        )

        # 7. DB 업데이트
        print(f"[INFO] Saving analysis to database...")
        self.save_analysis_to_db(
            portfolio=portfolio,
            extracted_text=extracted_text,
            analysis=analysis_result,
            db=db
        )

        # 8. 결과 반환
        result = {
            "portfolio_id": portfolio_id,
            "user_id": user_id,
            "role": role,
            "level": level,
            "extracted_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            **analysis_result
        }

        return result

    def save_analysis_to_db(
        self,
        portfolio: Portfolio,
        extracted_text: str,
        analysis: Dict[str, Any],
        db: Session
    ):
        """
        분석 결과를 DB에 저장

        Args:
            portfolio: Portfolio 객체
            extracted_text: 추출된 텍스트
            analysis: 분석 결과
            db: 데이터베이스 세션
        """
        # Portfolio 업데이트
        portfolio.parsed_text = extracted_text
        portfolio.summary = json.dumps(analysis, ensure_ascii=False)

        db.commit()
        db.refresh(portfolio)

        print(f"[SUCCESS] Analysis saved to portfolio {portfolio.id}")


# 싱글톤 인스턴스
cv_analyzer = CVAnalyzer()


def analyze_cv_pipeline(
    portfolio_id: str,
    user_id: str,
    db: Session,
    role: str = None,
    level: str = None
) -> Dict[str, Any]:
    """
    CV 분석 파이프라인 (외부에서 직접 호출 가능)

    Args:
        portfolio_id: 포트폴리오 ID
        user_id: 사용자 ID
        db: 데이터베이스 세션
        role: 직무 (선택)
        level: 경력 레벨 (선택)

    Returns:
        분석 결과
    """
    return cv_analyzer.analyze_cv(portfolio_id, user_id, db, role, level)
