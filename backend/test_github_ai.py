"""
GitHub 분석기 AI 역량 테스트

송재헌 유저의 GitHub을 분석하여 AI Junior 역량 매트릭스와 비교
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
from services.github_analyzer import GitHubAnalyzer
from rag.utils import get_competency_matrix

# 데이터베이스 설정
DATABASE_URL = "sqlite:///interview_app.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def test_github_analysis_for_ai():
    """송재헌(AI Junior) GitHub 분석 테스트"""

    print("\n" + "=" * 80)
    print("GitHub 분석 - AI Junior 역량 평가 테스트")
    print("=" * 80)

    session = Session()

    try:
        # 1. 송재헌 유저 조회
        user = session.query(User).filter(User.email == "thdwogjs040923@korea.ac.kr").first()
        if not user:
            print("\n✗ 송재헌 유저를 찾을 수 없습니다.")
            return False

        print(f"\n사용자 정보:")
        print(f"  이름: {user.name}")
        print(f"  이메일: {user.email}")
        print(f"  역할: {user.role}")
        print(f"  레벨: {user.level}")

        # 2. GitHub 사용자명 입력
        github_username = "thdwogjs"  # 송재헌 GitHub username
        print(f"\nGitHub 사용자명: {github_username}")

        # 3. AI Junior 역량 매트릭스 조회
        print(f"\n{user.level}, {user.role} 역량 매트릭스 조회 중...")
        competency_matrix = get_competency_matrix(user.level, user.role)

        print(f"\n✓ 역량 매트릭스 조회 성공!")
        print(f"  필수 기술 스킬: {len(competency_matrix['must_have']['technical_skills'])}개")
        print(f"  필수 프로젝트 경험: {len(competency_matrix['must_have']['project_experiences'])}개")

        # 필수 기술 키워드 출력
        print(f"\n주요 평가 키워드:")
        must_have_skills = competency_matrix['must_have']['technical_skills']
        for i, skill in enumerate(must_have_skills[:5], 1):
            print(f"  [{i}] {skill['skill']}: {', '.join(skill['keywords'][:3])}")

        # 4. GitHub 분석 실행
        print(f"\n{'=' * 80}")
        print(f"GitHub 분석 실행 중...")
        print(f"{'=' * 80}\n")

        analyzer = GitHubAnalyzer()
        analysis_result = analyzer.analyze_github_profile(
            username=github_username,
            role=user.role,
            level=user.level
        )

        # 5. 분석 결과 출력
        print(f"\n{'=' * 80}")
        print("분석 결과")
        print(f"{'=' * 80}\n")

        # 에러 체크
        if 'error' in analysis_result:
            print(f"✗ 분석 실패: {analysis_result['error']}")
            return False

        print(f"GitHub 사용자: {analysis_result.get('github_username', github_username)}")
        print(f"역할: {analysis_result.get('role', user.role)}")
        print(f"레벨: {analysis_result.get('level', user.level)}")
        print(f"\n저장소 분석:")
        analyzed_repos = analysis_result.get('analyzed_repos', [])
        print(f"  분석한 저장소: {len(analyzed_repos)}개")

        if analyzed_repos:
            print(f"\n주요 저장소:")
            for i, repo in enumerate(analyzed_repos[:5], 1):
                print(f"  [{i}] {repo['name']}")
                if repo.get('description'):
                    print(f"      {repo['description']}")
                if repo.get('languages'):
                    langs = ', '.join(repo['languages'].keys())
                    print(f"      사용 언어: {langs}")

        # 보유 역량
        possessed_skills = analysis_result.get('possessed_skills', [])
        print(f"\n보유 역량 ({len(possessed_skills)}개):")
        for skill in possessed_skills[:10]:
            print(f"  ✓ {skill}")
        if len(possessed_skills) > 10:
            print(f"  ... 외 {len(possessed_skills) - 10}개")

        # 부족한 역량
        missing_skills = analysis_result.get('missing_skills', [])
        print(f"\n부족한 역량 ({len(missing_skills)}개):")
        for skill in missing_skills[:10]:
            print(f"  ✗ {skill}")
        if len(missing_skills) > 10:
            print(f"  ... 외 {len(missing_skills) - 10}개")

        # 강점
        strengths = analysis_result.get('strengths', [])
        print(f"\n강점 ({len(strengths)}개):")
        for strength in strengths:
            if isinstance(strength, dict):
                print(f"  • {strength.get('skill', '')}: {strength.get('reason', '')}")
            else:
                print(f"  • {strength}")

        # 약점
        weaknesses = analysis_result.get('weaknesses', [])
        print(f"\n개선 필요 영역 ({len(weaknesses)}개):")
        for weakness in weaknesses:
            if isinstance(weakness, dict):
                print(f"  • {weakness.get('skill', '')}: {weakness.get('reason', '')}")
            else:
                print(f"  • {weakness}")

        # 종합 점수
        print(f"\n종합 평가:")
        print(f"  점수: {analysis_result.get('overall_score', 0)}/100")
        print(f"  요약: {analysis_result.get('summary', 'N/A')}")

        print(f"\n{'=' * 80}")
        print("✓ GitHub 분석 완료!")
        print(f"{'=' * 80}\n")

        return True

    except Exception as e:
        print(f"\n✗ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()


if __name__ == "__main__":
    print("\n[TEST] GitHub 분석기 - AI 역량 평가 테스트 시작")

    # GitHub Token 확인
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("\n⚠ GITHUB_TOKEN 환경변수가 설정되지 않았습니다.")
        print("  일부 기능이 제한될 수 있습니다.")

    result = test_github_analysis_for_ai()

    print("\n" + "=" * 80)
    print("테스트 결과")
    print("=" * 80)
    print(f"GitHub 분석 테스트: {'✓ 통과' if result else '✗ 실패'}")
    print("=" * 80 + "\n")
