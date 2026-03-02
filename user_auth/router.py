"""
router.py
---------
Single Responsibility: Defines authentication HTTP endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from user_auth.security import verify_password

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