"""
main.py
-------
Single Responsibility: Application entry point and composition root.

Routers mounted:
  - specialties → /api/v1/specialties
  - staff       → /api/v1/staff
  - vacation    → /api/v1/human-resources/vacation-management
                  /api/v1/myprofile/requestvacation
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import specialties, staff, vacation


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Hospital Management System",
    version="1.0.0",
    description="API for the Hospital Management System.",
    lifespan=lifespan
)

# ============================================================================
# MOUNT ROUTERS
# ============================================================================
app.include_router(specialties.router, prefix="/api/v1")
app.include_router(staff.router, prefix="/api/v1")
app.include_router(vacation.router, prefix="/api/v1")


# ============================================================================
# HEALTH CHECK
# ============================================================================
@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "message": "Hospital Management API is running",
        "version": "1.0.0"
    }
