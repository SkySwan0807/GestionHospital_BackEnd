"""
router.py
---------
Single Responsibility: Defines authentication HTTP endpoints.
"""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Patient, VerificationCode
from user_auth.security import verify_password
from user_auth.email_service import send_email, generate_code
from user_auth.security import hash_password
from datetime import datetime, timedelta

CODE_EXPIRATION_MINUTES = 10

router = APIRouter(tags=["Authentication"])


# Dependency injection for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    """
    Validates user credentials.

    Returns:
        - success: True if credentials are valid
        - success: False otherwise
    """

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"success": False, "message": "Invalid credentials"}

    if not verify_password(password, user.password):
        return {"success": False, "message": "Invalid credentials"}

    return {
        "success": True,
        "message": "Login successful",
        "role": user.role
    }

@router.post("/forgot_password")
def forgot_password(email: str, db: Session = Depends(get_db)):

    if not verify_user(email, db):
        raise HTTPException(status_code=404, detail="User not found")

    code = generate_code()

    verification = VerificationCode(
        email=email,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=CODE_EXPIRATION_MINUTES),
        used=False,
        type=1
    )

    db.add(verification)
    db.commit()

    send_email(email, code, 1)

    return {"message": "Verification code sent to the provided email address: " + email +
            "to reset your password."}

@router.post("/new_user")
def new_user(email: str, db: Session = Depends(get_db)):

    if verify_user(email, db):
        raise HTTPException(status_code=400, detail="Email already registered")

    code = generate_code()

    verification = VerificationCode(
        email=email,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=CODE_EXPIRATION_MINUTES),
        used=False,
        type=2
    )

    db.add(verification)
    db.commit()

    send_email(email, code, 2)

    return {"message": "Verification code sent to the provided email address: " + email +
            "to complete your registration."}


@router.post("/verify")
def verify(email: str, code: str, db: Session = Depends(get_db)):

    verification = db.query(VerificationCode).filter(
        VerificationCode.email == email,
        VerificationCode.code == code
    ).first()

    if not verification:
        raise HTTPException(status_code=400, detail="Invalid code or email")

    if verification.used:
        raise HTTPException(status_code=400, detail="Code already used")

    if verification.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Code expired")

    verification.used = True
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

@router.post("/reset_password")
def reset_password(
        email: str,
        new_password: str,
        password_confirmation: str,
        db: Session = Depends(get_db)
):

    if not verify_user(email, db):
        raise HTTPException(status_code=404, detail="User not found")

    user = db.query(User).filter(User.email == email).first()

    if new_password != password_confirmation:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user.password = hash_password(new_password)

    db.commit()

    return {"message": "Password updated successfully"}

@router.post("/register")
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

    if verify_user(email, db):
        raise HTTPException(status_code=400, detail="Email already registered")

    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user = User(
        email=email,
        password=hash_password(password),
        role="patient"
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

    db.add(patient)
    db.commit()

    return {"message": "User registered successfully"}

def verify_user(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()
