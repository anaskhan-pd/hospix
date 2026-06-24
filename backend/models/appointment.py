from extensions import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)

    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"),  nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    date = db.Column(db.Date,    nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.String(255), nullable=True)

    status = db.Column(db.String(20), default="booked") 

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship("Doctor",  backref="appointments")
    patient = db.relationship("Patient", backref="appointments")

    def __repr__(self):
        return f"<Appointment {self.id} | {self.date} {self.time_slot} | {self.status}>"