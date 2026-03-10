from sqlalchemy import text
from flask import Flask

from config import Config
from extensions import db, login_manager, bcrypt, csrf
from models import User, Role


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
        migrate_application_status_schema()

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


def migrate_application_status_schema():
    row = db.session.execute(
        text("SELECT sql FROM sqlite_master WHERE type='table' AND name='applications'")
    ).scalar()

    if not row or 'selected' not in row:
        return

    with db.engine.begin() as connection:
        connection.execute(text('PRAGMA foreign_keys=OFF'))
        connection.execute(text(
            '''
            CREATE TABLE applications_new (
                id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                drive_id INTEGER NOT NULL,
                application_date DATE,
                status VARCHAR(20),
                remark TEXT,
                resume_link TEXT NOT NULL,
                PRIMARY KEY (id),
                CONSTRAINT unique_application UNIQUE (student_id, drive_id),
                CONSTRAINT check_valid_status CHECK (
                    status IN ("applied", "shortlisted", "interview", "rejected", "placed")
                ),
                FOREIGN KEY(student_id) REFERENCES students (id),
                FOREIGN KEY(drive_id) REFERENCES drives (id)
            )
            '''
        ))
        connection.execute(text(
            '''
            INSERT INTO applications_new (id, student_id, drive_id, application_date, status, remark, resume_link)
            SELECT
                id,
                student_id,
                drive_id,
                application_date,
                CASE
                    WHEN status = 'selected' THEN 'placed'
                    WHEN status IS NULL OR status = '' THEN 'applied'
                    ELSE status
                END,
                CASE
                    WHEN remark IS NULL OR remark = '' OR remark = 'None' THEN 'Pending review'
                    ELSE remark
                END,
                resume_link
            FROM applications
            '''
        ))
        connection.execute(text('DROP TABLE applications'))
        connection.execute(text('ALTER TABLE applications_new RENAME TO applications'))
        connection.execute(text('PRAGMA foreign_keys=ON'))
