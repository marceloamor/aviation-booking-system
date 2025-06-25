#!/usr/bin/env python3
"""
Script to add demo past flights for Marcelo Amorelli to test the rating system
"""

from src.utils.database import get_session
from src.models.user import User
from src.models.flight import Flight, FlightSchedule, FlightStatus
from src.models.booking import Booking, PaymentStatus
from datetime import datetime, timedelta
import random
import string

def generate_confirmation_code():
    """Generate a random confirmation code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def add_past_bookings():
    """Add past flight bookings for Marcelo Amorelli"""
    session = get_session()
    
    try:
        # Get Marcelo Amorelli user (ID 6)
        marcelo = session.query(User).filter_by(id=6).first()
        if not marcelo:
            print("❌ Marcelo Amorelli user not found!")
            return
        
        print(f"✅ Found user: {marcelo.full_name} ({marcelo.email})")
        
        # Get some existing flight schedules that we can make past flights
        schedules = session.query(FlightSchedule).limit(10).all()
        if not schedules:
            print("❌ No flight schedules found!")
            return
        
        print(f"✅ Found {len(schedules)} flight schedules")
        
        # Create 3 past bookings with completed flights
        past_bookings = []
        
        # Past flight 1: Last month - Manchester to London
        past_date_1 = datetime.now() - timedelta(days=30)
        schedule_1 = schedules[0]  # Use first available schedule
        
        # Update this schedule to be in the past
        schedule_1.scheduled_departure_time = past_date_1
        schedule_1.scheduled_arrival_time = past_date_1 + timedelta(hours=1.5)
        schedule_1.actual_departure_time = past_date_1 + timedelta(minutes=5)  # 5 min delay
        schedule_1.actual_arrival_time = past_date_1 + timedelta(hours=1, minutes=35)
        schedule_1.status = FlightStatus.LANDED
        schedule_1.departure_airport = "MAN"
        schedule_1.arrival_airport = "LHR"
        
        booking_1 = Booking(
            passenger_id=marcelo.id,
            flight_schedule_id=schedule_1.id,
            booking_date=past_date_1 - timedelta(days=7),  # Booked a week before
            confirmation_code=generate_confirmation_code(),
            cost_charged=185.50,
            thank_you_sent=True,
            payment_status=PaymentStatus.COMPLETED
        )
        
        # Past flight 2: 3 weeks ago - London to Edinburgh
        past_date_2 = datetime.now() - timedelta(days=21)
        schedule_2 = schedules[1] if len(schedules) > 1 else schedules[0]
        
        schedule_2.scheduled_departure_time = past_date_2
        schedule_2.scheduled_arrival_time = past_date_2 + timedelta(hours=2)
        schedule_2.actual_departure_time = past_date_2  # On time
        schedule_2.actual_arrival_time = past_date_2 + timedelta(hours=1, minutes=55)
        schedule_2.status = FlightStatus.LANDED
        schedule_2.departure_airport = "LHR"
        schedule_2.arrival_airport = "EDI"
        
        booking_2 = Booking(
            passenger_id=marcelo.id,
            flight_schedule_id=schedule_2.id,
            booking_date=past_date_2 - timedelta(days=14),  # Booked 2 weeks before
            confirmation_code=generate_confirmation_code(),
            cost_charged=210.75,
            thank_you_sent=True,
            payment_status=PaymentStatus.COMPLETED
        )
        
        # Past flight 3: 2 weeks ago - Edinburgh to Birmingham
        past_date_3 = datetime.now() - timedelta(days=14)
        schedule_3 = schedules[2] if len(schedules) > 2 else schedules[0]
        
        schedule_3.scheduled_departure_time = past_date_3
        schedule_3.scheduled_arrival_time = past_date_3 + timedelta(hours=1, minutes=30)
        schedule_3.actual_departure_time = past_date_3 + timedelta(minutes=25)  # 25 min delay
        schedule_3.actual_arrival_time = past_date_3 + timedelta(hours=1, minutes=50)
        schedule_3.status = FlightStatus.LANDED
        schedule_3.departure_airport = "EDI"
        schedule_3.arrival_airport = "BHX"
        
        booking_3 = Booking(
            passenger_id=marcelo.id,
            flight_schedule_id=schedule_3.id,
            booking_date=past_date_3 - timedelta(days=5),  # Booked 5 days before
            confirmation_code=generate_confirmation_code(),
            cost_charged=165.25,
            thank_you_sent=True,
            payment_status=PaymentStatus.COMPLETED
        )
        
        # Add bookings to database
        session.add_all([booking_1, booking_2, booking_3])
        session.commit()
        
        print(f"✅ Successfully added 3 past bookings for {marcelo.full_name}:")
        print(f"   📍 {booking_1.confirmation_code}: MAN → LHR ({past_date_1.strftime('%Y-%m-%d')}) - £{booking_1.cost_charged}")
        print(f"   📍 {booking_2.confirmation_code}: LHR → EDI ({past_date_2.strftime('%Y-%m-%d')}) - £{booking_2.cost_charged}")
        print(f"   📍 {booking_3.confirmation_code}: EDI → BHX ({past_date_3.strftime('%Y-%m-%d')}) - £{booking_3.cost_charged}")
        print(f"\n🎯 Demo Instructions:")
        print(f"   1. Login with: {marcelo.email}")
        print(f"   2. Go to 'My Bookings' page")
        print(f"   3. Click 'Past Flights' tab")
        print(f"   4. Click 'Leave Rating' buttons to demo the rating system")
        
    except Exception as e:
        print(f"❌ Error adding bookings: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    add_past_bookings() 