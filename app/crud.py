"""
crud.py
-------
Single Responsibility: Contain ALL database operations for the Specialty resource.
(CRUD = Create, Read, Update, Delete)

This is the DATA ACCESS LAYER (also called Repository pattern).
Functions here:
  - Accept a SQLAlchemy session (db) as their first argument
  - Accept Pydantic schema objects as input data
  - Execute ORM queries against the Specialty model
  - Return ORM model instances (which FastAPI then serializes via schemas)

Imported by: routers/specialties.py (calls these functions from endpoint handlers)
Imports from: app.models (Specialty ORM class), app.schemas (SpecialtyCreate schema)

Why separate from routers/specialties.py?
  Routers handle HTTP concerns (status codes, request/response shapes).
  CRUD handles DATA concerns (SQL queries, transactions).
  This separation means you could swap SQLite for PostgreSQL by only changing
  crud.py — routers would not need to change at all.
"""

from sqlalchemy.orm import Session
from app.models import Specialty
from app.schemas import SpecialtyCreate


def get_specialty_by_name(db: Session, name: str) -> Specialty | None:
    """
    Query the database for a specialty by its exact name.

    Used by create_specialty() to check for duplicates before inserting.

    Args:
        db   : Active SQLAlchemy database session
        name : The specialty name to look up

    Returns:
        The Specialty ORM instance if found, or None if not found
    """
    return db.query(Specialty).filter(Specialty.name == name).first()


def get_specialty(db: Session, specialty_id: int) -> Specialty | None:
    """
    Query the database for a single specialty by its primary key (id).

    Args:
        db           : Active SQLAlchemy database session
        specialty_id : The integer primary key to look up

    Returns:
        The Specialty ORM instance if found, or None if not found
    """
    return db.query(Specialty).filter(Specialty.id == specialty_id).first()


def get_specialties(db: Session, skip: int = 0, limit: int = 100) -> list[Specialty]:
    """
    Query the database for a paginated list of all specialties.

    Pagination is implemented via OFFSET (skip) and LIMIT (limit).
    Default: returns the first 100 specialties.

    Args:
        db    : Active SQLAlchemy database session
        skip  : Number of records to skip (for pagination, default 0)
        limit : Maximum number of records to return (default 100)

    Returns:
        A list of Specialty ORM instances (may be empty if table is empty)

    SQL equivalent:
        SELECT * FROM specialties ORDER BY id LIMIT limit OFFSET skip;
    """
    return db.query(Specialty).offset(skip).limit(limit).all()


def create_specialty(db: Session, specialty: SpecialtyCreate) -> Specialty:
    """
    Insert a new specialty record into the database.

    Steps:
      1. Instantiate a Specialty ORM object from the Pydantic schema data
      2. Add it to the session (marks it for INSERT)
      3. Commit the transaction (writes to the DB file)
      4. Refresh the instance (re-reads the row from DB to get id, created_at)
      5. Return the refreshed ORM instance

    Args:
        db        : Active SQLAlchemy database session
        specialty : Validated SpecialtyCreate Pydantic object from the request body

    Returns:
        The newly created Specialty ORM instance with id and created_at populated

    Note:
        Duplicate name checking is done in the router BEFORE calling this function.
        This function assumes the name is already confirmed to be unique.
    """
    db_specialty = Specialty(
        name=specialty.name,
        description=specialty.description,
    )
    db.add(db_specialty)
    db.commit()
    db.refresh(db_specialty)
    return db_specialty
