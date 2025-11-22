"""
AI 개발자 RAG 시스템 테스트

송재헌 유저(AI Junior)의 competency matrix가 제대로 조회되는지 테스트
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from rag.utils import get_competency_matrix
import json

def test_ai_competency_matrix():
    """AI Junior 역량 매트릭스 조회 테스트"""

    print("=" * 80)
    print("AI Junior 역량 매트릭스 조회 테스트")
    print("=" * 80)

    try:
        # AI Junior 역량 매트릭스 조회
        level = "LEVEL_JUNIOR"
        role = "ROLE_AI"

        print(f"\n레벨: {level}")
        print(f"역할: {role}")
        print(f"\n역량 매트릭스 조회 중...\n")

        competency = get_competency_matrix(level, role)

        print(f"✓ 역량 매트릭스 조회 성공!")
        print(f"\nID: {competency['id']}")
        print(f"Level: {competency['level']}")
        print(f"Role: {competency['role']}")

        # Must-have 기술 스킬 출력
        print(f"\n{'=' * 80}")
        print("필수 기술 스킬 (Must-have Technical Skills)")
        print(f"{'=' * 80}")

        must_have_skills = competency['must_have']['technical_skills']
        for i, skill in enumerate(must_have_skills, 1):
            print(f"\n[{i}] {skill['skill']}")
            print(f"    카테고리: {skill['category']}")
            print(f"    설명: {skill['description']}")
            print(f"    키워드: {', '.join(skill['keywords'])}")
            print(f"    중요도: {skill['importance']}")

        # Must-have 프로젝트 경험 출력
        print(f"\n{'=' * 80}")
        print("필수 프로젝트 경험 (Must-have Project Experiences)")
        print(f"{'=' * 80}")

        must_have_exp = competency['must_have']['project_experiences']
        for i, exp in enumerate(must_have_exp, 1):
            print(f"\n[{i}] {exp['experience']}")
            print(f"    설명: {exp['description']}")
            print(f"    키워드: {', '.join(exp['keywords'])}")
            print(f"    중요도: {exp['importance']}")

        # Soft Skills 출력
        print(f"\n{'=' * 80}")
        print("필수 소프트 스킬 (Must-have Soft Skills)")
        print(f"{'=' * 80}")

        soft_skills = competency['must_have']['soft_skills']
        for i, skill in enumerate(soft_skills, 1):
            print(f"\n[{i}] {skill['skill']}")
            print(f"    설명: {skill['description']}")
            print(f"    키워드: {', '.join(skill['keywords'])}")

        # Nice-to-have 기술 스킬 출력
        print(f"\n{'=' * 80}")
        print("우대 기술 스킬 (Nice-to-have Technical Skills)")
        print(f"{'=' * 80}")

        nice_to_have_skills = competency['nice_to_have']['technical_skills']
        for i, skill in enumerate(nice_to_have_skills, 1):
            print(f"\n[{i}] {skill['skill']}")
            print(f"    카테고리: {skill['category']}")
            print(f"    설명: {skill['description']}")
            print(f"    키워드: {', '.join(skill['keywords'])}")

        print(f"\n{'=' * 80}")
        print("✓ 모든 테스트 통과!")
        print(f"{'=' * 80}\n")

        # 전체 JSON 출력 (확인용)
        print("\n전체 역량 매트릭스 JSON:")
        print(json.dumps(competency, ensure_ascii=False, indent=2))

        return True

    except Exception as e:
        print(f"\n✗ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_mid_competency_matrix():
    """AI Mid 역량 매트릭스 조회 테스트"""

    print("\n" + "=" * 80)
    print("AI Mid 역량 매트릭스 조회 테스트")
    print("=" * 80)

    try:
        level = "LEVEL_MID"
        role = "ROLE_AI"

        competency = get_competency_matrix(level, role)

        print(f"\n✓ AI Mid 역량 매트릭스 조회 성공!")
        print(f"ID: {competency['id']}")

        # 주요 기술만 출력
        must_have_skills = competency['must_have']['technical_skills']
        print(f"\n필수 기술 스킬 ({len(must_have_skills)}개):")
        for skill in must_have_skills[:3]:  # 처음 3개만
            print(f"  - {skill['skill']}: {skill['description']}")
        print(f"  ... 외 {len(must_have_skills) - 3}개")

        return True

    except Exception as e:
        print(f"\n✗ AI Mid 테스트 실패: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n[TEST] AI 개발자 RAG 시스템 테스트 시작\n")

    # AI Junior 테스트
    result1 = test_ai_competency_matrix()

    # AI Mid 테스트
    result2 = test_ai_mid_competency_matrix()

    print("\n" + "=" * 80)
    print("테스트 요약")
    print("=" * 80)
    print(f"AI Junior 테스트: {'✓ 통과' if result1 else '✗ 실패'}")
    print(f"AI Mid 테스트: {'✓ 통과' if result2 else '✗ 실패'}")
    print("=" * 80 + "\n")
