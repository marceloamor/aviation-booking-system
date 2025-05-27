from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from src.utils.database import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    profile_picture = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=False)
    
    # Address information
    street = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(50), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    bookings = relationship("Booking", back_populates="passenger")
    created_flights = relationship("Flight", back_populates="created_by_user")
    
    def __repr__(self):
        return f"<User {self.first_name} {self.last_name} ({self.email})>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles) 