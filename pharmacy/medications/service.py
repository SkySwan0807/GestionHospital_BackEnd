"""
pharmacy/medications/service.py
─────────────────────────────────────────────────────────────────────────
Business logic layer for the medications module.

Architectural rules enforced here:
  • No FastAPI imports — this layer is web-framework-agnostic.
  • No raw SQL strings — SQLAlchemy ORM only.
  • No print() — all observability goes through the logging module.
  • Raises ONLY Tier 1 domain exceptions from exceptions.py.
  • router.py is responsible for catching domain exceptions and mapping
    them to Tier 2 HTTP exceptions.

Immutable fields (never written to by update operations):
  _IMMUTABLE_FIELDS = {"id", "created_at", "updated_at"}
"""

import logging
from typing import List

from sqlalchemy.orm import Session

from pharmacy.medications.exceptions import (
    InvalidStockQuantity,
    MedicationAlreadyExists,
    MedicationNotFound,
    InvalidTherapeuticCategory,
)
from pharmacy.medications.model import Medication
from pharmacy.medications.category_model import TherapeuticCategory
from pharmacy.medications.schemas import MedicationCreate, MedicationUpdate

logger = logging.getLogger(__name__)

# Fields that must never be overwritten by caller-supplied data.
# Acts as a belt-and-suspenders guard even if the schema were to change.
_IMMUTABLE_FIELDS: frozenset = frozenset({"id", "created_at", "updated_at"})


# ── Create ────────────────────────────────────────────────────────────────

def create_medication(db: Session, medication_in: MedicationCreate) -> Medication:
    """
    Create and persist a new medication record.

    Performs a service-level duplicate check on (name, generic_name) before
    attempting the INSERT. This gives callers a structured domain error
    instead of a raw IntegrityError from the DB layer.

    The DB-level UniqueConstraint remains as a safety net for concurrent
    writes that race past this check.

    Args:
        db:            Active SQLAlchemy session (injected via get_db).
        medication_in: Validated creation payload from MedicationCreate schema.

    Returns:
        The newly created and DB-refreshed Medication ORM instance.

    Raises:
        MedicationAlreadyExists: If a record with the same (name, generic_name)
                                 already exists in the medications table.
    """
    logger.info(
        "Attempting to create medication: name=%r, generic_name=%r",
        medication_in.name,
        medication_in.generic_name,
    )

    # Service-level duplicate check — gives a meaningful error before the DB
    # constraint fires. Checks both fields case-sensitively (adjust with
    # func.lower() for case-insensitive matching if required).
    existing = (
        db.query(Medication)
        .filter(
            Medication.name == medication_in.name,
            Medication.generic_name == medication_in.generic_name,
        )
        .first()
    )
    if existing:
        logger.warning(
            "Duplicate medication rejected: name=%r, generic_name=%r",
            medication_in.name,
            medication_in.generic_name,
        )
        raise MedicationAlreadyExists(medication_in.name, medication_in.generic_name)

    if medication_in.therapeutic_category_id is not None:
        category = db.get(TherapeuticCategory, medication_in.therapeutic_category_id)
        if not category:
            logger.warning(
                "Invalid therapeutic category: id=%d",
                medication_in.therapeutic_category_id,
            )
            raise InvalidTherapeuticCategory(medication_in.therapeutic_category_id)

    db_medication = Medication(**medication_in.model_dump())
    db.add(db_medication)
    db.commit()
    db.refresh(db_medication)

    logger.info("Medication created successfully: id=%d", db_medication.id)
    return db_medication


# ── Read (single) ─────────────────────────────────────────────────────────

def get_medication_by_id(db: Session, medication_id: int) -> Medication:
    """
    Retrieve a single medication by its primary key.

    Args:
        db:            Active SQLAlchemy session.
        medication_id: Integer PK of the medication to retrieve.

    Returns:
        The matching Medication ORM instance.

    Raises:
        MedicationNotFound: If no record with the given ID exists.
    """
    logger.debug("Fetching medication by id=%d", medication_id)

    medication = db.get(Medication, medication_id)
    if medication is None:
        logger.warning("Medication not found: id=%d", medication_id)
        raise MedicationNotFound(medication_id)

    return medication


# ── Read (list) ───────────────────────────────────────────────────────────

def get_all_medications(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Medication]:
    """
    Return a paginated list of ACTIVE medications (is_active=True).

    Inactive (soft-deleted) medications are excluded. Clients that need
    to query inactive records must call a separate admin-scoped endpoint.

    Args:
        db:    Active SQLAlchemy session.
        skip:  Number of records to skip (offset). Default: 0.
        limit: Maximum number of records to return. Default: 100.

    Returns:
        List of active Medication ORM instances, ordered by id ascending.
    """
    logger.debug("Fetching active medications: skip=%d, limit=%d", skip, limit)

    return (
        db.query(Medication)
        .filter(Medication.is_active.is_(True))
        .order_by(Medication.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


# ── Update (stock only) ───────────────────────────────────────────────────

def update_medication_stock(
    db: Session, medication_id: int, new_quantity: int
) -> Medication:
    """
    Set the stock_quantity of a medication to a specific absolute value.

    This is a direct assignment (not a delta), so the caller must have
    already computed the desired final quantity. For delta operations
    (increment/decrement), the router or caller is responsible for
    fetching the current quantity and computing the new value.

    Args:
        db:            Active SQLAlchemy session.
        medication_id: PK of the medication to update.
        new_quantity:  Target stock quantity. Must be >= 0.

    Returns:
        The updated Medication ORM instance.

    Raises:
        MedicationNotFound:   If no record with the given ID exists.
        InvalidStockQuantity: If new_quantity is negative.
    """
    logger.info(
        "Updating stock: medication_id=%d, new_quantity=%d",
        medication_id,
        new_quantity,
    )

    if new_quantity < 0:
        logger.warning(
            "Rejected negative stock update: medication_id=%d, requested=%d",
            medication_id,
            new_quantity,
        )
        raise InvalidStockQuantity(new_quantity)

    medication = get_medication_by_id(db, medication_id)
    medication.stock_quantity = new_quantity
    db.commit()
    db.refresh(medication)

    logger.info(
        "Stock updated: medication_id=%d, new_quantity=%d",
        medication.id,
        medication.stock_quantity,
    )
    return medication


# ── Update (general PATCH) ────────────────────────────────────────────────

def update_medication(
    db: Session, medication_id: int, medication_in: MedicationUpdate
) -> Medication:
    """
    Partially update a medication record with caller-supplied fields.

    Only fields explicitly set by the caller (exclude_unset=True) are
    applied. Any field in _IMMUTABLE_FIELDS is silently skipped even
    if it somehow appears in the payload (belt-and-suspenders guard).

    Args:
        db:            Active SQLAlchemy session.
        medication_id: PK of the medication to update.
        medication_in: Partial update payload; unset fields are ignored.

    Returns:
        The updated Medication ORM instance.

    Raises:
        MedicationNotFound:   If no record with the given ID exists.
        MedicationAlreadyExists: If changing name/generic_name would
                                 create a duplicate (name, generic_name) pair.
    """
    logger.info("Updating medication: id=%d", medication_id)

    medication = get_medication_by_id(db, medication_id)
    update_data = medication_in.model_dump(exclude_unset=True)

    # Check for duplicate (name, generic_name) if either field is being changed.
    incoming_name = update_data.get("name", medication.name)
    incoming_generic = update_data.get("generic_name", medication.generic_name)
    if incoming_name != medication.name or incoming_generic != medication.generic_name:
        conflict = (
            db.query(Medication)
            .filter(
                Medication.name == incoming_name,
                Medication.generic_name == incoming_generic,
                Medication.id != medication_id,
            )
            .first()
        )
        if conflict:
            raise MedicationAlreadyExists(incoming_name, incoming_generic)

    if "therapeutic_category_id" in update_data and update_data["therapeutic_category_id"] is not None:
        category = db.get(TherapeuticCategory, update_data["therapeutic_category_id"])
        if not category:
            logger.warning(
                "Invalid therapeutic category: id=%d",
                update_data["therapeutic_category_id"],
            )
            raise InvalidTherapeuticCategory(update_data["therapeutic_category_id"])

    for field, value in update_data.items():
        if field in _IMMUTABLE_FIELDS:
            logger.warning(
                "Attempted write to immutable field %r on medication id=%d — skipped.",
                field,
                medication_id,
            )
            continue
        setattr(medication, field, value)

    db.commit()
    db.refresh(medication)

    logger.info("Medication updated: id=%d", medication.id)
    return medication


# ── Low-stock query ───────────────────────────────────────────────────────

def get_low_stock_medications(db: Session) -> List[Medication]:
    """
    Return all ACTIVE medications where stock is at or below their threshold.

    This is a single DB-side filter — no Python-level looping over all
    records. The compound filter is evaluated entirely in SQLite.

    Medications with min_stock_threshold=0 are excluded (0 means alerting
    is not configured for that medication), preventing false positives when
    stock is intentionally zero.

    Args:
        db: Active SQLAlchemy session.

    Returns:
        List of Medication ORM instances ordered by stock_quantity ascending
        (most critical first).
    """
    logger.debug("Fetching low-stock medications")

    results = (
        db.query(Medication)
        .filter(
            Medication.is_active.is_(True),
            Medication.min_stock_threshold > 0,  # only alerting-configured records
            Medication.stock_quantity <= Medication.min_stock_threshold,
        )
        .order_by(Medication.stock_quantity.asc())
        .all()
    )

    logger.info("Low-stock query returned %d records.", len(results))
    return results

