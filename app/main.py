"""
main.py
-------
Single Responsibility: Application entry point and composition root.

This file:
  1. Creates the FastAPI application instance
  2. Creates all database tables on startup
  3. Mounts the specialties router under /api/v1
  4. Provides a root health-check endpoint

Imported by: Uvicorn (when booting the server)
Imports from:
  - fastapi (FastAPI)
  - app.database (engine, Base)
  - app.routers (specialties)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import specialties

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts
    Base.metadata.create_all(bind=engine)
    yield
    # This runs when the server stops


# DATABASE INITIALIZATION is now handled by the lifespan context below.


# ============================================================================
# 2. FASTAPI APP INSTANCE
# ============================================================================
# This `app` object is the core of your service. Uvicorn attaches to it.
# All routers, middleware, and dependency overrides ultimately connect back to it.
app = FastAPI(
    title="Hospital Specialty Catalog",
    version="1.0.0",
    description="API for managing medical specialties in the Hospital Management System.",
    lifespan=lifespan
)

# ============================================================================
# 3. MOUNT ROUTERS
# ============================================================================
# include_router() attaches all the endpoints defined in specialties.py to `app`.
# prefix="/api/v1" means that if the router defines `/`, the final URL
# becomes `/api/v1/specialties`. This versioning allows us to safely release
# a `/api/v2/specialties` later without breaking older Front-End clients.
app.include_router(specialties.router, prefix="/api/v1")

# ============================================================================
# 4. HEALTH CHECK ENDPOINT
# ============================================================================
@app.get("/", tags=["Health"])
def health_check():
    """
    Root health check endpoint.
    Used by load balancers, Docker, or Kubernetes to verify the API is alive.
    """
    return {
        "status": "ok",
        "message": "Hospital Management API is running",
        "service": "Specialty Catalog"
    }
