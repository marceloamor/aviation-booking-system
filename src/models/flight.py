from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from src.utils.database import Base
import enum

class FlightStatus(enum.Enum):
    SCHEDULED = "Scheduled"
    BOARDING = "Boarding"
    DEPARTED = "Departed"
    IN_AIR = "In Air"
    LANDED = "Landed"
    DELAYED = "Delayed"
    CANCELLED = "Cancelled"

class Flight(Base):
    __tablename__ = 'flights'
    
    id = Column(Integer, primary_key=True)
    flight_number = Column(String(10), unique=True, nullable=False)
    aircraft_id = Column(Integer, ForeignKey('aircraft.id'), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    base_cost = Column(Float, nullable=False)
    
    # Relationships
    aircraft = relationship("Aircraft", back_populates="flights")
    created_by_user = relationship("User", back_populates="created_flights")
    schedules = relationship("FlightSchedule", back_populates="flight")
    
    def __repr__(self):
        return f"<Flight {self.flight_number}>"

class FlightSchedule(Base):
    __tablename__ = 'flight_schedules'
    
    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey('flights.id'), nullable=False)
    
    # Airports and gates
    departure_airport = Column(String(3), nullable=False)  # IATA code
    arrival_airport = Column(String(3), nullable=False)  # IATA code
    departure_terminal = Column(String(10), nullable=True)
    departure_gate = Column(String(10), nullable=True)
    
    # Times
    scheduled_departure_time = Column(DateTime, nullable=False)
    actual_departure_time = Column(DateTime, nullable=True)
    scheduled_arrival_time = Column(DateTime, nullable=False)
    actual_arrival_time = Column(DateTime, nullable=True)
    
    # Status and details
    status = Column(Enum(FlightStatus), default=FlightStatus.SCHEDULED, nullable=False)
    flight_plan_notes = Column(Text, nullable=True)
    meals_provided = Column(Boolean, default=False, nullable=False)
    
    # Self-referencing relationship for return flights
    return_schedule_id = Column(Integer, ForeignKey('flight_schedules.id'), nullable=True)
    return_schedule = relationship("FlightSchedule", remote_side=[id], backref="outbound_schedule", uselist=False)
    
    # Relationships
    flight = relationship("Flight", back_populates="schedules")
    bookings = relationship("Booking", back_populates="flight_schedule")
    
    def __repr__(self):
        return f"<FlightSchedule {self.flight.flight_number} from {self.departure_airport} to {self.arrival_airport} at {self.scheduled_departure_time}>" 