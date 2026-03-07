from sqlalchemy import Column, Integer, String
from pharmacy.database import Base

class TherapeuticCategory(Base):
    __tablename__ = "therapeutic_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=True)
