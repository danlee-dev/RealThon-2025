"""
데이터베이스 초기화 스크립트 (페르소나 포함)

SQLite 데이터베이스를 초기화하고 2개의 페르소나(FE, BE) 생성
"""

import os
import shutil
from database import engine, Base
from models import User, Portfolio
from passlib.context import CryptContext
import uuid

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 페르소나 데이터
PERSONAS = [
    {
        "name": "이정민",
        "email": "danmin@jeong-min.com",
        "password": "password123",
        "role": "ROLE_FE",
        "level": "LEVEL_MID",
        "github_username": "danmin",
        "github_token": None,  # Optional: 사용자별 GitHub token
        "cv_image": "FE.png"
    },
    {
        "name": "이성민",
        "email": "first.last@gmail.com",
        "password": "password123",
        "role": "ROLE_BE",
        "level": "LEVEL_MID",
        "github_username": "sungmin-lee",
        "github_token": None,  # Optional: 사용자별 GitHub token
        "cv_image": "BE.png"
    }
]


def copy_persona_images():
    """
    local_reference에서 페르소나 CV 이미지를 backend/static/uploads로 복사
    """
    source_dir = os.path.join(os.path.dirname(__file__), "..", "local_reference")
    target_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")

    # static/uploads 디렉토리 생성
    os.makedirs(target_dir, exist_ok=True)

    copied_files = {}

    for persona in PERSONAS:
        cv_image = persona["cv_image"]
        source_path = os.path.join(source_dir, cv_image)
        target_path = os.path.join(target_dir, cv_image)

        if os.path.exists(source_path):
            shutil.copy2(source_path, target_path)
            copied_files[cv_image] = f"/static/uploads/{cv_image}"
            print(f"[OK] Copied {cv_image} -> {target_path}")
        else:
            print(f"[WARN] {cv_image} not found at {source_path}")

    return copied_files


def init_database():
    """데이터베이스 초기화 및 테이블 생성"""
    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)

    # 기존 데이터베이스 파일 삭제 (완전 초기화)
    db_file = "interview_app.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"[OK] Removed existing database: {db_file}")

    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    print("[OK] Created all tables")

    return engine


def create_personas(db_engine):
    """페르소나 사용자 및 포트폴리오 생성"""
    from sqlalchemy.orm import Session

    print("\n" + "=" * 60)
    print("CREATING PERSONAS")
    print("=" * 60)

    # CV 이미지 복사
    copied_files = copy_persona_images()

    with Session(db_engine) as session:
        for persona in PERSONAS:
            # User 생성
            user = User(
                id=str(uuid.uuid4()),
                name=persona["name"],
                email=persona["email"],
                password_hash=pwd_context.hash(persona["password"]),
                role=persona["role"],
                level=persona["level"],
                github_username=persona["github_username"],
                github_token=persona.get("github_token")
            )
            session.add(user)
            session.flush()  # user.id 생성

            print(f"\n[OK] Created user: {user.name}")
            print(f"     - Email: {user.email}")
            print(f"     - Role: {user.role}")
            print(f"     - Level: {user.level}")
            print(f"     - GitHub Username: {user.github_username}")
            print(f"     - GitHub Token: {'(not set)' if not user.github_token else '***' + user.github_token[-4:]}")

            # Portfolio 생성 (CV 이미지 연결)
            cv_image = persona["cv_image"]
            if cv_image in copied_files:
                portfolio = Portfolio(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    file_url=copied_files[cv_image],
                    filename=cv_image,
                    parsed_text=None,  # 나중에 CV 분석으로 채움
                    summary=None  # 나중에 CV 분석으로 채움
                )
                session.add(portfolio)

                print(f"     - Portfolio: {portfolio.filename}")
                print(f"     - File URL: {portfolio.file_url}")

        session.commit()
        print("\n[SUCCESS] All personas created successfully!")


def main():
    """메인 함수"""
    print("\n" + "🔄" * 30)
    print("Starting Database Initialization with Personas")
    print("🔄" * 30 + "\n")

    # 1. 데이터베이스 초기화
    db_engine = init_database()

    # 2. 페르소나 생성
    create_personas(db_engine)

    print("\n" + "=" * 60)
    print("INITIALIZATION COMPLETE")
    print("=" * 60)
    print("\nYou can now:")
    print("1. Run CV analysis on personas to populate portfolio data")
    print("2. Start the FastAPI server: uvicorn main:app --reload")
    print("\nPersona Credentials:")
    for persona in PERSONAS:
        print(f"  - {persona['name']}: {persona['email']} / {persona['password']}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # UTF-8 인코딩 설정 (한글 지원)
    import sys
    import locale

    # 윈도우 환경에서 UTF-8 강제 설정
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    # 기본 인코딩을 UTF-8로 설정
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

    main()
