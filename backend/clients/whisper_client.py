"""
Whisper STT 클라이언트

현재 단계:
- WhisperLocalClient: openai-whisper 로컬 모델 (CPU/GPU)
- WhisperA6000Client: 향후 A6000 서버 연동용 HTTP 클라이언트
"""

import asyncio
import os
from typing import Optional

import aiohttp

from clients.base import STTClient


class WhisperLocalClient(STTClient):
    """
    로컬 openai-whisper 모델을 사용하는 클라이언트

    환경 변수:
        WHISPER_LOCAL_MODEL: tiny/base/small/medium/large (기본: base)
        WHISPER_LOCAL_DEVICE: "cpu" or "cuda" (기본: cpu)
    """

    def __init__(
        self,
        model_size: Optional[str] = None,
        device: Optional[str] = None
    ):
        self.model_size = model_size or os.getenv("WHISPER_LOCAL_MODEL", "base")
        self.device = device or os.getenv("WHISPER_LOCAL_DEVICE", "cpu")

        try:
            import whisper  # type: ignore
        except ImportError as exc:  # pragma: no cover - 환경 의존
            raise RuntimeError(
                "openai-whisper 패키지가 필요합니다. requirements.txt를 설치했는지 확인하세요."
            ) from exc

        # 모델은 한 번만 로드해서 재사용 (CPU에서도 비용 큼)
        self._whisper = whisper.load_model(self.model_size, device=self.device)
        self._use_fp16 = self.device.lower() != "cpu"

    async def transcribe(
        self,
        audio_path: str,
        language: str = "ko"
    ) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self._transcribe_sync,
            audio_path,
            language
        )

    def _transcribe_sync(self, audio_path: str, language: str) -> str:
        result = self._whisper.transcribe(
            audio_path,
            language=language,
            fp16=self._use_fp16
        )
        return result.get("text", "").strip()


class WhisperA6000Client(STTClient):
    """
    A6000 서버의 Whisper Large-v3 클라이언트

    ✅ 최종 배포용

    환경 변수:
        A6000_STT_URL: A6000 STT 서버 URL (예: http://a6000-server:8002)
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("A6000_STT_URL")
        if not self.base_url:
            raise ValueError("A6000_STT_URL is required")

    async def transcribe(
        self,
        audio_path: str,
        language: str = "ko"
    ) -> str:
        """
        A6000 서버의 Whisper로 음성 파일을 텍스트로 변환

        Args:
            audio_path: .wav 파일 경로
            language: 언어 코드

        Returns:
            변환된 텍스트
        """
        async with aiohttp.ClientSession() as session:
            with open(audio_path, "rb") as audio_file:
                form = aiohttp.FormData()
                form.add_field(
                    "file",
                    audio_file,
                    filename=os.path.basename(audio_path),
                    content_type="audio/wav"
                )
                form.add_field("language", language)

                async with session.post(
                    f"{self.base_url}/stt",
                    data=form
                ) as resp:
                    resp.raise_for_status()
                    result = await resp.json()
                    return result.get("text", "")
