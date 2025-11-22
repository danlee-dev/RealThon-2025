"""
클라이언트 추상 인터페이스

STT, LLM, TTS 클라이언트의 기본 인터페이스 정의
향후 A6000 서버로 마이그레이션 시 구현체만 교체하면 됨
"""

from abc import ABC, abstractmethod
from typing import Optional


class STTClient(ABC):
    """
    음성 → 텍스트 변환 클라이언트 인터페이스

    구현체:
    - WhisperLocalClient: openai-whisper 로컬 모델 (기본)
    - WhisperA6000Client: A6000 로컬 Whisper (향후 HTTP 연동)
    """

    @abstractmethod
    async def transcribe(
        self,
        audio_path: str,
        language: str = "ko"
    ) -> str:
        """
        음성 파일을 텍스트로 변환

        Args:
            audio_path: .wav 파일 경로
            language: 언어 코드 (ko, en 등)

        Returns:
            변환된 텍스트
        """
        pass


class LLMClient(ABC):
    """
    대형 언어 모델 클라이언트 인터페이스

    구현체:
    - GeminiClient: Google Gemini API (현재)
    - LLaMAA6000Client: A6000 로컬 LLaMA (향후)
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 200,
        temperature: float = 0.7
    ) -> str:
        """
        프롬프트를 받아 텍스트 생성

        Args:
            prompt: 생성 프롬프트
            max_tokens: 최대 토큰 수
            temperature: 생성 온도 (0.0~1.0)

        Returns:
            생성된 텍스트
        """
        pass


class TTSClient(ABC):
    """
    텍스트 → 음성 변환 클라이언트 인터페이스

    구현체:
    - MeloTTSLocalClient: 로컬 CPU Melo TTS (현재)
    - MeloTTSA6000Client: A6000 GPU Melo TTS (향후)
    """

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        speaker: str = "KR",
        speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> str:
        """
        텍스트를 음성으로 변환

        Args:
            text: 음성으로 변환할 텍스트
            speaker: 화자 ID (KR, EN 등)
            speed: 속도 배율 (0.5~2.0)
            output_path: 저장 경로 (None이면 자동 생성)

        Returns:
            생성된 음성 파일 URL
        """
        pass
