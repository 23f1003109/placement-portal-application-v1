from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField, SelectField, TextAreaField, RadioField, DateField
from wtforms.fields.datetime import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, Optional, URL
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

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        email = self.email.data
        username = self.username.data
        user = User.query.filter_by(email=email, username=username).first()

        if not user:
            self.username.errors.append("Invalid username or email combination.")
            return False

        self.user = user
        return True

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), Length(max=MAX_RAW_PASSWORD_LENGTH)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(max=MAX_RAW_PASSWORD_LENGTH)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), Length(max=MAX_RAW_PASSWORD_LENGTH), EqualTo('new_password', message='Passwords must match the new password!')])
    submit = SubmitField('Change Password')

class UpdateStudentProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=MAX_NAME_LENGTH)])
    department = StringField('Department', validators=[DataRequired(), Length(max=MAX_DEPARTMENT_NAME_LENGTH)])
    degree = StringField('Degree', validators=[DataRequired(), Length(max=MAX_DEGREE_NAME_LENGTH)])
    contact_number = StringField('Phone Number', validators=[DataRequired(), Length(max=MAX_CONTACT_NUMBER_LENGTH), Regexp(r'^\+?\d{10,15}$', message="Invalid format for a phone number.")])


class UpdateCompanyProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=MAX_NAME_LENGTH)])
    industry = StringField('Industry', validators=[DataRequired(), Length(max=MAX_NAME_LENGTH)])
    hr_name = StringField('HR Name', validators=[DataRequired(), Length(max=MAX_NAME_LENGTH)])
    hr_email = EmailField('Email', validators=[DataRequired(), Length(max=MAX_EMAIL_LENGTH), Email()])
    hr_contact = StringField('Phone Number', validators=[DataRequired(), Length(max=MAX_CONTACT_NUMBER_LENGTH), Regexp(r'^\+?\d{10,15}$', message="Invalid format for a phone number.")])
    description = TextAreaField('Description')
    location = TextAreaField('Location')
    website = TextAreaField('Website', validators=[Optional(),URL(message='Not a valid domain! You may leave this field empty.')])

class CreateDriveForm(FlaskForm):
    drive_name = StringField('Drive Name', validators=[DataRequired(), Length(max=MAX_NAME_LENGTH)])
    job_title = StringField('Job Title', validators=[DataRequired(), Length(max=MAX_NAME_LENGTH)])
    job_description = TextAreaField('Job Description', )
    job_location = TextAreaField('Job Location')
    eligibility_criteria = TextAreaField('Eligibility Criteria')
    application_deadline = DateField('Application Deadline', validators=[DataRequired()])
    salary = IntegerField('Salary', validators=[DataRequired()])
    submit = SubmitField('Create Drive')


class ShortlistForm(FlaskForm):
    application_status = SelectField('Application Status',choices=[('shortlist', 'Shortlist'), ('waiting', 'Waiting'), ('reject', 'Reject')], validators=[DataRequired()])
    save_status = SubmitField('Save Status')

class CreateApplicationForm(FlaskForm):
    resume_link = StringField('Resume Link', validators=[DataRequired(), URL(message='Not a valid domain!')])
    submit = SubmitField('Apply')

class FilterForm(FlaskForm):
    filter_by = SelectField('Filter By', validators=[DataRequired()], default='name')
    filter_query = StringField('Query')
    submit = SubmitField('Filter')

class HideCSRFTokenForm(FlaskForm):
    pass

class MakeCompanyProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=MAX_NAME_LENGTH)])
    industry = StringField('Industry', validators=[DataRequired(), Length(max=MAX_NAME_LENGTH)])
    hr_name = StringField('HR Name', validators=[DataRequired(), Length(max=MAX_NAME_LENGTH)])
    hr_email = EmailField('HR Email', validators=[DataRequired(), Length(max=MAX_EMAIL_LENGTH), Email()])
    hr_contact = StringField('HR Contact', validators=[DataRequired(), Length(max=MAX_CONTACT_NUMBER_LENGTH)])
    description = TextAreaField('Description', validators=[Optional()])
    location = TextAreaField('Location', validators=[Optional()])
    website = TextAreaField('Website', validators=[URL(message='Not a valid domain! You may leave this field empty.'), Optional()])
    submit = SubmitField('Update Profile')


class MakeStudentProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=MAX_NAME_LENGTH)])
    department = StringField('Department', validators=[DataRequired(), Length(max=MAX_DEPARTMENT_NAME_LENGTH)])
    degree = StringField('Degree', validators=[DataRequired(), Length(max=MAX_DEGREE_NAME_LENGTH)])
    contact_number = StringField('Phone Number', validators=[DataRequired(), Length(max=MAX_CONTACT_NUMBER_LENGTH)])
    submit = SubmitField('Update Profile')

