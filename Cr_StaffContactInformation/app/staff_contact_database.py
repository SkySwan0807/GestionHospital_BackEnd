from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Obtiene la ruta absoluta del directorio raíz del proyecto (GestionHospital_BackEnd)
# El archivo actual está en: GestionHospital_BackEnd/app/Cr_StaffContactInformation/app/staff_contact_database.py
# Subimos 3 niveles para llegar a la raíz
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # → GestionHospital_BackEnd/

# Ruta completa al archivo de la base de datos
DB_PATH = BASE_DIR / "hospital.db"

# URL de conexión con ruta absoluta
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()