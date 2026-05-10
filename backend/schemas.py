"""
Pydantic schemas for request validation and response serialization.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    creator = "creator"
    consumer = "consumer"
    admin = "admin"


# ─── Auth Schemas ─────────────────────────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: Optional[str] = Field(None, max_length=100)
    role: UserRole = UserRole.consumer  # Consumers self-register; creators set by admin

    @validator("username")
    def username_alphanumeric(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores/hyphens allowed)")
        return v.lower()


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


# ─── User Schemas ─────────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)


class CreatorCreateRequest(BaseModel):
    """Admin-only: create a creator account."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: Optional[str] = None


# ─── Photo Schemas ────────────────────────────────────────────────────────────

class PhotoUploadMetadata(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    caption: Optional[str] = Field(None, max_length=2000)
    location: Optional[str] = Field(None, max_length=255)
    people_tagged: Optional[str] = Field(None, max_length=500)


class PhotoResponse(BaseModel):
    id: int
    title: str
    caption: Optional[str]
    location: Optional[str]
    people_tagged: Optional[str]
    image_url: str
    thumbnail_url: Optional[str]
    file_size: Optional[int]
    width: Optional[int]
    height: Optional[int]
    ai_tags: Optional[str]
    ai_description: Optional[str]
    view_count: int
    avg_rating: float
    rating_count: int
    creator_id: int
    creator: Optional[UserResponse]
    upload_date: datetime
    user_rating: Optional[int] = None  # current user's rating

    class Config:
        from_attributes = True


class PhotoListResponse(BaseModel):
    photos: List[PhotoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PhotoUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    caption: Optional[str] = Field(None, max_length=2000)
    location: Optional[str] = Field(None, max_length=255)
    people_tagged: Optional[str] = Field(None, max_length=500)


# ─── Comment Schemas ──────────────────────────────────────────────────────────

class CommentCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: int
    content: str
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    photo_id: int
    author_id: int
    author: Optional[UserResponse]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Rating Schemas ───────────────────────────────────────────────────────────

class RatingCreateRequest(BaseModel):
    score: int = Field(..., ge=1, le=5)


class RatingResponse(BaseModel):
    id: int
    score: int
    photo_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Search Schemas ───────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    page: int = Field(1, ge=1)
    page_size: int = Field(12, ge=1, le=50)


class StatsResponse(BaseModel):
    total_photos: int
    total_users: int
    total_comments: int
    total_ratings: int
    top_rated_photo: Optional[PhotoResponse]


# Update forward references
TokenResponse.model_rebuild()
