"""
PDF CV 분석 서비스

PDF에서 텍스트를 추출하고 RAG + Gemini를 사용하여 역량 분석
"""

import os
from typing import Dict, Any
import PyPDF2
from io import BytesIO

from rag.utils import get_competency_matrix
from .gemini_service import GeminiService


class PDFAnalyzer:
    """PDF CV 분석 클래스"""

    def __init__(self):
        self.gemini_service = GeminiService()

    def extract_text_from_pdf(self, pdf_file: bytes) -> str:
        """
        PDF 파일에서 텍스트 추출

        Args:
            pdf_file: PDF 파일 바이트 데이터

        Returns:
            추출된 텍스트
        """
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file))
        text = ""

        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        return text.strip()

    def analyze_cv(
        self,
        pdf_file: bytes,
        role: str,
        level: str = "LEVEL_MID"
    ) -> Dict[str, Any]:
        """
        CV PDF를 분석하여 역량 평가

        Args:
            pdf_file: PDF 파일 바이트 데이터
            role: 직무 ('ROLE_FE' or 'ROLE_BE')
            level: 경력 레벨 (기본값: 'LEVEL_MID')

        Returns:
            역량 평가 결과
            {
                "role": "ROLE_FE",
                "level": "LEVEL_MID",
                "extracted_text": "CV 텍스트...",
                "possessed_skills": ["React", "TypeScript", ...],
                "missing_skills": ["Next.js", "테스트 코드 작성", ...],
                "strengths": [
                    {"skill": "React", "reason": "5년 경력..."},
                    ...
                ],
                "weaknesses": [
                    {"skill": "테스트", "reason": "테스트 경험 부족..."},
                    ...
                ],
                "overall_score": 85,
                "summary": "전반적인 평가 요약"
            }
        """
        # 1. PDF에서 텍스트 추출
        cv_text = self.extract_text_from_pdf(pdf_file)

        if not cv_text:
            return {
                "error": "PDF에서 텍스트를 추출할 수 없습니다.",
                "role": role,
                "level": level
            }

        # 2. RAG에서 해당 직무/레벨의 역량 매트릭스 가져오기
        try:
            competency_matrix = get_competency_matrix(level, role)
        except Exception as e:
            return {
                "error": f"역량 매트릭스를 불러오는데 실패했습니다: {str(e)}",
                "role": role,
                "level": level
            }

        # 3. Gemini API로 분석
        analysis_result = self.gemini_service.analyze_cv_with_competency(
            cv_text=cv_text,
            role=role,
            competency_matrix=competency_matrix
        )

        # 4. 결과에 메타데이터 추가
        analysis_result["level"] = level
        analysis_result["extracted_text"] = cv_text[:500]  # 처음 500자만 저장

        return analysis_result


# 싱글톤 인스턴스
pdf_analyzer = PDFAnalyzer()


def analyze_cv_from_pdf(
    pdf_file: bytes,
    role: str,
    level: str = "LEVEL_MID"
) -> Dict[str, Any]:
    """
    PDF CV 분석 함수 (외부에서 직접 호출 가능)

    Args:
        pdf_file: PDF 파일 바이트 데이터
        role: 직무 ('ROLE_FE' or 'ROLE_BE')
        level: 경력 레벨 (기본값: 'LEVEL_MID')

    Returns:
        역량 평가 결과 JSON
    """
    return pdf_analyzer.analyze_cv(pdf_file, role, level)
