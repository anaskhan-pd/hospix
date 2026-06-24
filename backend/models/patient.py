from extensions import db

class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    age = db.Column(db.Integer , nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(20) , nullable=False)
    address = db.Column(db.String(200) , nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship("User", backref=db.backref("patient_profile", uselist = False))


    def __repr__(self):
        return f"<Patient user_id={self.user_id}>"
