from app import app
from models import db, User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print("Admin user already exists.")
        else:
            admin = User(
                full_name='Administrator',
                username='admin',
                password=generate_password_hash('AdminPass123', method='pbkdf2:sha256'),
                role='manager',  # Assuming manager role has admin privileges
                job_role='Supervisor'  # Assigning job role 'Supervisor' for the manager/admin
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully.")

if __name__ == '__main__':
    create_admin()
