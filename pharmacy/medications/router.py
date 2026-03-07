from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from pharmacy.database import get_db
from pharmacy.medications import service, schemas

router = APIRouter(
    prefix="/medications",
    tags=["medications"]
)

@router.post("/", response_model=schemas.MedicationResponse, status_code=status.HTTP_201_CREATED)
def create_medication(medication: schemas.MedicationCreate, db: Session = Depends(get_db)):
    return service.create_medication(db=db, medication_in=medication)

@router.get("/", response_model=List[schemas.MedicationResponse])
def read_medications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_all_medications(db, skip=skip, limit=limit)

@router.get("/{medication_id}", response_model=schemas.MedicationResponse)
def read_medication(medication_id: int, db: Session = Depends(get_db)):
    return service.get_medication_by_id(db, medication_id=medication_id)

@router.patch("/{medication_id}", response_model=schemas.MedicationResponse)
def update_medication(medication_id: int, medication: schemas.MedicationUpdate, db: Session = Depends(get_db)):
    return service.update_medication(db, medication_id=medication_id, medication_in=medication)

@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(medication_id: int, db: Session = Depends(get_db)):
    med = service.get_medication_by_id(db, medication_id=medication_id)
    db.delete(med)
    db.commit()
    return None

@router.post("/{medication_id}/stock", response_model=schemas.MedicationResponse)
def adjust_stock(medication_id: int, quantity: int, db: Session = Depends(get_db)):
    return service.update_medication_stock(db, medication_id=medication_id, new_quantity=quantity)
