import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from Cr_StaffContactInformation.app.main import app
from Cr_StaffContactInformation.app.staff_contact_database import Base, engine
from Cr_StaffContactInformation.app.staff_contact_model import Department, Specialty, User

client = TestClient(app)


def setup_module():
    """Elimina y crea todas las tablas antes de los tests."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module():
    """Limpia la base de datos después de todos los tests."""
    Base.metadata.drop_all(bind=engine)


def test_create_staff():
    """Prueba la creación exitosa de un staff con user_id válido."""
    db = Session(bind=engine)

    # Crear departamento y especialidad
    department = Department(name="Cardiology", description="Heart department")
    specialty = Specialty(name="Cardiologist", description="Heart specialist")
    db.add_all([department, specialty])
    db.commit()
    db.refresh(department)
    db.refresh(specialty)

    # Crear un usuario al que asociaremos el staff
    user = User(email="ana.lopez@test.com", password="hashed_password", role="doctor")
    db.add(user)
    db.commit()
    db.refresh(user)

    # Crear staff usando user_id
    response = client.post(
        "/api/staff/",
        json={
            "user_id": user.id,
            "first_name": "Ana",
            "last_name": "Lopez",
            "phone_number": "12345678",
            "start_date": "2024-01-01",
            "status": "Active",
            "role_level": "Resident",
            "department_id": department.id,
            "specialty_id": specialty.id,
            "profile_pic": "/images/ana.png"
        }
    )

    assert response.status_code == 201
    data = response.json()

    assert data["first_name"] == "Ana"
    assert data["department_id"] == department.id
    assert data["profile_pic"] == "/images/ana.png"
    assert data["vacation_details"]["assigned"] == 15
    assert data["vacation_details"]["used"] == 0
    assert data["vacation_details"]["available"] == 15
    assert data["email"] == "ana.lopez@test.com"  # Verificar que el email se obtiene del usuario

def test_create_staff_user_not_found():
    db = Session(bind=engine)
    department = Department(name="Cardiology_NotFound", description="Heart department")
    specialty = Specialty(name="Cardiologist_NotFound", description="Heart specialist")
    db.add_all([department, specialty])
    db.commit()
    db.refresh(department)
    db.refresh(specialty)

    response = client.post(
        "/api/staff/",
        json={
            "user_id": 9999,
            "first_name": "Ana",
            "last_name": "Lopez",
            "phone_number": "12345678",
            "start_date": "2024-01-01",
            "status": "Active",
            "role_level": "Resident",
            "department_id": department.id,
            "specialty_id": specialty.id,
            "profile_pic": "/images/ana.png"
        }
    )

    assert response.status_code == 400
    assert "El usuario especificado no existe" in response.json()["detail"]


def test_create_staff_user_already_associated():
    db = Session(bind=engine)
    department = Department(name="Cardiology_Already", description="Heart department")
    specialty = Specialty(name="Cardiologist_Already", description="Heart specialist")
    db.add_all([department, specialty])
    db.commit()
    db.refresh(department)
    db.refresh(specialty)

    # Email único
    user = User(email="carlos.already@test.com", password="hashed_password", role="doctor")
    db.add(user)
    db.commit()
    db.refresh(user)

    response1 = client.post(
        "/api/staff/",
        json={
            "user_id": user.id,
            "first_name": "Carlos",
            "last_name": "Perez",
            "phone_number": "87654321",
            "start_date": "2024-01-01",
            "status": "Active",
            "role_level": "Resident",
            "department_id": department.id,
            "specialty_id": specialty.id,
            "profile_pic": "/images/carlos.png"
        }
    )
    assert response1.status_code == 201

    response2 = client.post(
        "/api/staff/",
        json={
            "user_id": user.id,
            "first_name": "Otro",
            "last_name": "Nombre",
            "phone_number": "11111111",
            "start_date": "2024-01-01",
            "status": "Active",
            "role_level": "Resident",
            "department_id": department.id,
            "specialty_id": specialty.id,
            "profile_pic": "/images/otro.png"
        }
    )

    assert response2.status_code == 400
    assert "El usuario ya está asociado a un perfil de staff" in response2.json()["detail"]


def test_get_staff():
    db = Session(bind=engine)
    department = Department(name="Neurology_Get", description="Brain department")
    specialty = Specialty(name="Neurologist_Get", description="Brain specialist")
    db.add_all([department, specialty])
    db.commit()
    db.refresh(department)
    db.refresh(specialty)

    # Email único
    user = User(email="carlos.get@test.com", password="hashed_password", role="doctor")
    db.add(user)
    db.commit()
    db.refresh(user)

    create_response = client.post(
        "/api/staff/",
        json={
            "user_id": user.id,
            "first_name": "Carlos",
            "last_name": "Perez",
            "phone_number": "87654321",
            "start_date": "2024-01-01",
            "status": "Active",
            "role_level": "Specialist",
            "department_id": department.id,
            "specialty_id": specialty.id,
            "profile_pic": "/images/carlos.png"
        }
    )
    assert create_response.status_code == 201
    staff_id = create_response.json()["id"]

    get_response = client.get(f"/api/staff/{staff_id}")
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["id"] == staff_id
    assert data["first_name"] == "Carlos"
    assert data["email"] == "carlos.get@test.com"
    assert data["profile_pic"] == "/images/carlos.png"
    assert data["vacation_details"]["assigned"] == 15
    assert data["vacation_details"]["used"] == 0
    assert data["vacation_details"]["available"] == 15

def test_update_staff_first_name():
    """Prueba actualización de un campo editable (first_name)."""
    db = Session(bind=engine)

    department = Department(name="TestDept", description="Desc")
    specialty = Specialty(name="TestSpec", description="Desc")
    db.add_all([department, specialty])
    db.commit()
    db.refresh(department)
    db.refresh(specialty)

    # Crear usuario
    user = User(email="maria@test.com", password="hashed_password", role="doctor")
    db.add(user)
    db.commit()
    db.refresh(user)

    # Crear staff
    create_response = client.post(
        "/api/staff/",
        json={
            "user_id": user.id,
            "first_name": "Maria",
            "last_name": "Gomez",
            "phone_number": "12345678",
            "start_date": "2024-01-01",
            "status": "Active",
            "role_level": "Resident",
            "department_id": department.id,
            "specialty_id": specialty.id,
            "profile_pic": "/images/maria.png"
        }
    )
    assert create_response.status_code == 201
    staff_id = create_response.json()["id"]

    # Actualizar first_name
    update_response = client.patch(
        f"/api/staff/{staff_id}",
        json={"first_name": "NuevoNombre"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["first_name"] == "NuevoNombre"


def test_update_profile_pic():
    """Prueba actualización de profile_pic."""
    db = Session(bind=engine)

    department = Department(name="DeptPic", description="Desc")
    specialty = Specialty(name="SpecPic", description="Desc")
    db.add_all([department, specialty])
    db.commit()
    db.refresh(department)
    db.refresh(specialty)

    # Crear usuario
    user = User(email="pic@test.com", password="hashed_password", role="doctor")
    db.add(user)
    db.commit()
    db.refresh(user)

    create_response = client.post(
        "/api/staff/",
        json={
            "user_id": user.id,
            "first_name": "Pic",
            "last_name": "User",
            "phone_number": "11111111",
            "start_date": "2024-01-01",
            "status": "Active",
            "role_level": "Specialist",
            "department_id": department.id,
            "specialty_id": specialty.id,
            "profile_pic": "/images/old.png"
        }
    )
    assert create_response.status_code == 201
    staff_id = create_response.json()["id"]

    # Actualizar profile_pic
    response = client.patch(
        f"/api/staff/{staff_id}",
        json={"profile_pic": "/images/new.png"}
    )
    assert response.status_code == 200
    assert response.json()["profile_pic"] == "/images/new.png"


def test_update_staff_not_found():
    """Prueba actualización de un staff que no existe."""
    response = client.patch(
        "/api/staff/9999",
        json={"first_name": "Ghost"}
    )
    assert response.status_code == 404


def test_update_restricted_field_should_be_ignored_or_rejected():
    """
    Prueba que campos no editables (como user_id) no se puedan modificar.
    Dependiendo de tu implementación, puede que el campo no esté en el esquema
    y por lo tanto sea ignorado, o que devuelva 422 si se envía.
    En nuestro caso, StaffUpdate no incluye user_id, por lo que FastAPI
    devolverá 422 (Unprocessable Entity) porque el campo no es esperado.
    """
    db = Session(bind=engine)

    department = Department(name="DeptY", description="Desc")
    specialty = Specialty(name="SpecY", description="Desc")
    db.add_all([department, specialty])
    db.commit()
    db.refresh(department)
    db.refresh(specialty)

    # Crear usuario y staff
    user = User(email="testuser@test.com", password="hashed_password", role="doctor")
    db.add(user)
    db.commit()
    db.refresh(user)

    create_response = client.post(
        "/api/staff/",
        json={
            "user_id": user.id,
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "12345678",
            "start_date": "2024-01-01",
            "status": "Active",
            "role_level": "Resident",
            "department_id": department.id,
            "specialty_id": specialty.id,
            "profile_pic": "/images/test.png"
        }
    )
    assert create_response.status_code == 201
    staff_id = create_response.json()["id"]

    # Intentar actualizar user_id
    response = client.patch(
        f"/api/staff/{staff_id}",
        json={"user_id": 999}  # Campo no permitido en StaffUpdate
    )
    # FastAPI rechazará la petición con 422 porque el campo no está en el esquema
    assert response.status_code == 422


def test_update_specialty_id_not_allowed():
    """
    Prueba que specialty_id no se pueda actualizar (si no está en StaffUpdate).
    Ajusta según si en tu StaffUpdate incluyes o no specialty_id.
    En nuestro esquema original, no está incluido, así que debe dar 422.
    """
    db = Session(bind=engine)

    department = Department(name="DeptZ", description="Desc")
    specialty = Specialty(name="SpecZ", description="Desc")
    db.add_all([department, specialty])
    db.commit()
    db.refresh(department)
    db.refresh(specialty)

    user = User(email="z@test.com", password="hashed_password", role="doctor")
    db.add(user)
    db.commit()
    db.refresh(user)

    create_response = client.post(
        "/api/staff/",
        json={
            "user_id": user.id,
            "first_name": "Z",
            "last_name": "Z",
            "phone_number": "11111111",
            "start_date": "2024-01-01",
            "status": "Active",
            "role_level": "Resident",
            "department_id": department.id,
            "specialty_id": specialty.id,
            "profile_pic": "/images/z.png"
        }
    )
    assert create_response.status_code == 201
    staff_id = create_response.json()["id"]

    response = client.patch(
        f"/api/staff/{staff_id}",
        json={"specialty_id": 999}
    )
    assert response.status_code == 422