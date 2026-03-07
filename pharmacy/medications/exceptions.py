"""
pharmacy/medications/exceptions.py
─────────────────────────────────────────────────────────────────────────
Two-tier exception hierarchy:

  Tier 1 — Domain exceptions (no FastAPI dependency).
    • Raised by service.py.
    • Safe to unit-test without spinning up a FastAPI app.

  Tier 2 — HTTP exceptions (FastAPI HTTPException subclasses).
    • Re-raised (or caught and re-raised) by router.py.
    • Maps domain errors to structured HTTP responses.

Rule: service.py ONLY raises Tier 1.
      router.py catches Tier 1 and raises the matching Tier 2,
      OR uses FastAPI's exception_handler to do it automatically.
"""

from fastapi import HTTPException, status


# ════════════════════════════════════════════════════════════════════════
# TIER 1 — Domain exceptions (no FastAPI, importable from service.py)
# ════════════════════════════════════════════════════════════════════════

class MedicationDomainError(Exception):
    """Base class for all medication domain errors."""


class MedicationNotFound(MedicationDomainError):
    """Raised when a medication record cannot be located by ID."""
    def __init__(self, medication_id: int):
        self.medication_id = medication_id
        super().__init__(f"Medication with ID {medication_id} not found.")


class MedicationAlreadyExists(MedicationDomainError):
    """Raised when a (name, generic_name) pair already exists."""
    def __init__(self, name: str, generic_name: str):
        self.name = name
        self.generic_name = generic_name
        super().__init__(
            f"A medication named '{name}' with generic name "
            f"'{generic_name}' already exists."
        )


class InvalidStockQuantity(MedicationDomainError):
    """Raised when a stock quantity update would result in a negative value."""
    def __init__(self, requested: int):
        self.requested = requested
        super().__init__(
            f"Stock quantity cannot be negative. Requested: {requested}."
        )


class InvalidTherapeuticCategory(MedicationDomainError):
    """Raised when the provided therapeutic_category_id does not exist."""
    def __init__(self, category_id: int):
        self.category_id = category_id
        super().__init__(f"Therapeutic category with ID {category_id} not found.")


# ════════════════════════════════════════════════════════════════════════
# TIER 2 — HTTP exceptions (FastAPI-specific, for router.py only)
# ════════════════════════════════════════════════════════════════════════

class MedicationNotFoundException(HTTPException):
    """HTTP 404 — maps from MedicationNotFound domain exception."""
    def __init__(self, medication_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication with ID {medication_id} not found.",
        )


class MedicationConflictException(HTTPException):
    """HTTP 409 — maps from MedicationAlreadyExists domain exception."""
    def __init__(self, name: str, generic_name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"A medication named '{name}' with generic name "
                f"'{generic_name}' already exists."
            ),
        )


class InvalidStockException(HTTPException):
    """HTTP 422 — maps from InvalidStockQuantity domain exception."""
    def __init__(self, requested: int):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Stock quantity cannot be negative. Requested: {requested}.",
        )


class InvalidTherapeuticCategoryException(HTTPException):
    """HTTP 422 — maps from InvalidTherapeuticCategory domain exception."""
    def __init__(self, category_id: int):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Therapeutic category with ID {category_id} not found.",
        )
