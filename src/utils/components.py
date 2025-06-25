import dash_bootstrap_components as dbc
from dash import html, dcc
from src.utils.auth import require_login, has_role, get_user_display_info

def create_access_denied_page(required_role=None, message=None):
    """Create a standard access denied page"""
    
    if message is None:
        if required_role:
            message = f"You need {required_role} permissions to access this page."
        else:
            message = "You don't have permission to access this page."
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("🚫", className="display-1 text-center text-danger"),
                    html.H2("Access Denied", className="text-center mb-4"),
                    html.P(message, className="lead text-center mb-4"),
                    html.Div([
                        dbc.Button("🏠 Go Home", color="primary", href="/", className="me-2"),
                        dbc.Button("👤 Login", color="outline-primary", href="/login") if not require_login() else None
                    ], className="text-center")
                ], className="py-5")
            ], width=8, className="mx-auto")
        ], className="min-vh-100 d-flex align-items-center")
    ])

def create_login_required_page():
    """Create a standard login required page"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.H4("Login Required", className="alert-heading"),
                    html.P("You need to be logged in to access this page."),
                    html.Hr(),
                    dbc.ButtonGroup([
                        dbc.Button("Login", color="primary", href="/login"),
                        dbc.Button("Register", color="outline-primary", href="/register")
                    ])
                ], color="warning")
            ], width=6, className="mx-auto mt-5")
        ])
    ])

def protected_page(required_role=None):
    """
    Decorator for pages that require specific roles
    Usage: @protected_page('admin') or @protected_page()
    """
    def decorator(layout_func):
        def wrapper(*args, **kwargs):
            # Check if user is logged in
            if not require_login():
                return create_login_required_page()
            
            # Check role if specified
            if required_role and not has_role(required_role):
                return create_access_denied_page(required_role)
            
            # User has access, return the actual page
            return layout_func(*args, **kwargs)
        
        return wrapper
    return decorator

def create_page_header(title, subtitle=None, user_info=None):
    """Create a standard page header with title and user context"""
    if user_info is None:
        user_info = get_user_display_info()
    
    header_content = [
        html.H1(title, className="mb-2"),
    ]
    
    if subtitle:
        header_content.append(html.P(subtitle, className="lead text-muted"))
    
    if user_info.get("roles"):
        role_badges = []
        for role in user_info["roles"]:
            color = {
                "admin": "danger",
                "technical_staff": "warning", 
                "non_technical_staff": "info",
                "passenger": "secondary"
            }.get(role, "secondary")
            
            role_badges.append(
                html.Span(role.replace("_", " ").title(), 
                         className=f"badge bg-{color} me-2")
            )
        
        header_content.append(
            html.Div(role_badges, className="mb-3")
        )
    
    return dbc.Card([
        dbc.CardBody(header_content)
    ], className="mb-4")

def create_stats_card(title, value, subtitle=None, color="primary", icon=None):
    """Create a statistics card component"""
    card_content = []
    
    if icon:
        card_content.append(
            html.I(className=f"{icon} fa-2x text-{color} mb-2")
        )
    
    card_content.extend([
        html.H3(str(value), className=f"text-{color}"),
        html.H6(title, className="card-title"),
    ])
    
    if subtitle:
        card_content.append(
            html.P(subtitle, className="card-text text-muted")
        )
    
    return dbc.Card([
        dbc.CardBody(card_content, className="text-center")
    ]) 