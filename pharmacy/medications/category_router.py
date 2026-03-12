"""
pharmacy/medications/category_router.py
─────────────────────────────────────────────────────────────────────────
REST endpoints for the therapeutic_categories catalog table.

Routes:
  POST   /categories/                  → create a category
  GET    /categories/                  → list all categories
  GET    /categories/{category_id}     → get single category
  PATCH  /categories/{category_id}     → partial update
  DELETE /categories/{category_id}     → hard delete
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from pharmacy.database import get_db
from pharmacy.medications import schemas
from pharmacy.medications.category_model import TherapeuticCategory

router = APIRouter(
    prefix="/categories",
    tags=["therapeutic-categories"],
)


# ── Create ────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=schemas.TherapeuticCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a therapeutic category",
)
def create_category(
    category_in: schemas.TherapeuticCategoryCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new therapeutic category.

    - **name**: Unique category label (e.g., `"Analgesic"`, `"Antibiotic"`).
    - **description**: Optional free-text description.

    Raises **409 Conflict** if a category with the same name already exists.
    """
    existing = db.query(TherapeuticCategory).filter(
        TherapeuticCategory.name == category_in.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Therapeutic category '{category_in.name}' already exists.",
        )
    db_category = TherapeuticCategory(**category_in.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


# ── Read (list) ───────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[schemas.TherapeuticCategoryResponse],
    summary="List all therapeutic categories",
)
def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Return a paginated list of all therapeutic categories.

    - **skip**: Records to skip (offset). Default: `0`.
    - **limit**: Maximum records to return. Default: `100`.
    """
    return (
        db.query(TherapeuticCategory)
        .order_by(TherapeuticCategory.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


# ── Read (single) ─────────────────────────────────────────────────────────

@router.get(
    "/{category_id}",
    response_model=schemas.TherapeuticCategoryResponse,
    summary="Get a single therapeutic category",
)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Retrieve one therapeutic category by its primary key.

    Raises **404 Not Found** if the category does not exist.
    """
    category = db.get(TherapeuticCategory, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Therapeutic category with id={category_id} not found.",
        )
    return category


# ── Update (partial) ──────────────────────────────────────────────────────

@router.patch(
    "/{category_id}",
    response_model=schemas.TherapeuticCategoryResponse,
    summary="Partial update of a therapeutic category",
)
def update_category(
    category_id: int,
    category_in: schemas.TherapeuticCategoryUpdate,
    db: Session = Depends(get_db),
):
    """
    Partially update a therapeutic category.

    Only fields present in the request body are applied (`exclude_unset=True`).

    Raises **404 Not Found** if the category does not exist.
    Raises **409 Conflict** if the new name collides with an existing category.
    """
    category = db.get(TherapeuticCategory, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Therapeutic category with id={category_id} not found.",
        )

    update_data = category_in.model_dump(exclude_unset=True)

    # Reject conflicting name if being changed
    if "name" in update_data and update_data["name"] != category.name:
        conflict = db.query(TherapeuticCategory).filter(
            TherapeuticCategory.name == update_data["name"],
            TherapeuticCategory.id != category_id,
        ).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Therapeutic category '{update_data['name']}' already exists.",
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


# ── Delete ────────────────────────────────────────────────────────────────

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a therapeutic category",
)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    Hard-delete a therapeutic category.

    > ⚠️ Medications currently assigned to this category will have their
    > `therapeutic_category_id` set to `NULL` (FK is nullable).

    Raises **404 Not Found** if the category does not exist.
    """
    category = db.get(TherapeuticCategory, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Therapeutic category with id={category_id} not found.",
        )
    db.delete(category)
    db.commit()
    return None
