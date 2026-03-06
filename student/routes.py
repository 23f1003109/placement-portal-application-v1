from flask import render_template, redirect, url_for, abort
from functools import wraps
from . import student_bp
from flask_login import current_user, login_required
from models import User, Student, Drive, Application, Company
from forms import MakeStudentProfileForm, CreateApplicationForm, HideCSRFTokenForm
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
    if not current_user.student:
        return redirect(url_for('student.create_student'))
    student = current_user.student
    companies = Company.query.all()
    applied_applications =[application for application in student.applications if application.status == 'applied']
    form = HideCSRFTokenForm()
    return render_template("student/index.html", student=student, companies=companies, applied_applications=applied_applications, form=form)

@student_bp.route('/create_student/', methods=['GET', 'POST'])
@login_required
@role_required('student')
def create_student():
    form = MakeStudentProfileForm()
    if form.validate_on_submit():
        kwargs = {
            key : value
            for key, value in form.data.items()
            if key not in ('submit', 'csrf_token')
        }
        kwargs['user_id'] = current_user.id
        student = Student(**kwargs)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('student.index'))
    return render_template('student/create_student.html', form=form)


@student_bp.route('/view_history/')
@login_required
@role_required('student')
def view_history():
    if current_user.student.is_blacklisted:
        abort(403)
    application_history = current_user.student.applications
    return render_template('student/view_history.html', application_history=application_history)

@student_bp.route('/edit_profile/', methods=['GET', 'POST'])
@login_required
@role_required('student')
def edit_student():
    if current_user.student.is_blacklisted:
        abort(403)
    form = MakeStudentProfileForm()
    for field in form:
        if hasattr(current_user.student, field.name):
            field.data = getattr(current_user.student, field.name)
    if form.validate_on_submit():
        form.populate_obj(current_user.student)
        db.session.commit()
        return redirect(url_for('student.index'))
    return render_template('student/edit_student.html', form=form)


@student_bp.route('/view_company/<int:company_id>/')
@login_required
@role_required('student')
def view_company(company_id):
    if current_user.student.is_blacklisted:
        abort(403)
    form = HideCSRFTokenForm()
    company = Company.query.get_or_404(company_id)
    return render_template('student/view_company.html', company=company, form=form)


@student_bp.route('view_drive/<int:drive_id>/')
@login_required
@role_required('student')
def view_drive(drive_id):
    if current_user.student.is_blacklisted:
        abort(403)
    drive = Drive.query.get_or_404(drive_id)
    return render_template('student/view_drive.html', drive=drive)

@student_bp.route('/apply_drive/<int:drive_id>/', methods=['GET', 'POST'])
@login_required
@role_required('student')
def apply_drive(drive_id):
    if current_user.student.is_blacklisted:
        abort(403)
    drive = Drive.query.get_or_404(drive_id)
    form = CreateApplicationForm()
    if form.validate_on_submit():
        resume_link = form.resume_link.data
        student_id = current_user.student.id
        drive_id = drive.id
        application = Application(student_id=student_id, drive_id=drive_id, resume_link=resume_link)
        db.session.add(application)
        db.session.commit()
        return redirect(url_for('student.view_company', company_id=drive.company.id))
    return render_template('student/apply_drive.html', form=form)
