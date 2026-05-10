"""Authentication endpoints: register (consumer), login, me."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db, User, UserRole as DBUserRole
from schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from auth_utils import hash_password, verify_password, create_access_token, get_current_user
from config import settings

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new consumer account (public endpoint)."""
    # Check uniqueness
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Only allow consumer self-registration; creators are created by admin
    role = DBUserRole.consumer

    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        display_name=request.display_name or request.username,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        data={"sub": user.id, "role": user.role.value},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """Login and receive JWT token."""
    user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.username)
    ).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    token = create_access_token(
        data={"sub": user.id, "role": user.role.value},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)
