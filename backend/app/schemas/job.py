from datetime import datetime
from pydantic import BaseModel
from app.models.job import JobType


class JobBase(BaseModel):
    title: str
    description: str
    location: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: JobType


class JobCreate(JobBase):
    company_id: int


class JobUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: JobType | None = None
    is_active: bool | None = None


class CompanyBrief(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class JobResponse(JobBase):
    id: int
    company_id: int
    company: CompanyBrief | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    id: int
    company_id: int
    title: str
    location: str | None
    job_type: JobType
    salary_min: float | None
    salary_max: float | None
    company: CompanyBrief | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
