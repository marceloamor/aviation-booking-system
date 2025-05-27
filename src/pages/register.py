import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from werkzeug.security import generate_password_hash
from src.utils.database import get_session
from src.models.user import User
from src.models.role import Role
import flask
import re

dash.register_page(__name__, path='/register')

layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H2("Register", className="mb-4 text-center"),
            dbc.Card([
                dbc.CardBody([
                    dbc.Form([
                        # Personal Information
                        html.H5("Personal Information", className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("First Name"),
                                dbc.Input(
                                    type="text",
                                    id="register-first-name",
                                    placeholder="Enter your first name",
                                    required=True
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Last Name"),
                                dbc.Input(
                                    type="text",
                                    id="register-last-name",
                                    placeholder="Enter your last name",
                                    required=True
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Email"),
                                dbc.Input(
                                    type="email",
                                    id="register-email",
                                    placeholder="Enter your email address",
                                    required=True
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Phone Number"),
                                dbc.Input(
                                    type="tel",
                                    id="register-phone",
                                    placeholder="Enter your phone number",
                                    required=True
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Password"),
                                dbc.Input(
                                    type="password",
                                    id="register-password",
                                    placeholder="Enter password",
                                    required=True
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Confirm Password"),
                                dbc.Input(
                                    type="password",
                                    id="register-confirm-password",
                                    placeholder="Confirm your password",
                                    required=True
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        # Address Information
                        html.H5("Address Information", className="mb-3 mt-4"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Street Address"),
                                dbc.Input(
                                    type="text",
                                    id="register-street",
                                    placeholder="Enter your street address",
                                    required=True
                                )
                            ])
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("City"),
                                dbc.Input(
                                    type="text",
                                    id="register-city",
                                    placeholder="Enter your city",
                                    required=True
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Postal Code"),
                                dbc.Input(
                                    type="text",
                                    id="register-postal-code",
                                    placeholder="Enter your postal code",
                                    required=True
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Country"),
                                dbc.Input(
                                    type="text",
                                    id="register-country",
                                    placeholder="Enter your country",
                                    value="United Kingdom",
                                    required=True
                                )
                            ])
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Register",
                                    id="register-button",
                                    color="primary",
                                    className="w-100"
                                ),
                                html.Div(id="register-output", className="mt-3")
                            ])
                        ]),
                        
                        html.Hr(),
                        
                        dbc.Row([
                            dbc.Col([
                                html.P([
                                    "Already have an account? ",
                                    html.A("Login here", href="/login")
                                ], className="text-center")
                            ])
                        ])
                    ])
                ])
            ])
        ], width=8, className="mx-auto")
    ])
])

@callback(
    Output("register-output", "children"),
    Input("register-button", "n_clicks"),
    State("register-first-name", "value"),
    State("register-last-name", "value"),
    State("register-email", "value"),
    State("register-phone", "value"),
    State("register-password", "value"),
    State("register-confirm-password", "value"),
    State("register-street", "value"),
    State("register-city", "value"),
    State("register-postal-code", "value"),
    State("register-country", "value"),
    prevent_initial_call=True
)
def process_registration(n_clicks, first_name, last_name, email, phone, password, 
                         confirm_password, street, city, postal_code, country):
    # Validate required fields
    if not all([first_name, last_name, email, phone, password, confirm_password, 
               street, city, postal_code, country]):
        return dbc.Alert("Please fill in all required fields", color="danger")
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return dbc.Alert("Please enter a valid email address", color="danger")
    
    # Validate password match
    if password != confirm_password:
        return dbc.Alert("Passwords do not match", color="danger")
    
    # Check if email already exists
    session = get_session()
    existing_user = session.query(User).filter_by(email=email).first()
    if existing_user:
        return dbc.Alert("This email is already registered", color="danger")
    
    try:
        # Get passenger role
        passenger_role = session.query(Role).filter_by(name="passenger").first()
        if not passenger_role:
            return dbc.Alert("System error: Role not found", color="danger")
        
        # Create new user
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone,
            password_hash=generate_password_hash(password),
            street=street,
            city=city,
            postal_code=postal_code,
            country=country,
            roles=[passenger_role]
        )
        
        session.add(new_user)
        session.commit()
        
        # Log the user in
        flask.session["user_id"] = new_user.id
        flask.session["user_email"] = new_user.email
        flask.session["user_name"] = new_user.full_name
        
        # Show success and redirect
        return html.Div([
            dbc.Alert("Registration successful! Redirecting to home page...", color="success"),
            dcc.Location(pathname="/", id="register-redirect")
        ])
        
    except Exception as e:
        # Handle any errors
        session.rollback()
        return dbc.Alert(f"An error occurred: {str(e)}", color="danger")
    
    finally:
        session.close() 