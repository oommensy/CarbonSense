"""
Tests for authentication endpoints.
Covers registration, login, token refresh, and protected route access.
"""

import pytest


class TestRegistration:
    def test_register_success(self, client, test_user_data):
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, test_user_data, registered_user):
        duplicate = {**test_user_data, "username": "different_user"}
        response = client.post("/api/v1/auth/register", json=duplicate)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_duplicate_username(self, client, test_user_data, registered_user):
        duplicate = {**test_user_data, "email": "other@example.com"}
        response = client.post("/api/v1/auth/register", json=duplicate)
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    def test_register_invalid_email(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "username": "user",
            "password": "pass",
            "full_name": "User",
        })
        assert response.status_code == 422

    def test_register_corporate_role(self, client, test_user_data):
        data = {**test_user_data, "role": "corporate"}
        response = client.post("/api/v1/auth/register", json=data)
        assert response.status_code == 200
        assert response.json()["role"] == "corporate"


class TestLogin:
    def test_login_success(self, client, test_user_data, registered_user):
        response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user_data, registered_user):
        response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": "WrongPassword!",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "pass",
        })
        assert response.status_code == 401


class TestProtectedRoutes:
    def test_get_me_authenticated(self, client, auth_headers, test_user_data):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["email"] == test_user_data["email"]

    def test_get_me_unauthenticated(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403

    def test_get_me_invalid_token(self, client):
        response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert response.status_code == 401
