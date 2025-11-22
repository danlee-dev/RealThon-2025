from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Portfolio, User
from schemas import PortfolioCreate, PortfolioResponse, CVAnalysisResponse
from services.cv_analyzer import analyze_cv_pipeline
from auth import get_current_user
import os
import uuid
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
