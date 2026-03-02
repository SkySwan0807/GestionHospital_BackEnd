import pytest
from fastapi.testclient import TestClient

from app.clients.specialty_client import SpecialtyServiceUnavailableError

def test_create_license_success(client: TestClient, mock_sc):
    mock_sc.validate_specialty.return_value = True
    response = client.post(
        "/api/v1/licenses",
        json={
            "staff_id": "STF-1001",
            "specialty_id": 5,
            "license_number": "MD-987654321",
            "issue_date": "2023-01-15",
            "expiration_date": "2025-01-15",
            "status": "Active"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["license_number"] == "MD-987654321"

def test_create_license_duplicate(client: TestClient, mock_sc):
    payload = {
        "staff_id": "STF-1001",
        "specialty_id": 5,
        "license_number": "DUP-123",
        "issue_date": "2023-01-15",
        "expiration_date": "2025-01-15",
        "status": "Active"
    }
    client.post("/api/v1/licenses", json=payload)
    
    response = client.post("/api/v1/licenses", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "License number already exists"

def test_create_license_bad_specialty(client: TestClient, mock_sc):
    mock_sc.validate_specialty.return_value = False
    response = client.post(
        "/api/v1/licenses",
        json={
            "staff_id": "STF-1001",
            "specialty_id": 999,
            "license_number": "BAD-SPEC-123",
            "issue_date": "2023-01-15",
            "expiration_date": "2025-01-15",
            "status": "Active"
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Specialty not found"

def test_create_license_service_down(client: TestClient, mock_sc):
    mock_sc.validate_specialty.side_effect = SpecialtyServiceUnavailableError("Down")
    response = client.post(
        "/api/v1/licenses",
        json={
            "staff_id": "STF-1001",
            "specialty_id": 5,
            "license_number": "FAIL-123",
            "issue_date": "2023-01-15",
            "expiration_date": "2025-01-15",
            "status": "Active"
        },
    )
    assert response.status_code == 424
    assert response.json()["detail"] == "Specialty service unavailable"

def test_create_license_empty_number(client: TestClient, mock_sc):
    response = client.post(
        "/api/v1/licenses",
        json={
            "staff_id": "STF-1001",
            "specialty_id": 5,
            "license_number": "   ",
            "issue_date": "2023-01-15",
            "expiration_date": "2025-01-15",
            "status": "Active"
        },
    )
    assert response.status_code == 422


def test_get_all_licenses(client: TestClient, mock_sc):
    client.post(
        "/api/v1/licenses",
        json={
            "staff_id": "STF-1001",
            "specialty_id": 5,
            "license_number": "ALL-123",
            "issue_date": "2023-01-15",
            "expiration_date": "2025-01-15",
            "status": "Active"
        },
    )
    response = client.get("/api/v1/licenses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["license_number"] == "ALL-123"

def test_get_licenses_filter_status(client: TestClient, mock_sc):
    client.post(
        "/api/v1/licenses",
        json={
            "staff_id": "STF-1001",
            "specialty_id": 5,
            "license_number": "STAT-ACT",
            "issue_date": "2023-01-15",
            "expiration_date": "2025-01-15",
            "status": "Active"
        },
    )
    client.post(
        "/api/v1/licenses",
        json={
            "staff_id": "STF-1002",
            "specialty_id": 5,
            "license_number": "STAT-EXP",
            "issue_date": "2020-01-15",
            "expiration_date": "2021-01-15",
            "status": "Expired"
        },
    )
    response = client.get("/api/v1/licenses?status=Active")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "Active"

def test_get_license_by_id_found(client: TestClient, mock_sc):
    resp = client.post(
        "/api/v1/licenses",
        json={
            "staff_id": "STF-1001",
            "specialty_id": 5,
            "license_number": "FIND-ME",
            "issue_date": "2023-01-15",
            "expiration_date": "2025-01-15",
            "status": "Active"
        },
    )
    license_id = resp.json()["id"]
    
    response = client.get(f"/api/v1/licenses/{license_id}")
    assert response.status_code == 200
    assert response.json()["id"] == license_id

def test_get_license_by_id_not_found(client: TestClient, mock_sc):
    response = client.get("/api/v1/licenses/999")
    assert response.status_code == 404

def test_update_license_status(client: TestClient, mock_sc):
    resp = client.post(
        "/api/v1/licenses",
        json={
            "staff_id": "STF-1001",
            "specialty_id": 5,
            "license_number": "UPD-123",
            "issue_date": "2023-01-15",
            "expiration_date": "2025-01-15",
            "status": "Active"
        },
    )
    license_id = resp.json()["id"]
    
    response = client.put(
        f"/api/v1/licenses/{license_id}",
        json={"status": "Expired"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Expired"
    assert data["expiration_date"] == "2025-01-15"

def test_update_license_not_found(client: TestClient, mock_sc):
    response = client.put("/api/v1/licenses/999", json={"status": "Expired"})
    assert response.status_code == 404

def test_delete_license_success(client: TestClient, mock_sc):
    create_resp = client.post(
        "/api/v1/licenses",
        json={
            "staff_id": "STF-1001",
            "specialty_id": 5,
            "license_number": "DEL-123",
            "issue_date": "2023-01-15",
            "expiration_date": "2025-01-15",
            "status": "Active"
        },
    )
    license_id = create_resp.json()["id"]
    
    del_resp = client.delete(f"/api/v1/licenses/{license_id}")
    assert del_resp.status_code == 204
    
    get_resp = client.get(f"/api/v1/licenses/{license_id}")
    assert get_resp.status_code == 404

def test_delete_license_not_found(client: TestClient, mock_sc):
    response = client.delete("/api/v1/licenses/999")
    assert response.status_code == 404
