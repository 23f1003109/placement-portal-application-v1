from flask import render_template, redirect, url_for, abort, request
from flask_login import login_required, current_user
from . import company_bp
from functools import wraps
from forms import CreateDriveForm, ShortlistForm, MakeCompanyProfileForm,HideCSRFTokenForm
from models import Drive, Application, Company
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

@company_bp.route('/')
@login_required
@role_required('company')
def index():
    if not current_user.company:
        return redirect(url_for('company.create_company'))
    company = current_user.company
    upcoming_drives = [drive for drive in company.drives if not drive.is_completed]
    closed_drives = [drive for drive in company.drives if drive.is_completed]
    form = HideCSRFTokenForm()
    return render_template('company/index.html', company=company, upcoming_drives=upcoming_drives, closed_drives=closed_drives, form=form)


@company_bp.route('/create_company/', methods=['GET', 'POST'])
@login_required
@role_required('company')
def create_company():
    form = MakeCompanyProfileForm()
    if form.validate_on_submit():
        kwargs = {
            "user_id" : current_user.id,
            "name": form.name.data,
            "industry": form.industry.data,
            "hr_name": form.hr_name.data,
            "hr_email": form.hr_email.data,
            "hr_contact": form.hr_contact.data,
            "description": form.description.data,
            "location": form.location.data,
            "website": form.website.data,
        }
        company = Company(**kwargs)
        db.session.add(company)
        db.session.commit()
        return redirect(url_for('company.index'))
    return render_template('company/create_company.html', form=form)



@company_bp.route('/edit_company/', methods=['GET', 'POST'])
@login_required
@role_required('company')
def edit_company():
    if current_user.company.is_blacklisted:
        abort(403)
    form = MakeCompanyProfileForm()
    if request.method == 'GET':
        form.name.data = current_user.company.name
        form.industry.data = current_user.company.industry
        form.hr_name.data = current_user.company.hr_name
        form.hr_email.data = current_user.company.hr_email
        form.hr_contact.data = current_user.company.hr_contact
        form.description.data = current_user.company.description
        form.location.data = current_user.company.location
        form.website.data = current_user.company.website

    if form.validate_on_submit():
        form.populate_obj(current_user.company)
        return redirect(url_for('company.index'))
    return render_template('company/edit_company.html', form=form)


@company_bp.route('/create_drive/', methods=['GET', 'POST'])
@login_required
@role_required('company')
def create_drive():
    if current_user.company.is_blacklisted:
        abort(403)
    if not current_user.company.is_approved:
        return redirect(url_for('company.index'))
    form = CreateDriveForm()
    if form.validate_on_submit():
        kwargs = {
            "name" : form.drive_name.data,
            "job_title" : form.job_title.data,
            "job_description" : form.job_description.data,
            "job_location": form.job_location.data,
            "salary" : form.salary.data,
            "eligibility_criteria" : form.eligibility_criteria.data,
            "application_deadline" : form.application_deadline.data,
            "company_id": current_user.company.id
        }
        drive = Drive(**kwargs)
        db.session.add(drive)
        db.session.commit()
        return  redirect(url_for('company.index'))
    return render_template('company/create_drive.html', form=form)



@company_bp.route('/view_drive/<int:drive_id>/')
@login_required
@role_required('company')
def view_drive(drive_id):
    if current_user.company.is_blacklisted:
        abort(403)
    drive = Drive.query.filter_by(company_id=current_user.company.id, id=drive_id).first_or_404()
    return render_template('company/view_drive.html', drive=drive)

@company_bp.route('/drive_completed/<int:drive_id>/')
@login_required
@role_required('company')
def drive_completed(drive_id):
    if current_user.company.is_blacklisted:
        abort(403)
    drive = Drive.query.get_or_404(drive_id)
    drive.is_completed = True
    db.session.commit()
    return redirect(url_for('company.index'))


@company_bp.route('/student_application/<int:application_id>/')
@login_required
@role_required('company')
def student_application(application_id):
    if current_user.company.is_blacklisted:
        abort(403)
    application = Application.query.join(Drive).filter(Application.id == application_id, Drive.company_id==current_user.company.id).first_or_404()
    shortlist_form = ShortlistForm()
    return render_template('company/student_application.html', application=application, shortlist_form=shortlist_form)

@company_bp.route('/update_drive/<int:drive_id>/')
@login_required
@role_required('company')
def update_drive(drive_id):
    if current_user.company.is_blacklisted:
        abort(403)
    drive = Drive.query.get_or_404(drive_id)
    drive.is_completed = False
    db.session.commit()
    return redirect(url_for('company.index'))