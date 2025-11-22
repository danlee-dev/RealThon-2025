"""
질문 생성 및 관리 서비스

메인 질문 관리 및 꼬리질문 프롬프트 생성
"""

from typing import List, Dict, Any


class QuestionGenerator:
    """
    면접 질문 생성 및 관리

    메인 질문은 미리 정의된 리스트 사용
    꼬리질문은 LLM으로 동적 생성
    """

    # 기본 메인 질문 리스트
    DEFAULT_MAIN_QUESTIONS = [
        {
            "id": "main_1",
            "text": "간단히 자기소개를 30초 내로 해주세요.",
            "type": "intro",
            "order": 1
        },
        {
            "id": "main_2",
            "text": "포트폴리오에서 가장 자신있는 프로젝트에 대해 설명해주세요.",
            "type": "portfolio",
            "order": 2
        },
        {
            "id": "main_3",
            "text": "해당 프로젝트에서 사용한 기술 스택과 그 이유를 설명해주세요.",
            "type": "technical",
            "order": 3
        },
        {
            "id": "main_4",
            "text": "팀 프로젝트에서 겪었던 어려움과 해결 방법을 말씀해주세요.",
            "type": "behavioral",
            "order": 4
        },
        {
            "id": "main_5",
            "text": "앞으로의 커리어 목표와 학습 계획에 대해 말씀해주세요.",
            "type": "career",
            "order": 5
        }
    ]

    def __init__(self, custom_questions: List[Dict[str, Any]] = None):
        """
        Args:
            custom_questions: 커스텀 질문 리스트 (없으면 기본 질문 사용)
        """
        self.main_questions = custom_questions or self.DEFAULT_MAIN_QUESTIONS

    def get_main_question(self, index: int = 0) -> Dict[str, Any]:
        """
        인덱스로 메인 질문 가져오기

        Args:
            index: 질문 인덱스 (0부터 시작)

        Returns:
            질문 딕셔너리
        """
        if 0 <= index < len(self.main_questions):
            return self.main_questions[index]
        else:
            # 마지막 질문 (종료)
            return {
                "id": "main_end",
                "text": "면접이 종료되었습니다. 수고하셨습니다.",
                "type": "end",
                "order": 999
            }

    def get_total_main_questions(self) -> int:
        """메인 질문 총 개수"""
        return len(self.main_questions)

    def has_more_questions(self, current_index: int) -> bool:
        """
        다음 메인 질문이 있는지 확인

        Args:
            current_index: 현재 질문 인덱스

        Returns:
            다음 질문 존재 여부
        """
        return current_index < len(self.main_questions) - 1
