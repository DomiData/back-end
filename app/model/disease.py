from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Disease(Base):
    __tablename__ = "diseases"

    acronym = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)

    occurrences = relationship("Occurrence", back_populates="disease")