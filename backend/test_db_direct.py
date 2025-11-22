"""
직접 DB에 사용자 생성해보기
"""
from database import SessionLocal
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_direct_db():
    """직접 DB 조작 테스트"""
    print("=" * 60)
    print("🔬 직접 DB 테스트")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 기존 사용자 확인
        existing = db.query(User).filter(User.email == "test@example.com").first()
        if existing:
            print(f"⚠️ 기존 사용자 발견: {existing.name} ({existing.email})")
            db.delete(existing)
            db.commit()
            print("✅ 기존 사용자 삭제")
        
        # 새 사용자 생성
        print("\n📝 새 사용자 생성 중...")
        user = User(
            email="test@example.com",
            name="Test User",
            password_hash=pwd_context.hash("test123")
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ 사용자 생성 성공!")
        print(f"  - ID: {user.id}")
        print(f"  - Email: {user.email}")
        print(f"  - Name: {user.name}")
        print(f"  - Created: {user.created_at}")
        
        # 조회 테스트
        found = db.query(User).filter(User.email == "test@example.com").first()
        if found:
            print(f"\n✅ 조회 성공: {found.name}")
        
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_direct_db()

