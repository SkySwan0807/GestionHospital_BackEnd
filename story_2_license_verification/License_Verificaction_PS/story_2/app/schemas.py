from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class LicenseStatus(str, Enum):
    active = "Active"
    expired = "Expired"
    suspended = "Suspended"


class LicenseBase(BaseModel):
    staff_id: str
    specialty_id: int
    license_number: str
    issue_date: date
    expiration_date: date
    status: LicenseStatus

    @field_validator("license_number", mode="before")
    @classmethod
    def validate_license_number_not_empty(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("License number cannot be empty")
        return v


class LicenseCreate(LicenseBase):
    pass


class LicenseUpdate(BaseModel):
    staff_id: Optional[str] = None
    specialty_id: Optional[int] = None
    license_number: Optional[str] = None
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    status: Optional[LicenseStatus] = None


class LicenseOut(LicenseBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
