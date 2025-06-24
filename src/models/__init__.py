# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .role import Role, UserRole
from .aircraft import Aircraft
from .flight import Flight, FlightSchedule
from .booking import Booking
from .rating import Rating

__all__ = [
    'User',
    'Role', 
    'UserRole',
    'Aircraft',
    'Flight',
    'FlightSchedule', 
    'Booking',
    'Rating'
] 