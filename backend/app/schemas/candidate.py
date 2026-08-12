from datetime import datetime
from pydantic import BaseModel


class CandidateProfileBase(BaseModel):
    full_name: str
    phone: str | None = None
    resume_url: str | None = None
    skills: str | None = None


class CandidateProfileCreate(CandidateProfileBase):
    pass


class CandidateProfileResponse(CandidateProfileBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
