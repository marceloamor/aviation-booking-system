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

def create_sample_users(roles):
    """Create sample passenger users"""
    session = get_session()
    
    passenger_role = next(role for role in roles if role.name == "passenger")
    
    users = [
        User(
            first_name="John",
            last_name="Smith",
            email="john.smith@email.com",
            password_hash=generate_password_hash("password123"),
            phone_number="07700900456",
            street="123 High Street",
            city="Manchester",
            postal_code="M1 1AA",
            country="United Kingdom",
            roles=[passenger_role]
        ),
        User(
            first_name="Sarah",
            last_name="Johnson",
            email="sarah.johnson@email.com",
            password_hash=generate_password_hash("password123"),
            phone_number="07700900789",
            street="456 Queen's Road",
            city="Edinburgh",
            postal_code="EH1 2BB",
            country="United Kingdom",
            roles=[passenger_role]
        ),
        User(
            first_name="David",
            last_name="Wilson",
            email="david.wilson@email.com",
            password_hash=generate_password_hash("password123"),
            phone_number="07700900321",
            street="789 King Street",
            city="Birmingham",
            postal_code="B1 3CC",
            country="United Kingdom",
            roles=[passenger_role]
        ),
        User(
            first_name="Emma",
            last_name="Brown",
            email="emma.brown@email.com",
            password_hash=generate_password_hash("password123"),
            phone_number="07700900654",
            street="321 Victoria Avenue",
            city="Glasgow",
            postal_code="G1 4DD",
            country="United Kingdom",
            roles=[passenger_role]
        )
    ]
    
    session.add_all(users)
    session.commit()
    
    return users

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
            aip_info="Max altitude: 41,000ft, Range: 3,850km, Capacity: 189 passengers"
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
            aip_info="Max altitude: 39,000ft, Range: 3,300km, Capacity: 180 passengers"
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
            aip_info="Max altitude: 25,000ft, Range: 2,040km, Capacity: 78 passengers"
        ),
        Aircraft(
            model_number="A321-200",
            serial_number="55544",
            registration_number="G-NEAE",
            manufacturer="Airbus",
            date_of_manufacture=datetime.date(2018, 11, 8),
            aircraft_class="Narrow-body",
            generic_name="Airbus A321",
            popular_name="Stretch Airbus",
            number_of_engines=2,
            aip_info="Max altitude: 39,000ft, Range: 3,200km, Capacity: 220 passengers"
        ),
        Aircraft(
            model_number="B787-8",
            serial_number="77889",
            registration_number="G-NEAF",
            manufacturer="Boeing",
            date_of_manufacture=datetime.date(2019, 6, 15),
            aircraft_class="Wide-body",
            generic_name="Boeing 787",
            popular_name="Dreamliner",
            number_of_engines=2,
            aip_info="Max altitude: 43,000ft, Range: 7,350km, Capacity: 242 passengers"
        ),
        Aircraft(
            model_number="ATR72-600",
            serial_number="11223",
            registration_number="G-NEAG",
            manufacturer="ATR",
            date_of_manufacture=datetime.date(2016, 2, 29),
            aircraft_class="Regional",
            generic_name="ATR 72",
            popular_name="Island Hopper",
            number_of_engines=2,
            aip_info="Max altitude: 25,000ft, Range: 1,665km, Capacity: 78 passengers"
        )
    ]
    
    session.add_all(aircraft)
    session.commit()
    
    return aircraft

def create_sample_flights(admin_user, aircraft):
    """Create sample flights with various routes and pricing"""
    session = get_session()
    
    # Flight numbers with different pricing strategies
    flight_configs = [
        # Short-haul domestic routes
        {"number": "NE101", "base_cost": 69.99},
        {"number": "NE102", "base_cost": 79.99},
        {"number": "NE103", "base_cost": 89.99},
        {"number": "NE104", "base_cost": 74.99},
        {"number": "NE105", "base_cost": 84.99},
        {"number": "NE106", "base_cost": 64.99},
        {"number": "NE107", "base_cost": 94.99},
        {"number": "NE108", "base_cost": 59.99},
        {"number": "NE109", "base_cost": 99.99},
        {"number": "NE110", "base_cost": 54.99},
        # Regional routes
        {"number": "NE201", "base_cost": 119.99},
        {"number": "NE202", "base_cost": 129.99},
        {"number": "NE203", "base_cost": 109.99},
        {"number": "NE204", "base_cost": 139.99},
        {"number": "NE205", "base_cost": 149.99},
        # Premium routes
        {"number": "NE301", "base_cost": 199.99},
        {"number": "NE302", "base_cost": 179.99},
        {"number": "NE303", "base_cost": 189.99},
        {"number": "NE304", "base_cost": 209.99},
        {"number": "NE305", "base_cost": 219.99},
    ]
    
    flights = []
    for config in flight_configs:
        # Assign aircraft randomly but with some logic
        if config["base_cost"] < 70:
            # Cheapest flights use regional aircraft
            chosen_aircraft = random.choice([a for a in aircraft if a.aircraft_class == "Regional"])
        elif config["base_cost"] > 150:
            # Premium flights use larger aircraft
            chosen_aircraft = random.choice([a for a in aircraft if a.aircraft_class in ["Wide-body", "Narrow-body"]])
        else:
            # Standard flights use any aircraft
            chosen_aircraft = random.choice(aircraft)
            
        flight = Flight(
            flight_number=config["number"],
            aircraft=chosen_aircraft,
            created_by_user=admin_user,
            base_cost=config["base_cost"]
        )
        flights.append(flight)
    
    session.add_all(flights)
    session.commit()
    
    return flights

def create_sample_flight_schedules(flights):
    """Create many sample flight schedules"""
    session = get_session()
    
    # UK airport codes with popularity weights
    uk_airports = [
        "LHR", "LGW", "MAN", "EDI", "GLA", "BHX", 
        "BRS", "NCL", "ABZ", "BFS", "LTN", "STN",
        "LPL", "BOH", "SOU", "EXT", "NWI", "CWL"
    ]
    
    # Popular routes (from -> to with weights)
    popular_routes = [
        ("LHR", ["MAN", "EDI", "GLA", "BHX", "NCL"]),
        ("LGW", ["EDI", "GLA", "BFS", "ABZ", "BHX"]),
        ("MAN", ["LHR", "LGW", "EDI", "GLA", "BFS"]),
        ("EDI", ["LHR", "LGW", "MAN", "BHX", "BRS"]),
        ("GLA", ["LHR", "LGW", "MAN", "BFS", "BHX"]),
        ("BHX", ["EDI", "GLA", "ABZ", "BFS", "NCL"]),
    ]
    
    now = datetime.datetime.now()
    schedules = []
    
    # Create 100+ flight schedules over the next 60 days
    for day_offset in range(60):  # 60 days
        current_date = now + datetime.timedelta(days=day_offset)
        
        # 3-6 flights per day
        daily_flights = random.randint(3, 6)
        
        for _ in range(daily_flights):
            # Choose route - 70% popular routes, 30% random
            if random.random() < 0.7 and popular_routes:
                # Popular route
                departure_airport, destinations = random.choice(popular_routes)
                arrival_airport = random.choice(destinations)
            else:
                # Random route
                departure_airport = random.choice(uk_airports)
                arrival_airport = random.choice([a for a in uk_airports if a != departure_airport])
            
            # Choose flight
            flight = random.choice(flights)
            
            # Generate departure time (6 AM to 10 PM)
            hour = random.randint(6, 22)
            minute = random.choice([0, 15, 30, 45])
            departure_time = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Flight duration based on route distance (estimate)
            major_airports = ["LHR", "LGW", "MAN", "EDI", "GLA", "BHX"]
            if departure_airport in major_airports and arrival_airport in major_airports:
                duration_minutes = random.randint(60, 120)  # 1-2 hours for major routes
            else:
                duration_minutes = random.randint(45, 90)   # 45-90 minutes for regional
                
            arrival_time = departure_time + datetime.timedelta(minutes=duration_minutes)
            
            # Determine status based on date
            if day_offset < 0:
                status = random.choice([FlightStatus.LANDED, FlightStatus.DELAYED])
            elif day_offset == 0:
                status = random.choice([FlightStatus.SCHEDULED, FlightStatus.DELAYED])
            else:
                status = FlightStatus.SCHEDULED
            
            schedule = FlightSchedule(
                flight=flight,
                departure_airport=departure_airport,
                arrival_airport=arrival_airport,
                departure_terminal=f"T{random.randint(1, 5)}",
                departure_gate=f"G{random.randint(1, 30)}",
                scheduled_departure_time=departure_time,
                scheduled_arrival_time=arrival_time,
                status=status,
                flight_plan_notes=f"Route {departure_airport}-{arrival_airport}",
                meals_provided=random.choice([True, False])
            )
            
            schedules.append(schedule)
    
    session.add_all(schedules)
    session.commit()
    
    # Create some return flights for popular routes
    return_count = min(20, len(schedules) // 4)
    for i in range(return_count):
        outbound = schedules[i * 4]  # Take every 4th flight
        
        # Return flight is 1-7 days after outbound arrival
        return_departure = outbound.scheduled_arrival_time + datetime.timedelta(
            days=random.randint(1, 7),
            hours=random.randint(2, 8)
        )
        
        # Similar duration for return
        duration_delta = outbound.scheduled_arrival_time - outbound.scheduled_departure_time
        return_arrival = return_departure + duration_delta + datetime.timedelta(minutes=random.randint(-15, 15))
        
        return_schedule = FlightSchedule(
            flight=outbound.flight,
            departure_airport=outbound.arrival_airport,
            arrival_airport=outbound.departure_airport,
            departure_terminal=f"T{random.randint(1, 5)}",
            departure_gate=f"G{random.randint(1, 30)}",
            scheduled_departure_time=return_departure,
            scheduled_arrival_time=return_arrival,
            status=FlightStatus.SCHEDULED,
            flight_plan_notes=f"Return route {outbound.arrival_airport}-{outbound.departure_airport}",
            meals_provided=outbound.meals_provided
        )
        
        session.add(return_schedule)
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
    
    # Create sample passenger users
    users = create_sample_users(roles)
    
    # Create sample aircraft
    aircraft = create_sample_aircraft()
    
    # Create sample flights
    flights = create_sample_flights(admin, aircraft)
    
    # Create sample flight schedules
    schedules = create_sample_flight_schedules(flights)
    
    print(f"Database seeded successfully!")
    print(f"Created: {len(roles)} roles, {len(users) + 1} users, {len(aircraft)} aircraft")
    print(f"Created: {len(flights)} flights, {len(schedules)} flight schedules")
    
if __name__ == "__main__":
    seed_database() 