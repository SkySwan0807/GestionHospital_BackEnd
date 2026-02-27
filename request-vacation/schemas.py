from pydantic import BaseModel, ConfigDict, Field
from fastapi import UploadFile, File
from datetime import date

class PostBase(BaseModel):
  author:str=Field(min_length=1, max_length=20)
  type:str=Field(min_length=1, max_length=20)
  description:str=Field(min_length=1, max_length=50)
  startDate:date
  endDay:date


class PostCreate(PostBase):
  pass

class PostResponse(PostBase):
  # re fill from attributes and not only for dictionaries
  model_config = ConfigDict(from_attributes=True)

  id:int
  status:str
  # createdAt:date
