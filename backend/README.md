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

### Interviews (세션 및 질문 관리)
- `POST /api/interviews/sessions?user_id={user_id}` - 면접 세션 생성
- `GET /api/interviews/sessions/{session_id}` - 세션 조회
- `GET /api/interviews/sessions/user/{user_id}` - 사용자별 세션 목록
- `PATCH /api/interviews/sessions/{session_id}/complete` - 세션 완료 처리
- `POST /api/interviews/sessions/{session_id}/questions` - 면접 질문 생성
- `GET /api/interviews/sessions/{session_id}/questions` - 세션 질문 목록 조회

### Video Analysis (비디오 분석 - 통합 파이프라인) ⭐️
**권장 워크플로우**: 아래 3개 엔드포인트만 사용하면 모든 분석이 자동으로 완료됩니다.

- `GET /api/video/status` - API 상태 확인 (Gemini 활성화 여부 등)
- `POST /api/video/upload` - 비디오 파일 업로드 + DB 저장
  - 파일, user_id, session_id, question_id를 한 번에 전송
- `POST /api/video/analyze/{video_id}` - **전체 비디오 분석 자동 실행** ⚡️
  - 프레임 추출 → 얼굴 분석 → STT → 메트릭 계산 → AI 피드백 → DB 저장
  - 모든 과정이 한 번의 호출로 완료
- `GET /api/video/results/{video_id}` - 분석 결과 조회 (metrics, feedbacks, transcript, timeline 포함)

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
POST /api/video/upload
- file: 비디오 파일 (.mp4, .webm, .mov)
- user_id: 사용자 ID
- session_id: 면접 세션 ID
- question_id: 면접 질문 ID
```

3. **비디오 분석 (통합 엔드포인트):**
```bash
POST /api/video/analyze/{video_id}
```
이 엔드포인트는 다음을 **자동으로 한 번에** 수행합니다:
- 비디오 분해 및 프레임 추출 (5 FPS)
- 얼굴/제스처 분석 (MediaPipe)
- 음성 전사 (Whisper STT)
- 메트릭 계산 (gaze, smile, nod, WPM, filler)
- 피드백 생성 (Gemini AI 또는 규칙 기반)
- DB 저장 (transcript, metrics, timeline, feedback)

**참고**: 같은 video_id로 재분석하면 기존 결과를 삭제하고 새로 저장합니다.

4. **결과 조회:**
```bash
GET /api/video/results/{video_id}
```
응답에 포함되는 내용:
- `video`: 비디오 메타데이터
- `metrics`: 비언어 지표
  - 핵심 지표: `center_gaze_ratio`, `smile_ratio`, `nod_count`, `wpm`, `filler_count`, `primary_emotion`, `emotion_distribution`
  - **`metadata`**: 계산 메타데이터 (새로 추가) - 디버깅 및 투명성을 위한 정보
    - `fps_analyzed`: 분석에 사용된 FPS (예: 5.0)
    - `frame_count_total`: 추출된 총 프레임 수 (예: 404)
    - `frame_count_valid`: 유효한 프레임 수 (예: 167)
    - `thresholds`: 규칙 기반 임계값 (smile_threshold, nod_pitch_delta_threshold 등)
    - `models`: 사용된 모델 버전/설정 (MediaPipe, Whisper 등)
    - `confidence`: 신뢰도 집계 (gaze_confidence_mean, valid_frame_ratio)
    - `outlier_flags`: 이상치 플래그 (pose_outlier_ratio - solvePnP 오류 비율)
- `feedbacks`: 피드백 목록
- `transcript`: STT 전사 결과
- `timeline`: 타임라인 JSON 배열 (각 프레임별 gaze, smile, emotion, pitch, yaw 등)
- `timeline_available`: 타임라인 존재 여부

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

### 응답 형식 및 필드 설명

**GET /api/video/results/{video_id}** 응답 예시 및 상세 설명:

```json
{
  "video": {
    "id": "video-uuid",                    // 비디오 고유 ID
    "user_id": "user-uuid",                // 사용자 ID
    "session_id": "session-uuid",          // 면접 세션 ID
    "question_id": "question-uuid",        // 면접 질문 ID
    "duration_sec": 37.5,                  // 비디오 길이 (초)
    "created_at": "2025-01-15T10:30:00"    // 업로드 시간
  },
  "metrics": {
    // === 핵심 비언어 지표 ===
    
    "center_gaze_ratio": 0.93,
    // 🎯 의미: 전체 유효 프레임 중 카메라를 정면으로 응시한 비율 (0.0 ~ 1.0)
    // 📊 평가: 0.7 이상 = 우수 (신뢰감, 자신감 전달)
    //         0.5~0.7 = 보통 (개선 여지)
    //         0.5 미만 = 개선 필요 (불안정한 인상)
    // 💡 활용: 아이 컨택 능력 평가, 면접 준비도 측정
    
    "smile_ratio": 0.35,
    // 🎯 의미: 미소 점수가 임계값을 넘은 프레임의 비율 (0.0 ~ 1.0)
    // 📊 평가: 0.25~0.5 = 자연스러움 (친근하고 긍정적 인상)
    //         0.1~0.25 = 다소 부족 (표정 경직 가능성)
    //         0.5 이상 = 과도 (부자연스러울 수 있음)
    // 💡 활용: 표정 관리 능력, 친화력 평가
    // 🔧 계산: 적응형 임계값 (mean + 0.5*std) 사용하여 개인별 최적화
    
    "nod_count": 1,
    // 🎯 의미: 비디오 전체에서 감지된 고개 끄덕임 횟수 (정수)
    // 📊 평가: 1~3회 = 적절함 (경청과 공감 표현)
    //         0회 = 부족 (무반응으로 보일 수 있음)
    //         4회 이상 = 과다 (산만한 인상)
    // 💡 활용: 경청 자세, 비언어 소통 능력 평가
    // 🔧 계산: pitch 각도 변화를 평활화하여 8도 이상 변동 시 끄덕임으로 감지
    
    "wpm": 119.1,
    // 🎯 의미: Words Per Minute - 분당 단어 수 (평균 말하기 속도)
    // 📊 평가: 140~180 = 이상적 (명확하고 안정적인 템포)
    //         120~140 = 다소 느림 (신중하지만 답답할 수 있음)
    //         100 미만 = 매우 느림 (준비 부족으로 보일 수 있음)
    //         180~200 = 다소 빠름 (긴장감 전달 가능)
    //         200 이상 = 매우 빠름 (이해 어려움)
    // 💡 활용: 발표 능력, 긴장도 측정
    // 🔧 계산: 전사된 텍스트의 단어 수 / (비디오 길이 / 60)
    
    "filler_count": 4,
    // 🎯 의미: 불필요한 채움말 사용 횟수 (음, 어, 그, uh, um, like 등)
    // 📊 평가: 0~5회 = 우수 (유창하고 자신감 있는 답변)
    //         6~10회 = 보통 (약간의 망설임)
    //         11회 이상 = 개선 필요 (준비 부족 또는 긴장)
    // 💡 활용: 답변 유창성, 준비도, 긴장도 평가
    // 🔧 계산: 정규식으로 한국어/영어 채움말 패턴 매칭 및 카운트
    
    "primary_emotion": "happy",
    // 🎯 의미: 전체 비디오에서 가장 많이 표현된 감정 (카테고리)
    // 📊 감정 종류: 
    //    - "happy": 행복/즐거움 (넓은 미소, 밝은 표정)
    //    - "pleasant": 유쾌함/만족 (미소, 편안한 표정)
    //    - "neutral": 중립 (무표정, 집중)
    //    - "focused": 집중 (약간의 긴장, 진지함)
    //    - "concerned": 우려/걱정 (미간 찌푸림, 긴장)
    // 💡 활용: 전반적 감정 상태, 면접 태도 평가
    // 🔧 계산: MediaPipe Blendshapes 기반 또는 기하학적 특징 기반 감정 분류
    
    "emotion_distribution": {
      "happy": 0.59,         // 59%의 프레임에서 행복한 표정
      "pleasant": 0.32,      // 32%의 프레임에서 유쾌한 표정
      "neutral": 0.06,       // 6%의 프레임에서 중립 표정
      "concerned": 0.02      // 2%의 프레임에서 우려 표정
    },
    // 🎯 의미: 각 감정이 차지하는 비율 (합계 = 1.0)
    // 📊 이상적 패턴: pleasant/happy 합산 50~70% (긍정적이지만 자연스러움)
    //                neutral 20~30% (진지함과 집중력)
    //                concerned 10% 미만 (과도한 긴장 방지)
    // 💡 활용: 감정 안정성, 표정 다양성, 면접 태도 분석
    
    // === 계산 메타데이터 (투명성 및 디버깅용) ===
    "metadata": {
      // 프레임 분석 정보
      "fps_analyzed": 5.0,
      // 🎯 의미: 비디오에서 초당 추출/분석한 프레임 수
      // 💡 활용: 분석 정밀도 파악 (5 FPS = 0.2초마다 1프레임 분석)
      
      "frame_count_total": 404,
      // 🎯 의미: 추출된 전체 프레임 수 (duration_sec * fps_analyzed)
      // 💡 활용: 전체 데이터 포인트 수 확인
      
      "frame_count_valid": 167,
      // 🎯 의미: 얼굴 감지 성공 + 유효한 특징 추출된 프레임 수
      // 📊 평가: valid/total 비율이 낮으면 비디오 품질 문제 (조명, 각도, 흔들림)
      // 💡 활용: 분석 신뢰도 평가, 재촬영 필요성 판단
      
      "duration_sec": 37.5,
      // 🎯 의미: 실제 비디오 재생 시간 (초)
      
      // 규칙 기반 임계값
      "thresholds": {
        "smile_threshold": "adaptive (mean + 0.5*std)",
        // 🎯 의미: 미소 감지에 사용된 임계값 (개인별 적응형)
        // 💡 활용: 개인차 고려한 공정한 평가 확인
        
        "gaze_center_range": "CENTER classification from MediaPipe",
        // 🎯 의미: 중앙 응시 판정 기준 (MediaPipe 내부 분류 사용)
        
        "nod_pitch_delta_threshold": 8.0,
        // 🎯 의미: 끄덕임 감지를 위한 최소 pitch 각도 변화 (도)
        // 💡 활용: 미세한 움직임과 명확한 끄덕임 구분
        
        "pose_outlier_thresholds": {
          "yaw": 60,    // 좌우 회전 한계 (도)
          "pitch": 45,  // 상하 회전 한계 (도)
          "roll": 40    // 좌우 기울임 한계 (도)
        }
        // 🎯 의미: 물리적으로 불가능한 포즈 감지 기준
        // 💡 활용: solvePnP 오류 감지, 데이터 품질 평가
      },
      
      // 사용된 모델 정보
      "models": {
        "vision_model": "MediaPipe FaceMesh",
        // 🎯 의미: 얼굴 특징 추출에 사용된 모델
        
        "vision_config": {
          "refine_landmarks": true,
          "min_detection_confidence": 0.5,
          "min_tracking_confidence": 0.5
        },
        // 🎯 의미: 얼굴 감지 설정 파라미터
        
        "emotion_model": "rule-based from landmarks + blendshapes (if available)",
        // 🎯 의미: 감정 분류 방식 (Blendshapes 52개 파라미터 또는 기하학적 규칙)
        
        "stt_model": "openai-whisper-base",
        // 🎯 의미: 음성 인식 모델 (base = 74M 파라미터, 빠르고 정확)
        
        "stt_version": "20250625"
        // 🎯 의미: Whisper 모델 버전 (requirements.txt 기준)
      },
      
      // 신뢰도 지표
      "confidence": {
        "gaze_confidence_mean": 0.95,
        // 🎯 의미: 시선 추적 신뢰도 평균 (유효 프레임 비율로 근사)
        // 📊 평가: 0.9 이상 = 높은 신뢰도, 0.7 미만 = 낮은 신뢰도 (재분석 권장)
        
        "valid_frame_ratio": 0.41
        // 🎯 의미: 전체 프레임 중 유효 프레임 비율 (167/404 = 0.41)
        // 📊 평가: 0.5 이상 = 양호, 0.3~0.5 = 보통, 0.3 미만 = 비디오 품질 문제
        // 💡 활용: 분석 결과 신뢰도 평가, UI에서 경고 표시 여부 결정
      },
      
      // 이상치 플래그
      "outlier_flags": {
        "pose_outlier_ratio": 0.02,
        // 🎯 의미: 물리적으로 불가능한 포즈를 가진 프레임 비율 (2%)
        // 📊 평가: 0.05 미만 = 정상, 0.05~0.15 = 약간 불안정, 0.15 이상 = 매우 불안정
        // 💡 활용: 카메라 흔들림, 조명 변화, solvePnP 오류 감지
        
        "pose_outlier_description": "Proportion of frames with extreme head pose angles (likely solvePnP errors)"
        // 🎯 의미: 이상치 플래그 설명
      }
    }
  },
  
  // === 피드백 (AI 또는 규칙 기반) ===
  "feedbacks": [
    {
      "id": "feedback-uuid",
      "title": "강점 #1",
      "message": "카메라 응시 비율이 93%로 매우 안정적이다. 정면 시선 유지가 잘 되어 신뢰감 있는 인상을 준다...",
      "severity": "info",      // info = 강점, warning = 개선 필요, suggestion = 제안
      "level": "video"         // video = 전체 비디오 피드백, segment = 특정 구간 피드백
    }
  ],
  // 🎯 의미: 구체적이고 실천 가능한 면접 코칭 피드백
  // 💡 구성: 관찰 → 해석 → 개선 제안 (1~3가지 구체적 솔루션)
  
  // === 전사 텍스트 ===
  "transcript": "안녕하세요, 저는 백엔드 개발자로 지원한...",
  // 🎯 의미: Whisper STT로 변환된 음성 전사 텍스트
  // 💡 활용: 답변 내용 분석, 키워드 추출, 필러 감지
  
  // === 타임라인 (프레임별 상세 데이터) ===
  "timeline": [
    {
      "t": 0.0,              // 타임스탬프 (초)
      "valid": true,         // 이 프레임이 분석에 사용되었는지 (얼굴 감지 성공 여부)
      "gaze": "CENTER",      // 시선 방향: CENTER, LEFT, RIGHT
      "smile": 0.8,          // 미소 점수 (0.0 ~ 1.0, 높을수록 웃는 표정)
      "emotion": "happy",    // 감정 분류 (Blendshapes 또는 규칙 기반)
      "pitch": -2.1,         // 고개 상하 각도 (도, - = 아래, + = 위)
      "yaw": 3.5,            // 고개 좌우 각도 (도, - = 왼쪽, + = 오른쪽)
      "roll": -1.2           // 고개 기울임 각도 (도, - = 왼쪽 기울임, + = 오른쪽 기울임)
    }
    // ... 더 많은 프레임
  ],
  // 🎯 의미: 시간에 따른 모든 비언어 신호의 변화 추적
  // 💡 활용: 타임라인 시각화, 특정 구간 분석, 패턴 감지
  // 📊 데이터: 5 FPS로 분석 시 30초 비디오 = 약 150개 프레임
  
  "timeline_available": true
  // 🎯 의미: 타임라인 데이터 존재 여부 (분석 완료 여부)
}
```

### 주요 메트릭 요약표

| 메트릭 | 의미 | 이상적 범위 | 개선 필요 |
|-------|------|-----------|----------|
| **center_gaze_ratio** | 카메라 응시 비율 | 70% 이상 | 50% 미만 |
| **smile_ratio** | 미소/긍정 표정 비율 | 25~50% | 10% 미만 or 60% 이상 |
| **nod_count** | 끄덕임 횟수 | 1~3회 | 0회 or 5회 이상 |
| **wpm** | 말하기 속도 | 140~180 | 120 미만 or 200 이상 |
| **filler_count** | 채움말 횟수 | 5회 이하 | 11회 이상 |
| **valid_frame_ratio** | 분석 신뢰도 | 50% 이상 | 30% 미만 |
| **pose_outlier_ratio** | 포즈 안정성 | 5% 미만 | 15% 이상 |

## 주의사항

- SQLite의 외래키 지원은 기본적으로 꺼져있으므로 `PRAGMA foreign_keys=ON`이 필요 (database.py에서 자동 설정)
- 비밀번호는 bcrypt로 해싱되어 저장됨
- UUID v4를 기본 ID로 사용
- 날짜/시간은 ISO 8601 형식의 문자열로 저장
- 비디오 분석은 CPU/GPU 사용량이 높으므로 서버 리소스 확인 필요
