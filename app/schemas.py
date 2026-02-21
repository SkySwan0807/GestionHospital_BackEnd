"""
schemas.py
----------
Single Responsibility: Define Pydantic v2 models for the API contract.

These schemas serve two purposes:
  1. REQUEST validation  — FastAPI uses them to parse and validate incoming JSON
  2. RESPONSE serialization — FastAPI uses them to shape outgoing JSON

For Story 1, we define three schemas:
  - SpecialtyBase    : Shared fields between create and response
  - SpecialtyCreate  : What the client sends in a POST request (input)
  - SpecialtyResponse: What the server sends back (output)

Imported by: crud.py (parameter types), routers/specialties.py (endpoint annotations)
Imports from: Nothing in this project — only from pydantic

Why separate from models.py?
  ORM models (models.py) describe HOW data is stored.
  Pydantic schemas (schemas.py) describe HOW data is communicated.
  They evolve independently. For example, you might want to hide the `created_at`
  field from the API response, or add a computed field — without touching the DB model.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SpecialtyBase(BaseModel):
    """
    Shared fields used by both input and output schemas.
    Putting common fields here avoids repeating them in every schema.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the medical specialty (e.g., 'Cardiology')",
        examples=["Cardiology"],
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional description of what this specialty covers",
        examples=["Diagnosis and treatment of heart diseases"],
    )


class SpecialtyCreate(SpecialtyBase):
    """
    Schema for POST /specialties requests.
    Inherits name and description from SpecialtyBase.
    The client does NOT send id or created_at — those are set by the server/DB.
    """

    pass  # No additional fields needed beyond SpecialtyBase


class SpecialtyResponse(SpecialtyBase):
    """
    Schema for API responses (GET and POST responses).
    Extends SpecialtyBase with server-generated fields: id and created_at.

    model_config with from_attributes=True (Pydantic v2 equivalent of orm_mode=True)
    tells Pydantic it can read data from SQLAlchemy ORM objects, not just plain dicts.
    Without this, Pydantic would fail to serialize ORM model instances.
    """

    id: int = Field(description="Auto-generated unique identifier")
    created_at: datetime = Field(description="Timestamp of when the specialty was created")

    model_config = {"from_attributes": True}
