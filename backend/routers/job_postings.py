from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import JobPosting, User
from schemas import JobPostingCreate, JobPostingResponse

router = APIRouter()


@router.post("/", response_model=JobPostingResponse, status_code=status.HTTP_201_CREATED)
def create_job_posting(
    job_posting: JobPostingCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Create a new job posting for a user"""
    # Verify user exists
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db_job_posting = JobPosting(
        user_id=user_id,
        company_name=job_posting.company_name,
        title=job_posting.title,
        raw_text=job_posting.raw_text,
        source_url=job_posting.source_url,
        parsed_skills=job_posting.parsed_skills
    )
    db.add(db_job_posting)
    db.commit()
    db.refresh(db_job_posting)
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
