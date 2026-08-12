from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import Base, engine, verify_db_connection
from app.routers import jobs, auth, users, companies, candidates, applications

settings = get_settings()

app = FastAPI(
    title="Job Portal API",
    description="Job Portal & Application Tracker API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(companies.router, prefix="/api/v1")
app.include_router(candidates.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    verify_db_connection()


@app.get("/")
def root():
    return {"message": "Job Portal API", "docs": "/docs"}


@app.get("/health")
def health():
    db_ok = verify_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
    }
