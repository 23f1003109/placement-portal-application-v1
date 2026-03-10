from functools import wraps

from flask import render_template, redirect, url_for, abort, flash
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from . import student_bp
from extensions import db
from forms import MakeStudentProfileForm, CreateApplicationForm, HideCSRFTokenForm
from models import Student, Drive, Application, Company


def role_required(role_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.role or current_user.role.name != role_name:
                abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_accessible_drive_or_404(drive_id, include_existing_application=False):
    drive = Drive.query.get_or_404(drive_id)
    student = current_user.student
    existing_application = None

    if student:
        existing_application = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()

    if drive.company.is_blacklisted or not drive.company.is_approved:
        abort(404)

    if not drive.is_open and not (include_existing_application and existing_application):
        abort(404)

    return drive, existing_application


@student_bp.route('/')
@login_required
@role_required('student')
def index():
    if not current_user.student:
        return redirect(url_for('student.create_student'))

    student = current_user.student
    companies = Company.query.filter_by(is_approved=True, is_blacklisted=False).order_by(Company.name.asc()).all()
    recent_applications = (
        Application.query.filter_by(student_id=student.id)
        .order_by(Application.application_date.desc(), Application.id.desc())
        .all()
    )
    form = HideCSRFTokenForm()
    return render_template(
        'student/index.html',
        student=student,
        companies=companies,
        recent_applications=recent_applications,
        form=form,
    )


@student_bp.route('/create_student/', methods=['GET', 'POST'])
@login_required
@role_required('student')
def create_student():
    form = MakeStudentProfileForm()
    if form.validate_on_submit():
        kwargs = {
            key: value
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

    application_history = (
        Application.query.filter_by(student_id=current_user.student.id)
        .order_by(Application.application_date.desc(), Application.id.desc())
        .all()
    )
    form = HideCSRFTokenForm()
    return render_template('student/view_history.html', application_history=application_history, form=form)


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
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('student.index'))
    return render_template('student/edit_student.html', form=form)


@student_bp.route('/view_company/<int:company_id>/')
@login_required
@role_required('student')
def view_company(company_id):
    if current_user.student.is_blacklisted:
        abort(403)

    form = HideCSRFTokenForm()
    company = Company.query.filter_by(id=company_id, is_approved=True, is_blacklisted=False).first_or_404()
    open_drives = [drive for drive in company.drives if drive.is_open]
    return render_template('student/view_company.html', company=company, open_drives=open_drives, form=form)


@student_bp.route('/view_drive/<int:drive_id>/')
@login_required
@role_required('student')
def view_drive(drive_id):
    if current_user.student.is_blacklisted:
        abort(403)

    drive, existing_application = get_accessible_drive_or_404(drive_id, include_existing_application=True)
    return render_template('student/view_drive.html', drive=drive, existing_application=existing_application)


@student_bp.route('/apply_drive/<int:drive_id>/', methods=['GET', 'POST'])
@login_required
@role_required('student')
def apply_drive(drive_id):
    if current_user.student.is_blacklisted:
        abort(403)

    drive, existing_application = get_accessible_drive_or_404(drive_id, include_existing_application=True)
    if existing_application:
        flash('You have already applied for this placement drive.', 'warning')
        return redirect(url_for('student.view_drive', drive_id=drive.id))

    if not drive.is_open:
        flash('This placement drive is no longer accepting applications.', 'danger')
        return redirect(url_for('student.view_drive', drive_id=drive.id))

    form = CreateApplicationForm()
    if form.validate_on_submit():
        application = Application(
            student_id=current_user.student.id,
            drive_id=drive.id,
            resume_link=form.resume_link.data,
        )
        db.session.add(application)
        try:
            db.session.commit()
            flash('Application submitted successfully.', 'success')
            return redirect(url_for('student.view_history'))
        except IntegrityError:
            db.session.rollback()
            flash('You have already applied for this placement drive.', 'warning')
            return redirect(url_for('student.view_drive', drive_id=drive.id))

    return render_template('student/apply_drive.html', form=form, drive=drive)
