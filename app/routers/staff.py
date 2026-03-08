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
