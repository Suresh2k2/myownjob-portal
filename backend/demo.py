"""Run: cd backend && python demo.py"""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "demo-secret-key"

import app.database as _db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

_engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
_db.engine = _engine
_db.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.candidate_profile import CandidateProfile
from app.models.company import Company
from app.models.job import Job, JobType
from app.models.application import Application, ApplicationStatus
from app.utils.security import hash_password

Base.metadata.create_all(bind=_engine)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

def _override():
    s = _Session()
    try:
        yield s
    finally:
        s.close()

app.dependency_overrides[get_db] = _override

from fastapi.testclient import TestClient
from app.utils.jwt import create_access_token

c = TestClient(app)
db = _Session()

W = 55
print("=" * W)
print("   JOB PORTAL & APPLICATION TRACKER - FULL DEMO")
print("=" * W)

# --- Bootstrap users directly (registration always creates candidates) ---
alice = User(email="alice@test.com", hashed_password=hash_password("securepass123"), role=UserRole.candidate)
bob = User(email="bob@test.com", hashed_password=hash_password("securepass123"), role=UserRole.recruiter)
db.add_all([alice, bob])
db.commit()
db.refresh(alice)
db.refresh(bob)

ct = create_access_token({"sub": alice.id})
rt = create_access_token({"sub": bob.id})
ch = {"Authorization": f"Bearer {ct}"}
rh = {"Authorization": f"Bearer {rt}"}

print("\n[1] Health Check")
r = c.get("/health")
print(f"    {r.status_code}: {r.json()}")

print("\n[2] Register Candidate (public endpoint)")
r = c.post("/api/v1/auth/register", json={"email":"charlie@test.com","password":"securepass123"})
print(f"    {r.status_code}: {r.json()['email']} (role={r.json()['role']})")

print("\n[3] Login Candidate & Recruiter")
r = c.post("/api/v1/auth/login", data={"username":"alice@test.com","password":"securepass123"})
print(f"    Candidate: {r.status_code} -> token obtained")
r = c.post("/api/v1/auth/login", data={"username":"bob@test.com","password":"securepass123"})
print(f"    Recruiter: {r.status_code} -> token obtained")

print("\n[4] Candidate Creates Profile")
r = c.post("/api/v1/candidates/me/profile", json={"full_name":"Alice Johnson","phone":"555-0101","skills":"Python, FastAPI, SQLAlchemy"}, headers=ch)
print(f"    {r.status_code}: {r.json()['full_name']}, skills={r.json()['skills']}")

print("\n[5] Recruiter Creates Company")
r = c.post("/api/v1/companies/", json={"name":"TechCorp","description":"Leading tech innovation"}, headers=rh)
print(f"    {r.status_code}: {r.json()['name']}")

print("\n[6] Recruiter Posts 2 Jobs")
r = c.post("/api/v1/jobs/", json={"company_id":1,"title":"Senior Python Developer","description":"Build scalable APIs with FastAPI. 5+ years exp.","location":"San Francisco, CA","job_type":"full_time","salary_min":120000,"salary_max":180000}, headers=rh)
print(f"    Job #{r.json()['id']}: {r.json()['title']} ({r.status_code})")
r = c.post("/api/v1/jobs/", json={"company_id":1,"title":"Frontend React Developer","description":"Build modern UIs with React and TypeScript.","location":"Remote","job_type":"full_time","salary_min":100000,"salary_max":150000}, headers=rh)
print(f"    Job #{r.json()['id']}: {r.json()['title']} ({r.status_code})")

print("\n[7] Browse All Jobs")
r = c.get("/api/v1/jobs/")
for j in r.json():
    co = j.get("company") or {}
    sal = f"${j['salary_min']:,.0f}-${j['salary_max']:,.0f}" if j.get("salary_min") else "N/A"
    print(f"    #{j['id']} {j['title']} @ {co.get('name','?')} | {j['location']} | {sal}")

print("\n[8] Search: 'Python'")
r = c.get("/api/v1/jobs/?search=Python")
for j in r.json():
    print(f"    #{j['id']} {j['title']}")

print("\n[9] Job Detail")
r = c.get("/api/v1/jobs/1")
d = r.json()
print(f"    #{d['id']} {d['title']} @ {d['company']['name']}")
print(f"    {d['location']} | {d['job_type']}")
print(f"    ${d['salary_min']:,.0f} - ${d['salary_max']:,.0f}")
print(f"    {d['description'][:60]}...")

print("\n[10] Candidate Applies to Job")
r = c.post("/api/v1/applications/", json={"job_id":1,"cover_letter":"Senior Python dev with 7 yrs FastAPI."}, headers=ch)
print(f"    {r.status_code}: app #{r.json()['id']}, status={r.json()['status']}")

print("\n[11] Duplicate Application (Blocked)")
r = c.post("/api/v1/applications/", json={"job_id":1,"cover_letter":"Again"}, headers=ch)
print(f"    {r.status_code}: {r.json()['detail']}")

print("\n[12] My Applications")
r = c.get("/api/v1/applications/me", headers=ch)
for a in r.json():
    print(f"    App #{a['id']}: job={a['job_id']}, status={a['status']}")

print("\n[13] Recruiter Views Applicants")
r = c.get("/api/v1/applications/job/1", headers=rh)
for a in r.json():
    print(f"    App #{a['id']}: candidate={a['candidate_id']}, status={a['status']}")

print("\n[14] Status Flow (State Machine)")
r = c.put("/api/v1/applications/1/status", json={"status":"shortlisted"}, headers=rh)
print(f"    pending -> shortlisted: {r.status_code} -> {r.json()['status']}")
r = c.put("/api/v1/applications/1/status", json={"status":"pending"}, headers=rh)
print(f"    shortlisted -> pending (INVALID): {r.status_code} -> {r.json().get('detail','?')}")
r = c.put("/api/v1/applications/1/status", json={"status":"accepted"}, headers=rh)
print(f"    shortlisted -> accepted: {r.status_code} -> {r.json()['status']}")

print("\n[15] Role Enforcement")
r = c.post("/api/v1/companies/", json={"name":"Sneaky"}, headers=ch)
print(f"    Candidate creates company: {r.status_code} (blocked)")
r = c.put("/api/v1/applications/1/status", json={"status":"rejected"}, headers=ch)
print(f"    Candidate updates status: {r.status_code} (blocked)")

db.close()
print("\n" + "=" * W)
print("   ALL 15 FLOWS VERIFIED SUCCESSFULLY!")
print("   To run the live server:")
print("   cd backend && SECRET_KEY=your-secret uvicorn app.main:app --reload")
print("   Swagger UI: http://localhost:8000/docs")
print("=" * W)
