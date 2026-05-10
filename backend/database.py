"""
Database configuration and SQLAlchemy models.
Supports both SQLite (local dev) and Azure SQL (production).
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey, UniqueConstraint, Index, Enum as SAEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import os

from config import settings

# ─── Engine setup ────────────────────────────────────────────────────────────

def get_database_url() -> str:
    """Build the database URL, preferring Azure SQL when env vars are set."""
    if settings.AZURE_SQL_SERVER:
        return (
            f"mssql+pyodbc://{settings.AZURE_SQL_USERNAME}:{settings.AZURE_SQL_PASSWORD}"
            f"@{settings.AZURE_SQL_SERVER}/{settings.AZURE_SQL_DATABASE}"
            f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
        )
    return settings.DATABASE_URL  # SQLite for local dev


engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {},
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─── Enums ───────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    creator = "creator"
    consumer = "consumer"
    admin = "admin"


# ─── Models ──────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.consumer, nullable=False)
    display_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    photos = relationship("Photo", back_populates="creator", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    caption = Column(Text, nullable=True)
    location = Column(String(255), nullable=True, index=True)
    people_tagged = Column(Text, nullable=True)  # Comma-separated names
    
    # Storage URLs
    image_url = Column(String(1000), nullable=False)
    thumbnail_url = Column(String(1000), nullable=True)
    blob_name = Column(String(500), nullable=True)
    
    # Metadata
    file_size = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # AI Analysis results
    ai_tags = Column(Text, nullable=True)        # JSON string of AI-detected tags
    ai_description = Column(Text, nullable=True)  # AI-generated description
    sentiment_score = Column(Float, nullable=True) # Sentiment of caption
    
    # Stats
    view_count = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Foreign key
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Timestamps
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    is_active = Column(Boolean, default=True)

    # Relationships
    creator = relationship("User", back_populates="photos")
    comments = relationship("Comment", back_populates="photo", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="photo", cascade="all, delete-orphan")

    # Indexes for search performance
    __table_args__ = (
        Index("ix_photos_creator_id", "creator_id"),
        Index("ix_photos_upload_date", "upload_date"),
        Index("ix_photos_avg_rating", "avg_rating"),
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    sentiment = Column(String(20), nullable=True)  # positive/negative/neutral
    sentiment_score = Column(Float, nullable=True)
    
    # Foreign keys
    photo_id = Column(Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    photo = relationship("Photo", back_populates="comments")
    author = relationship("User", back_populates="comments")

    __table_args__ = (
        Index("ix_comments_photo_id", "photo_id"),
    )


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    score = Column(Integer, nullable=False)  # 1-5 stars
    
    # Foreign keys
    photo_id = Column(Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    photo = relationship("Photo", back_populates="ratings")
    user = relationship("User", back_populates="ratings")

    # One rating per user per photo
    __table_args__ = (
        UniqueConstraint("photo_id", "user_id", name="uq_rating_photo_user"),
        Index("ix_ratings_photo_id", "photo_id"),
    )


# ─── Dependency ──────────────────────────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
