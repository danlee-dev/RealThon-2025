"""
역량 평가 생성 테스트 (송재헌 유저)
"""

from database import get_db, engine, Base
from models import User, Portfolio
from services.capability_evaluator import evaluate_portfolio_capabilities


def test_song_jaeheon_evaluation():
    """송재헌 유저의 역량 평가 생성 및 저장"""

    # 1. 테이블 생성
    print("\n" + "="*80)
    print("테이블 생성")
    print("="*80)
    Base.metadata.create_all(bind=engine)
    print("[OK] 테이블 생성 완료")

    # 2. DB 연결
    db = next(get_db())

    try:
        # 3. 송재헌 유저 찾기
        print("\n[STEP 1] 송재헌 유저 찾기...")
        user = db.query(User).filter(User.name == "송재헌").first()

        if not user:
            print("[ERROR] 송재헌 유저를 찾을 수 없습니다.")
            return

        print(f"[OK] 유저 발견:")
        print(f"     - 이름: {user.name}")
        print(f"     - 이메일: {user.email}")
        print(f"     - 역할: {user.role}")

        # 4. 포트폴리오 찾기
        print("\n[STEP 2] 포트폴리오 찾기...")
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()

        if not portfolio:
            print("[ERROR] 포트폴리오를 찾을 수 없습니다.")
            return

        print(f"[OK] 포트폴리오 발견:")
        print(f"     - ID: {portfolio.id}")
        print(f"     - 파일명: {portfolio.filename}")
        print(f"     - Summary 존재: {'Yes' if portfolio.summary else 'No'}")

        if not portfolio.summary:
            print("\n[ERROR] Portfolio summary가 비어 있습니다.")
            print("먼저 CV/GitHub 분석을 실행하세요:")
            print(f"  python run_analysis.py")
            return

        # 5. 역량 평가 생성
        print("\n" + "="*80)
        print("[STEP 3] Gemini로 역량 평가 생성 중...")
        print("="*80)

        result = evaluate_portfolio_capabilities(
            portfolio_id=portfolio.id,
            user_id=user.id,
            db=db
        )

        print("\n" + "="*80)
        print("역량 평가 결과")
        print("="*80)

        print(f"\n직무: {result['role']}")
        print(f"포트폴리오 ID: {result['portfolio_id']}")
        print(f"\n6개 역량 평가:")

        for i, eval_data in enumerate(result['evaluations'], start=1):
            print(f"\n{i}. 역량 #{eval_data['capability_index']}")
            print(f"   점수: {eval_data['score']}/100")
            print(f"   이유: {eval_data['reason'][:100]}...")
            print(f"   피드백: {eval_data['feedback'][:100]}...")

        # 6. DB 검증
        print("\n" + "="*80)
        print("[STEP 4] DB 저장 확인")
        print("="*80)

        from models import CapabilityEvaluation
        saved = db.query(CapabilityEvaluation).filter(
            CapabilityEvaluation.portfolio_id == portfolio.id
        ).first()

        if saved:
            print(f"[OK] DB에 저장됨:")
            print(f"     - ID: {saved.id}")
            print(f"     - Role: {saved.role}")
            print(f"\n     역량별 점수:")
            for i in range(1, 7):
                name_ko = getattr(saved, f"capability{i}_name_ko")
                score = getattr(saved, f"capability{i}_score")
                print(f"       {i}. {name_ko}: {score}점")
        else:
            print("[ERROR] DB에 저장되지 않았습니다.")

        print("\n" + "="*80)
        print("[SUCCESS] 테스트 완료!")
        print("="*80)

    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    test_song_jaeheon_evaluation()
