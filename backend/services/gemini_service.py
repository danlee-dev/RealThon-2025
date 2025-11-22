"""
Gemini API 연동 서비스

Google Gemini API를 사용한 텍스트 분석 및 역량 평가
"""

import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class GeminiService:
    """Gemini API 서비스 클래스"""

    def __init__(self, model_name: str = None):
        """
        Args:
            model_name: 사용할 Gemini 모델 이름 (기본값: 환경변수 또는 gemini-2.5-flash)
        """
        if model_name is None:
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.model = genai.GenerativeModel(model_name)

    def analyze_cv_with_competency(
        self,
        cv_text: str,
        role: str,
        competency_matrix: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        CV 텍스트를 분석하여 역량 평가

        Args:
            cv_text: PDF에서 추출된 CV 텍스트
            role: 직무 ('ROLE_FE' or 'ROLE_BE')
            competency_matrix: RAG에서 가져온 역량 매트릭스

        Returns:
            역량 평가 결과 JSON
        """
        prompt = self._build_cv_analysis_prompt(cv_text, role, competency_matrix)

        response = self.model.generate_content(prompt)
        result_text = response.text

        # JSON 파싱 (마크다운 코드블록 제거)
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 기본 구조 반환
            return {
                "role": role,
                "possessed_skills": [],
                "missing_skills": [],
                "strengths": [],
                "weaknesses": [],
                "overall_score": 0,
                "analysis": result_text
            }

    def analyze_github_with_competency(
        self,
        github_data: Dict[str, Any],
        role: str,
        competency_matrix: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        GitHub 프로필 데이터를 분석하여 역량 평가

        Args:
            github_data: GitHub API에서 가져온 데이터
            role: 직무 ('ROLE_FE' or 'ROLE_BE')
            competency_matrix: RAG에서 가져온 역량 매트릭스

        Returns:
            역량 평가 결과 JSON
        """
        prompt = self._build_github_analysis_prompt(github_data, role, competency_matrix)

        response = self.model.generate_content(prompt)
        result_text = response.text

        # JSON 파싱
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            return {
                "role": role,
                "possessed_skills": [],
                "missing_skills": [],
                "strengths": [],
                "weaknesses": [],
                "overall_score": 0,
                "analysis": result_text
            }

    def _build_cv_analysis_prompt(
        self,
        cv_text: str,
        role: str,
        competency_matrix: Dict[str, Any]
    ) -> str:
        """CV 분석을 위한 프롬프트 생성"""

        must_have_skills = competency_matrix.get("must_have", {}).get("technical_skills", [])
        nice_to_have_skills = competency_matrix.get("nice_to_have", {}).get("technical_skills", [])

        must_have_list = [skill["skill"] for skill in must_have_skills]
        nice_to_have_list = [skill["skill"] for skill in nice_to_have_skills]

        role_name = "Frontend Developer" if role == "ROLE_FE" else "Backend Developer"

        prompt = f"""
당신은 개발자 역량을 평가하는 전문가입니다.

아래 CV를 분석하여 {role_name} 직무에 대한 역량을 평가해주세요.

# CV 내용
{cv_text}

# 평가 기준 - 필수 역량
{json.dumps(must_have_list, ensure_ascii=False, indent=2)}

# 평가 기준 - 우대 역량
{json.dumps(nice_to_have_list, ensure_ascii=False, indent=2)}

# 요구사항
1. CV에서 보유하고 있는 기술 스택과 역량을 파악하세요.
2. 필수 역량 중 보유한 것과 부족한 것을 구분하세요.
3. 우대 역량 중 보유한 것이 있다면 강점으로 표시하세요.
4. 전반적인 역량 점수를 100점 만점으로 평가하세요.
5. 월등한 부분(강점)과 부족한 부분(약점)을 각각 3개씩 도출하세요.

# 출력 형식 (반드시 JSON으로만 응답)
{{
  "role": "{role}",
  "possessed_skills": ["보유한 기술/역량 리스트"],
  "missing_skills": ["부족한 필수 역량 리스트"],
  "strengths": [
    {{
      "skill": "강점 기술/역량",
      "reason": "왜 강점인지 설명"
    }}
  ],
  "weaknesses": [
    {{
      "skill": "약점 기술/역량",
      "reason": "왜 약점인지 설명"
    }}
  ],
  "overall_score": 85,
  "summary": "전반적인 평가 요약 (2-3 문장)"
}}
"""
        return prompt

    def _build_github_analysis_prompt(
        self,
        github_data: Dict[str, Any],
        role: str,
        competency_matrix: Dict[str, Any]
    ) -> str:
        """GitHub 분석을 위한 프롬프트 생성"""

        must_have_skills = competency_matrix.get("must_have", {}).get("technical_skills", [])
        nice_to_have_skills = competency_matrix.get("nice_to_have", {}).get("technical_skills", [])

        must_have_list = [skill["skill"] for skill in must_have_skills]
        nice_to_have_list = [skill["skill"] for skill in nice_to_have_skills]

        role_name = "Frontend Developer" if role == "ROLE_FE" else "Backend Developer"

        prompt = f"""
당신은 개발자 역량을 평가하는 전문가입니다.

아래 GitHub 프로필 정보를 분석하여 {role_name} 직무에 대한 역량을 평가해주세요.

# GitHub 프로필 정보
{json.dumps(github_data, ensure_ascii=False, indent=2)}

# 평가 기준 - 필수 역량
{json.dumps(must_have_list, ensure_ascii=False, indent=2)}

# 평가 기준 - 우대 역량
{json.dumps(nice_to_have_list, ensure_ascii=False, indent=2)}

# 요구사항
1. 저장소의 언어 사용 비율, README, 프로젝트 설명을 분석하세요.
2. 필수 역량 중 보유한 것과 부족한 것을 구분하세요.
3. 우대 역량 중 보유한 것이 있다면 강점으로 표시하세요.
4. 커밋 활동, 프로젝트 복잡도, 코드 품질을 고려하세요.
5. 전반적인 역량 점수를 100점 만점으로 평가하세요.
6. 월등한 부분(강점)과 부족한 부분(약점)을 각각 3개씩 도출하세요.

# 출력 형식 (반드시 JSON으로만 응답)
{{
  "role": "{role}",
  "possessed_skills": ["보유한 기술/역량 리스트"],
  "missing_skills": ["부족한 필수 역량 리스트"],
  "strengths": [
    {{
      "skill": "강점 기술/역량",
      "reason": "왜 강점인지 설명"
    }}
  ],
  "weaknesses": [
    {{
      "skill": "약점 기술/역량",
      "reason": "왜 약점인지 설명"
    }}
  ],
  "overall_score": 75,
  "summary": "전반적인 평가 요약 (2-3 문장)"
}}
"""
        return prompt
