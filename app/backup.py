import shutil, os
from datetime import datetime
import json
from app.database import SessionLocal
from app import models, schemas

BACKUP_DIR = "respaldos"
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_sqlite_file():
    fecha = datetime.now().strftime("%Y-%m-%d")
    origen = "hospital.db"
    destino = os.path.join(BACKUP_DIR, f"hospital_{fecha}.db")
    shutil.copy2(origen, destino)
    print(f"Respaldo completo creado: {destino}")



def export_table_with_schema(session, model, schema, filename):
    rows = session.query(model).all()
    if not rows:
        return
    data = [schema.model_validate(row).model_dump() for row in rows]
    with open(os.path.join(BACKUP_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, default=str)
    print(f"Tabla {model.__tablename__} exportada a {filename}")

def main():
    backup_sqlite_file()
    db = SessionLocal()
    try:
        export_table_with_schema(db, models.Specialty, schemas.SpecialtyOut, "specialties.json")
        export_table_with_schema(db, models.Staff, schemas.StaffOut, "staff.json")
        # Aquí puedes añadir más tablas y schemas según lo que definas en schemas.py
    finally:
        db.close()

if __name__ == "__main__":
    main()