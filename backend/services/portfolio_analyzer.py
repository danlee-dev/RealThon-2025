"""
포트폴리오 통합 분석 서비스

CV + GitHub 분석을 통합하여 수행
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from .cv_analyzer import cv_analyzer
from .github_analyzer import github_analyzer


def analyze_full_portfolio(
    user_id: str,
    portfolio_id: str,
    db: Session,
    role: str = None,
    level: str = None,
    max_repos: int = 10,
    analyze_cv: bool = True,
    analyze_github: bool = True
) -> Dict[str, Any]:
    """
    CV + GitHub 통합 분석 파이프라인

    Args:
        user_id: 사용자 ID
        portfolio_id: 포트폴리오 ID
        db: 데이터베이스 세션
        role: 직무 (선택, 기본값: User.role)
        level: 경력 레벨 (선택, 기본값: User.level)
        max_repos: GitHub 분석 시 최대 저장소 개수
        analyze_cv: CV 분석 수행 여부 (기본값: True)
        analyze_github: GitHub 분석 수행 여부 (기본값: True)

    Returns:
        통합 분석 결과
        {
            "user_id": "...",
            "portfolio_id": "...",
            "cv_analysis": {...},
            "github_analysis": {...},
            "status": "success"
        }
    """
    result = {
        "user_id": user_id,
        "portfolio_id": portfolio_id,
        "status": "success"
    }

    # 1. CV 분석
    if analyze_cv:
        try:
            print("\n" + "="*60)
            print("STEP 1: CV 분석 시작")
            print("="*60)
            cv_result = cv_analyzer.analyze_cv(
                portfolio_id=portfolio_id,
                user_id=user_id,
                db=db,
                role=role,
                level=level
            )
            result["cv_analysis"] = cv_result
            print("\n[SUCCESS] CV 분석 완료")
        except Exception as e:
            print(f"\n[ERROR] CV 분석 실패: {str(e)}")
            result["cv_analysis"] = {"error": str(e)}
            result["status"] = "partial"

    # 2. GitHub 분석
    if analyze_github:
        try:
            print("\n" + "="*60)
            print("STEP 2: GitHub 분석 시작")
            print("="*60)
            github_result = github_analyzer.analyze_github_and_save(
                user_id=user_id,
                portfolio_id=portfolio_id,
                db=db,
                role=role,
                level=level,
                max_repos=max_repos
            )
            result["github_analysis"] = github_result
            print("\n[SUCCESS] GitHub 분석 완료")
        except Exception as e:
            print(f"\n[ERROR] GitHub 분석 실패: {str(e)}")
            result["github_analysis"] = {"error": str(e)}
            result["status"] = "partial"

    # 3. 최종 상태 확인
    if not analyze_cv and not analyze_github:
        result["status"] = "no_analysis"
        print("\n[WARNING] 분석이 수행되지 않았습니다.")

    print("\n" + "="*60)
    print(f"포트폴리오 분석 완료 (상태: {result['status']})")
    print("="*60)

    return result


def analyze_cv_only(
    user_id: str,
    portfolio_id: str,
    db: Session,
    role: str = None,
    level: str = None
) -> Dict[str, Any]:
    """
    CV만 분석 (헬퍼 함수)

    Args:
        user_id: 사용자 ID
        portfolio_id: 포트폴리오 ID
        db: 데이터베이스 세션
        role: 직무 (선택)
        level: 경력 레벨 (선택)

    Returns:
        CV 분석 결과
    """
    return analyze_full_portfolio(
        user_id=user_id,
        portfolio_id=portfolio_id,
        db=db,
        role=role,
        level=level,
        analyze_cv=True,
        analyze_github=False
    )


def analyze_github_only(
    user_id: str,
    portfolio_id: str,
    db: Session,
    role: str = None,
    level: str = None,
    max_repos: int = 10
) -> Dict[str, Any]:
    """
    GitHub만 분석 (헬퍼 함수)

    Args:
        user_id: 사용자 ID
        portfolio_id: 포트폴리오 ID
        db: 데이터베이스 세션
        role: 직무 (선택)
        level: 경력 레벨 (선택)
        max_repos: 분석할 최대 저장소 개수

    Returns:
        GitHub 분석 결과
    """
    return analyze_full_portfolio(
        user_id=user_id,
        portfolio_id=portfolio_id,
        db=db,
        role=role,
        level=level,
        max_repos=max_repos,
        analyze_cv=False,
        analyze_github=True
    )
