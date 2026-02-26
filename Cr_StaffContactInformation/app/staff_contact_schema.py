from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from pydantic import ConfigDict

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

    model_config = ConfigDict(from_attributes=True)