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
    response_model=List[schemas.StaffContactOut],
    status_code=status.HTTP_200_OK
)
def search_staff_endpoint(
    name: str | None = None,
    department: str | None = None,
    specialty: str | None = None,
    role: str | None = None,
    status: str | None = None,
    email: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Endpoint to search staff contacts.
    Accepts optional query parameters:
    - name
    - department
    - role
    - specialty
    - role
    - status
    - email

    Returns a list of matching staff records.
    """
    results = crud.search_staff(
        db=db,
        name=name,
        department=department,
        specialty=specialty,
        role=role,
        status=status,
        email=email
    )

    return [
        schemas.StaffContactOut(
            id=staff.id,
            first_name=staff.first_name,
            last_name=staff.last_name,
            email=staff.user.email if staff.user else "no-email@example.com",
            phone_number=staff.phone_number,
            role_level=staff.role_level,
            status=staff.status,
            profile_pic=staff.profile_pic,
            department=staff.department.name if staff.department else None,
            specialty=staff.specialty.name if staff.specialty else None,
            created_at=staff.created_at
        )
        for staff in results
    ]

# =====================================================================
# PATCH /staff/update-profile
# =====================================================================
@router.patch(
    "/update-profile",
    response_model=schemas.StaffContactOut,
    status_code=status.HTTP_200_OK
)
def update_profile_endpoint(
    payload: schemas.StaffSelfUpdate,
    db: Session = Depends(get_db)
):
    updated_staff = crud.update_staff_contact_info(db, payload)

    if not updated_staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff with ID {payload.staff_id} not found"
        )

    return schemas.StaffContactOut(
        id=updated_staff.id,
        first_name=updated_staff.first_name,
        last_name=updated_staff.last_name,
        email=updated_staff.user.email,
        phone_number=updated_staff.phone_number,
        role_level=updated_staff.role_level,
        status=updated_staff.status,
        profile_pic=updated_staff.profile_pic,
        department=updated_staff.department.name if updated_staff.department else None,
        specialty=updated_staff.specialty.name if updated_staff.specialty else None,
        created_at=updated_staff.created_at
    )

def _to_staff_contact_out(staff) -> schemas.StaffContactOut:
    return schemas.StaffContactOut(
        id=staff.id,
        first_name=staff.first_name,
        last_name=staff.last_name,
        email=staff.user.email if staff.user else "no-email@example.com",
        phone_number=staff.phone_number,
        role_level=staff.role_level,
        status=staff.status,
        profile_pic=staff.profile_pic,
        department=staff.department.name if staff.department else None,
        specialty=staff.specialty.name if staff.specialty else None,
        created_at=staff.created_at
    )

@router.get(
    "/{id}",
    response_model=schemas.StaffContactOut,
    status_code=status.HTTP_200_OK
)
def get_staff_by_id_endpoint(
    id: str,
    requester_role: str | None = None,
    db: Session = Depends(get_db)
):
    if (requester_role or "").strip().lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this resource"
        )
    staff = crud.get_staff_by_id(db, id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return _to_staff_contact_out(staff)