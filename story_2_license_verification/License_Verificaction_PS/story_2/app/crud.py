from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import License
from app.schemas import LicenseCreate, LicenseUpdate


def get_all_licenses(
    db: Session,
    staff_id: str | None = None,
    specialty_id: int | None = None,
    status: str | None = None,
) -> list[License]:
    query = db.query(License)
    if staff_id is not None:
        query = query.filter(License.staff_id == staff_id)
    if specialty_id is not None:
        query = query.filter(License.specialty_id == specialty_id)
    if status is not None:
        query = query.filter(License.status == status)
    return query.all()


def get_license_by_id(db: Session, license_id: int) -> License | None:
    return db.query(License).filter(License.id == license_id).first()


def get_license_by_number(db: Session, license_number: str) -> License | None:
    return (
        db.query(License)
        .filter(func.lower(License.license_number) == license_number.lower().strip())
        .first()
    )


def create_license(db: Session, data: LicenseCreate) -> License:
    db_obj = License(**data.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_license(db: Session, license: License, data: LicenseUpdate) -> License:
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(license, key, value)
    db.commit()
    db.refresh(license)
    return license


def delete_license(db: Session, license: License) -> None:
    db.delete(license)
    db.commit()
