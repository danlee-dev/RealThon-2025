from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, engine
from models import Base
import uvicorn

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Interview Practice API",
    description="API for AI-powered interview practice application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "Interview Practice API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection (SQLAlchemy 2.0 syntax)
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Include routers
from routers import users, portfolios, job_postings, interviews, video_analysis

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(portfolios.router, prefix="/api/portfolios", tags=["portfolios"])
app.include_router(job_postings.router, prefix="/api/job-postings", tags=["job-postings"])
app.include_router(interviews.router, prefix="/api/interviews", tags=["interviews"])
app.include_router(video_analysis.router, prefix="/api/video", tags=["video-analysis"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
