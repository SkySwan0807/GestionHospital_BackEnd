from datetime import date, datetime
from pydantic import ConfigDict, model_validator
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from .staff_contact_model import Staff

class StaffCreate(BaseModel):
    user_id: int          # antes era email
    first_name: str
    last_name: str
    phone_number: str | None = None
    start_date: date
    status: str
    role_level: str
    department_id: int
    specialty_id: Optional[int] = None
    profile_pic: Optional[str] = None
    vacation_details: Optional[dict] = None

class StaffResponse(BaseModel):
    id: int
    user_id: int  # nuevo campo
    first_name: str
    last_name: str
    email: EmailStr  # se mantiene, se obtiene de la propiedad del modelo
    phone_number: Optional[str]
    start_date: date
    status: str
    role_level: str
    department_id: int
    specialty_id: Optional[int]
    profile_pic: Optional[str]
    vacation_details: Optional[dict]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def extract_email(cls, data):
        """Si data es una instancia de Staff, extrae el email de la relación user."""
        if isinstance(data, Staff):
            if data.user:
                # Asignamos el email directamente al campo 'email' en el diccionario de datos
                data.email = data.user.email
            else:
                # Si no hay usuario, lanzamos un error claro (esto no debería ocurrir)
                raise ValueError(f"El staff con ID {data.id} no tiene un usuario asociado")
        return data

class StaffUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=7, max_length=20)
    status: Optional[str] = None
    role_level: Optional[str] = None
    profile_pic: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )