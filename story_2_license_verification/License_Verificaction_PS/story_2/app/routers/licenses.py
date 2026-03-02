from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app import crud
from app.clients.specialty_client import (
    SpecialtyClient,
    SpecialtyServiceUnavailableError,
)
from app.dependencies import get_db, get_specialty_client
from app.schemas import LicenseCreate, LicenseOut, LicenseStatus, LicenseUpdate

router = APIRouter(prefix="/api/v1/licenses", tags=["licenses"])


@router.post("", response_model=LicenseOut, status_code=201)
async def create_license(
    data: LicenseCreate,
    db: Session = Depends(get_db),
    sc: SpecialtyClient = Depends(get_specialty_client),
):
    try:
        is_valid = await sc.validate_specialty(data.specialty_id)
    except SpecialtyServiceUnavailableError:
        raise HTTPException(status_code=424, detail="Specialty service unavailable")
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Specialty not found")

    if crud.get_license_by_number(db, data.license_number):
        raise HTTPException(status_code=400, detail="License number already exists")

    return LicenseOut.model_validate(crud.create_license(db, data))


@router.get("", response_model=list[LicenseOut])
def get_licenses(
    staff_id: str | None = None,
    specialty_id: int | None = None,
    status: LicenseStatus | None = None,
    db: Session = Depends(get_db),
):
    # Convert Enum to string for repository layer
    status_str = status.value if status else None
    licenses = crud.get_all_licenses(db, staff_id, specialty_id, status_str)
    return [LicenseOut.model_validate(l) for l in licenses]


@router.get("/{license_id}", response_model=LicenseOut)
def get_license(license_id: int, db: Session = Depends(get_db)):
    license = crud.get_license_by_id(db, license_id)
    if not license:
        raise HTTPException(status_code=404, detail="License not found")
    return LicenseOut.model_validate(license)


@router.put("/{license_id}", response_model=LicenseOut)
async def update_license(
    license_id: int,
    data: LicenseUpdate,
    db: Session = Depends(get_db),
    sc: SpecialtyClient = Depends(get_specialty_client),
):
    license = crud.get_license_by_id(db, license_id)
    if not license:
        raise HTTPException(status_code=404, detail="License not found")

    if data.specialty_id is not None:
        try:
            is_valid = await sc.validate_specialty(data.specialty_id)
        except SpecialtyServiceUnavailableError:
            raise HTTPException(status_code=424, detail="Specialty service unavailable")
            
        if not is_valid:
            raise HTTPException(status_code=400, detail="Specialty not found")

    # If license_number is updated, we typically want to check uniqueness, 
    # but the instructions didn't explicitly ask for it on PUT.
    # We will strictly adhere to the instructions.

    return LicenseOut.model_validate(crud.update_license(db, license, data))


@router.delete("/{license_id}", status_code=204)
def delete_license(license_id: int, db: Session = Depends(get_db)):
    license = crud.get_license_by_id(db, license_id)
    if not license:
        raise HTTPException(status_code=404, detail="License not found")
        
    crud.delete_license(db, license)
    return Response(status_code=204)
