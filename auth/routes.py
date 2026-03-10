from flask import render_template, redirect, flash, url_for, abort
from models import User, Role
from extensions import db
from flask_login import login_user, current_user, login_required, logout_user

from forms import LoginForm, RegistrationForm, ResetPasswordForm, ChangePasswordForm
from . import auth_bp



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role.name}.index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            role_name = user.role.name
            login_user(user, remember=True)
            return redirect(url_for(f'{role_name}.index'))
        flash('Invalid username or password', 'danger')
    return render_template('auth/user_login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role.name}.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        role_name = form.role.data
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            flash("Invalid role selection.", "danger")
            return redirect(url_for("auth.register"))
        new_user = User(username=username, email=email, role_id=role.id)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for(f'{new_user.role.name}.index'))

    return render_template('auth/user_signup.html', form=form)

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset():
    if current_user.is_authenticated:
        return redirect(url_for('auth.change_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = form.user
        new_password = form.new_password.data
        user.set_password(new_password)
        db.session.commit()
        login_user(user, remember=True)
        return redirect(url_for(f"{user.role.name}.index"))
    return render_template('auth/reset.html', form=form)



@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            form.current_password.errors.append('Incorrect current password.')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password updated successfully.", "success")
            return redirect(url_for(f'{current_user.role.name}.index'))
    return render_template('auth/change_password.html', form=form)