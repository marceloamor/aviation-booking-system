from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment or use default SQLite path
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///northeastern_airways.db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory bound to the engine
session_factory = sessionmaker(bind=engine)

# Create thread-safe scoped session
Session = scoped_session(session_factory)

# Base class for all models
Base = declarative_base()

def init_db():
    """Initialize the database by creating all tables."""
    # Import all models to ensure they're registered with Base
    from src.models.user import User
    from src.models.role import Role, UserRole
    from src.models.aircraft import Aircraft
    from src.models.flight import Flight, FlightSchedule
    from src.models.booking import Booking
    from src.models.rating import Rating
    
    # Create all tables
    Base.metadata.create_all(engine)

def get_session():
    """Get a new session for database operations."""
    return Session() 