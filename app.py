from constraints import *
from flask import Flask, render_template, url_for, redirect, request
from config import Config
from extensions import db, login_manager, bcrypt, csrf
from models import User, Role
# from forms import (ResetPasswordForm, LoginForm, RegistrationForm, ChangePasswordForm,
#     UpdateCompanyProfileForm, UpdateStudentProfileForm, CreateDriveForm,
#     CreateApplicationForm)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.login'

    from auth import auth_bp
    from admin import admin_bp
    from company import company_bp
    from student import student_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(company_bp, url_prefix='/company')
    app.register_blueprint(student_bp, url_prefix='/student')

    with app.app_context():
        db.create_all()
        seed_roles_and_admin()

    return app

def seed_roles_and_admin():
    for role_name in ['admin', 'company', 'student']:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name))

    db.session.commit()

    admin_role = Role.query.filter_by(name='admin').first()

    if not User.query.filter_by(username='admin').first():
        admin_email = 'admin@iitm.ac.in'
        admin_raw_password = 'password'
        admin_username = 'admin'
        role_id = admin_role.id

        admin = User(email=admin_email, username=admin_username, role_id=role_id)
        admin.set_password(admin_raw_password)

        db.session.add(admin)
        db.session.commit()