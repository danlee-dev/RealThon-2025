"""
면접 질문 및 시나리오 생성 모듈

포트폴리오 분석 결과를 바탕으로 맞춤형 면접 질문 및 시나리오 생성
"""

import json
import os
from typing import List, Dict, Any


def load_reference_data(filename: str) -> Dict[str, Any]:
    """
    레퍼런스 JSON 파일 로드

    Args:
        filename: 파일명 (예: 'competency_matrix.json')

    Returns:
        JSON 데이터
    """
    base_path = os.path.join(os.path.dirname(__file__), "..", "data", "reference")
    file_path = os.path.join(base_path, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_competency_matrix(level: str, role: str) -> Dict[str, Any]:
    """
    특정 레벨과 역할에 대한 역량 매트릭스 반환

    Args:
        level: 'LEVEL_JUNIOR', 'LEVEL_MID', 'LEVEL_SENIOR', 'LEVEL_STAFF'
        role: 'ROLE_FE', 'ROLE_BE', 'ROLE_AI'

    Returns:
        해당 레벨/역할의 역량 매트릭스
    """
    matrix = load_reference_data("competency_matrix.json")

    # 레벨+역할 조합 찾기
    key_map = {
        ("LEVEL_JUNIOR", "ROLE_FE"): "FE_JUNIOR",
        ("LEVEL_MID", "ROLE_FE"): "FE_MID",
        ("LEVEL_JUNIOR", "ROLE_BE"): "BE_JUNIOR",
        ("LEVEL_MID", "ROLE_BE"): "BE_MID",
        ("LEVEL_JUNIOR", "ROLE_AI"): "AI_JUNIOR",
        ("LEVEL_MID", "ROLE_AI"): "AI_MID",
    }

    competency_key = key_map.get((level, role))
    if not competency_key:
        raise ValueError(f"Invalid level/role combination: {level}, {role}")

    return matrix["competencies"][competency_key]


def generate_interview_questions(
    missing_competencies: List[str],
    level: str,
    role: str,
    max_questions: int = 10
) -> List[Dict[str, Any]]:
    """
    부족한 역량에 대한 면접 질문 생성

    Args:
        missing_competencies: 부족한 역량 ID 리스트
        level: 레벨
        role: 역할
        max_questions: 최대 질문 개수

    Returns:
        선택된 면접 질문 리스트
    """
    questions_bank = load_reference_data("interview_questions.json")

    # 레벨+역할 키 매핑
    key_map = {
        ("LEVEL_JUNIOR", "ROLE_FE"): "FE_JUNIOR",
        ("LEVEL_MID", "ROLE_FE"): "FE_MID",
        ("LEVEL_JUNIOR", "ROLE_BE"): "BE_JUNIOR",
        ("LEVEL_MID", "ROLE_BE"): "BE_MID",
        ("LEVEL_JUNIOR", "ROLE_AI"): "AI_JUNIOR",
        ("LEVEL_MID", "ROLE_AI"): "AI_MID",
    }

    question_key = key_map.get((level, role))
    if not question_key:
        return []

    all_questions = questions_bank["questions"].get(question_key, [])

    # 부족한 역량에 해당하는 질문 필터링
    selected_questions = []
    for question in all_questions:
        if question["competency_id"] in missing_competencies:
            selected_questions.append(question)

        if len(selected_questions) >= max_questions:
            break

    return selected_questions


def generate_interview_scenario(
    candidate_name: str,
    level: str,
    role: str,
    possessed_competencies: List[str],
    missing_competencies: List[str],
    main_project: str = ""
) -> Dict[str, Any]:
    """
    맞춤형 면접 시나리오 생성

    Args:
        candidate_name: 지원자 이름
        level: 레벨
        role: 역할
        possessed_competencies: 보유 역량 ID 리스트
        missing_competencies: 부족한 역량 ID 리스트
        main_project: 주요 프로젝트명

    Returns:
        면접 시나리오
    """
    templates = load_reference_data("scenario_templates.json")

    # 레벨+역할 키 매핑
    key_map = {
        ("LEVEL_JUNIOR", "ROLE_FE"): "FE_JUNIOR",
        ("LEVEL_MID", "ROLE_FE"): "FE_MID",
        ("LEVEL_JUNIOR", "ROLE_BE"): "BE_JUNIOR",
        ("LEVEL_MID", "ROLE_BE"): "BE_MID",
        ("LEVEL_JUNIOR", "ROLE_AI"): "AI_JUNIOR",
        ("LEVEL_MID", "ROLE_AI"): "AI_MID",
    }

    template_key = key_map.get((level, role))
    if not template_key:
        return {}

    template = templates["templates"][template_key]

    # 개인화 변수 치환
    scenario = _personalize_scenario(
        template,
        candidate_name,
        possessed_competencies,
        missing_competencies,
        main_project
    )

    # 부족한 역량에 대한 질문 추가
    questions = generate_interview_questions(missing_competencies, level, role)
    scenario["technical_questions"] = questions

    return scenario


def _personalize_scenario(
    template: Dict[str, Any],
    name: str,
    possessed: List[str],
    missing: List[str],
    project: str
) -> Dict[str, Any]:
    """
    템플릿 개인화 (내부 함수)
    """
    scenario = template.copy()

    # Introduction 섹션 개인화
    if "introduction" in scenario:
        intro = scenario["introduction"]
        if isinstance(intro.get("greeting"), str):
            intro["greeting"] = intro["greeting"].replace("{이름}", name)

        if isinstance(intro.get("portfolio_overview"), str):
            # 강점 요약 생성
            strengths_summary = f"{len(possessed)}개의 핵심 역량"
            intro["portfolio_overview"] = intro["portfolio_overview"].replace(
                "{강점_요약}", strengths_summary
            )

    # Portfolio Review 섹션 개인화
    if "portfolio_review" in scenario and project:
        review = scenario["portfolio_review"]
        if isinstance(review.get("main_project_question"), str):
            review["main_project_question"] = review["main_project_question"].replace(
                "{주요_프로젝트}", project
            )

    return scenario


def evaluate_portfolio(
    portfolio_data: Dict[str, Any],
    level: str,
    role: str
) -> Dict[str, Any]:
    """
    포트폴리오 평가 및 체크리스트 기반 분석

    Args:
        portfolio_data: 포트폴리오 데이터
        level: 레벨
        role: 역할

    Returns:
        평가 결과
            - possessed_competencies: 보유 역량 ID 리스트
            - missing_competencies: 부족한 역량 ID 리스트
            - score: 점수
    """
    checklist_data = load_reference_data("portfolio_checklist.json")

    # 레벨+역할 키 매핑
    key_map = {
        ("LEVEL_JUNIOR", "ROLE_FE"): "FE_JUNIOR",
        ("LEVEL_MID", "ROLE_FE"): "FE_MID",
        ("LEVEL_JUNIOR", "ROLE_BE"): "BE_JUNIOR",
        ("LEVEL_MID", "ROLE_BE"): "BE_MID",
        ("LEVEL_JUNIOR", "ROLE_AI"): "AI_JUNIOR",
        ("LEVEL_MID", "ROLE_AI"): "AI_MID",
    }

    checklist_key = key_map.get((level, role))
    if not checklist_key:
        return {"possessed_competencies": [], "missing_competencies": [], "score": 0}

    checklist = checklist_data["checklist_templates"][checklist_key]

    possessed = []
    missing = []
    total_score = 0
    max_score = 0

    # 포트폴리오 텍스트 (skills, projects 등을 하나의 문자열로)
    portfolio_text = " ".join([
        " ".join(portfolio_data.get("skills", [])),
        " ".join([p.get("name", "") for p in portfolio_data.get("projects", [])]),
        " ".join([t for p in portfolio_data.get("projects", []) for t in p.get("technologies", [])])
    ]).lower()

    # Must-have 체크리스트
    for item in checklist["must_have_checklist"]:
        competency_id = item["competency_id"]
        keywords = item["keywords_to_find"]
        score = item["score"]
        max_score += score

        # 키워드 매칭
        if any(kw.lower() in portfolio_text for kw in keywords):
            possessed.append(competency_id)
            total_score += score
        else:
            missing.append(competency_id)

    # Nice-to-have 체크리스트
    for item in checklist.get("nice_to_have_checklist", []):
        competency_id = item["competency_id"]
        keywords = item["keywords_to_find"]
        score = item["score"]
        max_score += score

        if any(kw.lower() in portfolio_text for kw in keywords):
            possessed.append(competency_id)
            total_score += score

    return {
        "possessed_competencies": possessed,
        "missing_competencies": missing,
        "score": total_score,
        "max_score": max_score,
        "percentage": (total_score / max_score * 100) if max_score > 0 else 0
    }
