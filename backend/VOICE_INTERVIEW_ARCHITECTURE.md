# 음성 면접 시스템 아키텍처

## 개요

STT → LLM → TTS 파이프라인 기반 음성 면접 시스템

**중요**: 🚨 **A6000 서버 마이그레이션 대상**
- 현재: 로컬 Whisper (openai-whisper, CPU) + Melo TTS 로컬 서버
- 향후: A6000 서버의 로컬 모델로 완전 대체

---

## 시스템 구성도

```
┌─────────────┐
│  Frontend   │
│  (React)    │
└─────┬───────┘
      │ WebRTC Audio Recording
      ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend                 │
├─────────────────────────────────────────┤
│  POST /api/session/start                │
│  POST /api/answer/complete              │
└─────┬───────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│    InterviewOrchestrator Service        │
└─────┬───────────────────────────────────┘
      │
      ├──► 🔴 WhisperClient (STT)
      │    └─► 현재: WhisperLocalClient (openai-whisper @ CPU)
      │    └─► 향후: A6000 Whisper Large-v3
      │
      ├──► 🟡 GeminiClient (LLM)
      │    └─► 현재: Google Gemini API
      │    └─► 향후: A6000 LLaMA/Gemma
      │
      └──► 🔴 MeloTTSClient (TTS)
           └─► 현재: 로컬 CPU Melo TTS
           └─► 향후: A6000 GPU Melo TTS / VITS
```

---

## 🚨 A6000 서버 마이그레이션 계획

### Phase 1: MVP (현재)
- **STT**: openai-whisper 로컬 모델 (CPU, 무료)
- **LLM**: Google Gemini API (무료 티어)
- **TTS**: Melo TTS (로컬 CPU)

### Phase 2: A6000 통합 (목표)
- **STT**: Whisper Large-v3 @ A6000 GPU
  - 엔드포인트: `http://a6000-server:8002/stt`
  - 파일 업로드 → JSON 응답
- **LLM**: LLaMA 3.1 or Gemma 2 @ A6000 GPU
  - 엔드포인트: `http://a6000-server:8003/generate`
  - 프롬프트 전송 → 텍스트 응답
- **TTS**: Melo TTS GPU or VITS @ A6000 GPU
  - 엔드포인트: `http://a6000-server:8004/tts`
  - 텍스트 → 음성 파일 URL

### 마이그레이션 체크리스트

- [ ] A6000 서버에 Whisper Large-v3 FastAPI 서버 구축
- [ ] A6000 서버에 LLM 추론 서버 구축 (vLLM or TGI)
- [ ] A6000 서버에 TTS 서버 구축
- [ ] 환경 변수로 엔드포인트 전환 (`USE_A6000_MODELS=true`)
- [ ] Client 인터페이스는 그대로, 구현체만 교체
- [ ] 성능 테스트 (latency, throughput)

---

## 파일 구조

```
backend/
├── VOICE_INTERVIEW_ARCHITECTURE.md  # 이 문서
├── clients/
│   ├── base.py                # 추상 인터페이스 (STTClient, LLMClient, TTSClient)
│   ├── whisper_client.py      # 🔴 A6000 대체 대상
│   ├── gemini_client.py       # 🟡 A6000 대체 대상
│   └── melo_tts_client.py     # 🔴 A6000 대체 대상
├── services/
│   ├── orchestrator.py        # 핵심 로직 (STT→LLM→TTS 파이프라인)
│   ├── audio_processor.py     # ffmpeg 변환 (webm → wav)
│   └── question_generator.py  # LLM 프롬프트 템플릿
├── routers/
│   └── voice_sessions.py      # /api/session/*, /api/answer/*
├── scripts/
│   └── melo_tts_cpu_infer.py  # 로컬 MeloTTS 단일 추론 스크립트
└── utils/
    └── audio_utils.py
```

---

## Client 인터페이스 설계

### 추상 인터페이스 (`clients/base.py`)

```python
from abc import ABC, abstractmethod

class STTClient(ABC):
    """음성 → 텍스트 변환 클라이언트"""
    @abstractmethod
    async def transcribe(self, audio_path: str, language: str = "ko") -> str:
        """
        Args:
            audio_path: .wav 파일 경로
            language: 언어 코드 (ko, en)
        Returns:
            텍스트 변환 결과
        """
        pass

class LLMClient(ABC):
    """대형 언어 모델 클라이언트"""
    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """
        Args:
            prompt: 생성 프롬프트
            max_tokens: 최대 토큰 수
        Returns:
            생성된 텍스트
        """
        pass

class TTSClient(ABC):
    """텍스트 → 음성 변환 클라이언트"""
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        speaker: str = "KR",
        speed: float = 1.0
    ) -> str:
        """
        Args:
            text: 음성으로 변환할 텍스트
            speaker: 화자 ID
            speed: 속도 배율
        Returns:
            생성된 음성 파일 URL
        """
        pass
```

---

## 구현체 예시

### WhisperClient (🔴 A6000 대체 대상)

```python
# clients/whisper_client.py
import asyncio
import aiohttp
import os
from clients.base import STTClient


class WhisperLocalClient(STTClient):
    """openai-whisper 로컬 모델 (CPU/GPU)"""

    def __init__(self, model_size: str = "base", device: str = "cpu"):
        import whisper
        self.model_size = os.getenv("WHISPER_LOCAL_MODEL", model_size)
        self.device = os.getenv("WHISPER_LOCAL_DEVICE", device)
        self._model = whisper.load_model(self.model_size, device=self.device)
        self._use_fp16 = self.device != "cpu"

    async def transcribe(self, audio_path: str, language: str = "ko") -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._model.transcribe(
                audio_path,
                language=language,
                fp16=self._use_fp16
            )["text"].strip()
        )


class WhisperA6000Client(STTClient):
    """A6000 서버의 Whisper Large-v3 HTTP 클라이언트"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def transcribe(self, audio_path: str, language: str = "ko") -> str:
        async with aiohttp.ClientSession() as session:
            with open(audio_path, "rb") as f:
                form = aiohttp.FormData()
                form.add_field("file", f, filename="audio.wav")
                form.add_field("language", language)

                async with session.post(
                    f"{self.base_url}/stt",
                    data=form
                ) as resp:
                    result = await resp.json()
                    return result["text"]
```

### MeloTTSClient (🔴 A6000 대체 대상)

```python
# clients/melo_tts_client.py
import aiohttp
from clients.base import TTSClient

class MeloTTSLocalClient(TTSClient):
    """
    로컬 CPU Melo TTS 클라이언트

    ⚠️ A6000 마이그레이션 시 MeloTTSA6000Client로 교체
    """
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url

    async def synthesize(
        self,
        text: str,
        speaker: str = "KR",
        speed: float = 1.0
    ) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tts",
                json={"text": text, "speaker": speaker, "speed": speed}
            ) as resp:
                result = await resp.json()
                return result["audio_url"]


class MeloTTSA6000Client(TTSClient):
    """
    A6000 서버의 GPU Melo TTS 클라이언트

    ✅ 최종 배포용
    """
    def __init__(self, base_url: str):
        self.base_url = base_url  # http://a6000-server:8004

    async def synthesize(
        self,
        text: str,
        speaker: str = "KR",
        speed: float = 1.0
    ) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tts",
                json={"text": text, "speaker": speaker, "speed": speed}
            ) as resp:
                result = await resp.json()
                return result["audio_url"]
```

---

## 환경 변수 관리

```env
# .env

# ──────────────────────────────────────
# 🔴 Phase 1: MVP (로컬 Whisper)
# ──────────────────────────────────────
WHISPER_LOCAL_MODEL=base
WHISPER_LOCAL_DEVICE=cpu
GEMINI_API_KEY=AIza...
MELO_TTS_BASE_URL=http://localhost:8001

# ──────────────────────────────────────
# ✅ Phase 2: A6000 서버
# ──────────────────────────────────────
USE_A6000_MODELS=false           # true로 변경 시 A6000 클라이언트 사용
A6000_STT_URL=http://a6000-server:8002
A6000_LLM_URL=http://a6000-server:8003
A6000_TTS_URL=http://a6000-server:8004
```

### Client 팩토리 (자동 전환)

```python
# clients/__init__.py
import os
from clients.whisper_client import WhisperLocalClient, WhisperA6000Client
from clients.melo_tts_client import MeloTTSLocalClient, MeloTTSA6000Client


def get_stt_client():
    """환경 변수에 따라 STT 클라이언트 반환"""
    if os.getenv("USE_A6000_MODELS") == "true":
        return WhisperA6000Client(os.getenv("A6000_STT_URL"))
    else:
        return WhisperLocalClient()


def get_tts_client():
    """환경 변수에 따라 TTS 클라이언트 반환"""
    if os.getenv("USE_A6000_MODELS") == "true":
        return MeloTTSA6000Client(os.getenv("A6000_TTS_URL"))
    else:
        return MeloTTSLocalClient(os.getenv("MELO_TTS_BASE_URL"))
```

---

## 로컬 MeloTTS (CPU) 사용법

1. `backend/third_party` 아래에 MeloTTS를 클론한다.
   ```bash
   cd backend
   mkdir -p third_party
   cd third_party
   git clone https://github.com/myshell-ai/MeloTTS.git
   ```
2. MeloTTS 의존성을 설치한다. (backend 전역 venv 재사용 가능)
   ```bash
   cd backend/third_party/MeloTTS
   pip install -r requirements.txt
   pip install -e .
   # macOS에서 에러가 나면 pytorch CPU 빌드를 수동 설치
   ```
3. 한국어 화자가 필요한 경우 모델 체크포인트를 다운로드하고
   `MeloTTS/checkpoints` 폴더에 배치한다. 기본 모델은 최초 추론 시 자동
   다운로드 된다.
4. 단일 추론 테스트는 제공된 스크립트를 사용한다.
    ```bash
    cd backend
    python scripts/melo_tts_cpu_infer.py \
      "안녕하세요! 오늘 면접 준비 잘 되셨나요?" \
      --language KR --speaker KR --speed 1.05 \
      --output tmp/melo_test.wav
    ```
   - `backend/third_party/MeloTTS/melo/pretrained/`에 `G_0.pth` 등을
     다운로드해두면 스크립트가 자동으로 해당 경로를 사용한다. 다른 위치에
     저장했다면 `--ckpt-path` 또는 `MELO_TTS_CKPT_PATH` 환경 변수를 지정한다.
5. HTTP 서버를 띄우려면 MeloTTS 레포 내 `python melo/app.py --device cpu`
   또는 `python melo/server.py --device cpu --host 0.0.0.0 --port 8001`를 실행한
   후, 백엔드 `.env`에서 `MELO_TTS_BASE_URL`을 해당 주소로 지정한다.

---

## API 엔드포인트

### POST /api/session/start

**요청**
```json
{
  "user_id": "u_123",
  "mode": "voice"
}
```

**응답**
```json
{
  "session_id": "s_456",
  "question": {
    "id": "q_main_1",
    "text": "자기소개를 30초 내로 해주세요.",
    "audio_url": "http://localhost:8000/static/audio/q_main_1.wav",
    "type": "main"
  }
}
```

### POST /api/answer/complete

**요청** (multipart/form-data)
- `session_id`: s_456
- `question_id`: q_main_1
- `turn_type`: "main" | "followup"
- `audio_file`: (webm or wav)

**응답**
```json
{
  "answer_text": "저는 백엔드 개발자로...",
  "metrics": {
    "duration_sec": 18.2,
    "wpm": 180,
    "filler_count": 3
  },
  "next_question": {
    "id": "q_follow_1",
    "text": "방금 말씀하신 프로젝트에서 가장 어려웠던 점은?",
    "audio_url": "http://localhost:8000/static/audio/q_follow_1.wav",
    "type": "followup"
  }
}
```

---

## 처리 흐름

```
1. 프론트: 음성 녹음 (webm) → 백엔드 업로드
2. 백엔드:
   ├─ audio_processor: webm → wav 변환
   ├─ WhisperClient: wav → 텍스트 (STT)
   ├─ DB 저장: InterviewVideo, InterviewTranscript
   ├─ QuestionGenerator: 컨텍스트 + 프롬프트 생성
   ├─ GeminiClient: 프롬프트 → 꼬리질문 텍스트 (LLM)
   ├─ MeloTTSClient: 텍스트 → 음성 URL (TTS)
   └─ 응답: {answer_text, next_question}
3. 프론트:
   ├─ answer_text 화면 표시
   └─ next_question.audio_url 재생
```

---

## 성능 고려사항

### 현재 (MVP)
- **STT 지연**: ~2-5초 (Whisper API, 네트워크 왕복)
- **LLM 지연**: ~1-3초 (Gemini API)
- **TTS 지연**: ~3-8초 (Melo TTS CPU)
- **총 지연**: ~6-16초

### A6000 이후
- **STT 지연**: ~0.5-1초 (로컬 GPU)
- **LLM 지연**: ~0.3-0.8초 (로컬 GPU)
- **TTS 지연**: ~0.5-1초 (로컬 GPU)
- **총 지연**: ~1.3-2.8초 🚀

---

## 로컬 Melo TTS 서버 실행

```bash
# backend/scripts/run_melo_tts_server.py
cd backend
CUDA_VISIBLE_DEVICES="" python scripts/run_melo_tts_server.py
```

서버는 `http://localhost:8001`에서 실행됨.

---

## 테스트 시나리오

1. **단위 테스트**: 각 Client 인터페이스
2. **통합 테스트**: Orchestrator 파이프라인
3. **E2E 테스트**: 프론트 → 백엔드 → DB 저장
4. **성능 테스트**: 동시 접속 10명, 지연 시간 측정

---

## 참고 문서

- [Melo TTS GitHub](https://github.com/myshell-ai/MeloTTS)
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [Google Gemini API](https://ai.google.dev/docs)
