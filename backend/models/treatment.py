from extensions import db 
from datetime import datetime

class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key= True)

    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"),unique=True, nullable = False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship("Appointment", backref=db.backref("treatment", uselist=False), uselist=False)

    def __repr__(self):
        return f"<Treatment {self.id} for Appointment {self.appointment_id}>"
