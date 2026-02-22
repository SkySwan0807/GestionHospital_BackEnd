"""
routers/specialties.py
----------------------
Single Responsibility: Define all HTTP endpoints for the /specialties resource.

This is the PRESENTATION LAYER.
It is the ONLY file allowed to speak HTTP (Methods, Status Codes, JSON Bodies).
It handles routing, validation (via schemas), and calls the CRUD layer for work.

Imported by: app/main.py
Imports from:
  - fastapi (APIRouter, Depends, HTTPException, status)
  - sqlalchemy.orm (Session)
  - app (crud, schemas)
  - app.database (SessionLocal)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.database import get_db

# ============================================================================
# ROUTER CONFIGURATION
# ============================================================================
# prefix="/specialties" means every route below automatically starts with /specialties
# tags=["Specialties"] groups these routes together in the /docs UI
router = APIRouter(
    prefix="/specialties",
    tags=["Specialties"]
)



# ============================================================================
# GET /specialties
# ============================================================================
@router.get(
    "/",
    response_model=List[schemas.SpecialtyOut],
    status_code=status.HTTP_200_OK
)
def get_all_specialties(db: Session = Depends(get_db)):
    """
    Retrieve all specialties from the database.
    """
    # Simply delegate to the CRUD layer.
    return crud.get_all_specialties(db=db)


# ============================================================================
# GET /specialties/{specialty_id}
# ============================================================================
@router.get(
    "/{specialty_id}",
    response_model=schemas.SpecialtyOut,
    status_code=status.HTTP_200_OK
)
def get_specialty(specialty_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific specialty by its ID.
    """
    specialty = crud.get_specialty(db=db, specialty_id=specialty_id)
    if not specialty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialty not found"
        )
    return specialty


# ============================================================================
# POST /specialties
# ============================================================================
@router.post(
    "/",
    response_model=schemas.SpecialtyOut,
    status_code=status.HTTP_201_CREATED
)
def create_specialty(
    specialty: schemas.SpecialtyCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new specialty.
    """
    # 1. Check if the specialty already exists (Case-Insensitive check happens in CRUD)
    existing_specialty = crud.get_specialty_by_name(db=db, name=specialty.name)
    
    # 2. If it exists, abort the request and return 409 Conflict
    if existing_specialty:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Specialty already exists"
        )
    
    # 3. If it doesn't exist, proceed with creation
    return crud.create_specialty(db=db, specialty=specialty)
