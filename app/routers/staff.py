from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.database import get_db

# =====================================================================
# ROUTER CONFIGURATION
# =====================================================================
router = APIRouter(
    prefix="/staff",
    tags=["Staff"]
)

# =====================================================================
# GET /staff/search
# =====================================================================
@router.get(
    "/search",
    response_model=List[schemas.StaffOut],
    status_code=status.HTTP_200_OK
)
def search_staff_endpoint(
    name: str | None = None,
    department: str | None = None,
    role: str | None = None,
    location: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Endpoint to search staff contacts.
    Accepts optional query parameters:
    - name
    - department
    - role
    - location

    Returns a list of matching staff records.
    """
    results = crud.search_staff(db, name, department, role, location)

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No staff found with given criteria"
        )

    return results

# =====================================================================
# PATCH /staff/update-profile
# =====================================================================
@router.patch(
    "/update-profile",
    response_model=schemas.StaffOut, 
    status_code=status.HTTP_200_OK
)
def update_profile_endpoint(
    payload: schemas.StaffSelfUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza la información de contacto recibiendo un objeto JSON.
    """
    updated_user = crud.update_staff_contact_info(db, payload)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff with ID {payload.staff_id} not found"
        )
    
    return updated_user
