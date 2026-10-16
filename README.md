# Women Safety & Emergency Assistance Platform

A production-grade, full-stack web application designed for personal safety preparedness, rapid emergency assistance coordination, safety education, and administrative incident management.

---

## 🎨 Visual Identity & Color System
The platform strictly follows the approved **Warm Plum + Forest Mint** aesthetic:
- **Primary Deep Warm Plum:** `#734B6D`
- **Success / Resolved Forest Mint:** `#4A8B71`
- **Urgent / SOS Muted Coral:** `#C77366`
- **Backgrounds:** Pure White (`#FFFFFF`), Cream White (`#FDFBFD`), Soft Mint (`#EBF4F0`)
- **Dark Text:** Deep Plum-Black (`#231A22`)
- **Secondary Text:** Light Gray-Purple (`#A2829D`)
- **Borders:** Very Light Gray-Purple (`#E5E0E8`)

---

## 🚀 Key Features

### 1. User Safety Dashboard & Preparedness
- **Dynamic Safety Readiness Score:** Safe preparedness index calculated from emergency contacts, completed checklist items, verified resource reviews, and safety guide readership.
- **Official Disclaimers:** Visible notices explaining that the platform assists preparedness and does not substitute municipal emergency responders.
- **Emergency Contacts:** Prioritized contact directory with trusted responder flags and one-touch calling.
- **Safety Checklist:** Interactive preventative actions with instant completion tracking and progress calculation.

### 2. Connected SOS Emergency Center
- **Two-Step Trigger Confirmation:** Eliminates accidental triggers while enabling rapid deployment.
- **Active Emergency Command Station:** Instant display of 5-step safety protocols, verified nearby safe havens, click-to-dial links for designated contacts, and real-time incident audit logging.
- **Resolution & Cancellation:** Users or administrators can mark alerts as `RESOLVED` (with outcome notes) or `CANCELLED` (false alarm).

### 3. Incident Reporting & Administrative Resolution
- **Confidential Reporting:** Users can log incidents across categories (*Harassment, Suspicious Activity, Unsafe Transportation, Online Harassment, Public Place Safety Issue, Other*) with perceived severity (*LOW, MEDIUM, HIGH*).
- **Administrative Triage:** Dedicated review portal with status progression (*SUBMITTED &rarr; UNDER REVIEW &rarr; RESOLVED &rarr; CLOSED*), timeline logging, and automated user notifications.
- **Data Isolation:** Standard users are strictly restricted to their own reports.

### 4. Verified Emergency Resources Directory
- **Categorized Safe Havens:** Police stations, hospitals, crisis counseling centers, transit outposts, and emergency coordination points.
- **Search & Filtering:** Search by keyword, category, and municipality with GPS coordinates and phone links.

### 5. Administrative Intelligence, Analytics & Reports
- **Real-Time KPIs:** Live database queries for active SOS alerts, pending incidents, registered users, and resource counts.
- **Chart.js Visualizations:** SOS status distributions, incident types, and severity charts using the approved project color palette.
- **Export Engine:** Filterable operational reports with instant CSV, JSON, and printer-ready PDF export.
- **Security Audit Logs:** Comprehensive immutable logging of authentication, alerts, and administrative actions without logging passwords or secrets.

---

## 🛠️ Technology Stack
- **Backend:** Python 3.14 + Flask 3.1 + SQLAlchemy 2.0 (ORM) + SQLite
- **Security:** Scrypt password hashing, session protection, CSRF token validation, role-based decorators (`@login_required`, `@role_required`)
- **Frontend:** Semantic HTML5, Vanilla CSS3 with custom design tokens, JavaScript (ES6+), Chart.js
- **Testing:** Pytest automated test suite

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database & Demo Records
```bash
python scripts/seed_db.py
```

### 3. Run Application
```bash
python run.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

### 4. Default Demonstration Accounts
| Role | Email | Password |
|---|---|---|
| **Administrator** | `admin@womensafety.org` | `Admin@12345` |
| **Standard User** | `user@womensafety.org` | `User@12345` |

---

## 🧪 Running Automated Tests
```bash
pytest -v
```

---

## 📦 Export Project Zip
To generate or update the standalone project archive:
```bash
python scripts/export_zip.py
```
The resulting `womensafety_platform.zip` file will be generated in the root workspace directory.
