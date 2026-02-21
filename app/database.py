"""
database.py
-----------
Single Responsibility: Own ALL database connection concerns.
- Creates the SQLAlchemy engine (backed by SQLite via DATABASE_URL from .env)
- Creates the SessionLocal factory (one session per request)
- Exposes Base (declarative base) so models.py can define ORM classes
- Provides the get_db() dependency used by FastAPI routers via Depends()

Imported by: main.py, models.py, routers/specialties.py, tests/test_specialties.py
Imports from: .env (DATABASE_URL via pydantic-settings / python-dotenv)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read the database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hospital.db")

# Create the SQLAlchemy engine
# connect_args={"check_same_thread": False} is required for SQLite only
# (SQLite connections are not thread-safe by default; FastAPI runs in threads)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# SessionLocal: a factory that produces database sessions
# Each request gets its own session, which is opened and closed via get_db()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: the declarative base class all ORM models will inherit from
# When Base.metadata.create_all(bind=engine) is called in main.py,
# SQLAlchemy inspects all subclasses of Base and creates their tables
Base = declarative_base()


# ---------------------------------------------------------------------------
# FastAPI Dependency: get_db()
# ---------------------------------------------------------------------------
# This generator function is used with FastAPI's Depends() system.
# It yields a database session and guarantees the session is closed
# even if an exception occurs (the finally block always runs).
#
# Usage in a router:
#   def some_endpoint(db: Session = Depends(get_db)):
#       ...
# ---------------------------------------------------------------------------
def get_db():
    """Yield a database session, then close it when the request is done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
