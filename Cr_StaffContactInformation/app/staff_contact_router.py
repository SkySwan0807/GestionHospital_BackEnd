from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from .staff_contact_database import get_db

from .staff_contact_schema import StaffCreate, StaffResponse
from .staff_contact_service import create_staff, get_staff

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