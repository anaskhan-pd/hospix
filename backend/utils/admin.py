from models.user import User
from extensions import db

def create_admin():
    admin_email = "admin@hospix.in"

    admin = User.query.filter_by(email= admin_email).first()

    if not admin:
        admin = User(
            name = "admin",
            email = admin_email,
            role = "admin"
        )

        admin.set_password("admin@123")

        db.session.add(admin)
        db.session.commit()

        print("Admin user created")
    else:
        print("Admin user already exists")
