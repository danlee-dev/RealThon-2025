"""
Embedding 생성 및 관리 모듈

포트폴리오, 스킬, 채용공고를 임베딩으로 변환
"""

from typing import List, Dict, Any
import json
import os


def create_embeddings(documents: List[str], model: str = "text-embedding-ada-002") -> List[List[float]]:
    """
    문서 리스트를 임베딩 벡터로 변환

    Args:
        documents: 임베딩할 문서 리스트
        model: 사용할 임베딩 모델 (OpenAI or Gemini)

    Returns:
        임베딩 벡터 리스트
    """
    # TODO: Gemini API or OpenAI API 연동
    # 현재는 placeholder
    embeddings = []

    for doc in documents:
        # 실제 구현 시 API 호출
        embedding = [0.0] * 1536  # Ada-002 dimension
        embeddings.append(embedding)

    return embeddings


def load_embeddings(persona: str, data_type: str) -> Dict[str, Any]:
    """
    저장된 임베딩 로드

    Args:
        persona: 'frontend' or 'backend'
        data_type: 'portfolios', 'skills', 'job_posts'

    Returns:
        임베딩 데이터
    """
    base_path = os.path.join(os.path.dirname(__file__), "..", "embeddings", persona)
    file_path = os.path.join(base_path, f"{data_type}.json")

    if not os.path.exists(file_path):
        return {"embeddings": [], "metadata": []}

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_embeddings(persona: str, data_type: str, embeddings: List[List[float]], metadata: List[Dict]) -> None:
    """
    임베딩을 파일로 저장

    Args:
        persona: 'frontend' or 'backend'
        data_type: 'portfolios', 'skills', 'job_posts'
        embeddings: 임베딩 벡터 리스트
        metadata: 각 임베딩에 대한 메타데이터
    """
    base_path = os.path.join(os.path.dirname(__file__), "..", "embeddings", persona)
    os.makedirs(base_path, exist_ok=True)

    file_path = os.path.join(base_path, f"{data_type}.json")

    data = {
        "embeddings": embeddings,
        "metadata": metadata
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
