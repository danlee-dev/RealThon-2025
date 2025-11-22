"""
LLM 기반 역량 분석 서비스

Google Gemini API를 사용한 CV 및 GitHub 데이터 분석
"""

import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Gemini API 설정
# GEMINI_API_KEY는 이제 동적으로 로드하여 사용합니다.


class LLMAnalyzer:
    """LLM 기반 역량 분석 클래스 (Gemini API 사용)"""

    def __init__(self, model_name: str = None):
        """
        Args:
            model_name: 사용할 Gemini 모델 이름 (기본값: 환경변수 또는 gemini-1.5-flash)
        """
        if model_name is None:
            # 모델명 업데이트: 2.0-flash-exp -> 1.5-flash (안정성 및 쿼터 확보)
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.model_name = model_name

    def get_api_keys(self) -> List[str]:
        """환경변수에서 사용 가능한 모든 Gemini API 키를 가져옵니다."""
        keys = []
        # GEMINI_API_KEY1 ~ 3 확인
        for i in range(1, 4):
            key = os.getenv(f"GEMINI_API_KEY{i}")
            if key:
                keys.append(key)
        
        # 레거시 키 확인
        legacy_key = os.getenv("GEMINI_API_KEY")
        if legacy_key and legacy_key not in keys:
            keys.append(legacy_key)
            
        return keys

    def _generate_content(self, prompt: str) -> Any:
        """
        여러 API 키를 순차적으로 시도하여 컨텐츠를 생성합니다.
        """
        api_keys = self.get_api_keys()
        if not api_keys:
            raise Exception("No Gemini API keys found in environment variables.")

        last_error = None
        for i, api_key in enumerate(api_keys):
            try:
                # API 키 설정
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(self.model_name)
                
                # 생성 요청
                return model.generate_content(prompt)
                
            except Exception as e:
                last_error = e
                print(f"⚠️ Gemini API Key #{i+1} failed: {str(e)[:200]}...")
                continue
        
        # 모든 키 실패 시 마지막 에러 발생
        raise last_error or Exception("All Gemini API keys failed.")

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

        response = self._generate_content(prompt)
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

        response = self._generate_content(prompt)
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

    def parse_job_posting(self, raw_text: str, company_name: str, position: str, source_url: str = "") -> Dict[str, Any]:
        """
        직무 공고 텍스트를 분석하여 구조화된 JSON으로 변환
        
        Args:
            raw_text: 크롤링된 공고 텍스트
            company_name: 회사명
            position: 직무명
            source_url: 원본 URL (선택)
            
        Returns:
            구조화된 공고 정보 JSON
        """
        prompt = f"""
당신은 채용 공고 분석 전문가입니다.
아래의 채용 공고 텍스트를 분석하여 구조화된 JSON 형식으로 변환해주세요.

# 회사 정보
회사명: {company_name}
직무명: {position}
원본 URL: {source_url}

# 공고 내용
{raw_text}

# 요구사항
1. 공고 내용에서 핵심 정보를 추출하여 아래 JSON 구조에 맞춰 정리해주세요.
2. 경력 연차는 "N년 이상" 또는 "신입", "무관" 등으로 통일해주세요.
3. 고용 형태는 "정규직", "계약직", "인턴" 등으로 명시해주세요.
4. 기술 스택은 영어 원문 그대로(예: Python, AWS) 추출해주세요.
5. 주요 업무(responsibilities), 자격 요건(qualifications), 우대 사항(preferred_qualifications)은 리스트 형태로 정리해주세요.
6. 입력받은 원본 URL을 "url" 필드에 그대로 포함시켜주세요.

# 출력 형식 (반드시 JSON으로만 응답)
{{
  "company": "{company_name}",
  "position": "{position}",
  "url": "{source_url}",
  "experience_years": "3년 이상",
  "employment_type": "정규직",
  "required_skills": [
    "Python",
    "Django"
  ],
  "preferred_skills": [
    "AWS",
    "Docker"
  ],
  "responsibilities": [
    "서버 개발",
    "API 설계"
  ],
  "qualifications": [
    "Python 개발 경험",
    "CS 지식 보유"
  ],
  "preferred_qualifications": [
    "관련 학과 전공",
    "정보처리기사 자격증"
  ]
}}
"""
        try:
            response = self._generate_content(prompt)
            result_text = response.text.strip()
            
            # JSON 파싱 (마크다운 코드블록 제거)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
                
            return json.loads(result_text)
        except Exception as e:
            print(f"Job posting parsing error: {e}")
            # 실패 시 기본 구조 반환 (프론트엔드 호환성 유지)
            return {
                "company": company_name,
                "position": position,
                "url": source_url,
                "experience_years": "공백",
                "employment_type": "공백",
                "required_skills": ["공백"],
                "preferred_skills": ["공백"],
                "responsibilities": ["공백"],
                "qualifications": ["공백"],
                "preferred_qualifications": ["공백"],
                "raw_text_summary": raw_text[:500] + "...",
                "error": str(e)
            }

    def generate_initial_questions(
        self,
        portfolio_text: str,
        job_posting_text: str
    ) -> List[Dict[str, str]]:
        """
        초기 면접 질문 3개를 생성합니다.
        
        Args:
            portfolio_text: 포트폴리오 내용 (요약 또는 전체)
            job_posting_text: 직무 공고 내용
            
        Returns:
            질문 리스트 (type, text)
        """
        prompt = f"""
당신은 전문 기술 면접관입니다.
지원자의 포트폴리오와 채용 공고를 바탕으로 면접 질문 3개를 생성해주세요.

# 채용 공고
{job_posting_text}

# 지원자 포트폴리오
{portfolio_text}

# 질문 생성 규칙 (반드시 아래 3가지 유형으로 하나씩 생성)

1. 약점 질문 (Weakness)
   - 정의: 직무(채용 공고)에서는 중요하게 요구하지만, 포트폴리오에는 드러나지 않거나 부족해 보이는 역량에 대한 질문입니다.
   - 기준: 반드시 '직무 공고'를 기준으로 판단하세요.

2. 포트폴리오 검증 질문 (Portfolio Verification)
   - 정의: 포트폴리오에 기재된 프로젝트 경험, 성과, 기술 사용에 대한 사실 여부와 깊이를 검증하는 질문입니다.
   - 내용: 포트폴리오의 구체적인 내용을 언급하며 질문하세요.

3. 직무 관련 질문 (Job Competency)
   - 정의: 업로드한 직무 공고에서 요구하는 핵심 역량 전반에 대한 질문입니다.
   - 내용: 해당 직무를 수행하기 위해 필수적인 지식이나 문제 해결 능력을 묻습니다.

# 출력 형식 (반드시 JSON 배열로만 응답)
[
  {{
    "type": "weakness",
    "text": "질문 내용"
  }},
  {{
    "type": "portfolio",
    "text": "질문 내용"
  }},
  {{
    "type": "job",
    "text": "질문 내용"
  }}
]
"""
        try:
            response = self._generate_content(prompt)
            result_text = response.text.strip()
            
            # JSON 파싱
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
                
            questions = json.loads(result_text)
            return questions
            
        except Exception as e:
            print(f"Initial question generation failed: {e}")
            # 실패 시 기본 질문 반환
            return [
                {"type": "weakness", "text": "직무 공고에서 요구하는 기술 중 본인이 가장 부족하다고 생각하는 것은 무엇이며, 이를 보완하기 위해 어떤 노력을 하고 있나요?"},
                {"type": "portfolio", "text": "포트폴리오에 기재된 프로젝트 중 가장 도전적이었던 경험에 대해 구체적으로 설명해주세요."},
                {"type": "job", "text": "이 직무에 지원하게 된 동기와 본인이 이 직무에 적합하다고 생각하는 이유는 무엇인가요?"}
            ]

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

        # 역할 이름 매핑
        role_map = {
            "ROLE_FE": "Frontend Developer",
            "ROLE_BE": "Backend Developer",
            "ROLE_AI": "AI/ML Developer"
        }
        role_name = role_map.get(role, "Developer")

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

        # 역할 이름 매핑
        role_map = {
            "ROLE_FE": "Frontend Developer",
            "ROLE_BE": "Backend Developer",
            "ROLE_AI": "AI/ML Developer"
        }
        role_name = role_map.get(role, "Developer")

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
