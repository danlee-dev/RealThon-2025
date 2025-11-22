from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, HttpUrl
import json
import os
from database import get_db
from models import JobPosting, User
from schemas import JobPostingCreate, JobPostingResponse
from services.job_posting_crawler import crawl_job_posting
from services.gemini_service import GeminiService

router = APIRouter()

# Gemini 서비스 인스턴스
gemini_service = GeminiService()


class CrawlRequest(BaseModel):
    """직무 공고 크롤링 요청"""
    url: str  # 크롤링할 URL


@router.post("/crawl", response_model=JobPostingResponse, status_code=status.HTTP_201_CREATED)
def crawl_and_create_job_posting(
    request: CrawlRequest,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    직무 공고 URL을 크롤링하여 사용자의 희망직무 목록에 저장합니다.
    
    Args:
        request: 크롤링 요청 (url 포함)
        user_id: 사용자 ID (query parameter)
        db: 데이터베이스 세션
    
    Returns:
        생성된 JobPosting 객체
    
    Example:
        POST /api/job-postings/crawl?user_id={user_id}
        Body: { "url": "https://www.wanted.co.kr/wd/12345" }
    """
    # 사용자 존재 확인
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # URL 크롤링
    try:
        crawled_data = crawl_job_posting(request.url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"크롤링 실패: {str(e)}"
        )
    
    # 중복 체크 (동일한 source_url이 이미 있는지)
    existing = db.query(JobPosting).filter(
        JobPosting.user_id == user_id,
        JobPosting.source_url == crawled_data['source_url']
    ).first()
    
    if existing:
        # 기존 공고 삭제 (덮어쓰기)
        db.delete(existing)
        db.commit()
    
    # JobPosting 생성 및 저장
    db_job_posting = JobPosting(
        user_id=user_id,
        company_name=crawled_data['company_name'],
        title=crawled_data['title'],
        raw_text=crawled_data['raw_text'],
        source_url=crawled_data['source_url'],
        parsed_skills=None  # 나중에 파싱 가능
    )
    
    db.add(db_job_posting)
    db.commit()
    db.refresh(db_job_posting)
    
    # Gemini로 구조화된 JSON 파싱
    try:
        structured_json = gemini_service.parse_job_posting(
            raw_text=crawled_data['raw_text'],
            company_name=crawled_data['company_name'],
            position=crawled_data['title'],
            source_url=crawled_data['source_url']
        )
        
        # DB에 JSON 문자열로 저장 (parsed_skills 필드 활용)
        db_job_posting.parsed_skills = json.dumps(structured_json, ensure_ascii=False)
        db.commit()
        
    except Exception as e:
        print(f"⚠️ JSON 파싱/저장 실패 (계속 진행): {str(e)}")
        # 파싱 실패해도 DB 저장은 완료되었으므로 계속 진행
    
    return db_job_posting


@router.get("/{job_posting_id}", response_model=JobPostingResponse)
def get_job_posting(job_posting_id: str, db: Session = Depends(get_db)):
    """Get job posting by ID"""
    db_job_posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()
    if not db_job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
    return db_job_posting


@router.get("/user/{user_id}", response_model=List[JobPostingResponse])
def list_user_job_postings(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all job postings for a user"""
    job_postings = db.query(JobPosting).filter(
        JobPosting.user_id == user_id
    ).offset(skip).limit(limit).all()
    return job_postings


@router.delete("/{job_posting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_posting(job_posting_id: str, db: Session = Depends(get_db)):
    """Delete a job posting"""
    db_job_posting = db.query(JobPosting).filter(JobPosting.id == job_posting_id).first()
    if not db_job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
    db.delete(db_job_posting)
    db.commit()
    return None
