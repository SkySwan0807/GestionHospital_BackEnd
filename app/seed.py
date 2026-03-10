from app.database import SessionLocal
from app.models import User, Department, Specialty, Staff, Patient, Vacation, Appointment
from datetime import date, timedelta, time


def seed_data():
    db = SessionLocal()

    try:
        print("🌱 Iniciando la siembra de datos con la nueva tabla Users...")

        # 1. Crear Departamentos
        dept_urgencias = db.query(Department).filter_by(name="Urgencias").first() or Department(name="Urgencias",
                                                                                                description="Atención médica inmediata y crítica")
        dept_cirugia = db.query(Department).filter_by(name="Cirugía").first() or Department(name="Cirugía",
                                                                                            description="Quirófanos y recuperación")
        dept_pediatria = db.query(Department).filter_by(name="Pediatría").first() or Department(name="Pediatría",
                                                                                                description="Atención a infantes y adolescentes")
        dept_rrhh = db.query(Department).filter_by(name="Recursos Humanos").first() or Department(
            name="Recursos Humanos", description="Gestión de talento humano")

        db.add_all([dept_urgencias, dept_cirugia, dept_pediatria, dept_rrhh])
        db.commit()

        # 2. Crear Especialidades
        spec_cardio = db.query(Specialty).filter_by(name="Cardiología").first() or Specialty(name="Cardiología",
                                                                                             description="Especialistas en el corazón")
        spec_neuro = db.query(Specialty).filter_by(name="Neurología").first() or Specialty(name="Neurología",
                                                                                           description="Sistema nervioso y cerebro")
        spec_trauma = db.query(Specialty).filter_by(name="Traumatología").first() or Specialty(name="Traumatología",
                                                                                               description="Huesos y lesiones físicas")

        db.add_all([spec_cardio, spec_neuro, spec_trauma])
        db.commit()

        hoy = date.today()

        # 3. Crear Usuarios y Staff (Adaptado a tus campos phone_number y status)
        # --- Carlos Mendoza (Doctor) ---
        user_carlos = db.query(User).filter_by(email="cmendoza@hospital.com").first()
        if not user_carlos:
            user_carlos = User(email="cmendoza@hospital.com", password="password123", role="doctor")
            db.add(user_carlos)
            db.commit()  # Guardamos para obtener el ID

            staff_1 = Staff(
                user_id=user_carlos.id,
                first_name="Carlos",
                last_name="Mendoza",
                phone_number="77711122",
                role_level="Attending Physician",
                department_id=dept_urgencias.id,
                specialty_id=spec_cardio.id,
                status="Online",
                start_date=hoy,
                profile_pic="https://ui-avatars.com/api/?name=Carlos+Mendoza&background=0D8ABC&color=fff",
                vacation_details={"assigned": 15, "used": 5, "available": 10}
            )
            db.add(staff_1)
            print("  ➕ Creado Usuario y Staff: Carlos Mendoza")

        # --- Laura Vargas (RRHH) ---
        user_laura = db.query(User).filter_by(email="lvargas@hospital.com").first()
        if not user_laura:
            user_laura = User(email="lvargas@hospital.com", password="password123", role="hr")
            db.add(user_laura)
            db.commit()

            staff_rrhh = Staff(
                user_id=user_laura.id,
                first_name="Laura",
                last_name="Vargas",
                phone_number="77799988",
                role_level="HR Specialist",
                department_id=dept_rrhh.id,
                specialty_id=None,
                status="Online",
                start_date=hoy,
                profile_pic="https://ui-avatars.com/api/?name=Laura+Vargas&background=48BB78&color=fff",
                vacation_details={"assigned": 15, "used": 5, "available": 10}
            )
            db.add(staff_rrhh)
            print("  ➕ Creado Usuario y Staff: Laura Vargas (RRHH)")

        db.commit()

        # 4. Crear Usuario y Paciente (Adaptado a tu campo contact_number)
        user_paciente = db.query(User).filter_by(email="juanperez@mail.com").first()
        if not user_paciente:
            user_paciente = User(email="juanperez@mail.com", password="password123", role="patient")
            db.add(user_paciente)
            db.commit()

            paciente_1 = Patient(
                user_id=user_paciente.id,
                first_name="Juan",
                last_name="Pérez",
                date_of_birth=date(1990, 5, 14),
                contact_number="77712345"
            )
            db.add(paciente_1)
            db.commit()
            print("  ➕ Creado Usuario y Paciente: Juan Pérez")

        # 5. Citas y Vacaciones (Usando a Carlos y Juan)
        carlos_staff = db.query(Staff).filter_by(first_name="Carlos").first()
        juan_patient = db.query(Patient).filter_by(first_name="Juan").first()

        if carlos_staff and juan_patient:
            vacation_1 = db.query(Vacation).filter_by(staff_id=carlos_staff.id).first()
            if not vacation_1:
                db.add(Vacation(
                    staff_id=carlos_staff.id,
                    start_date=hoy + timedelta(days=10),
                    end_date=hoy + timedelta(days=15),
                    status="Pending",
                    reason="Vacaciones anuales",
                    comment="Turno cubierto por Dr. Pérez"
                ))

            appointment_1 = db.query(Appointment).filter_by(patient_id=juan_patient.id).first()
            if not appointment_1:
                db.add(Appointment(
                    patient_id=juan_patient.id,
                    doctor_id=carlos_staff.id,
                    date=hoy + timedelta(days=2),
                    time=time(14, 30),
                    reason="Chequeo general",
                    status="Scheduled"
                ))

            db.commit()
            print("  ➕ Creadas vacaciones y citas de prueba")

        print("✅ ¡Datos de prueba insertados con la nueva arquitectura!")

    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()