"""
실제 포트폴리오 분석 실행 스크립트
"""

import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(__file__))

from database import get_db
from models import User, Portfolio
from services import analyze_full_portfolio
import json


def main():
    """송재헌 유저의 포트폴리오 분석 실행"""

    print("\n" + "="*80)
    print("포트폴리오 분석 실행")
    print("="*80)

    # DB 연결
    db = next(get_db())

    try:
        # 1. 송재헌 유저 찾기
        print("\n[1] 송재헌 유저 찾기...")
        user = db.query(User).filter(User.name == "송재헌").first()

        if not user:
            print("[ERROR] 송재헌 유저를 찾을 수 없습니다.")
            return

        print(f"[OK] 유저 발견: {user.name} ({user.email})")
        print(f"     Role: {user.role}, Level: {user.level}")
        print(f"     GitHub: {user.github_username}")

        # 2. 포트폴리오 찾기
        print("\n[2] 포트폴리오 찾기...")
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()

        if not portfolio:
            print("[ERROR] 포트폴리오를 찾을 수 없습니다.")
            return

        print(f"[OK] 포트폴리오 발견: {portfolio.filename}")
        print(f"     ID: {portfolio.id}")

        # 3. 기존 summary 확인
        print("\n[3] 기존 summary 확인...")
        if portfolio.summary:
            try:
                existing = json.loads(portfolio.summary)
                print(f"[INFO] 기존 summary 존재: {list(existing.keys())}")
            except:
                print("[INFO] 기존 summary가 있지만 JSON 파싱 실패")
        else:
            print("[INFO] 기존 summary 없음")

        # 4. 분석 실행
        print("\n[4] CV + GitHub 분석 실행...")
        print("-" * 80)

        result = analyze_full_portfolio(
            user_id=user.id,
            portfolio_id=portfolio.id,
            db=db,
            role=user.role,
            level=user.level,
            max_repos=10,
            analyze_cv=True,
            analyze_github=True
        )

        print("-" * 80)

        # 5. 결과 확인
        print("\n[5] 분석 결과 확인...")
        print(f"상태: {result['status']}")

        if "cv_analysis" in result:
            cv = result.get("cv_analysis", {})
            if "error" not in cv:
                print(f"\n[OK] CV 분석 성공:")
                print(f"  - 점수: {cv.get('overall_score')}/100")
                print(f"  - 보유 기술: {len(cv.get('possessed_skills', []))}개")
                print(f"  - 부족 기술: {len(cv.get('missing_skills', []))}개")
            else:
                print(f"\n[ERROR] CV 분석 실패: {cv['error']}")

        if "github_analysis" in result:
            gh = result.get("github_analysis", {})
            if "error" not in gh:
                print(f"\n[OK] GitHub 분석 성공:")
                print(f"  - 점수: {gh.get('overall_score')}/100")
                print(f"  - 분석 저장소: {len(gh.get('analyzed_repos', []))}개")
                print(f"  - 보유 기술: {len(gh.get('possessed_skills', []))}개")
            else:
                print(f"\n[ERROR] GitHub 분석 실패: {gh['error']}")

        # 6. DB에 저장된 최종 summary 확인
        print("\n[6] DB에 저장된 summary 확인...")
        db.refresh(portfolio)

        if portfolio.summary:
            summary_data = json.loads(portfolio.summary)
            print(f"\n저장된 summary 키: {list(summary_data.keys())}")

            # CV 분석
            if "cv_analysis" in summary_data:
                cv_data = summary_data["cv_analysis"]
                print(f"\n[cv_analysis]")
                print(f"  - Role: {cv_data.get('role')}")
                print(f"  - Level: {cv_data.get('level')}")
                print(f"  - Score: {cv_data.get('overall_score')}/100")
                print(f"  - Possessed skills: {len(cv_data.get('possessed_skills', []))}개")
                print(f"  - Missing skills: {len(cv_data.get('missing_skills', []))}개")
                print(f"  - Strengths: {len(cv_data.get('strengths', []))}개")
                print(f"  - Weaknesses: {len(cv_data.get('weaknesses', []))}개")

                # 강점 출력
                if cv_data.get('strengths'):
                    print(f"\n  강점:")
                    for s in cv_data['strengths']:
                        print(f"    - {s.get('skill')}: {s.get('reason')}")

            # GitHub 분석
            if "github_analysis" in summary_data:
                gh_data = summary_data["github_analysis"]
                print(f"\n[github_analysis]")
                print(f"  - Role: {gh_data.get('role')}")
                print(f"  - Level: {gh_data.get('level')}")
                print(f"  - GitHub User: {gh_data.get('github_username')}")
                print(f"  - Score: {gh_data.get('overall_score')}/100")
                print(f"  - Analyzed repos: {len(gh_data.get('analyzed_repos', []))}개")
                print(f"  - Possessed skills: {len(gh_data.get('possessed_skills', []))}개")
                print(f"  - Missing skills: {len(gh_data.get('missing_skills', []))}개")

                # 분석된 저장소 목록
                if gh_data.get('analyzed_repos'):
                    print(f"\n  분석된 저장소:")
                    for repo in gh_data['analyzed_repos'][:5]:  # 최대 5개만
                        langs = ', '.join(repo.get('languages', {}).keys())
                        print(f"    - {repo.get('name')}: {langs}")
        else:
            print("[WARNING] Summary가 비어 있습니다!")

        print("\n" + "="*80)
        print("[SUCCESS] 분석 완료 및 DB 저장 성공!")
        print("="*80)

    except Exception as e:
        print(f"\n[ERROR] 실행 실패: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    main()
