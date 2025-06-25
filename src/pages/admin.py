import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta
from src.utils.database import get_session
from src.models.user import User
from src.models.role import Role
from src.models.booking import Booking
from src.models.flight import Flight, FlightSchedule
from src.models.aircraft import Aircraft
from src.utils.components import protected_page, create_page_header, create_stats_card
from src.utils.auth import get_user_display_info
from sqlalchemy import func, text

dash.register_page(__name__, path="/admin")

@protected_page("admin")
def layout():
    """Admin dashboard layout"""
    user_info = get_user_display_info()
    
    # Get database statistics
    session = get_session()
    try:
        # User statistics - using SQL joins to avoid relationship loading issues
        total_users = session.query(User).count()
        
        # Count admin users using SQL join
        admin_users = session.query(User).join(User.roles).filter(Role.name == "admin").count()
        
        # Count staff users using SQL join
        staff_users = session.query(User).join(User.roles).filter(
            Role.name.in_(["technical_staff", "non_technical_staff"])
        ).count()
        
        passenger_users = total_users - admin_users - staff_users
        
        # Booking statistics - FIXED: using booking_date instead of booking_time
        total_bookings = session.query(Booking).count()
        today_bookings = session.query(Booking).filter(
            func.date(Booking.booking_date) == datetime.now().date()
        ).count()
        this_week_bookings = session.query(Booking).filter(
            Booking.booking_date >= datetime.now() - timedelta(days=7)
        ).count()
        
        # Revenue statistics - FIXED: using cost_charged instead of total_price
        total_revenue = session.query(func.sum(Booking.cost_charged)).scalar() or 0
        avg_booking_value = session.query(func.avg(Booking.cost_charged)).scalar() or 0
        
        # Flight statistics
        total_flights = session.query(Flight).count()
        total_schedules = session.query(FlightSchedule).count()
        active_aircraft = session.query(Aircraft).count()
        
    except Exception as e:
        print(f"Error getting admin stats: {e}")
        total_users = admin_users = staff_users = passenger_users = 0
        total_bookings = today_bookings = this_week_bookings = 0
        total_revenue = avg_booking_value = 0
        total_flights = total_schedules = active_aircraft = 0
    finally:
        session.close()
    
    return html.Div([
        # Page header
        create_page_header(
            "Admin Panel", 
            "System overview and management",
            user_info
        ),
        
        # Quick statistics cards
        dbc.Row([
            dbc.Col([
                create_stats_card(
                    "Total Users", 
                    total_users,
                    f"{passenger_users} passengers, {staff_users} staff, {admin_users} admins",
                    "primary",
                    "fas fa-users"
                )
            ], md=3),
            dbc.Col([
                create_stats_card(
                    "Total Bookings", 
                    total_bookings,
                    f"{today_bookings} today, {this_week_bookings} this week",
                    "success",
                    "fas fa-ticket-alt"
                )
            ], md=3),
            dbc.Col([
                create_stats_card(
                    "Total Revenue", 
                    f"£{total_revenue:,.2f}",
                    f"Avg: £{avg_booking_value:.2f} per booking",
                    "warning",
                    "fas fa-pound-sign"
                )
            ], md=3),
            dbc.Col([
                create_stats_card(
                    "Fleet & Routes", 
                    f"{active_aircraft} aircraft",
                    f"{total_flights} routes, {total_schedules} schedules",
                    "info",
                    "fas fa-plane"
                )
            ], md=3),
        ], className="mb-4"),
        
        # Management sections
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("👥 User Management", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Manage user accounts and permissions", className="card-text"),
                        dbc.ButtonGroup([
                            dbc.Button("View All Users", color="primary", id="btn-view-users"),
                            dbc.Button("User Reports", color="outline-primary", id="btn-user-reports"),
                        ])
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📊 Booking Management", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("View and manage flight bookings", className="card-text"),
                        dbc.ButtonGroup([
                            dbc.Button("View All Bookings", color="success", id="btn-view-bookings"),
                            dbc.Button("Booking Reports", color="outline-success", id="btn-booking-reports"),
                        ])
                    ])
                ])
            ], md=6),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("✈️ Flight Operations", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Monitor flight schedules and operations", className="card-text"),
                        dbc.ButtonGroup([
                            dbc.Button("Flight Status", color="info", id="btn-flight-status"),
                            dbc.Button("Schedule Reports", color="outline-info", id="btn-schedule-reports"),
                        ])
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("🔧 System Settings", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Configure system settings and preferences", className="card-text"),
                        dbc.ButtonGroup([
                            dbc.Button("System Config", color="warning", id="btn-system-config"),
                            dbc.Button("Audit Logs", color="outline-warning", id="btn-audit-logs"),
                        ])
                    ])
                ])
            ], md=6),
        ], className="mb-4"),
        
        # Content area for dynamic loading
        html.Div(id="admin-content", className="mt-4"),
        
        # Store for current view
        dcc.Store(id="admin-current-view")
    ])

# Callbacks for the different admin views
@callback(
    [Output("admin-content", "children"),
     Output("admin-current-view", "data")],
    [Input("btn-view-users", "n_clicks"),
     Input("btn-user-reports", "n_clicks"),
     Input("btn-view-bookings", "n_clicks"),
     Input("btn-booking-reports", "n_clicks"),
     Input("btn-flight-status", "n_clicks"),
     Input("btn-schedule-reports", "n_clicks"),
     Input("btn-system-config", "n_clicks"),
     Input("btn-audit-logs", "n_clicks")],
    prevent_initial_call=True
)
def handle_admin_navigation(users_btn, user_reports_btn, bookings_btn, booking_reports_btn,
                          flight_btn, schedule_btn, config_btn, audit_btn):
    ctx = dash.callback_context
    if not ctx.triggered:
        return html.Div(), None
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "btn-view-users":
        return load_users_view(), "users"
    elif button_id == "btn-user-reports":
        return load_user_reports_view(), "user_reports"
    elif button_id == "btn-view-bookings":
        return load_bookings_view(), "bookings"
    elif button_id == "btn-booking-reports":
        return load_booking_reports_view(), "booking_reports"
    elif button_id == "btn-flight-status":
        return load_flight_status_view(), "flight_status"
    elif button_id == "btn-schedule-reports":
        return load_schedule_reports_view(), "schedule_reports"
    elif button_id == "btn-system-config":
        return load_system_config_view(), "system_config"
    elif button_id == "btn-audit-logs":
        return load_audit_logs_view(), "audit_logs"
    
    return html.Div(), None

def load_users_view():
    """Load the users management view"""
    session = get_session()
    try:
        # Get all users with their roles using SQL join to avoid DetachedInstanceError
        users_with_roles = session.query(User, Role.name).outerjoin(User.roles).all()
        
        # Group roles by user
        user_roles_dict = {}
        for user, role_name in users_with_roles:
            if user.id not in user_roles_dict:
                user_roles_dict[user.id] = {
                    "user": user,
                    "roles": []
                }
            if role_name:
                user_roles_dict[user.id]["roles"].append(role_name)
        
        user_data = []
        for user_id, data in user_roles_dict.items():
            user = data["user"]
            roles = data["roles"]
            user_data.append({
                "ID": user.id,
                "Name": f"{user.first_name} {user.last_name}",
                "Email": user.email,
                "Roles": ", ".join(roles) if roles else "No roles",
                "Created": user.created_at.strftime("%Y-%m-%d") if user.created_at else "N/A"
            })
        
        df = pd.DataFrame(user_data)
        
    except Exception as e:
        print(f"Error loading users: {e}")
        df = pd.DataFrame()
    finally:
        session.close()
    
    if df.empty:
        return html.Div([
            dbc.Alert("No users found or error loading data.", color="warning")
        ])
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("👥 All Users", className="mb-0")
            ]),
            dbc.CardBody([
                dash_table.DataTable(
                    id="users-table",
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
                            "if": {"filter_query": "{Roles} contains admin"},
                            "backgroundColor": "#ffebee",
                            "color": "black",
                        }
                    ]
                )
            ])
        ])
    ])

def load_user_reports_view():
    """Load user reports and analytics"""
    session = get_session()
    try:
        # User registration trends (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_registrations = session.query(User).filter(
            User.created_at >= thirty_days_ago
        ).count()
        
        # Role distribution
        role_stats = session.query(Role.name, func.count(User.id)).join(User.roles).group_by(Role.name).all()
        
        # Active users (those with bookings in last 30 days)
        active_users = session.query(User).join(Booking).filter(
            Booking.booking_date >= thirty_days_ago
        ).distinct().count()
        
    except Exception as e:
        print(f"Error loading user reports: {e}")
        recent_registrations = 0
        role_stats = []
        active_users = 0
    finally:
        session.close()
    
    # Create role distribution chart data
    role_chart_data = []
    for role_name, count in role_stats:
        role_chart_data.append({
            "Role": role_name.replace("_", " ").title(),
            "Count": count
        })
    
    role_df = pd.DataFrame(role_chart_data)
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("📈 User Analytics & Reports", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        create_stats_card(
                            "New Users (30 days)",
                            recent_registrations,
                            "Recent registrations",
                            "success",
                            "fas fa-user-plus"
                        )
                    ], md=4),
                    dbc.Col([
                        create_stats_card(
                            "Active Users (30 days)",
                            active_users,
                            "Users with recent bookings",
                            "info",
                            "fas fa-user-check"
                        )
                    ], md=4),
                    dbc.Col([
                        create_stats_card(
                            "User Engagement",
                            f"{(active_users / max(recent_registrations, 1) * 100):.1f}%",
                            "Active/New user ratio",
                            "warning",
                            "fas fa-chart-line"
                        )
                    ], md=4),
                ], className="mb-4"),
                
                # Role distribution table
                html.H6("Role Distribution", className="mb-3"),
                dash_table.DataTable(
                    data=role_df.to_dict("records") if not role_df.empty else [],
                    columns=[{"name": col, "id": col} for col in role_df.columns] if not role_df.empty else [],
                    style_cell={"textAlign": "left"},
                    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"}
                ) if not role_df.empty else dbc.Alert("No role data available", color="info")
            ])
        ])
    ])

def load_bookings_view():
    """Load bookings management view"""
    session = get_session()
    try:
        # Get recent bookings with flight details - FIXED: eager load passenger relationship
        bookings = session.query(Booking).join(FlightSchedule).join(Flight).join(User, Booking.passenger_id == User.id).all()
        
        booking_data = []
        for booking in bookings:
            booking_data.append({
                "Booking ID": booking.confirmation_code,
                "Passenger": f"{booking.passenger.first_name} {booking.passenger.last_name}",
                "Flight": f"{booking.flight_schedule.flight.flight_number}",
                "Route": f"{booking.flight_schedule.flight.origin} → {booking.flight_schedule.flight.destination}",
                "Date": booking.flight_schedule.scheduled_departure_time.strftime("%Y-%m-%d"),
                "Price": f"£{booking.cost_charged:.2f}",
                "Status": "Confirmed",
                "Booked": booking.booking_date.strftime("%Y-%m-%d %H:%M")
            })
        
        df = pd.DataFrame(booking_data)
        
    except Exception as e:
        print(f"Error loading bookings: {e}")
        df = pd.DataFrame()
    finally:
        session.close()
    
    if df.empty:
        return html.Div([
            dbc.Alert("No bookings found or error loading data.", color="warning")
        ])
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("🎫 All Bookings", className="mb-0")
            ]),
            dbc.CardBody([
                dash_table.DataTable(
                    id="bookings-table",
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

def load_booking_reports_view():
    """Load booking reports and analytics"""
    session = get_session()
    try:
        # Revenue by time period
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        today_revenue = session.query(func.sum(Booking.cost_charged)).filter(
            func.date(Booking.booking_date) == today
        ).scalar() or 0
        
        yesterday_revenue = session.query(func.sum(Booking.cost_charged)).filter(
            func.date(Booking.booking_date) == yesterday
        ).scalar() or 0
        
        week_revenue = session.query(func.sum(Booking.cost_charged)).filter(
            Booking.booking_date >= week_ago
        ).scalar() or 0
        
        month_revenue = session.query(func.sum(Booking.cost_charged)).filter(
            Booking.booking_date >= month_ago
        ).scalar() or 0
        
        # COMPLEX QUERY 1: Revenue trends by day with rolling averages
        # This uses window functions, date operations, and subqueries
        revenue_trends = session.execute(text("""
            SELECT 
                DATE(booking_date) as booking_date,
                COUNT(*) as daily_bookings,
                SUM(cost_charged) as daily_revenue,
                AVG(cost_charged) as avg_booking_value,
                AVG(SUM(cost_charged)) OVER (
                    ORDER BY DATE(booking_date) 
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                ) as seven_day_avg_revenue
            FROM bookings 
            WHERE booking_date >= DATE('now', '-30 days')
            GROUP BY DATE(booking_date)
            ORDER BY booking_date DESC
            LIMIT 30
        """)).fetchall()
        
        # Popular routes
        popular_routes = session.query(
            Flight.origin,
            Flight.destination,
            func.count(Booking.id).label('booking_count'),
            func.sum(Booking.cost_charged).label('total_revenue')
        ).join(FlightSchedule).join(Booking).group_by(
            Flight.origin, Flight.destination
        ).order_by(func.count(Booking.id).desc()).limit(10).all()
        
        # Average booking value by period
        avg_booking_today = session.query(func.avg(Booking.cost_charged)).filter(
            func.date(Booking.booking_date) == today
        ).scalar() or 0
        
    except Exception as e:
        print(f"Error loading booking reports: {e}")
        today_revenue = yesterday_revenue = week_revenue = month_revenue = 0
        popular_routes = []
        avg_booking_today = 0
        revenue_trends = []
    finally:
        session.close()
    
    # Create popular routes data
    routes_data = []
    for route in popular_routes:
        routes_data.append({
            "Route": f"{route.origin} → {route.destination}",
            "Bookings": route.booking_count,
            "Revenue": f"£{route.total_revenue:,.2f}",
            "Avg Value": f"£{route.total_revenue / route.booking_count:.2f}"
        })
    
    routes_df = pd.DataFrame(routes_data)
    
    # Create revenue trends data
    trends_data = []
    for trend in revenue_trends:
        trends_data.append({
            "Date": trend.booking_date,
            "Daily Bookings": trend.daily_bookings,
            "Daily Revenue": f"£{trend.daily_revenue:,.2f}",
            "Avg Booking": f"£{trend.avg_booking_value:.2f}",
            "7-Day Avg Revenue": f"£{trend.seven_day_avg_revenue:,.2f}"
        })
    
    trends_df = pd.DataFrame(trends_data)
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("📊 Booking Analytics & Revenue Reports", className="mb-0")
            ]),
            dbc.CardBody([
                # Revenue statistics
                dbc.Row([
                    dbc.Col([
                        create_stats_card(
                            "Today's Revenue",
                            f"£{today_revenue:,.2f}",
                            f"Avg: £{avg_booking_today:.2f} per booking",
                            "success",
                            "fas fa-calendar-day"
                        )
                    ], md=3),
                    dbc.Col([
                        create_stats_card(
                            "Yesterday",
                            f"£{yesterday_revenue:,.2f}",
                            f"Change: {((today_revenue - yesterday_revenue) / max(yesterday_revenue, 1) * 100):+.1f}%",
                            "info",
                            "fas fa-calendar-minus"
                        )
                    ], md=3),
                    dbc.Col([
                        create_stats_card(
                            "Last 7 Days",
                            f"£{week_revenue:,.2f}",
                            f"Daily avg: £{week_revenue / 7:.2f}",
                            "warning",
                            "fas fa-calendar-week"
                        )
                    ], md=3),
                    dbc.Col([
                        create_stats_card(
                            "Last 30 Days",
                            f"£{month_revenue:,.2f}",
                            f"Monthly projection",
                            "primary",
                            "fas fa-calendar-alt"
                        )
                    ], md=3),
                ], className="mb-4"),
                
                # Revenue trends table
                html.H6("📈 Daily Revenue Trends (Last 30 Days)", className="mb-3"),
                dash_table.DataTable(
                    data=trends_df.to_dict("records") if not trends_df.empty else [],
                    columns=[{"name": col, "id": col} for col in trends_df.columns] if not trends_df.empty else [],
                    style_cell={"textAlign": "left"},
                    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
                    page_size=10,
                    style_data_conditional=[
                        {
                            "if": {"row_index": 0},
                            "backgroundColor": "#e8f5e8",
                            "color": "black",
                        }
                    ]
                ) if not trends_df.empty else dbc.Alert("No revenue trends data available", color="info"),
                
                html.Hr(),
                
                # Popular routes
                html.H6("🏆 Top 10 Popular Routes", className="mb-3"),
                dash_table.DataTable(
                    data=routes_df.to_dict("records") if not routes_df.empty else [],
                    columns=[{"name": col, "id": col} for col in routes_df.columns] if not routes_df.empty else [],
                    style_cell={"textAlign": "left"},
                    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
                    style_data_conditional=[
                        {
                            "if": {"row_index": 0},
                            "backgroundColor": "#e8f5e8",
                            "color": "black",
                        },
                        {
                            "if": {"row_index": 1},
                            "backgroundColor": "#f0f8f0",
                            "color": "black",
                        }
                    ]
                ) if not routes_df.empty else dbc.Alert("No booking data available", color="info")
            ])
        ])
    ])

def load_flight_status_view():
    """Load flight status overview"""
    session = get_session()
    try:
        # Get flight schedules for today and tomorrow
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        today_flights = session.query(FlightSchedule).filter(
            func.date(FlightSchedule.scheduled_departure_time) == today
        ).join(Flight).all()
        
        tomorrow_flights = session.query(FlightSchedule).filter(
            func.date(FlightSchedule.scheduled_departure_time) == tomorrow
        ).join(Flight).all()
        
        # Flight status summary
        total_today = len(today_flights)
        total_tomorrow = len(tomorrow_flights)
        
        # Create flight data
        flight_data = []
        for schedule in today_flights[:20]:  # Limit to 20 for display
            flight_data.append({
                "Flight": schedule.flight.flight_number,
                "Route": f"{schedule.flight.origin} → {schedule.flight.destination}",
                "Departure": schedule.scheduled_departure_time.strftime("%H:%M"),
                "Arrival": schedule.scheduled_arrival_time.strftime("%H:%M"),
                "Aircraft": schedule.flight.aircraft.registration_number,
                "Status": schedule.status.value if schedule.status else "Scheduled"
            })
        
    except Exception as e:
        print(f"Error loading flight status: {e}")
        flight_data = []
        total_today = total_tomorrow = 0
    finally:
        session.close()
    
    flights_df = pd.DataFrame(flight_data)
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("✈️ Flight Operations Monitor", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        create_stats_card(
                            "Today's Flights",
                            total_today,
                            "Scheduled departures",
                            "primary",
                            "fas fa-plane-departure"
                        )
                    ], md=6),
                    dbc.Col([
                        create_stats_card(
                            "Tomorrow's Flights",
                            total_tomorrow,
                            "Scheduled departures",
                            "info",
                            "fas fa-calendar-plus"
                        )
                    ], md=6),
                ], className="mb-4"),
                
                html.H6("Today's Flight Schedule", className="mb-3"),
                dash_table.DataTable(
                    data=flights_df.to_dict("records") if not flights_df.empty else [],
                    columns=[{"name": col, "id": col} for col in flights_df.columns] if not flights_df.empty else [],
                    style_cell={"textAlign": "left"},
                    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
                    page_size=15
                ) if not flights_df.empty else dbc.Alert("No flights scheduled for today", color="info")
            ])
        ])
    ])

def load_schedule_reports_view():
    """Load schedule reports"""
    session = get_session()
    try:
        # Aircraft utilisation
        aircraft_usage = session.query(
            Aircraft.registration_number,
            Aircraft.model_number,
            func.count(FlightSchedule.id).label('flight_count')
        ).join(Flight).join(FlightSchedule).group_by(
            Aircraft.id
        ).order_by(func.count(FlightSchedule.id).desc()).all()
        
        # Route frequency
        route_frequency = session.query(
            Flight.origin,
            Flight.destination,
            func.count(FlightSchedule.id).label('schedule_count')
        ).join(FlightSchedule).group_by(
            Flight.origin, Flight.destination
        ).order_by(func.count(FlightSchedule.id).desc()).limit(10).all()
        
    except Exception as e:
        print(f"Error loading schedule reports: {e}")
        aircraft_usage = []
        route_frequency = []
    finally:
        session.close()
    
    # Create aircraft usage data
    aircraft_data = []
    for usage in aircraft_usage:
        aircraft_data.append({
            "Aircraft": usage.registration_number,
            "Model": usage.model_number,
            "Scheduled Flights": usage.flight_count,
            "Utilisation": f"{usage.flight_count * 100 / max(len(aircraft_usage) * 10, 1):.1f}%"
        })
    
    aircraft_df = pd.DataFrame(aircraft_data)
    
    # Create route frequency data
    route_data = []
    for route in route_frequency:
        route_data.append({
            "Route": f"{route.origin} → {route.destination}",
            "Scheduled Flights": route.schedule_count
        })
    
    routes_df = pd.DataFrame(route_data)
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("📅 Schedule Analytics & Aircraft Utilisation", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6("Aircraft Utilisation", className="mb-3"),
                        dash_table.DataTable(
                            data=aircraft_df.to_dict("records") if not aircraft_df.empty else [],
                            columns=[{"name": col, "id": col} for col in aircraft_df.columns] if not aircraft_df.empty else [],
                            style_cell={"textAlign": "left"},
                            style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
                            page_size=10
                        ) if not aircraft_df.empty else dbc.Alert("No aircraft usage data", color="info")
                    ], md=6),
                    dbc.Col([
                        html.H6("Route Frequency", className="mb-3"),
                        dash_table.DataTable(
                            data=routes_df.to_dict("records") if not routes_df.empty else [],
                            columns=[{"name": col, "id": col} for col in routes_df.columns] if not routes_df.empty else [],
                            style_cell={"textAlign": "left"},
                            style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
                            page_size=10
                        ) if not routes_df.empty else dbc.Alert("No route frequency data", color="info")
                    ], md=6),
                ])
            ])
        ])
    ])

def load_system_config_view():
    """Load system configuration"""
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("⚙️ System Configuration", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Booking Settings", className="mb-3"),
                                dbc.Form([
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label("Maximum booking days in advance"),
                                            dbc.Input(type="number", value=90, disabled=True)
                                        ], md=6),
                                        dbc.Col([
                                            dbc.Label("Minimum booking hours before departure"),
                                            dbc.Input(type="number", value=2, disabled=True)
                                        ], md=6)
                                    ], className="mb-3"),
                                    dbc.Alert("Configuration editing will be implemented in future updates", color="info")
                                ])
                            ])
                        ])
                    ], md=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("System Information", className="mb-3"),
                                html.P([html.Strong("Database: "), "SQLite"]),
                                html.P([html.Strong("Environment: "), "Development"]),
                                html.P([html.Strong("Version: "), "1.0.0"]),
                                html.P([html.Strong("Last Updated: "), datetime.now().strftime("%Y-%m-%d %H:%M")])
                            ])
                        ])
                    ], md=6)
                ])
            ])
        ])
    ])

def load_audit_logs_view():
    """Load audit logs"""
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("📋 System Audit Logs", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Alert([
                    html.H6("Audit Logging System", className="mb-3"),
                    html.P("A comprehensive audit logging system will track:"),
                    html.Ul([
                        html.Li("User login/logout events"),
                        html.Li("Flight booking and cancellation activities"),
                        html.Li("Administrative actions and configuration changes"),
                        html.Li("Data modification attempts"),
                        html.Li("Security-related events"),
                    ]),
                    html.P("This feature will be implemented to provide complete system traceability.", className="mb-0")
                ], color="info")
            ])
        ])
    ]) 