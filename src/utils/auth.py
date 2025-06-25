import flask
from src.utils.database import get_session
from src.models.user import User
from functools import wraps
from sqlalchemy.orm import joinedload

def get_current_user():
    """Get the current logged-in user from session"""
    user_id = flask.session.get("user_id")
    if not user_id:
        return None
    
    session = get_session()
    try:
        # Eagerly load the roles to avoid DetachedInstanceError
        user = session.query(User).options(joinedload(User.roles)).filter_by(id=user_id).first()
        if user:
            # Access roles while session is still open to load them
            _ = user.roles  # This forces the relationship to load
        return user
    except Exception:
        return None
    finally:
        session.close()

def get_user_roles():
    """Get the current user's roles as a list of role names"""
    user_id = flask.session.get("user_id")
    if not user_id:
        return []
    
    session = get_session()
    try:
        # Load user with roles in the same session context
        user = session.query(User).options(joinedload(User.roles)).filter_by(id=user_id).first()
        if not user:
            return []
        
        # Extract role names while session is open
        role_names = [role.name for role in user.roles]
        return role_names
    except Exception:
        return []
    finally:
        session.close()

def has_role(role_name):
    """Check if current user has a specific role"""
    user_roles = get_user_roles()
    return role_name in user_roles

def is_admin():
    """Check if current user is an admin"""
    return has_role("admin")

def is_technical_staff():
    """Check if current user is technical staff"""
    return has_role("technical_staff")

def is_non_technical_staff():
    """Check if current user is non-technical staff"""
    return has_role("non_technical_staff")

def is_staff():
    """Check if current user is any type of staff"""
    return is_technical_staff() or is_non_technical_staff()

def require_login():
    """Check if user is logged in"""
    return flask.session.get("user_id") is not None

def require_role(required_role):
    """Decorator to require a specific role for page access"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not require_login():
                return {
                    "error": "login_required",
                    "message": "You must be logged in to access this page.",
                    "redirect": "/login"
                }
            
            if not has_role(required_role):
                return {
                    "error": "insufficient_permissions", 
                    "message": f"You need {required_role} permissions to access this page.",
                    "redirect": "/"
                }
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_admin():
    """Decorator to require admin role"""
    return require_role("admin")

def require_technical_staff():
    """Decorator to require technical staff role"""
    return require_role("technical_staff")

def get_user_display_info():
    """Get user info for display purposes"""
    user_id = flask.session.get("user_id")
    user_name = flask.session.get("user_name") 
    user_email = flask.session.get("user_email")
    
    return {
        "id": user_id,
        "name": user_name,
        "email": user_email,
        "roles": get_user_roles(),
        "is_admin": is_admin(),
        "is_technical_staff": is_technical_staff(),
        "is_staff": is_staff()
    } 