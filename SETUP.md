# Setup Instructions for Northeastern Airways Booking System

## Prerequisites
- Python 3.8+ installed
- pip (Python package manager)
- virtualenv (recommended)

## Step 1: Set Up a Virtual Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

## Step 2: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

## Step 3: Initialize the Database
```bash
# Run the database initialization script
python init_db.py
```

## Step 4: Environment Configuration
Create a `.env` file in the root directory with the following content:
```
# Database configuration
DATABASE_URL=sqlite:///northeastern_airways.db

# Flask configuration
SECRET_KEY=your_secure_random_key
FLASK_DEBUG=True
DEBUG=True

# App configuration
COMPANY_NAME=Northeastern Airways
ADMIN_EMAIL=admin@northeastern-airways.com
```

## Step 5: Run the Application
```bash
# Start the application
python app.py
```

The application will be available at http://127.0.0.1:8050/ in your web browser.

## Default Admin Login
- Email: admin@northeastern-airways.com
- Password: admin123

## Key Features
1. **User Management**: Register and login with role-based access
2. **Flight Search**: Search for flights by departure, arrival, and date
3. **Booking System**: Book flights and manage your bookings
4. **Ratings & Feedback**: Rate your flights after completion

## Project Structure
- `app.py`: Main application entry point
- `src/models/`: Database models (ORM)
- `src/pages/`: Dash UI pages
- `src/logic/`: Business logic modules
- `src/utils/`: Utility functions and helpers
- `assets/`: Static files (images, CSS, etc.) 