from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date, Time, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import date


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
    requestDate = Column(Date, nullable=False, default=date.today)
    reason = Column(String(255), nullable=True)
    comment = Column(String(255), nullable=True)


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


