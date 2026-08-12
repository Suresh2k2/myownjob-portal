import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

# Import ALL models so Base.metadata knows about every table
from app.models.user import User, UserRole  # noqa: F401
from app.models.candidate_profile import CandidateProfile  # noqa: F401
from app.models.company import Company  # noqa: F401
from app.models.job import Job, JobType  # noqa: F401
from app.models.application import Application, ApplicationStatus  # noqa: F401

from app.utils.security import hash_password
from app.utils.jwt import create_access_token, create_refresh_token

# In-memory SQLite with StaticPool ensures all connections share the same DB
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """Provide a clean database session for direct model operations."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    """Provide a test client that uses the test database."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# --- Helpers ---

def create_user(db, email="test@test.com", password="secret123", role=UserRole.candidate):
    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_token(user_id):
    return create_access_token({"sub": user_id})


def get_refresh_token(user_id):
    return create_refresh_token({"sub": user_id})


# --- User Fixtures ---

@pytest.fixture()
def candidate_user(db):
    return create_user(db, email="candidate@test.com", role=UserRole.candidate)


@pytest.fixture()
def recruiter_user(db):
    return create_user(db, email="recruiter@test.com", role=UserRole.recruiter)


@pytest.fixture()
def other_candidate(db):
    return create_user(db, email="other@test.com", role=UserRole.candidate)


@pytest.fixture()
def candidate_token(candidate_user):
    return get_token(candidate_user.id)


@pytest.fixture()
def recruiter_token(recruiter_user):
    return get_token(recruiter_user.id)


@pytest.fixture()
def other_token(other_candidate):
    return get_token(other_candidate.id)


# --- Profile Fixtures ---

@pytest.fixture()
def candidate_profile(db, candidate_user):
    profile = CandidateProfile(
        user_id=candidate_user.id,
        full_name="Jane Doe",
        phone="555-0100",
        skills="Python, FastAPI",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@pytest.fixture()
def other_profile(db, other_candidate):
    profile = CandidateProfile(
        user_id=other_candidate.id,
        full_name="John Smith",
        phone="555-0200",
        skills="React, TypeScript",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


# --- Company Fixtures ---

@pytest.fixture()
def company(db, recruiter_user):
    co = Company(
        owner_id=recruiter_user.id,
        name="Acme Corp",
        description="Best tech company",
    )
    db.add(co)
    db.commit()
    db.refresh(co)
    return co


# --- Job Fixtures ---

@pytest.fixture()
def job(db, company):
    j = Job(
        company_id=company.id,
        title="Python Developer",
        description="Build APIs with FastAPI",
        location="Remote",
        job_type=JobType.full_time,
        salary_min=80000,
        salary_max=120000,
    )
    db.add(j)
    db.commit()
    db.refresh(j)
    return j


@pytest.fixture()
def closed_job(db, company):
    j = Job(
        company_id=company.id,
        title="Closed Position",
        description="This job is closed",
        job_type=JobType.contract,
        is_active=False,
    )
    db.add(j)
    db.commit()
    db.refresh(j)
    return j
