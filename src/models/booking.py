from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from src.utils.database import Base
import enum
import datetime

class PaymentStatus(enum.Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"
    REFUNDED = "Refunded"

class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    flight_schedule_id = Column(Integer, ForeignKey('flight_schedules.id'), nullable=False)
    booking_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    confirmation_code = Column(String(10), unique=True, nullable=False)
    cost_charged = Column(Float, nullable=False)
    thank_you_sent = Column(Boolean, default=False, nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Relationships
    passenger = relationship("User", back_populates="bookings")
    flight_schedule = relationship("FlightSchedule", back_populates="bookings")
    rating = relationship("Rating", back_populates="booking", uselist=False)
    
    def __repr__(self):
        return f"<Booking {self.confirmation_code} for {self.passenger.full_name} on flight {self.flight_schedule.flight.flight_number}>" 