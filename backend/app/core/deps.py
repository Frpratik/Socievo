"""FastAPI dependencies for authentication, role authorization, and tenant isolation."""

import uuid
from typing import Callable, Optional
from fastapi import Depends, Header, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.redis import is_token_blacklisted
from app.core.security import decode_token
from app.db.session import get_async_session
from app.models.society import MembershipRole, MembershipStatus, SocietyMembership
from app.models.user import User, UserRole

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    """Extracts, validates JWT access token, and retrieves the authenticated User."""
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Authorization header missing or invalid.")

    token = credentials.credentials
    payload = decode_token(token)

    # Check token type
    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type. Expected access token.")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token claims.")

    # Check revocation if jti is present
    jti = payload.get("jti")
    if jti and await is_token_blacklisted(jti):
        raise AuthenticationError("Token has been revoked.")

    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError:
        raise AuthenticationError("Malformed user identifier in token.")

    query = select(User).where(User.id == user_uuid)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError("User associated with token no longer exists.")

    if not user.is_active:
        raise AuthenticationError("User account is deactivated.")

    return user


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """Ensures user is active."""
    return user


def require_role(*allowed_roles: UserRole) -> Callable:
    """Factory creating a role-enforcing dependency."""
    async def role_checker(user: User = Depends(get_current_active_user)) -> User:
        allowed_values = [r.value if isinstance(r, UserRole) else r for r in allowed_roles]
        if user.role not in allowed_values:
            raise PermissionDeniedError(
                f"Action requires one of the following roles: {', '.join(allowed_values)}"
            )
        return user

    return role_checker


async def require_society_member(
    society_id: uuid.UUID = Path(..., description="Target Society UUID"),
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> SocietyMembership:
    """Multi-tenancy isolation guard: Enforces that user is an approved member of the society."""
    if user.role == UserRole.PLATFORM_ADMIN.value:
        # Platform admin bypasses tenant restriction for operational oversight
        return None  # type: ignore

    query = select(SocietyMembership).where(
        SocietyMembership.society_id == society_id,
        SocietyMembership.user_id == user.id,
        SocietyMembership.status == MembershipStatus.APPROVED.value,
    )
    result = await db.execute(query)
    membership = result.scalar_one_or_none()

    if not membership:
        raise PermissionDeniedError("Access denied. You are not an approved member of this society.")

    return membership


async def require_society_admin(
    society_id: uuid.UUID = Path(..., description="Target Society UUID"),
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> SocietyMembership:
    """Multi-tenancy isolation guard: Enforces that user is a Society Admin of the target society."""
    if user.role == UserRole.PLATFORM_ADMIN.value:
        return None  # type: ignore

    query = select(SocietyMembership).where(
        SocietyMembership.society_id == society_id,
        SocietyMembership.user_id == user.id,
        SocietyMembership.role == MembershipRole.SOCIETY_ADMIN.value,
        SocietyMembership.status == MembershipStatus.APPROVED.value,
    )
    result = await db.execute(query)
    membership = result.scalar_one_or_none()

    if not membership:
        raise PermissionDeniedError(
            "Access denied. You are not an authorized Society Administrator for this society."
        )

    return membership
