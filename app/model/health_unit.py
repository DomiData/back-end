from sqlalchemy import Column, String, Numeric
from sqlalchemy.orm import relationship
from app.core.base import Base


class HealthUnit(Base):
    __tablename__ = "health_units"

    cnes_code = Column(String(15), primary_key=True)
    name = Column(String(255))
    district = Column(String(100))
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    city_code = Column(String(10))
    unit_type = Column(String(50))

    occurrences = relationship("Occurrence", back_populates="health_unit")
