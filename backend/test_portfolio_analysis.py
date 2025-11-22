"""
포트폴리오 통합 분석 테스트 스크립트

송재헌 유저를 대상으로 CV + GitHub 분석 수행
"""

import sys
import os
from sqlalchemy.orm import Session

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(__file__))

from database import get_db
from models import User, Portfolio
from services import analyze_full_portfolio, analyze_cv_only, analyze_github_only


def find_user_by_name(name: str, db: Session):
    """이름으로 사용자 찾기"""
    user = db.query(User).filter(User.name == name).first()
    return user


def find_portfolio_by_user(user_id: str, db: Session):
    """사용자의 포트폴리오 찾기"""
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
    return portfolio


def test_full_analysis():
    """CV + GitHub 통합 분석 테스트"""
    print("\n" + "="*80)
    print("포트폴리오 통합 분석 테스트")
    print("="*80)

    # DB 연결
    db = next(get_db())

    try:
        # 1. 송재헌 유저 찾기
        print("\n[STEP 1] 송재헌 유저 찾기...")
        user = find_user_by_name("송재헌", db)

        if not user:
            print("[ERROR] 송재헌 유저를 찾을 수 없습니다.")
            return

        print(f"[SUCCESS] 유저 발견:")
        print(f"  - ID: {user.id}")
        print(f"  - 이름: {user.name}")
        print(f"  - 이메일: {user.email}")
        print(f"  - 역할: {user.role}")
        print(f"  - 레벨: {user.level}")
        print(f"  - GitHub 사용자명: {user.github_username}")

        # 2. 포트폴리오 찾기
        print("\n[STEP 2] 포트폴리오 찾기...")
        portfolio = find_portfolio_by_user(user.id, db)

        if not portfolio:
            print("[ERROR] 포트폴리오를 찾을 수 없습니다.")
            return

        print(f"[SUCCESS] 포트폴리오 발견:")
        print(f"  - ID: {portfolio.id}")
        print(f"  - 파일명: {portfolio.filename}")
        print(f"  - 파일 경로: {portfolio.file_url}")
        print(f"  - 기존 summary: {portfolio.summary[:100] if portfolio.summary else 'None'}...")

        # 3. 통합 분석 실행
        print("\n[STEP 3] CV + GitHub 통합 분석 실행...")
        result = analyze_full_portfolio(
            user_id=user.id,
            portfolio_id=portfolio.id,
            db=db,
            role=user.role,
            level=user.level,
            max_repos=10
        )

        # 4. 결과 출력
        print("\n" + "="*80)
        print("분석 결과")
        print("="*80)

        print(f"\n상태: {result['status']}")

        if "cv_analysis" in result:
            cv = result["cv_analysis"]
            if "error" not in cv:
                print("\n[CV 분석 결과]")
                print(f"  - 역할: {cv.get('role')}")
                print(f"  - 레벨: {cv.get('level')}")
                print(f"  - 전체 점수: {cv.get('overall_score')}/100")
                print(f"  - 보유 기술: {len(cv.get('possessed_skills', []))}개")
                print(f"  - 부족 기술: {len(cv.get('missing_skills', []))}개")
                print(f"  - 강점: {len(cv.get('strengths', []))}개")
                print(f"  - 약점: {len(cv.get('weaknesses', []))}개")
                print(f"  - 요약: {cv.get('summary', 'N/A')}")
            else:
                print(f"\n[CV 분석 실패] {cv['error']}")

        if "github_analysis" in result:
            gh = result["github_analysis"]
            if "error" not in gh:
                print("\n[GitHub 분석 결과]")
                print(f"  - 역할: {gh.get('role')}")
                print(f"  - 레벨: {gh.get('level')}")
                print(f"  - GitHub 사용자: {gh.get('github_username')}")
                print(f"  - 분석된 저장소: {len(gh.get('analyzed_repos', []))}개")
                print(f"  - 전체 점수: {gh.get('overall_score')}/100")
                print(f"  - 보유 기술: {len(gh.get('possessed_skills', []))}개")
                print(f"  - 부족 기술: {len(gh.get('missing_skills', []))}개")
                print(f"  - 강점: {len(gh.get('strengths', []))}개")
                print(f"  - 약점: {len(gh.get('weaknesses', []))}개")
                print(f"  - 요약: {gh.get('summary', 'N/A')}")
            else:
                print(f"\n[GitHub 분석 실패] {gh['error']}")

        # 5. DB에 저장된 최종 summary 확인
        print("\n[STEP 4] DB에 저장된 최종 summary 확인...")
        db.refresh(portfolio)

        import json
        if portfolio.summary:
            try:
                summary_data = json.loads(portfolio.summary)
                print("\n[DB에 저장된 Summary 구조]")
                for key in summary_data.keys():
                    print(f"  - {key}: OK")

                # CV 분석 요약
                if "cv_analysis" in summary_data:
                    cv_data = summary_data["cv_analysis"]
                    print(f"\n  [cv_analysis 요약]")
                    print(f"    - 보유 기술: {len(cv_data.get('possessed_skills', []))}개")
                    print(f"    - 부족 기술: {len(cv_data.get('missing_skills', []))}개")
                    print(f"    - 전체 점수: {cv_data.get('overall_score')}/100")

                # GitHub 분석 요약
                if "github_analysis" in summary_data:
                    gh_data = summary_data["github_analysis"]
                    print(f"\n  [github_analysis 요약]")
                    print(f"    - 분석된 저장소: {len(gh_data.get('analyzed_repos', []))}개")
                    print(f"    - 보유 기술: {len(gh_data.get('possessed_skills', []))}개")
                    print(f"    - 부족 기술: {len(gh_data.get('missing_skills', []))}개")
                    print(f"    - 전체 점수: {gh_data.get('overall_score')}/100")

            except json.JSONDecodeError:
                print("[ERROR] Summary JSON 파싱 실패")
        else:
            print("[WARNING] Summary가 비어 있습니다.")

        print("\n" + "="*80)
        print("테스트 완료!")
        print("="*80)

    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


def test_cv_only():
    """CV만 분석 테스트"""
    print("\n" + "="*80)
    print("CV 분석 테스트")
    print("="*80)

    db = next(get_db())

    try:
        user = find_user_by_name("송재헌", db)
        if not user:
            print("[ERROR] 송재헌 유저를 찾을 수 없습니다.")
            return

        portfolio = find_portfolio_by_user(user.id, db)
        if not portfolio:
            print("[ERROR] 포트폴리오를 찾을 수 없습니다.")
            return

        print(f"[INFO] 유저: {user.name} ({user.email})")
        print(f"[INFO] 포트폴리오: {portfolio.filename}")

        result = analyze_cv_only(
            user_id=user.id,
            portfolio_id=portfolio.id,
            db=db
        )

        print(f"\n[결과] 상태: {result['status']}")
        if "cv_analysis" in result and "error" not in result["cv_analysis"]:
            cv = result["cv_analysis"]
            print(f"  - 전체 점수: {cv.get('overall_score')}/100")
            print(f"  - 보유 기술: {len(cv.get('possessed_skills', []))}개")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


def test_github_only():
    """GitHub만 분석 테스트"""
    print("\n" + "="*80)
    print("GitHub 분석 테스트")
    print("="*80)

    db = next(get_db())

    try:
        user = find_user_by_name("송재헌", db)
        if not user:
            print("[ERROR] 송재헌 유저를 찾을 수 없습니다.")
            return

        portfolio = find_portfolio_by_user(user.id, db)
        if not portfolio:
            print("[ERROR] 포트폴리오를 찾을 수 없습니다.")
            return

        print(f"[INFO] 유저: {user.name} ({user.github_username})")

        result = analyze_github_only(
            user_id=user.id,
            portfolio_id=portfolio.id,
            db=db
        )

        print(f"\n[결과] 상태: {result['status']}")
        if "github_analysis" in result and "error" not in result["github_analysis"]:
            gh = result["github_analysis"]
            print(f"  - 전체 점수: {gh.get('overall_score')}/100")
            print(f"  - 분석된 저장소: {len(gh.get('analyzed_repos', []))}개")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "cv":
            test_cv_only()
        elif mode == "github":
            test_github_only()
        elif mode == "full":
            test_full_analysis()
        else:
            print("사용법: python test_portfolio_analysis.py [cv|github|full]")
    else:
        # 기본값: 통합 분석
        test_full_analysis()
