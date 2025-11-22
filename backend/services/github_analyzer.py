"""
GitHub 프로필 분석 서비스

GitHub API를 사용하여 사용자의 저장소를 분석하고 RAG + Gemini로 역량 평가
"""

import os
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

from rag.utils import get_competency_matrix
from .gemini_service import GeminiService

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


class GitHubAnalyzer:
    """GitHub 프로필 분석 클래스"""

    def __init__(self):
        self.gemini_service = GeminiService()
        self.headers = {}
        if GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {GITHUB_TOKEN}"

    def fetch_user_repos(self, username: str, max_repos: int = 10) -> List[Dict[str, Any]]:
        """
        GitHub 사용자의 저장소 목록 가져오기

        Args:
            username: GitHub 사용자명
            max_repos: 최대 저장소 개수

        Returns:
            저장소 정보 리스트
        """
        url = f"https://api.github.com/users/{username}/repos"
        params = {
            "sort": "updated",
            "per_page": max_repos
        }

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise Exception(f"GitHub API 오류: {response.status_code}")

        return response.json()

    def fetch_repo_details(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """
        특정 저장소의 상세 정보 가져오기

        Args:
            owner: 저장소 소유자
            repo_name: 저장소 이름

        Returns:
            저장소 상세 정보
        """
        url = f"https://api.github.com/repos/{owner}/{repo_name}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return {}

        repo_data = response.json()

        # 언어 정보 가져오기
        languages_url = repo_data.get("languages_url")
        languages = {}
        if languages_url:
            lang_response = requests.get(languages_url, headers=self.headers)
            if lang_response.status_code == 200:
                languages = lang_response.json()

        # README 가져오기 (선택)
        readme_url = f"https://api.github.com/repos/{owner}/{repo_name}/readme"
        readme_content = ""
        readme_response = requests.get(readme_url, headers=self.headers)
        if readme_response.status_code == 200:
            import base64
            readme_data = readme_response.json()
            readme_content = base64.b64decode(readme_data.get("content", "")).decode("utf-8")

        return {
            "name": repo_data.get("name"),
            "description": repo_data.get("description"),
            "languages": languages,
            "stars": repo_data.get("stargazers_count"),
            "forks": repo_data.get("forks_count"),
            "open_issues": repo_data.get("open_issues_count"),
            "created_at": repo_data.get("created_at"),
            "updated_at": repo_data.get("updated_at"),
            "readme": readme_content[:1000] if readme_content else ""  # README 일부만
        }

    def analyze_github_profile(
        self,
        username: str,
        role: str,
        level: str = "LEVEL_MID",
        max_repos: int = 10
    ) -> Dict[str, Any]:
        """
        GitHub 프로필을 분석하여 역량 평가

        Args:
            username: GitHub 사용자명
            role: 직무 ('ROLE_FE' or 'ROLE_BE')
            level: 경력 레벨 (기본값: 'LEVEL_MID')
            max_repos: 분석할 최대 저장소 개수

        Returns:
            역량 평가 결과
            {
                "role": "ROLE_FE",
                "level": "LEVEL_MID",
                "github_username": "user123",
                "analyzed_repos": [...],
                "possessed_skills": ["React", "TypeScript", ...],
                "missing_skills": ["Next.js", "테스트 코드 작성", ...],
                "strengths": [
                    {"skill": "React", "reason": "여러 프로젝트에서 사용..."},
                    ...
                ],
                "weaknesses": [
                    {"skill": "테스트", "reason": "테스트 코드 부족..."},
                    ...
                ],
                "overall_score": 75,
                "summary": "전반적인 평가 요약"
            }
        """
        # 1. GitHub 저장소 목록 가져오기
        try:
            repos = self.fetch_user_repos(username, max_repos)
        except Exception as e:
            return {
                "error": f"GitHub 저장소를 가져오는데 실패했습니다: {str(e)}",
                "role": role,
                "level": level
            }

        if not repos:
            return {
                "error": "저장소가 없습니다.",
                "role": role,
                "level": level,
                "github_username": username
            }

        # 2. 각 저장소의 상세 정보 수집
        detailed_repos = []
        for repo in repos[:max_repos]:
            try:
                repo_detail = self.fetch_repo_details(username, repo["name"])
                if repo_detail:
                    detailed_repos.append(repo_detail)
            except Exception:
                continue  # 실패한 저장소는 스킵

        # 3. GitHub 데이터 요약
        github_data = {
            "username": username,
            "total_repos_analyzed": len(detailed_repos),
            "repositories": detailed_repos
        }

        # 4. RAG에서 해당 직무/레벨의 역량 매트릭스 가져오기
        try:
            competency_matrix = get_competency_matrix(level, role)
        except Exception as e:
            return {
                "error": f"역량 매트릭스를 불러오는데 실패했습니다: {str(e)}",
                "role": role,
                "level": level,
                "github_username": username
            }

        # 5. Gemini API로 분석
        analysis_result = self.gemini_service.analyze_github_with_competency(
            github_data=github_data,
            role=role,
            competency_matrix=competency_matrix
        )

        # 6. 결과에 메타데이터 추가
        analysis_result["level"] = level
        analysis_result["github_username"] = username
        analysis_result["analyzed_repos"] = [
            {
                "name": r["name"],
                "description": r["description"],
                "languages": r["languages"]
            }
            for r in detailed_repos
        ]

        return analysis_result


# 싱글톤 인스턴스
github_analyzer = GitHubAnalyzer()


def analyze_github_profile(
    username: str,
    role: str,
    level: str = "LEVEL_MID",
    max_repos: int = 10
) -> Dict[str, Any]:
    """
    GitHub 프로필 분석 함수 (외부에서 직접 호출 가능)

    Args:
        username: GitHub 사용자명
        role: 직무 ('ROLE_FE' or 'ROLE_BE')
        level: 경력 레벨 (기본값: 'LEVEL_MID')
        max_repos: 분석할 최대 저장소 개수

    Returns:
        역량 평가 결과 JSON
    """
    return github_analyzer.analyze_github_profile(username, role, level, max_repos)
