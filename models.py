from datetime import date

from constraints import *
from sqlalchemy import CheckConstraint
from extensions import db


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_ROLE_LENGTH), unique=True)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('Role')

    username = db.Column(db.String(MAX_USERNAME_LENGTH), unique=True, nullable=False)
    email = db.Column(db.String(MAX_EMAIL_LENGTH), unique=True, nullable=False)
    password = db.Column(db.String(PASSWORD_HASH_LENGTH), nullable=False)
    student = db.relationship('Student', back_populates='user', uselist=False, cascade='all, delete-orphan')
    company = db.relationship('Company', back_populates='user', uselist=False, cascade='all, delete-orphan')


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(MAX_NAME_LENGTH))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    user = db.relationship('User', back_populates='student')

    department = db.Column(db.String(MAX_DEPARTMENT_NAME_LENGTH), nullable=False)
    degree = db.Column(db.String(MAX_DEGREE_NAME_LENGTH), nullable=False)
    contact_number = db.Column(db.String(MAX_CONTACT_NUMBER_LENGTH), nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False)

    applications = db.relationship('Application', back_populates='student', cascade='all, delete-orphan')



class Company(db.Model):
    __tablename__ ="companies"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(MAX_NAME_LENGTH), nullable=False, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    user = db.relationship('User', back_populates='company', uselist=False)

    hr_name = db.Column(db.String(MAX_NAME_LENGTH), nullable=False)
    hr_email = db.Column(db.String(MAX_EMAIL_LENGTH), nullable=False)
    hr_contact = db.Column(db.String(MAX_CONTACT_NUMBER_LENGTH), nullable=False)

    description = db.Column(db.Text)
    location = db.Column(db.Text)
    website = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    is_blacklisted = db.Column(db.Boolean, nullable=False, default=False)

    drives =db.relationship('Drive', back_populates='company', cascade='all, delete-orphan')
    

class Drive(db.Model):
    __tablename__ = "drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    job_title = db.Column(db.String(MAX_NAME_LENGTH), nullable=False)
    job_description = db.Column(db.Text)
    job_location = db.Column(db.Text)
    salary = db.Column(db.Integer, nullable=False)

    company = db.relationship('Company', back_populates='drives')
    applications = db.relationship('Application', back_populates='drive', cascade='all, delete-orphan')



class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    student = db.relationship('Student', back_populates='applications')

    drive_id = db.Column(db.Integer, db.ForeignKey('drives.id'), nullable=False)
    drive = db.relationship('Drive', back_populates='applications')

    application_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(MAX_STATUS_TEXT_LENGTH), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),
        CheckConstraint('status IN ("applied", "shortlisted", "selected", "rejected")', name="check_valid_status"),
    )
