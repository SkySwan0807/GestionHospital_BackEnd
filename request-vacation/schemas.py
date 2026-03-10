from pydantic import BaseModel, ConfigDict, Field, EmailStr
from fastapi import UploadFile, File
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date, Time, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# class PostBase(BaseModel):
#   author:str=Field(min_length=1, max_length=20)
#   type:str=Field(min_length=1, max_length=20)
#   description:str=Field(min_length=1, max_length=50)
#   startDate:date
#   endDay:date


class Staff(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str | None = None
    start_date: date
    status: str
    role_level: str
    department_id: int
    specialty_id: int


class StaffCreate(Staff):
    pass


class StaffResponse(Staff):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

class VacationBase(BaseModel):
    # id = Column(Integer, primary_key=True, index=True)
    start_date:date = Field(nullable=False)
    end_date:date = Field(nullable=False)
    description:str | None = Field(default=None, max_length=250)
    status:str = Field(min_length=1,max_length=8, default='pending')



class VacationPostCreate(VacationBase):
  pass


class VacationPostResponse(VacationBase):
  # re fill from attributes (from models) and not only for dictionaries
  model_config = ConfigDict(from_attributes=True)

  id:int
  staff_id:int
  

class VacationUpdate(BaseModel):
   reason:str | None = Field(default=None, max_length=100)
   status:str | None = Field(default='pending', max_length=10)


