"""
tests/medications/test_router.py
──────────────────────────────────────────────────────────────────────────
Integration tests for all HTTP endpoints (medications + categories).

Every test uses TestClient backed by an in-memory SQLite database via the
db_session / override_get_db fixtures from conftest.py.

Test categories:
  A) Medication CRUD
  B) Stock adjustment
  C) Low-stock alert
  D) Therapeutic category CRUD
"""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

from pharmacy.main import app
from pharmacy.database import get_db


# ── Fixture: HTTP test client with DB override ────────────────────────────

@pytest.fixture
def client(override_get_db, db_session):
    """
    Return a TestClient that routes ALL requests through the in-memory
    test DB session (never touches hospital.db).
    """
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helpers ───────────────────────────────────────────────────────────────

def _med_payload(**overrides) -> dict:
    """Minimum valid medication payload."""
    base = {
        "name": "Ibuprofen",
        "generic_name": "Ibuprofen INN",
        "dosage": "400 mg",
        "price": "8.50",
        "stock_quantity": 50,
        "min_stock_threshold": 10,
    }
    base.update(overrides)
    return base


def _cat_payload(**overrides) -> dict:
    """Minimum valid therapeutic category payload."""
    base = {"name": "Analgesic"}
    base.update(overrides)
    return base


# ══════════════════════════════════════════════════════════════════════════
# A) MEDICATION CRUD
# ══════════════════════════════════════════════════════════════════════════

class TestMedicationCreate:
    def test_create_success_returns_201(self, client):
        """POST /medications/ with valid payload → 201 + full object."""
        r = client.post("/medications/", json=_med_payload())
        assert r.status_code == 201
        data = r.json()
        assert data["id"] is not None
        assert data["name"] == "Ibuprofen"
        assert data["generic_name"] == "Ibuprofen INN"
        assert data["dosage"] == "400 mg"
        assert data["price"] == "8.50"
        assert data["stock_quantity"] == 50
        assert data["min_stock_threshold"] == 10
        assert data["is_active"] is True
        assert data["created_at"] is not None

    def test_create_missing_required_field_returns_422(self, client):
        """POST /medications/ without dosage → 422."""
        payload = _med_payload()
        del payload["dosage"]
        r = client.post("/medications/", json=payload)
        assert r.status_code == 422

    def test_create_price_zero_returns_422(self, client):
        """POST /medications/ with price=0 → 422 (must be > 0)."""
        r = client.post("/medications/", json=_med_payload(price="0"))
        assert r.status_code == 422

    def test_create_duplicate_name_generic_returns_409(self, client):
        """POST same (name, generic_name) twice → 409 Conflict."""
        client.post("/medications/", json=_med_payload())
        r = client.post("/medications/", json=_med_payload())
        assert r.status_code == 409

    def test_create_with_valid_category_returns_201(self, client):
        """POST with a real therapeutic_category_id → 201."""
        cat = client.post("/categories/", json=_cat_payload()).json()
        r = client.post("/medications/", json=_med_payload(therapeutic_category_id=cat["id"]))
        assert r.status_code == 201
        assert r.json()["therapeutic_category_id"] == cat["id"]

    def test_create_with_invalid_category_returns_422(self, client):
        """POST with a non-existent therapeutic_category_id → 422."""
        r = client.post("/medications/", json=_med_payload(therapeutic_category_id=9999))
        assert r.status_code == 422


class TestMedicationList:
    def test_list_returns_200(self, client):
        """GET /medications/ → 200 + list."""
        client.post("/medications/", json=_med_payload())
        r = client.get("/medications/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert len(r.json()) == 1

    def test_inactive_medication_excluded_from_list(self, client):
        """Inactive medications do not appear in GET /medications/."""
        created = client.post("/medications/", json=_med_payload()).json()
        client.patch(f"/medications/{created['id']}", json={"is_active": False})
        r = client.get("/medications/")
        assert r.status_code == 200
        assert len(r.json()) == 0


class TestMedicationGet:
    def test_get_existing_returns_200(self, client):
        """GET /medications/{id} for a known record → 200."""
        created = client.post("/medications/", json=_med_payload()).json()
        r = client.get(f"/medications/{created['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_nonexistent_returns_404(self, client):
        """GET /medications/9999 → 404."""
        r = client.get("/medications/9999")
        assert r.status_code == 404


class TestMedicationUpdate:
    def test_patch_single_field_returns_200(self, client):
        """PATCH with one field → 200; other fields unchanged."""
        created = client.post("/medications/", json=_med_payload()).json()
        r = client.patch(f"/medications/{created['id']}", json={"dosage": "800 mg"})
        assert r.status_code == 200
        assert r.json()["dosage"] == "800 mg"
        assert r.json()["name"] == "Ibuprofen"

    def test_patch_empty_body_is_noop(self, client):
        """PATCH {} → 200 with no changes (exclude_unset=True)."""
        created = client.post("/medications/", json=_med_payload()).json()
        r = client.patch(f"/medications/{created['id']}", json={})
        assert r.status_code == 200
        assert r.json()["name"] == "Ibuprofen"

    def test_patch_nonexistent_returns_404(self, client):
        """PATCH /medications/9999 → 404."""
        r = client.patch("/medications/9999", json={"dosage": "100 mg"})
        assert r.status_code == 404


class TestMedicationDelete:
    def test_delete_existing_returns_204(self, client):
        """DELETE /medications/{id} → 204 No Content."""
        created = client.post("/medications/", json=_med_payload()).json()
        r = client.delete(f"/medications/{created['id']}")
        assert r.status_code == 204

    def test_delete_nonexistent_returns_404(self, client):
        """DELETE /medications/9999 → 404."""
        r = client.delete("/medications/9999")
        assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# B) STOCK ADJUSTMENT
# ══════════════════════════════════════════════════════════════════════════

class TestStockAdjustment:
    def test_set_stock_to_valid_value_returns_200(self, client):
        """POST /{id}/stock?quantity=100 → 200 + updated stock_quantity."""
        created = client.post("/medications/", json=_med_payload()).json()
        r = client.post(f"/medications/{created['id']}/stock?quantity=100")
        assert r.status_code == 200
        assert r.json()["stock_quantity"] == 100

    def test_set_stock_to_zero_returns_200(self, client):
        """POST /{id}/stock?quantity=0 → 200 (zero is valid)."""
        created = client.post("/medications/", json=_med_payload()).json()
        r = client.post(f"/medications/{created['id']}/stock?quantity=0")
        assert r.status_code == 200
        assert r.json()["stock_quantity"] == 0

    def test_negative_stock_returns_422(self, client):
        """POST /{id}/stock?quantity=-1 → 422 Unprocessable Entity (InvalidStockException)."""
        created = client.post("/medications/", json=_med_payload()).json()
        r = client.post(f"/medications/{created['id']}/stock?quantity=-1")
        assert r.status_code == 422

    def test_stock_on_nonexistent_medication_returns_404(self, client):
        """POST /medications/9999/stock?quantity=10 → 404."""
        r = client.post("/medications/9999/stock?quantity=10")
        assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# C) LOW-STOCK ALERT
# ══════════════════════════════════════════════════════════════════════════

class TestLowStock:
    def test_low_stock_returns_only_critical_medications(self, client):
        """
        Two meds: one below threshold, one above.
        GET /medications/low-stock must return only the one below.
        """
        # Below threshold: stock=5, threshold=10 → ALERT
        client.post("/medications/", json=_med_payload(
            name="MedA", generic_name="MedA INN",
            stock_quantity=5, min_stock_threshold=10,
        ))
        # Above threshold: stock=100, threshold=10 → OK
        client.post("/medications/", json=_med_payload(
            name="MedB", generic_name="MedB INN",
            stock_quantity=100, min_stock_threshold=10,
        ))

        r = client.get("/medications/low-stock")
        assert r.status_code == 200
        names = [m["name"] for m in r.json()]
        assert "MedA" in names
        assert "MedB" not in names

    def test_zero_threshold_excluded_from_low_stock(self, client):
        """Medications with min_stock_threshold=0 are never in low-stock results."""
        client.post("/medications/", json=_med_payload(
            name="MedC", generic_name="MedC INN",
            stock_quantity=0, min_stock_threshold=0,
        ))
        r = client.get("/medications/low-stock")
        assert r.status_code == 200
        assert all(m["name"] != "MedC" for m in r.json())

    def test_low_stock_empty_when_no_critical_meds(self, client):
        """GET /medications/low-stock returns empty list when all meds have enough stock."""
        client.post("/medications/", json=_med_payload(
            stock_quantity=100, min_stock_threshold=10,
        ))
        r = client.get("/medications/low-stock")
        assert r.status_code == 200
        assert r.json() == []


# ══════════════════════════════════════════════════════════════════════════
# D) THERAPEUTIC CATEGORY CRUD
# ══════════════════════════════════════════════════════════════════════════

class TestCategoryCreate:
    def test_create_category_success(self, client):
        """POST /categories/ with valid payload → 201 + id."""
        r = client.post("/categories/", json=_cat_payload(description="Pain relief drugs"))
        assert r.status_code == 201
        data = r.json()
        assert data["id"] is not None
        assert data["name"] == "Analgesic"
        assert data["description"] == "Pain relief drugs"

    def test_create_category_duplicate_name_returns_409(self, client):
        """POST same category name twice → 409 Conflict."""
        client.post("/categories/", json=_cat_payload())
        r = client.post("/categories/", json=_cat_payload())
        assert r.status_code == 409

    def test_create_category_missing_name_returns_422(self, client):
        """POST without name → 422."""
        r = client.post("/categories/", json={"description": "No name"})
        assert r.status_code == 422


class TestCategoryList:
    def test_list_categories_returns_200(self, client):
        """GET /categories/ → 200 + list."""
        client.post("/categories/", json=_cat_payload())
        r = client.get("/categories/")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_list_categories_empty_on_fresh_db(self, client):
        """GET /categories/ with no data → 200 + empty list."""
        r = client.get("/categories/")
        assert r.status_code == 200
        assert r.json() == []


class TestCategoryGet:
    def test_get_existing_category(self, client):
        """GET /categories/{id} → 200."""
        created = client.post("/categories/", json=_cat_payload()).json()
        r = client.get(f"/categories/{created['id']}")
        assert r.status_code == 200
        assert r.json()["name"] == "Analgesic"

    def test_get_nonexistent_category_returns_404(self, client):
        """GET /categories/9999 → 404."""
        r = client.get("/categories/9999")
        assert r.status_code == 404


class TestCategoryUpdate:
    def test_patch_category_name(self, client):
        """PATCH /categories/{id} changing name → 200 with updated name."""
        created = client.post("/categories/", json=_cat_payload()).json()
        r = client.patch(f"/categories/{created['id']}", json={"name": "Anti-inflammatory"})
        assert r.status_code == 200
        assert r.json()["name"] == "Anti-inflammatory"

    def test_patch_nonexistent_category_returns_404(self, client):
        """PATCH /categories/9999 → 404."""
        r = client.patch("/categories/9999", json={"name": "X"})
        assert r.status_code == 404

    def test_patch_category_duplicate_name_returns_409(self, client):
        """PATCH a category to collide with another name → 409."""
        client.post("/categories/", json={"name": "Antibiotic"})
        cat2 = client.post("/categories/", json={"name": "Analgesic"}).json()
        r = client.patch(f"/categories/{cat2['id']}", json={"name": "Antibiotic"})
        assert r.status_code == 409


class TestCategoryDelete:
    def test_delete_existing_category_returns_204(self, client):
        """DELETE /categories/{id} → 204."""
        created = client.post("/categories/", json=_cat_payload()).json()
        r = client.delete(f"/categories/{created['id']}")
        assert r.status_code == 204

    def test_delete_nonexistent_category_returns_404(self, client):
        """DELETE /categories/9999 → 404."""
        r = client.delete("/categories/9999")
        assert r.status_code == 404
