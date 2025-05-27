import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from werkzeug.security import check_password_hash
from src.utils.database import get_session
from src.models.user import User
import flask

dash.register_page(__name__, path='/login')

layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H2("Login", className="mb-4 text-center"),
            dbc.Card([
                dbc.CardBody([
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Email"),
                                dbc.Input(
                                    type="email",
                                    id="login-email",
                                    placeholder="Enter your email",
                                    required=True
                                ),
                                dbc.FormFeedback(
                                    "Please enter a valid email address",
                                    type="invalid"
                                )
                            ])
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Password"),
                                dbc.Input(
                                    type="password",
                                    id="login-password",
                                    placeholder="Enter your password",
                                    required=True
                                ),
                                dbc.FormFeedback(
                                    "Please enter your password",
                                    type="invalid"
                                )
                            ])
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Login",
                                    id="login-button",
                                    color="primary",
                                    className="w-100"
                                ),
                                html.Div(id="login-output", className="mt-3")
                            ])
                        ]),
                        
                        html.Hr(),
                        
                        dbc.Row([
                            dbc.Col([
                                html.P([
                                    "Don't have an account? ",
                                    html.A("Register here", href="/register")
                                ], className="text-center")
                            ])
                        ])
                    ])
                ])
            ])
        ], width=6, className="mx-auto")
    ])
])

@callback(
    Output("login-output", "children"),
    Input("login-button", "n_clicks"),
    State("login-email", "value"),
    State("login-password", "value"),
    prevent_initial_call=True
)
def process_login(n_clicks, email, password):
    if not email or not password:
        return dbc.Alert("Please fill in all fields", color="danger")
    
    session = get_session()
    user = session.query(User).filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        # Store user info in session
        flask.session["user_id"] = user.id
        flask.session["user_email"] = user.email
        flask.session["user_name"] = user.full_name
        
        # Create success message with redirect
        return html.Div([
            dbc.Alert("Login successful! Redirecting...", color="success"),
            dcc.Location(pathname="/", id="login-redirect")
        ])
    else:
        return dbc.Alert("Invalid email or password", color="danger") 