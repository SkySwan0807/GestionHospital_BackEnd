from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date, Time, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .staff_contact_database import Base


# =========================================================================
# MÓDULO 1: RECURSOS HUMANOS
# =========================================================================

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    staff_members = relationship("Staff", back_populates="department")


class Specialty(Base):
    __tablename__ = "specialties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    staff_members = relationship("Staff", back_populates="specialty")


class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone_number = Column(String(50))
    start_date = Column(Date, nullable=False)
    status = Column(String(50), default='Online')
    role_level = Column(String(50))

    department_id = Column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"))
    specialty_id = Column(Integer, ForeignKey("specialties.id", ondelete="RESTRICT"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    department = relationship("Department", back_populates="staff_members")
    specialty = relationship("Specialty", back_populates="staff_members")
    user_account = relationship("User", back_populates="staff_profile", uselist=False)


class Salary(Base):
    __tablename__ = "salaries"
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"))
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default='USD')
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class Vacation(Base):
    __tablename__ = "vacations"
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(50), default='Pending')
    reason = Column(String(255))


class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"))
    day_of_week = Column(String(15), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)


# =========================================================================
# MÓDULO 2: USUARIOS Y AUTENTICACIÓN
# =========================================================================

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="SET NULL"), nullable=True)
    role = Column(String(50), nullable=False, default='User')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    staff_profile = relationship("Staff", back_populates="user_account")


# =========================================================================
# MÓDULO 3: GESTIÓN DE PACIENTES Y ÁREA MÉDICA
# =========================================================================

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date)
    contact_number = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MedicalHistory(Base):
    __tablename__ = "medical_histories"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    details = Column(JSON, nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    doctor_id = Column(Integer, ForeignKey("staff.id", ondelete="RESTRICT"))
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    reason = Column(String(255))
    status = Column(String(50), default='Scheduled')


# =========================================================================
# MÓDULO 4: RESERVA DE ESPACIOS
# =========================================================================

class HospitalSpace(Base):
    __tablename__ = "hospital_spaces"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(String(50), default='Available')


class SpaceReservation(Base):
    __tablename__ = "space_reservations"
    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("hospital_spaces.id", ondelete="CASCADE"))
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="SET NULL"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("staff.id", ondelete="SET NULL"), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)


# =========================================================================
# MÓDULO 5: LABORATORIO Y MORGUE
# =========================================================================

class LaboratoryTest(Base):
    __tablename__ = "laboratory_tests"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    doctor_id = Column(Integer, ForeignKey("staff.id", ondelete="SET NULL"), nullable=True)
    test_type = Column(String(100), nullable=False)
    results = Column(JSON)
    status = Column(String(50), default='Pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MorgueRecord(Base):
    __tablename__ = "morgue_records"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"))
    date_of_death = Column(DateTime(timezone=True), nullable=False)
    cause_of_death = Column(String(255))
    notes = Column(Text)


# =========================================================================
# MÓDULO 6: ADMINISTRACIÓN Y FINANZAS
# =========================================================================

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), nullable=False)
    quantity = Column(Integer, default=0)
    unit = Column(String(20))
    last_restock_date = Column(DateTime(timezone=True))


class ProcurementOrder(Base):
    __tablename__ = "procurement_orders"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory.id", ondelete="CASCADE"))
    quantity_ordered = Column(Integer, nullable=False)
    status = Column(String(50), default='Pending')
    order_date = Column(DateTime(timezone=True), server_default=func.now())


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"))
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default='Unpaid')
    issued_at = Column(DateTime(timezone=True), server_default=func.now())


class Tax(Base):
    __tablename__ = "taxes"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"))
    tax_name = Column(String(50), nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=False)