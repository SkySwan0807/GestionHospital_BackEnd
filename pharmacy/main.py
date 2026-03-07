from fastapi import FastAPI, Request
from pharmacy.medications.router import router as medications_router
from pharmacy.database import Base, engine

# Ensure all models are imported so metadata is populated before create_all
from pharmacy.medications.model import Medication
from pharmacy.medications.category_model import TherapeuticCategory

from pharmacy.medications import exceptions as exc

# Optionally create database tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Core Medication Inventory API",
    description="API for the Hospital Management System - Specialty and Medication modules",
    version="1.0.0",
)

@app.exception_handler(exc.MedicationNotFound)
def medication_not_found_handler(request: Request, e: exc.MedicationNotFound):
    raise exc.MedicationNotFoundException(e.medication_id)

@app.exception_handler(exc.MedicationAlreadyExists)
def medication_already_exists_handler(request: Request, e: exc.MedicationAlreadyExists):
    raise exc.MedicationConflictException(e.name, e.generic_name)

@app.exception_handler(exc.InvalidStockQuantity)
def invalid_stock_quantity_handler(request: Request, e: exc.InvalidStockQuantity):
    raise exc.InvalidStockException(e.requested)

@app.exception_handler(exc.InvalidTherapeuticCategory)
def invalid_therapeutic_category_handler(request: Request, e: exc.InvalidTherapeuticCategory):
    raise exc.InvalidTherapeuticCategoryException(e.category_id)

app.include_router(medications_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
