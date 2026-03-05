from datetime import date, timedelta
from extensions import db
from models import Role, User, Student, Company, Drive, Application


def seed_database():

    # Prevent duplicate seeding
    if Student.query.first():
        return "Database already seeded."

    # Fetch roles
    student_role = Role.query.filter_by(name="student").first()
    company_role = Role.query.filter_by(name="company").first()

    if not student_role or not company_role:
        return "Required roles not found."

    # ---- Students ----
    students = []
    for i in range(1, 6):
        user = User(
            username=f"student{i}",
            email=f"student{i}@test.com",
            role_id=student_role.id
        )
        user.set_password("password")

        student = Student(
            name=f"Student {i}",
            user=user,
            department="CSE",
            degree="B.Tech",
            contact_number=f"98765432{i:02d}"
        )

        db.session.add(user)
        db.session.add(student)
        students.append(student)

    # ---- Companies ----
    companies = []
    for i in range(1, 4):
        user = User(
            username=f"company{i}",
            email=f"company{i}@test.com",
            role_id=company_role.id
        )
        user.set_password("password")

        company = Company(
            name=f"Company {i}",
            industry="Software",
            user=user,
            hr_name="HR Person",
            hr_email=f"hr{i}@company.com",
            hr_contact=f"99988877{i:02d}",
            description="Test company",
            location="India",
            website="https://example.com",
            is_approved=True
        )

        db.session.add(user)
        db.session.add(company)
        companies.append(company)

    db.session.commit()

    # ---- Drives ----
    drives = []
    for i, company in enumerate(companies, start=1):
        drive = Drive(
            company=company,
            name=f"Drive {i}",
            job_title="Software Engineer",
            job_description="Test role",
            job_location="Remote",
            eligibility_criteria="CSE only",
            application_deadline=date.today() + timedelta(days=30),
            salary=1000000
        )

        db.session.add(drive)
        drives.append(drive)

    db.session.commit()

    # ---- Applications ----
    for student in students:
        for drive in drives:
            application = Application(
                student=student,
                drive=drive,
                status="applied",
                resume_link="https://resume.link"
            )
            db.session.add(application)

    db.session.commit()

    return "Database seeded successfully."