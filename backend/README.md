# Interview Practice API

FastAPI + SQLite 기반 AI 면접 연습 백엔드 서버

## 프로젝트 구조

```
backend/
├── main.py                    # FastAPI 앱 진입점
├── database.py                # 데이터베이스 연결 설정
├── models.py                  # SQLAlchemy 모델
├── schemas.py                 # Pydantic 스키마
├── init_db.py                 # 데이터베이스 초기화 스크립트
├── requirements.txt           # Python 의존성
├── create_test_data.py        # 테스트용 세션/질문 생성 스크립트
├── routers/                   # API 라우터
│   ├── users.py
│   ├── portfolios.py
│   ├── job_postings.py
│   ├── interviews.py
│   └── video_analysis.py     # 비디오 분석 API
└── pipeline/                  # 비디오 분석 파이프라인
    ├── video_io.py            # 프레임/오디오 추출
    ├── vision_mediapipe.py    # 얼굴 분석 (MediaPipe)
    ├── audio_analysis.py      # 음성 분석 (Whisper)
    ├── metrics.py             # 메트릭 계산
    └── feedback_generator.py  # AI 피드백 생성 (Gemini)
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
- `POST /api/interviews/sessions/{session_id}/videos?user_id={user_id}` - 영상 메타데이터 생성 (비디오 URL 등)
- `GET /api/interviews/videos/{video_id}` - 영상 조회
- `POST /api/interviews/videos/{video_id}/transcript` - 트랜스크립트 생성
- `POST /api/interviews/videos/{video_id}/metrics` - 비언어 지표 생성
- `POST /api/interviews/videos/{video_id}/timeline` - 타임라인 생성
- `POST /api/interviews/videos/{video_id}/feedback` - 피드백 생성
- `GET /api/interviews/videos/{video_id}/feedback` - 피드백 목록

### Video Analysis (비디오 분석 - 통합 엔드포인트)
- `POST /api/video/upload` - 비디오 파일 업로드 (파일 업로드 + DB 저장)
- `POST /api/video/analyze/{video_id}` - 비디오 분석 실행 (AI 피드백 포함, 통합)
- `GET /api/video/results/{video_id}` - 분석 결과 조회 (통합)
- `GET /api/video/status` - API 상태 확인

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

`.env` 파일 생성:

```bash
# Gemini API Key (선택사항 - AI 피드백용)
GEMINI_API_KEY=your_gemini_api_key_here
```

**Gemini API Key 발급:**
- https://makersuite.google.com/app/apikey

## 비디오 분석 기능

### 빠른 시작

1. **테스트 데이터 생성:**
```bash
python create_test_data.py
```

2. **비디오 업로드:**
```bash
# 통합 엔드포인트 (파일 업로드 + DB 저장)
POST /api/video/upload
- file: 비디오 파일 (.mp4, .webm, .mov)
- user_id: 사용자 ID
- session_id: 면접 세션 ID
- question_id: 면접 질문 ID
```

또는 개별 엔드포인트 사용 (비디오 메타데이터만 생성):
```bash
POST /api/interviews/sessions/{session_id}/videos?user_id={user_id}
- question_id: 질문 ID
- video_url: 비디오 URL (이미 업로드된 경우)
- audio_url: 오디오 URL
- duration_sec: 비디오 길이 (초)
```

3. **비디오 분석 (통합 엔드포인트):**
```bash
POST /api/video/analyze/{video_id}
```
이 엔드포인트는 다음을 자동으로 수행합니다:
- 비디오 분해 및 프레임 추출
- 얼굴/제스처 분석
- STT 및 메트릭 계산
- 피드백 생성
- DB 저장 (transcript, metrics, timeline, feedback)

또는 개별 엔드포인트 사용:
```bash
POST /api/interviews/videos/{video_id}/transcript  # 트랜스크립트 생성
POST /api/interviews/videos/{video_id}/metrics      # 비언어 지표 생성
POST /api/interviews/videos/{video_id}/timeline     # 타임라인 생성
POST /api/interviews/videos/{video_id}/feedback     # 피드백 생성
```

4. **결과 조회:**
```bash
GET /api/video/results/{video_id}  # 통합 결과 조회
```
또는 개별 조회:
```bash
GET /api/interviews/videos/{video_id}                    # 영상 정보
GET /api/interviews/videos/{video_id}/feedback            # 피드백 목록
```

### 분석 파이프라인

1. **비디오 분해** (5 FPS)
   - 프레임 추출 → `artifacts/{video_id}/frames/`
   - 오디오 추출 → `artifacts/{video_id}/audio.wav`

2. **얼굴/제스처 분석** (MediaPipe Face Mesh)
   - 랜드마크 추출 (478개 + iris)
   - Head pose (yaw/pitch/roll) - solvePnP
   - Gaze 분류 (LEFT/RIGHT/CENTER)
   - Smile 점수
   - 감정 인식 (happy/pleasant/neutral/focused/concerned)
   - 타임라인 생성: `[{"t": 0.0, "gaze": "CENTER", "smile": 0.8, "emotion": "happy", "pitch": -2, "yaw": 3}, ...]`

3. **STT + 말 속도** (Whisper)
   - 음성 전사
   - WPM 계산
   - Filler count ("음", "어", "uh", "um")

4. **지표 계산**
   - `center_gaze_ratio` = center 프레임 수 / 전체 유효 프레임
   - `smile_ratio` = smile score > threshold인 프레임 비율
   - `nod_count` = pitch 변화로 끄덕임 감지
   - `emotion_distribution` = 감정별 프레임 비율
   - `primary_emotion` = 가장 많은 감정

5. **피드백 생성**
   - 규칙 기반 (기본)
   - Gemini AI (GEMINI_API_KEY 설정시)

6. **DB 저장**
   - InterviewVideo, NonverbalMetrics, NonverbalTimeline
   - InterviewTranscript, Feedback

### 응답 형식

```json
{
  "center_gaze_ratio": 0.93,
  "smile_ratio": 0.35,
  "nod_count": 1,
  "emotion_distribution": {
    "happy": 0.59,
    "pleasant": 0.32,
    "neutral": 0.06,
    "concerned": 0.02
  },
  "primary_emotion": "happy",
  "wpm": 119.1,
  "filler_count": 4,
  "feedback": [
    "카메라 응시 비율이 93%로 매우 안정적이다...",
    "전체적으로 밝고 긍정적 표정(59%)이 우세하다..."
  ],
  "transcript": "...",
  "database_records": {...}
}
```

## 주의사항

- SQLite의 외래키 지원은 기본적으로 꺼져있으므로 `PRAGMA foreign_keys=ON`이 필요 (database.py에서 자동 설정)
- 비밀번호는 bcrypt로 해싱되어 저장됨
- UUID v4를 기본 ID로 사용
- 날짜/시간은 ISO 8601 형식의 문자열로 저장
- 비디오 분석은 CPU/GPU 사용량이 높으므로 서버 리소스 확인 필요
