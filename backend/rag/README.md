# RAG (Retrieval-Augmented Generation) Directory

이 디렉토리는 개발자 역량 분석 및 AI 면접 시스템을 위한 RAG 기반 시스템을 구성합니다.

## 디렉토리 구조

```
rag/
├── data/                    # 원본 데이터 저장
│   ├── frontend/           # FE 개발자 포트폴리오 및 역량 데이터
│   │   ├── portfolios/     # FE 개발자 포트폴리오 샘플
│   │   ├── skills/         # FE 필수 스킬 및 역량 정의
│   │   └── job_posts/      # FE 개발자 채용 공고 데이터
│   ├── backend/            # BE 개발자 포트폴리오 및 역량 데이터
│   │   ├── portfolios/     # BE 개발자 포트폴리오 샘플
│   │   ├── skills/         # BE 필수 스킬 및 역량 정의
│   │   └── job_posts/      # BE 개발자 채용 공고 데이터
│   └── reference/          # 역량 매트릭스 및 평가 기준 레퍼런스
│       ├── competency_matrix.json      # 연차/직무별 역량 매트릭스
│       ├── interview_questions.json    # 역량별 면접 질문 뱅크
│       ├── portfolio_checklist.json    # 포트폴리오 평가 체크리스트
│       ├── scenario_templates.json     # 면접 시나리오 템플릿
│       ├── evaluation_rubric.json      # 답변 평가 루브릭
│       └── README.md                   # 레퍼런스 사용 가이드
│
├── embeddings/             # 임베딩된 벡터 데이터
│   ├── frontend/
│   └── backend/
│
├── vectorstore/            # Vector DB (Chroma/FAISS 등)
│   ├── frontend/
│   └── backend/
│
└── utils/                  # RAG 유틸리티 함수
    ├── __init__.py
    ├── embedding.py        # 임베딩 생성 로직
    ├── retriever.py        # 문서 검색 로직
    └── analyzer.py         # 역량 비교 및 분석 로직
```

## 핵심 기능

### 1. 역량 분석 시스템
- **포트폴리오 자동 분석**: 사용자가 업로드한 포트폴리오에서 보유 역량 파악
- **역량 매트릭스 매칭**: 연차(Junior/Mid/Senior)와 직무(FE/BE)별 필수/우대 역량과 비교
- **GAP 분석**: 부족한 역량 식별 및 개선 방안 제시
- **강점 발견**: 차별화된 역량 및 경쟁력 포인트 도출

### 2. AI 면접 시스템
- **맞춤형 질문 생성**: 부족한 역량 위주로 면접 질문 자동 선택
- **면접 시나리오 생성**: 개인화된 면접 대본 자동 구성
- **비언어적 표현 분석**: 얼굴 표정, 시선, 제스처 실시간 평가
- **답변 평가**: 구조화된 루브릭 기반 객관적 평가

## 데이터 소스

- AI Hub 면접 데이터셋 (https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=71592)
- 실제 채용 공고 (프로그래머스, 원티드, 사람인 등)
- 샘플 포트폴리오 데이터
- 연차/직무별 역량 매트릭스 (competency_matrix.json)

## 주요 워크플로우

### 포트폴리오 분석 → 면접 질문 생성
1. 사용자 포트폴리오 업로드 (PDF, GitHub 링크 등)
2. 포트폴리오에서 키워드 추출 및 역량 체크 (portfolio_checklist.json)
3. 연차/직무별 필수 역량과 비교 (competency_matrix.json)
4. 부족한 역량에 대한 면접 질문 선택 (interview_questions.json)
5. 맞춤형 면접 시나리오 생성 (scenario_templates.json)
6. AI 면접 진행 및 답변 평가 (evaluation_rubric.json)
