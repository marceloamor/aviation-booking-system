import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from flask import Flask
import flask
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Flask server
server = Flask(__name__)
server.secret_key = os.getenv("SECRET_KEY", "default-dev-key-replace-in-production")

# Initialize the Dash app with the Flask server
app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    pages_folder="src/pages",  # Specify the correct pages folder path
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Define the app layout
app.layout = html.Div([
    # Header with user info
    html.Div(id="app-header"),
    
    # Navigation
    html.Div(id="app-navigation"),
    
    # Content
    html.Div([
        dash.page_container
    ], className="container"),
    
    # Footer
    html.Footer([
        html.P("© 2023 Northeastern Airways. All rights reserved."),
    ], className="container py-3 mt-4 bg-light text-center"),
    
    # Store for logout trigger
    dcc.Store(id="logout-trigger", data=False),
    
    # Store for login status
    dcc.Store(id="login-status", data=False)
])

@callback(
    Output("app-header", "children"),
    [Input("logout-trigger", "data"),
     Input("login-status", "data")]
)
def update_header(logout_trigger, login_status):
    # Get user info from session
    user_name = flask.session.get("user_name")
    user_email = flask.session.get("user_email")
    
    if user_name:
        return html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H1("✈️ Northeastern Airways", className="display-4"),
                        html.P("Flight Booking System", className="lead"),
                    ], width=6),
                    dbc.Col([
                        html.Div([
                            html.P([
                                html.I(className="fas fa-user me-2"),
                                f"Welcome back, {user_name.split()[0]}!"
                            ], className="mb-1 text-end"),
                            html.P([
                                html.Small(user_email, className="text-muted")
                            ], className="mb-0 text-end")
                        ], className="d-flex flex-column justify-content-center h-100")
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            dbc.Button(
                                [html.I(className="fas fa-sign-out-alt me-1"), "Logout"],
                                id="header-logout-btn",
                                color="outline-secondary",
                                size="sm",
                                className="mt-2"
                            )
                        ], className="d-flex justify-content-end h-100 align-items-center")
                    ], width=2)
                ])
            ], fluid=False, className="py-3 bg-light rounded")
        ])
    else:
        return html.Div([
            html.H1("✈️ Northeastern Airways", className="display-4"),
            html.P("Flight Booking System", className="lead"),
        ], className="container py-3 bg-light rounded")

@callback(
    Output("app-navigation", "children"),
    [Input("logout-trigger", "data"),
     Input("login-status", "data")]
)
def update_navigation(logout_trigger, login_status):
    # Get user info from session
    user_id = flask.session.get("user_id")
    user_name = flask.session.get("user_name")
    
    if user_id:
        # User is logged in - show full navigation
        return dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.NavItem(dbc.NavLink("Flights", href="/flights")),
                dbc.NavItem(dbc.NavLink("My Bookings", href="/bookings")),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("Profile", href="/profile"),
                        dbc.DropdownMenuItem("Settings", href="/settings"),
                        dbc.DropdownMenuItem(divider=True),
                        dbc.DropdownMenuItem("Logout", id="nav-logout-btn"),
                    ],
                    nav=True,
                    in_navbar=True,
                    label=f"👤 {user_name.split()[0] if user_name else 'User'}",
                ),
            ],
            brand="✈️ Northeastern Airways",
            brand_href="/",
            color="primary",
            dark=True,
            className="mb-4",
        )
    else:
        # User is not logged in - show basic navigation
        return dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.NavItem(dbc.NavLink("Flights", href="/flights")),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("Login", href="/login"),
                        dbc.DropdownMenuItem("Register", href="/register"),
                    ],
                    nav=True,
                    in_navbar=True,
                    label="Sign In",
                ),
            ],
            brand="✈️ Northeastern Airways",
            brand_href="/",
            color="primary",
            dark=True,
            className="mb-4",
        )

@callback(
    [Output("logout-trigger", "data"),
     Output("app-navigation", "children", allow_duplicate=True),
     Output("app-header", "children", allow_duplicate=True)],
    Input("nav-logout-btn", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout(nav_clicks):
    if nav_clicks:
        # Clear the session
        flask.session.clear()
        
        # Return updated navigation and header for logged-out state
        logged_out_nav = dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.NavItem(dbc.NavLink("Flights", href="/flights")),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("Login", href="/login"),
                        dbc.DropdownMenuItem("Register", href="/register"),
                    ],
                    nav=True,
                    in_navbar=True,
                    label="Sign In",
                ),
            ],
            brand="✈️ Northeastern Airways",
            brand_href="/",
            color="primary",
            dark=True,
            className="mb-4",
        )
        
        logged_out_header = html.Div([
            html.H1("✈️ Northeastern Airways", className="display-4"),
            html.P("Flight Booking System", className="lead"),
        ], className="container py-3 bg-light rounded")
        
        return True, logged_out_nav, logged_out_header
    return False, html.Div(), html.Div()

if __name__ == '__main__':
    app.run_server(debug=True) 