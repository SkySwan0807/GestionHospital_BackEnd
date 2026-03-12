from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from pharmacy.database import get_db
from pharmacy.medications import service, schemas

router = APIRouter(
    prefix="/medications",
    tags=["medications"]
)


@router.post(
    "/",
    response_model=schemas.MedicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new medication",
)
def create_medication(medication: schemas.MedicationCreate, db: Session = Depends(get_db)):
    """
    Register a new medication in the inventory.

    - **name**: Brand / trade name (required, max 200 chars).
    - **generic_name**: INN / active ingredient (required, max 200 chars).
    - **dosage**: Strength description, e.g. `"500 mg"` (required).
    - **unit**: Dispensing unit, e.g. `"tablet"` (optional).
    - **description**: Clinical notes or storage instructions (optional).
    - **price**: Unit price — must be > 0 (Decimal, e.g. `"12.50"`).
    - **stock_quantity**: Initial stock level (default: `0`).
    - **min_stock_threshold**: Reorder alert level (default: `0` = no alerting).
    - **therapeutic_category_id**: FK to therapeutic_categories table (optional).
    - **expiration_date**: Batch expiry date in `YYYY-MM-DD` format (optional).
    - **is_active**: Soft-delete flag (default: `true`).

    Returns **201 Created** with the full medication object including `id`, `created_at`, and `updated_at`.
    """
    return service.create_medication(db=db, medication_in=medication)


@router.get(
    "/",
    response_model=List[schemas.MedicationResponse],
    summary="List all active medications",
)
def read_medications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Return a paginated list of **active** medications (`is_active=True`).

    Inactive (soft-deleted) medications are excluded.

    - **skip**: Records to skip (offset). Default: `0`.
    - **limit**: Maximum records to return. Default: `100`.
    """
    return service.get_all_medications(db, skip=skip, limit=limit)


@router.get(
    "/low-stock",
    response_model=List[schemas.MedicationResponse],
    summary="List medications below their minimum stock threshold",
)
def read_low_stock_medications(db: Session = Depends(get_db)):
    """
    Return all **active** medications where `stock_quantity <= min_stock_threshold`.

    Medications with `min_stock_threshold = 0` are **excluded** (alerting not configured).
    Results are ordered by `stock_quantity` ascending (most critical first).
    """
    return service.get_low_stock_medications(db)


@router.get(
    "/{medication_id}",
    response_model=schemas.MedicationResponse,
    summary="Get a single medication by ID",
)
def read_medication(medication_id: int, db: Session = Depends(get_db)):
    """
    Retrieve one medication by its primary key.

    Raises **404 Not Found** if no medication with the given `id` exists.
    """
    return service.get_medication_by_id(db, medication_id=medication_id)


@router.patch(
    "/{medication_id}",
    response_model=schemas.MedicationResponse,
    summary="Partially update a medication",
)
def update_medication(
    medication_id: int,
    medication: schemas.MedicationUpdate,
    db: Session = Depends(get_db),
):
    """
    Partial update — only fields present in the request body are changed.

    **Fields that CANNOT be updated here**:
    - `id`, `created_at`, `updated_at` — system-managed, always read-only.
    - `stock_quantity` — use `POST /{medication_id}/stock` instead.

    Raises **404 Not Found** if the medication does not exist.
    Raises **409 Conflict** if changing `name`/`generic_name` would duplicate another record.
    """
    return service.update_medication(db, medication_id=medication_id, medication_in=medication)


@router.delete(
    "/{medication_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a medication",
)
def delete_medication(medication_id: int, db: Session = Depends(get_db)):
    """
    Hard-delete a medication record.

    > ⚠️ Consider using `PATCH /{medication_id}` with `is_active: false` for
    > soft-delete to preserve the audit trail and avoid FK cascade issues.

    Raises **404 Not Found** if the medication does not exist.
    """
    med = service.get_medication_by_id(db, medication_id=medication_id)
    db.delete(med)
    db.commit()
    return None


@router.post(
    "/{medication_id}/stock",
    response_model=schemas.MedicationResponse,
    summary="Set the stock quantity of a medication",
)
def adjust_stock(medication_id: int, quantity: int, db: Session = Depends(get_db)):
    """
    Set the `stock_quantity` to an **absolute** value.

    - **quantity**: New stock level. Must be `>= 0`.

    Raises **422 Unprocessable Entity** if `quantity` is negative.
    Raises **404 Not Found** if the medication does not exist.
    """
    return service.update_medication_stock(db, medication_id=medication_id, new_quantity=quantity)

