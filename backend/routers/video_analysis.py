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
    center_gaze_ratio, smile_ratio, nod_count, emotion_distribution, get_primary_emotion,
    compute_metadata
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
# GEMINI_API_KEY1, GEMINI_API_KEY2, GEMINI_API_KEY3 또는 GEMINI_API_KEY 중 하나라도 있으면 사용
# 실제 피드백 생성 시에는 generate_feedback_with_gemini()에서 키 1, 2, 3을 순차적으로 시도
USE_GEMINI = any(
    os.getenv(f"GEMINI_API_KEY{i}") for i in range(1, 4)
) or bool(os.getenv("GEMINI_API_KEY"))


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
        
        FPS_ANALYZED = 5.0  # Store for metadata
        frames = extract_frames_opencv(
            video_path, fps=FPS_ANALYZED, out_dir=frames_dir
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
        WHISPER_MODEL_SIZE = "base"  # Store for metadata
        stt = transcribe_whisper(wav, model_size=WHISPER_MODEL_SIZE)
        text = stt["text"]

        # 5. 메트릭 계산
        print("📊 Computing metrics...")
        emotion_dist = emotion_distribution(timeline)
        primary_emo = get_primary_emotion(timeline)
        
        # Calculate smile_ratio and capture threshold used
        smile_ratio_val, smile_threshold_used = smile_ratio(timeline, threshold=None)
        
        # Nod pitch threshold
        NOD_PITCH_THRESHOLD = 8.0
        
        metrics = {
            "center_gaze_ratio": center_gaze_ratio(timeline),
            "smile_ratio": smile_ratio_val,
            "nod_count": nod_count(timeline, pitch_thresh_deg=NOD_PITCH_THRESHOLD),
            "emotion_distribution": emotion_dist,
            "primary_emotion": primary_emo,
            "wpm": compute_wpm(text, duration_sec),
            "filler_count": compute_filler_count(text),
        }
        
        # 5.5. 메타데이터 계산
        print("📋 Computing metadata...")
        metadata = compute_metadata(
            timeline=timeline,
            fps_analyzed=FPS_ANALYZED,
            smile_threshold=smile_threshold_used,
            nod_pitch_threshold=NOD_PITCH_THRESHOLD,
            whisper_model_size=WHISPER_MODEL_SIZE,
            duration_sec=duration_sec
        )

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

        # 7. DB에 저장 (기존 데이터 삭제 후 새로 저장)
        print("💾 Saving to database...")
        
        # 7-0. 기존 분석 결과 삭제 (재분석 시 중복 방지)
        print("🗑️  기존 분석 결과 삭제 중...")
        db.query(InterviewTranscript).filter(InterviewTranscript.video_id == video_id).delete()
        db.query(NonverbalMetrics).filter(NonverbalMetrics.video_id == video_id).delete()
        db.query(NonverbalTimeline).filter(NonverbalTimeline.video_id == video_id).delete()
        db.query(Feedback).filter(Feedback.video_id == video_id).delete()
        db.flush()  # 삭제를 즉시 반영
        
        # 7-1. Transcript 저장
        transcript_record = InterviewTranscript(
            video_id=video_id,
            text=text,
            language="ko"  # Whisper가 자동 감지하지만 기본값
        )
        db.add(transcript_record)
        
        # 7-2. NonverbalMetrics 저장 (with metadata)
        metrics_record = NonverbalMetrics(
            video_id=video_id,
            center_gaze_ratio=metrics["center_gaze_ratio"],
            smile_ratio=metrics["smile_ratio"],
            nod_count=metrics["nod_count"],
            wpm=metrics["wpm"],
            filler_count=metrics["filler_count"],
            primary_emotion=primary_emo,
            metadata_json=json.dumps(metadata, ensure_ascii=False)  # Store metadata as JSON
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
            "metrics": {
                **metrics,
                "metadata": metadata  # Include computation metadata in response
            },
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
    timeline_data = None
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
    
    # Parse metadata from JSON
    metadata_dict = None
    if metrics and metrics.metadata_json:
        try:
            metadata_dict = json.loads(metrics.metadata_json)
        except Exception as e:
            print(f"⚠️ 메타데이터 파싱 실패: {e}")
    
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
            "metadata": metadata_dict  # Include computation metadata
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
        "timeline": timeline_data,  # 타임라인 JSON 직접 반환
        "timeline_available": timeline is not None
    }
