from extensions import db

class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)

    specialization = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.Text, nullable=True, default="[]")
    experience_yrs = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship("User", backref=db.backref("doctor_profile", uselist=False))
    department = db.relationship("Department", backref="doctors")

    def __repr__(self):
        return f"<Doctor user_id={self.user_id} spec={self.specialization}>"