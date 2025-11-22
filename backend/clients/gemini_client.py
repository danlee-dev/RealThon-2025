"""
Gemini LLM 클라이언트

🟡 A6000 마이그레이션 대상
- 현재: Google Gemini API (무료 티어)
- 향후: A6000 서버의 LLaMA/Gemma (무료, 로컬)
"""

import os
import json
from typing import Optional
import google.generativeai as genai
from clients.base import LLMClient


class GeminiClient(LLMClient):
    """
    Google Gemini API 클라이언트 (꼬리질문 생성용)

    ⚠️ A6000 서버로 마이그레이션 시 LLaMAA6000Client로 교체

    환경 변수:
        GEMINI_API_KEY: Google Gemini API 키
        GEMINI_MODEL: 모델 이름 (기본: gemini-2.0-flash-exp)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")

        genai.configure(api_key=self.api_key)

        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.model = genai.GenerativeModel(self.model_name)

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
            temperature: 생성 온도

        Returns:
            생성된 텍스트
        """
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature
        )

        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )

        return response.text.strip()

    def build_followup_prompt(
        self,
        portfolio_text: str,
        current_question: str,
        user_answer: str,
        question_type: str = "technical"
    ) -> str:
        """
        꼬리질문 생성을 위한 프롬프트 구성

        Args:
            portfolio_text: 포트폴리오 파싱 텍스트
            current_question: 현재 질문
            user_answer: 사용자 답변 (STT 결과)
            question_type: 질문 유형 (technical, behavioral, project)

        Returns:
            꼬리질문 생성 프롬프트
        """
        prompt = f"""당신은 경험 많은 개발자 면접관입니다.
지원자의 포트폴리오와 답변을 기반으로 깊이 있는 꼬리질문 1개를 생성해주세요.

# 포트폴리오 정보
{portfolio_text[:1000]}  # 너무 길면 잘라냄

# 현재 질문
{current_question}

# 지원자 답변
{user_answer}

# 요구사항
1. 지원자의 답변에서 **구체적인 경험**을 더 파고들어야 합니다
2. 포트폴리오에 언급된 기술 스택과 연관지어 질문하세요
3. 단답형이 아닌, 경험과 생각을 이끌어낼 수 있는 질문이어야 합니다
4. 질문은 **1문장**으로 간결하게 작성하세요
5. 존댓말을 사용하세요 (예: "~하셨나요?", "~하신 경험이 있나요?")

# 출력 형식
꼬리질문만 출력하세요. 추가 설명이나 마크다운 없이 질문 1개만 작성하세요.

예시:
- "방금 말씀하신 마이크로서비스 아키텍처에서 서비스 간 통신은 어떻게 구현하셨나요?"
- "포트폴리오에 있는 Docker를 실제 프로젝트에서 어떻게 활용하셨나요?"
"""
        return prompt


class LLaMAA6000Client(LLMClient):
    """
    A6000 서버의 LLaMA/Gemma 클라이언트

    ✅ 최종 배포용

    환경 변수:
        A6000_LLM_URL: A6000 LLM 서버 URL (예: http://a6000-server:8003)
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("A6000_LLM_URL")
        if not self.base_url:
            raise ValueError("A6000_LLM_URL is required")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 200,
        temperature: float = 0.7
    ) -> str:
        """
        A6000 서버의 LLM으로 텍스트 생성

        Args:
            prompt: 생성 프롬프트
            max_tokens: 최대 토큰 수
            temperature: 생성 온도

        Returns:
            생성된 텍스트
        """
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/generate",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            ) as resp:
                resp.raise_for_status()
                result = await resp.json()
                return result.get("text", "")

    def build_followup_prompt(
        self,
        portfolio_text: str,
        current_question: str,
        user_answer: str,
        question_type: str = "technical"
    ) -> str:
        """GeminiClient와 동일한 프롬프트 빌더"""
        # GeminiClient와 동일한 로직
        prompt = f"""당신은 경험 많은 개발자 면접관입니다.
지원자의 포트폴리오와 답변을 기반으로 깊이 있는 꼬리질문 1개를 생성해주세요.

# 포트폴리오 정보
{portfolio_text[:1000]}

# 현재 질문
{current_question}

# 지원자 답변
{user_answer}

# 요구사항
1. 지원자의 답변에서 **구체적인 경험**을 더 파고들어야 합니다
2. 포트폴리오에 언급된 기술 스택과 연관지어 질문하세요
3. 단답형이 아닌, 경험과 생각을 이끌어낼 수 있는 질문이어야 합니다
4. 질문은 **1문장**으로 간결하게 작성하세요
5. 존댓말을 사용하세요

# 출력
꼬리질문만 출력하세요.
"""
        return prompt
