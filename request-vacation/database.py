from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./hospital.db"
engine = create_engine(
  SQLALCHEMY_DATABASE_URL,
  connect_args={"check_same_thread":False}
)

SessionLocal = sessionmaker(autoflush=False, bind=engine)

class Base(DeclarativeBase):
  pass

def get_db():
  with SessionLocal() as db:
    yield db