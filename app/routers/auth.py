"""
routers/auth.py
---------------
Single Responsibility: Define all HTTP endpoints for user authentication.

Adapted from user_auth/router.py (feature/user-Authentication).
Converts the standalone FastAPI app into an APIRouter that plugs into
the central hospital server (app/main.py).

Endpoints:
  POST /login/patient          → Patient login
  POST /login/staff            → Staff login
  POST /forgot_password        → Request password reset code via email
  POST /new_user               → Request account verification code via email
  POST /verify                 → Verify email code (for reset or registration)
  POST /reset_password         → Set new password after verification
  POST /register               → Complete patient registration

Bug fixed vs original user_auth/router.py:
  [BUG-01] Unused import `from app.database import SessionLocal` → removed

Imported by: app/main.py
Imports from:
  - fastapi
  - sqlalchemy.orm
  - app.models, app.database
  - user_auth.security, user_auth.email_service
"""

from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import re

from app.database import get_db
from app.models import User, Patient, VerificationCode
from user_auth.security import verify_password, hash_password
from user_auth.email_service import send_email, generate_code

# ============================================================================
# ROUTER CONFIGURATION
# ============================================================================
router = APIRouter(tags=["Authentication"])

DB = Session

CODE_EXPIRATION_MINUTES = 10


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def verify_user(email: str, db: Session):
    """Returns the User object if it exists, None otherwise."""
    return db.query(User).filter(User.email == email).first()


def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def is_valid_phone(phone: str) -> bool:
    pattern = r"^\+?\d{7,15}$"
    return re.match(pattern, phone) is not None


# ============================================================================
# LOGIN ENDPOINTS
# ============================================================================

@router.post(
    "/login/patient",
    summary="[Auth] Patient login"
)
def login_patient(email: str, password: str, db: Session = Depends(get_db)):
    """
    Authenticates a patient user by email and password.
    Returns user id, full name, and role on success.
    """
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"success": False, "message": "Invalid User"}

    if not user.patient_profile:
        return {"success": False, "message": "User is not a patient"}

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid Password")

    return {
        "id": user.id,
        "name": user.patient_profile.first_name + " " + user.patient_profile.last_name,
        "role": user.role
    }


@router.post(
    "/login/staff",
    summary="[Auth] Staff login"
)
def login_staff(email: str, password: str, db: Session = Depends(get_db)):
    """
    Authenticates a staff member by email and password.
    Returns user id, full name, and role on success.
    """
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"success": False, "message": "Invalid credentials"}

    if not user.staff_profile:
        return {"success": False, "message": "User is not staff"}

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid Password")

    return {
        "id": user.id,
        "name": user.staff_profile.first_name + " " + user.staff_profile.last_name,
        "role": user.role
    }


# ============================================================================
# PASSWORD RESET FLOW
# ============================================================================

@router.post(
    "/forgot_password",
    summary="[Auth] Request password reset code"
)
def forgot_password(email: str, db: Session = Depends(get_db)):
    """
    Sends a 6-digit verification code to the email for password reset (type=1).
    Code expires in 10 minutes.
    """
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    if not verify_user(email, db):
        raise HTTPException(status_code=404, detail="User not found")

    code = generate_code()

    verification = VerificationCode(
        email=email,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=CODE_EXPIRATION_MINUTES),
        is_authorized=False,
        is_used=False,
        type=1
    )

    db.add(verification)
    db.commit()
    send_email(email, code, 1)

    return {
        "message": f"Verification code sent to {email} to reset your password."
    }


@router.post(
    "/reset_password",
    summary="[Auth] Set new password after verification"
)
def reset_password(
    email: str,
    new_password: str,
    password_confirmation: str,
    db: Session = Depends(get_db)
):
    """
    Resets the user's password after verifying the email code.
    Requires a previously authorized and unused type=1 code.
    """
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    if not verify_user(email, db):
        raise HTTPException(status_code=404, detail="User not found")

    verification = db.query(VerificationCode).filter(
        VerificationCode.email == email,
        VerificationCode.expires_at > datetime.utcnow(),
        VerificationCode.is_authorized == True,
        VerificationCode.is_used == False,
        VerificationCode.type == 1
    ).first()

    if not verification:
        raise HTTPException(
            status_code=400,
            detail="No authorized code found for this email"
        )

    if new_password != password_confirmation:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user = db.query(User).filter(User.email == email).first()
    user.password = hash_password(new_password)
    verification.is_used = True
    db.commit()

    return {"message": "Password updated successfully"}


# ============================================================================
# REGISTRATION FLOW
# ============================================================================

@router.post(
    "/new_user",
    summary="[Auth] Request account verification code"
)
def new_user(email: str, db: Session = Depends(get_db)):
    """
    Sends a 6-digit verification code to the email for new account registration (type=2).
    Code expires in 10 minutes.
    """
    if verify_user(email, db):
        raise HTTPException(status_code=400, detail="Email already registered")

    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    code = generate_code()

    verification = VerificationCode(
        email=email,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=CODE_EXPIRATION_MINUTES),
        is_authorized=False,
        is_used=False,
        type=2
    )

    db.add(verification)
    db.commit()
    send_email(email, code, 2)

    return {
        "message": f"Verification code sent to {email} to complete your registration."
    }


@router.post(
    "/verify",
    summary="[Auth] Verify email code"
)
def verify(email: str, code: str, db: Session = Depends(get_db)):
    """
    Verifies the code sent to the email.
    - type=1: directs to /reset_password
    - type=2: directs to /register
    Marks code as authorized on success.
    """
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    verification = db.query(VerificationCode).filter(
        VerificationCode.email == email,
        VerificationCode.code == code
    ).first()

    if not verification:
        raise HTTPException(status_code=400, detail="Invalid code or email")

    if verification.is_used:
        raise HTTPException(status_code=400, detail="Code already used")

    if verification.is_authorized:
        raise HTTPException(status_code=400, detail="Code already verified")

    if verification.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Code expired")

    verification.is_authorized = True
    db.commit()

    if verification.type == 1:
        return {
            "message": "Code verified",
            "next_step": "/reset_password",
            "email": email
        }
    elif verification.type == 2:
        return {
            "message": "Code verified",
            "next_step": "/register",
            "email": email
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid verification type")


@router.post(
    "/register",
    summary="[Auth] Complete patient registration"
)
def register_user(
    email: str,
    password: str,
    confirm_password: str,
    first_name: str,
    last_name: str,
    date_of_birth: date,
    contact_number: str,
    db: Session = Depends(get_db)
):
    """
    Completes patient registration after email verification.
    Creates a User (role=Patient) and linked Patient profile.
    Requires a previously authorized and unused type=2 code.
    """
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    if verify_user(email, db):
        raise HTTPException(status_code=400, detail="Email already registered")

    verification = db.query(VerificationCode).filter(
        VerificationCode.email == email,
        VerificationCode.expires_at > datetime.utcnow(),
        VerificationCode.is_authorized == True,
        VerificationCode.is_used == False,
        VerificationCode.type == 2
    ).first()

    if not verification:
        raise HTTPException(
            status_code=400,
            detail="No authorized code found for this email"
        )

    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if not is_valid_phone(contact_number):
        raise HTTPException(status_code=400, detail="Invalid phone number")

    user = User(
        email=email,
        password=hash_password(password),
        role="Patient"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    patient = Patient(
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        contact_number=contact_number
    )

    verification.is_used = True
    db.add(patient)
    db.commit()

    return {"message": "User registered successfully"}
