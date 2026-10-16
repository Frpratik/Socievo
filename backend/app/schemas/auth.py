"""Pydantic schemas for authentication and user accounts."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserRegisterRequest(BaseModel):
    """Payload for resident or organizer registration."""
    email: EmailStr
    password: str = Field(min_length=8, description="Password with minimum 8 characters")
    full_name: str = Field(min_length=2, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: UserRole = Field(default=UserRole.RESIDENT)


class UserLoginRequest(BaseModel):
    """Payload for user credentials authentication."""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Payload to exchange a refresh token for new access token."""
    refresh_token: str


class UserResponse(BaseModel):
    """Public user identity representation."""
    id: UUID
    email: EmailStr
    phone: Optional[str] = None
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Bearer token pair with public user payload."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserProfileUpdate(BaseModel):
    """Editable profile attributes."""
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)


class PasswordChangeRequest(BaseModel):
    """Authenticated password update payload."""
    old_password: str
    new_password: str = Field(min_length=8)
