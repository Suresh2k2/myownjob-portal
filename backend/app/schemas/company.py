from datetime import datetime
from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str
    description: str | None = None
    website: str | None = None
    logo_url: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
