from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from .staff_contact_database import get_db
from .staff_contact_schema import StaffCreate, StaffResponse, StaffUpdate
from .staff_contact_service import create_staff, get_staff, update_staff

router = APIRouter(
    prefix="/api/staff",
    tags=["Staff"]
)


@router.post(
    "/",
    response_model=StaffResponse,
    status_code=status.HTTP_201_CREATED
)
def create_staff_endpoint(
    staff: StaffCreate,
    db: Session = Depends(get_db)
):
    return create_staff(db, staff)


@router.get(
    "/{staff_id}",
    response_model=StaffResponse
)
def get_staff_endpoint(
    staff_id: int,
    db: Session = Depends(get_db)
):
    return get_staff(db, staff_id)

@router.patch(
    "/{staff_id}",
    response_model=StaffResponse
)
def update_staff_endpoint(
    staff_id: int,
    staff_update: StaffUpdate,
    db: Session = Depends(get_db)
):
    return update_staff(db, staff_id, staff_update)