"""
pharmacy/medications/schemas.py
─────────────────────────────────────────────────────────────────────────
Pydantic validation and serialization layer.

Rules:
  • No ORM imports — schemas are independent of SQLAlchemy.
  • Restricted fields (id, created_at, updated_at) are NEVER writable;
    they are absent from Create/Update schemas by design.
  • price uses Decimal (not float) to match Numeric(10, 2) in the model.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


# ── Shared base (fields common to Create and Response) ────────────────────
class MedicationBase(BaseModel):
    name: str = Field(..., max_length=200, description="Brand / trade name")
    generic_name: str = Field(..., max_length=200, description="INN / active ingredient")
    dosage: str = Field(..., max_length=100, description="e.g. '500 mg', '10 mg/5 ml'")
    unit: Optional[str] = Field(None, max_length=20, description="e.g. 'tablet', 'ml'")
    description: Optional[str] = Field(None, max_length=500)
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Unit price (non-zero)")
    stock_quantity: int = Field(default=0, ge=0)
    min_stock_threshold: int = Field(default=0, ge=0)
    therapeutic_category_id: Optional[int] = None
    expiration_date: Optional[date] = None
    is_active: bool = Field(default=True)


# ── Create schema ─────────────────────────────────────────────────────────
class MedicationCreate(MedicationBase):
    """All required and optional fields for a new medication record."""
    pass


# ── Update schema (all fields optional; restricted fields omitted) ─────────
class MedicationUpdate(BaseModel):
    """
    Partial update payload.

    Fields NOT listed here cannot be modified via PATCH:
      - id, created_at, updated_at  → system-managed, never caller-settable
      - stock_quantity               → use the dedicated stock endpoint instead

    All listed fields are optional so PATCH can be used for single-field edits.
    """
    name: Optional[str] = Field(None, max_length=200)
    generic_name: Optional[str] = Field(None, max_length=200)
    dosage: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    min_stock_threshold: Optional[int] = Field(None, ge=0)
    therapeutic_category_id: Optional[int] = None
    expiration_date: Optional[date] = None
    is_active: Optional[bool] = None


# ── Response schema ───────────────────────────────────────────────────────
class MedicationResponse(MedicationBase):
    """Read-only projection returned by all GET and write endpoints."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}  # Pydantic v2 (replaces orm_mode)
