from fastapi import FastAPI, HTTPException, status, Depends
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from database import Base, engine, get_db
from schemas import VacationPostCreate, VacationPostResponse, VacationUpdate

Base.metadata.create_all(bind=engine)


app = FastAPI()



vacationRequests:list[dict] = []

users:list[dict] = []


@app.get('/')
def home():
  return "Welcome to the vacation request site"

# VACATION MANAGMENT

@app.get("/human-resources/vacation-managment", response_model=list[VacationPostResponse])
def get_requests(db:Annotated[Session, Depends(get_db)]):
  result = db.execute(select(models.Vacation))
  extracting_vacation_requests = result.scalars().all()
  if not extracting_vacation_requests:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no existence data")
  return extracting_vacation_requests


@app.get("/human-resources/vacation-managment/{request_id}", response_model=VacationPostResponse)
def get_vacation_request(request_id:int, db:Annotated[Session, Depends(get_db)]):
  result  = db.execute(select(models.Vacation).where(models.Vacation.id == request_id))
  if not result:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="There is no conection with a database or something else went wrong")
  requested_vacation = result.scalars().first()
  if not requested_vacation:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="requested id does not exist")
  return requested_vacation

  
  
@app.patch("/human-resources/vacation-managment/{request_id}", response_model=VacationPostResponse, status_code=status.HTTP_206_PARTIAL_CONTENT)
def update_request_status(request_id:int, updated_data:VacationUpdate, db:Annotated[Session, Depends(get_db)]):
  result = db.execute(select(models.Vacation).where(models.Vacation.id == request_id))
  if not result:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="There is no conection with a database or something else went wrong")
  requested_vacation = result.scalars().first()
  if requested_vacation:
    requested_vacation.status = updated_data.status
    if updated_data.status == "rejected":
      if not updated_data.reason:
        raise HTTPException(status_code=400, detail="reason field is required when status is rejected")
      requested_vacation.reason = updated_data.reason
    db.commit()
    db.refresh(requested_vacation)
    return requested_vacation
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="requested id not found")
  # for p in vacationRequests:
  #   if p.get("id") == request_id:
  #     p["status"] = status
  #     if status == "rejected":
  #       if not reason:
  #         raise HTTPException(status_code=400, detail="reason field is required when status is rejected")
  #       p["reason"] = reason
  #     else:
  #       p["reason"] = None
  #     return p
    
# EMPLOYEE VACATION REQUESTS

@app.post("/myprofile/requestvacation", response_model=VacationPostResponse, status_code=status.HTTP_201_CREATED)
def create_vacation_request(staff_id:int, post:VacationPostCreate, db:Annotated[Session, Depends(get_db)]):
  # new_id = max(p["id"] for p in vacationRequests) + 1 if vacationRequests else 1
  result = db.execute(select(models.Vacation).where(models.Vacation.staff_id == staff_id).where(models.Vacation.status == "pending"))
  vacation_request = result.scalars().first()

  if vacation_request:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A vacation request is still with status pending, wait until there is no request with status pending to make another request")
  
  new_request = models.Vacation(staff_id = staff_id,**post.model_dump())
  db.add(new_request)
  db.commit()
  db.refresh(new_request)
  return new_request


    
# make the get request for employees with request id
@app.get("/myprofile/requestvacation/{request_id}", response_model=VacationPostResponse)
def get_vacation_request_information(request_id:int, db:Annotated[Session, Depends(get_db)]):
  result = db.execute(select(models.Vacation).where(models.Vacation.id == request_id))
  vacation_requested = result.scalars().first()
  if not vacation_requested:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="vacation request not found")
  
  return vacation_requested

@app.delete("/myprofile/requestvacation/{request_id}", response_model=VacationPostResponse)
def delete_vacation_request(request_vacation_id:int, db:Annotated[Session, Depends(get_db)]):
  result = db.execute(select(models.Vacation).where(models.Vacation.id == request_vacation_id))
  vacation_request = result.scalars().first()
  if vacation_request:
    db.delete(vacation_request)
    db.commit()
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requested vacation id not found")

