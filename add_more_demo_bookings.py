#!/usr/bin/env python3
"""
Script to add 3 more demo past flights for Marcelo Amorelli to test the rating system
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

def add_more_past_bookings():
    """Add 3 more past flight bookings for Marcelo Amorelli"""
    session = get_session()
    
    try:
        # Get Marcelo Amorelli user (ID 6)
        marcelo = session.query(User).filter_by(id=6).first()
        if not marcelo:
            print("❌ Marcelo Amorelli user not found!")
            return
        
        print(f"✅ Found user: {marcelo.full_name} ({marcelo.email})")
        
        # Get some existing flight schedules that we can make past flights
        schedules = session.query(FlightSchedule).offset(3).limit(10).all()  # Skip the first 3 we used earlier
        if not schedules:
            print("❌ No additional flight schedules found!")
            return
        
        print(f"✅ Found {len(schedules)} additional flight schedules")
        
        # Create 3 more past bookings with completed flights
        
        # Past flight 4: 10 days ago - Birmingham to Glasgow
        past_date_4 = datetime.now() - timedelta(days=10)
        schedule_4 = schedules[0] if len(schedules) > 0 else schedules[0]
        
        # Update this schedule to be in the past
        schedule_4.scheduled_departure_time = past_date_4
        schedule_4.scheduled_arrival_time = past_date_4 + timedelta(hours=1, minutes=45)
        schedule_4.actual_departure_time = past_date_4 + timedelta(minutes=15)  # 15 min delay
        schedule_4.actual_arrival_time = past_date_4 + timedelta(hours=2)
        schedule_4.status = FlightStatus.LANDED
        schedule_4.departure_airport = "BHX"
        schedule_4.arrival_airport = "GLA"
        
        booking_4 = Booking(
            passenger_id=marcelo.id,
            flight_schedule_id=schedule_4.id,
            booking_date=past_date_4 - timedelta(days=3),  # Booked 3 days before
            confirmation_code=generate_confirmation_code(),
            cost_charged=195.75,
            thank_you_sent=True,
            payment_status=PaymentStatus.COMPLETED
        )
        
        # Past flight 5: 5 days ago - Glasgow to Newcastle
        past_date_5 = datetime.now() - timedelta(days=5)
        schedule_5 = schedules[1] if len(schedules) > 1 else schedules[0]
        
        schedule_5.scheduled_departure_time = past_date_5
        schedule_5.scheduled_arrival_time = past_date_5 + timedelta(hours=1, minutes=20)
        schedule_5.actual_departure_time = past_date_5 - timedelta(minutes=2)  # 2 min early
        schedule_5.actual_arrival_time = past_date_5 + timedelta(hours=1, minutes=15)
        schedule_5.status = FlightStatus.LANDED
        schedule_5.departure_airport = "GLA"
        schedule_5.arrival_airport = "NCL"
        
        booking_5 = Booking(
            passenger_id=marcelo.id,
            flight_schedule_id=schedule_5.id,
            booking_date=past_date_5 - timedelta(days=8),  # Booked 8 days before
            confirmation_code=generate_confirmation_code(),
            cost_charged=155.50,
            thank_you_sent=True,
            payment_status=PaymentStatus.COMPLETED
        )
        
        # Past flight 6: 2 days ago - Newcastle to Bristol
        past_date_6 = datetime.now() - timedelta(days=2)
        schedule_6 = schedules[2] if len(schedules) > 2 else schedules[0]
        
        schedule_6.scheduled_departure_time = past_date_6
        schedule_6.scheduled_arrival_time = past_date_6 + timedelta(hours=1, minutes=35)
        schedule_6.actual_departure_time = past_date_6  # On time
        schedule_6.actual_arrival_time = past_date_6 + timedelta(hours=1, minutes=30)
        schedule_6.status = FlightStatus.LANDED
        schedule_6.departure_airport = "NCL"
        schedule_6.arrival_airport = "BRS"
        
        booking_6 = Booking(
            passenger_id=marcelo.id,
            flight_schedule_id=schedule_6.id,
            booking_date=past_date_6 - timedelta(days=12),  # Booked 12 days before
            confirmation_code=generate_confirmation_code(),
            cost_charged=175.25,
            thank_you_sent=True,
            payment_status=PaymentStatus.COMPLETED
        )
        
        # Add bookings to database
        session.add_all([booking_4, booking_5, booking_6])
        session.commit()
        
        print(f"✅ Successfully added 3 more past bookings for {marcelo.full_name}:")
        print(f"   📍 {booking_4.confirmation_code}: BHX → GLA ({past_date_4.strftime('%Y-%m-%d')}) - £{booking_4.cost_charged}")
        print(f"   📍 {booking_5.confirmation_code}: GLA → NCL ({past_date_5.strftime('%Y-%m-%d')}) - £{booking_5.cost_charged}")
        print(f"   📍 {booking_6.confirmation_code}: NCL → BRS ({past_date_6.strftime('%Y-%m-%d')}) - £{booking_6.cost_charged}")
        print(f"\n🎯 Total Past Flights for Demo:")
        print(f"   Now Marcelo has 6 past flights available for rating!")
        print(f"   Routes: MAN→LHR, LHR→EDI, EDI→BHX, BHX→GLA, GLA→NCL, NCL→BRS")
        
        # Show current total
        total_bookings = session.query(Booking).filter_by(passenger_id=marcelo.id).count()
        print(f"   📊 Total bookings for {marcelo.full_name}: {total_bookings}")
        
    except Exception as e:
        print(f"❌ Error adding bookings: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    add_more_past_bookings() 