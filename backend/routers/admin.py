"""Admin-only endpoints: creator account management and platform stats."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db, User, Photo, Comment, Rating, UserRole as DBUserRole
from schemas import CreatorCreateRequest, UserResponse, StatsResponse, PhotoResponse
from auth_utils import get_current_admin, hash_password

router = APIRouter()


@router.post("/creators", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_creator_account(
    request: CreatorCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Admin: create a creator account (no public self-registration for creators)."""
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        display_name=request.display_name or request.username,
        role=DBUserRole.creator,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Admin: list all users."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [UserResponse.model_validate(u) for u in users]


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Admin: deactivate a user account."""
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()


@router.get("/stats", response_model=StatsResponse)
def get_platform_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Admin: platform-wide statistics."""
    from sqlalchemy.orm import joinedload
    
    total_photos = db.query(func.count(Photo.id)).filter(Photo.is_active == True).scalar()
    total_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    total_comments = db.query(func.count(Comment.id)).scalar()
    total_ratings = db.query(func.count(Rating.id)).scalar()

    top_photo = (
        db.query(Photo)
        .options(joinedload(Photo.creator))
        .filter(Photo.is_active == True, Photo.rating_count > 0)
        .order_by(Photo.avg_rating.desc())
        .first()
    )

    top_rated_photo = None
    if top_photo:
        top_rated_photo = PhotoResponse(
            id=top_photo.id,
            title=top_photo.title,
            caption=top_photo.caption,
            location=top_photo.location,
            people_tagged=top_photo.people_tagged,
            image_url=top_photo.image_url,
            thumbnail_url=top_photo.thumbnail_url,
            file_size=top_photo.file_size,
            width=top_photo.width,
            height=top_photo.height,
            ai_tags=top_photo.ai_tags,
            ai_description=top_photo.ai_description,
            view_count=top_photo.view_count,
            avg_rating=round(top_photo.avg_rating or 0.0, 2),
            rating_count=top_photo.rating_count or 0,
            creator_id=top_photo.creator_id,
            creator=top_photo.creator,
            upload_date=top_photo.upload_date,
        )

    return StatsResponse(
        total_photos=total_photos or 0,
        total_users=total_users or 0,
        total_comments=total_comments or 0,
        total_ratings=total_ratings or 0,
        top_rated_photo=top_rated_photo,
    )


@router.post("/seed", status_code=201)
def seed_admin(db: Session = Depends(get_db)):
    """
    ONE-TIME: Seed the default admin account.
    Remove or protect this endpoint in production!
    Credentials: admin / Admin@1234
    """
    if db.query(User).filter(User.username == "admin").first():
        return {"message": "Admin already exists"}

    admin = User(
        username="admin",
        email="admin@photoshare.app",
        hashed_password=hash_password("Admin@1234"),
        display_name="Platform Admin",
        role=DBUserRole.admin,
    )
    db.add(admin)
    db.commit()
    return {"message": "Admin account created", "username": "admin", "password": "Admin@1234"}
