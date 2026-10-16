"""Tests for Argon2id password hashing and JWT token life cycle."""

import pytest
from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    """Verify that password hashing produces valid Argon2 hashes that verify correctly."""
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False


def test_jwt_access_token():
    """Verify access token creation, claims, and decoding."""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    role = "RESIDENT"
    society_id = "987fcdeb-51a2-43f1-b987-123456789abc"

    token = create_access_token(
        subject=user_id,
        role=role,
        society_id=society_id,
    )
    assert isinstance(token, str)

    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == role
    assert payload["society_id"] == society_id
    assert payload["type"] == "access"
    assert "exp" in payload


def test_jwt_refresh_token():
    """Verify refresh token creation and payload structure."""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = create_refresh_token(subject=user_id)

    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"


def test_invalid_token_decoding():
    """Verify that decoding a malformed token raises an AuthenticationError."""
    with pytest.raises(AuthenticationError):
        decode_token("this.is.not.a.valid.jwt")
