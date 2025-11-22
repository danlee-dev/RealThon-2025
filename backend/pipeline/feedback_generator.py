"""
Gemini-based feedback generation
AI를 활용한 면접 피드백 생성
"""
import os
from typing import Dict, List
from dotenv import load_dotenv
import google.generativeai as genai

# .env 파일 로드
load_dotenv()


def configure_gemini():
    """Configure Gemini API with environment variable"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    genai.configure(api_key=api_key)


def generate_feedback_with_gemini(metrics: Dict, transcript: str = "") -> List[str]:
    """
    Generate interview feedback using Gemini 2.5 Flash Lite.
    
    Args:
        metrics: 분석 메트릭 딕셔너리
        transcript: 면접 답변 전사 텍스트 (선택)
    
    Returns:
        List of feedback strings in Korean
    """
    try:
        configure_gemini()
        
        # Gemini 2.0 Flash 모델 사용 (가장 빠르고 효율적)
        # 사용 가능한 모델: gemini-2.0-flash-exp, gemini-1.5-flash, gemini-1.5-pro
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
        except Exception:
            # Fallback to stable version
            model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 프롬프트 구성
        prompt = build_feedback_prompt(metrics, transcript)
        
        # API 호출
        response = model.generate_content(prompt)
        
        # 응답 파싱
        feedback_text = response.text.strip()
        feedback_list = parse_feedback_response(feedback_text)
        
        return feedback_list
        
    except Exception as e:
        print(f"⚠️ Gemini API 호출 실패: {e}")
        # Fallback to rule-based feedback
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

1. 시선 처리:
   - 카메라 응시 비율: {metrics['center_gaze_ratio']:.1%}
   - 평가: {'우수' if metrics['center_gaze_ratio'] >= 0.7 else '보통' if metrics['center_gaze_ratio'] >= 0.5 else '개선 필요'}

2. 표정 관리:
   - 미소/긍정 표정 비율: {metrics['smile_ratio']:.1%}
   - 평가: {'자연스러움' if metrics['smile_ratio'] >= 0.25 else '다소 부족' if metrics['smile_ratio'] >= 0.1 else '개선 필요'}

3. 제스처:
   - 고개 끄덕임 횟수: {metrics['nod_count']}회
   - 평가: {'적절함' if 1 <= metrics['nod_count'] <= 3 else '과다' if metrics['nod_count'] > 3 else '부족'}

{emotion_info}

4. 말하기 패턴:
   - 말 속도: {metrics['wpm']:.0f} WPM (분당 단어 수)
   - 목표: 140-180 WPM
   - 필러 사용: {metrics['filler_count']}회 (음, 어, uh, um 등)
   - 평가: {'적절' if metrics['filler_count'] <= 5 else '다소 많음' if metrics['filler_count'] <= 10 else '과다'}
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
    
    prompt = f"""당신은 면접 코칭 전문가입니다. 면접 영상 분석 결과를 바탕으로 지원자에게 구체적이고 실용적인 피드백을 제공해주세요.

{metrics_summary}{transcript_section}

**피드백 작성 가이드라인:**

1. **톤**: 격려하면서도 전문적이고 구체적으로
2. **구조**: 각 피드백은 "관찰 → 해석 → 개선 제안" 순서로
3. **실용성**: 즉시 실천 가능한 구체적 팁 제공
4. **긍정성**: 강점을 먼저 언급하고, 개선점은 건설적으로
5. **개인화**: 이 지원자의 데이터를 기반으로 맞춤형 조언

**피드백 항목 (5-7개):**
- 시선 처리 (아이 컨택)
- 표정 관리 (미소, 감정 표현)
- 제스처와 자세 (끄덕임 등)
- 말하기 속도와 리듬
- 필러 사용 개선
- 전반적 인상 및 강점
- 우선순위 개선 사항

각 피드백은 2-3문장으로, 불릿 포인트(•, -)나 번호 없이 **평문**으로 작성해주세요.
각 피드백은 줄바꿈으로 구분됩니다.

피드백:"""

    return prompt


def parse_feedback_response(response_text: str) -> List[str]:
    """
    Parse Gemini response into list of feedback items.
    """
    # 줄바꿈으로 분리
    lines = response_text.strip().split('\n')
    
    feedback_list = []
    for line in lines:
        line = line.strip()
        
        # 빈 줄 건너뛰기
        if not line:
            continue
        
        # 불릿 포인트나 번호 제거
        line = line.lstrip('•-*123456789.) ')
        
        # 너무 짧은 줄 건너뛰기
        if len(line) < 20:
            continue
        
        feedback_list.append(line)
    
    return feedback_list


def generate_feedback_fallback(metrics: Dict) -> List[str]:
    """
    Fallback to rule-based feedback if Gemini API fails.
    기존 규칙 기반 피드백
    """
    fb = []

    # ---- gaze ----
    if metrics["center_gaze_ratio"] >= 0.8:
        fb.append(f"카메라 응시 비율이 {metrics['center_gaze_ratio']:.0%}로 매우 안정적이다. 정면 시선 유지가 잘 된다.")
    elif metrics["center_gaze_ratio"] >= 0.5:
        fb.append(f"카메라 응시 비율이 {metrics['center_gaze_ratio']:.0%}로 대체로 양호하다. 핵심 답변 구간에서 조금 더 유지하면 좋다.")
    else:
        fb.append(f"카메라 응시 비율이 {metrics['center_gaze_ratio']:.0%}로 낮다. 정면 시선을 더 의식해보면 신뢰감이 올라간다.")

    # ---- smile ----
    if metrics["smile_ratio"] >= 0.3:
        fb.append(f"미소/긍정 표정 비율이 {metrics['smile_ratio']:.0%}로 자연스럽다. 친근한 인상을 준다.")
    elif metrics["smile_ratio"] >= 0.1:
        fb.append(f"미소 비율이 {metrics['smile_ratio']:.0%}로 약간 적을 수 있다. 시작/마무리에서 가볍게 웃어보면 좋다.")
    else:
        fb.append(f"미소 비율이 {metrics['smile_ratio']:.0%}로 낮다. 표정이 딱딱하게 보일 수 있어 의도적으로 부드러운 표정을 넣어보자.")

    # ---- nod ----
    if metrics["nod_count"] == 0:
        fb.append("고개 끄덕임이 거의 감지되지 않는다. 공감/리스닝 제스처가 약해 보일 수 있다.")
    elif metrics["nod_count"] <= 2:
        fb.append("끄덕임이 과하지 않고 적절하다. 경청하는 인상을 준다.")
    else:
        fb.append("끄덕임이 많은 편이다. 과도하면 불안해 보일 수 있으니 속도를 조금 줄여도 좋다.")
    
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
            fb.append(f"전체적으로 {emotion_kr} 표정({primary_ratio:.0%})이 우세하다. 매우 긍정적인 인상을 준다.")
        elif primary_emotion == "pleasant":
            fb.append(f"{emotion_kr} 표정({primary_ratio:.0%})이 주를 이룬다. 안정적이고 신뢰감 있는 인상이다.")
        elif primary_emotion == "neutral" and primary_ratio > 0.7:
            fb.append(f"중립적 표정({primary_ratio:.0%})이 많다. 핵심 내용을 말할 때 미소를 더하면 좋다.")
        elif primary_emotion == "concerned":
            fb.append(f"다소 긴장된 표정({primary_ratio:.0%})이 보인다. 심호흡하고 어깨를 내리면 좋다.")

    # ---- speech ----
    if metrics["wpm"] > 190:
        fb.append(f"말 속도가 WPM {metrics['wpm']:.0f}로 빠른 편이다. 문장 사이에 짧은 호흡을 넣어 전달력을 높여라.")
    elif metrics["wpm"] < 100:
        fb.append(f"말 속도가 WPM {metrics['wpm']:.0f}로 느린 편이다. 핵심 문장은 조금 더 자신 있게 속도를 줘도 좋다.")
    else:
        fb.append(f"말 속도(WPM {metrics['wpm']:.0f})가 안정적이다. 듣기 편한 템포다.")

    if metrics["filler_count"] > 6:
        fb.append(f"필러(음/어/uh 등)가 {metrics['filler_count']}회로 잦다. 답변 전 1초만 생각하고 말하면 훨씬 줄어든다.")
    else:
        fb.append(f"필러 사용({metrics['filler_count']}회)이 과도하지 않다. 전반적으로 유창하다.")

    return fb

