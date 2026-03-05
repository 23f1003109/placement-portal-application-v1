from flask import render_template, redirect, url_for, abort
from functools import wraps
from . import student_bp
from flask_login import current_user, login_required
from models import User, Student, Drive, Application, Company
from extensions import db


def role_required(role_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.role or current_user.role.name != role_name:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator


@student_bp.route('/')
@login_required
@role_required('student')
def index():
    return render_template("index.html")


@student_bp.route('/view_history')
@login_required
@role_required('student')
def view_history():
    return render_template('student/view_history.html')

@student_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
@role_required('student')
def edit_profile():
    pass


@student_bp.route('/company/<int:company_id>/')
@login_required
@role_required('student')
def view_company(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template('student/company.html', company=company)


@student_bp.route('view_drive/<int:drive_id>/')
@login_required
@role_required('student')
def view_drive(drive_id):
    drive = Drive.query.get_or_404(drive_id)
    return render_template('student/drive.html', drive=drive)

@student_bp.route('/apply_drive/<int:drive_id>/', methods=['GET', 'POST'])
@login_required
@role_required('student')
def apply_drive(drive_id):
    pass
