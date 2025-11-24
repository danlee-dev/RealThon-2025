"""
역량 분석 모듈

사용자의 포트폴리오와 직무 요구사항을 비교하여 GAP 분석
"""

from typing import List, Dict, Any, Set


def analyze_competency_gap(
    user_portfolio: Dict[str, Any],
    job_requirements: Dict[str, Any],
    similar_profiles: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    역량 GAP 분석

    Args:
        user_portfolio: 사용자 포트폴리오 데이터
        job_requirements: 직무 요구사항
        similar_profiles: 유사한 다른 개발자 프로필

    Returns:
        GAP 분석 결과
            - missing_skills: 부족한 스킬
            - weak_areas: 약한 영역
            - recommendations: 개선 방안
    """
    user_skills = set(user_portfolio.get("skills", []))
    required_skills = set(job_requirements.get("required_skills", []))
    preferred_skills = set(job_requirements.get("preferred_skills", []))

    # 필수 스킬 중 부족한 것
    missing_required = required_skills - user_skills

    # 우대 스킬 중 부족한 것
    missing_preferred = preferred_skills - user_skills

    # 유사 프로필과 비교
    common_skills_in_similar = set()
    for profile in similar_profiles:
        profile_skills = set(profile.get("profile", {}).get("skills", []))
        common_skills_in_similar.update(profile_skills)

    # 동일 직군에서 많이 가진 스킬인데 본인에게 없는 것
    missing_common = common_skills_in_similar - user_skills

    return {
        "missing_skills": {
            "required": list(missing_required),
            "preferred": list(missing_preferred),
            "common_in_peers": list(missing_common)
        },
        "weak_areas": _identify_weak_areas(user_portfolio, job_requirements),
        "recommendations": _generate_recommendations(missing_required, missing_preferred)
    }


def identify_strengths(
    user_portfolio: Dict[str, Any],
    job_requirements: Dict[str, Any],
    similar_profiles: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    사용자의 강점 파악

    Args:
        user_portfolio: 사용자 포트폴리오 데이터
        job_requirements: 직무 요구사항
        similar_profiles: 유사한 다른 개발자 프로필

    Returns:
        강점 분석 결과
            - unique_skills: 차별화된 스킬
            - exceeding_requirements: 요구사항을 초과하는 부분
            - standout_projects: 돋보이는 프로젝트
    """
    user_skills = set(user_portfolio.get("skills", []))
    required_skills = set(job_requirements.get("required_skills", []))
    preferred_skills = set(job_requirements.get("preferred_skills", []))

    # 요구사항 충족
    meets_required = user_skills & required_skills
    meets_preferred = user_skills & preferred_skills

    # 다른 사람들이 잘 안 가진 스킬
    peer_skills = set()
    for profile in similar_profiles:
        peer_skills.update(set(profile.get("profile", {}).get("skills", [])))

    unique_skills = user_skills - peer_skills

    return {
        "unique_skills": list(unique_skills),
        "exceeding_requirements": {
            "required_match_rate": len(meets_required) / len(required_skills) if required_skills else 0,
            "preferred_match_rate": len(meets_preferred) / len(preferred_skills) if preferred_skills else 0
        },
        "standout_projects": _find_standout_projects(user_portfolio)
    }


def _identify_weak_areas(user_portfolio: Dict[str, Any], job_requirements: Dict[str, Any]) -> List[str]:
    """
    약한 영역 식별 (내부 함수)
    """
    weak_areas = []

    # 경력 부족
    user_exp = user_portfolio.get("experience_years", 0)
    required_exp = job_requirements.get("experience_years", 0)

    if user_exp < required_exp:
        weak_areas.append(f"경력: {required_exp}년 요구되나 {user_exp}년 보유")

    # 프로젝트 수
    user_projects = len(user_portfolio.get("projects", []))
    if user_projects < 3:
        weak_areas.append(f"프로젝트 경험 부족 (현재 {user_projects}개)")

    return weak_areas


def _generate_recommendations(missing_required: Set[str], missing_preferred: Set[str]) -> List[str]:
    """
    개선 방안 생성 (내부 함수)
    """
    recommendations = []

    if missing_required:
        recommendations.append(
            f"필수 스킬 학습 필요: {', '.join(list(missing_required)[:3])}"
        )

    if missing_preferred:
        recommendations.append(
            f"우대 스킬 학습 권장: {', '.join(list(missing_preferred)[:3])}"
        )

    return recommendations


def _find_standout_projects(user_portfolio: Dict[str, Any]) -> List[str]:
    """
    돋보이는 프로젝트 찾기 (내부 함수)
    """
    projects = user_portfolio.get("projects", [])

    standout = []
    for project in projects:
        # 기여도가 높거나, 특별한 기술을 사용한 프로젝트
        if project.get("contribution_rate", 0) > 70:
            standout.append(project.get("name", "Unknown"))

    return standout
