"""
Automated tests for PhotoShare API.
Run with: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///./test_photoshare.db"

import os
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"

from main import app
from database import Base, get_db, engine as prod_engine

# Override database for tests
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture
def admin_token():
    client.post("/api/admin/seed")
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@1234"})
    return resp.json()["access_token"]


@pytest.fixture
def consumer_data():
    return {"username": "testconsumer", "email": "consumer@test.com", "password": "Password123"}


@pytest.fixture
def consumer_token(consumer_data):
    client.post("/api/auth/register", json=consumer_data)
    resp = client.post("/api/auth/login", json={"username": consumer_data["username"], "password": consumer_data["password"]})
    return resp.json()["access_token"]


@pytest.fixture
def creator_token(admin_token):
    client.post(
        "/api/admin/creators",
        json={"username": "testcreator", "email": "creator@test.com", "password": "Password123"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = client.post("/api/auth/login", json={"username": "testcreator", "password": "Password123"})
    return resp.json()["access_token"]


# ─── Auth Tests ───────────────────────────────────────────────────────────────

class TestAuth:
    def test_register_consumer(self, consumer_data):
        resp = client.post("/api/auth/register", json=consumer_data)
        assert resp.status_code == 201
        data = resp.json()
        assert data["user"]["role"] == "consumer"
        assert "access_token" in data

    def test_register_duplicate_username(self, consumer_data):
        client.post("/api/auth/register", json=consumer_data)
        resp = client.post("/api/auth/register", json=consumer_data)
        assert resp.status_code == 400

    def test_login_success(self, consumer_data):
        client.post("/api/auth/register", json=consumer_data)
        resp = client.post("/api/auth/login", json={"username": consumer_data["username"], "password": consumer_data["password"]})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, consumer_data):
        client.post("/api/auth/register", json=consumer_data)
        resp = client.post("/api/auth/login", json={"username": consumer_data["username"], "password": "wrong"})
        assert resp.status_code == 401

    def test_get_me(self, consumer_token):
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {consumer_token}"})
        assert resp.status_code == 200
        assert resp.json()["username"] == "testconsumer"


# ─── Photo Tests ──────────────────────────────────────────────────────────────

class TestPhotos:
    def _upload_photo(self, token: str):
        import io
        from PIL import Image
        img = Image.new("RGB", (100, 100), color="blue")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)

        return client.post(
            "/api/photos/upload",
            headers={"Authorization": f"Bearer {token}"},
            data={"title": "Test Photo", "caption": "A test", "location": "London"},
            files={"file": ("test.jpg", buf, "image/jpeg")},
        )

    def test_upload_as_creator(self, creator_token):
        resp = self._upload_photo(creator_token)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Test Photo"
        assert data["location"] == "London"

    def test_upload_as_consumer_forbidden(self, consumer_token):
        resp = self._upload_photo(consumer_token)
        assert resp.status_code == 403

    def test_list_photos(self, creator_token):
        self._upload_photo(creator_token)
        resp = client.get("/api/photos")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_get_photo_increments_view(self, creator_token):
        upload = self._upload_photo(creator_token)
        photo_id = upload.json()["id"]
        client.get(f"/api/photos/{photo_id}")
        resp = client.get(f"/api/photos/{photo_id}")
        assert resp.json()["view_count"] >= 1

    def test_delete_own_photo(self, creator_token):
        upload = self._upload_photo(creator_token)
        photo_id = upload.json()["id"]
        resp = client.delete(f"/api/photos/{photo_id}", headers={"Authorization": f"Bearer {creator_token}"})
        assert resp.status_code == 204


# ─── Comment Tests ────────────────────────────────────────────────────────────

class TestComments:
    def _get_photo_id(self, creator_token):
        import io
        from PIL import Image
        img = Image.new("RGB", (50, 50), color="red")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        resp = client.post(
            "/api/photos/upload",
            headers={"Authorization": f"Bearer {creator_token}"},
            data={"title": "Commentable"},
            files={"file": ("img.jpg", buf, "image/jpeg")},
        )
        return resp.json()["id"]

    def test_add_comment(self, creator_token, consumer_token):
        pid = self._get_photo_id(creator_token)
        resp = client.post(
            f"/api/comments/{pid}",
            json={"content": "Great photo!"},
            headers={"Authorization": f"Bearer {consumer_token}"},
        )
        assert resp.status_code == 201
        assert resp.json()["content"] == "Great photo!"

    def test_list_comments(self, creator_token, consumer_token):
        pid = self._get_photo_id(creator_token)
        client.post(f"/api/comments/{pid}", json={"content": "Nice!"}, headers={"Authorization": f"Bearer {consumer_token}"})
        resp = client.get(f"/api/comments/{pid}")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


# ─── Rating Tests ─────────────────────────────────────────────────────────────

class TestRatings:
    def _get_photo_id(self, creator_token):
        import io
        from PIL import Image
        img = Image.new("RGB", (50, 50), color="green")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        resp = client.post(
            "/api/photos/upload",
            headers={"Authorization": f"Bearer {creator_token}"},
            data={"title": "Rateable"},
            files={"file": ("img.jpg", buf, "image/jpeg")},
        )
        return resp.json()["id"]

    def test_rate_photo(self, creator_token, consumer_token):
        pid = self._get_photo_id(creator_token)
        resp = client.post(
            f"/api/ratings/{pid}",
            json={"score": 5},
            headers={"Authorization": f"Bearer {consumer_token}"},
        )
        assert resp.status_code == 200

    def test_rerate_photo(self, creator_token, consumer_token):
        pid = self._get_photo_id(creator_token)
        client.post(f"/api/ratings/{pid}", json={"score": 3}, headers={"Authorization": f"Bearer {consumer_token}"})
        client.post(f"/api/ratings/{pid}", json={"score": 5}, headers={"Authorization": f"Bearer {consumer_token}"})
        photo = client.get(f"/api/photos/{pid}").json()
        assert photo["avg_rating"] == 5.0

    def test_invalid_rating(self, creator_token, consumer_token):
        pid = self._get_photo_id(creator_token)
        resp = client.post(f"/api/ratings/{pid}", json={"score": 6}, headers={"Authorization": f"Bearer {consumer_token}"})
        assert resp.status_code == 422


# ─── Search Tests ─────────────────────────────────────────────────────────────

class TestSearch:
    def test_search_by_title(self, creator_token):
        import io
        from PIL import Image
        img = Image.new("RGB", (50, 50))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        client.post(
            "/api/photos/upload",
            headers={"Authorization": f"Bearer {creator_token}"},
            data={"title": "Sunset in Paris", "location": "Paris"},
            files={"file": ("img.jpg", buf, "image/jpeg")},
        )
        resp = client.get("/api/search?q=Paris")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_search_no_results(self):
        resp = client.get("/api/search?q=xyzzy_doesnotexist_42")
        assert resp.json()["total"] == 0
