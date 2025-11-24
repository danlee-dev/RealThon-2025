"""
역량 평가 생성 서비스

Portfolio summary를 분석하여 Gemini로 6개 역량에 대한 점수 및 피드백 생성
"""

import os
import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import google.generativeai as genai
from dotenv import load_dotenv

from models import Portfolio, User, CapabilityEvaluation

load_dotenv()

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


# 직무별 역량 카테고리 정의 (6개 고정)
ROLE_CAPABILITIES = {
    "ROLE_FE": [
        {"name_en": "Technical Skills", "name_ko": "기술 역량"},
        {"name_en": "UI/UX Design", "name_ko": "UI/UX 설계"},
        {"name_en": "Performance Optimization", "name_ko": "성능 최적화"},
        {"name_en": "Problem Solving", "name_ko": "문제 해결"},
        {"name_en": "Communication", "name_ko": "커뮤니케이션"},
        {"name_en": "Adaptability", "name_ko": "적응력"}
    ],
    "ROLE_BE": [
        {"name_en": "Technical Skills", "name_ko": "기술 역량"},
        {"name_en": "System Design", "name_ko": "시스템 설계"},
        {"name_en": "Database Management", "name_ko": "데이터베이스 관리"},
        {"name_en": "API Design", "name_ko": "API 설계"},
        {"name_en": "Security", "name_ko": "보안"},
        {"name_en": "DevOps", "name_ko": "데브옵스"}
    ],
    "ROLE_AI": [
        {"name_en": "Technical Skills", "name_ko": "기술 역량"},
        {"name_en": "Model Development", "name_ko": "모델 개발"},
        {"name_en": "Data Processing", "name_ko": "데이터 처리"},
        {"name_en": "Math & Statistics", "name_ko": "수학/통계"},
        {"name_en": "Research Ability", "name_ko": "연구 능력"},
        {"name_en": "MLOps", "name_ko": "MLOps"}
    ]
}


class CapabilityEvaluator:
    """역량 평가 생성 클래스"""

    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.model = genai.GenerativeModel(model_name)

    def evaluate_portfolio_capabilities(
        self,
        portfolio_id: str,
        user_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        포트폴리오를 분석하여 6개 역량 평가 생성

        Args:
            portfolio_id: 포트폴리오 ID
            user_id: 사용자 ID
            db: 데이터베이스 세션

        Returns:
            생성된 역량 평가 데이터
        """
        # 1. Portfolio, User 조회
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise ValueError(f"Portfolio not found: {portfolio_id}")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User not found: {user_id}")

        # 2. portfolio.summary 확인
        if not portfolio.summary:
            raise ValueError("Portfolio summary가 비어 있습니다. 먼저 CV/GitHub 분석을 실행하세요.")

        # 3. summary 파싱
        try:
            summary_data = json.loads(portfolio.summary)
        except json.JSONDecodeError:
            raise ValueError("Portfolio summary가 올바른 JSON 형식이 아닙니다.")

        # 4. 직무별 역량 카테고리 가져오기
        if user.role not in ROLE_CAPABILITIES:
            raise ValueError(f"지원하지 않는 직무입니다: {user.role}")

        capabilities = ROLE_CAPABILITIES[user.role]

        # 5. Gemini로 역량 평가 생성
        print(f"[INFO] Gemini로 역량 평가 생성 중...")
        evaluation_result = self._generate_capability_scores(
            summary_data=summary_data,
            role=user.role,
            capabilities=capabilities
        )

        # 6. DB에 저장
        print(f"[INFO] DB에 역량 평가 저장 중...")
        capability_evaluation = self._save_to_db(
            portfolio_id=portfolio_id,
            role=user.role,
            capabilities=capabilities,
            evaluation_result=evaluation_result,
            db=db
        )

        print(f"[SUCCESS] 역량 평가 생성 완료: {capability_evaluation.id}")

        return {
            "portfolio_id": portfolio_id,
            "role": user.role,
            "evaluations": evaluation_result
        }

    def _generate_capability_scores(
        self,
        summary_data: Dict[str, Any],
        role: str,
        capabilities: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Gemini를 사용하여 각 역량별 점수 및 피드백 생성

        Args:
            summary_data: portfolio.summary 데이터 (cv_analysis, github_analysis 포함)
            role: 직무 (ROLE_FE, ROLE_BE, ROLE_AI)
            capabilities: 6개 역량 카테고리 리스트

        Returns:
            6개 역량에 대한 점수, 이유, 피드백 리스트
        """
        # 역할 이름 매핑
        role_map = {
            "ROLE_FE": "Frontend Developer",
            "ROLE_BE": "Backend Developer",
            "ROLE_AI": "AI/ML Developer"
        }
        role_name = role_map.get(role, "Developer")

        # CV 분석 데이터
        cv_analysis = summary_data.get("cv_analysis", {})
        github_analysis = summary_data.get("github_analysis", {})

        # 역량 카테고리 리스트
        capability_names = [f"{cap['name_ko']} ({cap['name_en']})" for cap in capabilities]

        # Gemini 프롬프트 생성
        prompt = f"""
당신은 개발자 역량을 평가하는 전문가입니다.

아래 {role_name}의 포트폴리오 분석 결과를 바탕으로, 다음 6가지 역량에 대해 각각 점수를 매기고 피드백을 작성해주세요.

# 포트폴리오 분석 결과

## CV 분석
{json.dumps(cv_analysis, ensure_ascii=False, indent=2)}

## GitHub 분석
{json.dumps(github_analysis, ensure_ascii=False, indent=2)}

# 평가 대상 역량 (6개)
{json.dumps(capability_names, ensure_ascii=False, indent=2)}

# 요구사항
각 역량에 대해 다음을 작성해주세요:

1. **점수 (score)**: 0-100 사이의 점수
2. **이유 (reason)**: 해당 점수를 준 근거 (2-3 문장, CV/GitHub 분석 결과 구체적으로 언급)
3. **피드백 (feedback)**:
   - 첫 문장: 현재 수준에 대한 간단한 긍정적 평가 (1문장)
   - 나머지: 해당 역량을 더 기르기 위한 구체적인 개선 방향 및 실천 가능한 액션 아이템 (2-3문장)
   - 예시: "현재 기술 역량은 준수한 수준입니다. 더 발전하기 위해서는 최신 프레임워크(Svelte, Solid.js)를 학습하고 실제 프로젝트에 적용해보세요. 또한 기술 블로그를 작성하여 학습 내용을 정리하고 커뮤니티와 공유하면 깊이 있는 이해가 가능합니다."

# 출력 형식 (반드시 JSON으로만 응답)
{{
  "evaluations": [
    {{
      "capability_index": 1,
      "score": 85,
      "reason": "CV에서 React, TypeScript, Next.js 경험이 풍부하고, GitHub에서 다수의 프론트엔드 프로젝트를 확인할 수 있어 기술 역량이 우수합니다.",
      "feedback": "현재 기술 역량은 우수한 수준입니다. 더 발전하기 위해서는 최신 프론트엔드 프레임워크(Svelte, Solid.js 등)를 학습하고 실제 프로젝트에 적용해보세요. 또한 성능 최적화 관련 블로그 포스팅을 작성하여 학습 내용을 정리하면 더욱 깊이 있는 이해가 가능합니다."
    }},
    {{
      "capability_index": 2,
      "score": 70,
      "reason": "...",
      "feedback": "현재 수준은 양호합니다. ... (개선 방향) ... (구체적 액션)"
    }},
    ... (총 6개)
  ]
}}

중요:
- 반드시 6개 역량 모두에 대해 평가해주세요.
- feedback은 긍정적 평가 1문장 + 개선 방향 2-3문장 형식을 반드시 지켜주세요.
"""

        # Gemini API 호출
        response = self.model.generate_content(prompt)
        result_text = response.text

        # JSON 파싱
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        try:
            result_data = json.loads(result_text)
            evaluations = result_data.get("evaluations", [])

            if len(evaluations) != 6:
                raise ValueError(f"Gemini가 {len(evaluations)}개 역량을 반환했습니다. 6개여야 합니다.")

            return evaluations

        except json.JSONDecodeError as e:
            raise ValueError(f"Gemini 응답을 JSON으로 파싱할 수 없습니다: {str(e)}\n\n응답:\n{result_text}")

    def _save_to_db(
        self,
        portfolio_id: str,
        role: str,
        capabilities: List[Dict[str, str]],
        evaluation_result: List[Dict[str, Any]],
        db: Session
    ) -> CapabilityEvaluation:
        """
        생성된 역량 평가를 DB에 저장

        Args:
            portfolio_id: 포트폴리오 ID
            role: 직무
            capabilities: 6개 역량 카테고리
            evaluation_result: Gemini가 생성한 평가 결과
            db: 데이터베이스 세션

        Returns:
            저장된 CapabilityEvaluation 객체
        """
        # 기존 평가 삭제 (있다면)
        existing = db.query(CapabilityEvaluation).filter(
            CapabilityEvaluation.portfolio_id == portfolio_id
        ).first()

        if existing:
            db.delete(existing)
            db.commit()
            print(f"[INFO] 기존 역량 평가 삭제됨: {existing.id}")

        # 새로운 평가 생성
        capability_data = {}

        for i, (capability, evaluation) in enumerate(zip(capabilities, evaluation_result), start=1):
            capability_data[f"capability{i}_name_en"] = capability["name_en"]
            capability_data[f"capability{i}_name_ko"] = capability["name_ko"]
            capability_data[f"capability{i}_score"] = float(evaluation["score"])
            capability_data[f"capability{i}_reason"] = evaluation["reason"]
            capability_data[f"capability{i}_feedback"] = evaluation["feedback"]

        capability_evaluation = CapabilityEvaluation(
            portfolio_id=portfolio_id,
            role=role,
            **capability_data
        )

        db.add(capability_evaluation)
        db.commit()
        db.refresh(capability_evaluation)

        return capability_evaluation


# 싱글톤 인스턴스
capability_evaluator = CapabilityEvaluator()


def evaluate_portfolio_capabilities(
    portfolio_id: str,
    user_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    포트폴리오 역량 평가 생성 (외부에서 직접 호출 가능)

    Args:
        portfolio_id: 포트폴리오 ID
        user_id: 사용자 ID
        db: 데이터베이스 세션

    Returns:
        생성된 역량 평가 데이터
    """
    return capability_evaluator.evaluate_portfolio_capabilities(
        portfolio_id, user_id, db
    )
