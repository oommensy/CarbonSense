"""
Pytest configuration and shared fixtures for CarbonSense backend tests.
Uses an in-memory SQLite database so tests are fully isolated and fast.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Use in-memory SQLite for tests
os.environ["DATABASE_URL"] = "sqlite://"

from app.models.database import Base, get_db  # noqa: E402
from main import app  # noqa: E402

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create fresh tables for each test, drop after."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """FastAPI test client with overridden DB dependency."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    return {
        "email": "test@carbonsense.com",
        "username": "testuser",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "role": "individual",
    }


@pytest.fixture
def registered_user(client, test_user_data):
    """Register a user and return the response data."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def auth_headers(client, test_user_data, registered_user):
    """Return Authorization headers for a logged-in user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user_data["email"], "password": test_user_data["password"]},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
