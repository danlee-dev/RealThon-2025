# RealThon 2025 - AI 기반 면접 연습 플랫폼

취업 준비생을 위한 AI 기반 실전 면접 연습 시스템입니다. 포트폴리오와 직무 공고를 분석하여 맞춤형 면접 질문을 생성하고, 면접 영상을 분석하여 비언어적 피드백을 제공합니다.

## 주요 기능

### 1. 포트폴리오 분석
- PDF 포트폴리오 업로드 및 자동 파싱
- Gemini AI 기반 역량 평가 (6개 역량)
- GitHub 레포지토리 자동 분석
- 직무별(Frontend/Backend/AI) 스킬 매칭

### 2. 직무 공고 크롤링
- 주요 채용 플랫폼 지원 (Wanted, 사람인, 잡코리아, LinkedIn, Indeed)
- AI 기반 구조화된 데이터 파싱
- 필수/우대 스킬, 자격요건 자동 추출

### 3. 맞춤형 면접 질문 생성
- 포트폴리오 + 직무 공고 기반 질문 자동 생성
- 초기 질문 3개 자동 제공 (약점, 포트폴리오 검증, 직무 관련)
- 답변 기반 동적 꼬리 질문 생성

### 4. 비디오 면접 분석
- **음성 분석 (Whisper STT)**
  - 답변 내용 전사
  - 말하기 속도(WPM) 측정
  - 채움말(음, 어, 그 등) 횟수 카운트

- **비언어 분석 (MediaPipe)**
  - 시선 응시율 (center_gaze_ratio)
  - 미소 비율 (smile_ratio)
  - 고개 끄덕임 횟수 및 빈도
  - 감정 분류 (happy, pleasant, neutral, focused, concerned)
  - Head pose 추적 (yaw, pitch, roll)

- **AI 피드백 (Gemini)**
  - 강점 및 개선점 자동 분석
  - 시간대별 타임라인 알림
  - 구체적 행동 개선 제안

### 5. 음성 면접 (향후 확장)
- STT → LLM → TTS 파이프라인
- 실시간 음성 대화형 면접
- A6000 GPU 서버 마이그레이션 계획

## 기술 스택

### Backend
- **Framework**: FastAPI 0.115.5
- **Database**: SQLite (SQLAlchemy 2.0)
- **AI/ML**:
  - Google Gemini API (질문 생성, 피드백, 역량 평가)
  - OpenAI Whisper 20250625 (음성 전사)
  - MediaPipe 0.10.14 (얼굴/제스처 분석)
- **Video/Audio Processing**:
  - OpenCV 4.12.0
  - FFmpeg-python 0.2.0
  - PyTorch 2.5.1
- **Web Scraping**: BeautifulSoup4, lxml
- **Authentication**: JWT (python-jose), bcrypt

### Frontend
- **Framework**: Next.js 14.2.0 (React 18.3.0, TypeScript)
- **Styling**: Tailwind CSS 3.4.0
- **Animation**: Framer Motion 12.23.24
- **Data Visualization**:
  - Nivo (pie, radar charts)
- **Icons**: Lucide React 0.554.0

## 프로젝트 구조

```
RealThon-2025/
├── backend/
│   ├── main.py                       # FastAPI 앱 진입점
│   ├── database.py                   # DB 연결 설정
│   ├── models.py                     # SQLAlchemy 모델 (11개 테이블)
│   ├── schemas.py                    # Pydantic 스키마
│   ├── auth.py                       # JWT 인증
│   ├── routers/                      # API 라우터
│   │   ├── users.py                  # 사용자 관리
│   │   ├── portfolios.py             # 포트폴리오 CRUD + 역량 평가
│   │   ├── job_postings.py           # 공고 크롤링/CRUD
│   │   ├── interviews.py             # 면접 세션 및 질문 관리
│   │   ├── video_analysis.py         # 비디오 분석 파이프라인
│   │   └── voice_sessions.py         # 음성 면접 (향후)
│   ├── services/                     # 비즈니스 로직
│   │   ├── job_posting_crawler.py    # 채용 공고 크롤러
│   │   ├── cv_analyzer.py            # 포트폴리오 분석
│   │   ├── github_analyzer.py        # GitHub 레포 분석
│   │   ├── llm_analyzer.py           # Gemini 통합
│   │   ├── capability_evaluator.py   # 역량 평가 시스템
│   │   └── voice_orchestrator.py     # STT→LLM→TTS 파이프라인
│   ├── pipeline/                     # 비디오 분석 파이프라인
│   │   ├── video_io.py               # 프레임/오디오 추출
│   │   ├── vision_mediapipe.py       # MediaPipe 얼굴 분석
│   │   ├── audio_analysis.py         # Whisper STT
│   │   ├── metrics.py                # 메트릭 계산 (gaze, smile, nod 등)
│   │   └── feedback_generator.py     # Gemini 피드백 생성
│   ├── clients/                      # 외부 서비스 클라이언트
│   │   ├── base.py                   # 추상 인터페이스
│   │   ├── whisper_client.py         # STT 클라이언트
│   │   ├── gemini_client.py          # LLM 클라이언트
│   │   └── melo_tts_client.py        # TTS 클라이언트 (향후)
│   ├── rag/                          # RAG 데이터 및 유틸
│   │   ├── data/                     # 직무별 샘플 데이터
│   │   │   ├── frontend/
│   │   │   ├── backend/
│   │   │   ├── ai/
│   │   │   └── reference/            # 평가 기준, 질문 템플릿
│   │   └── utils/
│   │       ├── embedding.py
│   │       ├── retriever.py
│   │       └── interview_generator.py
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/                      # Next.js 페이지
│       │   ├── login/
│       │   ├── signup/
│       │   ├── onboarding/           # 역할/레벨 선택
│       │   ├── setup/                # 포트폴리오/공고 업로드
│       │   ├── interview/            # 면접 진행
│       │   ├── graph/                # 결과 시각화
│       │   └── profile/
│       ├── components/               # 재사용 컴포넌트
│       │   ├── Button.tsx
│       │   ├── Input.tsx
│       │   ├── Combobox.tsx
│       │   └── FileUpload.tsx
│       ├── lib/                      # 유틸리티
│       └── types/                    # TypeScript 타입
└── local_reference/                  # 참고 자료
```

## 데이터베이스 스키마

### 주요 테이블 (11개)

1. **user** - 사용자 정보 (역할, 레벨, GitHub 연동)
2. **portfolio** - 포트폴리오 파일 및 파싱 결과
3. **job_posting** - 직무 공고 (크롤링 데이터)
4. **interview_session** - 면접 세션
5. **interview_question** - 면접 질문 (초기 + 꼬리 질문)
6. **interview_video** - 답변 영상
7. **interview_transcript** - STT 전사 결과
8. **nonverbal_metrics** - 비언어 지표 요약 (gaze, smile, nod, wpm, filler)
9. **nonverbal_timeline** - 시계열 타임라인 (5 FPS, 프레임별 분석)
10. **feedback** - AI 피드백 (video-level, segment-level)
11. **capability_evaluation** - 포트폴리오 역량 평가 (6개 역량)

## 설치 및 실행

### 1. Backend 설정

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 GEMINI_API_KEY 추가

# 데이터베이스 초기화
python init_db_with_personas.py

# 서버 실행
python main.py
# 또는: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버 접속:
- API: http://localhost:8000
- Swagger 문서: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. Frontend 설정

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

프론트엔드 접속: http://localhost:3000

## 주요 API 엔드포인트

### 사용자
- `POST /api/users/` - 사용자 생성
- `GET /api/users/{user_id}` - 사용자 조회
- `DELETE /api/users/{user_id}` - 사용자 삭제

### 포트폴리오
- `POST /api/portfolios/?user_id={user_id}` - 포트폴리오 업로드
- `GET /api/portfolios/{portfolio_id}` - 포트폴리오 조회
- `GET /api/portfolios/{portfolio_id}/capability-evaluation` - 역량 평가 조회
- `POST /api/portfolios/{portfolio_id}/evaluate-capability` - 역량 평가 생성

### 직무 공고
- `POST /api/job-postings/crawl?user_id={user_id}` - URL 크롤링 및 저장
  - Body: `{ "url": "https://www.wanted.co.kr/wd/12345" }`
  - 지원: Wanted, 사람인, 잡코리아, 인크루트, LinkedIn, Indeed
- `GET /api/job-postings/{job_posting_id}` - 공고 조회
- `GET /api/job-postings/user/{user_id}` - 사용자별 공고 목록

### 면접 세션
- `POST /api/interviews/sessions?user_id={user_id}` - 세션 생성 (초기 질문 3개 자동 생성)
  - Body: `{ "job_posting_id": "xxx", "portfolio_id": "yyy" }`
- `GET /api/interviews/sessions/{session_id}` - 세션 조회
- `GET /api/interviews/sessions/{session_id}/questions` - 질문 목록
- `POST /api/interviews/sessions/{session_id}/questions` - 질문 추가
- `PATCH /api/interviews/sessions/{session_id}/complete` - 세션 완료

### 비디오 분석 (통합 파이프라인)
- `POST /api/video/upload` - 비디오 업로드
  - Multipart: file, user_id, session_id, question_id
- `POST /api/video/analyze/{video_id}` - 전체 분석 자동 실행
  - 프레임 추출 → 얼굴 분석 → STT → 메트릭 계산 → AI 피드백 → DB 저장
- `GET /api/video/results/{video_id}` - 분석 결과 조회
  - 응답: video, metrics, metadata, alerts, feedbacks, transcript, timeline

## 비디오 분석 파이프라인

### 1. 비디오 분해 (5 FPS)
- 프레임 추출: `artifacts/{video_id}/frames/`
- 오디오 추출: `artifacts/{video_id}/audio.wav`

### 2. 얼굴/제스처 분석 (MediaPipe Face Mesh)
- 478개 랜드마크 + iris 추출
- Head pose (yaw/pitch/roll) - solvePnP
- Gaze 분류 (LEFT/RIGHT/CENTER)
- Smile 점수 (adaptive threshold)
- 감정 인식 (Blendshapes 기반)

### 3. 음성 분석 (Whisper)
- STT 전사
- WPM (Words Per Minute) 계산
- 채움말 카운트 (정규식 패턴 매칭)

### 4. 메트릭 계산
| 메트릭 | 의미 | 범위 |
|-------|------|------|
| `center_gaze_ratio` | 카메라 정면 응시 비율 | 0.0~1.0 |
| `smile_ratio` | 미소 표정 비율 | 0.0~1.0 |
| `nod_count` | 고개 끄덕임 횟수 | 정수 |
| `nod_rate_per_min` | 분당 끄덕임 횟수 | float |
| `wpm` | 말하기 속도 (분당 단어 수) | float |
| `filler_count` | 채움말 횟수 | 정수 |
| `primary_emotion` | 주요 감정 | 카테고리 |
| `emotion_distribution` | 감정별 비율 | dict |

### 5. AI 피드백 생성
- Gemini 기반 구체적 피드백
- 강점/개선점 분석
- 타임라인 기반 실시간 알림 (smile >= 0.8 구간 감지)

### 6. DB 저장
- `nonverbal_metrics`: 지표 요약
- `nonverbal_timeline`: 프레임별 타임라인 (JSON)
- `interview_transcript`: STT 결과
- `feedback`: AI 피드백 목록

## 역량 평가 시스템

### 직무별 6개 역량

**Frontend**
1. Technical Skills (기술 역량)
2. Design Sense (디자인 감각)
3. Performance Optimization (성능 최적화)
4. Code Quality (코드 품질)
5. Collaboration (협업 능력)
6. Problem Solving (문제 해결)

**Backend**
1. Technical Skills (기술 역량)
2. Architecture Design (아키텍처 설계)
3. Database & Query Optimization (DB 최적화)
4. Code Quality (코드 품질)
5. Collaboration (협업 능력)
6. Problem Solving (문제 해결)

**AI**
1. Technical Skills (기술 역량)
2. Model Development (모델 개발)
3. Data Engineering (데이터 엔지니어링)
4. Code Quality (코드 품질)
5. Collaboration (협업 능력)
6. Problem Solving (문제 해결)

### 평가 응답 형식
```json
{
  "capabilities": [
    {
      "skill": "Technical Skills",
      "skill_ko": "기술 역량",
      "value": 85
    }
  ],
  "improvement_suggestions": [
    {
      "capability": "Technical Skills",
      "capability_ko": "기술 역량",
      "currentScore": 85,
      "title": "TypeScript 고급 기능 활용",
      "description": "현재 TypeScript를 사용하고 있으나...",
      "actionItems": [
        "Generic과 Conditional Types 학습",
        "Type Guards 적극 활용",
        "실무 프로젝트에 적용"
      ]
    }
  ]
}
```

## 환경 변수

```env
# Backend (.env)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (음성 면접 - 향후)
WHISPER_LOCAL_MODEL=base
WHISPER_LOCAL_DEVICE=cpu
MELO_TTS_BASE_URL=http://localhost:8001
USE_A6000_MODELS=false
A6000_STT_URL=http://a6000-server:8002
A6000_LLM_URL=http://a6000-server:8003
A6000_TTS_URL=http://a6000-server:8004
```

Gemini API Key 발급: https://makersuite.google.com/app/apikey

## 테스트 데이터 생성

```bash
cd backend

# 데이터베이스 초기화 + 테스트 사용자 생성
python init_db_with_personas.py

# 역량 평가 테스트
python test_capability_evaluation.py
```

## 성능 최적화

### 현재 (로컬 Whisper + Gemini API)
- STT 지연: ~2-5초
- LLM 지연: ~1-3초
- 비디오 분석: ~10-30초 (영상 길이에 따라)

### A6000 GPU 마이그레이션 계획
- STT 지연: ~0.5-1초 (Whisper Large-v3)
- LLM 지연: ~0.3-0.8초 (LLaMA/Gemma)
- TTS 지연: ~0.5-1초 (GPU Melo TTS)
- **총 지연**: ~1.3-2.8초

자세한 내용은 `backend/VOICE_INTERVIEW_ARCHITECTURE.md` 참조

## 주요 라이브러리 버전

### Backend
- FastAPI 0.115.5
- SQLAlchemy 2.0.36
- Pydantic 2.10.3
- OpenCV 4.12.0
- MediaPipe 0.10.14
- OpenAI Whisper 20250625
- PyTorch 2.5.1
- Google Generative AI 0.8.5

### Frontend
- Next.js 14.2.0
- React 18.3.0
- TypeScript 5
- Tailwind CSS 3.4.0
- Framer Motion 12.23.24

## 라이선스

MIT

## 기여

이 프로젝트는 RealThon 2025 해커톤을 위해 개발되었습니다.

## 참고 문서

- [Backend README](backend/README.md) - 자세한 API 문서
- [Voice Interview Architecture](backend/VOICE_INTERVIEW_ARCHITECTURE.md) - 음성 면접 시스템 설계
- [Refactoring Summary](backend/REFACTORING_SUMMARY.md) - 리팩토링 히스토리
