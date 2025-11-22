"""
Melo TTS 클라이언트

🔴 A6000 마이그레이션 대상
- 현재: 로컬 CPU Melo TTS
- 향후: A6000 서버의 GPU Melo TTS/VITS
"""

import os
import uuid
import aiohttp
from typing import Optional
from clients.base import TTSClient


class MeloTTSLocalClient(TTSClient):
    """
    로컬 CPU Melo TTS 클라이언트

    ⚠️ A6000 서버로 마이그레이션 시 MeloTTSA6000Client로 교체

    환경 변수:
        MELO_TTS_BASE_URL: Melo TTS 서버 URL (기본: http://localhost:8001)
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv(
            "MELO_TTS_BASE_URL",
            "http://localhost:8001"
        )

    async def synthesize(
        self,
        text: str,
        speaker: str = "KR",
        speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> str:
        """
        텍스트를 음성으로 변환 (로컬 Melo TTS 서버 호출)

        Args:
            text: 음성으로 변환할 텍스트
            speaker: 화자 ID (KR, EN 등)
            speed: 속도 배율
            output_path: 저장 경로 (사용 안 함, 서버가 자동 생성)

        Returns:
            생성된 음성 파일 URL
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tts",
                json={
                    "text": text,
                    "speaker": speaker,
                    "speed": speed
                }
            ) as resp:
                resp.raise_for_status()
                result = await resp.json()
                return result.get("audio_url", "")


class MeloTTSA6000Client(TTSClient):
    """
    A6000 서버의 GPU Melo TTS 클라이언트

    ✅ 최종 배포용

    환경 변수:
        A6000_TTS_URL: A6000 TTS 서버 URL (예: http://a6000-server:8004)
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("A6000_TTS_URL")
        if not self.base_url:
            raise ValueError("A6000_TTS_URL is required")

    async def synthesize(
        self,
        text: str,
        speaker: str = "KR",
        speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> str:
        """
        텍스트를 음성으로 변환 (A6000 서버 호출)

        Args:
            text: 음성으로 변환할 텍스트
            speaker: 화자 ID
            speed: 속도 배율
            output_path: 저장 경로 (사용 안 함)

        Returns:
            생성된 음성 파일 URL
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tts",
                json={
                    "text": text,
                    "speaker": speaker,
                    "speed": speed
                }
            ) as resp:
                resp.raise_for_status()
                result = await resp.json()
                return result.get("audio_url", "")
