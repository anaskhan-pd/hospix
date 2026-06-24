# Hospix
Modern Healthcare Operations Platform

A modern, SaaS-inspired hospital management platform designed to streamline operations, appointment scheduling, and patient workflows.

---

## Screenshots

| Landing Page (Light) | Landing Page (Dark) |
|:---:|:---:|
| ![Landing Page Light Placeholder](#) | ![Landing Page Dark Placeholder](#) |

| Dashboard (Light) | Dashboard (Dark) |
|:---:|:---:|
| ![Dashboard Light Placeholder](#) | ![Dashboard Dark Placeholder](#) |

*(Add screenshots by replacing the placeholder links above)*

---

## Features

- **Light & Dark Theme** — Seamless theme toggling on the landing page
- **Patient Management** — View and manage complete patient profiles and treatment histories
- **Appointment Scheduling** — Smart scheduling with real-time doctor availability and conflict detection
- **Doctor Management** — Dedicated views for doctors to manage schedules, update diagnoses, and write prescriptions
- **Analytics Dashboard** — Centralized overview of hospital operations, staff allocation, and departments
- **Secure Authentication** — Role-based access control (RBAC) with distinct portals for Admins, Doctors, and Patients
- **Smooth User Experience** — Background jobs automate daily email reminders and monthly performance reports
- **Performance Caching** — Redis-backed caching for rapid API responses
- **Responsive Design** — Custom, premium SaaS-inspired design system 

---

## Tech Stack

| Component | Technology |
|---|---|
| **Backend** | Python Flask |
| **Frontend** | Vue.js 3 (CDN), Custom CSS (Design System) |
| **Database** | SQLite via SQLAlchemy ORM |
| **Caching** | Redis (Flask-Caching) |
| **Background Jobs** | Celery + Redis |
| **Email Testing** | MailHog |
| **Version Control** | Git |

---

## Project Structure

```text
hospital-management-system/
├── backend/
│   ├── app.py              # Main Flask app & API routes
│   ├── config.py           # Application configurations
│   ├── extensions.py       # SQLAlchemy & Cache instances
│   ├── tasks.py            # Celery background jobs
│   ├── models/             # Database ORM models
│   │   ├── appointment.py  
│   │   ├── department.py   
│   │   ├── doctor.py       
│   │   ├── patient.py      
│   │   ├── treatment.py    
│   │   └── user.py         
│   ├── routes/
│   │   └── auth.py         # Authentication logic
│   └── utils/
│       └── admin.py        # Admin seeder script
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   ├── landing.css # Landing page styling
│   │   │   └── style.css   # Dashboard design system
│   │   └── js/
│   │       ├── admin.js    # Admin portal logic
│   │       ├── app.js      # Global Vue application logic
│   │       ├── doctor.js   # Doctor portal logic
│   │       ├── landing.js  # Landing interactions
│   │       └── patient.js  # Patient portal logic
│   └── templates/
│       ├── index.html      # Vue dashboard entrypoint
│       └── landing.html    # Pre-auth landing page
└── README.md
```

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/hospix.git
cd hospix
```

### 2. Create and activate a virtual environment
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```
**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install requirements
```bash
pip install -r backend/requirements.txt
```

### 4. Start supporting services (Docker)
You need Redis for caching/Celery, and MailHog for testing emails.
```bash
docker run -d -p 6379:6379 --name redis-hms redis
docker run -d -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog
```

### 5. Run the application
Open 3 separate terminals within the `backend/` directory:

**Terminal 1 — Flask Server:**
```bash
python app.py
```

**Terminal 2 — Celery Worker:**
```bash
python -m celery -A tasks:celery worker --loglevel=info --pool=solo
```

**Terminal 3 — Celery Beat Scheduler:**
```bash
python -m celery -A tasks:celery beat --loglevel=info
```

---

## Usage

Once the servers are running, access the application:

1. **Web Application:** Navigate to `http://localhost:5000`
2. **MailHog Inbox:** Navigate to `http://localhost:8025` (To view sent reminders and reports)

**Default Admin Credentials:**
- **Email:** `admin@hospix.in`
- **Password:** `admin@123`

Patients can self-register from the login page. Doctors must be added by an Admin.

---

## Design Philosophy

Hospix intentionally moves away from traditional, bulky enterprise software interfaces. It implements a modern SaaS-inspired design language—drawing heavy inspiration from industry leaders like Linear, Stripe, and Vercel. 

Key design elements include:
- Minimalist, distraction-free layouts
- Purpose-driven typography
- Subtle micro-interactions and smooth keyframe animations
- A comprehensive custom CSS design system tailored for healthcare usability without sacrificing aesthetic quality.

---

## Future Improvements

- [ ] Email notifications
- [ ] Multi-hospital support
- [ ] AI appointment assistant
- [ ] Advanced analytics
- [ ] PWA support

---

## Contributing

Contributions are welcome! If you'd like to improve Hospix, please follow these steps:
1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

---

## License

This project is licensed under the [MIT License](LICENSE).