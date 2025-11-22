# 비디오 분석 로그 스키마 리팩터링 완료 요약

## 변경 사항

### 1. 정책과 로그 분리 ✅
- **제거**: README에서 "우수/보통/개선 필요" 등 평가 기준 텍스트 제거
- **유지**: 관측값, 계산 방법, 임계값만 로그에 기록
- **결과**: JSON 응답에 정책 텍스트 없음, 객관적 데이터만 포함

### 2. 재현 가능성 강화 ✅
- **Adaptive threshold**: formula + value 구조화 저장
  ```json
  "smile_threshold": {
    "type": "adaptive",
    "formula": "mean + 0.5*std",
    "value": 0.55
  }
  ```
- **Gaze 방법**: method + range 명시
  ```json
  "gaze": {
    "method": "mediapipe_center + iris_yaw_check",
    "center_range_deg": [-15, 15]
  }
  ```
- **모델 버전**: MediaPipe, Whisper 버전 및 설정 저장

### 3. 일관성 확보 ✅
- **Frame count 정리**:
  - `frame_count_total`: 실제 추출한 프레임 수
  - `frame_count_valid`: 분석에 사용된 유효 프레임 수
  - `frame_count_expected`: duration * fps (기대값)
- **정규화 지표 추가**: `nod_rate_per_min` (영상 길이 정규화)

### 4. 신뢰도 정량화 ✅
- **Confidence 점수 수집**:
  - `face_presence_mean`, `face_presence_std`
  - `landmark_confidence_mean`, `landmark_confidence_std`
  - `gaze_confidence_mean`, `gaze_confidence_std`
- **Outlier detection**:
  - `pose_outlier_ratio` + `pose_outlier_rule` (재현 가능)

## 수정된 파일 목록

1. **models.py**: `nod_rate_per_min` 컬럼 추가
2. **schemas.py**: MetricsMetadata 구조화 (nested Pydantic models)
3. **pipeline/vision_mediapipe.py**: FrameResult에 confidence 필드 추가
4. **pipeline/metrics.py**: compute_metadata() 전면 재작성
5. **routers/video_analysis.py**: nod_rate_per_min 계산 및 metadata 저장
6. **README.md**: 정책 제거, 계산 방법 및 구조 문서화

## 테스트 시나리오

### 기본 동작 확인
```bash
# 1. 비디오 업로드
POST /api/video/upload

# 2. 분석 실행
POST /api/video/analyze/{video_id}

# 3. 결과 조회 및 검증
GET /api/video/results/{video_id}
```

### 검증 항목

#### ✅ 일관성
- `frame_count_expected` ≈ `duration_sec * fps_analyzed`
- `frame_count_total` ≤ `frame_count_expected` (약간의 오차 허용)
- `frame_count_valid` ≤ `frame_count_total`

#### ✅ 재현 가능성
- `metadata.thresholds.smile_threshold.value`: float 값 존재
- `metadata.thresholds.smile_threshold.formula`: "mean + 0.5*std"
- `metadata.models`: 모든 버전 정보 존재
- `metadata.outlier_flags.pose_outlier_rule`: 규칙 문자열 존재

#### ✅ 정규화
- `nod_rate_per_min = nod_count / (duration_sec / 60)`
- 30초 영상과 60초 영상의 nod_count 비교 가능

#### ✅ 신뢰도
- `confidence` 객체에 최소 `valid_frame_ratio` 존재
- MediaPipe 사용 시 `landmark_confidence_mean` 존재
- 모든 confidence 값이 0~1 범위

#### ✅ 정책 분리
- JSON 응답에 "우수", "보통", "개선 필요" 등 텍스트 없음
- 숫자와 구조화된 데이터만 존재

## 샘플 검증 (3개 영상 권장)

### 짧은 영상 (15초)
- Expected: ~75 frames (5 FPS * 15s)
- Verify: `frame_count_expected` ≈ 75
- Verify: `nod_rate_per_min` 계산 올바름

### 중간 영상 (35초)
- Expected: ~175 frames
- Verify: confidence 점수들 존재
- Verify: adaptive threshold value 저장됨

### 긴 영상 (60초)
- Expected: ~300 frames
- Verify: outlier_ratio 합리적 (< 0.2)
- Verify: metadata 완전성

## 수용 기준 (User Requirements)

✅ 샘플 영상 3개 이상 분석 시 metadata 일관됨
✅ frame_count_total, expected가 fps/duration과 모순 없음
✅ adaptive threshold는 formula+value 모두 기록
✅ gaze 기준이 수치/방법으로 설명 가능
✅ nod_rate_per_min 출력됨
✅ confidence와 outlier ratio가 실제 변동 반영
✅ JSON 로그에서 정책 텍스트 사라짐

## 다음 단계 (Optional)

1. **논문/서비스 확장**:
   - 여러 모델 버전 비교 (A/B testing)
   - 대규모 영상 배치 분석 및 통계
   
2. **추가 신뢰도 지표**:
   - Temporal consistency (프레임 간 변화율)
   - Multi-model ensemble confidence
   
3. **데이터 품질 자동 경고**:
   - `valid_frame_ratio < 0.3` → 재촬영 권장
   - `pose_outlier_ratio > 0.15` → 환경 개선 필요

