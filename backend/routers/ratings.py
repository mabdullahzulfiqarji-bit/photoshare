"""Ratings endpoints: rate a photo (1-5 stars)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db, Rating, Photo, User
from schemas import RatingCreateRequest, RatingResponse
from auth_utils import get_current_user

router = APIRouter()


@router.post("/{photo_id}", response_model=RatingResponse)
def rate_photo(
    photo_id: int,
    request: RatingCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rate a photo (1-5). Re-rating updates the existing rating."""
    photo = db.query(Photo).filter(Photo.id == photo_id, Photo.is_active == True).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Upsert rating
    existing = db.query(Rating).filter(
        Rating.photo_id == photo_id,
        Rating.user_id == current_user.id,
    ).first()

    if existing:
        existing.score = request.score
        rating = existing
    else:
        rating = Rating(photo_id=photo_id, user_id=current_user.id, score=request.score)
        db.add(rating)

    db.flush()

    # Recalculate photo average
    stats = (
        db.query(func.avg(Rating.score), func.count(Rating.id))
        .filter(Rating.photo_id == photo_id)
        .first()
    )
    photo.avg_rating = round(float(stats[0] or 0), 2)
    photo.rating_count = stats[1] or 0

    db.commit()
    db.refresh(rating)
    return RatingResponse.model_validate(rating)


@router.delete("/{photo_id}", status_code=204)
def remove_rating(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove your rating from a photo."""
    rating = db.query(Rating).filter(
        Rating.photo_id == photo_id,
        Rating.user_id == current_user.id,
    ).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    db.delete(rating)
    db.flush()

    # Recalculate
    stats = (
        db.query(func.avg(Rating.score), func.count(Rating.id))
        .filter(Rating.photo_id == photo_id)
        .first()
    )
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        photo.avg_rating = round(float(stats[0] or 0), 2)
        photo.rating_count = stats[1] or 0

    db.commit()
