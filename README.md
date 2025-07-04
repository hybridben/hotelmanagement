# HotelMS - Employee Check-In System

HotelMS is a Flask web application for managing hotel staff check-ins and attendance. It supports user authentication, role-based access, and automatic penalties for late check-ins based on job roles.

## Features

- Secure user login and logout
- Role-based permissions:
  - **Chairman:** view all records, reset history
  - **Manager:** manage users, assign penalties
  - **Employee:** daily check-in, view personal records
- Automatic penalties ($5) for late arrivals
- Dashboards for tracking check-ins and penalties
- Job-role-specific check-in times:
  - Day Receptionist: 7:30 AM
  - Cleaner / House Keeping: 8:30 AM
  - Supervisor: 8:00 AM
  - Night Receptionist: between 5:00 PM and 5:30 PM

## Tech Stack

- Python (Flask)
- Flask-Login
- Flask-WTF
- SQLite (SQLAlchemy)
- HTML/Jinja Templates

## How to Run

1. Install dependencies:
    ```bash
    pip install flask flask-login flask-wtf werkzeug
    ```

2. Run the app:
    ```bash
    python app.py
    ```

The app runs at [http://localhost:5000](http://localhost:5000).

