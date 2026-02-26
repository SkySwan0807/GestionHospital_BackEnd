from fastapi import FastAPI
from .staff_contact_router import router as staff_router
import logging
from .staff_contact_model import Staff
from .staff_contact_database import engine

Staff.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(staff_router)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)