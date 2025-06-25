import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta
from src.utils.database import get_session
from src.models.user import User
from src.models.flight import Flight, FlightSchedule, FlightStatus
from src.models.aircraft import Aircraft
from src.utils.components import protected_page, create_page_header, create_stats_card
from src.utils.auth import get_user_display_info
from sqlalchemy import func, text, case
import string
import random
import flask

dash.register_page(__name__, path="/staff")

@protected_page("technical_staff")
def layout():
    """Flight management dashboard for technical staff"""
    user_info = get_user_display_info()
    
    # Get operational statistics
    session = get_session()
    try:
        # Flight statistics
        total_flights = session.query(Flight).count()
        total_schedules = session.query(FlightSchedule).count()
        
        # Today's operations
        today = datetime.now().date()
        today_schedules = session.query(FlightSchedule).filter(
            func.date(FlightSchedule.scheduled_departure_time) == today
        ).count()
        
        # Aircraft availability
        total_aircraft = session.query(Aircraft).count()
        
        # Upcoming schedules (next 7 days)
        week_from_now = datetime.now() + timedelta(days=7)
        upcoming_schedules = session.query(FlightSchedule).filter(
            FlightSchedule.scheduled_departure_time <= week_from_now,
            FlightSchedule.scheduled_departure_time >= datetime.now()
        ).count()
        
    except Exception as e:
        print(f"Error getting staff stats: {e}")
        total_flights = total_schedules = today_schedules = total_aircraft = upcoming_schedules = 0
    finally:
        session.close()
    
    return html.Div([
        # Page header
        create_page_header(
            "Flight Management", 
            "Technical operations and schedule management",
            user_info
        ),
        
        # Quick statistics cards
        dbc.Row([
            dbc.Col([
                create_stats_card(
                    "Total Flight Routes", 
                    total_flights,
                    "Active flight routes",
                    "primary",
                    "fas fa-route"
                )
            ], md=3),
            dbc.Col([
                create_stats_card(
                    "Total Schedules", 
                    total_schedules,
                    f"{today_schedules} scheduled today",
                    "success",
                    "fas fa-calendar-alt"
                )
            ], md=3),
            dbc.Col([
                create_stats_card(
                    "Aircraft Fleet", 
                    total_aircraft,
                    "Available aircraft",
                    "info",
                    "fas fa-plane"
                )
            ], md=3),
            dbc.Col([
                create_stats_card(
                    "Upcoming Flights", 
                    upcoming_schedules,
                    "Next 7 days",
                    "warning",
                    "fas fa-clock"
                )
            ], md=3),
        ], className="mb-4"),
        
        # Management sections
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("✈️ Flight Management", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Create and manage flight routes", className="card-text"),
                        dbc.ButtonGroup([
                            dbc.Button("Create New Flight", color="primary", id="btn-create-flight"),
                            dbc.Button("View All Flights", color="outline-primary", id="btn-view-flights"),
                        ])
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📅 Schedule Management", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Manage flight schedules and timing", className="card-text"),
                        dbc.ButtonGroup([
                            dbc.Button("Create Schedule", color="success", id="btn-create-schedule"),
                            dbc.Button("View Schedules", color="outline-success", id="btn-view-schedules"),
                        ])
                    ])
                ])
            ], md=6),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("🛩️ Aircraft Management", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Monitor aircraft status and availability", className="card-text"),
                        dbc.ButtonGroup([
                            dbc.Button("Aircraft Status", color="info", id="btn-aircraft-status"),
                            dbc.Button("Maintenance Log", color="outline-info", id="btn-maintenance-log"),
                        ])
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📊 Operations Reports", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Flight operations analytics and reports", className="card-text"),
                        dbc.ButtonGroup([
                            dbc.Button("Daily Operations", color="warning", id="btn-daily-ops"),
                            dbc.Button("Performance Reports", color="outline-warning", id="btn-performance-reports"),
                        ])
                    ])
                ])
            ], md=6),
        ], className="mb-4"),
        
        # Content area for dynamic loading
        html.Div(id="staff-content", className="mt-4"),
        
        # Store for current view
        dcc.Store(id="staff-current-view")
    ])

# Callbacks for the different staff views
@callback(
    [Output("staff-content", "children"),
     Output("staff-current-view", "data")],
    [Input("btn-create-flight", "n_clicks"),
     Input("btn-view-flights", "n_clicks"),
     Input("btn-create-schedule", "n_clicks"),
     Input("btn-view-schedules", "n_clicks"),
     Input("btn-aircraft-status", "n_clicks"),
     Input("btn-maintenance-log", "n_clicks"),
     Input("btn-daily-ops", "n_clicks"),
     Input("btn-performance-reports", "n_clicks")],
    prevent_initial_call=True
)
def handle_staff_navigation(create_flight_btn, view_flights_btn, create_schedule_btn, view_schedules_btn,
                          aircraft_btn, maintenance_btn, daily_ops_btn, performance_btn):
    ctx = dash.callback_context
    if not ctx.triggered:
        return html.Div(), None
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "btn-create-flight":
        return load_create_flight_view(), "create_flight"
    elif button_id == "btn-view-flights":
        return load_view_flights_view(), "view_flights"
    elif button_id == "btn-create-schedule":
        return load_create_schedule_view(), "create_schedule"
    elif button_id == "btn-view-schedules":
        return load_view_schedules_view(), "view_schedules"
    elif button_id == "btn-aircraft-status":
        return load_aircraft_status_view(), "aircraft_status"
    elif button_id == "btn-maintenance-log":
        return load_maintenance_log_view(), "maintenance_log"
    elif button_id == "btn-daily-ops":
        return load_daily_operations_view(), "daily_ops"
    elif button_id == "btn-performance-reports":
        return load_performance_reports_view(), "performance_reports"
    
    return html.Div(), None

def load_create_flight_view():
    """Load the create flight form"""
    session = get_session()
    try:
        # Get available aircraft
        aircraft = session.query(Aircraft).all()
        aircraft_options = [
            {"label": f"{ac.registration_number} - {ac.model_number}", "value": ac.id}
            for ac in aircraft
        ]
        
    except Exception as e:
        print(f"Error loading aircraft: {e}")
        aircraft_options = []
    finally:
        session.close()
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("✈️ Create New Flight", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Alert([
                    html.Strong("Note: "),
                    "This creates a flight template. Routes and schedules are configured separately in the 'Create Schedule' section."
                ], color="info", className="mb-3"),
                
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Flight Number"),
                            dbc.Input(
                                type="text",
                                id="create-flight-number",
                                placeholder="e.g., NE401",
                                required=True
                            ),
                            dbc.FormText("Flight number must be unique")
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Aircraft"),
                            dcc.Dropdown(
                                id="create-flight-aircraft",
                                options=aircraft_options,
                                placeholder="Select aircraft",
                                clearable=False
                            )
                        ], md=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Base Cost (£)"),
                            dbc.Input(
                                type="number",
                                id="create-flight-cost",
                                placeholder="Base price",
                                min=0,
                                step=0.01,
                                required=True
                            ),
                            dbc.FormText("Base cost before any surcharges or route-specific pricing")
                        ], md=12)
                    ], className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "Create Flight",
                                id="submit-create-flight",
                                color="primary",
                                size="lg",
                                className="me-2"
                            ),
                            dbc.Button(
                                "Cancel",
                                id="cancel-create-flight",
                                color="outline-secondary",
                                size="lg"
                            )
                        ])
                    ])
                ]),
                
                html.Div(id="create-flight-output", className="mt-3")
            ])
        ])
    ])

def load_view_flights_view():
    """Load the view flights table"""
    session = get_session()
    try:
        # Get all flights with aircraft information
        flights = session.query(Flight).join(Aircraft).all()
        
        flight_data = []
        for flight in flights:
            # Get schedule count for this flight
            schedule_count = session.query(FlightSchedule).filter_by(flight_id=flight.id).count()
            
            flight_data.append({
                "ID": flight.id,
                "Flight Number": flight.flight_number,
                "Aircraft": f"{flight.aircraft.registration_number} ({flight.aircraft.model_number})",
                "Base Cost": f"£{flight.base_cost:.2f}",
                "Schedules": schedule_count,
                "Created": flight.created_at.strftime("%Y-%m-%d") if flight.created_at else "N/A"
            })
        
        df = pd.DataFrame(flight_data)
        
    except Exception as e:
        print(f"Error loading flights: {e}")
        df = pd.DataFrame()
    finally:
        session.close()
    
    if df.empty:
        return html.Div([
            dbc.Alert("No flights found. Create your first flight!", color="info")
        ])
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("✈️ All Flights", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Alert([
                    html.Strong("Note: "),
                    "Routes are defined per schedule. Use 'View Schedules' to see specific routes and times."
                ], color="info", className="mb-3"),
                
                dash_table.DataTable(
                    id="flights-table",
                    data=df.to_dict("records"),
                    columns=[{"name": col, "id": col} for col in df.columns],
                    sort_action="native",
                    filter_action="native",
                    page_action="native",
                    page_size=20,
                    style_cell={"textAlign": "left"},
                    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"}
                )
            ])
        ])
    ])

def load_create_schedule_view():
    """Load the create schedule form"""
    session = get_session()
    try:
        # Get available flights
        flights = session.query(Flight).all()
        flight_options = [
            {"label": f"{flight.flight_number} ({flight.aircraft.registration_number})", "value": flight.id}
            for flight in flights
        ]
        
    except Exception as e:
        print(f"Error loading flights: {e}")
        flight_options = []
    finally:
        session.close()
    
    # UK airport codes
    uk_airports = [
        {"label": "London Heathrow (LHR)", "value": "LHR"},
        {"label": "London Gatwick (LGW)", "value": "LGW"},
        {"label": "Manchester (MAN)", "value": "MAN"},
        {"label": "Edinburgh (EDI)", "value": "EDI"},
        {"label": "Glasgow (GLA)", "value": "GLA"},
        {"label": "Birmingham (BHX)", "value": "BHX"},
        {"label": "Bristol (BRS)", "value": "BRS"},
        {"label": "Newcastle (NCL)", "value": "NCL"},
        {"label": "Aberdeen (ABZ)", "value": "ABZ"},
        {"label": "Belfast (BFS)", "value": "BFS"},
        {"label": "Liverpool (LPL)", "value": "LPL"},
        {"label": "Southampton (SOU)", "value": "SOU"},
        {"label": "Cardiff (CWL)", "value": "CWL"},
    ]
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("📅 Create Flight Schedule", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Select Flight"),
                            dcc.Dropdown(
                                id="create-schedule-flight",
                                options=flight_options,
                                placeholder="Select flight",
                                clearable=False
                            )
                        ], md=12)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Origin Airport"),
                            dcc.Dropdown(
                                id="create-schedule-origin",
                                options=uk_airports,
                                placeholder="Select origin",
                                clearable=False
                            )
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Destination Airport"),
                            dcc.Dropdown(
                                id="create-schedule-destination",
                                options=uk_airports,
                                placeholder="Select destination",
                                clearable=False
                            )
                        ], md=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Departure Date"),
                            dbc.Input(
                                type="date",
                                id="create-schedule-date",
                                min=datetime.now().strftime("%Y-%m-%d"),
                                required=True
                            )
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Departure Time"),
                            dbc.Input(
                                type="time",
                                id="create-schedule-time",
                                required=True
                            )
                        ], md=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Status"),
                            dcc.Dropdown(
                                id="create-schedule-status",
                                options=[
                                    {"label": "Scheduled", "value": "SCHEDULED"},
                                    {"label": "Delayed", "value": "DELAYED"},
                                    {"label": "Cancelled", "value": "CANCELLED"}
                                ],
                                value="SCHEDULED",
                                clearable=False
                            )
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Gate (Optional)"),
                            dbc.Input(
                                type="text",
                                id="create-schedule-gate",
                                placeholder="e.g., A12"
                            )
                        ], md=6)
                    ], className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "Create Schedule",
                                id="submit-create-schedule",
                                color="success",
                                size="lg",
                                className="me-2"
                            ),
                            dbc.Button(
                                "Cancel",
                                id="cancel-create-schedule",
                                color="outline-secondary",
                                size="lg"
                            )
                        ])
                    ])
                ]),
                
                html.Div(id="create-schedule-output", className="mt-3")
            ])
        ])
    ])

def load_view_schedules_view():
    """Load the view schedules table"""
    session = get_session()
    try:
        # Get upcoming schedules (next 30 days)
        thirty_days_from_now = datetime.now() + timedelta(days=30)
        schedules = session.query(FlightSchedule).filter(
            FlightSchedule.scheduled_departure_time >= datetime.now(),
            FlightSchedule.scheduled_departure_time <= thirty_days_from_now
        ).join(Flight).order_by(FlightSchedule.scheduled_departure_time).all()
        
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                "ID": schedule.id,
                "Flight": schedule.flight.flight_number,
                "Route": f"{schedule.departure_airport} → {schedule.arrival_airport}",
                "Departure": schedule.scheduled_departure_time.strftime("%Y-%m-%d %H:%M"),
                "Arrival": schedule.scheduled_arrival_time.strftime("%Y-%m-%d %H:%M"),
                "Status": schedule.status.value if schedule.status else "Scheduled",
                "Gate": schedule.departure_gate or "TBA"
            })
        
        df = pd.DataFrame(schedule_data)
        
    except Exception as e:
        print(f"Error loading schedules: {e}")
        df = pd.DataFrame()
    finally:
        session.close()
    
    if df.empty:
        return html.Div([
            dbc.Alert("No upcoming schedules found. Create your first schedule!", color="info")
        ])
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("📅 Upcoming Flight Schedules (Next 30 Days)", className="mb-0")
            ]),
            dbc.CardBody([
                dash_table.DataTable(
                    id="schedules-table",
                    data=df.to_dict("records"),
                    columns=[{"name": col, "id": col} for col in df.columns],
                    sort_action="native",
                    filter_action="native",
                    page_action="native",
                    page_size=20,
                    style_cell={"textAlign": "left"},
                    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
                    style_data_conditional=[
                        {
                            "if": {"filter_query": '{Status} = "DELAYED"'},
                            "backgroundColor": "#fff3cd",
                            "color": "black",
                        },
                        {
                            "if": {"filter_query": '{Status} = "CANCELLED"'},
                            "backgroundColor": "#f8d7da",
                            "color": "black",
                        }
                    ]
                )
            ])
        ])
    ])

def load_aircraft_status_view():
    """Load aircraft status overview"""
    session = get_session()
    try:
        # Get all aircraft with their current status
        aircraft = session.query(Aircraft).all()
        
        aircraft_data = []
        for ac in aircraft:
            # Count scheduled flights for this aircraft
            scheduled_flights = session.query(FlightSchedule).join(Flight).filter(
                Flight.aircraft_id == ac.id,
                FlightSchedule.scheduled_departure_time >= datetime.now()
            ).count()
            
            aircraft_data.append({
                "Registration": ac.registration_number,
                "Model": ac.model_number,
                "Manufacturer": ac.manufacturer,
                "Class": ac.aircraft_class,
                "Capacity": ac.aip_info.split("Capacity: ")[-1].split(" passengers")[0] if "Capacity:" in ac.aip_info else "N/A",
                "Upcoming Flights": scheduled_flights,
                "Status": "Active" if scheduled_flights > 0 else "Available"
            })
        
        df = pd.DataFrame(aircraft_data)
        
    except Exception as e:
        print(f"Error loading aircraft status: {e}")
        df = pd.DataFrame()
    finally:
        session.close()
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("🛩️ Aircraft Fleet Status", className="mb-0")
            ]),
            dbc.CardBody([
                dash_table.DataTable(
                    data=df.to_dict("records") if not df.empty else [],
                    columns=[{"name": col, "id": col} for col in df.columns] if not df.empty else [],
                    sort_action="native",
                    filter_action="native",
                    page_action="native",
                    page_size=20,
                    style_cell={"textAlign": "left"},
                    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
                    style_data_conditional=[
                        {
                            "if": {"filter_query": '{Status} = "Active"'},
                            "backgroundColor": "#d4edda",
                            "color": "black",
                        }
                    ]
                ) if not df.empty else dbc.Alert("No aircraft data available", color="info")
            ])
        ])
    ])

def load_maintenance_log_view():
    """Load maintenance log placeholder"""
    return dbc.Alert([
        html.H5("🔧 Aircraft Maintenance Log"),
        html.P("Aircraft maintenance tracking system will be implemented here."),
        html.P("Features to include: maintenance schedules, service history, compliance tracking.")
    ], color="info")

def load_daily_operations_view():
    """Load daily operations overview"""
    session = get_session()
    try:
        today = datetime.now().date()
        
        # Today's flights
        today_flights = session.query(FlightSchedule).filter(
            func.date(FlightSchedule.scheduled_departure_time) == today
        ).join(Flight).all()
        
        # Create operations summary
        ops_data = []
        for schedule in today_flights:
            ops_data.append({
                "Time": schedule.scheduled_departure_time.strftime("%H:%M"),
                "Flight": schedule.flight.flight_number,
                "Route": f"{schedule.departure_airport} → {schedule.arrival_airport}",
                "Aircraft": schedule.flight.aircraft.registration_number,
                "Status": schedule.status.value if schedule.status else "Scheduled",
                "Gate": schedule.departure_gate or "TBA"
            })
        
        df = pd.DataFrame(ops_data)
        
    except Exception as e:
        print(f"Error loading daily operations: {e}")
        df = pd.DataFrame()
    finally:
        session.close()
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5(f"📊 Daily Operations - {datetime.now().strftime('%Y-%m-%d')}", className="mb-0")
            ]),
            dbc.CardBody([
                dash_table.DataTable(
                    data=df.to_dict("records") if not df.empty else [],
                    columns=[{"name": col, "id": col} for col in df.columns] if not df.empty else [],
                    sort_action="native",
                    page_size=20,
                    style_cell={"textAlign": "left"},
                    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"}
                ) if not df.empty else dbc.Alert("No flights scheduled for today", color="info")
            ])
        ])
    ])

def load_performance_reports_view():
    """Load performance reports with comprehensive flight analytics"""
    session = get_session()
    try:
        # COMPLEX QUERY 2: Comprehensive Flight Performance Analysis
        # This uses multiple joins, subqueries, conditional aggregations, and performance metrics
        performance_analysis = session.execute(text("""
            SELECT 
                f.flight_number,
                fs.departure_airport as origin,
                fs.arrival_airport as destination,
                a.registration_number as aircraft,
                a.model_number,
                COUNT(fs.id) as total_schedules,
                SUM(CASE WHEN fs.status = 'SCHEDULED' THEN 1 ELSE 0 END) as scheduled_flights,
                SUM(CASE WHEN fs.status = 'DELAYED' THEN 1 ELSE 0 END) as delayed_flights,
                SUM(CASE WHEN fs.status = 'CANCELLED' THEN 1 ELSE 0 END) as cancelled_flights,
                ROUND(
                    (SUM(CASE WHEN fs.status = 'SCHEDULED' THEN 1 ELSE 0 END) * 100.0) / 
                    COUNT(fs.id), 2
                ) as on_time_percentage,
                COUNT(b.id) as total_bookings,
                COALESCE(SUM(b.cost_charged), 0) as total_revenue,
                ROUND(AVG(b.cost_charged), 2) as avg_booking_value,
                ROUND(
                    (COUNT(b.id) * 100.0) / 
                    NULLIF(COUNT(fs.id), 0), 2
                ) as load_factor_percentage,
                MIN(fs.scheduled_departure_time) as first_flight,
                MAX(fs.scheduled_departure_time) as last_flight
            FROM flights f
            JOIN aircraft a ON f.aircraft_id = a.id
            LEFT JOIN flight_schedules fs ON f.id = fs.flight_id
            LEFT JOIN bookings b ON fs.id = b.flight_schedule_id
            WHERE fs.scheduled_departure_time >= DATE('now', '-90 days')
            GROUP BY f.id, f.flight_number, fs.departure_airport, fs.arrival_airport, a.registration_number, a.model_number
            HAVING COUNT(fs.id) > 0
            ORDER BY on_time_percentage DESC, total_revenue DESC
        """)).fetchall()
        
        # Aircraft efficiency analysis with subqueries
        aircraft_efficiency = session.execute(text("""
            SELECT 
                a.registration_number,
                a.model_number,
                a.manufacturer,
                COUNT(DISTINCT f.id) as routes_operated,
                COUNT(fs.id) as total_flights,
                AVG(
                    CASE 
                        WHEN fs.status = 'SCHEDULED' THEN 1.0
                        WHEN fs.status = 'DELAYED' THEN 0.7
                        ELSE 0.0
                    END
                ) as efficiency_score,
                SUM(b.cost_charged) as revenue_generated,
                COUNT(b.id) as passengers_carried,
                ROUND(
                    SUM(b.cost_charged) / NULLIF(COUNT(fs.id), 0), 2
                ) as revenue_per_flight
            FROM aircraft a
            LEFT JOIN flights f ON a.id = f.aircraft_id
            LEFT JOIN flight_schedules fs ON f.id = fs.flight_id
            LEFT JOIN bookings b ON fs.id = b.flight_schedule_id
            WHERE fs.scheduled_departure_time >= DATE('now', '-90 days')
            GROUP BY a.id, a.registration_number, a.model_number, a.manufacturer
            HAVING COUNT(fs.id) > 0
            ORDER BY efficiency_score DESC, revenue_generated DESC
        """)).fetchall()
        
    except Exception as e:
        print(f"Error loading performance reports: {e}")
        performance_analysis = []
        aircraft_efficiency = []
    finally:
        session.close()
    
    # Create flight performance data
    performance_data = []
    for perf in performance_analysis:
        performance_data.append({
            "Flight": perf.flight_number,
            "Route": f"{perf.origin} → {perf.destination}",
            "Aircraft": f"{perf.aircraft} ({perf.model_number})",
            "Total Flights": perf.total_schedules,
            "On-Time %": f"{perf.on_time_percentage}%",
            "Load Factor %": f"{perf.load_factor_percentage}%",
            "Total Revenue": f"£{perf.total_revenue:,.2f}",
            "Avg Booking": f"£{perf.avg_booking_value:.2f}" if perf.avg_booking_value else "N/A",
            "Status": "Excellent" if perf.on_time_percentage >= 90 else "Good" if perf.on_time_percentage >= 75 else "Needs Improvement"
        })
    
    performance_df = pd.DataFrame(performance_data)
    
    # Create aircraft efficiency data
    efficiency_data = []
    for eff in aircraft_efficiency:
        efficiency_data.append({
            "Aircraft": eff.registration_number,
            "Model": f"{eff.manufacturer} {eff.model_number}",
            "Routes": eff.routes_operated,
            "Total Flights": eff.total_flights,
            "Efficiency Score": f"{eff.efficiency_score:.2f}",
            "Revenue": f"£{eff.revenue_generated:,.2f}" if eff.revenue_generated else "£0",
            "Passengers": eff.passengers_carried or 0,
            "Revenue/Flight": f"£{eff.revenue_per_flight:.2f}" if eff.revenue_per_flight else "£0"
        })
    
    efficiency_df = pd.DataFrame(efficiency_data)
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("📈 Comprehensive Flight Performance Analytics", className="mb-0")
            ]),
            dbc.CardBody([
                # Performance overview
                dbc.Alert([
                    html.H6("📊 Performance Analysis Overview", className="mb-2"),
                    html.P("This analysis covers the last 90 days of flight operations, including on-time performance, load factors, and revenue metrics.")
                ], color="info", className="mb-4"),
                
                # Flight performance table
                html.H6("✈️ Flight Route Performance (Last 90 Days)", className="mb-3"),
                dash_table.DataTable(
                    data=performance_df.to_dict("records") if not performance_df.empty else [],
                    columns=[{"name": col, "id": col} for col in performance_df.columns] if not performance_df.empty else [],
                    style_cell={"textAlign": "left", "fontSize": "12px"},
                    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
                    page_size=15,
                    style_data_conditional=[
                        {
                            "if": {"filter_query": '{Status} = "Excellent"'},
                            "backgroundColor": "#d4edda",
                            "color": "black",
                        },
                        {
                            "if": {"filter_query": '{Status} = "Good"'},
                            "backgroundColor": "#fff3cd",
                            "color": "black",
                        },
                        {
                            "if": {"filter_query": '{Status} = "Needs Improvement"'},
                            "backgroundColor": "#f8d7da",
                            "color": "black",
                        }
                    ]
                ) if not performance_df.empty else dbc.Alert("No flight performance data available", color="warning"),
                
                html.Hr(className="my-4"),
                
                # Aircraft efficiency table
                html.H6("🛩️ Aircraft Efficiency Analysis", className="mb-3"),
                dash_table.DataTable(
                    data=efficiency_df.to_dict("records") if not efficiency_df.empty else [],
                    columns=[{"name": col, "id": col} for col in efficiency_df.columns] if not efficiency_df.empty else [],
                    style_cell={"textAlign": "left", "fontSize": "12px"},
                    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
                    page_size=10,
                    style_data_conditional=[
                        {
                            "if": {"row_index": 0},
                            "backgroundColor": "#e8f5e8",
                            "color": "black",
                        }
                    ]
                ) if not efficiency_df.empty else dbc.Alert("No aircraft efficiency data available", color="warning"),
                
                # Key metrics summary
                html.Hr(className="my-4"),
                dbc.Alert([
                    html.H6("🎯 Key Performance Indicators", className="mb-2"),
                    html.Ul([
                        html.Li("On-Time Performance: Percentage of flights departing as scheduled"),
                        html.Li("Load Factor: Percentage of scheduled flights that have bookings"),
                        html.Li("Efficiency Score: Weighted performance metric (1.0 = scheduled, 0.7 = delayed, 0.0 = cancelled)"),
                        html.Li("Revenue per Flight: Average revenue generated per flight operation")
                    ])
                ], color="light")
            ])
        ])
    ])

# Callback for creating flights
@callback(
    Output("create-flight-output", "children"),
    Input("submit-create-flight", "n_clicks"),
    [State("create-flight-number", "value"),
     State("create-flight-aircraft", "value"),
     State("create-flight-cost", "value")],
    prevent_initial_call=True
)
def create_flight(n_clicks, flight_number, aircraft_id, cost):
    if not all([flight_number, aircraft_id, cost]):
        return dbc.Alert("Please fill in all required fields", color="danger")
    
    session = get_session()
    try:
        # Check if flight number already exists
        existing_flight = session.query(Flight).filter_by(flight_number=flight_number.upper()).first()
        if existing_flight:
            return dbc.Alert("Flight number already exists", color="danger")
        
        # Get current user
        user_id = flask.session.get("user_id")
        if not user_id:
            return dbc.Alert("User not logged in", color="danger")
        
        # Create new flight - only with valid Flight model fields
        new_flight = Flight(
            flight_number=flight_number.upper(),
            aircraft_id=aircraft_id,
            base_cost=float(cost),
            created_by_user_id=user_id
        )
        
        session.add(new_flight)
        session.commit()
        
        return dbc.Alert([
            html.H6("✅ Flight Created Successfully!", className="mb-2"),
            html.P(f"Flight {flight_number.upper()} has been created with base cost £{cost}."),
            html.P("You can now create schedules for this flight using the 'Create Schedule' section.", className="mb-0")
        ], color="success")
        
    except Exception as e:
        session.rollback()
        return dbc.Alert(f"Error creating flight: {str(e)}", color="danger")
    finally:
        session.close()

# Callback for creating schedules
@callback(
    Output("create-schedule-output", "children"),
    Input("submit-create-schedule", "n_clicks"),
    [State("create-schedule-flight", "value"),
     State("create-schedule-origin", "value"),
     State("create-schedule-destination", "value"),
     State("create-schedule-date", "value"),
     State("create-schedule-time", "value"),
     State("create-schedule-status", "value"),
     State("create-schedule-gate", "value")],
    prevent_initial_call=True
)
def create_schedule(n_clicks, flight_id, origin, destination, departure_date, departure_time, status, gate):
    if not all([flight_id, origin, destination, departure_date, departure_time, status]):
        return dbc.Alert("Please fill in all required fields", color="danger")
    
    if origin == destination:
        return dbc.Alert("Origin and destination airports cannot be the same", color="danger")
    
    session = get_session()
    try:
        # Get the flight to calculate duration
        flight = session.query(Flight).filter_by(id=flight_id).first()
        if not flight:
            return dbc.Alert("Flight not found", color="danger")
        
        # Parse departure datetime
        departure_datetime = datetime.strptime(f"{departure_date} {departure_time}", "%Y-%m-%d %H:%M")
        
        # Check if it's not in the past
        if departure_datetime <= datetime.now():
            return dbc.Alert("Departure time cannot be in the past", color="danger")
        
        # Calculate arrival time (assuming 1.5 hours default flight duration)
        arrival_datetime = departure_datetime + timedelta(hours=1.5)
        
        # Create flight schedule
        new_schedule = FlightSchedule(
            flight_id=flight_id,
            scheduled_departure_time=departure_datetime,
            scheduled_arrival_time=arrival_datetime,
            status=FlightStatus[status],
            departure_gate=gate if gate else None,
            departure_airport=origin,
            arrival_airport=destination
        )
        
        session.add(new_schedule)
        session.commit()
        
        return dbc.Alert([
            html.H6("✅ Schedule Created Successfully!", className="mb-2"),
            html.P(f"Schedule created for flight {flight.flight_number}"),
            html.P(f"Route: {origin} → {destination}"),
            html.P(f"Departure: {departure_date} at {departure_time}", className="mb-0")
        ], color="success")
        
    except ValueError as e:
        return dbc.Alert("Invalid date or time format", color="danger")
    except Exception as e:
        session.rollback()
        return dbc.Alert(f"Error creating schedule: {str(e)}", color="danger")
    finally:
        session.close() 