import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.clients.specialty_client import SpecialtyClient

load_dotenv()

STORY1_API_URL = os.getenv("STORY1_API_URL", "http://localhost:8000")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_specialty_client() -> SpecialtyClient:
    return SpecialtyClient(base_url=STORY1_API_URL)
