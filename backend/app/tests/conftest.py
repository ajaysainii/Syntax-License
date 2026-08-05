import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["LICENSE_HMAC_SECRET"] = "license-secret"

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.main import app
from app.models.admin_user import AdminUser


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.add(
        AdminUser(
            email="admin@syntaxnation.com",
            full_name="Syntax Admin",
            password_hash=hash_password("password123"),
        )
    )
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@syntaxnation.com", "password": "password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

