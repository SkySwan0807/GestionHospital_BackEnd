"""
main.py
-------
Single Responsibility: Application entry point and composition root.

This file:
  1. Creates the FastAPI application instance
  2. Configures global metadata (title, version, description for Swagger UI)
  3. Creates all database tables on startup via SQLAlchemy
  4. Mounts all routers (specialties, and future ones)
  5. Configures global middleware (CORS)

This is the ONLY file that Uvicorn references externally:
    uvicorn app.main:app --reload

Imported by: Nothing inside the app imports from main.py
Imports from: app.database (Base, engine), app.routers.specialties (router)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.database import Base, engine
from app.routers import specialties

# Load environment variables from .env before anything else
load_dotenv()

# ---------------------------------------------------------------------------
# Database Table Creation
# ---------------------------------------------------------------------------
# This call inspects all classes that inherit from Base (i.e., Specialty in models.py)
# and issues CREATE TABLE IF NOT EXISTS statements for each one.
# This is acceptable for development/SQLite. In production with PostgreSQL,
# you would use Alembic migrations instead.
# Note: models.py must be imported (directly or transitively) before this line
# so that SQLAlchemy knows about the Specialty class. The import of `specialties`
# router triggers the import chain: specialties.py → crud.py → models.py → Base
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# FastAPI Application Instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title=os.getenv("APP_NAME", "Hospital Management API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description=(
        "## Hospital Management System\n\n"
        "**Story 1 — Specialty Catalog Service**\n\n"
        "Provides endpoints to create and retrieve medical specialties "
        "for the hospital's clinical catalog.\n\n"
        "### Available Resources\n"
        "- **Specialties** — Medical specialty catalog (Cardiology, Neurology, etc.)"
    ),
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)

# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------
# CORS (Cross-Origin Resource Sharing) must be configured so that browser-based
# frontends (React, Vue, etc.) can call this API.
# Origins are read from .env (ALLOWED_ORIGINS=http://localhost:3000,...).
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Mount Routers
# ---------------------------------------------------------------------------
# include_router() registers all routes defined in specialties.py.
# prefix="/api/v1" + router's own prefix="/specialties" → /api/v1/specialties
api_prefix = os.getenv("API_V1_PREFIX", "/api/v1")

app.include_router(specialties.router, prefix=api_prefix)


# ---------------------------------------------------------------------------
# Root Health-Check Endpoint
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def root():
    """
    Root health-check endpoint.
    Returns a simple JSON message confirming the API is running.
    Useful for load balancers and container orchestrators (Docker, Kubernetes).
    """
    return {
        "message": "Hospital Management API is running",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "docs": "/docs",
    }
