# Interview Practice API

FastAPI + SQLite 기반 AI 면접 연습 백엔드 서버

## 프로젝트 구조

```
backend/
├── main.py              # FastAPI 앱 진입점
├── database.py          # 데이터베이스 연결 설정
├── models.py            # SQLAlchemy 모델
├── schemas.py           # Pydantic 스키마
├── init_db.py           # 데이터베이스 초기화 스크립트
├── requirements.txt     # Python 의존성
└── routers/            # API 라우터
    ├── users.py
    ├── portfolios.py
    ├── job_postings.py
    └── interviews.py
```

## 데이터베이스 스키마

### 주요 테이블

1. **user** - 사용자 정보
2. **portfolio** - 포트폴리오 PDF 파일 및 파싱 결과
3. **job_posting** - 회사 공고 정보
4. **interview_session** - 면접 세션
5. **interview_question** - 면접 질문
6. **interview_video** - 답변 영상
7. **interview_transcript** - STT 텍스트
8. **nonverbal_metrics** - 비언어 지표 요약
9. **nonverbal_timeline** - 시계열 분석 데이터
10. **feedback** - 피드백

## 설치 및 실행

### 1. 가상환경 생성 및 활성화

```bash
cd backend
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 데이터베이스 초기화

```bash
python init_db.py
```

### 4. 서버 실행

```bash
# 개발 모드 (자동 리로드)
python main.py

# 또는
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 시작되면:
- API 서버: http://localhost:8000
- API 문서 (Swagger): http://localhost:8000/docs
- API 문서 (ReDoc): http://localhost:8000/redoc

## API 엔드포인트

### Users
- `POST /api/users/` - 사용자 생성
- `GET /api/users/{user_id}` - 사용자 조회
- `GET /api/users/` - 사용자 목록
- `DELETE /api/users/{user_id}` - 사용자 삭제

### Portfolios
- `POST /api/portfolios/?user_id={user_id}` - 포트폴리오 생성
- `GET /api/portfolios/{portfolio_id}` - 포트폴리오 조회
- `GET /api/portfolios/user/{user_id}` - 사용자별 포트폴리오 목록
- `DELETE /api/portfolios/{portfolio_id}` - 포트폴리오 삭제

### Job Postings
- `POST /api/job-postings/?user_id={user_id}` - 공고 생성
- `GET /api/job-postings/{job_posting_id}` - 공고 조회
- `GET /api/job-postings/user/{user_id}` - 사용자별 공고 목록
- `DELETE /api/job-postings/{job_posting_id}` - 공고 삭제

### Interviews
- `POST /api/interviews/sessions?user_id={user_id}` - 세션 생성
- `GET /api/interviews/sessions/{session_id}` - 세션 조회
- `GET /api/interviews/sessions/user/{user_id}` - 사용자별 세션 목록
- `PATCH /api/interviews/sessions/{session_id}/complete` - 세션 완료
- `POST /api/interviews/sessions/{session_id}/questions` - 질문 생성
- `GET /api/interviews/sessions/{session_id}/questions` - 세션 질문 목록
- `POST /api/interviews/sessions/{session_id}/videos?user_id={user_id}` - 영상 업로드
- `GET /api/interviews/videos/{video_id}` - 영상 조회
- `POST /api/interviews/videos/{video_id}/transcript` - 트랜스크립트 생성
- `POST /api/interviews/videos/{video_id}/metrics` - 비언어 지표 생성
- `POST /api/interviews/videos/{video_id}/timeline` - 타임라인 생성
- `POST /api/interviews/videos/{video_id}/feedback` - 피드백 생성
- `GET /api/interviews/videos/{video_id}/feedback` - 피드백 목록

## 데이터베이스 관리

### 데이터베이스 초기화
```bash
python init_db.py
```

### 데이터베이스 삭제 (모든 데이터 삭제)
```bash
python init_db.py drop
```

## 개발 가이드

### 새로운 라우터 추가

1. `routers/` 폴더에 새 파일 생성
2. APIRouter 인스턴스 생성
3. `main.py`에서 라우터 import 및 include

### 새로운 모델 추가

1. `models.py`에 SQLAlchemy 모델 추가
2. `schemas.py`에 Pydantic 스키마 추가
3. `init_db.py` 다시 실행

## 환경 변수

`.env.example` 파일을 참조하여 `.env` 파일 생성:

```bash
cp .env.example .env
```

## 주의사항

- SQLite의 외래키 지원은 기본적으로 꺼져있으므로 `PRAGMA foreign_keys=ON`이 필요 (database.py에서 자동 설정)
- 비밀번호는 bcrypt로 해싱되어 저장됨
- UUID v4를 기본 ID로 사용
- 날짜/시간은 ISO 8601 형식의 문자열로 저장
