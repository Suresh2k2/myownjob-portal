from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User, UserRole
from app.models.candidate_profile import CandidateProfile
from app.models.job import Job
from app.models.company import Company
from app.models.application import Application, ApplicationStatus
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationStatusUpdate
from app.utils.deps import get_current_user, require_role

router = APIRouter(prefix="/applications", tags=["applications"])

ALLOWED_TRANSITIONS: dict[ApplicationStatus, list[ApplicationStatus]] = {
    ApplicationStatus.pending: [ApplicationStatus.reviewed, ApplicationStatus.shortlisted, ApplicationStatus.accepted, ApplicationStatus.rejected],
    ApplicationStatus.reviewed: [ApplicationStatus.shortlisted, ApplicationStatus.accepted, ApplicationStatus.rejected],
    ApplicationStatus.shortlisted: [ApplicationStatus.accepted, ApplicationStatus.rejected],
    ApplicationStatus.rejected: [],
    ApplicationStatus.accepted: [],
}


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    body: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.candidate)),
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create a candidate profile first",
        )

    job = db.query(Job).filter(Job.id == body.job_id, Job.is_active == True).first()
    if not job:
        raise HTTPException(status_code=404, detail="Active job not found")

    existing = (
        db.query(Application)
        .filter(Application.candidate_id == profile.id, Application.job_id == body.job_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied to this job",
        )

    application = Application(
        candidate_id=profile.id,
        job_id=body.job_id,
        cover_letter=body.cover_letter,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return (
        db.query(Application)
        .options(joinedload(Application.job).joinedload(Job.company))
        .filter(Application.id == application.id)
        .first()
    )


@router.get("/me", response_model=list[ApplicationResponse])
def list_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.candidate)),
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        return []

    return (
        db.query(Application)
        .options(joinedload(Application.job).joinedload(Job.company))
        .filter(Application.candidate_id == profile.id)
        .order_by(Application.applied_at.desc())
        .all()
    )


@router.get("/job/{job_id}", response_model=list[ApplicationResponse])
def list_job_applications(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.recruiter, UserRole.admin)),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    company = db.query(Company).filter(Company.id == job.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view applications for your own company's jobs",
        )

    return (
        db.query(Application)
        .options(
            joinedload(Application.candidate).joinedload(CandidateProfile.user)
        )
        .filter(Application.job_id == job_id)
        .order_by(Application.applied_at.desc())
        .all()
    )


@router.put("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    body: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.recruiter, UserRole.admin)),
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    job = db.query(Job).filter(Job.id == application.job_id).first()
    company = db.query(Company).filter(Company.id == job.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if company.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update applications for your own company's jobs",
        )

    allowed = ALLOWED_TRANSITIONS.get(application.status, [])
    if body.status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from '{application.status.value}' to '{body.status.value}'",
        )

    application.status = body.status
    db.commit()
    db.refresh(application)
    return (
        db.query(Application)
        .options(joinedload(Application.job).joinedload(Job.company))
        .filter(Application.id == application.id)
        .first()
    )
