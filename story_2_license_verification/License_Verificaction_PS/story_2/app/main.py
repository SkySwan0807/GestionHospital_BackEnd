from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import licenses


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown logic could go here


app = FastAPI(
    title="Staff License Verification API",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(licenses.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "license-verification"}
