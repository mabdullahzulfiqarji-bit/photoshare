"""Photo endpoints: upload (creator), list, get, update, delete.

IMPORTANT: Static routes (/upload, /my) MUST be registered before
dynamic routes (/{photo_id}) to avoid FastAPI matching 'my' as an ID.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session, joinedload
from typing import Optional
import json

from database import get_db, Photo, User, Rating
from schemas import PhotoResponse, PhotoListResponse, PhotoUpdateRequest
from auth_utils import get_current_user, get_current_creator, get_optional_user
from storage_service import storage_service
from ai_service import ai_service
from config import settings

router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def _photo_to_response(photo: Photo, user_rating: Optional[int] = None) -> PhotoResponse:
    return PhotoResponse(
        id=photo.id,
        title=photo.title,
        caption=photo.caption,
        location=photo.location,
        people_tagged=photo.people_tagged,
        image_url=photo.image_url,
        thumbnail_url=photo.thumbnail_url,
        file_size=photo.file_size,
        width=photo.width,
        height=photo.height,
        ai_tags=photo.ai_tags,
        ai_description=photo.ai_description,
        view_count=photo.view_count or 0,
        avg_rating=round(photo.avg_rating or 0.0, 2),
        rating_count=photo.rating_count or 0,
        creator_id=photo.creator_id,
        creator=photo.creator,
        upload_date=photo.upload_date,
        user_rating=user_rating,
    )


@router.post("/upload", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    title: str = Form(...),
    caption: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    people_tagged: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_creator),
):
    """Upload a photo - creator only."""
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Use JPG, PNG, GIF or WebP.")

    file_data = await file.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(file_data) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max {settings.MAX_FILE_SIZE_MB}MB.")
    if len(file_data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        image_url, thumbnail_url, blob_name, width, height = storage_service.upload_photo(
            file_data=file_data,
            filename=file.filename or "photo.jpg",
            content_type=content_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")

    ai_tags_json = "[]"
    ai_description = ""
    try:
        tags, description = ai_service.analyze_image(image_url)
        ai_tags_json = json.dumps(tags)
        ai_description = description
    except Exception:
        pass

    photo = Photo(
        title=title,
        caption=caption,
        location=location,
        people_tagged=people_tagged,
        image_url=image_url,
        thumbnail_url=thumbnail_url,
        blob_name=blob_name,
        file_size=len(file_data),
        width=width,
        height=height,
        ai_tags=ai_tags_json,
        ai_description=ai_description,
        creator_id=current_user.id,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)

    photo = db.query(Photo).options(joinedload(Photo.creator)).filter(Photo.id == photo.id).first()
    return _photo_to_response(photo)


@router.get("", response_model=PhotoListResponse)
def list_photos(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    sort: str = Query("newest", regex="^(newest|top_rated|most_viewed)$"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    query = (
        db.query(Photo)
        .options(joinedload(Photo.creator))
        .filter(Photo.is_active == True)
    )
    if sort == "newest":
        query = query.order_by(Photo.upload_date.desc())
    elif sort == "top_rated":
        query = query.order_by(Photo.avg_rating.desc(), Photo.upload_date.desc())
    elif sort == "most_viewed":
        query = query.order_by(Photo.view_count.desc(), Photo.upload_date.desc())

    total = query.count()
    photos = query.offset((page - 1) * page_size).limit(page_size).all()

    user_ratings = {}
    if current_user and photos:
        rows = db.query(Rating).filter(
            Rating.photo_id.in_([p.id for p in photos]),
            Rating.user_id == current_user.id,
        ).all()
        user_ratings = {r.photo_id: r.score for r in rows}

    return PhotoListResponse(
        photos=[_photo_to_response(p, user_ratings.get(p.id)) for p in photos],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get("/my", response_model=PhotoListResponse)
def get_my_photos(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_creator),
):
    query = (
        db.query(Photo)
        .options(joinedload(Photo.creator))
        .filter(Photo.creator_id == current_user.id, Photo.is_active == True)
        .order_by(Photo.upload_date.desc())
    )
    total = query.count()
    photos = query.offset((page - 1) * page_size).limit(page_size).all()
    return PhotoListResponse(
        photos=[_photo_to_response(p) for p in photos],
        total=total, page=page, page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get("/{photo_id}", response_model=PhotoResponse)
def get_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    photo = (
        db.query(Photo)
        .options(joinedload(Photo.creator))
        .filter(Photo.id == photo_id, Photo.is_active == True)
        .first()
    )
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    db.query(Photo).filter(Photo.id == photo_id).update({"view_count": Photo.view_count + 1})
    db.commit()
    db.refresh(photo)

    user_rating = None
    if current_user:
        r = db.query(Rating).filter(Rating.photo_id == photo_id, Rating.user_id == current_user.id).first()
        if r:
            user_rating = r.score

    return _photo_to_response(photo, user_rating)


@router.put("/{photo_id}", response_model=PhotoResponse)
def update_photo(
    photo_id: int,
    update: PhotoUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_creator),
):
    photo = db.query(Photo).filter(
        Photo.id == photo_id, Photo.creator_id == current_user.id, Photo.is_active == True
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found or not yours")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(photo, field, value)
    db.commit()
    photo = db.query(Photo).options(joinedload(Photo.creator)).filter(Photo.id == photo_id).first()
    return _photo_to_response(photo)


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_creator),
):
    photo = db.query(Photo).filter(Photo.id == photo_id, Photo.creator_id == current_user.id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found or not yours")
    photo.is_active = False
    db.commit()
