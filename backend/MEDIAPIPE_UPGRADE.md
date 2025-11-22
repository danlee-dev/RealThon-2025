# MediaPipe Blendshapes 업그레이드 가이드

## 📊 개선 사항

reference 코드(`main_medipipe_reference.py`)를 참고하여 MediaPipe 로직을 개선했습니다.

### ✅ 주요 변경사항

1. **Blendshapes 지원 추가** 🎭
   - 52개의 얼굴 표정 파라미터를 사용한 정밀한 감정 분석
   - `mouthSmileLeft/Right`, `eyeWide`, `browInnerUp` 등

2. **감정 인식 개선** 😊
   - 기존: 감정 인식 없음
   - 개선: blendshapes 기반 감정 분류 (happy, pleasant, neutral, surprised, concerned)

3. **Dual-mode 지원** 🔄
   - Blendshapes 모델 있으면 → 고급 분석
   - 없으면 → 기존 FaceMesh로 자동 fallback

4. **더 정확한 미소 감지** 😄
   - 기존: 입 너비 기하학적 계산
   - 개선: `mouthSmileLeft/Right` blendshapes 사용

---

## 🚀 사용 방법

### 1. Blendshapes 모델 다운로드 (선택사항)

MediaPipe의 공식 Face Landmarker v2 모델을 다운로드합니다:

```bash
# 다운로드 경로
mkdir -p MediaPipe
cd MediaPipe

# MediaPipe 공식 모델 다운로드
wget https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task -O face_landmarker_v2_with_blendshapes.task
```

또는 다음 경로 중 하나에 모델 파일을 배치:
- `MediaPipe/face_landmarker_v2_with_blendshapes.task`
- `./MediaPipe/face_landmarker_v2_with_blendshapes.task`
- `models/face_landmarker_v2_with_blendshapes.task`

### 2. API 사용

```bash
# 비디오 분석 실행
curl -X POST http://localhost:8000/api/video/analyze
```

### 3. 응답 예시

**Blendshapes 모델 사용시:**

```json
{
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
  "filler_count": 3,
  "feedback": [
    "카메라 응시 비율이 65%로 대체로 양호하다. 핵심 답변 구간에서 조금 더 유지하면 좋다.",
    "미소/긍정 표정 비율이 42%로 자연스럽다. 친근한 인상을 준다.",
    "끄덕임이 과하지 않고 적절하다. 경청하는 인상을 준다.",
    "전체적으로 밝고 긍정적 표정(45%)이 우세하다. 매우 긍정적인 인상을 준다.",
    "말 속도(WPM 165)가 안정적이다. 듣기 편한 템포다.",
    "필러 사용(3회)이 과도하지 않다. 전반적으로 유창하다."
  ]
}
```

**Blendshapes 모델 없을 때 (자동 fallback):**

```json
{
  "center_gaze_ratio": 0.65,
  "smile_ratio": 0.38,
  "nod_count": 2,
  "emotion_distribution": {},
  "primary_emotion": null,
  "wpm": 165.0,
  "filler_count": 3,
  "feedback": [
    "카메라 응시 비율이 65%로 대체로 양호하다...",
    "미소/긍정 표정 비율이 38%로 자연스럽다..."
  ]
}
```

---

## 🔧 기술 상세

### FrameResult 구조 변경

```python
@dataclass
class FrameResult:
    t: float
    valid: bool
    gaze: Optional[str]
    smile: Optional[float]
    yaw: Optional[float]
    pitch: Optional[float]
    roll: Optional[float]
    emotion: Optional[str]          # ✨ NEW
    blendshapes: Optional[Dict]      # ✨ NEW
```

### Blendshapes 기반 감정 분류

```python
def _detect_emotion_from_blendshapes(blendshapes):
    smile = (mouthSmileLeft + mouthSmileRight) / 2
    eye_wide = (eyeWideLeft + eyeWideRight) / 2
    brow_up = max(browInnerUp, browOuterUpLeft, browOuterUpRight)
    frown = (mouthFrownLeft + mouthFrownRight) / 2
    
    if smile > 0.3:          return "happy"
    elif eye_wide > 0.5:     return "surprised"
    elif frown > 0.3:        return "concerned"
    elif smile > 0.1:        return "pleasant"
    else:                    return "neutral"
```

### 새로운 Metrics

```python
# 감정 분포 계산
emotion_distribution(timeline) -> {"happy": 0.45, "neutral": 0.30, ...}

# 주요 감정 추출
get_primary_emotion(timeline) -> "happy"
```

---

## 📈 성능 비교

| 기능 | 기존 (FaceMesh) | 개선 (Blendshapes) |
|-----|----------------|-------------------|
| 랜드마크 | 478개 | 478개 |
| 미소 감지 | 기하학 계산 | Blendshapes 파라미터 |
| 감정 인식 | ❌ | ✅ (5가지) |
| 처리 속도 | 빠름 | 약간 느림 |
| 정확도 | 보통 | 높음 |
| 모델 필요 | ❌ | ✅ (선택) |

---

## 🐛 트러블슈팅

### 모델을 찾을 수 없음

```
⚠️ Failed to load blendshapes model
Falling back to legacy FaceMesh
```

→ 정상입니다! 모델 없이도 기존 방식으로 작동합니다.

### 감정 분포가 비어있음

```json
"emotion_distribution": {},
"primary_emotion": null
```

→ Blendshapes 모델이 없어서 감정 분석을 건너뛴 것입니다.

---

## 📝 다음 단계

1. ✅ Blendshapes 기반 분석 구현
2. ⬜ 비디오 업로드 엔드포인트 추가
3. ⬜ DB 연동 (NonverbalMetrics, NonverbalTimeline 저장)
4. ⬜ 실시간 분석 (WebSocket)
5. ⬜ 프론트엔드 차트 렌더링

---

## 🔗 참고 자료

- [MediaPipe Face Landmarker](https://developers.google.com/mediapipe/solutions/vision/face_landmarker)
- [Blendshapes 문서](https://github.com/google/mediapipe/blob/master/docs/solutions/face_mesh.md)
- Reference: `main_medipipe_reference.py`

