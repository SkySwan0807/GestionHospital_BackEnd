from datetime import date, datetime
from pydantic import ConfigDict
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class StaffCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str | None = None
    start_date: date
    status: str
    role_level: str
    department_id: int
    specialty_id: int


class StaffResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str | None
    start_date: date
    status: str
    role_level: str
    department_id: int
    specialty_id: int
    created_at: datetime

class StaffUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=7, max_length=20)
    status: Optional[str] = None
    role_level: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")