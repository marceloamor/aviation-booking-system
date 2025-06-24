import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from src.utils.database import get_session
from src.models.flight import Flight, FlightSchedule, FlightStatus
import pandas as pd
from datetime import datetime, timedelta
import flask

dash.register_page(__name__, path='/flights')

# Define UK airports for the dropdowns
UK_AIRPORTS = [
    {"label": "London Heathrow (LHR)", "value": "LHR"},
    {"label": "London Gatwick (LGW)", "value": "LGW"},
    {"label": "Manchester (MAN)", "value": "MAN"},
    {"label": "Edinburgh (EDI)", "value": "EDI"},
    {"label": "Glasgow (GLA)", "value": "GLA"},
    {"label": "Birmingham (BHX)", "value": "BHX"},
    {"label": "Bristol (BRS)", "value": "BRS"},
    {"label": "Newcastle (NCL)", "value": "NCL"},
    {"label": "Aberdeen (ABZ)", "value": "ABZ"},
    {"label": "Belfast (BFS)", "value": "BFS"}
]

# Date picker min and max dates
min_date = datetime.now().date()
max_date = min_date + timedelta(days=365)  # Allow booking up to 1 year in advance

layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H2("Find Flights", className="mb-4"),
            dbc.Card([
                dbc.CardBody([
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("From"),
                                dcc.Dropdown(
                                    id="flight-from",
                                    options=UK_AIRPORTS,
                                    placeholder="Select departure airport"
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("To"),
                                dcc.Dropdown(
                                    id="flight-to",
                                    options=UK_AIRPORTS,
                                    placeholder="Select arrival airport"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Departure Date"),
                                dcc.DatePickerSingle(
                                    id="flight-date",
                                    min_date_allowed=min_date,
                                    max_date_allowed=max_date,
                                    initial_visible_month=min_date,
                                    placeholder="Select departure date"
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Number of Passengers"),
                                dcc.Dropdown(
                                    id="flight-passengers",
                                    options=[
                                        {"label": f"{i} passenger{'s' if i > 1 else ''}", "value": i}
                                        for i in range(1, 9)
                                    ],
                                    value=1
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Search Flights",
                                    id="search-flights-btn",
                                    color="primary",
                                    className="w-100"
                                )
                            ])
                        ])
                    ])
                ])
            ], className="mb-4"),
            
            # Flight search results
            html.Div(id="flight-search-results")
        ])
    ])
])

@callback(
    Output("flight-search-results", "children"),
    Input("search-flights-btn", "n_clicks"),
    State("flight-from", "value"),
    State("flight-to", "value"),
    State("flight-date", "date"),
    State("flight-passengers", "value"),
    prevent_initial_call=True
)
def search_flights(n_clicks, from_airport, to_airport, departure_date, num_passengers):
    if not all([from_airport, to_airport, departure_date]):
        return dbc.Alert(
            "Please select departure airport, arrival airport, and departure date.",
            color="warning"
        )
    
    if from_airport == to_airport:
        return dbc.Alert(
            "Departure and arrival airports cannot be the same.",
            color="warning"
        )
    
    try:
        # Convert date string to datetime object
        selected_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
        
        # Query flights
        session = get_session()
        
        # Find flight schedules matching the criteria
        query = session.query(
            FlightSchedule
        ).filter(
            FlightSchedule.departure_airport == from_airport,
            FlightSchedule.arrival_airport == to_airport,
            FlightSchedule.scheduled_departure_time >= datetime.combine(selected_date, datetime.min.time()),
            FlightSchedule.scheduled_departure_time < datetime.combine(selected_date + timedelta(days=1), datetime.min.time())
        )
        
        flight_schedules = query.all()
        
        if not flight_schedules:
            return dbc.Alert(
                f"No flights found from {from_airport} to {to_airport} on {selected_date.strftime('%d %b %Y')}.",
                color="info"
            )
        
        # Prepare data for table
        data = []
        for fs in flight_schedules:
            departure_time = fs.scheduled_departure_time.strftime("%H:%M")
            arrival_time = fs.scheduled_arrival_time.strftime("%H:%M")
            duration = (fs.scheduled_arrival_time - fs.scheduled_departure_time).total_seconds() / 60
            duration_str = f"{int(duration // 60)}h {int(duration % 60)}m"
            
            flight = fs.flight
            cost = flight.base_cost * num_passengers
            
            data.append({
                "flight_id": fs.id,
                "flight_number": flight.flight_number,
                "departure": f"{from_airport} ({departure_time})",
                "arrival": f"{to_airport} ({arrival_time})",
                "duration": duration_str,
                "aircraft": flight.aircraft.model_number,
                "status": fs.status.value,
                "cost": f"£{cost:.2f}",
                "base_cost": cost  # Used for sorting
            })
        
        # Convert to DataFrame for table
        df = pd.DataFrame(data)
        
        # Create results component
        results = html.Div([
            html.H4(f"Flights from {from_airport} to {to_airport} on {selected_date.strftime('%d %b %Y')}"),
            html.P(f"Showing {len(data)} flight{'s' if len(data) > 1 else ''} for {num_passengers} passenger{'s' if num_passengers > 1 else ''}"),
            
            dash_table.DataTable(
                id="flights-table",
                columns=[
                    {"name": "Flight", "id": "flight_number"},
                    {"name": "Departure", "id": "departure"},
                    {"name": "Arrival", "id": "arrival"},
                    {"name": "Duration", "id": "duration"},
                    {"name": "Aircraft", "id": "aircraft"},
                    {"name": "Status", "id": "status"},
                    {"name": "Total Cost", "id": "cost"},
                ],
                data=df.to_dict("records"),
                sort_action="native",
                sort_by=[{"column_id": "base_cost", "direction": "asc"}],
                row_selectable="single",
                selected_rows=[],
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "left",
                    "padding": "10px"
                },
                style_header={
                    "backgroundColor": "rgb(230, 230, 230)",
                    "fontWeight": "bold"
                }
            ),
            
            dbc.Button(
                "Book Selected Flight",
                id="book-flight-btn",
                color="success",
                className="mt-3",
                disabled=True
            ),
            
            dcc.Store(id="selected-flight-id")
        ])
        
        return results
        
    except Exception as e:
        return dbc.Alert(
            f"An error occurred while searching for flights: {str(e)}",
            color="danger"
        )

@callback(
    [Output("book-flight-btn", "disabled"),
     Output("selected-flight-id", "data")],
    [Input("flights-table", "selected_rows")],
    [State("flights-table", "data")],
    prevent_initial_call=True
)
def update_book_button(selected_rows, table_data):
    if not selected_rows:
        return True, None
    
    selected_flight_id = table_data[selected_rows[0]]["flight_id"]
    return False, selected_flight_id

@callback(
    Output("flight-search-results", "children", allow_duplicate=True),
    Input("book-flight-btn", "n_clicks"),
    State("selected-flight-id", "data"),
    State("flight-passengers", "value"),
    prevent_initial_call=True
)
def handle_booking_redirect(n_clicks, flight_id, num_passengers):
    if not flight_id:
        return dash.no_update
    
    # Store booking info in session
    flask.session["booking_flight_id"] = flight_id
    flask.session["booking_passengers"] = num_passengers
    
    # Redirect to booking page
    return html.Div([
        dbc.Alert("Redirecting to booking page...", color="success"),
        dcc.Location(pathname="/bookings/new", id="redirect-to-booking")
    ]) 