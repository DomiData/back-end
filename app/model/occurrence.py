from sqlalchemy import Column, String, Integer, Date, ForeignKey, Numeric, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Occurrence(Base):
    __tablename__ = "occurrences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    disease_type = Column(String(10), ForeignKey("diseases.acronym"), nullable=False)
    health_unit_id = Column(String(15), ForeignKey("health_units.cnes_code"), nullable=False)
    notification_date = Column(Date, nullable=False)
    city_id = Column(String(10))
    patient_age = Column(Integer)
    patient_sex = Column(String(1))
    evolution = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    disease = relationship("Disease", back_populates="occurrences")
    health_unit = relationship("HealthUnit", back_populates="occurrences")