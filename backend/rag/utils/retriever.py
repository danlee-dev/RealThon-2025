"""
문서 검색 모듈

Vector DB에서 유사한 포트폴리오 및 역량 정보 검색
"""

from typing import List, Dict, Any
import numpy as np


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    두 벡터 간의 코사인 유사도 계산

    Args:
        vec1: 첫 번째 벡터
        vec2: 두 번째 벡터

    Returns:
        코사인 유사도 (-1 ~ 1)
    """
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)

    dot_product = np.dot(vec1_np, vec2_np)
    norm_product = np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np)

    if norm_product == 0:
        return 0.0

    return dot_product / norm_product


def retrieve_similar_profiles(
    user_embedding: List[float],
    persona: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    사용자 포트폴리오와 유사한 다른 개발자 프로필 검색

    Args:
        user_embedding: 사용자 포트폴리오 임베딩
        persona: 'frontend' or 'backend'
        top_k: 반환할 결과 개수

    Returns:
        유사한 프로필 리스트
    """
    # TODO: Vector DB (Chroma/FAISS)에서 검색
    # 현재는 placeholder

    similar_profiles = [
        {
            "similarity": 0.95,
            "profile": {
                "skills": ["React", "TypeScript", "Next.js"],
                "experience_years": 3,
                "projects": 5
            }
        }
    ]

    return similar_profiles[:top_k]


def search_job_requirements(
    user_skills: List[str],
    persona: str,
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    사용자 스킬과 관련된 채용 공고 요구사항 검색

    Args:
        user_skills: 사용자가 보유한 스킬 리스트
        persona: 'frontend' or 'backend'
        top_k: 반환할 결과 개수

    Returns:
        관련 채용 공고 리스트
    """
    # TODO: Vector DB에서 검색
    # 현재는 placeholder

    job_requirements = [
        {
            "company": "Example Corp",
            "required_skills": ["React", "TypeScript", "AWS"],
            "preferred_skills": ["Docker", "CI/CD"],
            "experience_required": "3년 이상"
        }
    ]

    return job_requirements[:top_k]
