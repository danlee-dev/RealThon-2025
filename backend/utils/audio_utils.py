"""
오디오 처리 유틸리티

ffmpeg를 사용한 오디오 변환 (webm → wav)
"""

import os
import uuid
import subprocess
from pathlib import Path
from typing import Optional


def convert_to_wav(
    input_path: str,
    output_path: Optional[str] = None,
    sample_rate: int = 16000,
    channels: int = 1
) -> str:
    """
    오디오 파일을 WAV 형식으로 변환 (ffmpeg 사용)

    Args:
        input_path: 입력 파일 경로 (webm, mp3, m4a 등)
        output_path: 출력 파일 경로 (None이면 자동 생성)
        sample_rate: 샘플링 레이트 (기본: 16kHz, Whisper 권장)
        channels: 채널 수 (1=모노, 2=스테레오)

    Returns:
        변환된 WAV 파일 경로

    Raises:
        FileNotFoundError: 입력 파일이 없을 때
        RuntimeError: ffmpeg 변환 실패
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # 출력 경로 자동 생성
    if output_path is None:
        upload_dir = Path("uploads/audio")
        upload_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(upload_dir / f"{uuid.uuid4()}.wav")

    # ffmpeg 명령어
    command = [
        "ffmpeg",
        "-i", input_path,
        "-ar", str(sample_rate),  # 샘플링 레이트
        "-ac", str(channels),     # 채널 수
        "-y",                     # 덮어쓰기
        output_path
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"ffmpeg conversion failed: {e.stderr}"
        )


def get_audio_duration(audio_path: str) -> float:
    """
    오디오 파일의 길이를 초 단위로 반환 (ffprobe 사용)

    Args:
        audio_path: 오디오 파일 경로

    Returns:
        오디오 길이 (초)

    Raises:
        RuntimeError: ffprobe 실패
    """
    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError) as e:
        raise RuntimeError(f"ffprobe failed: {e}")


async def save_upload_file(upload_file, destination: str) -> str:
    """
    FastAPI UploadFile을 디스크에 저장

    Args:
        upload_file: FastAPI UploadFile 객체
        destination: 저장 경로

    Returns:
        저장된 파일 경로
    """
    # 디렉토리 생성
    Path(destination).parent.mkdir(parents=True, exist_ok=True)

    # 파일 저장
    with open(destination, "wb") as f:
        content = await upload_file.read()
        f.write(content)

    return destination
