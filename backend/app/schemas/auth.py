from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.candidate


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
