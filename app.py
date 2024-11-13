from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, time
from models import db, User, Checkin, Penalty
from forms import (
    LoginForm, RegistrationForm, CheckinForm, PenaltyForm, 
    UserEditForm, DeleteUserForm
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotelms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Job role check-in times
JOB_ROLE_TIMES = {
    "DAY RECEPTIONIST": time(7, 30),
    "THE CLEANER": time(8, 30),
    "HOUSE KEEPING": time(8, 30),
    "NIGHT RECEPTIONIST": time(17, 30),  # Check-in deadline for Night Receptionist at 5:30 PM
    "SUPERVISOR": time(8, 0),
}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.role != 'manager':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(
            full_name=form.full_name.data,
            username=form.username.data,
            password=hashed_password,
            role=form.role.data,
            job_role=form.job_role.data if form.role.data != 'chairman' else None
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully!', 'success')
        return redirect(url_for('manage_users'))
    return render_template('register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    checkins = Checkin.query.filter_by(user_id=current_user.id).all()
    penalties = Penalty.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', checkins=checkins, penalties=penalties, job_role=current_user.job_role)

@app.route('/chairman_dashboard')
@login_required
def chairman_dashboard():
    if current_user.role != 'chairman':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    
    checkins = Checkin.query.all()
    penalties = Penalty.query.all()
    return render_template('chairman_dashboard.html', checkins=checkins, penalties=penalties)

@app.route('/checkin', methods=['GET', 'POST'])
@login_required
def checkin():
    form = CheckinForm()
    now = datetime.utcnow()

    # Restriction for NIGHT RECEPTIONIST: can check in only between 5:00 PM and 5:30 PM
    if current_user.job_role and current_user.job_role.upper() == "NIGHT RECEPTIONIST":
        allowed_checkin_start = time(17, 0)
        allowed_checkin_end = JOB_ROLE_TIMES["NIGHT RECEPTIONIST"]
        
        if not (allowed_checkin_start <= now.time() <= allowed_checkin_end):
            flash("Check-in for Night Receptionist is only allowed between 5:00 PM and 5:30 PM.", "warning")
            return redirect(url_for('dashboard'))

    last_checkin = Checkin.query.filter_by(user_id=current_user.id).order_by(Checkin.timestamp.desc()).first()
    if last_checkin and last_checkin.timestamp.date() == now.date():
        flash('You have already checked in today. Please wait until tomorrow to check in again.', 'warning')
        return redirect(url_for('dashboard'))

    if form.validate_on_submit():
        checkin_time = now.time()
        new_checkin = Checkin(user_id=current_user.id, timestamp=now)
        db.session.add(new_checkin)

        # Apply penalty if late
        role = current_user.job_role.upper() if current_user.job_role else None
        required_time = JOB_ROLE_TIMES.get(role)
        if required_time and checkin_time > required_time:
            penalty = Penalty(
                user_id=current_user.id,
                description="Late Arrival",
                amount=5.0,
                remark=f"Required time: {required_time}, Checked in at: {checkin_time}"
            )
            db.session.add(penalty)
            flash("You have been penalized for late arrival.", "danger")

        db.session.commit()
        flash('Check-in successful!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('checkin.html', form=form)

@app.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if current_user.role != 'manager':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    users = User.query.all()
    edit_form = UserEditForm()
    delete_forms = {user.id: DeleteUserForm() for user in users}
    return render_template('manage_users.html', users=users, edit_form=edit_form, delete_forms=delete_forms)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'manager':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    if form.validate_on_submit():
        user.full_name = form.full_name.data
        user.username = form.username.data
        if form.password.data:
            user.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user.role = form.role.data
        user.job_role = form.job_role.data if form.role.data != 'chairman' else None
        db.session.commit()
        flash('User details updated successfully.', 'success')
        return redirect(url_for('manage_users'))
    return render_template('edit_user.html', form=form, user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'manager':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    user = User.query.get_or_404(user_id)
    if user.role == 'chairman':
        flash('Cannot delete chairman!', 'danger')
        return redirect(url_for('manage_users'))
    
    # Delete associated check-ins and penalties before deleting the user
    Checkin.query.filter_by(user_id=user.id).delete()
    Penalty.query.filter_by(user_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/manage_penalties', methods=['GET', 'POST'])
@login_required
def manage_penalties():
    if current_user.role != 'manager':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    form = PenaltyForm()
    users = User.query.all()
    form.user_id.choices = [(user.id, user.full_name) for user in users]
    if form.validate_on_submit():
        penalty = Penalty(
            user_id=form.user_id.data,
            description=form.description.data,
            amount=form.amount.data,
            remark=form.remark.data
        )
        db.session.add(penalty)
        db.session.commit()
        flash('Penalty added successfully!', 'success')
        return redirect(url_for('manage_penalties'))
    penalties = Penalty.query.order_by(Penalty.timestamp.desc()).all()
    return render_template('manage_penalties.html', form=form, penalties=penalties)

@app.route('/history', methods=['GET', 'POST'])
@login_required
def history():
    if current_user.role != 'chairman':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        Checkin.query.delete()
        Penalty.query.delete()
        db.session.commit()
        flash('Monthly records reset successfully.', 'success')

    checkins = Checkin.query.all()
    penalties = Penalty.query.all()
    return render_template('history.html', checkins=checkins, penalties=penalties)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
