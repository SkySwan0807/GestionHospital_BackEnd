"""
main.py
-------
Single Responsibility: Application entry point and composition root.

This file:
  1. Creates the FastAPI application instance
  2. Creates all database tables on startup
  3. Mounts the authentication router under /api/v1
  4. Exposes the /login endpoint

Imported by: Uvicorn (when booting the server)

Imports from:
  - fastapi (FastAPI)
  - app.database (engine, Base)
  - user_auth.router (auth router)

To run the server:
python -m uvicorn user_auth.main:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from user_auth import router as auth_router


# ============================================================================
# 1. APPLICATION LIFESPAN
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on application startup and shutdown.
    Responsible for infrastructure bootstrapping.
    """
    # Create all database tables
    Base.metadata.create_all(bind=engine)
    yield
    # (Optional) Add shutdown cleanup logic here


# ============================================================================
# 2. FASTAPI APPLICATION INSTANCE
# ============================================================================
app = FastAPI(
    title="Hospital Management System - Authentication Service",
    version="1.0.0",
    description="Authentication service responsible for validating user credentials.",
    lifespan=lifespan
)


# ============================================================================
# 3. MOUNT AUTHENTICATION ROUTER
# ============================================================================
# All authentication endpoints will be available under /api/v1
app.include_router(auth_router.router, prefix="/api/v1")