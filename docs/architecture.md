# System Architecture & Technical Specifications

## 1. Architectural Layers

The Women Safety & Emergency Assistance Platform implements a clean layered architecture:

```text
[ Web Browser Client ]
        │  (HTTP / JSON / HTML5)
        ▼
[ Flask Presentation Routes & Blueprints ]
   ├─ Main & Static Views
   ├─ Authentication (Session & CSRF Protection)
   ├─ User Dashboard & Profile
   ├─ Emergency SOS Center
   ├─ Emergency Contacts & Safe Havens
   ├─ Incident Reporting Portal
   ├─ Safety Education & Checklist
   ├─ Notifications Engine
   └─ Admin Command Center, Analytics & Reporting
        │
        ▼
[ Security & Validation Interceptors ]
   ├─ CSRF Token Middleware
   ├─ Role-Based Access Control (@role_required)
   └─ Strict Input Validators
        │
        ▼
[ Business Logic Services Layer ]
   ├─ AuthService
   ├─ SOSService
   ├─ IncidentService
   ├─ ReadinessService
   ├─ AnalyticsService
   └─ ReportService
        │
        ▼
[ Repositories Layer (Data Access Abstraction) ]
   ├─ UserRepository & ContactRepository
   ├─ SOSRepository & IncidentRepository
   ├─ ResourceRepository & TipRepository
   ├─ ChecklistRepository & NotificationRepository
   └─ AuditRepository
        │
        ▼
[ SQLAlchemy 2.0 ORM & SQLite Relational Database ]
   (Enforced Foreign Keys, Indexed Statuses, UTC Timestamps)
```

## 2. Emergency SOS State Machine

```text
[ IDLE / STANDBY ]
        │
        ▼  (User Confirms SOS Activation)
[ ACTIVE ] ────► Dispatches Notifications & Logs Security Audit
        │        Displays Emergency Guidance & One-Touch Contacts
        │
        ├──────────────────────┬──────────────────────┐
        ▼                      ▼                      ▼
 [ RESOLVED by User ]   [ RESOLVED by Admin ]   [ CANCELLED (False Alarm) ]
```

## 3. Safety Readiness Score Formula
The Safety Readiness Score \(S \in [0, 100]\) is calculated deterministically:
\[
S = S_{\text{contacts}} + S_{\text{checklist}} + S_{\text{tips}} + S_{\text{profile}}
\]
Where:
- \(S_{\text{contacts}} \le 30\): Up to 25 points for adding contacts, plus a 5-point bonus for having at least 1 trusted contact.
- \(S_{\text{checklist}} \le 40\): Proportional to completed items in the safety preparation checklist.
- \(S_{\text{tips}} \le 15\): 3 points per unique safety guide viewed.
- \(S_{\text{profile}} \le 15\): Completion of non-sensitive location and phone fields.
