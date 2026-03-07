"""
pharmacy/database.py
─────────────────────────────────────────────────────────────────────────
Shared database infrastructure for the entire pharmacy application.

Rules:
  • This file owns the Engine, SessionLocal factory, and Base class.
  • It must NOT import any module-level models — models import Base from
    here, not the other way around (prevents circular imports).
  • Table creation (create_all) is intentionally absent; use Alembic
    migrations in all environments.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# ── Database URL ──────────────────────────────────────────────────────────
# Loaded from an environment variable in a real deployment.
# The file path ./hospital.db is relative to the working directory
# (i.e., the project root when running `uvicorn pharmacy.main:app`).
SQLALCHEMY_DATABASE_URL = "sqlite:///./hospital.db"

# ── Engine ────────────────────────────────────────────────────────────────
# create_engine configures the connection pool and driver.
# One engine instance is shared for the entire application lifetime.
#
# connect_args={"check_same_thread": False}
#   SQLite's default behaviour is to raise an error if a connection
#   object is used on a thread different from the one that created it.
#   FastAPI uses a thread-pool executor for synchronous path operations,
#   so the same connection may be handed to a different thread mid-
#   request.  Setting check_same_thread=False disables this guard.
#   This is SAFE here because SQLAlchemy's connection pool manages
#   thread ownership correctly — each request gets its own session
#   (and therefore its own connection) via the get_db() dependency.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # echo=True can be temporarily enabled for SQL query logging during
    # local debugging. Never enable in production (leaks query params).
    echo=False,
)

# ── Enable SQLite foreign key enforcement ─────────────────────────────────
# SQLite does NOT enforce FK constraints by default.
# This event listener fires "PRAGMA foreign_keys = ON" at every new
# connection, enforcing referential integrity at the DB level in addition
# to SQLAlchemy's ORM-level validation.
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# ── Session factory ───────────────────────────────────────────────────────
# sessionmaker returns a *class* (SessionLocal), not a session.
# Each call to SessionLocal() produces a new, independent Session object
# that tracks ORM object state and manages one database transaction.
#
# autocommit=False  → transactions must be explicitly committed.
#                     Prevents accidental partial writes from being saved.
# autoflush=False   → SQLAlchemy will not automatically emit SQL when
#                     accessing a relationship before a commit.
#                     Controlled flushing avoids surprises in service code.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ── Declarative base ──────────────────────────────────────────────────────
# All ORM models inherit from this Base.
# Base.metadata tracks every mapped table so Alembic can diff the schema.
# Shared across ALL modules — do not create a second Base in any module.
Base = declarative_base()


# ── FastAPI dependency ────────────────────────────────────────────────────
def get_db():
    """
    Yield a database session scoped to a single HTTP request.

    Opens a session → yields it to the route handler → guarantees
    closure in the `finally` block regardless of whether the handler
    raised an exception.  The caller (service layer) is responsible
    for commit/rollback; this function only manages the session
    lifecycle.

    Usage:
        @router.get("/")
        def list_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

