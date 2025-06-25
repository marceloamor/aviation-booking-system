import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path_template="/404")

layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("404", className="display-1 text-center text-primary"),
                html.H2("Page not implemented by the devs haha whoooops (outside the scope of this project)", className="text-center mb-4"),
                html.P(
                    "404 - Page not implemented by the devs haha whoooops (outside the scope of this project)",
                    className="lead text-center mb-4"
                ),
                html.Div([
                    html.I(className="fas fa-plane fa-3x text-muted mb-3"),
                ], className="text-center mb-4"),
                html.P(
                    "Looks like this page took off without us! Let's get you back on track.",
                    className="text-center text-muted"
                ),
                html.Div([
                    dbc.Button("🏠 Go Home", color="primary", href="/", className="me-2"),
                    dbc.Button("✈️ Search Flights", color="outline-primary", href="/flights")
                ], className="text-center")
            ], className="py-5")
        ], width=8, className="mx-auto")
    ], className="min-vh-100 d-flex align-items-center")
]) 