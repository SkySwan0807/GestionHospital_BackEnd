from app.database import SessionLocal
from app.models import Department, Specialty, Staff
from datetime import date

def seed_data():
    # Creamos la sesión de la base de datos
    db = SessionLocal()

    try:
        print("🌱 Iniciando la siembra de datos...")

        # 1. Crear Departamentos (3 datos) - Verificar si ya existen
        dept_urgencias = db.query(Department).filter_by(name="Urgencias").first()
        if not dept_urgencias:
            dept_urgencias = Department(name="Urgencias", description="Atención médica inmediata y crítica")
            db.add(dept_urgencias)
            print("  ➕ Creando departamento: Urgencias")
        else:
            print("  ✓ Departamento 'Urgencias' ya existe")

        dept_cirugia = db.query(Department).filter_by(name="Cirugía").first()
        if not dept_cirugia:
            dept_cirugia = Department(name="Cirugía", description="Quirófanos y recuperación")
            db.add(dept_cirugia)
            print("  ➕ Creando departamento: Cirugía")
        else:
            print("  ✓ Departamento 'Cirugía' ya existe")

        dept_pediatria = db.query(Department).filter_by(name="Pediatría").first()
        if not dept_pediatria:
            dept_pediatria = Department(name="Pediatría", description="Atención a infantes y adolescentes")
            db.add(dept_pediatria)
            print("  ➕ Creando departamento: Pediatría")
        else:
            print("  ✓ Departamento 'Pediatría' ya existe")

        dept_rrhh = db.query(Department).filter_by(name="Recursos Humanos").first()
        if not dept_rrhh:
            dept_rrhh = Department(name="Recursos Humanos", description="Gestión de talento humano")
            db.add(dept_rrhh)
            print("  ➕ Creando departamento: Recursos Humanos")
        else:
            print("  ✓ Departamento 'Recursos Humanos' ya existe")

        db.commit()  # Guardamos para que se generen los IDs

        # 2. Crear Especialidades (3 datos) - Verificar si ya existen
        spec_cardio = db.query(Specialty).filter_by(name="Cardiología").first()
        if not spec_cardio:
            spec_cardio = Specialty(name="Cardiología", description="Especialistas en el corazón")
            db.add(spec_cardio)
            print("  ➕ Creando especialidad: Cardiología")
        else:
            print("  ✓ Especialidad 'Cardiología' ya existe")

        spec_neuro = db.query(Specialty).filter_by(name="Neurología").first()
        if not spec_neuro:
            spec_neuro = Specialty(name="Neurología", description="Sistema nervioso y cerebro")
            db.add(spec_neuro)
            print("  ➕ Creando especialidad: Neurología")
        else:
            print("  ✓ Especialidad 'Neurología' ya existe")

        spec_trauma = db.query(Specialty).filter_by(name="Traumatología").first()
        if not spec_trauma:
            spec_trauma = Specialty(name="Traumatología", description="Huesos y lesiones físicas")
            db.add(spec_trauma)
            print("  ➕ Creando especialidad: Traumatología")
        else:
            print("  ✓ Especialidad 'Traumatología' ya existe")

        db.commit()

        # 3. Crear Personal / Staff (4 datos) - Verificar si ya existen por email
        hoy = date.today()

        staff_1 = db.query(Staff).filter_by(email="cmendoza@hospital.com").first()
        if not staff_1:
            staff_1 = Staff(
                first_name="Carlos", last_name="Mendoza", email="cmendoza@hospital.com",
                role_level="Médico Titular", department_id=dept_urgencias.id, specialty_id=spec_cardio.id,
                status="Activo", start_date=hoy
            )
            db.add(staff_1)
            print("  ➕ Creando empleado: Carlos Mendoza")
        else:
            print("  ✓ Empleado 'Carlos Mendoza' ya existe")

        staff_2 = db.query(Staff).filter_by(email="agomez@hospital.com").first()
        if not staff_2:
            staff_2 = Staff(
                first_name="Ana", last_name="Gómez", email="agomez@hospital.com",
                role_level="Enfermera Jefe", department_id=dept_cirugia.id, status="Activo", start_date=hoy
            )
            db.add(staff_2)
            print("  ➕ Creando empleado: Ana Gómez")
        else:
            print("  ✓ Empleado 'Ana Gómez' ya existe")

        staff_3 = db.query(Staff).filter_by(email="lperez@hospital.com").first()
        if not staff_3:
            staff_3 = Staff(
                first_name="Luis", last_name="Pérez", email="lperez@hospital.com",
                role_level="Médico Residente", department_id=dept_pediatria.id, specialty_id=spec_trauma.id,
                status="Activo", start_date=hoy
            )
            db.add(staff_3)
            print("  ➕ Creando empleado: Luis Pérez")
        else:
            print("  ✓ Empleado 'Luis Pérez' ya existe")

        staff_4 = db.query(Staff).filter_by(email="mrodriguez@hospital.com").first()
        if not staff_4:
            staff_4 = Staff(
                first_name="María", last_name="Rodríguez", email="mrodriguez@hospital.com",
                role_level="Recepcionista", department_id=dept_urgencias.id, status="Activo", start_date=hoy
            )
            db.add(staff_4)
            print("  ➕ Creando empleado: María Rodríguez")
        else:
            print("  ✓ Empleado 'María Rodríguez' ya existe")

        staff_rrhh = db.query(Staff).filter_by(email="lvargas@hospital.com").first()
        if not staff_rrhh:
            staff_rrhh = Staff(
                first_name="Laura", last_name="Vargas", email="lvargas@hospital.com",
                role_level="Especialista RRHH", department_id=dept_rrhh.id, specialty_id=None,
                status="Activo", start_date=hoy
            )
            db.add(staff_rrhh)
            print("  ➕ Creando empleado: Laura Vargas (RRHH)")
        else:
            print("  ✓ Empleado 'Laura Vargas (RRHH)' ya existe")

        db.commit()

        print("✅ ¡Datos de prueba verificados/insertados con éxito!")

    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()

