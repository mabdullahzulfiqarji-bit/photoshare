"""
PhotoShare - Scalable Cloud-Native Photo Sharing Platform
FastAPI Backend with Azure SQL, Azure Blob Storage, and Azure AI Vision
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from contextlib import asynccontextmanager

from database import create_tables
from routers import auth, photos, users, comments, ratings, search, admin
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Create local upload directories (fallback when Azure not configured)
    os.makedirs("uploads/photos", exist_ok=True)
    os.makedirs("uploads/thumbnails", exist_ok=True)
    # Create database tables on startup
    create_tables()
    yield


app = FastAPI(
    title="PhotoShare API",
    description="Scalable Cloud-Native Photo Sharing Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(photos.router, prefix="/api/photos", tags=["Photos"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(comments.router, prefix="/api/comments", tags=["Comments"])
app.include_router(ratings.router, prefix="/api/ratings", tags=["Ratings"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/")
async def root():
    return {"message": "PhotoShare API is running", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "PhotoShare API"}


# Serve locally uploaded files (dev mode only)
# In production, Azure Blob Storage serves files directly
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
if os.path.isdir(uploads_dir):
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
