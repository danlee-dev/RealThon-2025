"""
테스트용 InterviewSession과 InterviewQuestion 생성
비디오 업로드 전에 필요한 데이터 생성
"""
from database import SessionLocal
from models import User, InterviewSession, InterviewQuestion
from datetime import datetime

def create_test_session_and_question(user_id: str):
    """테스트용 세션과 질문 생성"""
    db = SessionLocal()
    
    try:
        # 사용자 확인
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"❌ 사용자를 찾을 수 없습니다: {user_id}")
            print("\n먼저 사용자를 생성하세요:")
            print("  POST /api/users/")
            return None, None
        
        print(f"✅ 사용자 확인: {user.name} ({user.email})")
        
        # 세션 생성
        print("\n📝 면접 세션 생성 중...")
        session = InterviewSession(
            user_id=user_id,
            title="테스트 면접 세션",
            status="in_progress"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        print(f"✅ 세션 생성 완료!")
        print(f"  - Session ID: {session.id}")
        print(f"  - Title: {session.title}")
        print(f"  - Status: {session.status}")
        
        # 질문 생성
        print("\n❓ 면접 질문 생성 중...")
        question = InterviewQuestion(
            session_id=session.id,
            order=1,
            text="자기소개를 해주세요.",
            type="intro",
            source="manual"
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        
        print(f"✅ 질문 생성 완료!")
        print(f"  - Question ID: {question.id}")
        print(f"  - Text: {question.text}")
        
        return session.id, question.id
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        db.rollback()
        return None, None
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 테스트용 세션 & 질문 생성")
    print("=" * 60)
    
    # 사용자 ID 입력 (또는 첫 번째 사용자 사용)
    db = SessionLocal()
    first_user = db.query(User).first()
    db.close()
    
    if not first_user:
        print("\n❌ 사용자가 없습니다. 먼저 사용자를 생성하세요:")
        print("   POST /api/users/")
        exit(1)
    
    print(f"\n사용자: {first_user.name} ({first_user.email})")
    print(f"User ID: {first_user.id}")
    
    session_id, question_id = create_test_session_and_question(first_user.id)
    
    if session_id and question_id:
        print("\n" + "=" * 60)
        print("✅ 생성 완료! 이제 비디오를 업로드할 수 있습니다:")
        print("=" * 60)
        print(f"\nPOST /api/video/upload")
        print(f"  - file: (비디오 파일)")
        print(f"  - user_id: {first_user.id}")
        print(f"  - session_id: {session_id}")
        print(f"  - question_id: {question_id}")
        print("\n또는 Swagger UI에서:")
        print(f"  http://localhost:8000/docs")
    else:
        print("\n❌ 생성 실패")

