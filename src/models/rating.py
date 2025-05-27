from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, Text
from sqlalchemy.orm import relationship
from src.utils.database import Base
import datetime

class Rating(Base):
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.id'), unique=True, nullable=False)
    stars = Column(Integer, nullable=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Ensure stars are between 1 and 5
    __table_args__ = (
        CheckConstraint('stars >= 1 AND stars <= 5', name='check_stars_range'),
    )
    
    # Relationships
    booking = relationship("Booking", back_populates="rating")
    
    def __repr__(self):
        return f"<Rating {self.stars}★ for booking {self.booking.confirmation_code}>" 