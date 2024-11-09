from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    HiddenField,
    FloatField
)
from wtforms.validators import (
    DataRequired,
    Length,
    EqualTo,
    Optional,
    ValidationError
)
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=150)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('employee', 'Employee'), ('manager', 'Manager'), ('chairman', 'Chairman')], validators=[DataRequired()])
    job_role = SelectField('Job Role', choices=[
        ('DAY RECEPTIONIST', 'Day Receptionist'),
        ('THE CLEANER', 'The Cleaner'),
        ('HOUSE KEEPING', 'House Keeping'),
        ('NIGHT RECEPTIONIST', 'Night Receptionist')
    ], validators=[Optional()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

class CheckinForm(FlaskForm):
    qr_code_data = HiddenField('QR Code Data', validators=[DataRequired()])
    checkin_button = SubmitField('Check In')

class PenaltyForm(FlaskForm):
    user_id = SelectField('User', coerce=int, validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired(), Length(min=2, max=255)])
    amount = FloatField('Amount (GHS)', validators=[DataRequired()])
    remark = StringField('Remark', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Add Penalty')

class UserEditForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=150)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[Optional(), EqualTo('password')])
    role = SelectField('Role', choices=[('employee', 'Employee'), ('manager', 'Manager'), ('chairman', 'Chairman')], validators=[DataRequired()])
    job_role = SelectField('Job Role', choices=[
        ('DAY RECEPTIONIST', 'Day Receptionist'),
        ('THE CLEANER', 'The Cleaner'),
        ('HOUSE KEEPING', 'House Keeping'),
        ('NIGHT RECEPTIONIST', 'Night Receptionist')
    ], validators=[Optional()])
    submit = SubmitField('Update')

class DeleteUserForm(FlaskForm):
    submit = SubmitField('Delete')
