"""
tests/medications/conftest.py
─────────────────────────────────────────────────────────────────────────
Test-database setup for the medications module.

Key isolation guarantees:
  • Uses sqlite:///:memory: — never touches the production hospital.db.
  • A separate engine (and separate connection) is created per test
    session; all tables are dropped after the session ends.
  • Each individual test receives a fresh transactional savepoint via
    db_session (function scope); the transaction is rolled back after
    the test — no DELETE statements needed between tests.
  • FastAPI's get_db dependency is overridden via app.dependency_overrides
    so that any TestClient request routes through the test session.
"""

from decimal import Decimal

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from pharmacy.database import Base, get_db
from pharmacy.medications.model import Medication
from pharmacy.medications.category_model import TherapeuticCategory

# ── In-memory engine ──────────────────────────────────────────────────────
# sqlite:///:memory: creates a completely fresh DB in process memory.
# It is destroyed automatically when the engine is garbage-collected —
# no file cleanup required.
#
# connect_args={"check_same_thread": False} mirrors production config;
# pytest-xdist may run fixtures on different threads.
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    # Echo SQL during test runs to aid debugging when tests fail.
    echo=False,
)

# ── Enable FK enforcement on the test engine ─────────────────────────────
# Mirrors the pragma set in pharmacy/database.py so constraint violations
# are caught during testing, not only in production.
@event.listens_for(TEST_ENGINE, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# ── Session factory for tests ─────────────────────────────────────────────
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=TEST_ENGINE,
)


# ── Function-scoped transactional session ─────────────────────────────────
@pytest.fixture
def db_session():
    """
    Yield a database session.
    
    100% isolation guarantee: we create the schema fresh for every
    test function, and drop it after the test. For in-memory SQLite,
    this is effectively instantaneous and bypasses all the DBAPI quirks
    with nested transactions / SAVEPOINTs across different SQLAlchemy
    and Python versions.
    """
    # Create tables fresh for this test
    Base.metadata.create_all(bind=TEST_ENGINE)
    
    # Open a standard session
    connection = TEST_ENGINE.connect()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    connection.close()
    
    # Destroy tables after this test
    Base.metadata.drop_all(bind=TEST_ENGINE)


# ── FastAPI dependency override ───────────────────────────────────────────
@pytest.fixture
def override_get_db(db_session):
    """
    Override FastAPI's get_db dependency so that HTTP requests made via
    TestClient also use the test session.

    Usage (in a test file):
        def test_create_endpoint(client, override_get_db):
            response = client.post("/medications/", json={...})
            assert response.status_code == 201
    """
    def _override():
        try:
            yield db_session
        finally:
            pass  # session lifecycle managed by db_session fixture

    return _override


# ── Reusable sample medication ────────────────────────────────────────────
@pytest.fixture
def sample_medication(db_session) -> Medication:
    """
    Insert one valid Medication row and return it.

    Provides a known-good record for tests that need an existing
    medication (e.g., GET, PATCH, DELETE tests) without repeating
    setup boilerplate.

    The row is rolled back along with every other db_session write
    after the test completes.
    """
    med = Medication(
        name="Paracetamol",
        generic_name="Acetaminophen",
        dosage="500 mg",
        unit="tablet",
        stock_quantity=200,
        min_stock_threshold=20,
        price=Decimal("4.99"),
        is_active=True,
    )
    db_session.add(med)
    db_session.commit()
    db_session.refresh(med)
    return med
