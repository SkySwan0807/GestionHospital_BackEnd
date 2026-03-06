"""
router.py
---------
Single Responsibility: Defines authentication HTTP endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from user_auth.security import verify_password
from user_auth.password_reset_store import store_code, verify_code
from user_auth.email_service import send_reset_email
from user_auth.security import hash_password

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

    if not verify_password(password, user.password_hash):
        return {"success": False, "message": "Invalid credentials"}

    return {
        "success": True,
        "message": "Login successful",
        "role": user.role
    }

@router.post("/forgot_password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"message": "The email does not exist in our records"}

    code = store_code(email)
    send_reset_email(email, code)

    return {"message": "Code sent to email if it exists in our records Email: " + email}


@router.post("/reset_password")
def reset_password(
    email: str,
    code: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid user")

    if not verify_code(email, code):
        raise HTTPException(status_code=400, detail="Invalid or expired code")


    user.password_hash = hash_password(new_password)
    db.commit()

    return {"message": "Password updated successfully"}