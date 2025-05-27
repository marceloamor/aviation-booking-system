from sqlalchemy import Column, Integer, String, Date, Text, JSON
from sqlalchemy.orm import relationship
from src.utils.database import Base

class Aircraft(Base):
    __tablename__ = 'aircraft'
    
    id = Column(Integer, primary_key=True)
    model_number = Column(String(50), nullable=False)
    serial_number = Column(String(50), unique=True, nullable=False)
    registration_number = Column(String(20), unique=True, nullable=False)
    manufacturer = Column(String(100), nullable=False)
    date_of_manufacture = Column(Date, nullable=False)
    aircraft_class = Column(String(50), nullable=False)
    generic_name = Column(String(100), nullable=False)
    popular_name = Column(String(100), nullable=True)
    number_of_engines = Column(Integer, nullable=False)
    aip_info = Column(Text, nullable=True)  # AIP = Aeronautical Information Publication
    
    # Relationships
    flights = relationship("Flight", back_populates="aircraft")
    
    def __repr__(self):
        return f"<Aircraft {self.registration_number} ({self.model_number})>" 