from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db

# Importamos tus Schemas y tu CRUD
from app.schemas import StaffPositionUpdate, StaffResponse
from app import crud
from app.models import Staff

# Creamos el router para agrupar todas las URLs de Recursos Humanos
router = APIRouter(
    prefix="/staff",
    tags=["Staff Management"]
)

# ============================================================================
# 1. NUEVO ENDPOINT: OBTENER TODO EL PERSONAL
# ============================================================================
@router.get("", response_model=List[StaffResponse])
def get_all_staff(db: Session = Depends(get_db)):
    """
    Obtiene la lista de todo el personal del hospital, incluyendo
    sus fotos de perfil (profile_pic) y detalles de vacaciones (vacation_details).
    """
    # Consulta directa a la base de datos para obtener a todos
    staff_members = db.query(Staff).all()
    return staff_members

# ============================================================================
# 2. ENDPOINT END-27: ASIGNAR CARGO
# ============================================================================
@router.patch("/{staff_id}/position", response_model=StaffResponse)
def assign_position(
        staff_id: int,
        position_data: StaffPositionUpdate,
        db: Session = Depends(get_db)
):
    """
    END-27: Asigna o actualiza el cargo, departamento y especialidad de un empleado.
    """
    try:
        # Llamamos a tu función CRUD
        updated_staff = crud.assign_staff_position(db=db, staff_id=staff_id, position_data=position_data)

        # Si el CRUD devuelve None, es porque el empleado no existe
        if updated_staff is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error: El empleado con ID {staff_id} no existe en el sistema."
            )

        return updated_staff

    except ValueError as e:
        # Atrapamos los errores que programaste en tu CRUD (ej. Departamento no existe)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )