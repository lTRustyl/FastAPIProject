import pytest
from tests.conftest import auth_headers

class TestLogin:
    def test_login_success(self, client, regular_user):
        response = client.post(
            "/auth/login",
            data={"username": "user_one", "password": "user123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, regular_user):
        response = client.post(
            "/auth/login",
            data={"username": "user_one", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_wrong_username(self, client):
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent", "password": "user123"},
        )
        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        response = client.post("/auth/login", data={})
        assert response.status_code == 422
