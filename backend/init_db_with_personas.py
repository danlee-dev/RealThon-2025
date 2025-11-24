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
        "cv_file": "FE.pdf"
    },
    {
        "name": "이성민",
        "email": "first.last@gmail.com",
        "password": "password123",
        "role": "ROLE_BE",
        "level": "LEVEL_MID",
        "github_username": "sungmin-lee",
        "github_token": None,  # Optional: 사용자별 GitHub token
        "cv_file": "BE.pdf"
    },
    {
        "name": "송재헌",
        "email": "thdwogjs040923@korea.ac.kr",
        "password": "password123",
        "role": "ROLE_AI",
        "level": "LEVEL_JUNIOR",
        "github_username": "dreameerbb",
        "github_token": "FROM_ENV",  # Will be replaced from .env
        "cv_file": "my_cv.pdf"  # AI developer CV
    }
]


def copy_persona_cv_files():
    """
    local_reference에서 페르소나 CV PDF 파일을 backend/static/uploads로 복사
    """
    source_dir = os.path.join(os.path.dirname(__file__), "..", "local_reference")
    target_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")

    # static/uploads 디렉토리 생성
    os.makedirs(target_dir, exist_ok=True)

    copied_files = {}

    for persona in PERSONAS:
        cv_file = persona.get("cv_file")

        # cv_file이 없는 경우 스킵
        if not cv_file:
            continue

        source_path = os.path.join(source_dir, cv_file)
        target_path = os.path.join(target_dir, cv_file)

        if os.path.exists(source_path):
            shutil.copy2(source_path, target_path)
            copied_files[cv_file] = f"/static/uploads/{cv_file}"
            print(f"[OK] Copied {cv_file} -> {target_path}")
        else:
            print(f"[WARN] {cv_file} not found at {source_path}")

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
    from dotenv import load_dotenv

    load_dotenv()

    print("\n" + "=" * 60)
    print("CREATING PERSONAS")
    print("=" * 60)

    # CV PDF 파일 복사
    copied_files = copy_persona_cv_files()

    with Session(db_engine) as session:
        for persona in PERSONAS:
            # GitHub 토큰 처리 (FROM_ENV이면 환경변수에서 가져오기)
            github_token = persona.get("github_token")
            if github_token == "FROM_ENV":
                github_token = os.getenv("GITHUB_TOKEN")

            # User 생성
            user = User(
                id=str(uuid.uuid4()),
                name=persona["name"],
                email=persona["email"],
                password_hash=pwd_context.hash(persona["password"]),
                role=persona["role"],
                level=persona["level"],
                github_username=persona["github_username"],
                github_token=github_token
            )
            session.add(user)
            session.flush()  # user.id 생성

            print(f"\n[OK] Created user: {user.name}")
            print(f"     - Email: {user.email}")
            print(f"     - Role: {user.role}")
            print(f"     - Level: {user.level}")
            print(f"     - GitHub Username: {user.github_username}")
            print(f"     - GitHub Token: {'(not set)' if not user.github_token else '***' + user.github_token[-4:]}")

            # Portfolio 생성 (CV PDF 파일 연결)
            cv_file = persona.get("cv_file")
            if cv_file and cv_file in copied_files:
                portfolio = Portfolio(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    file_url=copied_files[cv_file],
                    filename=cv_file,
                    parsed_text=None,  # 나중에 CV 분석으로 채움
                    summary=None  # 나중에 CV 분석으로 채움
                )
                session.add(portfolio)

                print(f"     - Portfolio: {portfolio.filename}")
                print(f"     - File URL: {portfolio.file_url}")
            else:
                print(f"     - Portfolio: (not set - GitHub analysis only)")

        session.commit()
        print("\n[SUCCESS] All personas created successfully!")


def analyze_persona_cvs(db_engine):
    """페르소나 CV 자동 분석"""
    from sqlalchemy.orm import Session
    from services.cv_analyzer import analyze_cv_pipeline

    print("\n" + "=" * 60)
    print("ANALYZING PERSONA CVs")
    print("=" * 60)

    with Session(db_engine) as session:
        users = session.query(User).all()

        for user in users:
            portfolios = session.query(Portfolio).filter(Portfolio.user_id == user.id).all()

            if not portfolios:
                print(f"\n[SKIP] {user.name} - No portfolio found")
                continue

            portfolio = portfolios[0]

            print(f"\n[INFO] Analyzing CV for {user.name}...")
            print(f"       Portfolio: {portfolio.filename}")
            print(f"       Role: {user.role}, Level: {user.level}")

            try:
                result = analyze_cv_pipeline(
                    portfolio_id=portfolio.id,
                    user_id=user.id,
                    db=session
                )

                print(f"[SUCCESS] CV analyzed!")
                print(f"          - Score: {result['overall_score']}/100")
                print(f"          - Possessed skills: {len(result['possessed_skills'])}")
                print(f"          - Missing skills: {len(result['missing_skills'])}")

            except Exception as e:
                print(f"[ERROR] Failed to analyze CV: {str(e)}")


def main():
    """메인 함수"""
    print("\n" + "🔄" * 30)
    print("Starting Database Initialization with Personas")
    print("🔄" * 30 + "\n")

    # 1. 데이터베이스 초기화
    db_engine = init_database()

    # 2. 페르소나 생성
    create_personas(db_engine)

    # 3. CV 자동 분석 생략 (사용자가 나중에 수동으로 실행)
    print("\n" + "=" * 60)
    print("INITIALIZATION COMPLETE")
    print("=" * 60)
    print("\nYou can now:")
    print("1. Start the FastAPI server: uvicorn main:app --reload")
    print("2. Run CV analysis: POST /api/portfolios/{portfolio_id}/analyze")
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
