from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.clients.specialty_client import SpecialtyClient
from app.database import Base
from app.dependencies import get_db, get_specialty_client
from app.main import app
from app.models import License

# Create in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


class MockSpecialtyClient:
    def __init__(self):
        self.validate_specialty = AsyncMock(return_value=True)


@pytest.fixture(scope="function")
def mock_sc():
    """Returns a fresh instance of MockSpecialtyClient per test."""
    client = MockSpecialtyClient()
    app.dependency_overrides[get_specialty_client] = lambda: client
    return client


@pytest.fixture(scope="function")
def client(mock_sc):
    """
    Returns a TestClient instance. 
    Also recreates tables before each test to ensure a clean database state.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
