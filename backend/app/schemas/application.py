from datetime import datetime
from pydantic import BaseModel, model_validator
from app.models.application import ApplicationStatus


class CompanyBrief(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class JobBrief(BaseModel):
    id: int
    title: str
    location: str | None = None
    company: CompanyBrief | None = None
    model_config = {"from_attributes": True}


class CandidateBrief(BaseModel):
    id: int
    full_name: str
    email: str | None = None
    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_email(cls, data):
        if hasattr(data, "user") and data.user is not None:
            return {"id": data.id, "full_name": data.full_name, "email": data.user.email}
        return data


class ApplicationCreate(BaseModel):
    job_id: int
    cover_letter: str | None = None


class ApplicationResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    cover_letter: str | None
    status: ApplicationStatus
    applied_at: datetime
    job: JobBrief | None = None
    candidate: CandidateBrief | None = None

    model_config = {"from_attributes": True}


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
