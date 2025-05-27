import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask import Flask
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
    # Header
    html.Div([
        html.H1("✈️ Northeastern Airways", className="display-4"),
        html.P("Flight Booking System", className="lead"),
    ], className="container py-3 bg-light rounded"),
    
    # Navigation
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Flights", href="/flights")),
            dbc.NavItem(dbc.NavLink("Bookings", href="/bookings")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Login", href="/login"),
                    dbc.DropdownMenuItem("Register", href="/register"),
                ],
                nav=True,
                in_navbar=True,
                label="User",
            ),
        ],
        brand="✈️ Northeastern Airways",
        brand_href="/",
        color="primary",
        dark=True,
        className="mb-4",
    ),
    
    # Content
    html.Div([
        dash.page_container
    ], className="container"),
    
    # Footer
    html.Footer([
        html.P("© 2023 Northeastern Airways. All rights reserved."),
    ], className="container py-3 mt-4 bg-light text-center")
])

if __name__ == '__main__':
    app.run_server(debug=True) 