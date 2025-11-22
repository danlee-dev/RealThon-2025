"""
Video Analysis Router
면접 영상 분석 및 피드백 제공
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from sqlalchemy.orm import Session
from pathlib import Path
import soundfile as sf
import os
import json
import shutil
from datetime import datetime
from typing import Optional

from database import get_db
from models import InterviewVideo, InterviewTranscript, NonverbalMetrics, NonverbalTimeline, Feedback, InterviewSession, InterviewQuestion
from pipeline.video_io import extract_frames_opencv, extract_audio_ffmpeg
from pipeline.vision_mediapipe import build_timeline_from_frames, save_timeline
from pipeline.metrics import (
    center_gaze_ratio, smile_ratio, nod_count, emotion_distribution, get_primary_emotion
)
from pipeline.audio_analysis import transcribe_whisper, compute_wpm, compute_filler_count
from pipeline.feedback_generator import generate_feedback_with_gemini, generate_feedback_fallback
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

router = APIRouter()

# 비디오 저장 디렉토리
VIDEO_UPLOAD_DIR = Path("uploads/videos")
VIDEO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Gemini API 사용 여부 확인 (.env 로드 후)
USE_GEMINI = bool(os.getenv("GEMINI_API_KEY"))


def generate_feedback(m: dict):
    """분석 메트릭을 기반으로 한국어 피드백 생성"""
    fb = []

    # ---- gaze ----
    if m["center_gaze_ratio"] >= 0.8:
        fb.append(f"카메라 응시 비율이 {m['center_gaze_ratio']:.0%}로 매우 안정적이다. 정면 시선 유지가 잘 된다.")
    elif m["center_gaze_ratio"] >= 0.5:
        fb.append(f"카메라 응시 비율이 {m['center_gaze_ratio']:.0%}로 대체로 양호하다. 핵심 답변 구간에서 조금 더 유지하면 좋다.")
    else:
        fb.append(f"카메라 응시 비율이 {m['center_gaze_ratio']:.0%}로 낮다. 정면 시선을 더 의식해보면 신뢰감이 올라간다.")

    # ---- smile ----
    if m["smile_ratio"] >= 0.3:
        fb.append(f"미소/긍정 표정 비율이 {m['smile_ratio']:.0%}로 자연스럽다. 친근한 인상을 준다.")
    elif m["smile_ratio"] >= 0.1:
        fb.append(f"미소 비율이 {m['smile_ratio']:.0%}로 약간 적을 수 있다. 시작/마무리에서 가볍게 웃어보면 좋다.")
    else:
        fb.append(f"미소 비율이 {m['smile_ratio']:.0%}로 낮다. 표정이 딱딱하게 보일 수 있어 의도적으로 부드러운 표정을 넣어보자.")

    # ---- nod ----
    if m["nod_count"] == 0:
        fb.append("고개 끄덕임이 거의 감지되지 않는다. 공감/리스닝 제스처가 약해 보일 수 있다.")
    elif m["nod_count"] <= 2:
        fb.append("끄덕임이 과하지 않고 적절하다. 경청하는 인상을 준다.")
    else:
        fb.append("끄덕임이 많은 편이다. 과도하면 불안해 보일 수 있으니 속도를 조금 줄여도 좋다.")
    
    # ---- emotion ----
    emotion_dist = m.get("emotion_distribution", {})
    primary_emotion = m.get("primary_emotion")
    
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
    if m["wpm"] > 190:
        fb.append(f"말 속도가 WPM {m['wpm']:.0f}로 빠른 편이다. 문장 사이에 짧은 호흡을 넣어 전달력을 높여라.")
    elif m["wpm"] < 100:
        fb.append(f"말 속도가 WPM {m['wpm']:.0f}로 느린 편이다. 핵심 문장은 조금 더 자신 있게 속도를 줘도 좋다.")
    else:
        fb.append(f"말 속도(WPM {m['wpm']:.0f})가 안정적이다. 듣기 편한 템포다.")

    if m["filler_count"] > 6:
        fb.append(f"필러(음/어/uh 등)가 {m['filler_count']}회로 잦다. 답변 전 1초만 생각하고 말하면 훨씬 줄어든다.")
    else:
        fb.append(f"필러 사용({m['filler_count']}회)이 과도하지 않다. 전반적으로 유창하다.")

    return fb


@router.get("/status")
def video_status():
    """API 상태 확인"""
    return {
        "gemini_api_enabled": USE_GEMINI,
        "feedback_mode": "AI-powered (Gemini 2.5 Flash Lite)" if USE_GEMINI else "Rule-based",
        "upload_directory": str(VIDEO_UPLOAD_DIR.resolve())
    }


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    session_id: str = Form(...),
    question_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    비디오 파일 업로드 및 DB 저장
    
    Args:
        file: 업로드할 비디오 파일 (.mp4, .webm, .mov)
        user_id: 사용자 ID
        session_id: 면접 세션 ID
        question_id: 면접 질문 ID
    
    Returns:
        video_id, file_path 등
    """
    # 파일 확장자 검증
    allowed_extensions = {".mp4", ".webm", ".mov", ".avi"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Allowed: {allowed_extensions}"
        )
    
    try:
        # FK 검증: session_id와 question_id가 실제로 존재하는지 확인
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"InterviewSession not found: {session_id}. Please create a session first."
            )
        
        question = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()
        if not question:
            raise HTTPException(
                status_code=404,
                detail=f"InterviewQuestion not found: {question_id}. Please create a question first."
            )
        
        # session_id가 해당 user_id에 속하는지 확인
        if session.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail=f"Session {session_id} does not belong to user {user_id}"
            )
        
        # 고유 파일명 생성
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{user_id}_{session_id}_{timestamp}{file_ext}"
        video_path = VIDEO_UPLOAD_DIR / unique_filename
        
        # 파일 저장
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 비디오 길이 추출
        import cv2
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration_sec = frame_count / fps if fps > 0 else 0
        cap.release()
        
        # DB에 저장
        video_record = InterviewVideo(
            user_id=user_id,
            session_id=session_id,
            question_id=question_id,
            video_url=str(video_path),
            duration_sec=float(duration_sec)
        )
        db.add(video_record)
        db.commit()
        db.refresh(video_record)
        
        return {
            "video_id": video_record.id,
            "filename": unique_filename,
            "file_path": str(video_path),
            "duration_sec": duration_sec,
            "created_at": video_record.created_at
        }
        
    except HTTPException:
        # HTTPException은 그대로 전달
        raise
    except Exception as e:
        # 오류 발생시 업로드된 파일 삭제
        if 'video_path' in locals() and video_path.exists():
            video_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/analyze/{video_id}")
def analyze_interview(video_id: str, db: Session = Depends(get_db)):
    """
    업로드된 비디오 분석 및 AI 피드백 생성 + DB 저장
    
    Args:
        video_id: InterviewVideo ID
    
    Environment Variables:
        - GEMINI_API_KEY: Gemini API 키 (설정시 AI 피드백 사용)
    
    Returns:
        - 분석 결과 + DB에 저장된 레코드 IDs
    """
    # 1. DB에서 비디오 정보 조회
    video_record = db.query(InterviewVideo).filter(InterviewVideo.id == video_id).first()
    if not video_record:
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")
    
    video_path = Path(video_record.video_url)
    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Video file not found: {video_path}"
        )
    
    try:
        # 2. 비디오 분해
        print(f"🎬 Processing video: {video_path}")
        
        artifacts_dir = Path("artifacts") / video_id
        frames_dir = artifacts_dir / "frames"
        
        frames = extract_frames_opencv(
            video_path, fps=5.0, out_dir=frames_dir
        )

        # 3. Vision timeline 생성
        print("👁️ Analyzing facial features...")
        timeline = build_timeline_from_frames(frames)
        timeline_path = artifacts_dir / "timeline.json"
        save_timeline(timeline, timeline_path)

        # 4. 오디오 분석
        print("🎤 Analyzing audio...")
        wav_path = artifacts_dir / "audio.wav"
        wav = extract_audio_ffmpeg(video_path, wav_path)
        audio, sr = sf.read(str(wav))
        duration_sec = len(audio) / sr
        
        print("📝 Transcribing speech...")
        stt = transcribe_whisper(wav, model_size="base")
        text = stt["text"]

        # 5. 메트릭 계산
        print("📊 Computing metrics...")
        emotion_dist = emotion_distribution(timeline)
        primary_emo = get_primary_emotion(timeline)
        
        metrics = {
            "center_gaze_ratio": center_gaze_ratio(timeline),
            "smile_ratio": smile_ratio(timeline, threshold=None),
            "nod_count": nod_count(timeline),
            "emotion_distribution": emotion_dist,
            "primary_emotion": primary_emo,
            "wpm": compute_wpm(text, duration_sec),
            "filler_count": compute_filler_count(text),
        }

        # 6. 피드백 생성
        if USE_GEMINI:
            print("🤖 Generating feedback with Gemini 2.5 Flash Lite...")
            try:
                feedback_list = generate_feedback_with_gemini(metrics, transcript=text)
                feedback_mode = "gemini"
            except Exception as e:
                print(f"⚠️ Gemini failed, using fallback: {e}")
                feedback_list = generate_feedback_fallback(metrics)
                feedback_mode = "rule-based"
        else:
            print("📝 Generating feedback with rule-based system...")
            feedback_list = generate_feedback_fallback(metrics)
            feedback_mode = "rule-based"

        # 7. DB에 저장
        print("💾 Saving to database...")
        
        # 7-1. Transcript 저장
        transcript_record = InterviewTranscript(
            video_id=video_id,
            text=text,
            language="ko"  # Whisper가 자동 감지하지만 기본값
        )
        db.add(transcript_record)
        
        # 7-2. NonverbalMetrics 저장
        metrics_record = NonverbalMetrics(
            video_id=video_id,
            center_gaze_ratio=metrics["center_gaze_ratio"],
            smile_ratio=metrics["smile_ratio"],
            nod_count=metrics["nod_count"],
            wpm=metrics["wpm"],
            filler_count=metrics["filler_count"],
            primary_emotion=primary_emo
        )
        db.add(metrics_record)
        
        # 7-3. NonverbalTimeline 저장
        timeline_record = NonverbalTimeline(
            video_id=video_id,
            timeline_json=json.dumps(timeline, ensure_ascii=False)
        )
        db.add(timeline_record)
        
        # 7-4. Feedback 저장
        feedback_records = []
        for idx, feedback_text in enumerate(feedback_list):
            # 피드백 분류 (간단한 규칙)
            if any(word in feedback_text for word in ["우수", "안정적", "자연스럽", "적절", "긍정적"]):
                severity = "info"
                title = "강점"
            elif any(word in feedback_text for word in ["과다", "많", "딱딱", "낮", "긴장"]):
                severity = "warning"
                title = "개선 필요"
            else:
                severity = "suggestion"
                title = "제안"
            
            feedback_rec = Feedback(
                video_id=video_id,
                level="video",
                title=f"{title} #{idx+1}",
                message=feedback_text,
                severity=severity
            )
            feedback_records.append(feedback_rec)
            db.add(feedback_rec)
        
        # 커밋
        db.commit()
        
        print("✅ Analysis complete!")
        
        return {
            "video_id": video_id,
            "metrics": metrics,
            "feedback": feedback_list,
            "feedback_mode": feedback_mode,
            "transcript": text,
            "database_records": {
                "transcript_id": transcript_record.id,
                "metrics_id": metrics_record.id,
                "timeline_id": timeline_record.id,
                "feedback_ids": [f.id for f in feedback_records]
            }
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Video analysis failed: {str(e)}"
        )


@router.get("/results/{video_id}")
def get_analysis_results(video_id: str, db: Session = Depends(get_db)):
    """
    저장된 분석 결과 조회
    
    Args:
        video_id: InterviewVideo ID
    
    Returns:
        비디오, 메트릭, 피드백, 전사 등 모든 분석 결과
    """
    # 비디오 정보
    video = db.query(InterviewVideo).filter(InterviewVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")
    
    # 메트릭 (가장 최신 것 조회)
    metrics = db.query(NonverbalMetrics).filter(
        NonverbalMetrics.video_id == video_id
    ).order_by(NonverbalMetrics.created_at.desc()).first()
    
    # 피드백
    feedbacks = db.query(Feedback).filter(Feedback.video_id == video_id).all()
    
    # 전사
    transcript = db.query(InterviewTranscript).filter(InterviewTranscript.video_id == video_id).first()
    
    # 타임라인 (가장 최신 것 조회)
    timeline = db.query(NonverbalTimeline).filter(
        NonverbalTimeline.video_id == video_id
    ).order_by(NonverbalTimeline.created_at.desc()).first()
    
    # 타임라인에서 emotion_distribution 계산
    emotion_dist = {}
    primary_emo = None
    if timeline:
        try:
            timeline_data = json.loads(timeline.timeline_json)
            emotion_dist = emotion_distribution(timeline_data)
            primary_emo = get_primary_emotion(timeline_data)
        except Exception as e:
            print(f"⚠️ 타임라인 파싱 실패: {e}")
    
    # metrics의 primary_emotion이 있으면 우선 사용
    if metrics and metrics.primary_emotion:
        primary_emo = metrics.primary_emotion
    
    return {
        "video": {
            "id": video.id,
            "user_id": video.user_id,
            "session_id": video.session_id,
            "question_id": video.question_id,
            "duration_sec": video.duration_sec,
            "created_at": video.created_at
        },
        "metrics": {
            "center_gaze_ratio": metrics.center_gaze_ratio if metrics else None,
            "smile_ratio": metrics.smile_ratio if metrics else None,
            "nod_count": metrics.nod_count if metrics else None,
            "wpm": metrics.wpm if metrics else None,
            "filler_count": metrics.filler_count if metrics else None,
            "primary_emotion": primary_emo,
            "emotion_distribution": emotion_dist,
        } if metrics else None,
        "feedbacks": [
            {
                "id": f.id,
                "title": f.title,
                "message": f.message,
                "severity": f.severity,
                "level": f.level
            } for f in feedbacks
        ],
        "transcript": transcript.text if transcript else None,
        "timeline_available": timeline is not None
    }
