"""
routers/vacation.py
-------------------
Single Responsibility: Define all HTTP endpoints for the vacation request module.

This router was adapted from request-vacation/main.py (feature/leave-vacation-request-staff).
It converts Diego's standalone FastAPI app into an APIRouter that plugs into the
central hospital server (app/main.py).

Route groups:
  HR MANAGEMENT  (/human-resources/vacation-management)
    GET    /human-resources/vacation-management              → list all requests
    GET    /human-resources/vacation-management/{id}         → get single request
    PATCH  /human-resources/vacation-management/{id}         → approve / reject

  EMPLOYEE SELF-SERVICE  (/myprofile/requestvacation)
    POST   /myprofile/requestvacation                        → create request
    PATCH  /myprofile/requestvacation/{id}/cancel            → cancel request
    PATCH  /myprofile/requestvacation/{id}                   → edit pending request
    GET    /myprofile/requestvacation/balance/{staff_id}     → check balance
    GET    /myprofile/requestvacation/{staff_id}/{request_id}→ get specific request
    GET    /myprofile/requestvacation/{staff_id}             → get all by staff

Bugs fixed vs original request-vacation/main.py:
  [BUG-01] Path param mismatch on DELETE → replaced with proper cancel PATCH
  [BUG-02] DELETE always raised 404 on success → fixed with else branch
  [BUG-03] `if not result` never triggers (CursorResult always truthy) → removed
  [BUG-04] Status inconsistency 'Pending' vs 'pending' → normalized to lowercase
  [BUG-05] SQLAlchemy imports in schemas.py → cleaned up
  [BUG-06] Field(nullable=False) invalid in Pydantic → removed
  [BUG-07] staff_id/user_id confusion in POST — Vacation.staff_id is FK to staff.id
           but code was passing user_id directly → fixed to resolve staff.id first
  [BUG-08] Route ordering — /balance/{staff_id} must be declared BEFORE /{staff_id}
           or FastAPI matches it as a generic path param → fixed by ordering correctly

Imported by: app/main.py
Imports from:
  - fastapi
  - sqlalchemy
  - app.models, app.schemas, app.database
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Annotated, List
from datetime import date

from app import models, schemas
from app.database import get_db

# ============================================================================
# ROUTER CONFIGURATION
# ============================================================================
router = APIRouter(tags=["Vacation Requests"])

DB = Annotated[Session, Depends(get_db)]


# ============================================================================
# HR MANAGEMENT ENDPOINTS
# ============================================================================

@router.get(
    "/human-resources/vacation-management",
    response_model=List[schemas.VacationPostResponse],
    status_code=status.HTTP_200_OK,
    summary="[HR] List all vacation requests"
)
def get_all_vacation_requests(db: DB):
    """Returns every vacation request in the system for HR review."""
    requests = db.execute(select(models.Vacation)).scalars().all()
    if not requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vacation requests found"
        )
    return requests


@router.get(
    "/human-resources/vacation-management/{request_id}",
    response_model=schemas.VacationPostResponse,
    status_code=status.HTTP_200_OK,
    summary="[HR] Get a single vacation request by ID"
)
def get_vacation_request_hr(request_id: int, db: DB):
    """
    Returns a single vacation request by its ID.
    FIX [BUG-03]: Removed false `if not result` guard.
    """
    vacation = db.execute(
        select(models.Vacation).where(models.Vacation.id == request_id)
    ).scalars().first()

    if not vacation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacation request with id {request_id} not found"
        )
    return vacation


@router.patch(
    "/human-resources/vacation-management/{request_id}",
    response_model=schemas.VacationPostResponse,
    status_code=status.HTTP_200_OK,
    summary="[HR] Approve or reject a vacation request"
)
def update_vacation_request_status(request_id: int, updated_data: schemas.VacationStaffUpdate, db: DB):
    """
    HR approves or rejects a vacation request.
    - Cannot modify a cancelled request.
    - Cannot re-modify an already accepted/rejected request.
    - Rejection requires a rejection_reason.
    - Rejection restores the employee's vacation balance.
    FIX [BUG-03]: Removed false `if not result` guard.
    FIX [BUG-04]: Status comparisons use lowercase consistently.
    """
    vacation = db.execute(
        select(models.Vacation).where(models.Vacation.id == request_id)
    ).scalars().first()

    if not vacation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacation request with id {request_id} not found"
        )

    if vacation.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify a request that was cancelled by the employee"
        )

    if vacation.status in ("accepted", "rejected"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This request has already been resolved"
        )

    if updated_data.status not in ("accepted", "rejected"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status can only be set to 'accepted' or 'rejected'"
        )

    if updated_data.status == "rejected":
        if not updated_data.rejection_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="rejection_reason is required when rejecting a request"
            )
        vacation.rejection_reason = updated_data.rejection_reason

        # Restore balance on rejection
        # FIX [BUG-07]: Query staff by staff.id (vacation.staff_id), not by user_id
        staff = db.execute(
            select(models.Staff).where(models.Staff.id == vacation.staff_id)
        ).scalars().first()

        if not staff or not staff.vacation_details:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No vacation balance assigned to this staff member"
            )

        vacation_days = (vacation.end_date - vacation.start_date).days
        staff.vacation_details["used"] -= vacation_days
        staff.vacation_details["available"] += vacation_days
        db.commit()
        db.refresh(staff)

    vacation.status = updated_data.status
    db.commit()
    db.refresh(vacation)
    return vacation


# ============================================================================
# EMPLOYEE SELF-SERVICE ENDPOINTS
# ============================================================================

@router.post(
    "/myprofile/requestvacation",
    response_model=schemas.VacationPostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Employee] Submit a new vacation request"
)
def create_vacation_request(staff_id: int, post: schemas.VacationPostCreate, db: DB):
    """
    Creates a vacation request. Validates:
    - No existing pending request for this staff member.
    - Start date is at least 7 days from today.
    - Duration is between 3 and 15 days.
    - Enough available vacation balance.
    FIX [BUG-07]: staff_id param is user_id — resolve staff.id first, then
                  use staff.id for Vacation.staff_id (FK to staff.id).
    """
    # Resolve Staff record from user_id
    staff = db.execute(
        select(models.Staff).where(models.Staff.user_id == staff_id)
    ).scalars().first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found for this user ID"
        )

    # Check for existing pending request using staff.id (the real FK)
    existing_pending = db.execute(
        select(models.Vacation)
        .where(models.Vacation.staff_id == staff.id)
        .where(models.Vacation.status == "pending")
    ).scalars().first()

    if existing_pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending request already exists. Wait for it to be resolved before submitting a new one."
        )

    if post.start_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be in the past"
        )

    if (post.start_date - date.today()).days < 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vacation request must be submitted at least one week in advance"
        )

    vacation_days = (post.end_date - post.start_date).days
    if not (3 <= vacation_days <= 15):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vacation duration must be between 3 and 15 days"
        )

    if not staff.vacation_details:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No vacation balance assigned to this staff member"
        )

    if staff.vacation_details["available"] == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No vacation days available"
        )

    if staff.vacation_details["available"] < vacation_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough vacation days. Available: {staff.vacation_details['available']}, requested: {vacation_days}"
        )

    # Deduct balance
    staff.vacation_details["used"] += vacation_days
    staff.vacation_details["available"] -= vacation_days

    # Create request using staff.id (correct FK), not user_id
    new_request = models.Vacation(staff_id=staff.id, **post.model_dump())
    db.add(new_request)
    db.commit()
    db.refresh(staff)
    db.refresh(new_request)
    return new_request


@router.patch(
    "/myprofile/requestvacation/{request_id}/cancel",
    response_model=schemas.VacationPostResponse,
    status_code=status.HTTP_200_OK,
    summary="[Employee] Cancel a vacation request"
)
def cancel_vacation_request(request_id: int, updated_data: schemas.VacationCanceled, db: DB):
    """
    Employee cancels a pending vacation request.
    Restores the vacation balance when cancelled.
    Cannot cancel an already accepted/rejected request.
    FIX [BUG-03]: Removed false `if not result` guard.
    FIX [BUG-07]: Resolves staff by staff.id, not user_id.
    """
    vacation = db.execute(
        select(models.Vacation).where(models.Vacation.id == request_id)
    ).scalars().first()

    if not vacation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacation request with id {request_id} not found"
        )

    if vacation.status in ("accepted", "rejected"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot cancel a request that has already been accepted or rejected"
        )

    if vacation.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This request is already cancelled"
        )

    if updated_data.status != "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status can only be set to 'cancelled' via this endpoint"
        )

    # Restore balance
    staff = db.execute(
        select(models.Staff).where(models.Staff.id == vacation.staff_id)
    ).scalars().first()

    if not staff or not staff.vacation_details:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No vacation balance found for this staff member"
        )

    vacation_days = (vacation.end_date - vacation.start_date).days
    staff.vacation_details["used"] -= vacation_days
    staff.vacation_details["available"] += vacation_days

    vacation.status = "cancelled"
    db.commit()
    db.refresh(staff)
    db.refresh(vacation)
    return vacation


@router.patch(
    "/myprofile/requestvacation/{request_id}",
    response_model=schemas.VacationPostResponse,
    status_code=status.HTTP_200_OK,
    summary="[Employee] Edit a pending vacation request"
)
def update_vacation_request(request_id: int, updated_data: schemas.VacationBase, db: DB):
    """
    Employee edits the dates of a pending vacation request.
    Restores old balance and deducts new balance.
    Cannot edit accepted, rejected, or cancelled requests.
    FIX [BUG-03]: Removed false `if not result` guard.
    FIX [BUG-07]: Resolves staff by staff.id.
    """
    vacation = db.execute(
        select(models.Vacation).where(models.Vacation.id == request_id)
    ).scalars().first()

    if not vacation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacation request with id {request_id} not found"
        )

    if vacation.status in ("accepted", "rejected"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot edit a request that has already been accepted or rejected"
        )

    if vacation.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot edit a cancelled request"
        )

    if updated_data.start_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be in the past"
        )

    if (updated_data.start_date - date.today()).days < 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vacation request must be submitted at least one week in advance"
        )

    new_days = (updated_data.end_date - updated_data.start_date).days
    if not (3 <= new_days <= 15):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vacation duration must be between 3 and 15 days"
        )

    staff = db.execute(
        select(models.Staff).where(models.Staff.id == vacation.staff_id)
    ).scalars().first()

    if not staff or not staff.vacation_details:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No vacation balance found for this staff member"
        )

    old_days = (vacation.end_date - vacation.start_date).days

    # Restore old balance
    staff.vacation_details["used"] -= old_days
    staff.vacation_details["available"] += old_days

    # Validate and deduct new balance
    if staff.vacation_details["available"] == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No vacation days available"
        )

    if staff.vacation_details["available"] < new_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough vacation days. Available: {staff.vacation_details['available']}, requested: {new_days}"
        )

    staff.vacation_details["used"] += new_days
    staff.vacation_details["available"] -= new_days

    # Apply field updates
    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(vacation, key, value)

    db.commit()
    db.refresh(staff)
    db.refresh(vacation)
    return vacation


# ============================================================================
# IMPORTANT: /balance/{staff_id} MUST be declared BEFORE /{staff_id}
# FIX [BUG-08]: FastAPI matches routes top-to-bottom. If /{staff_id} is first,
# "balance" gets interpreted as a staff_id integer → 422 Unprocessable Entity.
# ============================================================================

@router.get(
    "/myprofile/requestvacation/balance/{staff_id}",
    response_model=schemas.VacationBalanceResponse,
    status_code=status.HTTP_200_OK,
    summary="[Employee] Check vacation balance"
)
def get_vacation_balance(staff_id: int, db: DB):
    """
    Returns the vacation balance (assigned, used, available) for a staff member.
    Only accessible by users with role 'doctor' or 'administrative'.
    """
    user = db.execute(
        select(models.User).where(models.User.id == staff_id)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.role not in ("doctor", "administrative"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors and administrative staff can check vacation balance"
        )

    staff = db.execute(
        select(models.Staff).where(models.Staff.user_id == staff_id)
    ).scalars().first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found for this user"
        )

    return {"vacation_details": staff.vacation_details}


@router.get(
    "/myprofile/requestvacation/{staff_id}/{request_id}",
    response_model=schemas.VacationPostResponse,
    status_code=status.HTTP_200_OK,
    summary="[Employee] Get a specific vacation request"
)
def get_vacation_request_by_staff(staff_id: int, request_id: int, db: DB):
    """
    Returns a specific vacation request belonging to the given staff member.
    Only accessible by doctors and administrative staff.
    """
    user = db.execute(
        select(models.User).where(models.User.id == staff_id)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.role not in ("doctor", "administrative"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    # Find staff.id from user_id to match Vacation.staff_id correctly
    staff = db.execute(
        select(models.Staff).where(models.Staff.user_id == staff_id)
    ).scalars().first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found"
        )

    vacation = db.execute(
        select(models.Vacation)
        .where(models.Vacation.staff_id == staff.id)
        .where(models.Vacation.id == request_id)
    ).scalars().first()

    if not vacation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacation request not found"
        )

    return vacation


@router.get(
    "/myprofile/requestvacation/{staff_id}",
    response_model=List[schemas.VacationPostResponse],
    status_code=status.HTTP_200_OK,
    summary="[Employee] Get all vacation requests for a staff member"
)
def get_all_vacation_requests_by_staff(staff_id: int, db: DB):
    """
    Returns all vacation requests for a given staff member.
    Only accessible by doctors and administrative staff.
    """
    user = db.execute(
        select(models.User).where(models.User.id == staff_id)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.role not in ("doctor", "administrative"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    staff = db.execute(
        select(models.Staff).where(models.Staff.user_id == staff_id)
    ).scalars().first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found"
        )

    vacations = db.execute(
        select(models.Vacation).where(models.Vacation.staff_id == staff.id)
    ).scalars().all()

    if not vacations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vacation requests found for this staff member"
        )

    return vacations
