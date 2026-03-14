import logging
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from .staff_contact_model import Staff, User
from .staff_contact_schema import StaffCreate, StaffUpdate

logger = logging.getLogger(__name__)

def create_staff(db: Session, staff_data: StaffCreate) -> Staff:
    """
    Crea un nuevo registro de staff.
    Valida que el user_id exista y que no esté ya asociado a otro staff.
    """
    # 1. Verificar que el usuario existe
    user = db.query(User).filter(User.id == staff_data.user_id).first()
    if not user:
        logger.warning(f"Intento de crear staff con user_id inexistente: {staff_data.user_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario especificado no existe"
        )

    # 2. Verificar que el usuario no tenga ya un perfil de staff
    existing_staff = db.query(Staff).filter(Staff.user_id == staff_data.user_id).first()
    if existing_staff:
        logger.warning(f"El usuario {staff_data.user_id} ya tiene un perfil de staff")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está asociado a un perfil de staff"
        )

    data = staff_data.model_dump()

    if data.get("vacation_details") is None:
        data["vacation_details"] = {
            "assigned": 15,
            "used": 0,
            "available": 15
        }

    new_staff = Staff(**data)
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)

    logger.info(f"Staff creado exitosamente con ID: {new_staff.id}")
    return new_staff


def get_staff(db: Session, staff_id: int) -> Staff:
    """
    Obtiene un registro de staff por su ID.
    Incluye la carga de la relación 'user' para poder acceder al email.
    """
    staff = (
        db.query(Staff)
        .options(joinedload(Staff.user))
        .filter(Staff.id == staff_id)
        .first()
    )

    if not staff:
        logger.warning(f"Staff no encontrado con ID: {staff_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff no encontrado"
        )

    logger.info(f"Staff recuperado exitosamente: {staff_id}")
    return staff


def update_staff(db: Session, staff_id: int, staff_update: StaffUpdate) -> Staff:
    """
    Actualiza parcialmente un registro de staff.
    No permite modificar el user_id ni el email (este último se gestiona a través de User).
    """
    staff = (
        db.query(Staff)
        .options(joinedload(Staff.user))
        .filter(Staff.id == staff_id)
        .first()
    )

    if not staff:
        logger.warning(f"Intento de actualizar staff inexistente ID: {staff_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff no encontrado"
        )

    update_data = staff_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(staff, field, value)

    db.commit()
    db.refresh(staff)

    logger.info(f"Staff actualizado exitosamente: {staff_id}")
    return staff