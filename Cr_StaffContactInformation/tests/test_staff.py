import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from Cr_StaffContactInformation.app.main import app
from Cr_StaffContactInformation.app.staff_contact_database import Base, engine
from Cr_StaffContactInformation.app.staff_contact_model import Department, Specialty

client = TestClient(app)


def setup_module():
    Base.metadata.create_all(bind=engine)


def teardown_module():
    Base.metadata.drop_all(bind=engine)


def test_create_staff():
    db = Session(bind=engine)

    # Crear registros requeridos por las FK
    department = Department(
        name="Cardiology",
        description="Heart department"
    )

    specialty = Specialty(
        name="Cardiologist",
        description="Heart specialist"
    )

    db.add(department)
    db.add(specialty)
    db.commit()
    db.refresh(department)
    db.refresh(specialty)

    response = client.post(
        "/api/staff/",
        json={
            "first_name": "Ana",
            "last_name": "Lopez",
            "email": "ana.lopez@test.com",
            "phone_number": "12345678",
            "start_date": "2024-01-01",
            "status": "Active",
            "role_level": "Senior",
            "department_id": department.id,
            "specialty_id": specialty.id
        }
    )

    assert response.status_code == 201
    data = response.json()

    assert data["first_name"] == "Ana"
    assert data["department_id"] == department.id

def test_get_staff():
    db = Session(bind=engine)

    # Crear registros necesarios
    department = Department(
        name="Neurology",
        description="Brain department"
    )

    specialty = Specialty(
        name="Neurologist",
        description="Brain specialist"
    )

    db.add(department)
    db.add(specialty)
    db.commit()
    db.refresh(department)
    db.refresh(specialty)

    # Crear staff
    create_response = client.post(
        "/api/staff/",
        json={
            "first_name": "Carlos",
            "last_name": "Perez",
            "email": "carlos.perez@test.com",
            "phone_number": "87654321",
            "start_date": "2024-01-01",
            "status": "Active",
            "role_level": "Junior",
            "department_id": department.id,
            "specialty_id": specialty.id
        }
    )

    assert create_response.status_code == 201

    created_staff = create_response.json()
    staff_id = created_staff["id"]

    # Ahora hacer GET
    get_response = client.get(f"/api/staff/{staff_id}")

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["id"] == staff_id
    assert data["first_name"] == "Carlos"
    assert data["email"] == "carlos.perez@test.com"