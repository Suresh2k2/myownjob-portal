# Job Portal & Application Tracker

A full-stack job portal and application tracking platform built with **FastAPI, React, MySQL, SQLAlchemy, and JWT authentication**.

The platform supports two types of users:

- **Job Seekers** — browse jobs, apply for positions, manage profiles, upload resumes, and track applications.
- **Recruiters** — create company profiles, post jobs, view applicants, and manage application status.

---

## ✨ Features

### 👨‍💼 Job Seekers

- Create an account and securely log in
- Manage personal profile
- Add skills and contact information
- Upload and view resume
- Browse available jobs
- Search and explore job opportunities
- View job details
- Apply for jobs
- Track submitted applications
- View application status:
  - Pending
  - Accepted
  - Rejected

### 🏢 Recruiters

- Recruiter registration and authentication
- Create and manage company information
- Post new job openings
- View jobs posted by the recruiter
- View applicants for each job
- Review candidate profiles
- View candidate resume
- Accept applications
- Reject applications
- Manage applicant status

### 🔐 Authentication & Security

- JWT-based authentication
- Password hashing
- Role-based access control
- Protected API endpoints
- Recruiter-only job management
- Job-seeker-only application functionality
- Backend authorization for applicant management

---

## 🛠️ Tech Stack

### Backend

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0
- Pydantic v2
- Alembic
- MySQL 8.x
- Python-JOSE
- Passlib

### Frontend

- React 18
- Vite
- React Router v6
- Axios
- CSS

### Database

- MySQL 8.x
- SQLAlchemy ORM
- Alembic migrations

---

## 📁 Project Structure

```text
job-portal/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── database/
│   │   └── core/
│   │
│   ├── alembic/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── context/
│   │   └── App.jsx
│   │
│   ├── package.json
│   └── .env.example
│
├── docs/
│   └── schema.sql
│
├── .gitignore
└── README.md
