from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.candidate_profile import CandidateProfile
from app.schemas.candidate import CandidateProfileCreate, CandidateProfileResponse
from app.utils.deps import get_current_user, require_role

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/me/profile", response_model=CandidateProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    body: CandidateProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.candidate)),
):
    existing = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists. Use PUT to update.",
        )

    profile = CandidateProfile(
        user_id=current_user.id,
        full_name=body.full_name,
        phone=body.phone,
        resume_url=body.resume_url,
        skills=body.skills,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/me/profile", response_model=CandidateProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.candidate)),
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Create one first.")
    return profile


@router.put("/me/profile", response_model=CandidateProfileResponse)
def update_profile(
    body: CandidateProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.candidate)),
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Create one first.")

    profile.full_name = body.full_name
    profile.phone = body.phone
    profile.resume_url = body.resume_url
    profile.skills = body.skills

    db.commit()
    db.refresh(profile)
    return profile
