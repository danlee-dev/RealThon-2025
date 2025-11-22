# 비디오 분석 API 사용 가이드

## 🎯 완성된 기능

### ✅ 1. Emotion Distribution & Timeline
- **Blendshapes 기반 감정 인식** 구현 완료
- Timeline에 `emotion` 필드 추가
- `emotion_distribution`: {"happy": 0.45, "pleasant": 0.35, ...}
- `primary_emotion`: "happy", "pleasant", "neutral", etc.

### ✅ 2. DB 연동
- 모든 분석 결과가 자동으로 DB에 저장됨
- `InterviewVideo` - 비디오 메타데이터
- `NonverbalMetrics` - 시선, 미소, 끄덕임, WPM 등
- `NonverbalTimeline` - 전체 타임라인 JSON
- `InterviewTranscript` - STT 결과
- `Feedback` - AI 생성 피드백 (각 항목별)

### ✅ 3. 비디오 업로드
- 멀티파트 파일 업로드 지원
- .mp4, .webm, .mov, .avi 형식 지원
- 자동 파일명 생성 및 저장

### ✅ 4. AI 피드백 (Gemini 2.5 Flash Lite)
- 환경 변수로 설정
- Gemini API 실패시 자동 fallback

---

## 🚀 API 사용 흐름

### 1단계: 비디오 업로드

```bash
curl -X POST "http://localhost:8000/api/video/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@interview.mp4" \
  -F "user_id=user123" \
  -F "session_id=session456" \
  -F "question_id=question789"
```

**응답:**
```json
{
  "video_id": "abc-def-ghi-123",
  "filename": "user123_session456_20251122_143025.mp4",
  "file_path": "/path/to/uploads/videos/...",
  "duration_sec": 45.3,
  "created_at": "2025-11-22T14:30:25.123456"
}
```

### 2단계: 비디오 분석 실행

```bash
curl -X POST "http://localhost:8000/api/video/analyze/abc-def-ghi-123"
```

**처리 과정:**
1. 🎬 비디오 분해 (5 FPS 프레임 추출)
2. 👁️ 얼굴 분석 (MediaPipe + Blendshapes)
3. 🎤 오디오 추출 및 STT (Whisper)
4. 📊 메트릭 계산
5. 🤖 AI 피드백 생성 (Gemini 2.5 Flash Lite)
6. 💾 DB 저장

**응답:**
```json
{
  "video_id": "abc-def-ghi-123",
  "metrics": {
    "center_gaze_ratio": 0.65,
    "smile_ratio": 0.42,
    "nod_count": 2,
    "emotion_distribution": {
      "happy": 0.45,
      "pleasant": 0.35,
      "neutral": 0.20
    },
    "primary_emotion": "happy",
    "wpm": 165.0,
    "filler_count": 3
  },
  "feedback": [
    "카메라 응시가 안정적입니다. 정면을 65% 가량 바라보고 있어 신뢰감을 줍니다.",
    "전반적으로 밝고 긍정적인 표정(45%)이 우세합니다. 매우 좋은 인상을 만들고 있습니다.",
    "말 속도는 분당 165단어로 적절합니다. 청자가 이해하기 편한 템포입니다.",
    "필러 사용이 3회로 매우 적습니다. 유창한 답변입니다."
  ],
  "feedback_mode": "gemini",
  "transcript": "안녕하세요. 저는 컴퓨터 공학을 전공한...",
  "database_records": {
    "transcript_id": "transcript-id-123",
    "metrics_id": "metrics-id-456",
    "timeline_id": "timeline-id-789",
    "feedback_ids": ["fb1", "fb2", "fb3", "fb4"]
  }
}
```

### 3단계: 결과 조회

```bash
curl "http://localhost:8000/api/video/results/abc-def-ghi-123"
```

**응답:**
```json
{
  "video": {
    "id": "abc-def-ghi-123",
    "user_id": "user123",
    "session_id": "session456",
    "question_id": "question789",
    "duration_sec": 45.3,
    "created_at": "2025-11-22T14:30:25"
  },
  "metrics": {
    "center_gaze_ratio": 0.65,
    "smile_ratio": 0.42,
    "nod_count": 2,
    "wpm": 165.0,
    "filler_count": 3,
    "primary_emotion": "happy"
  },
  "feedbacks": [
    {
      "id": "fb1",
      "title": "강점 #1",
      "message": "카메라 응시가 안정적입니다...",
      "severity": "info",
      "level": "video"
    },
    ...
  ],
  "transcript": "안녕하세요. 저는...",
  "timeline_available": true
}
```

---

## 🔧 환경 설정

### `.env` 파일

```bash
# Gemini API Key (필수: AI 피드백용)
GEMINI_API_KEY=your_gemini_api_key_here

# Database (자동 생성됨)
# DATABASE_URL=sqlite:///./interview_app.db
```

### Gemini API Key 발급

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. API Key 생성
3. `.env` 파일에 추가

---

## 📊 DB 스키마

### InterviewVideo (메인)
- `id`, `user_id`, `session_id`, `question_id`
- `video_url`, `audio_url`, `duration_sec`
- `created_at`

### NonverbalMetrics (분석 결과)
- `video_id` (FK)
- `center_gaze_ratio`, `smile_ratio`, `nod_count`
- `wpm`, `filler_count`, `primary_emotion`

### NonverbalTimeline (상세 타임라인)
- `video_id` (FK)
- `timeline_json` - 전체 프레임별 데이터

### InterviewTranscript (음성 전사)
- `video_id` (FK)
- `text`, `language`

### Feedback (AI 피드백)
- `video_id` (FK)
- `title`, `message`, `severity` (info/warning/suggestion)
- `level` (video/segment)

---

## 🎨 프론트엔드 연동 예시

```typescript
// 1. 비디오 업로드
const uploadVideo = async (file: File, userId: string, sessionId: string, questionId: string) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user_id', userId);
  formData.append('session_id', sessionId);
  formData.append('question_id', questionId);
  
  const response = await fetch('/api/video/upload', {
    method: 'POST',
    body: formData
  });
  
  return response.json(); // { video_id: "...", ... }
};

// 2. 분석 실행 (로딩 표시)
const analyzeVideo = async (videoId: string) => {
  const response = await fetch(`/api/video/analyze/${videoId}`, {
    method: 'POST'
  });
  
  return response.json(); // { metrics, feedback, ... }
};

// 3. 결과 표시
const displayResults = (data: any) => {
  // Progress bars
  <ProgressBar label="카메라 응시" value={data.metrics.center_gaze_ratio} />
  <ProgressBar label="미소 비율" value={data.metrics.smile_ratio} />
  
  // Emotion pie chart
  <PieChart data={data.metrics.emotion_distribution} />
  
  // Feedback cards
  data.feedback.map(fb => <FeedbackCard message={fb} />)
  
  // Transcript
  <Transcript text={data.transcript} />
};
```

---

## 🐛 트러블슈팅

### 1. Gemini API 없을 때
```
⚠️ Gemini API 호출 실패
Falling back to rule-based feedback
```
→ 정상입니다! 규칙 기반 피드백으로 작동합니다.

### 2. Blendshapes 모델 없을 때
```
⚠️ Failed to load blendshapes model
Falling back to legacy FaceMesh
```
→ 감정 인식은 안 되지만 나머지는 정상 작동합니다.

### 3. DB 초기화
```bash
# DB 초기화 (주의: 모든 데이터 삭제됨)
rm interview_app.db
python init_db.py
```

---

## ✨ 완성된 체크리스트

- [x] Emotion distribution 구현 (Blendshapes 기반)
- [x] Timeline에 emotion 필드 추가
- [x] DB 연동 완료 (6개 테이블)
- [x] 비디오 업로드 엔드포인트
- [x] AI 피드백 생성 (Gemini 2.5 Flash Lite)
- [x] 자동 fallback 시스템
- [x] 결과 조회 API

---

## 📝 다음 단계

1. ⬜ 프론트엔드 UI 구현
2. ⬜ 실시간 진행 상태 표시 (WebSocket)
3. ⬜ 비디오 스트리밍 재생
4. ⬜ Timeline 시각화 (시간축 차트)
5. ⬜ 여러 비디오 비교 분석

