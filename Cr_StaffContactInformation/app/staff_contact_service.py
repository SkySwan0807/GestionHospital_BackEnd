import logging
from sqlalchemy.orm import Session
from .staff_contact_model import Staff
from .staff_contact_schema import StaffCreate
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def create_staff(db: Session, staff_data: StaffCreate) -> Staff:
    """
    Creates a new staff record with validation and traceability.
    """

    existing_staff = db.query(Staff).filter(Staff.email == staff_data.email).first()
    if existing_staff:
        logger.warning(f"Attempt to create staff with duplicate email: {staff_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_staff = Staff(**staff_data.model_dump())

    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)

    logger.info(f"Staff created successfully with ID: {new_staff.id}")

    return new_staff


def get_staff(db: Session, staff_id: int) -> Staff:
    """
    Retrieves a staff record by ID.
    """

    staff = db.query(Staff).filter(Staff.id == staff_id).first()

    if not staff:
        logger.warning(f"Staff not found with ID: {staff_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff not found"
        )

    logger.info(f"Staff retrieved successfully: {staff_id}")

    return staff


def update_staff(db, staff_id: int, staff_update):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()

    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    update_data = staff_update.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing = db.query(Staff).filter(
            Staff.email == update_data["email"],
            Staff.id != staff_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email already in use"
            )

    for field, value in update_data.items():
        setattr(staff, field, value)

    db.commit()
    db.refresh(staff)

    return staff