"""
crud.py
-------
Single Responsibility: Contain ALL database operations for the application resources.
(CRUD = Create, Read, Update, Delete)

This is the DATA ACCESS LAYER (Repository Pattern).
It is the ONLY file allowed to speak directly to the database via SQLAlchemy.

Imported by: routers/specialties.py, routers/staff.py
Imports from:
  - sqlalchemy.orm (Session)
  - sqlalchemy (func)
  - app.models (Specialty, Staff, Department)
  - app.schemas (SpecialtyCreate, StaffPositionUpdate)
"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Specialty, Staff, Department
from app.schemas import SpecialtyCreate, StaffPositionUpdate

# =====================================================================
# CRUD PARA ESPECIALIDADES (END-34 - Código de tu compañero)
# =====================================================================

def get_all_specialties(db: Session) -> list[Specialty]:
    """
    Retrieve all specialties from the database.

    Equivalent SQL:
        SELECT * FROM specialties;
    """
    # db.query(Specialty) creates a SELECT statement targeted at the specialties table
    # .all() executes the statement and returns all resulting rows as a Python list
    return db.query(Specialty).all()


def get_specialty_by_name(db: Session, name: str) -> Specialty | None:
    """
    Query the database for a specialty by its name.
    Performs a case-insensitive search (e.g., 'cardio' matches 'Cardio').

    Equivalent SQL:
        SELECT * FROM specialties WHERE LOWER(name) = LOWER('cardio') LIMIT 1;
    """
    # func.lower() translates into the SQL LOWER() function.
    # We apply it to both the database column and the incoming string
    # to guarantee a case-insensitive match regardless of how it was typed.
    return db.query(Specialty).filter(
        func.lower(Specialty.name) == func.lower(name)
    ).first()


def get_specialty(db: Session, specialty_id: int) -> Specialty | None:
    """
    Retrieve a single specialty by its ID.
    """
    return db.query(Specialty).filter(Specialty.id == specialty_id).first()


def create_specialty(db: Session, specialty: SpecialtyCreate) -> Specialty:
    """
    Insert a new specialty record into the database.
    """
    # Step 1: Create a SQLAlchemy ORM object from the Pydantic schema data
    db_specialty = Specialty(
        name=specialty.name,
        description=specialty.description
    )

    # Step 2: Add it to the session (marks it as "to be inserted")
    db.add(db_specialty)

    # Step 3: Commit the transaction (writes it to the physical database file)
    db.commit()

    # Step 4: Refresh the instance (re-reads the row from DB to populate 'id' and 'created_at')
    db.refresh(db_specialty)

    # Step 5: Return the populated object
    return db_specialty


# =====================================================================
# CRUD PARA RECURSOS HUMANOS / STAFF (END-27 - Tu código)
# =====================================================================

def assign_staff_position(db: Session, staff_id: int, position_data: StaffPositionUpdate):
    """
    Asigna o actualiza el cargo, departamento y especialidad de un empleado.
    """
    # 1. Validación A: Buscar al empleado por su ID
    db_staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not db_staff:
        return None  # Retornamos None para que el Router lance un Error HTTP 404

    # 2. Validación B: Verificar que el departamento realmente exista
    db_department = db.query(Department).filter(Department.id == position_data.department_id).first()
    if not db_department:
        raise ValueError(f"Error: El departamento con ID {position_data.department_id} no existe en el hospital.")

    # 3. Validación C: Verificar que la especialidad exista (SOLO si nos enviaron una)
    if position_data.specialty_id is not None:
        db_specialty = db.query(Specialty).filter(Specialty.id == position_data.specialty_id).first()
        if not db_specialty:
            raise ValueError(f"Error: La especialidad con ID {position_data.specialty_id} no existe.")

    # 4. Todo está correcto -> Actualizamos los datos del empleado
    db_staff.role_level = position_data.role_level
    db_staff.department_id = position_data.department_id
    db_staff.specialty_id = position_data.specialty_id

    # 5. Guardar los cambios físicos en la base de datos
    db.commit()

    # 6. Refrescar el objeto para obtener los datos actualizados
    db.refresh(db_staff)

    return db_staff