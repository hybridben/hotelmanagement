from app import app, db
from models import User, Checkin, Penalty

def init_db():
    with app.app_context():
        db.drop_all()  # Optional: Drops all tables if you want a fresh start
        db.create_all()  # Creates all tables according to the current models
        print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
