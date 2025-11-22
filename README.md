# RealThon 2025 - AI 면접 플랫폼

AI 기반 실시간 면접 시뮬레이션 및 분석 플랫폼입니다. 음성/수화 면접을 지원하며, AI가 실시간으로 질문을 생성하고 면접 종료 후 상세한 피드백을 제공합니다.

## 주요 기능

### 🎤 음성 면접 모드
- **실시간 TTS (Text-to-Speech)**: AI가 생성한 질문을 음성으로 출력
- **STT (Speech-to-Text)**: 면접자의 답변을 자동으로 텍스트로 변환
- **동적 꼬리 질문 생성**: 답변 내용을 분석하여 맞춤형 후속 질문 자동 생성
- **실시간 음성 피드백**: 볼륨 조절 및 음성 재생 제어

### 🤟 수화 면접 모드
- **비디오 녹화**: 수화 면접을 위한 전체 비디오 녹화 지원
- **오프라인 동작**: 백엔드 API 호출 없이 하드코딩된 질문으로 데모 가능
- **간소화된 UI**: 음성 관련 컨트롤 제거, 수화에 최적화된 인터페이스

### 📊 AI 면접 분석
- **다차원 평가**: 의사소통, 전문성, 문제해결, 태도 등 종합 분석
- **시각화 리포트**: Radar Chart, Pie Chart 등을 활용한 직관적인 분석 결과
- **맞춤형 피드백**: 직무별 특성을 고려한 개인화된 개선 제안

### 🎯 채용 공고 연동
- **URL 기반 질문 생성**: 채용 공고 URL 입력 시 맞춤형 질문 자동 생성
- **웹 스크래핑**: BeautifulSoup을 활용한 채용 공고 정보 추출
- **RAG 기반 질문 생성**: 포트폴리오 및 공고 정보를 기반으로 한 질문 생성

## 기술 스택

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animation**: Framer Motion
- **Charts**: Nivo (Radar, Pie Charts)
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.12
- **Database**: SQLAlchemy ORM
- **Authentication**: JWT (python-jose), bcrypt
- **AI/ML**:
  - Google Gemini API (LLM for question generation & analysis)
  - OpenAI Whisper (STT)
  - MediaPipe (Video processing)
- **Web Scraping**: BeautifulSoup4, lxml
- **File Processing**: PyPDF2 (Resume parsing)

### Infrastructure
- **Containerization**: Docker
- **Deployment**: Railway (with nixpacks.toml)
- **TTS Server**: MeloTTS (External service)

## 설치 및 실행

### Prerequisites
- Node.js 18+
- Python 3.12+
- Docker (optional)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:3000`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend will run on `http://localhost:8000`

### Environment Variables

Create `.env` file in the `backend` directory:

```env
# Database
DATABASE_URL=sqlite:///./interview.db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Gemini API
GOOGLE_API_KEY=your-gemini-api-key

# TTS Server (Optional)
TTS_SERVER_URL=http://localhost:5000
```

### Docker Deployment

```bash
# Build and run backend
cd backend
docker build -t realthon-backend .
docker run -p 8000:8000 realthon-backend

# Frontend deployment
cd frontend
npm run build
npm start
```

## 프로젝트 구조

```
RealThon-2025/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── interview/          # 면접 페이지
│   │   │   │   ├── components/
│   │   │   │   │   ├── screens/    # WaitingScreen, InterviewingScreen, etc.
│   │   │   │   │   └── layout/     # Header, Sidebar
│   │   │   │   └── page.tsx
│   │   │   ├── profile/            # 프로필 페이지
│   │   │   └── auth/               # 인증 페이지
│   │   ├── components/             # 공통 컴포넌트
│   │   ├── lib/                    # API clients, utilities
│   │   └── constants/              # 상수 정의
│   └── package.json
│
├── backend/
│   ├── main.py                     # FastAPI 앱 진입점
│   ├── routers/                    # API 라우터
│   │   ├── auth.py
│   │   ├── interviews.py
│   │   ├── job_postings.py
│   │   └── profiles.py
│   ├── clients/                    # External API clients
│   │   └── gemini_client.py
│   ├── pipeline/                   # AI 분석 파이프라인
│   │   └── llm_interview_evaluator.py
│   ├── rag/                        # RAG 시스템
│   ├── utils/                      # 유틸리티 함수
│   ├── requirements.txt
│   ├── Dockerfile
│   └── railway.json
│
└── README.md
```

## 주요 워크플로우

### 1. 면접 시작
1. 사용자가 채용 공고 URL 입력 (선택사항)
2. 백엔드가 URL 스크래핑 → 공고 정보 저장
3. 면접 세션 생성 → 초기 질문 4개 생성
4. TTS 서버에 질문 전송 → 음성 파일 생성

### 2. 면접 진행 (음성 모드)
1. 질문 음성 자동 재생
2. 사용자 답변 녹음 → STT 변환
3. 답변 저장 → AI가 꼬리 질문 생성
4. 총 6번 답변 완료 → 면접 종료

### 3. 면접 진행 (수화 모드)
1. 하드코딩된 질문 표시
2. 비디오 녹화 → 백엔드 호출 없이 로컬 처리
3. 2개 질문 완료 → 면접 종료

### 4. 분석 및 피드백
1. 모든 답변 데이터를 AI에 전송
2. Gemini API로 종합 분석 수행
3. 점수 및 피드백 생성 → 시각화
4. 결과 화면에 표시

## 특별 기능

### React 18 Strict Mode 대응
- TTS 중복 재생 방지를 위한 useRef 기반 중복 호출 차단
- Cleanup 함수를 통한 오디오 리소스 관리

### 동적 질문 카운터
- 일반 모드: 실제 질문 개수 기반 (4-6개)
- 수화 모드: 하드코딩된 카운터 (1/3, 2/4)

### 반응형 UI
- Framer Motion을 활용한 부드러운 화면 전환
- layoutId 기반 Shared Element Transition

## 개발자

RealThon 2025 Team

## 라이선스

This project is private and proprietary.
