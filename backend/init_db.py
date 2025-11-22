from database import engine, Base
from models import (
    User,
    Portfolio,
    JobPosting,
    InterviewSession,
    InterviewQuestion,
    InterviewVideo,
    InterviewTranscript,
    NonverbalMetrics,
    NonverbalTimeline,
    Feedback
)


def init_db():
    """Initialize database with all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def drop_db():
    """Drop all database tables"""
    print("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_db()
    else:
        init_db()
