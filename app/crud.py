"""
crud.py
-------
Single Responsibility: Contain ALL database operations for the Specialty resource.
(CRUD = Create, Read, Update, Delete)

This is the DATA ACCESS LAYER (Repository Pattern).
It is the ONLY file allowed to speak directly to the database via SQLAlchemy.

Imported by: routers/specialties.py
Imports from:
  - sqlalchemy.orm (Session)
  - sqlalchemy (func)
  - app.models (Specialty)
  - app.schemas (SpecialtyCreate)
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from app.models import Staff, Department, Specialty, User
from app.schemas import SpecialtyCreate, StaffSelfUpdate
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status

def get_staff_by_id(db: Session, staff_id: str | int) -> Staff | None:
    return (
        db.query(Staff)
        .options(
            joinedload(Staff.user),
            joinedload(Staff.department),
            joinedload(Staff.specialty)
        )
        .filter(Staff.id == staff_id)
        .first()
    )

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

def search_staff(
    db: Session,
    name: str | None = None,
    department: str | None = None,
    specialty: str | None = None,
    role: str | None = None,
    status: str | None = None,
    email: str | None = None
) -> list[Staff]:
    """
    Search staff records with optional filters.
    - name: matches first_name or last_name (case-insensitive)
    - department: matches department name
    - role: matches role_level
    - location: matches location (if Staff has this field) [ahora en lugar de dejar location, usamos filtros que sí existen en el dominio. También conviene cargar relaciones con joinedload]
    """

    # Start query joining Department and Specialty for filtering
    query = (
        db.query(Staff)
        .options(
            joinedload(Staff.user),
            joinedload(Staff.department),
            joinedload(Staff.specialty)
        )
        .join(Department, Staff.department_id == Department.id, isouter=True)
        .join(Specialty, Staff.specialty_id == Specialty.id, isouter=True)
        .join(User, Staff.user_id == User.id, isouter=True)
    )

    # Filter by name (first or last)
    if name:
        query = query.filter(
            or_(
                Staff.first_name.ilike(f"%{name}%"),
                Staff.last_name.ilike(f"%{name}%")
            )
        )

    # Filter by department name
    if department:
        query = query.filter(Department.name.ilike(f"%{department}%"))
    
    #Filter by specialty name
    if specialty:
        query = query.filter(Specialty.name.ilike(f"%{specialty}%"))

    # Filter by role level
    if role:
        query = query.filter(Staff.role_level.ilike(f"%{role}%"))

    # Filter by status
    if status:
        query = query.filter(Staff.status.ilike(f"%{status}%"))
        
    # Filter by email:
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    
    # Return all matching results
    return query.all()

def update_staff_contact_info(db: Session, update_data: StaffSelfUpdate):
    # 1. Buscar al empleado por el ID que viene en el JSON
    db_staff = db.query(Staff).filter(Staff.id == update_data.staff_id).first()
    
    if not db_staff:
        return None

    # 2. Convertir el esquema a dict, pero quitamos 'staff_id' porque ese no se actualiza
    payload = update_data.model_dump(exclude_unset=True)
    payload.pop("staff_id", None) 
    
    staff_fields = {
        "first_name",
        "last_name",
        "phone_number",
        "profile_pic",
        "status",
        "role_level"
    }

    # 3. Actualizar solo los campos enviados (email, phone, etc.)
    # email se persiste en users
    # el resto se persiste en staff
    # para evitar meter campos incorrectos en la entidad equivocada.
    for key, value in payload.items():
        if key == "email":
            if not db_staff.user:
                return None
            db_staff.user.email = value
        elif key in staff_fields:
            setattr(db_staff, key, value)

    db.commit()
    db.refresh(db_staff)
    return db_staff


def create_staff(db: Session, staff_data: "schemas.StaffCreate") -> Staff:
    # 1. Validar que el usuario exista
    user = db.query(User).filter(User.id == staff_data.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="El usuario especificado no existe en la BD")

    # 2. Validar que no tenga perfil duplicado
    existing = db.query(Staff).filter(Staff.user_id == staff_data.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Este usuario ya tiene un perfil de staff")

    # 3. Crear el registro
    db_staff = Staff(**staff_data.model_dump())
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)

    # Cargar relaciones para que _to_staff_contact_out no falle
    return db.query(Staff).options(
        joinedload(Staff.user), joinedload(Staff.department), joinedload(Staff.specialty)
    ).filter(Staff.id == db_staff.id).first()


def update_staff_admin(db: Session, staff_id: int, staff_update: "schemas.StaffUpdate") -> Staff:
    staff = db.query(Staff).options(
        joinedload(Staff.user), joinedload(Staff.department), joinedload(Staff.specialty)
    ).filter(Staff.id == staff_id).first()

    if not staff:
        raise HTTPException(status_code=404, detail="Staff no encontrado")

    update_data = staff_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(staff, key, value)

    db.commit()
    db.refresh(staff)
    return staff