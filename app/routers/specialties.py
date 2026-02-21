"""
routers/specialties.py
----------------------
Single Responsibility: Define all HTTP endpoints for the /specialties resource.

This is the PRESENTATION LAYER (also called Controller in MVC).
It handles:
  - HTTP method routing (POST, GET)
  - Request body parsing (delegated to FastAPI + Pydantic via schemas)
  - Calling the CRUD layer for data operations
  - Returning appropriate HTTP status codes and response bodies
  - HTTP-level error handling (e.g., 404 Not Found, 409 Conflict)

Imported by: app/main.py (mounts this router via app.include_router())
Imports from:
  - app.crud     (database operations)
  - app.schemas  (request/response models)
  - app.database (get_db dependency for session injection)

Why use APIRouter instead of putting routes directly in main.py?
  APIRouter lets you group related endpoints into a module.
  main.py stays clean — it only assembles the app.
  As the system grows (doctors, patients, appointments), each resource
  gets its own router file without touching main.py.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.database import get_db

# Create a router instance with a prefix and tag
# prefix="/specialties" means all routes here are under /specialties
# tags=["Specialties"] groups them together in the Swagger UI at /docs
router = APIRouter(
    prefix="/specialties",
    tags=["Specialties"],
)


# ---------------------------------------------------------------------------
# POST /specialties
# ---------------------------------------------------------------------------
@router.post(
    "/",
    response_model=schemas.SpecialtyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new medical specialty",
    description=(
        "Creates a new entry in the hospital specialty catalog. "
        "Returns 409 Conflict if a specialty with the same name already exists."
    ),
)
def create_specialty(
    specialty: schemas.SpecialtyCreate,
    db: Session = Depends(get_db),
):
    """
    POST /specialties

    Request body (JSON):
        {
            "name": "Cardiology",
            "description": "Diagnosis and treatment of heart diseases"
        }

    Lifecycle:
        1. FastAPI parses the JSON body into a SpecialtyCreate Pydantic object
           (validates types, min/max length constraints — returns 422 if invalid)
        2. FastAPI calls get_db() via Depends() to open a DB session
        3. We check for duplicate name — return 409 if it already exists
        4. crud.create_specialty() inserts the record and returns the ORM object
        5. FastAPI serializes the ORM object via SpecialtyResponse → JSON
        6. Returns HTTP 201 Created with the new specialty as the body
    """
    # Step 1: Check for duplicate name to enforce uniqueness at the application layer
    # (The DB also enforces unique=True, but we return a friendlier 409 instead of 500)
    existing = crud.get_specialty_by_name(db, name=specialty.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A specialty with the name '{specialty.name}' already exists.",
        )

    # Step 2: Delegate to the CRUD layer to perform the INSERT
    return crud.create_specialty(db=db, specialty=specialty)


# ---------------------------------------------------------------------------
# GET /specialties
# ---------------------------------------------------------------------------
@router.get(
    "/",
    response_model=List[schemas.SpecialtyResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve all medical specialties",
    description=(
        "Returns a paginated list of all specialties in the catalog. "
        "Use 'skip' and 'limit' query parameters for pagination."
    ),
)
def get_specialties(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    GET /specialties?skip=0&limit=100

    Query parameters:
        skip  (int, default 0)   : Number of records to skip (offset)
        limit (int, default 100) : Maximum number of records to return

    Lifecycle:
        1. FastAPI parses ?skip and ?limit from the URL query string
        2. FastAPI calls get_db() via Depends() to open a DB session
        3. crud.get_specialties() executes SELECT with OFFSET and LIMIT
        4. FastAPI serializes the list via List[SpecialtyResponse] → JSON array
        5. Returns HTTP 200 OK with the list as the body (empty list [] if no records)
    """
    return crud.get_specialties(db=db, skip=skip, limit=limit)


# ---------------------------------------------------------------------------
# GET /specialties/{specialty_id}
# ---------------------------------------------------------------------------
@router.get(
    "/{specialty_id}",
    response_model=schemas.SpecialtyResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a single specialty by ID",
    description="Returns a single specialty by its unique integer ID. Returns 404 if not found.",
)
def get_specialty(
    specialty_id: int,
    db: Session = Depends(get_db),
):
    """
    GET /specialties/{specialty_id}

    Path parameter:
        specialty_id (int): The primary key of the specialty to retrieve

    Returns 404 Not Found if no specialty with that ID exists.
    """
    db_specialty = crud.get_specialty(db=db, specialty_id=specialty_id)
    if db_specialty is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specialty with id={specialty_id} not found.",
        )
    return db_specialty
