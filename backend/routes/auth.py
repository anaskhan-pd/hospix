from flask import jsonify, Blueprint, request, session
from models.user import User
from models.patient import Patient
from extensions import db , cache
from functools import wraps

auth_bp = Blueprint('auth', __name__)


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return jsonify({"error": "Please Login"}), 401
            if session.get("user_role") not in roles:
                return jsonify({"error": "Unauthorised Access"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


@auth_bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    name    = data.get("name", "").strip()
    email   = data.get("email", "").strip().lower()
    password = data.get("password", "")
    age     = data.get("age")
    gender  = data.get("gender", "")
    contact = data.get("contact", "")
    address = data.get("address", "")

    if not all([name, email, password, age, gender, contact, address]):
        return jsonify({"error": "Please Fill All Fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(name=name, email=email, role="patient")
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    patient = Patient(
        user_id=user.id, age=int(age),
        gender=gender, contact=contact, address=address
    )
    db.session.add(patient)
    db.session.commit()
    cache.delete("admin_dashboard")

    return jsonify({"message": "Registration successful"}), 201


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data     = request.get_json()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"success": False, "message": "Invalid email ID or password"}), 401

    if not user.is_active:
        return jsonify({"success": False, "message": "Deactivated Account"}), 403

    session["user_id"]   = user.id
    session["user_role"] = user.role
    session["user_name"] = user.name

    return jsonify({"success": True, "role": user.role, "name": user.name})


@auth_bp.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@auth_bp.route("/api/check-session")
def check_session():
    if "user_id" in session:
        return jsonify({
            "loggedIn": True,
            "role": session["user_role"],
            "name": session["user_name"],
            "user_id": session["user_id"]
        })
    return jsonify({"loggedIn": False})