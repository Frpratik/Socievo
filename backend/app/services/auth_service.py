"""Authentication and User Account Service."""

import hashlib
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
)
from app.core.redis import blacklist_token
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole
from app.schemas.auth import (
    PasswordChangeRequest,
    TokenResponse,
    UserProfileUpdate,
    UserRegisterRequest,
    UserResponse,
)


def _hash_token(token: str) -> str:
    """Computes SHA-256 hash of a refresh token string for safe database lookup."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    """Encapsulates authentication, token generation, and account operations."""

    @staticmethod
    async def register_user(
        db: AsyncSession,
        req: UserRegisterRequest,
    ) -> User:
        """Registers a new user account with Argon2id password hashing."""
        # 1. Check for duplicate email
        query = select(User).where(User.email == req.email.lower().strip())
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise ConflictError(f"A user with email '{req.email}' already exists.")

        # 2. Hash password & create user
        user = User(
            email=req.email.lower().strip(),
            phone=req.phone.strip() if req.phone else None,
            password_hash=hash_password(req.password),
            full_name=req.full_name.strip(),
            role=req.role.value,
            is_active=True,
            is_verified=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str,
        society_id: Optional[str] = None,
    ) -> TokenResponse:
        """Validates credentials, creates session, and issues access & refresh tokens."""
        query = select(User).where(User.email == email.lower().strip())
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationError("Account has been deactivated. Please contact support.")

        # Generate tokens
        access_token = create_access_token(
            subject=user.id,
            role=user.role,
            society_id=society_id,
        )
        refresh_token = create_refresh_token(subject=user.id)

        # Decode refresh token expiration to store accurately
        payload = decode_token(refresh_token)
        exp_timestamp = payload.get("exp")
        expires_at = (
            datetime.fromtimestamp(exp_timestamp, timezone.utc)
            if exp_timestamp
            else datetime.now(timezone.utc)
        )

        # Persist refresh token hash
        db_token = RefreshToken(
            user_id=user.id,
            token_hash=_hash_token(refresh_token),
            expires_at=expires_at,
            is_revoked=False,
        )
        db.add(db_token)
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def refresh_tokens(
        db: AsyncSession,
        refresh_token_str: str,
    ) -> TokenResponse:
        """Rotates refresh tokens and issues a new access token."""
        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type. Expected refresh token.")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Missing subject in token payload.")

        token_hash = _hash_token(refresh_token_str)
        query = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked.is_(False),
        )
        result = await db.execute(query)
        db_token = result.scalar_one_or_none()

        if not db_token:
            raise AuthenticationError("Refresh token has been revoked or is invalid.")

        # Check expiration
        now = datetime.now(timezone.utc)
        if db_token.expires_at.replace(tzinfo=timezone.utc) < now:
            db_token.is_revoked = True
            await db.commit()
            raise AuthenticationError("Refresh token has expired. Please log in again.")

        # Revoke old token (rotation)
        db_token.is_revoked = True

        # Fetch user
        user_query = select(User).where(User.id == db_token.user_id)
        user_res = await db.execute(user_query)
        user = user_res.scalar_one_or_none()
        if not user or not user.is_active:
            await db.commit()
            raise AuthenticationError("User is no longer active.")

        # Issue new token pair
        new_access = create_access_token(subject=user.id, role=user.role)
        new_refresh = create_refresh_token(subject=user.id)
        new_payload = decode_token(new_refresh)
        new_exp = new_payload.get("exp")
        new_expires_at = (
            datetime.fromtimestamp(new_exp, timezone.utc)
            if new_exp
            else now
        )

        new_db_token = RefreshToken(
            user_id=user.id,
            token_hash=_hash_token(new_refresh),
            expires_at=new_expires_at,
            is_revoked=False,
        )
        db.add(new_db_token)
        await db.commit()

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def logout_user(
        db: AsyncSession,
        refresh_token_str: Optional[str] = None,
    ) -> None:
        """Revokes the given refresh token."""
        if refresh_token_str:
            token_hash = _hash_token(refresh_token_str)
            stmt = (
                update(RefreshToken)
                .where(RefreshToken.token_hash == token_hash)
                .values(is_revoked=True)
            )
            await db.execute(stmt)
            await db.commit()

    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user: User,
        req: UserProfileUpdate,
    ) -> User:
        """Updates user profile details."""
        if req.full_name is not None:
            user.full_name = req.full_name.strip()
        if req.phone is not None:
            user.phone = req.phone.strip()

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User,
        req: PasswordChangeRequest,
    ) -> None:
        """Verifies old password and hashes new password."""
        if not verify_password(req.old_password, user.password_hash):
            raise AuthenticationError("Incorrect current password.")

        user.password_hash = hash_password(req.new_password)
        db.add(user)

        # Invalidate all existing refresh tokens for security
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user.id)
            .values(is_revoked=True)
        )
        await db.execute(stmt)
        await db.commit()
