from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database import get_db
from app.models.job import Job
from app.models.company import Company
from app.models.user import User, UserRole
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobListResponse
from app.utils.deps import get_current_user, require_role

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[JobListResponse])
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    location: str | None = None,
    job_type: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(Job)
        .options(joinedload(Job.company))
        .filter(Job.is_active == True)
    )

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if search:
        query = query.filter(
            Job.title.ilike(f"%{search}%") | Job.description.ilike(f"%{search}%")
        )

    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = (
        db.query(Job)
        .options(joinedload(Job.company))
        .filter(Job.id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    body: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.recruiter, UserRole.admin)),
):
    company = db.query(Company).filter(Company.id == body.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only post jobs for your own company",
        )

    job = Job(
        company_id=body.company_id,
        title=body.title,
        description=body.description,
        location=body.location,
        salary_min=body.salary_min,
        salary_max=body.salary_max,
        job_type=body.job_type,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return db.query(Job).options(joinedload(Job.company)).filter(Job.id == job.id).first()


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    body: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.recruiter, UserRole.admin)),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    company = db.query(Company).filter(Company.id == job.company_id).first()
    if company.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update jobs for your own company",
        )

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return db.query(Job).options(joinedload(Job.company)).filter(Job.id == job.id).first()


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.recruiter, UserRole.admin)),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    company = db.query(Company).filter(Company.id == job.company_id).first()
    if company.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete jobs for your own company",
        )

    db.delete(job)
    db.commit()
