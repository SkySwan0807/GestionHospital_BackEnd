from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, String

from app.database import Base


class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(String, nullable=False)
    specialty_id = Column(Integer, nullable=False)
    license_number = Column(String, nullable=False, unique=True)
    issue_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
