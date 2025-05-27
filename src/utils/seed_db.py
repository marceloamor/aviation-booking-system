from src.utils.database import init_db, get_session
from src.models.user import User
from src.models.role import Role
from src.models.aircraft import Aircraft
from src.models.flight import Flight, FlightSchedule, FlightStatus
from src.models.booking import Booking, PaymentStatus
from werkzeug.security import generate_password_hash
import datetime
import random
import string

def create_roles():
    """Create default roles"""
    session = get_session()
    
    roles = [
        Role(name="passenger"),
        Role(name="admin"),
        Role(name="technical_staff"),
        Role(name="non_technical_staff")
    ]
    
    session.add_all(roles)
    session.commit()
    
    return roles

def create_admin_user(roles):
    """Create an admin user"""
    session = get_session()
    
    # Find admin role
    admin_role = next(role for role in roles if role.name == "admin")
    tech_role = next(role for role in roles if role.name == "technical_staff")
    
    # Create admin user
    admin = User(
        first_name="Admin",
        last_name="User",
        email="admin@northeastern-airways.com",
        password_hash=generate_password_hash("admin123"),
        phone_number="07700900123",
        street="1 Northeastern Way",
        city="London",
        postal_code="E1 6AN",
        country="United Kingdom",
        roles=[admin_role, tech_role]
    )
    
    session.add(admin)
    session.commit()
    
    return admin

def create_sample_aircraft():
    """Create sample aircraft"""
    session = get_session()
    
    aircraft = [
        Aircraft(
            model_number="B737-800",
            serial_number="34567",
            registration_number="G-NEAB",
            manufacturer="Boeing",
            date_of_manufacture=datetime.date(2015, 5, 12),
            aircraft_class="Narrow-body",
            generic_name="Boeing 737",
            popular_name="Baby Boeing",
            number_of_engines=2,
            aip_info="Max altitude: 41,000ft, Range: 3,850km"
        ),
        Aircraft(
            model_number="A320-200",
            serial_number="98765",
            registration_number="G-NEAC",
            manufacturer="Airbus",
            date_of_manufacture=datetime.date(2017, 8, 23),
            aircraft_class="Narrow-body",
            generic_name="Airbus A320",
            popular_name="Mini-Airbus",
            number_of_engines=2,
            aip_info="Max altitude: 39,000ft, Range: 3,300km"
        ),
        Aircraft(
            model_number="DH8D-402",
            serial_number="12345",
            registration_number="G-NEAD",
            manufacturer="Bombardier",
            date_of_manufacture=datetime.date(2012, 3, 17),
            aircraft_class="Regional",
            generic_name="Dash 8",
            popular_name="Q400",
            number_of_engines=2,
            aip_info="Max altitude: 25,000ft, Range: 2,040km"
        )
    ]
    
    session.add_all(aircraft)
    session.commit()
    
    return aircraft

def create_sample_flights(admin_user, aircraft):
    """Create sample flights"""
    session = get_session()
    
    flights = [
        Flight(
            flight_number="NE101",
            aircraft=aircraft[0],
            created_by_user=admin_user,
            base_cost=89.99
        ),
        Flight(
            flight_number="NE102",
            aircraft=aircraft[1],
            created_by_user=admin_user,
            base_cost=79.99
        ),
        Flight(
            flight_number="NE103",
            aircraft=aircraft[2],
            created_by_user=admin_user,
            base_cost=69.99
        )
    ]
    
    session.add_all(flights)
    session.commit()
    
    return flights

def create_sample_flight_schedules(flights):
    """Create sample flight schedules"""
    session = get_session()
    
    # UK airport codes
    uk_airports = ["LHR", "LGW", "MAN", "EDI", "GLA", "BHX", "BRS", "NCL", "ABZ", "BFS"]
    
    # Create schedules for upcoming days
    now = datetime.datetime.now()
    
    schedules = []
    
    for i in range(10):
        # Random departure and arrival airports
        dep_idx = random.randint(0, len(uk_airports)-1)
        arr_idx = random.randint(0, len(uk_airports)-1)
        while arr_idx == dep_idx:  # Ensure departure != arrival
            arr_idx = random.randint(0, len(uk_airports)-1)
            
        # Random flight from our list
        flight = flights[random.randint(0, len(flights)-1)]
        
        # Create a departure time in the next 30 days
        departure_time = now + datetime.timedelta(days=random.randint(1, 30))
        
        # Flight duration between 45 mins and 2 hours
        flight_duration = datetime.timedelta(minutes=random.randint(45, 120))
        arrival_time = departure_time + flight_duration
        
        schedule = FlightSchedule(
            flight=flight,
            departure_airport=uk_airports[dep_idx],
            arrival_airport=uk_airports[arr_idx],
            departure_terminal=f"T{random.randint(1, 5)}",
            departure_gate=f"G{random.randint(1, 30)}",
            scheduled_departure_time=departure_time,
            scheduled_arrival_time=arrival_time,
            status=FlightStatus.SCHEDULED,
            flight_plan_notes=f"Standard flight plan from {uk_airports[dep_idx]} to {uk_airports[arr_idx]}",
            meals_provided=random.choice([True, False])
        )
        
        schedules.append(schedule)
    
    session.add_all(schedules)
    session.commit()
    
    # Create some return flights
    for i in range(min(5, len(schedules))):
        outbound = schedules[i]
        
        # Return flight is 2-5 days after outbound arrival
        return_departure = outbound.scheduled_arrival_time + datetime.timedelta(days=random.randint(2, 5))
        return_duration = datetime.timedelta(minutes=random.randint(45, 120))
        return_arrival = return_departure + return_duration
        
        return_schedule = FlightSchedule(
            flight=outbound.flight,
            departure_airport=outbound.arrival_airport,
            arrival_airport=outbound.departure_airport,
            departure_terminal=f"T{random.randint(1, 5)}",
            departure_gate=f"G{random.randint(1, 30)}",
            scheduled_departure_time=return_departure,
            scheduled_arrival_time=return_arrival,
            status=FlightStatus.SCHEDULED,
            flight_plan_notes=f"Return flight from {outbound.arrival_airport} to {outbound.departure_airport}",
            meals_provided=outbound.meals_provided
        )
        
        session.add(return_schedule)
        
        # Link the outbound and return flights
        outbound.return_schedule = return_schedule
    
    session.commit()
    
    return schedules

def generate_confirmation_code():
    """Generate a random 8-character alphanumeric confirmation code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(8))

def seed_database():
    """Initialize and seed the database with sample data"""
    # Initialize the database (create tables)
    init_db()
    
    # Create roles
    roles = create_roles()
    
    # Create admin user
    admin = create_admin_user(roles)
    
    # Create sample aircraft
    aircraft = create_sample_aircraft()
    
    # Create sample flights
    flights = create_sample_flights(admin, aircraft)
    
    # Create sample flight schedules
    schedules = create_sample_flight_schedules(flights)
    
    print("Database seeded successfully!")
    
if __name__ == "__main__":
    seed_database() 