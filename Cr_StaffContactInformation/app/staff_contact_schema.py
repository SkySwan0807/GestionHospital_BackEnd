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

    profile_pic: Optional[str] = None
    vacation_details: Optional[dict] = None


class StaffResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str]
    start_date: date
    status: str
    role_level: str
    department_id: int
    specialty_id: int

    profile_pic: Optional[str]
    vacation_details: Optional[dict]

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StaffUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=7, max_length=20)
    status: Optional[str] = None
    role_level: Optional[str] = None

    profile_pic: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )