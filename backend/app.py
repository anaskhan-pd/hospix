import os
from flask import Flask , render_template , url_for , redirect , request , session , jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from config import BASE_DIR, Config
from extensions import db, cache
from routes.auth import auth_bp, role_required
from models.user import User
from models.doctor import Doctor
from models.patient import Patient
from models.appointment import Appointment
from models.treatment import Treatment
import json
from datetime import date as date_type, datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static")
)
app.config.from_object(Config)
app.secret_key = "dev-secret-key"
app.register_blueprint(auth_bp)


db.init_app(app)
cache.init_app(app)

os.makedirs(os.path.join(os.path.dirname(__file__), "instance"), exist_ok= True)
from models import user
from models.department import Department
from utils.admin import create_admin

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/app")
def index():
    return render_template("index.html")


@app.route("/ping")
def ping():
    return {"message": "Yes Sir ! Backend is working fine."}


@app.route("/api/admin/dashboard")
@role_required("admin")
@cache.cached(timeout=120, key_prefix="admin_dashboard")
def admin_dashboard():
    return jsonify({
        "doctorCount": Doctor.query.count(),
        "patientCount": Patient.query.count(),
        "appointmentCount": Appointment.query.count()
    })

@app.route('/api/admin/doctors', methods=['GET'])
@cache.cached(timeout=180, key_prefix="doctors_list")
@role_required("admin")
def api_admin_doctors():
    doctors = Doctor.query.all()
    doctor_list = []
    for doc in doctors:
        doctor_list.append({
            "id": doc.id,
            "name": doc.user.name,
            "email": doc.user.email,
            "specialization": doc.specialization,
            "isActive": doc.user.is_active
        })
    return jsonify(doctor_list)

@app.route('/api/admin/doctors', methods=['POST'])
@role_required("admin")
def add_doctor():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    specialization = data.get("specialization")

    if not all([name, email, password, specialization]):
        return jsonify({"error": "All fields are required."}), 400
    
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Doctor with this email already exists."}), 400
    
    new_user = User(name=name, email=email, password_hash =generate_password_hash(password), role="doctor", is_active = True)
    db.session.add(new_user)
    db.session.flush()

    new_doctor = Doctor(user_id=new_user.id, specialization=specialization)

    db.session.add(new_doctor)
    db.session.commit()
    cache.delete("admin_dashboard")
    cache.delete("doctors_list")

    return jsonify({"message": "Doctor added successfully."}), 201

@app.route("/api/admin/doctors/<int:doctor_id>", methods=["PUT"])
@role_required("admin")
def update_doctor(doctor_id):
    doc = Doctor.query.get_or_404(doctor_id)
    data = request.get_json()
    if "name" in data:
        doc.user.name = data["name"]
    if "specialization" in data:
        doc.specialization = data["specialization"]
    if "experience" in data:
        doc.experience_yrs = int(data["experience"])
    db.session.commit()
    return jsonify({"message": "Doctor updated"})


@app.route("/api/admin/doctors/<int:doctor_id>/toggle", methods=["POST"])
@role_required("admin")
def toggle_doctor(doctor_id):
    doc = Doctor.query.get_or_404(doctor_id)
    doc.user.is_active = not doc.user.is_active
    db.session.commit()
    cache.delete("admin_doctors")
    status = "activated" if doc.user.is_active else "blacklisted"
    return jsonify({"message": f"Doctor {status}", "isActive": doc.user.is_active})

@app.route("/api/admin/patients", methods=["GET"])
@role_required("admin")
def list_patients():
    from models.patient import Patient
    patients = Patient.query.all()
    return jsonify([{
        "id":      p.id,
        "name":    p.user.name,
        "email":   p.user.email,
        "contact": p.contact,
        "age":     p.age,
        "gender":  p.gender,
        "isActive": p.user.is_active,
    } for p in patients])


@app.route("/api/admin/patients/<int:patient_id>/toggle", methods=["POST"])
@role_required("admin")
def toggle_patient(patient_id):
    p = Patient.query.get_or_404(patient_id)
    p.user.is_active = not p.user.is_active
    db.session.commit()
    return jsonify({"isActive": p.user.is_active})


@app.route("/api/admin/search")
@role_required("admin")
def admin_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"doctors": [], "patients": []})

    doctors = Doctor.query.join(Doctor.user).filter(
        Doctor.user.has(User.name.ilike(f"%{q}%")) |
        Doctor.specialization.ilike(f"%{q}%")
    ).all()
    patients = Patient.query.join(Patient.user).filter(
        Patient.user.has(User.name.ilike(f"%{q}%")) |
        Patient.contact.ilike(f"%{q}%")
    ).all()

    return jsonify({
        "doctors":  [{"id": d.id, "name": d.user.name, "specialization": d.specialization} for d in doctors],
        "patients": [{"id": p.id, "name": p.user.name, "contact": p.contact} for p in patients],
    })


@app.route("/api/admin/appointments")
@role_required("admin")
def admin_appointments():
    appts = Appointment.query.order_by(Appointment.date.desc()).all()
    return jsonify([_appt_dict(a) for a in appts])


@app.route("/api/departments", methods=["GET"])
@cache.cached(timeout=300, key_prefix="departments_list")
def get_departments():
    depts = Department.query.all()
    return jsonify([{"id": d.id, "name": d.name, "description": d.description} for d in depts])


@app.route("/api/departments", methods=["POST"])
@role_required("admin")
def add_department():
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name required"}), 400
    if Department.query.filter_by(name=name).first():
        return jsonify({"error": "Department already exists"}), 409
    dept = Department(name=name, description=data.get("description", ""))
    db.session.add(dept)
    db.session.commit()
    return jsonify({"message": "Department added", "id": dept.id}), 201


@app.route("/api/doctors/search")
@cache.cached(timeout=300, query_string=True, key_prefix="search_doctors")
def search_doctors():
    spec = request.args.get("specialization", "").strip()
    query = Doctor.query.filter(Doctor.user.has(is_active=True))
    if spec:
        query = query.filter(Doctor.specialization.ilike(f"%{spec}%"))
    doctors = query.all()
    return jsonify([{
        "id":             d.id,
        "name":           d.user.name,
        "specialization": d.specialization,
        "experience":     d.experience_yrs,
        "availability":   d.availability or "[]",
    } for d in doctors])


@app.route("/api/doctor/appointments")
@role_required("doctor")
def doctor_appointments():
    doc = Doctor.query.filter_by(user_id=session["user_id"]).first_or_404()
    appts = Appointment.query.filter_by(doctor_id=doc.id).order_by(Appointment.date).all()
    return jsonify([_appt_dict(a) for a in appts])


@app.route("/api/doctor/appointments/<int:appt_id>/complete", methods=["POST"])
@role_required("doctor")
def complete_appointment(appt_id):
    doc = Doctor.query.filter_by(user_id=session["user_id"]).first_or_404()
    appt = Appointment.query.filter_by(id=appt_id, doctor_id=doc.id).first_or_404()
    data = request.get_json()
    appt.status = "completed"
    treatment = Treatment(
        appointment_id=appt.id,
        diagnosis=data.get("diagnosis", ""),
        prescription=data.get("prescription", ""),
        notes=data.get("notes", ""),
    )
    db.session.add(treatment)
    db.session.commit()
    return jsonify({"message": "Marked complete, treatment saved"})


@app.route("/api/doctor/appointments/<int:appt_id>/cancel", methods=["POST"])
@role_required("doctor")
def doctor_cancel_appointment(appt_id):
    doc = Doctor.query.filter_by(user_id=session["user_id"]).first_or_404()
    appt = Appointment.query.filter_by(id=appt_id, doctor_id=doc.id).first_or_404()
    appt.status = "cancelled"
    db.session.commit()
    return jsonify({"message": "Appointment cancelled"})


@app.route("/api/doctor/availability", methods=["POST"])
@role_required("doctor")
def set_availability():
    doc = Doctor.query.filter_by(user_id=session["user_id"]).first_or_404()
    data = request.get_json()
    dates = data.get("dates", [])           # list of date strings "YYYY-MM-DD"
    doc.availability = json.dumps(dates)
    db.session.commit()
    return jsonify({"message": "Availability updated"})


@app.route("/api/doctor/patients")
@role_required("doctor")
def doctor_patients():
    doc = Doctor.query.filter_by(user_id=session["user_id"]).first_or_404()
    appts = Appointment.query.filter_by(doctor_id=doc.id, status="completed").all()
    seen = {}
    for a in appts:
        pid = a.patient_id
        if pid not in seen:
            seen[pid] = {
                "id":      a.patient.id,
                "name":    a.patient.user.name,
                "age":     a.patient.age,
                "gender":  a.patient.gender,
                "contact": a.patient.contact,
                "history": []
            }
        t = a.treatment
        seen[pid]["history"].append({
            "date":         str(a.date),
            "diagnosis":    t.diagnosis    if t else "",
            "prescription": t.prescription if t else "",
            "notes":        t.notes        if t else "",
        })
    return jsonify(list(seen.values()))


@app.route("/api/patient/profile")
@role_required("patient")
def patient_profile():
    p = Patient.query.filter_by(user_id=session["user_id"]).first_or_404()
    return jsonify({
        "name":    p.user.name,
        "email":   p.user.email,
        "age":     p.age,
        "gender":  p.gender,
        "contact": p.contact,
        "address": p.address,
    })


@app.route("/api/patient/profile", methods=["PUT"])
@role_required("patient")
def update_patient_profile():
    p = Patient.query.filter_by(user_id=session["user_id"]).first_or_404()
    data = request.get_json()
    if "name"    in data: p.user.name = data["name"]
    if "contact" in data: p.contact   = data["contact"]
    if "address" in data: p.address   = data["address"]
    if "age"     in data: p.age       = int(data["age"])
    db.session.commit()
    return jsonify({"message": "Profile updated"})


@app.route("/api/patient/appointments", methods=["GET"])
@role_required("patient")
def patient_appointments():
    pat = Patient.query.filter_by(user_id=session["user_id"]).first_or_404()
    appts = Appointment.query.filter_by(patient_id=pat.id).order_by(Appointment.date.desc()).all()
    return jsonify([_appt_dict(a) for a in appts])

@app.route("/api/patient/appointments", methods=["POST"])
@role_required("patient")
def book_appointment():
    pat  = Patient.query.filter_by(user_id=session["user_id"]).first_or_404()
    data = request.get_json()
    doctor_id = data.get("doctor_id")
    date_str  = data.get("date")
    time_slot = data.get("time_slot", "").strip()
    reason    = data.get("reason", "")

    if not all([doctor_id, date_str, time_slot]):
        return jsonify({"error": "All fields are required"}), 400
    
    parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    existing = Appointment.query.filter_by(
        doctor_id=int(doctor_id), date=date_str, time_slot=time_slot
    ).filter(Appointment.status != "cancelled").first()
    if existing:
        return jsonify({"error": "This slot is already booked"}), 409

    appt = Appointment(
        doctor_id=int(doctor_id), patient_id=pat.id,
        date=parsed_date, time_slot=time_slot, reason=reason, status="booked"
    )
    db.session.add(appt)
    db.session.commit()
    return jsonify({"message": "Appointment booked", "id": appt.id}), 201


@app.route("/api/patient/appointments/<int:appt_id>/cancel", methods=["POST"])
@role_required("patient")
def cancel_appointment(appt_id):
    pat  = Patient.query.filter_by(user_id=session["user_id"]).first_or_404()
    appt = Appointment.query.filter_by(id=appt_id, patient_id=pat.id).first_or_404()
    if appt.status == "completed":
        return jsonify({"error": "Appointment is already completed"}), 400
    appt.status = "cancelled"
    db.session.commit()
    return jsonify({"message": "Appointment cancelled"})

@app.route("/api/patient/export-csv", methods=["GET"])
@role_required("patient")
def export_csv():
    from models.patient import Patient
    from models.appointment import Appointment
    import csv, io
    from flask import Response
    
    pat = Patient.query.filter_by(user_id=session["user_id"]).first_or_404()
    appts = Appointment.query.filter_by(
        patient_id=pat.id, status="completed"
    ).order_by(Appointment.date).all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Date", "Doctor", "Specialization", "Diagnosis", "Prescription", "Notes"])
    for a in appts:
        t = a.treatment
        if isinstance(t, list):
            t = t[0] if t else None
        writer.writerow([
            a.date,
            a.doctor.user.name,
            a.doctor.specialization,
            t.diagnosis    if t else "",
            t.prescription if t else "",
            t.notes        if t else "",
        ])

    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=treatment_history.csv"}
    )

def _appt_dict(a):
    t = a.treatment
    if isinstance(t, list):
        t = t[0] if t else None

    return {
        "id":           a.id,
        "date":         str(a.date),
        "time_slot":    a.time_slot,
        "status":       a.status,
        "reason":       a.reason or "",
        "doctor_name":  a.doctor.user.name,
        "patient_name": a.patient.user.name,
        "treatment": {
            "diagnosis":    t.diagnosis    if t else "",
            "prescription": t.prescription if t else "",
            "notes":        t.notes        if t else "",
        } if t else None
    }

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)