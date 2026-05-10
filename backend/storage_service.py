"""
Azure Blob Storage service.
Falls back to local filesystem storage if Azure credentials are not configured.
"""

import os
import uuid
import io
from typing import Tuple, Optional
from PIL import Image, ImageOps

from config import settings


class StorageService:
    """Handles photo and thumbnail storage - Azure Blob or local filesystem."""

    def __init__(self):
        self.use_azure = bool(settings.AZURE_STORAGE_CONNECTION_STRING)
        self.local_upload_dir = "uploads"
        
        if self.use_azure:
            from azure.storage.blob import BlobServiceClient
            self.blob_service = BlobServiceClient.from_connection_string(
                settings.AZURE_STORAGE_CONNECTION_STRING
            )
            self._ensure_containers()
            print("✅ Azure Blob Storage connected")
        else:
            os.makedirs(f"{self.local_upload_dir}/photos", exist_ok=True)
            os.makedirs(f"{self.local_upload_dir}/thumbnails", exist_ok=True)
            print("⚠️  Using local filesystem storage (Azure not configured)")

    def _ensure_containers(self):
        """Create blob containers if they don't exist."""
        for container_name in [
            settings.AZURE_STORAGE_CONTAINER_NAME,
            settings.AZURE_STORAGE_THUMBNAILS_CONTAINER,
        ]:
            try:
                container_client = self.blob_service.get_container_client(container_name)
                container_client.create_container(public_access="blob")
            except Exception:
                pass  # Container likely already exists

    def _generate_thumbnail(self, image_data: bytes, size: Tuple[int, int] = (400, 400)) -> bytes:
        """Generate a thumbnail from image bytes."""
        img = Image.open(io.BytesIO(image_data))
        img = ImageOps.exif_transpose(img)  # Fix rotation issues
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail(size, Image.LANCZOS)
        
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=85, optimize=True)
        return output.getvalue()

    def _get_image_dimensions(self, image_data: bytes) -> Tuple[int, int]:
        """Get image width and height."""
        img = Image.open(io.BytesIO(image_data))
        return img.size  # (width, height)

    def upload_photo(
        self, file_data: bytes, filename: str, content_type: str = "image/jpeg"
    ) -> Tuple[str, str, str, int, int]:
        """
        Upload a photo and its thumbnail.
        Returns: (image_url, thumbnail_url, blob_name, width, height)
        """
        # Generate unique filename
        ext = filename.rsplit(".", 1)[-1].lower()
        unique_name = f"{uuid.uuid4()}.{ext}"
        thumb_name = f"thumb_{uuid.uuid4()}.jpg"

        # Get dimensions
        try:
            width, height = self._get_image_dimensions(file_data)
        except Exception:
            width, height = 0, 0

        # Generate thumbnail
        thumbnail_data = self._generate_thumbnail(file_data)

        if self.use_azure:
            # Upload original
            blob_client = self.blob_service.get_blob_client(
                container=settings.AZURE_STORAGE_CONTAINER_NAME,
                blob=unique_name,
            )
            blob_client.upload_blob(file_data, blob_type="BlockBlob", content_settings=None, overwrite=True)

            # Upload thumbnail
            thumb_client = self.blob_service.get_blob_client(
                container=settings.AZURE_STORAGE_THUMBNAILS_CONTAINER,
                blob=thumb_name,
            )
            thumb_client.upload_blob(thumbnail_data, blob_type="BlockBlob", overwrite=True)

            # Build URLs
            account_name = self.blob_service.account_name
            image_url = f"https://{account_name}.blob.core.windows.net/{settings.AZURE_STORAGE_CONTAINER_NAME}/{unique_name}"
            thumbnail_url = f"https://{account_name}.blob.core.windows.net/{settings.AZURE_STORAGE_THUMBNAILS_CONTAINER}/{thumb_name}"
        else:
            # Local storage
            photo_path = f"{self.local_upload_dir}/photos/{unique_name}"
            thumb_path = f"{self.local_upload_dir}/thumbnails/{thumb_name}"
            
            with open(photo_path, "wb") as f:
                f.write(file_data)
            with open(thumb_path, "wb") as f:
                f.write(thumbnail_data)

            image_url = f"/uploads/photos/{unique_name}"
            thumbnail_url = f"/uploads/thumbnails/{thumb_name}"

        return image_url, thumbnail_url, unique_name, width, height

    def delete_photo(self, blob_name: str) -> bool:
        """Delete a photo and its thumbnail from storage."""
        if self.use_azure:
            try:
                self.blob_service.get_blob_client(
                    container=settings.AZURE_STORAGE_CONTAINER_NAME,
                    blob=blob_name,
                ).delete_blob()
                self.blob_service.get_blob_client(
                    container=settings.AZURE_STORAGE_THUMBNAILS_CONTAINER,
                    blob=f"thumb_{blob_name}",
                ).delete_blob()
            except Exception:
                return False
        else:
            try:
                os.remove(f"{self.local_upload_dir}/photos/{blob_name}")
                os.remove(f"{self.local_upload_dir}/thumbnails/thumb_{blob_name}")
            except FileNotFoundError:
                pass
        return True


# Singleton instance
storage_service = StorageService()
