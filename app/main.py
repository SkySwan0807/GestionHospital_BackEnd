"""
main.py
-------
Single Responsibility: Application entry point and composition root.

Routers mounted:
  - specialties → /api/v1/specialties
  - staff       → /api/v1/staff
  - vacation    → /api/v1/human-resources/vacation-management
                  /api/v1/myprofile/requestvacation
  - auth        → /api/v1/login
                  /api/v1/forgot_password
                  /api/v1/new_user
                  /api/v1/verify
                  /api/v1/reset_password
                  /api/v1/register
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import specialties, staff, vacation, auth


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
app.include_router(auth.router, prefix="/api/v1")


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
