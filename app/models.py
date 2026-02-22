"""
models.py
---------
Single Responsibility: Define the SQLAlchemy ORM model(s) for this service.

Each class in this file maps 1-to-1 to a database TABLE.
Each class attribute maps 1-to-1 to a database COLUMN.

For Story 1, we define one model: Specialty
  → maps to the `specialties` table in hospital.db

Imported by:
  - app/main.py   → so Base.metadata knows to create the specialties table
  - app/crud.py   → to run ORM queries (SELECT, INSERT) against Specialty

Imports from:
  - app.database  → Base (the declarative parent class)
  - sqlalchemy    → Column, Integer, String, Text, DateTime, func
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class Specialty(Base):
    """
    ORM model representing the `specialties` table.

    This class IS the table definition. SQLAlchemy reads it and generates
    the SQL needed to create the table and to build queries against it.

    Columns
    -------
    id          : Auto-incrementing integer primary key (server-generated)
    name        : Required, unique specialty name  (e.g. "Cardiology")
    description : Optional long-form text description (can be NULL/None)
    created_at  : Timestamp set automatically by the DB on every INSERT
    """

    # ------------------------------------------------------------------
    # __tablename__
    # The name of the physical table in the SQLite database.
    # SQLAlchemy uses this string when it generates:
    #   CREATE TABLE specialties (...)
    #   SELECT * FROM specialties
    #   INSERT INTO specialties (...)
    # ------------------------------------------------------------------
    __tablename__ = "specialties"

    # ------------------------------------------------------------------
    # COLUMN 1 — id
    # Type    : Integer
    # Role    : Primary Key (uniquely identifies every row)
    # Behavior: Auto-increments — SQLite assigns 1, 2, 3... automatically
    # index=True: SQLAlchemy creates a separate B-tree index on this column
    #             (primary keys are always indexed, but explicit is clearer)
    # ------------------------------------------------------------------
    id = Column(Integer, primary_key=True, index=True)

    # ------------------------------------------------------------------
    # COLUMN 2 — name
    # Type    : String(100) → maps to VARCHAR(100) in SQL
    # Role    : The human-readable specialty name ("Cardiology", etc.)
    # Rules:
    #   unique=True   → the DB enforces that no two rows share the same name
    #   nullable=False → the DB REJECTS an INSERT that omits this column
    #   index=True    → creates a B-tree index for fast name lookups
    # ------------------------------------------------------------------
    name = Column(String(100), unique=True, nullable=False, index=True)

    # ------------------------------------------------------------------
    # COLUMN 3 — description
    # Type    : Text → maps to TEXT in SQL (unlimited length string)
    # Role    : Optional long description of what the specialty covers
    # Rules:
    #   nullable=True → NULL is allowed; Python `None` becomes SQL NULL
    # Note: nullable=True is the DEFAULT in SQLAlchemy, shown explicitly
    #       here for maximum clarity.
    # ------------------------------------------------------------------
    description = Column(Text, nullable=True)

    # ------------------------------------------------------------------
    # COLUMN 4 — created_at
    # Type    : DateTime(timezone=True)
    # Role    : Audit timestamp — when was this specialty added to the catalog?
    # server_default=func.now() → the DATABASE sets this value automatically
    #   on every INSERT using its own NOW() / CURRENT_TIMESTAMP function.
    #   Python never needs to set this manually.
    # ------------------------------------------------------------------
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        """
        String representation for debugging.
        Shown when you print() a Specialty object in a Python shell or logs.
        """
        return f"<Specialty id={self.id} name='{self.name}'>"
