"""Full-text search across photo metadata."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from database import get_db, Photo
from schemas import PhotoListResponse, PhotoResponse

router = APIRouter()


@router.get("", response_model=PhotoListResponse)
def search_photos(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Search photos by title, caption, location, or tagged people."""
    term = f"%{q}%"
    query = (
        db.query(Photo)
        .options(joinedload(Photo.creator))
        .filter(
            Photo.is_active == True,
            or_(
                Photo.title.ilike(term),
                Photo.caption.ilike(term),
                Photo.location.ilike(term),
                Photo.people_tagged.ilike(term),
                Photo.ai_tags.ilike(term),
                Photo.ai_description.ilike(term),
            ),
        )
        .order_by(Photo.avg_rating.desc(), Photo.upload_date.desc())
    )

    total = query.count()
    photos = query.offset((page - 1) * page_size).limit(page_size).all()

    return PhotoListResponse(
        photos=[
            PhotoResponse(
                id=p.id,
                title=p.title,
                caption=p.caption,
                location=p.location,
                people_tagged=p.people_tagged,
                image_url=p.image_url,
                thumbnail_url=p.thumbnail_url,
                file_size=p.file_size,
                width=p.width,
                height=p.height,
                ai_tags=p.ai_tags,
                ai_description=p.ai_description,
                view_count=p.view_count,
                avg_rating=round(p.avg_rating or 0.0, 2),
                rating_count=p.rating_count or 0,
                creator_id=p.creator_id,
                creator=p.creator,
                upload_date=p.upload_date,
            )
            for p in photos
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )
