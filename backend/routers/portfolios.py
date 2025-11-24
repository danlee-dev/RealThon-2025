from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Portfolio, User, CapabilityEvaluation
from schemas import (
    PortfolioCreate, PortfolioResponse, CVAnalysisResponse,
    CapabilityEvaluationResponse, CapabilityData, ImprovementSuggestionData
)
from services.cv_analyzer import analyze_cv_pipeline
from services.capability_evaluator import evaluate_portfolio_capabilities
from auth import get_current_user
import os
import uuid
import json
from PyPDF2 import PdfReader

router = APIRouter()

UPLOAD_DIR = "uploads/portfolios"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def upload_portfolio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a portfolio PDF file"""
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    # Validate file size (10MB max)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit"
        )

    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract text from PDF
    parsed_text = ""
    try:
        pdf_reader = PdfReader(file_path)
        for page in pdf_reader.pages:
            parsed_text += page.extract_text() + "\n"
    except Exception as e:
        # If PDF parsing fails, delete the file and raise error
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse PDF: {str(e)}"
        )

    # Create portfolio record
    db_portfolio = Portfolio(
        user_id=current_user.id,
        file_url=file_path,
        filename=file.filename,
        parsed_text=parsed_text,
        summary=None  # Will be generated later by AI
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)

    return db_portfolio


@router.get("/", response_model=List[PortfolioResponse])
def list_my_portfolios(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all portfolios for the current authenticated user"""
    portfolios = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return portfolios


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio: PortfolioCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Create a new portfolio for a user"""
    # Verify user exists
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db_portfolio = Portfolio(
        user_id=user_id,
        file_url=portfolio.file_url,
        filename=portfolio.filename,
        parsed_text=portfolio.parsed_text,
        summary=portfolio.summary
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
def get_portfolio(portfolio_id: str, db: Session = Depends(get_db)):
    """Get portfolio by ID"""
    db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not db_portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    return db_portfolio


@router.get("/user/{user_id}", response_model=List[PortfolioResponse])
def list_user_portfolios(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all portfolios for a user"""
    portfolios = db.query(Portfolio).filter(
        Portfolio.user_id == user_id
    ).offset(skip).limit(limit).all()
    return portfolios


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(portfolio_id: str, db: Session = Depends(get_db)):
    """Delete a portfolio"""
    db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not db_portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    db.delete(db_portfolio)
    db.commit()
    return None


@router.post("/{portfolio_id}/analyze", response_model=CVAnalysisResponse)
def analyze_portfolio_cv(
    portfolio_id: str,
    user_id: str,
    role: Optional[str] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze portfolio CV and extract skills, strengths, weaknesses

    Args:
        portfolio_id: Portfolio ID
        user_id: User ID
        role: Optional role override (defaults to user's role)
        level: Optional level override (defaults to user's level)

    Returns:
        CV analysis result with skills, strengths, weaknesses, and overall score
    """
    try:
        result = analyze_cv_pipeline(
            portfolio_id=portfolio_id,
            user_id=user_id,
            db=db,
            role=role,
            level=level
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CV 분석 중 오류 발생: {str(e)}"
        )


@router.post("/{portfolio_id}/capabilities/generate")
def generate_portfolio_capabilities(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gemini를 사용하여 포트폴리오 역량 평가 생성

    portfolio.summary (CV + GitHub 분석)를 기반으로 6개 역량 평가 자동 생성

    Args:
        portfolio_id: Portfolio ID
        current_user: 현재 로그인한 유저

    Returns:
        생성된 역량 평가 결과
    """
    # 1. Portfolio 조회
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # 2. 권한 확인
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # 3. Gemini로 역량 평가 생성
    try:
        result = evaluate_portfolio_capabilities(
            portfolio_id=portfolio_id,
            user_id=current_user.id,
            db=db
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"역량 평가 생성 실패: {str(e)}")


@router.get("/{portfolio_id}/capabilities", response_model=CapabilityEvaluationResponse)
def get_portfolio_capabilities(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    포트폴리오의 역량 평가 결과 조회 (스파이더 차트용)

    6개 역량 카테고리와 점수, 개선 제안을 반환
    역량 평가가 없으면 404 에러 (먼저 /generate 호출 필요)

    Args:
        portfolio_id: Portfolio ID
        current_user: 현재 로그인한 유저

    Returns:
        {
            "capabilities": [{"skill": "Technical Skills", "value": 85, "skill_ko": "기술 역량"}, ...],
            "improvement_suggestions": [...]
        }
    """
    # 1. Portfolio 조회
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # 2. 권한 확인
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # 3. 역량 평가 조회
    evaluation = db.query(CapabilityEvaluation).filter(
        CapabilityEvaluation.portfolio_id == portfolio_id
    ).first()

    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail="역량 평가 데이터가 없습니다. POST /api/portfolios/{portfolio_id}/capabilities/generate를 먼저 호출하세요."
        )

    # 4. 응답 데이터 생성
    capabilities = []
    improvement_suggestions = []

    for i in range(1, 7):
        name_en = getattr(evaluation, f"capability{i}_name_en")
        name_ko = getattr(evaluation, f"capability{i}_name_ko")
        score = getattr(evaluation, f"capability{i}_score")
        reason = getattr(evaluation, f"capability{i}_reason")
        feedback = getattr(evaluation, f"capability{i}_feedback")

        # Capability 데이터
        capabilities.append(CapabilityData(
            skill=name_en,
            value=score,
            skill_ko=name_ko
        ))

        # 낮은 점수(80점 미만)면 개선 제안 추가
        if score < 80:
            improvement_suggestions.append(ImprovementSuggestionData(
                id=f"{evaluation.id}_{i}",
                capability=name_en,
                capability_ko=name_ko,
                currentScore=score,
                title=f"{name_ko} 역량 강화 방안",
                description=feedback,
                actionItems=[
                    f"{name_ko} 관련 온라인 강의 수강",
                    f"{name_ko} 실무 프로젝트 경험 쌓기",
                    f"{name_ko} 관련 기술 블로그 작성"
                ]
            ))

    return CapabilityEvaluationResponse(
        capabilities=capabilities,
        improvement_suggestions=improvement_suggestions
    )
