import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from src.utils.database import get_session
from src.models.booking import Booking
from src.models.flight import FlightSchedule
import flask
from datetime import datetime

dash.register_page(__name__, path='/')

def layout():
    return html.Div([
        # Dynamic content that changes based on login status
        html.Div(id="home-content")
    ])

@callback(
    Output("home-content", "children"),
    Input("login-status", "data")
)
def update_home_content(login_status):
    # Check if user is logged in
    user_id = flask.session.get("user_id")
    user_name = flask.session.get("user_name")
    
    if user_id and user_name:
        # User is logged in - show personalized content
        return get_logged_in_content(user_id, user_name)
    else:
        # User is not logged in - show default content
        return get_default_content()

def get_logged_in_content(user_id, user_name):
    """Content for logged-in users"""
    
    # Get user's upcoming bookings
    try:
        session = get_session()
        upcoming_bookings = session.query(Booking).join(
            Booking.flight_schedule
        ).filter(
            Booking.passenger_id == user_id,
            Booking.flight_schedule.has(
                FlightSchedule.scheduled_departure_time > datetime.now()
            )
        ).order_by(
            FlightSchedule.scheduled_departure_time.asc()
        ).limit(3).all()
        
        recent_bookings = session.query(Booking).join(
            Booking.flight_schedule
        ).filter(
            Booking.passenger_id == user_id
        ).order_by(
            Booking.booking_date.desc()
        ).limit(3).all()
        
    except Exception as e:
        upcoming_bookings = []
        recent_bookings = []
    
    first_name = user_name.split()[0]
    
    return dbc.Row([
        dbc.Col([
            html.H1(f"Welcome back, {first_name}!", className="mb-4"),
            html.P(
                "Ready for your next adventure? Manage your bookings or find new destinations below.",
                className="lead"
            ),
            
            # Upcoming flights section
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.H5("Your Upcoming Flights", className="mb-0"), width="auto"),
                        dbc.Col(dbc.Button("View All", color="outline-primary", size="sm", href="/bookings"), 
                                width="auto", className="ms-auto")
                    ])
                ]),
                dbc.CardBody([
                    get_upcoming_flights_content(upcoming_bookings)
                ])
            ], className="mb-4"),
            
            # Quick actions
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🔍 Search Flights", className="card-title"),
                            html.P("Find and book your next flight", className="card-text"),
                            dbc.Button("Search Now", color="primary", href="/flights", className="w-100")
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📋 My Bookings", className="card-title"),
                            html.P("Manage your current reservations", className="card-text"),
                            dbc.Button("View Bookings", color="success", href="/bookings", className="w-100")
                        ])
                    ])
                ], width=6)
            ])
        ], width=8),
        
        dbc.Col([
            # Account summary
            dbc.Card([
                dbc.CardHeader("Account Summary"),
                dbc.CardBody([
                    html.P([
                        html.Strong("Total Bookings: "),
                        str(len(recent_bookings))
                    ]),
                    html.P([
                        html.Strong("Upcoming Trips: "),
                        str(len(upcoming_bookings))
                    ]),
                    html.Hr(),
                    dbc.Button("Account Settings", color="outline-secondary", size="sm", href="/profile", className="w-100")
                ])
            ], className="mb-4"),
            
            # Quick links
            dbc.Card([
                dbc.CardHeader("Quick Links"),
                dbc.ListGroup([
                    dbc.ListGroupItem("Flight Status", href="/status"),
                    dbc.ListGroupItem("Check-in Online", href="/check-in"),
                    dbc.ListGroupItem("Baggage Info", href="/baggage"),
                    dbc.ListGroupItem("Contact Support", href="/contact"),
                ], flush=True)
            ])
        ], width=4)
    ])

def get_upcoming_flights_content(bookings):
    """Generate content for upcoming flights section"""
    if not bookings:
        return dbc.Alert([
            "No upcoming flights. ",
            dbc.Button("Book a flight", color="primary", size="sm", href="/flights", className="ms-2")
        ], color="info")
    
    flight_cards = []
    for booking in bookings:
        flight_schedule = booking.flight_schedule
        flight = flight_schedule.flight
        
        # Format date and times
        flight_date = flight_schedule.scheduled_departure_time.strftime("%a, %d %b")
        departure_time = flight_schedule.scheduled_departure_time.strftime("%H:%M")
        
        flight_cards.append(
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6(f"Flight {flight.flight_number}", className="mb-1"),
                            html.P(f"{flight_schedule.departure_airport} → {flight_schedule.arrival_airport}", 
                                   className="mb-1"),
                            html.Small(f"{flight_date} at {departure_time}", className="text-muted")
                        ], width=8),
                        dbc.Col([
                            html.Span(
                                flight_schedule.status.value,
                                className=f"badge bg-{'success' if flight_schedule.status.value == 'Scheduled' else 'warning'}"
                            )
                        ], width=4, className="text-end")
                    ])
                ])
            ], className="mb-2")
        )
    
    return html.Div(flight_cards)

def get_default_content():
    """Content for non-logged-in users"""
    return dbc.Row([
        dbc.Col([
            html.H1("Welcome to Northeastern Airways", className="mb-4"),
            html.P(
                "Book your next journey across the UK with Northeastern Airways, "
                "your trusted partner for reliable and comfortable air travel.",
                className="lead"
            ),
            
            # Call-to-action for non-logged users
            dbc.Alert([
                html.H5("Ready to start your journey?", className="alert-heading"),
                html.P("Sign up or log in to unlock personalized features and manage your bookings."),
                dbc.ButtonGroup([
                    dbc.Button("Sign Up", color="primary", href="/register"),
                    dbc.Button("Log In", color="outline-primary", href="/login")
                ])
            ], color="info", className="mb-4"),
            
            dbc.Card([
                dbc.CardImg(src="/assets/plane-banner.jpg", top=True),
                dbc.CardBody([
                    html.H4("Find Your Flight", className="card-title"),
                    html.P(
                        "Search for available flights and book your next journey.",
                        className="card-text"
                    ),
                    dbc.Button("Search Flights", color="primary", href="/flights")
                ])
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Quick Booking", className="card-title"),
                            html.P(
                                "Already know your travel dates? Book directly!",
                                className="card-text"
                            ),
                            dbc.Button("Book Now", color="success", href="/flights")
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Check-in Online", className="card-title"),
                            html.P(
                                "Save time at the airport with our easy online check-in.",
                                className="card-text"
                            ),
                            dbc.Button("Check-in", color="info", href="/check-in")
                        ])
                    ])
                ], width=6)
            ])
        ], width=8),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Latest Updates"),
                dbc.CardBody([
                    html.H5("New Summer Routes Added!", className="card-title"),
                    html.P(
                        "We've added new routes for the summer season. "
                        "Explore our destinations and plan your holiday!",
                        className="card-text"
                    ),
                    html.Hr(),
                    html.H5("COVID-19 Travel Information", className="card-title"),
                    html.P(
                        "We're committed to ensuring your safety during travel. "
                        "Check our latest COVID-19 policies before your journey.",
                        className="card-text"
                    ),
                    html.Hr(),
                    html.H5("Special Offers", className="card-title"),
                    html.P(
                        "Book your flight today and enjoy special discounts "
                        "on selected destinations.",
                        className="card-text"
                    )
                ])
            ], className="mb-4"),
            
            dbc.Card([
                dbc.CardHeader("Quick Links"),
                dbc.ListGroup([
                    dbc.ListGroupItem("Flight Status", href="/status"),
                    dbc.ListGroupItem("Baggage Information", href="/baggage"),
                    dbc.ListGroupItem("Contact Us", href="/contact"),
                    dbc.ListGroupItem("FAQs", href="/faqs"),
                ], flush=True)
            ])
        ], width=4)
    ]) 