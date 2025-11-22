"""
GitHub Analyzer 테스트 스크립트
"""

import sys
import os

# backend 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from services.github_analyzer import analyze_github_profile, GitHubAnalyzer


def test_github_analyzer():
    """GitHub 프로필 분석 테스트"""

    db = SessionLocal()

    try:
        # 송재헌 사용자 조회
        user = db.query(User).filter(User.email == "thdwogjs040923@korea.ac.kr").first()

        if not user:
            print("❌ 송재헌 사용자를 찾을 수 없습니다.")
            print("먼저 init_db_with_personas.py를 실행하세요.")
            return

        print("=" * 80)
        print("GitHub 프로필 분석 테스트")
        print("=" * 80)
        print(f"사용자: {user.name}")
        print(f"이메일: {user.email}")
        print(f"GitHub 유저명: {user.github_username}")
        print(f"Role: {user.role}")
        print(f"Level: {user.level}")
        print(f"GitHub Token: {'***' + user.github_token[-4:] if user.github_token else '(not set)'}")
        print()

        if not user.github_username:
            print("❌ GitHub 유저명이 설정되지 않았습니다.")
            return

        # GitHub 프로필 분석 실행
        print("🔍 GitHub 프로필 분석 시작...")
        print()

        result = analyze_github_profile(
            username=user.github_username,
            role=user.role,
            level=user.level,
            max_repos=10
        )

        # 결과 출력
        if "error" in result:
            print(f"❌ 오류 발생: {result['error']}")
            return

        print("=" * 80)
        print("분석 결과")
        print("=" * 80)
        print(f"\n📊 전체 점수: {result.get('overall_score', 0)}/100")

        print(f"\n📁 분석된 저장소 ({len(result.get('analyzed_repos', []))}개):")
        for repo in result.get('analyzed_repos', [])[:5]:
            languages = ', '.join(repo.get('languages', {}).keys()) or 'No languages'
            print(f"  - {repo['name']}: {languages}")
            if repo.get('description'):
                print(f"    {repo['description']}")

        print(f"\n✅ 보유 기술 ({len(result.get('possessed_skills', []))}개):")
        for skill in result.get('possessed_skills', [])[:10]:
            print(f"  - {skill}")
        if len(result.get('possessed_skills', [])) > 10:
            print(f"  ... 외 {len(result.get('possessed_skills', [])) - 10}개")

        print(f"\n❌ 부족한 기술 ({len(result.get('missing_skills', []))}개):")
        for skill in result.get('missing_skills', [])[:10]:
            print(f"  - {skill}")
        if len(result.get('missing_skills', [])) > 10:
            print(f"  ... 외 {len(result.get('missing_skills', [])) - 10}개")

        print(f"\n💪 강점 ({len(result.get('strengths', []))}개):")
        for item in result.get('strengths', []):
            print(f"  - {item['skill']}: {item['reason']}")

        print(f"\n⚠️  약점 ({len(result.get('weaknesses', []))}개):")
        for item in result.get('weaknesses', []):
            print(f"  - {item['skill']}: {item['reason']}")

        print(f"\n📝 요약:")
        print(f"  {result.get('summary', '(없음)')}")

        print("\n" + "=" * 80)
        print("✅ GitHub 프로필 분석 완료!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # UTF-8 인코딩 설정 (한글 지원)
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    test_github_analyzer()
