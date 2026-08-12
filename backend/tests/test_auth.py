"""
Authentication Tests
====================
Tests for login success/failure, registration, and token refresh.
Each test is independent — the database is recreated before every test.
"""

from tests.conftest import create_user, get_token, get_refresh_token
from app.models.user import UserRole


# ---- Registration ----

class TestRegister:
    """POST /api/v1/auth/register"""

    def test_register_creates_candidate(self, client):
        """
        A new user registering via the public endpoint always gets the
        'candidate' role, regardless of what the frontend sends.
        This prevents privilege escalation.
        """
        res = client.post("/api/v1/auth/register", json={
            "email": "new@test.com",
            "password": "securepassword",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["email"] == "new@test.com"
        assert data["role"] == "candidate"

    def test_register_duplicate_email_fails(self, client, candidate_user):
        """
        Registering with an email that already exists returns 409.
        The user fixture already created 'candidate@test.com'.
        """
        res = client.post("/api/v1/auth/register", json={
            "email": "candidate@test.com",
            "password": "securepassword",
        })
        assert res.status_code == 409

    def test_register_short_password_fails(self, client):
        """
        The backend enforces min_length=8 on passwords.
        A 5-character password should be rejected with 422.
        """
        res = client.post("/api/v1/auth/register", json={
            "email": "short@test.com",
            "password": "short",
        })
        assert res.status_code == 422

    def test_register_invalid_email_fails(self, client):
        """
        Pydantic EmailStr validation rejects malformed emails.
        """
        res = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "securepassword",
        })
        assert res.status_code == 422


# ---- Login ----

class TestLogin:
    """POST /api/v1/auth/login"""

    def test_login_success(self, client, candidate_user):
        """
        Valid credentials return an access token and a refresh token.
        The response shape matches the TokenResponse schema.
        """
        res = client.post("/api/v1/auth/login", data={
            "username": "candidate@test.com",
            "password": "secret123",
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password_fails(self, client, candidate_user):
        """
        A correct email with the wrong password returns 401.
        The error message must not reveal which field is wrong.
        """
        res = client.post("/api/v1/auth/login", data={
            "username": "candidate@test.com",
            "password": "wrongpassword",
        })
        assert res.status_code == 401
        assert res.json()["detail"] == "Incorrect email or password"

    def test_login_nonexistent_user_fails(self, client):
        """
        Attempting to log in with an email that doesn't exist
        returns the same generic 401 as a wrong password.
        This prevents user enumeration.
        """
        res = client.post("/api/v1/auth/login", data={
            "username": "nobody@test.com",
            "password": "anypassword",
        })
        assert res.status_code == 401
        assert res.json()["detail"] == "Incorrect email or password"


# ---- Token Refresh ----

class TestRefresh:
    """POST /api/v1/auth/refresh"""

    def test_refresh_returns_new_tokens(self, client, candidate_user):
        """
        A valid refresh token yields a new access/refresh pair.
        The old refresh token becomes invalid after rotation.
        """
        refresh = get_refresh_token(candidate_user.id)
        res = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh,
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_with_access_token_fails(self, client, candidate_user):
        """
        An access token cannot be used as a refresh token.
        The 'type' claim in the JWT distinguishes them.
        """
        access = get_token(candidate_user.id)
        res = client.post("/api/v1/auth/refresh", json={
            "refresh_token": access,
        })
        assert res.status_code == 401

    def test_refresh_with_invalid_token_fails(self, client):
        """
        A garbage token string is rejected with 401.
        """
        res = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "totally.invalid.token",
        })
        assert res.status_code == 401
