"""
tests/medications/test_model.py
──────────────────────────────────────────────────────────────────────────
Model-layer unit tests for the Medication ORM.

Scope:
  • Tests DB constraints (NOT NULL, UNIQUE, DEFAULT) and ORM column mapping.
  • Does NOT test business rules — those belong in test_service.py.
  • Every test is independent: the db_session fixture rolls back the entire
    transaction after each test, so no state bleeds between tests.
  • sample_medication fixture (from conftest.py) is used as the base record
    for tests that need an existing row.

Fixture dependency graph:
  db_session (function-scoped, transactional)
    └── sample_medication (function-scoped, reuses db_session)

Testing the DB constraint directly (NOT via service):
  Instantiate Medication objects, db_session.add(), then commit inside
  pytest.raises(IntegrityError). Call db_session.rollback() immediately
  after to recover the session before the conftest teardown runs.
"""

import time
from datetime import date, datetime
from decimal import Decimal

import pytest
import sqlalchemy.exc

from pharmacy.medications.model import Medication


# ── Helper: minimum valid payload (excludes restricted auto-fields) ────────
def _make_medication(**overrides) -> Medication:
    """
    Return a Medication instance with valid defaults for all NOT NULL fields.

    Tests that only care about one specific field inject overrides.
    Keeps test bodies focused on the single behaviour under test.
    """
    defaults = dict(
        name="Metformin",
        generic_name="Metformin HCl",
        dosage="850 mg",
        price=Decimal("3.20"),
    )
    defaults.update(overrides)
    return Medication(**defaults)


# ══════════════════════════════════════════════════════════════════════════
# 1. CREATE — happy path
# ══════════════════════════════════════════════════════════════════════════

def test_create_medication_success(sample_medication):
    """
    ARRANGE: sample_medication fixture inserts a valid Paracetamol row.
    ACT:     Fixture already committed; we inspect the returned instance.
    ASSERT:  All supplied fields are persisted; auto-fields are populated.
    """
    med = sample_medication

    assert med.id is not None,               "PK must be auto-assigned after commit"
    assert med.name == "Paracetamol"
    assert med.generic_name == "Acetaminophen"
    assert med.dosage == "500 mg"
    assert med.unit == "tablet"
    assert med.stock_quantity == 200
    assert med.min_stock_threshold == 20
    assert med.price == Decimal("4.99")
    assert med.is_active is True,            "is_active must default to True"
    assert med.created_at is not None,       "created_at must be set by server_default"


# ══════════════════════════════════════════════════════════════════════════
# 2. CONSTRAINT — name NOT NULL
# ══════════════════════════════════════════════════════════════════════════

def test_medication_name_cannot_be_null(db_session):
    """
    ARRANGE: Build a Medication with name=None.
    ACT:     Attempt to commit to the DB.
    ASSERT:  SQLite raises IntegrityError (NOT NULL constraint on `name`).

    Note: The exception fires at commit time (DB-side), NOT at db.add()
    (Python-side). SQLAlchemy propagates it as IntegrityError.
    """
    med = _make_medication(name=None)
    db_session.add(med)

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db_session.commit()

    # Recover the session so the conftest teardown rollback works cleanly.
    db_session.rollback()


# ══════════════════════════════════════════════════════════════════════════
# 3. DEFAULT — stock_quantity
# ══════════════════════════════════════════════════════════════════════════

def test_medication_stock_quantity_defaults_to_zero(db_session):
    """
    ARRANGE: Build a Medication without specifying stock_quantity.
    ACT:     Commit and refresh.
    ASSERT:  stock_quantity is 0 (Column default).
    """
    med = _make_medication()   # stock_quantity not supplied
    db_session.add(med)
    db_session.commit()
    db_session.refresh(med)

    assert med.stock_quantity == 0


# ══════════════════════════════════════════════════════════════════════════
# 4. DEFAULT — is_active
# ══════════════════════════════════════════════════════════════════════════

def test_medication_is_active_defaults_to_true(db_session):
    """
    ARRANGE: Build a Medication without specifying is_active.
    ACT:     Commit and refresh.
    ASSERT:  is_active is True (Column default).

    SQLite stores BOOLEAN as INTEGER (0 / 1). SQLAlchemy converts it back
    to a Python bool on read — this test also implicitly verifies that
    type coercion is working correctly.
    """
    med = _make_medication()   # is_active not supplied
    db_session.add(med)
    db_session.commit()
    db_session.refresh(med)

    assert med.is_active is True


# ══════════════════════════════════════════════════════════════════════════
# 5. UNIQUE CONSTRAINT — composite (name, generic_name)
# ══════════════════════════════════════════════════════════════════════════

def test_duplicate_name_and_generic_name_raises_integrity_error(db_session):
    """
    ARRANGE: Insert a medication with name='Amoxicillin', generic='Amoxicillin INN'.
    ACT:     Attempt to insert a second record with the same (name, generic_name).
    ASSERT:  DB raises IntegrityError on the second commit.

    This test intentionally bypasses the service layer to verify the DB-level
    UniqueConstraint independently. The service-level duplicate check provides
    a better error message; this constraint is the safety net.
    """
    first = _make_medication(name="Amoxicillin", generic_name="Amoxicillin INN")
    db_session.add(first)
    db_session.commit()

    # ACT — second row with same composite key
    second = _make_medication(
        name="Amoxicillin",
        generic_name="Amoxicillin INN",
        dosage="500 mg",          # different dosage — still a duplicate per constraint
    )
    db_session.add(second)

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db_session.commit()

    db_session.rollback()


# ══════════════════════════════════════════════════════════════════════════
# 6. AUDIT — updated_at changes after modification
# ══════════════════════════════════════════════════════════════════════════

def test_updated_at_changes_after_modification(db_session):
    """
    ARRANGE: Insert a medication and capture the initial updated_at value.
    ACT:     Modify stock_quantity, commit, and refresh.
    ASSERT:  updated_at after modification differs from updated_at at creation.

    Why sleep(0.01)?
      created_at uses server_default=func.now() → SQLite CURRENT_TIMESTAMP
      (second-level precision, no microseconds, e.g. "2026-03-06 21:39:05").
      updated_at after an UPDATE uses onupdate=datetime.utcnow (Python-level,
      full microsecond precision, e.g. "2026-03-06 21:39:05.017832").
      The 10ms sleep ensures the two values can never be identical even if
      both happen within the same wall-clock second.
    """
    med = _make_medication(stock_quantity=50)
    db_session.add(med)
    db_session.commit()
    db_session.refresh(med)

    updated_at_before = med.updated_at   # captured right after INSERT

    time.sleep(0.01)  # ensure datetime.utcnow() on UPDATE differs from server_default

    # ACT
    med.stock_quantity = 75
    db_session.commit()
    db_session.refresh(med)

    # ASSERT
    assert med.updated_at is not None, "updated_at must be set after modification"
    assert med.updated_at != updated_at_before, (
        "updated_at must change after a committed UPDATE; "
        f"before={updated_at_before!r}, after={med.updated_at!r}"
    )


# ══════════════════════════════════════════════════════════════════════════
# 7. DATE FIELD — expiration_date round-trip
# ══════════════════════════════════════════════════════════════════════════

def test_expiration_date_accepts_valid_date(db_session):
    """
    ARRANGE: Build a Medication with a specific expiration_date.
    ACT:     Commit and refresh.
    ASSERT:  The retrieved expiration_date matches the inserted Python date object.

    SQLite stores DATE as a text string ("YYYY-MM-DD"). SQLAlchemy's Date
    column type transparently converts it back to a Python date on read.
    This test verifies that round-trip serialisation is correct.
    """
    target_date = date(2027, 6, 30)

    med = _make_medication(expiration_date=target_date)
    db_session.add(med)
    db_session.commit()
    db_session.refresh(med)

    assert isinstance(med.expiration_date, date), (
        "expiration_date must be returned as a Python date object, "
        f"got {type(med.expiration_date)}"
    )
    assert med.expiration_date == target_date

