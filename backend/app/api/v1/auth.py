"""Authentication and user management REST endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_active_user
from app.db.session import get_async_session
from app.models.user import User
from app.schemas.auth import (
    PasswordChangeRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserProfileUpdate,
    UserRegisterRequest,
    UserResponse,
)
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & Accounts"])


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    req: UserRegisterRequest,
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[UserResponse]:
    """Registers a new resident, society organizer, or vendor."""
    user = await AuthService.register_user(db, req)
    return APIResponse(
        status="success",
        data=UserResponse.model_validate(user),
        message="Account registered successfully.",
    )


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    summary="Authenticate with email & password",
)
async def login(
    req: UserLoginRequest,
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[TokenResponse]:
    """Validates credentials and issues an access token and refresh token."""
    token_response = await AuthService.authenticate_user(
        db, email=req.email, password=req.password
    )
    return APIResponse(
        status="success",
        data=token_response,
        message="Authentication successful.",
    )


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    summary="Rotate refresh token and issue new access token",
)
async def refresh(
    req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[TokenResponse]:
    """Exchanges an unexpired refresh token for rotated tokens."""
    token_response = await AuthService.refresh_tokens(db, req.refresh_token)
    return APIResponse(
        status="success",
        data=token_response,
        message="Token refreshed successfully.",
    )


@router.post(
    "/logout",
    response_model=APIResponse[None],
    summary="Log out and revoke session refresh token",
)
async def logout(
    req: Optional[RefreshTokenRequest] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[None]:
    """Invalidates the provided refresh token session."""
    refresh_token = req.refresh_token if req else None
    await AuthService.logout_user(db, refresh_token)
    return APIResponse(
        status="success",
        data=None,
        message="Successfully logged out.",
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Get current authenticated user profile",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> APIResponse[UserResponse]:
    """Returns the authenticated user's profile."""
    return APIResponse(
        status="success",
        data=UserResponse.model_validate(current_user),
    )


@router.patch(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Update current authenticated user profile",
)
async def update_me(
    req: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[UserResponse]:
    """Updates editable personal attributes (full name, phone)."""
    updated_user = await AuthService.update_profile(db, current_user, req)
    return APIResponse(
        status="success",
        data=UserResponse.model_validate(updated_user),
        message="Profile updated successfully.",
    )


@router.post(
    "/change-password",
    response_model=APIResponse[None],
    summary="Update password and invalidate prior sessions",
)
async def change_password(
    req: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[None]:
    """Updates the user's password and revokes previous sessions."""
    await AuthService.change_password(db, current_user, req)
    return APIResponse(
        status="success",
        data=None,
        message="Password updated successfully. Please log in with your new password.",
    )
