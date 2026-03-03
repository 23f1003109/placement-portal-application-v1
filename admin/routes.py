from flask import render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user
from . import admin_bp
from forms import FilterForm, HideCSRFTokenForm
from models import Student, Company, Drive, Application
from extensions import db
from functools import wraps

def role_required(role_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.role or current_user.role.name != role_name:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator

##########SEED ROUTE###########
from .seed import seed_database


@admin_bp.route('/seed/')
@login_required
@role_required('admin')
def seed():
    message = seed_database()
    return message

##############################

@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def index():
    hide_csrf_tokens = HideCSRFTokenForm()
    student_filter_form = FilterForm(prefix='student')
    company_filter_form = FilterForm(prefix='company')
    student_filter_form.filter_by.choices = [('name', 'Name'), ('student_id', 'Student ID'), ('contact_number', 'Contact Number')]
    company_filter_form.filter_by.choices = [('name', 'Name'), ('company_id', 'Company ID'), ('industry','Industry')]
    student_query = Student.query
    company_query = Company.query.filter_by(is_approved=True)
    students = student_query.all()
    companies = company_query.all()
    unapproved_companies = Company.query.filter_by(is_approved=False).all()
    ongoing_drives = Drive.query.filter_by(is_completed=False).all()
    company_applications = Company.query.filter_by(is_approved=False).all()
    student_drive_applications = Application.query.all()

    if student_filter_form.submit.data and student_filter_form.validate() and student_filter_form.filter_query.data != '':
        query = student_filter_form.filter_query.data
        if student_filter_form.filter_by.data == 'name':
            students = student_query.filter(Student.name.ilike(f'%{query}%')).all()

        if student_filter_form.filter_by.data == 'student_id':
            try:
                student_id =int(student_filter_form.filter_query.data)
                students = student_query.filter_by(id = student_id).all()
            except ValueError:
                students = []


        if student_filter_form.filter_by.data == 'contact_number':
            students = student_query.filter(Student.contact_number.ilike(f'%{query}%')).all()

    if company_filter_form.submit.data and company_filter_form.validate() and company_filter_form.filter_query.data != '':
        query = company_filter_form.filter_query.data
        if company_filter_form.filter_by.data == 'name':
            companies = company_query.filter(Company.name.ilike(f'%{query}%')).all()
        if company_filter_form.filter_by.data == 'company_id':
            try:
                company_id =int(company_filter_form.filter_query.data)
                companies = company_query.filter_by(id =company_id).all()
            except ValueError:
                companies = []
        if company_filter_form.filter_by.data == 'industry':
            companies = company_query.filter(Company.industry.ilike(f'%{query}%')).all()
    kwargs = {
        "student_filter_form": student_filter_form,
        "company_filter_form": company_filter_form,
        "unapproved_companies": unapproved_companies,
        "ongoing_drives": ongoing_drives,
        "students": students,
        "companies": companies,
        "student_drive_applications": student_drive_applications,
        "company_applications": company_applications,
        "hide_csrf_tokens": hide_csrf_tokens
    }

    return render_template('admin/index.html', **kwargs)


@admin_bp.route('/student/<int:student_id>/blacklist/', methods=['POST'])
@login_required
@role_required('admin')
def blacklist_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()
    return redirect(url_for('admin.index'))

@admin_bp.route('/company/<int:company_id>/blacklist/', methods=['POST'])
@login_required
@role_required('admin')
def blacklist_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_blacklisted = not company.is_blacklisted
    db.session.commit()
    return redirect(url_for('admin.index'))

@admin_bp.route('/company_application/<int:company_id>/', methods=['POST'])
@login_required
@role_required('admin')
def approve_company_applications(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_approved = True
    db.session.commit()
    return redirect(url_for('admin.index'))

@admin_bp.route('/completed_drive/<int:drive_id>/', methods=['POST'])
@login_required
@role_required('admin')
def mark_drive_as_completed(drive_id):
    drive = Drive.query.get_or_404(drive_id)
    drive.is_completed = True
    db.session.commit()
    return redirect(url_for('admin.index'))

@admin_bp.route('/view_student/<int:student_id>/')
@login_required
@role_required('admin')
def view_student(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('admin/student.html', student=student)

@admin_bp.route('/view_company/<int:company_id>/')
@login_required
@role_required('admin')
def view_company(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template('admin/company.html', company=company)

@admin_bp.route('/drive/<int:drive_id>/')
@login_required
@role_required('admin')
def view_drive(drive_id):
    drive = Drive.query.get_or_404(drive_id)
    return render_template('admin/drive.html', drive=drive)

@admin_bp.route('/application/<int:application_id>/')
@login_required
@role_required('admin')
def view_application(application_id):
    application = Application.query.get_or_404(application_id)
    return render_template('admin/application.html', application=application)