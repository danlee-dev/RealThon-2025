"""
클라이언트 팩토리

환경 변수에 따라 적절한 클라이언트 구현체를 반환
USE_A6000_MODELS=true 시 A6000 클라이언트로 자동 전환
"""

import os
from clients.base import STTClient, LLMClient, TTSClient
from clients.whisper_client import WhisperLocalClient, WhisperA6000Client
from clients.gemini_client import GeminiClient, LLaMAA6000Client
from clients.melo_tts_client import MeloTTSLocalClient, MeloTTSA6000Client


def get_stt_client() -> STTClient:
    """
    환경 변수에 따라 STT 클라이언트 반환

    환경 변수:
        USE_A6000_MODELS: "true"이면 A6000 클라이언트 사용

    Returns:
        STTClient 구현체
    """
    use_a6000 = os.getenv("USE_A6000_MODELS", "false").lower() == "true"

    if use_a6000:
        return WhisperA6000Client()
    else:
        return WhisperLocalClient()


def get_llm_client() -> LLMClient:
    """
    환경 변수에 따라 LLM 클라이언트 반환

    환경 변수:
        USE_A6000_MODELS: "true"이면 A6000 클라이언트 사용

    Returns:
        LLMClient 구현체
    """
    use_a6000 = os.getenv("USE_A6000_MODELS", "false").lower() == "true"

    if use_a6000:
        return LLaMAA6000Client()
    else:
        return GeminiClient()


def get_tts_client() -> TTSClient:
    """
    환경 변수에 따라 TTS 클라이언트 반환

    환경 변수:
        USE_A6000_MODELS: "true"이면 A6000 클라이언트 사용

    Returns:
        TTSClient 구현체
    """
    use_a6000 = os.getenv("USE_A6000_MODELS", "false").lower() == "true"

    if use_a6000:
        return MeloTTSA6000Client()
    else:
        return MeloTTSLocalClient()


__all__ = [
    "get_stt_client",
    "get_llm_client",
    "get_tts_client",
    "STTClient",
    "LLMClient",
    "TTSClient"
]
