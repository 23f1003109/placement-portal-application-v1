from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms import ValidationError
from constraints import *
from models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=MAX_USERNAME_LENGTH)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=MAX_EMAIL_LENGTH)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=MAX_RAW_PASSWORD_LENGTH)])
    password2 = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password', message='Passwords must match!'), Length(max=MAX_RAW_PASSWORD_LENGTH)])
    role = RadioField('Role', choices=[('student', 'Student'), ('company', 'Company')], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=MAX_USERNAME_LENGTH)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=MAX_RAW_PASSWORD_LENGTH)])
    submit = SubmitField('Login')

class ResetPasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=MAX_USERNAME_LENGTH)])
    email = EmailField('Email', validators=[DataRequired(), Length(max=MAX_EMAIL_LENGTH), Email()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(max=MAX_RAW_PASSWORD_LENGTH)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(max=MAX_RAW_PASSWORD_LENGTH), EqualTo('new_password', message='Passwords must match!')])
    submit = SubmitField('Reset Password')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), Length(max=MAX_RAW_PASSWORD_LENGTH)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(max=MAX_RAW_PASSWORD_LENGTH)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), Length(max=MAX_RAW_PASSWORD_LENGTH), EqualTo('new_password', message='Passwords must match the new password!')])
    submit = SubmitField('Change Password')

class UpdateStudentProfileForm(FlaskForm):
    pass

class UpdateCompanyProfileForm(FlaskForm):
    pass

class CreateDriveForm(FlaskForm):
    pass

class CreateApplicationForm(FlaskForm):
    pass