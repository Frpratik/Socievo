"""Integration tests for user registration, authentication, and session lifecycle."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_registration_flow(client: AsyncClient):
    """Test successful user registration and duplicate conflict rejection."""
    reg_payload = {
        "email": "priya.sharma@example.com",
        "password": "StrongPassword123!",
        "full_name": "Priya Sharma",
        "phone": "+919876543210",
        "role": "RESIDENT",
    }

    # 1. Successful registration
    response = await client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["email"] == "priya.sharma@example.com"
    assert data["data"]["full_name"] == "Priya Sharma"
    assert data["data"]["role"] == "RESIDENT"
    assert "id" in data["data"]
    assert "password_hash" not in data["data"]  # Ensure hash is never leaked

    # 2. Duplicate registration attempt should return 409 Conflict
    dup_response = await client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_response.status_code == 409
    dup_data = dup_response.json()
    assert dup_data["status"] == "error"
    assert dup_data["code"] == "RESOURCE_CONFLICT"


@pytest.mark.asyncio
async def test_user_login_and_token_refresh(client: AsyncClient):
    """Test user login, authentication failure, and token rotation."""
    # Register user
    reg_payload = {
        "email": "rahul.verma@example.com",
        "password": "PasswordVerma123!",
        "full_name": "Rahul Verma",
        "phone": "+919812345678",
        "role": "RESIDENT",
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    # 1. Invalid password
    bad_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "rahul.verma@example.com", "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401
    assert bad_login.json()["code"] == "AUTHENTICATION_FAILED"

    # 2. Valid login
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "rahul.verma@example.com", "password": "PasswordVerma123!"},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()["data"]
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    assert access_token is not None
    assert refresh_token is not None
    assert token_data["token_type"] == "bearer"

    # 3. Access protected profile endpoint
    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()["data"]
    assert me_data["email"] == "rahul.verma@example.com"
    assert me_data["full_name"] == "Rahul Verma"

    # 4. Rotate refresh token
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()["data"]
    assert new_tokens["access_token"] is not None
    assert new_tokens["refresh_token"] != refresh_token  # Proves token rotation

    # 5. Old refresh token cannot be reused
    stale_refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert stale_refresh.status_code == 401


@pytest.mark.asyncio
async def test_update_profile_and_change_password(client: AsyncClient):
    """Test updating user profile attributes and changing password."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "anita.deshmukh@example.com",
            "password": "OldPassword123!",
            "full_name": "Anita Deshmukh",
            "role": "RESIDENT",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "anita.deshmukh@example.com", "password": "OldPassword123!"},
    )
    token = login_res.json()["data"]["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}

    # 1. Update Profile
    update_res = await client.patch(
        "/api/v1/auth/me",
        headers=auth_header,
        json={"full_name": "Anita D. Rao", "phone": "+919999888877"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["full_name"] == "Anita D. Rao"
    assert update_res.json()["data"]["phone"] == "+919999888877"

    # 2. Change password
    pwd_res = await client.post(
        "/api/v1/auth/change-password",
        headers=auth_header,
        json={"old_password": "OldPassword123!", "new_password": "BrandNewSecurePassword456!"},
    )
    assert pwd_res.status_code == 200

    # 3. Verify login with new password succeeds
    new_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "anita.deshmukh@example.com", "password": "BrandNewSecurePassword456!"},
    )
    assert new_login.status_code == 200
