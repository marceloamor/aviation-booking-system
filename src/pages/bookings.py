import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from src.utils.database import get_session
from src.models.booking import Booking
from src.models.flight import FlightSchedule
from src.models.rating import Rating
import flask
import pandas as pd
from datetime import datetime

dash.register_page(__name__, path='/bookings')

def layout():
    # Check if user is logged in
    user_id = flask.session.get("user_id")
    if not user_id:
        return html.Div([
            dbc.Alert(
                [
                    "You need to be logged in to view your bookings. ",
                    dbc.Button("Log in", color="primary", href="/login", className="ms-2")
                ],
                color="warning"
            ),
            dcc.Location(pathname="/login", id="redirect-to-login")
        ])
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H2("My Bookings", className="mb-4"),
                
                # Tabs for active and past bookings
                dbc.Tabs([
                    dbc.Tab(
                        html.Div(id="active-bookings-content", className="pt-3"),
                        label="Upcoming Flights",
                        tab_id="upcoming-tab"
                    ),
                    dbc.Tab(
                        html.Div(id="past-bookings-content", className="pt-3"),
                        label="Past Flights",
                        tab_id="past-tab"
                    )
                ], id="bookings-tabs", active_tab="upcoming-tab"),
                
                # Modal for leaving a rating
                dbc.Modal([
                    dbc.ModalHeader(dbc.ModalTitle("Rate Your Flight")),
                    dbc.ModalBody([
                        html.Div(id="rating-modal-content"),
                        dcc.Store(id="rating-booking-id")
                    ]),
                    dbc.ModalFooter([
                        dbc.Button(
                            "Close",
                            id="rating-modal-close",
                            className="ms-auto",
                            color="secondary"
                        ),
                        dbc.Button(
                            "Submit Rating",
                            id="rating-submit-btn",
                            color="primary"
                        )
                    ])
                ], id="rating-modal", size="lg", is_open=False),
                
                # Thank you modal for after rating submission
                dbc.Modal([
                    dbc.ModalHeader(dbc.ModalTitle("✈️ Thank You!", className="text-center w-100")),
                    dbc.ModalBody([
                        html.Div([
                            html.Div("🎉", className="text-center", style={"fontSize": "4rem"}),
                            html.H4("Thank you for flying with Northeastern Airways!", className="text-center mb-3"),
                            html.P("Your feedback is incredibly valuable to us and helps us improve our service.", className="text-center mb-3"),
                            html.P("We look forward to welcoming you aboard again soon!", className="text-center mb-4"),
                            html.Div([
                                html.I(className="fas fa-plane me-2"),
                                html.Span("Safe travels!"),
                                html.I(className="fas fa-heart ms-2 text-danger")
                            ], className="text-center text-muted")
                        ])
                    ]),
                    dbc.ModalFooter([
                        dbc.Button(
                            "Continue",
                            id="thank-you-modal-close",
                            color="primary",
                            className="mx-auto"
                        )
                    ])
                ], id="thank-you-modal", size="md", is_open=False, centered=True)
            ])
        ])
    ])

@callback(
    Output("active-bookings-content", "children"),
    Input("bookings-tabs", "active_tab")
)
def load_active_bookings(active_tab):
    if active_tab != "upcoming-tab":
        return dash.no_update
    
    user_id = flask.session.get("user_id")
    if not user_id:
        return dbc.Alert("Please log in to view your bookings", color="warning")
    
    try:
        session = get_session()
        
        # Query future bookings (where scheduled departure is in the future)
        query = session.query(Booking).join(
            Booking.flight_schedule
        ).filter(
            Booking.passenger_id == user_id,
            Booking.flight_schedule.has(
                FlightSchedule.scheduled_departure_time > datetime.now()
            )
        ).order_by(
            FlightSchedule.scheduled_departure_time.asc()
        )
        
        bookings = query.all()
        
        if not bookings:
            return dbc.Alert(
                [
                    "You don't have any upcoming flights. ",
                    dbc.Button(
                        "Book a flight",
                        color="primary",
                        href="/flights",
                        size="sm",
                        className="ms-2"
                    )
                ],
                color="info"
            )
        
        # Create a list of booking cards
        booking_cards = []
        for booking in bookings:
            flight_schedule = booking.flight_schedule
            flight = flight_schedule.flight
            
            # Format date and times
            flight_date = flight_schedule.scheduled_departure_time.strftime("%a, %d %b %Y")
            departure_time = flight_schedule.scheduled_departure_time.strftime("%H:%M")
            arrival_time = flight_schedule.scheduled_arrival_time.strftime("%H:%M")
            
            booking_cards.append(
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Row([
                            dbc.Col(html.H5(f"Flight {flight.flight_number}"), width="auto"),
                            dbc.Col(html.H6(f"Confirmation: {booking.confirmation_code}"), width="auto", className="ms-auto")
                        ])
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H5(flight_date, className="card-title"),
                                html.Div([
                                    html.Span(flight_schedule.departure_airport, className="h4"),
                                    html.Span(" → ", className="mx-2"),
                                    html.Span(flight_schedule.arrival_airport, className="h4")
                                ])
                            ], width=6),
                            dbc.Col([
                                html.Div([
                                    html.P([
                                        html.Strong("Departure: "),
                                        f"{departure_time} from Terminal {flight_schedule.departure_terminal or 'TBA'}"
                                    ]),
                                    html.P([
                                        html.Strong("Arrival: "),
                                        f"{arrival_time}"
                                    ]),
                                    html.P([
                                        html.Strong("Status: "),
                                        html.Span(
                                            flight_schedule.status.value,
                                            className=f"badge bg-{'success' if flight_schedule.status.value == 'Scheduled' else 'warning'}"
                                        )
                                    ])
                                ])
                            ], width=6)
                        ]),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                html.P([
                                    html.Strong("Cost: "),
                                    f"£{booking.cost_charged:.2f}"
                                ])
                            ], width=6),
                            dbc.Col([
                                dbc.Button(
                                    "View Boarding Pass",
                                    color="primary",
                                    className="w-100"
                                )
                            ], width=6)
                        ])
                    ])
                ], className="mb-3")
            )
        
        return html.Div(booking_cards)
        
    except Exception as e:
        return dbc.Alert(f"Error loading bookings: {str(e)}", color="danger")

@callback(
    Output("past-bookings-content", "children"),
    Input("bookings-tabs", "active_tab")
)
def load_past_bookings(active_tab):
    if active_tab != "past-tab":
        return dash.no_update
    
    user_id = flask.session.get("user_id")
    if not user_id:
        return dbc.Alert("Please log in to view your bookings", color="warning")
    
    try:
        session = get_session()
        
        # Query past bookings (where scheduled departure is in the past)
        query = session.query(Booking).join(
            Booking.flight_schedule
        ).filter(
            Booking.passenger_id == user_id,
            Booking.flight_schedule.has(
                FlightSchedule.scheduled_departure_time <= datetime.now()
            )
        ).order_by(
            FlightSchedule.scheduled_departure_time.desc()
        )
        
        bookings = query.all()
        
        if not bookings:
            return dbc.Alert("You don't have any past flights.", color="info")
        
        # Create a list of booking cards
        booking_cards = []
        for booking in bookings:
            flight_schedule = booking.flight_schedule
            flight = flight_schedule.flight
            
            # Format date and times
            flight_date = flight_schedule.scheduled_departure_time.strftime("%a, %d %b %Y")
            departure_time = flight_schedule.scheduled_departure_time.strftime("%H:%M")
            arrival_time = flight_schedule.scheduled_arrival_time.strftime("%H:%M")
            
            # Check if the booking has a rating
            has_rating = booking.rating is not None
            
            booking_cards.append(
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Row([
                            dbc.Col(html.H5(f"Flight {flight.flight_number}"), width="auto"),
                            dbc.Col(html.H6(f"Confirmation: {booking.confirmation_code}"), width="auto", className="ms-auto")
                        ])
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H5(flight_date, className="card-title"),
                                html.Div([
                                    html.Span(flight_schedule.departure_airport, className="h4"),
                                    html.Span(" → ", className="mx-2"),
                                    html.Span(flight_schedule.arrival_airport, className="h4")
                                ])
                            ], width=6),
                            dbc.Col([
                                html.Div([
                                    html.P([
                                        html.Strong("Departure: "),
                                        f"{departure_time} from Terminal {flight_schedule.departure_terminal or 'TBA'}"
                                    ]),
                                    html.P([
                                        html.Strong("Arrival: "),
                                        f"{arrival_time}"
                                    ]),
                                    html.P([
                                        html.Strong("Status: "),
                                        html.Span(
                                            flight_schedule.status.value,
                                            className=f"badge bg-{'success' if flight_schedule.status.value == 'Landed' else 'warning'}"
                                        )
                                    ])
                                ])
                            ], width=6)
                        ]),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                html.P([
                                    html.Strong("Cost: "),
                                    f"£{booking.cost_charged:.2f}"
                                ])
                            ], width=6),
                            dbc.Col([
                                # If already rated, show the rating, otherwise show "Rate your flight" button
                                html.Div([
                                    html.P([
                                        html.Strong("Your Rating: "),
                                        "★" * booking.rating.stars + "☆" * (5 - booking.rating.stars)
                                    ]) if has_rating else dbc.Button(
                                        "Rate Your Flight",
                                        id={"type": "rate-flight-btn", "index": booking.id},
                                        color="success",
                                        className="w-100"
                                    )
                                ])
                            ], width=6)
                        ])
                    ])
                ], className="mb-3")
            )
        
        return html.Div(booking_cards)
        
    except Exception as e:
        return dbc.Alert(f"Error loading bookings: {str(e)}", color="danger")

@callback(
    [Output("rating-modal", "is_open"),
     Output("rating-modal-content", "children"),
     Output("rating-booking-id", "data")],
    [Input({"type": "rate-flight-btn", "index": dash.ALL}, "n_clicks")],
    [State("rating-modal", "is_open")],
    prevent_initial_call=True
)
def open_rating_modal(n_clicks, is_open):
    # If no button was clicked, return
    if not n_clicks or not any(n_clicks):
        return is_open, dash.no_update, dash.no_update
    
    # Find which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    booking_id = eval(button_id)["index"]
    
    # Get booking details
    session = get_session()
    booking = session.query(Booking).filter_by(id=booking_id).first()
    
    if not booking:
        return is_open, dash.no_update, dash.no_update
    
    flight_schedule = booking.flight_schedule
    flight = flight_schedule.flight
    
    # Format date and route for display
    flight_date = flight_schedule.scheduled_departure_time.strftime("%a, %d %b %Y")
    route = f"{flight_schedule.departure_airport} → {flight_schedule.arrival_airport}"
    
    # Create rating form
    rating_form = html.Div([
        html.H5(f"Flight {flight.flight_number} - {flight_date}"),
        html.P(f"{route}", className="mb-4"),
        
        html.Label("How would you rate your flight experience?", className="form-label"),
        dbc.RadioItems(
            id="rating-stars",
            options=[
                {"label": "★" * i + "☆" * (5 - i) + f" ({i} star{'s' if i > 1 else ''})", "value": i}
                for i in range(1, 6)
            ],
            value=5,
            inline=False,
            className="mb-3"
        ),
        
        html.Label("Additional Comments (Optional)", className="form-label"),
        dbc.Textarea(
            id="rating-comments",
            placeholder="Tell us more about your experience...",
            style={"height": "150px"}
        )
    ])
    
    return not is_open, rating_form, booking_id

@callback(
    [Output("rating-modal", "is_open", allow_duplicate=True),
     Output("thank-you-modal", "is_open", allow_duplicate=True),
     Output("past-bookings-content", "children", allow_duplicate=True)],
    Input("rating-submit-btn", "n_clicks"),
    [State("rating-booking-id", "data"),
     State("rating-stars", "value"),
     State("rating-comments", "value"),
     State("bookings-tabs", "active_tab")],
    prevent_initial_call=True
)
def submit_rating(n_clicks, booking_id, stars, comments, active_tab):
    if not n_clicks or not booking_id:
        return dash.no_update, dash.no_update, dash.no_update
    
    # Save the rating
    session = get_session()
    
    try:
        # Check if rating already exists
        existing_rating = session.query(Rating).filter_by(booking_id=booking_id).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.stars = stars
            existing_rating.comments = comments
        else:
            # Create new rating
            new_rating = Rating(
                booking_id=booking_id,
                stars=stars,
                comments=comments
            )
            session.add(new_rating)
            
            # Update the booking to mark thank you as sent
            booking = session.query(Booking).filter_by(id=booking_id).first()
            if booking:
                booking.thank_you_sent = True
        
        session.commit()
        
        # Close rating modal, show thank you modal, and refresh past bookings
        return False, True, load_past_bookings(active_tab)
        
    except Exception as e:
        return False, False, dbc.Alert(f"Error submitting rating: {str(e)}", color="danger")

# Callback to close the rating modal without submitting
@callback(
    Output("rating-modal", "is_open", allow_duplicate=True),
    Input("rating-modal-close", "n_clicks"),
    prevent_initial_call=True
)
def close_rating_modal(n_clicks):
    if n_clicks:
        return False
    return dash.no_update

# Callback to close the thank you modal
@callback(
    Output("thank-you-modal", "is_open", allow_duplicate=True),
    Input("thank-you-modal-close", "n_clicks"),
    prevent_initial_call=True
)
def close_thank_you_modal(n_clicks):
    if n_clicks:
        return False
    return dash.no_update 