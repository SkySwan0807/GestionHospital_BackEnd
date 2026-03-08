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

    get_response = client.get(f"/api/staff/{staff_id}")

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["id"] == staff_id
    assert data["first_name"] == "Carlos"
    assert data["email"] == "carlos.perez@test.com"

def test_update_staff_first_name():
    db = Session(bind=engine)

    department = Department(name="TestDept", description="Desc")
    specialty = Specialty(name="TestSpec", description="Desc")

    db.add(department)
    db.add(specialty)
    db.commit()
    db.refresh(department)
    db.refresh(specialty)

    create_response = client.post(
        "/api/staff/",
        json={
            "first_name": "Maria",
            "last_name": "Gomez",
            "email": "maria@test.com",
            "phone_number": "12345678",
            "start_date": "2024-01-01",
            "status": "Active",
            "role_level": "Junior",
            "department_id": department.id,
            "specialty_id": specialty.id
        }
    )

    staff_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/staff/{staff_id}",
        json={"first_name": "NuevoNombre"}
    )

    assert update_response.status_code == 200
    assert update_response.json()["first_name"] == "NuevoNombre"

def test_update_email_duplicate():
    db = Session(bind=engine)

    department = Department(name="DeptX", description="Desc")
    specialty = Specialty(name="SpecX", description="Desc")

    db.add(department)
    db.add(specialty)
    db.commit()
    db.refresh(department)
    db.refresh(specialty)

    # Staff 1
    client.post("/api/staff/", json={
        "first_name": "A",
        "last_name": "A",
        "email": "a@test.com",
        "phone_number": "11111111",
        "start_date": "2024-01-01",
        "status": "Active",
        "role_level": "Junior",
        "department_id": department.id,
        "specialty_id": specialty.id
    })

    # Staff 2
    staff2 = client.post("/api/staff/", json={
        "first_name": "B",
        "last_name": "B",
        "email": "b@test.com",
        "phone_number": "22222222",
        "start_date": "2024-01-01",
        "status": "Active",
        "role_level": "Junior",
        "department_id": department.id,
        "specialty_id": specialty.id
    })

    staff2_id = staff2.json()["id"]

    # Intentar duplicar email
    response = client.patch(
        f"/api/staff/{staff2_id}",
        json={"email": "a@test.com"}
    )

    assert response.status_code == 400

def test_update_staff_not_found():
    response = client.patch(
        "/api/staff/9999",
        json={"first_name": "Ghost"}
    )

    assert response.status_code == 404

def test_update_restricted_field():
    db = Session(bind=engine)

    department = Department(name="DeptY", description="Desc")
    specialty = Specialty(name="SpecY", description="Desc")

    db.add(department)
    db.add(specialty)
    db.commit()
    db.refresh(department)
    db.refresh(specialty)

    create_response = client.post(
        "/api/staff/",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@test.com",
            "phone_number": "12345678",
            "start_date": "2024-01-01",
            "status": "Active",
            "role_level": "Junior",
            "department_id": department.id,
            "specialty_id": specialty.id
        }
    )

    staff_id = create_response.json()["id"]

    response = client.patch(
        f"/api/staff/{staff_id}",
        json={"department_id": 999}
    )

    assert response.status_code == 422

