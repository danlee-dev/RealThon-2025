"""
Gemini-based feedback generation
AI를 활용한 면접 피드백 생성
"""
import os
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import google.generativeai as genai

# .env 파일 로드
load_dotenv()


def get_gemini_api_keys() -> List[str]:
    """Get available Gemini API keys from environment variables"""
    keys = []
    for i in range(1, 4):  # GEMINI_API_KEY1, GEMINI_API_KEY2, GEMINI_API_KEY3
        key = os.getenv(f"GEMINI_API_KEY{i}")
        if key:
            keys.append(key)
    # 기존 GEMINI_API_KEY도 지원 (하위 호환성)
    legacy_key = os.getenv("GEMINI_API_KEY")
    if legacy_key and legacy_key not in keys:
        keys.append(legacy_key)
    return keys


def generate_feedback_with_gemini(metrics: Dict, transcript: str = "") -> List[str]:
    """
    Generate interview feedback using Gemini API.
    여러 API 키를 순차적으로 시도: GEMINI_API_KEY1 -> GEMINI_API_KEY2 -> GEMINI_API_KEY3
    
    Args:
        metrics: 분석 메트릭 딕셔너리
        transcript: 면접 답변 전사 텍스트 (선택)
    
    Returns:
        List of feedback strings in Korean
    """
    api_keys = get_gemini_api_keys()
    
    if not api_keys:
        print("⚠️ Gemini API 키가 없습니다. 규칙 기반 피드백을 사용합니다.")
        return generate_feedback_fallback(metrics)
    
    # 프롬프트 구성 (한 번만)
    prompt = build_feedback_prompt(metrics, transcript)
    
    # 각 API 키로 시도
    for idx, api_key in enumerate(api_keys, 1):
        try:
            print(f"🤖 Gemini API 키 #{idx} 시도 중...")
            genai.configure(api_key=api_key)
            
            # Gemini 2.0 Flash 모델 사용 (가장 빠르고 효율적)
            # 사용 가능한 모델: gemini-2.0-flash, gemini-1.5-flash, gemini-1.5-pro
            try:
                model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception:
                # Fallback to stable version
                model = genai.GenerativeModel('gemini-1.5-flash')
            
            # API 호출
            response = model.generate_content(prompt)
            
            # 응답 파싱
            feedback_text = response.text.strip()
            print(f"✅ API 키 #{idx} 성공!")
            print(f"📝 Gemini 원본 응답 (처음 500자): {feedback_text[:500]}")
            
            feedback_list = parse_feedback_response(feedback_text)
            print(f"✅ 파싱된 피드백 개수: {len(feedback_list)}")
            
            if len(feedback_list) == 0:
                print("⚠️ 파싱된 피드백이 없습니다. 원본 응답을 그대로 사용합니다.")
                return [feedback_text]
            
            return feedback_list
            
        except Exception as e:
            print(f"⚠️ API 키 #{idx} 실패: {str(e)[:200]}")
            # 마지막 키가 아니면 다음 키로 시도
            if idx < len(api_keys):
                print(f"   다음 API 키로 시도합니다...")
                continue
            else:
                # 모든 키 실패
                print(f"❌ 모든 API 키 시도 실패. 규칙 기반 피드백을 사용합니다.")
                import traceback
                print(f"마지막 에러 상세: {traceback.format_exc()}")
                return generate_feedback_fallback(metrics)
    
    # 여기 도달하면 안 되지만 안전장치
    return generate_feedback_fallback(metrics)


def build_feedback_prompt(metrics: Dict, transcript: str = "") -> str:
    """
    Build a comprehensive prompt for Gemini API.
    프롬프트 엔지니어링으로 고품질 피드백 생성
    """
    
    # 감정 정보 정리
    emotion_info = ""
    if metrics.get("emotion_distribution"):
        emotion_dist = metrics["emotion_distribution"]
        primary_emotion = metrics.get("primary_emotion", "")
        emotion_info = f"""
감정 분석:
- 주요 감정: {primary_emotion}
- 감정 분포: {emotion_dist}
"""
    
    # 메트릭 요약
    metrics_summary = f"""
비언어적 커뮤니케이션 분석 결과:

1. 시선 처리 (Eye Contact):
   - 카메라 응시 비율: {metrics['center_gaze_ratio']:.1%}
   - 평가: {'우수 ✓' if metrics['center_gaze_ratio'] >= 0.7 else '보통' if metrics['center_gaze_ratio'] >= 0.5 else '개선 필요 ⚠️'}
   - 의미: 면접관과의 눈 맞춤을 얼마나 잘 유지했는지 측정. 높을수록 신뢰감과 자신감 전달.

2. 표정 관리 (Facial Expression):
   - 미소/긍정 표정 비율: {metrics['smile_ratio']:.1%}
   - 평가: {'자연스러움 ✓' if metrics['smile_ratio'] >= 0.25 else '다소 부족' if metrics['smile_ratio'] >= 0.1 else '개선 필요 ⚠️'}
   - 의미: 자연스럽고 긍정적인 표정의 빈도. 과도하지 않으면서 친근한 인상 중요.

3. 제스처 (Head Nod):
   - 고개 끄덕임 횟수: {metrics['nod_count']}회
   - 평가: {'적절함 ✓' if 1 <= metrics['nod_count'] <= 3 else '과다 ⚠️' if metrics['nod_count'] > 3 else '부족'}
   - 의미: 경청과 공감을 표현하는 비언어적 신호. 1-3회가 자연스러움.

{emotion_info}

4. 말하기 패턴 (Speech Pattern):
   - 말 속도: {metrics['wpm']:.0f} WPM (Words Per Minute)
   - 목표 범위: 140-180 WPM (이상적인 면접 속도)
   - 현재 평가: {'적절함 ✓' if 140 <= metrics['wpm'] <= 180 else '다소 느림' if metrics['wpm'] < 140 else '다소 빠름'}
   
   - 필러 사용: {metrics['filler_count']}회 (음, 어, 그, uh, um, like 등)
   - 평가: {'우수 ✓' if metrics['filler_count'] <= 5 else '보통' if metrics['filler_count'] <= 10 else '개선 필요 ⚠️'}
   - 의미: 불필요한 채움말 빈도. 적을수록 답변이 명확하고 자신감 있어 보임.
"""
    
    # 전사 텍스트가 있으면 추가
    transcript_section = ""
    if transcript:
        # 너무 길면 앞부분만
        transcript_preview = transcript[:500] + "..." if len(transcript) > 500 else transcript
        transcript_section = f"""

5. 답변 내용 (참고용):
```
{transcript_preview}
```
"""
    
    prompt = f"""당신은 면접 코칭 전문가입니다. 면접 영상 분석 결과를 바탕으로 지원자에게 매우 구체적이고 실용적인 피드백을 제공해주세요.

{metrics_summary}{transcript_section}

**피드백 작성 가이드라인:**

1. **톤**: 격려하면서도 전문적이고 구체적으로, 친근하지만 전문가다운 톤 유지
   - "~하세요" 보다는 "~하면 좋다", "~할 수 있다" 등의 자연스러운 어투 사용
   
2. **구조**: 각 피드백은 반드시 다음 순서로 작성:
   - **관찰**: 현재 상태를 구체적인 수치와 함께 설명
   - **해석**: 이것이 면접관에게 어떤 인상을 주는지 설명
   - **개선 제안**: 즉시 실천 가능한 구체적인 솔루션 2-3가지 제시
   
3. **실용성**: 모든 피드백은 즉시 실천 가능한 구체적 팁이어야 함
   - ❌ "시선 처리를 개선하세요" (추상적)
   - ✅ "1) 카메라 렌즈 중앙에 작은 포스트잇을 붙여 고정점 만들기, 2) 답변 전 1-2초 카메라를 응시한 후 말하기 시작하기, 3) 연습 시 거울 앞에서 정면 응시 연습하기" (구체적)
   
4. **긍정성**: 강점을 먼저 언급하고, 개선점은 건설적으로 제시
   - 항상 지원자의 노력과 잠재력을 인정하는 표현 포함
   
5. **개인화**: 이 지원자의 실제 데이터를 기반으로 맞춤형 조언 제공
   - 일반적인 조언이 아닌, 수치와 관찰에 근거한 맞춤형 피드백
   
6. **상세성**: 각 피드백은 최소 3-4문장으로 작성하여 충분히 자세하게 설명
   - 왜 중요한지, 어떻게 개선할지 모두 포함

**피드백 항목 (6-8개, 우선순위 순):**

1. **시선 처리** - 카메라 응시 비율 분석 및 신뢰감 향상 방법
2. **표정 관리** - 미소/표정 비율과 자연스러운 긍정적 인상 방법
3. **감정 표현** - 주요 감정 및 분포 분석, 적절한 감정 표현 방법
4. **제스처와 자세** - 끄덕임 횟수와 경청 신호 최적화 방법
5. **말하기 속도** - WPM 분석 및 이상적인 템포 조절 방법
6. **필러 사용** - 채움말 빈도와 유창한 답변 연습 방법
7. **전반적 강점** - 잘한 부분 3가지와 유지 전략
8. **우선순위 개선 사항** - 즉시 실천할 1-2가지 핵심 조언

**각 피드백 작성 형식:**

- 불릿 포인트(•, -)나 번호 **없이** 평문으로 작성
- 각 피드백은 3-5문장으로 충분히 자세하게 작성
- 개선이 필요한 경우 반드시 구체적인 솔루션 2-3가지 포함
- 솔루션은 "1) 구체적 방법, 2) 구체적 방법" 형식으로 명시
- 각 피드백은 빈 줄로 구분

**피드백 예시:**

[개선이 필요한 경우]
카메라 응시 비율이 45%로 다소 낮은 편이다. 시선이 자주 흔들리면 면접관에게 불안하거나 준비가 부족해 보일 수 있다. 개선 방법: 1) 카메라 렌즈 중앙에 작은 포스트잇을 붙여 시선 고정점을 만들기, 2) 답변 시작 전 1-2초간 카메라를 직접 응시한 후 말하기 시작하는 습관 들이기, 3) 연습할 때 스마트폰 카메라로 녹화하며 시선 패턴 체크하기. 이렇게 연습하면 실전에서 자연스럽게 신뢰감 있는 인상을 줄 수 있다.

[양호한 경우]
카메라 응시 비율이 93%로 매우 안정적이다. 정면 시선을 꾸준히 유지하여 면접관에게 자신감 있고 진솔한 인상을 전달하고 있다. 이 습관은 대면 면접에서도 큰 강점이 될 것이므로 계속 유지하면 좋다. 답변 중간에도 자연스럽게 시선을 유지하는 모습이 인상적이다.

피드백:"""

    return prompt


def parse_feedback_response(response_text: str) -> List[str]:
    """
    Parse Gemini response into list of feedback items.
    더 robust한 파싱 로직으로 개선
    """
    if not response_text or not response_text.strip():
        return []
    
    # 빈 줄로 구분된 피드백 항목들을 찾기
    # Gemini는 보통 빈 줄로 각 피드백을 구분함
    paragraphs = response_text.strip().split('\n\n')
    
    feedback_list = []
    
    for para in paragraphs:
        # 각 paragraph를 줄바꿈으로 분리
        lines = [line.strip() for line in para.split('\n') if line.strip()]
        
        if not lines:
            continue
        
        # 여러 줄을 하나의 피드백으로 합치기
        combined = ' '.join(lines)
        
        # 불릿 포인트나 번호 제거 (시작 부분만)
        combined = combined.lstrip('•-*123456789.) ')
        
        # 너무 짧은 피드백 건너뛰기 (20자 미만)
        if len(combined) < 20:
            continue
        
        # 이미 포함된 피드백과 중복 체크 (간단한 방법)
        if combined not in feedback_list:
            feedback_list.append(combined)
    
    # 빈 줄로 구분되지 않은 경우, 줄바꿈으로 시도
    if len(feedback_list) < 2:
        lines = response_text.strip().split('\n')
        current_feedback = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # 빈 줄이면 현재까지 모은 것을 하나의 피드백으로
                if current_feedback:
                    combined = ' '.join(current_feedback)
                    combined = combined.lstrip('•-*123456789.) ')
                    if len(combined) >= 20 and combined not in feedback_list:
                        feedback_list.append(combined)
                    current_feedback = []
                continue
            
            # 불릿 포인트나 번호로 시작하는 줄은 새 피드백의 시작
            if line[0] in '•-*123456789':
                if current_feedback:
                    combined = ' '.join(current_feedback)
                    combined = combined.lstrip('•-*123456789.) ')
                    if len(combined) >= 20 and combined not in feedback_list:
                        feedback_list.append(combined)
                current_feedback = [line.lstrip('•-*123456789.) ')]
            else:
                current_feedback.append(line)
        
        # 마지막 피드백 처리
        if current_feedback:
            combined = ' '.join(current_feedback)
            combined = combined.lstrip('•-*123456789.) ')
            if len(combined) >= 20 and combined not in feedback_list:
                feedback_list.append(combined)
    
    # 여전히 피드백이 없거나 너무 적으면 전체를 하나로
    if len(feedback_list) < 2:
        cleaned = response_text.strip().lstrip('•-*123456789.) ')
        if len(cleaned) >= 20:
            # 긴 텍스트를 문장 단위로 나누기
            sentences = cleaned.split('. ')
            current = []
            for sent in sentences:
                current.append(sent)
                if len(' '.join(current)) >= 50:  # 최소 50자 이상이면 하나의 피드백으로
                    feedback_list.append('. '.join(current) + ('.' if not current[-1].endswith('.') else ''))
                    current = []
            if current:
                feedback_list.append('. '.join(current))
    
    return feedback_list if feedback_list else [response_text.strip()]


def generate_feedback_fallback(metrics: Dict) -> List[str]:
    """
    Fallback to rule-based feedback if Gemini API fails.
    기존 규칙 기반 피드백 (솔루션 포함)
    """
    fb = []

    # ---- gaze ----
    if metrics["center_gaze_ratio"] >= 0.8:
        fb.append(f"카메라 응시 비율이 {metrics['center_gaze_ratio']:.0%}로 매우 안정적이다. 정면 시선 유지가 잘 되어 신뢰감 있는 인상을 준다. 이 패턴을 유지하면 좋다.")
    elif metrics["center_gaze_ratio"] >= 0.5:
        fb.append(f"카메라 응시 비율이 {metrics['center_gaze_ratio']:.0%}로 대체로 양호하다. 핵심 답변 구간에서 조금 더 정면을 바라보면 신뢰감이 올라간다. 개선 방법: 1) 카메라 렌즈 중앙에 작은 스티커를 붙여 시선 고정점 만들기, 2) 모니터 상단 가장자리를 응시하는 습관 들이기, 3) 답변 시작 전 1-2초 카메라 응시 후 말하기. 이렇게 하면 더 안정적인 시선을 유지할 수 있다.")
    else:
        fb.append(f"카메라 응시 비율이 {metrics['center_gaze_ratio']:.0%}로 낮다. 시선이 자주 흔들리면 불안해 보일 수 있다. 개선 방법: 1) 카메라 렌즈 중앙에 작은 포스트잇을 붙여 고정점 만들기, 2) 답변 전 1-2초 카메라를 응시한 후 말하기 시작하기, 3) 연습 시 거울 앞에서 정면 응시 연습하기. 이렇게 하면 신뢰감 있는 인상을 줄 수 있다.")

    # ---- smile ----
    if metrics["smile_ratio"] >= 0.3:
        fb.append(f"미소/긍정 표정 비율이 {metrics['smile_ratio']:.0%}로 자연스럽다. 친근하고 긍정적인 인상을 주어 면접관에게 좋은 첫인상을 남긴다. 이 밝은 표정을 유지하면 좋다.")
    elif metrics["smile_ratio"] >= 0.1:
        fb.append(f"미소 비율이 {metrics['smile_ratio']:.0%}로 약간 적을 수 있다. 표정이 다소 딱딱해 보일 수 있어 자연스러운 미소를 더하면 좋다. 개선 방법: 1) 면접 시작 인사와 마무리 인사 시 가볍게 미소 짓기, 2) 자신의 강점이나 성과를 말할 때 자연스럽게 미소 넣기, 3) 연습 시 거울 앞에서 '입꼬리 살짝 올리기' 연습하기. 이렇게 하면 친근하고 자신감 있는 인상을 줄 수 있다.")
    else:
        fb.append(f"미소 비율이 {metrics['smile_ratio']:.0%}로 낮다. 표정이 딱딱하고 경직되어 보일 수 있어 의도적으로 부드러운 표정을 넣어야 한다. 개선 방법: 1) 면접 전 거울 앞에서 자연스러운 미소 연습하기 (입꼬리 1-2mm만 올리기), 2) 답변 시작 전 '안녕하세요' 인사 시 미소 포함하기, 3) 긍정적인 내용을 말할 때 표정도 함께 밝게 하기, 4) 연습 시 '친구에게 설명하는 것처럼' 편안한 톤과 표정 유지하기. 이렇게 하면 접근하기 쉬운 인상을 줄 수 있다.")

    # ---- nod ----
    if metrics["nod_count"] == 0:
        fb.append("고개 끄덕임이 거의 감지되지 않는다. 공감과 경청을 나타내는 제스처가 부족해 보일 수 있다. 개선 방법: 1) 면접관의 질문을 듣는 동안 가볍게 1-2회 끄덕이기, 2) '네, 이해했습니다' 같은 긍정 응답 시 자연스럽게 끄덕이기, 3) 과도하지 않게 느린 속도로 끄덕이기 (1초에 1회 정도). 이렇게 하면 적극적으로 경청하고 있다는 인상을 줄 수 있다.")
    elif metrics["nod_count"] <= 2:
        fb.append("끄덕임이 과하지 않고 적절하다. 경청하는 인상을 주면서도 불안해 보이지 않아 좋다. 이 패턴을 유지하면 된다.")
    else:
        fb.append("끄덕임이 많은 편이다. 과도하면 불안하거나 긴장한 것처럼 보일 수 있다. 개선 방법: 1) 끄덕임 속도를 줄이기 (2-3초에 1회 정도), 2) 면접관의 질문을 듣는 동안에만 끄덕이기, 3) 자신의 답변 중에는 끄덕임 최소화하기. 이렇게 하면 더 차분하고 자신감 있는 인상을 줄 수 있다.")
    
    # ---- emotion ----
    emotion_dist = metrics.get("emotion_distribution", {})
    primary_emotion = metrics.get("primary_emotion")
    
    if emotion_dist and primary_emotion:
        emotion_names = {
            "happy": "밝고 긍정적",
            "pleasant": "차분하고 호감가는",
            "neutral": "중립적",
            "surprised": "놀람/집중",
            "concerned": "걱정스러운"
        }
        emotion_kr = emotion_names.get(primary_emotion, primary_emotion)
        primary_ratio = emotion_dist.get(primary_emotion, 0)
        
        if primary_emotion == "happy" and primary_ratio > 0.4:
            fb.append(f"전체적으로 {emotion_kr} 표정({primary_ratio:.0%})이 우세하다. 매우 긍정적이고 자신감 있는 인상을 주어 면접관에게 좋은 느낌을 준다. 이 밝은 에너지를 유지하면 좋다.")
        elif primary_emotion == "pleasant":
            fb.append(f"{emotion_kr} 표정({primary_ratio:.0%})이 주를 이룬다. 안정적이고 신뢰감 있는 인상으로 면접관에게 좋은 인상을 준다. 이 차분한 톤을 유지하면 좋다.")
        elif primary_emotion == "neutral" and primary_ratio > 0.7:
            fb.append(f"중립적 표정({primary_ratio:.0%})이 많다. 표정 변화가 적어 다소 무표정해 보일 수 있다. 개선 방법: 1) 핵심 내용을 말할 때 미소를 더하기, 2) 자신의 강점을 설명할 때 표정도 함께 밝게 하기, 3) 연습 시 거울 앞에서 '입꼬리 살짝 올리기' 연습하기. 이렇게 하면 더 생동감 있고 열정적인 인상을 줄 수 있다.")
        elif primary_emotion == "concerned":
            fb.append(f"다소 긴장되거나 걱정스러운 표정({primary_ratio:.0%})이 보인다. 불안해 보일 수 있어 표정 관리를 개선해야 한다. 개선 방법: 1) 면접 전 심호흡 연습하기 (4초 들이쉬기, 4초 내쉬기), 2) 어깨를 내리고 턱을 살짝 당기기, 3) 답변 시작 전 1초간 미소 짓고 시작하기, 4) 긍정적인 자세 유지하기 (가슴 펴기, 어깨 내리기). 이렇게 하면 더 자신감 있고 차분한 인상을 줄 수 있다.")

    # ---- speech ----
    if metrics["wpm"] > 190:
        fb.append(f"말 속도가 WPM {metrics['wpm']:.0f}로 빠른 편이다. 빠른 말투는 불안하거나 성급해 보일 수 있어 속도 조절이 필요하다. 개선 방법: 1) 문장 사이에 0.5-1초 호흡 넣기, 2) 핵심 키워드 앞뒤로 0.3초씩 멈추기, 3) 연습 시 타이머로 1분에 150단어 정도 속도 연습하기, 4) '그리고', '또한' 같은 연결어에서 잠깐 멈추기. 이렇게 하면 전달력이 높아지고 듣기 편한 템포가 된다.")
    elif metrics["wpm"] < 100:
        fb.append(f"말 속도가 WPM {metrics['wpm']:.0f}로 느린 편이다. 너무 느리면 답답하거나 자신감이 부족해 보일 수 있다. 개선 방법: 1) 핵심 문장은 조금 더 자신 있게 속도 주기, 2) 불필요한 멈춤 줄이기, 3) 연습 시 타이머로 1분에 140-160단어 속도 목표로 연습하기, 4) 답변 전 2-3초 생각 시간 후 자신 있게 말하기. 이렇게 하면 더 역동적이고 자신감 있는 인상을 줄 수 있다.")
    else:
        fb.append(f"말 속도(WPM {metrics['wpm']:.0f})가 안정적이다. 듣기 편한 템포로 면접관이 내용을 이해하기 좋다. 이 속도를 유지하면 좋다.")

    if metrics["filler_count"] > 6:
        fb.append(f"필러(음/어/uh 등)가 {metrics['filler_count']}회로 잦다. 필러가 많으면 답변이 덜 유창해 보일 수 있다. 개선 방법: 1) 답변 전 1-2초 생각 시간 갖기 (침묵은 괜찮음), 2) 필러 대신 0.5초 멈춤 사용하기, 3) 연습 시 필러 사용하지 않고 말하기 연습하기, 4) '음', '어' 대신 '그렇습니다', '네' 같은 명확한 응답 사용하기. 이렇게 하면 더 전문적이고 유창한 인상을 줄 수 있다.")
    else:
        fb.append(f"필러 사용({metrics['filler_count']}회)이 과도하지 않다. 전반적으로 유창하고 자연스러운 답변으로 좋은 인상을 준다. 이 패턴을 유지하면 좋다.")

    return fb


def detect_timeline_segments(timeline: List[Dict]) -> List[Dict]:
    """
    Detect problematic segments in timeline:
    - smile >= 0.8 (과도한 웃음)
    
    Returns list of segments with start_t, end_t, and average smile value
    """
    segments = []
    
    if not timeline:
        return segments
    
    valid_frames = [f for f in timeline if f.get("valid")]
    if not valid_frames:
        return segments
    
    # Smile segments (smile >= 0.8)
    current_smile_start = None
    smile_values = []  # Collect smile values for average
    
    for i, frame in enumerate(valid_frames):
        smile = frame.get("smile")
        t = frame.get("t", 0.0)
        
        if smile is not None and smile >= 0.8:
            if current_smile_start is None:
                # Start of new smile segment
                current_smile_start = t
                smile_values = [smile]
            else:
                # Continue segment, collect smile value
                smile_values.append(smile)
        else:
            # End of smile segment
            if current_smile_start is not None:
                # Use previous frame's time as end
                prev_t = valid_frames[i-1].get("t", t) if i > 0 else current_smile_start
                # Calculate average smile value
                avg_smile = sum(smile_values) / len(smile_values) if smile_values else 0.8
                segments.append({
                    "start_t": current_smile_start,
                    "end_t": prev_t,
                    "severity": avg_smile  # Average smile value as severity
                })
                current_smile_start = None
                smile_values = []
    
    # Handle segment that continues to end
    if current_smile_start is not None:
        last_t = valid_frames[-1].get("t", 0.0)
        avg_smile = sum(smile_values) / len(smile_values) if smile_values else 0.8
        segments.append({
            "start_t": current_smile_start,
            "end_t": last_t,
            "severity": avg_smile
        })
    
    # Sort by start_t
    segments.sort(key=lambda x: x["start_t"])
    
    return segments


def generate_alert_feedback_with_gemini(segment: Dict) -> Optional[str]:
    """
    Generate natural language feedback for a timeline segment using Gemini.
    
    Args:
        segment: Segment dict with start_t, end_t, and severity (average smile value)
    
    Returns:
        Natural language feedback string in Korean, or None if Gemini fails
    """
    api_keys = get_gemini_api_keys()
    
    severity = segment.get("severity", 0.8)
    
    if not api_keys:
        # Fallback to simple rule-based feedback
        return f"{segment['start_t']:.1f}초~{segment['end_t']:.1f}초 구간에서 웃음이 과도했습니다 (평균 미소 점수: {severity:.2f}). 자연스러운 표정을 유지하는 것이 좋습니다."
    
    # Build prompt
    prompt = f"""면접 영상 분석 중 {segment['start_t']:.1f}초부터 {segment['end_t']:.1f}초까지의 구간에서 웃음이 과도했습니다 (평균 미소 점수: {severity:.2f}).

이 구간에 대해 면접 코칭 전문가 관점에서 간단하고 실용적인 피드백을 한 문장으로 작성해주세요.
예: "웃음이 과하다" 또는 "표정을 조금 더 차분하게 유지하세요" 같은 자연스러운 표현으로 작성해주세요.

피드백:"""
    
    # Try each API key
    for idx, api_key in enumerate(api_keys, 1):
        try:
            genai.configure(api_key=api_key)
            
            try:
                model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception:
                model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(prompt)
            feedback_text = response.text.strip()
            
            # Clean up feedback (remove quotes, bullets, etc.)
            feedback_text = feedback_text.lstrip('"\'•-*123456789.) ')
            feedback_text = feedback_text.rstrip('"\'')
            
            if len(feedback_text) >= 5:  # Minimum length check
                return feedback_text
            
        except Exception as e:
            if idx < len(api_keys):
                continue
            # All keys failed, use fallback
            break
    
    # Fallback
    return f"{segment['start_t']:.1f}초~{segment['end_t']:.1f}초 구간에서 웃음이 과하다."


def generate_alerts_from_timeline(timeline: List[Dict]) -> List[Dict]:
    """
    Generate alerts from timeline by detecting problematic segments and generating feedback.
    
    Returns list of alerts with:
    - start_t: start time in seconds
    - end_t: end time in seconds
    - severity: average smile value in the segment
    - message: natural language feedback from Gemini
    """
    segments = detect_timeline_segments(timeline)
    alerts = []
    
    for segment in segments:
        message = generate_alert_feedback_with_gemini(segment)
        
        if message:
            alerts.append({
                "start_t": segment["start_t"],
                "end_t": segment["end_t"],
                "severity": segment["severity"],
                "message": message
            })
    
    return alerts

