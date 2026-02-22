"""
database.py
-----------
Single Responsibility: Own ALL database connection concerns.

This is the INFRASTRUCTURE LAYER of the project. It is the foundation that
every other file depends on. It does exactly three things:

  1. Creates the ENGINE     → the one persistent connection to the DB file
  2. Creates SessionLocal   → a factory that stamps out sessions (conversations)
  3. Creates Base           → the parent class that all ORM models inherit from

Additionally it provides:
  4. get_db()               → a FastAPI dependency that opens/closes sessions safely

Who imports from this file?
  - app/models.py              imports Base
  - app/main.py                imports Base, engine  (to create tables on startup)
  - app/routers/specialties.py imports get_db        (via FastAPI Depends())
  - tests/test_specialties.py  imports Base, engine, get_db (to override with test DB)
"""

# ============================================================================
# IMPORTS
# ============================================================================
from sqlalchemy import create_engine          # Builds the engine (DB connection)
from sqlalchemy.orm import sessionmaker        # Builds the session factory
from sqlalchemy.orm import declarative_base    # Builds the Base class for ORM models
from dotenv import load_dotenv                 # Reads .env file into os.environ
import os

# Load .env variables into the environment BEFORE reading them
# This means DATABASE_URL= in .env becomes available via os.getenv()
load_dotenv()

# ============================================================================
# STEP 1 — THE ENGINE
# ============================================================================
# Read the database URL from the .env file.
# Default fallback: "sqlite:///./hospital.db"
#
# URL anatomy for SQLite:
#   sqlite://     → dialect+driver (SQLite needs no separate driver)
#   /             → absolute path separator (3 slashes = relative path)
#   ./hospital.db → relative to wherever you launch uvicorn from
#                   (i.e., the project root folder)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hospital.db")

engine = create_engine(
    DATABASE_URL,
    # WHY connect_args={"check_same_thread": False}?
    # SQLite was designed for single-threaded use. By default it raises an error
    # if the same connection is used from a different thread than the one that
    # created it. FastAPI, however, runs request handlers in a thread pool.
    # Setting check_same_thread=False tells SQLite: "I'll manage thread safety
    # myself (via scoped sessions), so you don't need to enforce this."
    # This argument is ONLY needed for SQLite. PostgreSQL/MySQL don't need it.
    connect_args={"check_same_thread": False},
)

# ============================================================================
# STEP 2 — THE SESSION FACTORY (SessionLocal)
# ============================================================================
# sessionmaker() is a FACTORY — a class that, when called, produces Session objects.
# Think of it like a cookie cutter: each call to SessionLocal() stamps out a
# fresh, independent Session (conversation) with the database.
SessionLocal = sessionmaker(
    bind=engine,
    # autocommit=False → Changes are NOT written to disk automatically.
    # You must explicitly call db.commit() to persist them.
    # This gives you transactional control: if something fails mid-operation,
    # you can call db.rollback() and nothing is saved — it's all-or-nothing.
    autocommit=False,
    # autoflush=False → SQLAlchemy will NOT automatically send pending SQL
    # statements to the DB before every query. This prevents unexpected
    # intermediate writes and gives you control over when SQL is actually sent.
    autoflush=False,
)

# ============================================================================
# STEP 3 — THE DECLARATIVE BASE
# ============================================================================
# declarative_base() returns a Base class.
# Every ORM model in this project (e.g., Specialty in models.py) will inherit
# from this Base. When a class inherits from Base, SQLAlchemy registers it
# internally and knows its table name and column definitions.
#
# Base.metadata is a registry object that tracks all registered models.
# When main.py calls Base.metadata.create_all(bind=engine), SQLAlchemy
# iterates over every registered model and issues:
#   CREATE TABLE IF NOT EXISTS specialties (...);
# for each one that doesn't already exist in the database.
Base = declarative_base()


# ============================================================================
# STEP 4 — THE FastAPI DB DEPENDENCY: get_db()
# ============================================================================
def get_db():
    """
    FastAPI dependency that provides a database session for a single request.

    This is a Python GENERATOR function (note the `yield`).
    FastAPI's Depends() system calls it, receives the session via yield,
    injects it into the endpoint handler, and then — when the request is done
    (success OR exception) — resumes the generator which runs the finally block.

    The finally block guarantees db.close() is ALWAYS called, even if an
    unhandled exception crashes the endpoint. This prevents connection leaks.

    Usage in a router (routers/specialties.py):
        @router.post("/")
        def create_specialty(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()   # Open a new session (start a conversation)
    try:
        yield db          # Hand the session to the endpoint handler
    finally:
        db.close()        # Always close, no matter what
