import os, csv, io, smtplib
from celery import Celery
from celery.schedules import crontab
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

celery = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery.conf.beat_schedule = {
    "daily-reminders": {
        "task":     "tasks.send_daily_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
    "monthly-reports": {
        "task":     "tasks.send_monthly_reports",
        "schedule": crontab(hour=7, minute=0, day_of_month=1),
    },
}
celery.conf.timezone = "Asia/Kolkata"


def get_app():
    from app import app
    return app

def send_email(to_addr, subject, html_body, attachment=None, filename=None):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = "hms@hospix.local"
    msg["To"]      = to_addr
    msg.attach(MIMEText(html_body, "html"))

    if attachment and filename:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
        msg.attach(part)

    with smtplib.SMTP("localhost", 1025) as s:
        s.sendmail("hms@hospix.local", to_addr, msg.as_string())


@celery.task(name="tasks.send_daily_reminders")
def send_daily_reminders():
    app = get_app()
    with app.app_context():
        from models.appointment import Appointment
        from datetime import date
        today = date.today()
        appts = Appointment.query.filter_by(date=today, status="booked").all()
        for a in appts:
            html = f"""
            <h2>Appointment Reminder — Hospix HMS</h2>
            <p>Dear <strong>{a.patient.user.name}</strong>,</p>
            <p>This is a reminder that you have an appointment
               <strong>today at {a.time_slot}</strong>
               with <strong>Dr. {a.doctor.user.name}</strong>
               ({a.doctor.specialization}).</p>
            <p>Please arrive 10 minutes before your scheduled time.</p>
            <p>— Hospix Hospital Management System</p>
            """
            send_email(
                a.patient.user.email,
                "Reminder: Your Appointment Today",
                html
            )


@celery.task(name="tasks.send_monthly_reports")
def send_monthly_reports():
    app = get_app()
    with app.app_context():
        from models.doctor import Doctor
        from models.appointment import Appointment
        from datetime import date, timedelta
        import calendar

        today    = date.today()
        first    = today.replace(day=1)
        prev     = (first - timedelta(days=1)).replace(day=1)
        last_day = calendar.monthrange(prev.year, prev.month)[1]
        prev_end = prev.replace(day=last_day)

        for doc in Doctor.query.all():
            appts = Appointment.query.filter(
                Appointment.doctor_id == doc.id,
                Appointment.date     >= prev,
                Appointment.date     <= prev_end,
                Appointment.status   == "completed"
            ).all()

            rows = "".join(f"""
              <tr>
                <td>{a.patient.user.name}</td>
                <td>{a.date}</td>
                <td>{a.treatment.diagnosis    if a.treatment else 'N/A'}</td>
                <td>{a.treatment.prescription if a.treatment else 'N/A'}</td>
              </tr>""" for a in appts)

            html = f"""
            <h2>Monthly Activity Report — {prev.strftime('%B %Y')}</h2>
            <p>Dr. {doc.user.name} | {doc.specialization}</p>
            <p>Total completed appointments: <strong>{len(appts)}</strong></p>
            <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse">
              <thead>
                <tr>
                  <th>Patient</th>
                  <th>Date</th>
                  <th>Diagnosis</th>
                  <th>Prescription</th>
                </tr>
              </thead>
              <tbody>
                {rows or '<tr><td colspan="4">No completed appointments this month.</td></tr>'}
              </tbody>
            </table>
            <p style="margin-top:20px;color:#888">— Hospix Hospital Management System</p>
            """

            send_email(
                doc.user.email,
                f"Monthly Report — {prev.strftime('%B %Y')}",
                html
            )


@celery.task(name="tasks.export_patient_csv")
def export_patient_csv(patient_id, patient_email):
    app = get_app()
    with app.app_context():
        from models.appointment import Appointment
        appts = Appointment.query.filter_by(
            patient_id=patient_id,
            status="completed"
        ).order_by(Appointment.date).all()

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            "Date", "Doctor", "Specialization",
            "Diagnosis", "Prescription", "Notes"
        ])
        for a in appts:
            t = a.treatment
            writer.writerow([
                a.date,
                a.doctor.user.name,
                a.doctor.specialization,
                t.diagnosis    if t else "",
                t.prescription if t else "",
                t.notes        if t else "",
            ])

        send_email(
            patient_email,
            "Your Treatment History Export — Hospix",
            "<p>Please find your treatment history CSV attached.</p>",
            attachment=buf.getvalue().encode("utf-8"),
            filename="treatment_history.csv"
        )