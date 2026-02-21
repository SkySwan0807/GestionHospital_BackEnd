"""
tests/test_specialties.py
-------------------------
Single Responsibility: Integration tests for the /specialties endpoints.

These tests use FastAPI's TestClient (built on httpx) to make real HTTP requests
against an in-memory SQLite test database — NOT the production hospital.db file.

Test coverage:
  - POST /api/v1/specialties   → 201 Created (success)
  - POST /api/v1/specialties   → 422 Unprocessable Entity (missing required field)
  - POST /api/v1/specialties   → 409 Conflict (duplicate name)
  - GET  /api/v1/specialties   → 200 OK (empty list)
  - GET  /api/v1/specialties   → 200 OK (list with items after creation)
  - GET  /api/v1/specialties/{id} → 200 OK (single item)
  - GET  /api/v1/specialties/{id} → 404 Not Found (non-existent id)

Imports from: app.main (app instance), app.database (Base, engine, get_db)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# ---------------------------------------------------------------------------
# Test Database Configuration
# ---------------------------------------------------------------------------
# Use a SEPARATE in-memory SQLite database for tests.
# This ensures tests never touch the real hospital.db file.
# Each test run starts with a clean, empty database.
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_hospital.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """
    Override the get_db dependency to use the test database session instead
    of the production SessionLocal. FastAPI's dependency injection system
    allows this without modifying any application code.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Pytest Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """
    Fixture that runs before and after EVERY test function.
    - Before: Creates all tables in the test DB
    - After:  Drops all tables so the next test starts clean
    This guarantees test isolation — no test pollutes the next.
    """
    Base.metadata.create_all(bind=test_engine)
    # Override the production DB dependency with the test DB
    app.dependency_overrides[get_db] = override_get_db
    yield
    # Teardown: drop all tables after each test
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client():
    """
    Provides a TestClient instance that makes real HTTP requests
    to the FastAPI app without starting an actual server.
    """
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

class TestCreateSpecialty:
    """Tests for POST /api/v1/specialties"""

    def test_create_specialty_success(self, client):
        """Should create a specialty and return 201 with the created object."""
        payload = {
            "name": "Cardiology",
            "description": "Diagnosis and treatment of heart diseases",
        }
        response = client.post("/api/v1/specialties/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Cardiology"
        assert data["description"] == "Diagnosis and treatment of heart diseases"
        assert "id" in data
        assert "created_at" in data
        assert isinstance(data["id"], int)

    def test_create_specialty_without_description(self, client):
        """Description is optional — should succeed with only a name."""
        payload = {"name": "Neurology"}
        response = client.post("/api/v1/specialties/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Neurology"
        assert data["description"] is None

    def test_create_specialty_missing_name(self, client):
        """Name is required — should return 422 Unprocessable Entity."""
        payload = {"description": "A specialty without a name"}
        response = client.post("/api/v1/specialties/", json=payload)

        assert response.status_code == 422

    def test_create_specialty_name_too_short(self, client):
        """Name must be at least 2 characters — should return 422."""
        payload = {"name": "X"}
        response = client.post("/api/v1/specialties/", json=payload)

        assert response.status_code == 422

    def test_create_specialty_duplicate_name(self, client):
        """Duplicate name should return 409 Conflict, not 500."""
        payload = {"name": "Cardiology", "description": "Heart stuff"}
        client.post("/api/v1/specialties/", json=payload)  # First creation

        response = client.post("/api/v1/specialties/", json=payload)  # Duplicate

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]


class TestGetSpecialties:
    """Tests for GET /api/v1/specialties"""

    def test_get_specialties_empty(self, client):
        """Should return an empty list when no specialties exist."""
        response = client.get("/api/v1/specialties/")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_specialties_with_data(self, client):
        """Should return all created specialties."""
        client.post("/api/v1/specialties/", json={"name": "Cardiology"})
        client.post("/api/v1/specialties/", json={"name": "Neurology"})

        response = client.get("/api/v1/specialties/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [item["name"] for item in data]
        assert "Cardiology" in names
        assert "Neurology" in names

    def test_get_specialty_by_id(self, client):
        """Should return a single specialty by its ID."""
        create_response = client.post("/api/v1/specialties/", json={"name": "Oncology"})
        created_id = create_response.json()["id"]

        response = client.get(f"/api/v1/specialties/{created_id}")

        assert response.status_code == 200
        assert response.json()["name"] == "Oncology"

    def test_get_specialty_not_found(self, client):
        """Should return 404 when the ID does not exist."""
        response = client.get("/api/v1/specialties/9999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestHealthCheck:
    """Tests for the root health-check endpoint."""

    def test_root_health_check(self, client):
        """Should return 200 with a running message."""
        response = client.get("/")

        assert response.status_code == 200
        assert "running" in response.json()["message"]
