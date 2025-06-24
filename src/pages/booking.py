import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from src.utils.database import get_session
from src.models.flight import FlightSchedule
from src.models.booking import Booking, PaymentStatus
from src.utils.seed_db import generate_confirmation_code
from urllib.parse import parse_qs
from flask import request
import flask
from datetime import datetime
import random

dash.register_page(__name__, path_template="/bookings/new")

def layout(flight_id=None, passengers=None, **kwargs):
    """Dynamic layout that handles URL parameters"""
    
    # Check if user is logged in
    user_id = flask.session.get("user_id")
    if not user_id:
        return html.Div([
            dbc.Alert(
                [
                    "You need to be logged in to book a flight. ",
                    dbc.Button("Log in", color="primary", href="/login", className="ms-2")
                ],
                color="warning",
                className="mb-4"
            ),
            dcc.Location(pathname="/login", id="redirect-to-login")
        ])
    
    # Get booking data from session if not provided as parameters
    if not flight_id:
        flight_id = flask.session.get("booking_flight_id")
    if not passengers:
        passengers = flask.session.get("booking_passengers", 1)
    
    # Default layout for booking form
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H2("Complete Your Booking", className="mb-4"),
                
                # Hidden inputs to store flight_id and passengers
                dcc.Store(id="booking-flight-id", data=flight_id),
                dcc.Store(id="booking-passengers", data=passengers),
                
                # Flight details will be loaded here
                html.Div(id="booking-flight-details"),
                
                # Simplified booking form
                dbc.Card([
                    dbc.CardHeader(html.H4("Confirm Your Booking")),
                    dbc.CardBody([
                        dbc.Alert([
                            html.H5("Payment Information"),
                            html.P("This is a demonstration system. No real payment will be processed.", className="mb-0")
                        ], color="info", className="mb-4"),
                        
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Passenger Name"),
                                    dbc.Input(
                                        type="text",
                                        id="booking-passenger-name",
                                        placeholder="Enter passenger name",
                                        required=True
                                    )
                                ])
                            ], className="mb-3"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Contact Phone"),
                                    dbc.Input(
                                        type="tel",
                                        id="booking-contact-phone",
                                        placeholder="Enter contact phone number",
                                        required=True
                                    )
                                ])
                            ], className="mb-3"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Checkbox(
                                        id="booking-terms",
                                        label="I agree to the Terms and Conditions and Privacy Policy",
                                        value=False
                                    )
                                ])
                            ], className="mb-3"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        "Confirm Booking",
                                        id="complete-booking-btn",
                                        color="success",
                                        className="w-100",
                                        disabled=True,
                                        size="lg"
                                    ),
                                    html.Div(id="booking-result", className="mt-3")
                                ])
                            ])
                        ])
                    ])
                ])
            ], width=8, className="mx-auto")
        ])
    ])

@callback(
    Output("booking-flight-details", "children"),
    [Input("booking-flight-id", "data"),
     Input("booking-passengers", "data")]
)
def load_flight_details(flight_id, passengers):
    if not flight_id:
        return dbc.Alert("No flight selected. Please search for and select a flight first.", color="warning")
    
    try:
        session = get_session()
        flight_schedule = session.query(FlightSchedule).filter_by(id=flight_id).first()
        
        if not flight_schedule:
            return dbc.Alert("Flight not found. Please try again.", color="danger")
        
        # Format date and times
        flight_date = flight_schedule.scheduled_departure_time.strftime("%A, %d %B %Y")
        departure_time = flight_schedule.scheduled_departure_time.strftime("%H:%M")
        arrival_time = flight_schedule.scheduled_arrival_time.strftime("%H:%M")
        
        # Calculate duration
        duration_mins = (flight_schedule.scheduled_arrival_time - flight_schedule.scheduled_departure_time).total_seconds() / 60
        duration = f"{int(duration_mins // 60)}h {int(duration_mins % 60)}m"
        
        # Calculate cost
        passengers = int(passengers) if passengers else 1
        total_cost = flight_schedule.flight.base_cost * passengers
        
        # Create flight details card
        return dbc.Card([
            dbc.CardHeader(html.H4("Flight Details")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5(f"Flight {flight_schedule.flight.flight_number}"),
                        html.P(f"{flight_date}", className="text-muted")
                    ], width=6),
                    dbc.Col([
                        html.H5(f"£{total_cost:.2f}", className="text-end"),
                        html.P(f"for {passengers} passenger{'s' if passengers > 1 else ''}", className="text-muted text-end")
                    ], width=6)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H5(flight_schedule.departure_airport),
                            html.P(f"Departure: {departure_time}", className="text-muted")
                        ], className="text-center")
                    ], width=5),
                    dbc.Col([
                        html.Div([
                            html.H5(duration),
                            html.Hr(className="my-1"),
                            html.P("Direct Flight", className="small text-muted")
                        ], className="text-center")
                    ], width=2),
                    dbc.Col([
                        html.Div([
                            html.H5(flight_schedule.arrival_airport),
                            html.P(f"Arrival: {arrival_time}", className="text-muted")
                        ], className="text-center")
                    ], width=5)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        html.P([
                            html.Strong("Aircraft: "),
                            f"{flight_schedule.flight.aircraft.manufacturer} {flight_schedule.flight.aircraft.model_number}"
                        ]),
                        html.P([
                            html.Strong("Terminal: "),
                            flight_schedule.departure_terminal or "TBA"
                        ]),
                        html.P([
                            html.Strong("Gate: "),
                            flight_schedule.departure_gate or "TBA"
                        ])
                    ], width=6),
                    dbc.Col([
                        html.P([
                            html.Strong("Status: "),
                            html.Span(flight_schedule.status.value, 
                                      className=f"badge bg-{'success' if flight_schedule.status.value == 'Scheduled' else 'warning'}")
                        ]),
                        html.P([
                            html.Strong("Meal Service: "),
                            "Yes" if flight_schedule.meals_provided else "No"
                        ])
                    ], width=6)
                ])
            ])
        ], className="mb-4")
        
    except Exception as e:
        return dbc.Alert(f"Error loading flight details: {str(e)}", color="danger")

@callback(
    Output("complete-booking-btn", "disabled"),
    [Input("booking-passenger-name", "value"),
     Input("booking-contact-phone", "value"),
     Input("booking-terms", "value")]
)
def enable_complete_booking(passenger_name, contact_phone, terms_accepted):
    # Enable button only if all fields are filled and terms accepted
    return not all([passenger_name, contact_phone, terms_accepted])

@callback(
    Output("booking-result", "children"),
    Input("complete-booking-btn", "n_clicks"),
    [State("booking-flight-id", "data"),
     State("booking-passengers", "data")],
    prevent_initial_call=True
)
def complete_booking(n_clicks, flight_id, passengers):
    if not flight_id:
        return dbc.Alert("No flight selected", color="danger")
    
    # Get the user ID from session
    user_id = flask.session.get("user_id")
    if not user_id:
        return dbc.Alert("You need to be logged in to complete a booking", color="danger")
    
    try:
        session = get_session()
        
        # Get the flight schedule
        flight_schedule = session.query(FlightSchedule).filter_by(id=flight_id).first()
        if not flight_schedule:
            return dbc.Alert("Flight not found", color="danger")
        
        # Generate a unique confirmation code
        confirmation_code = generate_confirmation_code()
        
        # Calculate cost
        passengers = int(passengers) if passengers else 1
        total_cost = flight_schedule.flight.base_cost * passengers
        
        # Create the booking
        booking = Booking(
            passenger_id=user_id,
            flight_schedule_id=flight_id,
            confirmation_code=confirmation_code,
            cost_charged=total_cost,
            payment_status=PaymentStatus.COMPLETED
        )
        
        session.add(booking)
        session.commit()
        
        # Return success message with booking details
        return html.Div([
            dbc.Alert([
                html.H4("Booking Successful!", className="alert-heading"),
                html.P([
                    "Your flight has been booked! Your confirmation code is: ",
                    html.Strong(confirmation_code)
                ]),
                html.Hr(),
                html.P(
                    "You will receive a confirmation email shortly with your booking details.",
                    className="mb-0"
                )
            ], color="success"),
            dcc.Location(pathname="/bookings", id="redirect-to-bookings")
        ])
        
    except Exception as e:
        return dbc.Alert(f"Error completing booking: {str(e)}", color="danger") 