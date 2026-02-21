"""
models.py
---------
Single Responsibility: Define the SQLAlchemy ORM model(s).
Each class here maps 1-to-1 to a database table.

For Story 1, this file defines the `Specialty` model,
which corresponds to the `specialties` table in the SQLite database.

Imported by: crud.py (to query the table), main.py (so Base knows to create the table)
Imports from: app.database (to inherit from Base)

Why separate from schemas.py?
  - models.py speaks to the DATABASE (SQLAlchemy)
  - schemas.py speaks to the CLIENT (Pydantic/JSON)
  Mixing them would couple your DB structure to your API contract — a violation
  of the Single Responsibility Principle and a common source of bugs.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class Specialty(Base):
    """
    ORM model for the `specialties` table.

    Columns:
        id          - Auto-incremented primary key
        name        - Name of the medical specialty (e.g., "Cardiology")
                      Must be unique — no two specialties can share the same name
        description - Optional long-form description of what the specialty covers
        created_at  - Timestamp set automatically by the database on INSERT
    """

    __tablename__ = "specialties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
