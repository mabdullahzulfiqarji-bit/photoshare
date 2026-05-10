"""User profile endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, User
from schemas import UserResponse, UserUpdateRequest
from auth_utils import get_current_user

router = APIRouter()


@router.get("/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    update: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)
