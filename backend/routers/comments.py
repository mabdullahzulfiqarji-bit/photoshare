"""Comments endpoints with Azure sentiment analysis."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db, Comment, Photo, User
from schemas import CommentCreateRequest, CommentResponse
from auth_utils import get_current_user
from ai_service import ai_service

router = APIRouter()


@router.post("/{photo_id}", response_model=CommentResponse, status_code=201)
def add_comment(
    photo_id: int,
    request: CommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a comment to a photo (any authenticated user)."""
    photo = db.query(Photo).filter(Photo.id == photo_id, Photo.is_active == True).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Sentiment analysis
    sentiment_label, sentiment_score = ai_service.analyze_sentiment(request.content)

    comment = Comment(
        content=request.content,
        sentiment=sentiment_label,
        sentiment_score=sentiment_score,
        photo_id=photo_id,
        author_id=current_user.id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    comment = (
        db.query(Comment)
        .options(joinedload(Comment.author))
        .filter(Comment.id == comment.id)
        .first()
    )
    return CommentResponse.model_validate(comment)


@router.get("/{photo_id}", response_model=List[CommentResponse])
def get_comments(
    photo_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all comments for a photo."""
    comments = (
        db.query(Comment)
        .options(joinedload(Comment.author))
        .filter(Comment.photo_id == photo_id)
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [CommentResponse.model_validate(c) for c in comments]


@router.delete("/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete own comment."""
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.author_id == current_user.id,
    ).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or not yours")
    db.delete(comment)
    db.commit()
