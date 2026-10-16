"""Domain models for Users and Roles."""

import enum
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.society import SocietyMembership
    from app.models.refresh_token import RefreshToken


class UserRole(str, enum.Enum):
    RESIDENT = "RESIDENT"
    SOCIETY_ADMIN = "SOCIETY_ADMIN"
    VENDOR = "VENDOR"
    PLATFORM_ADMIN = "PLATFORM_ADMIN"


class User(Base, TimestampMixin, UUIDMixin):
    """User accounts across all platform personas."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        index=True,
        nullable=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(30),
        default=UserRole.RESIDENT.value,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    memberships: Mapped[List["SocietyMembership"]] = relationship(
        "SocietyMembership",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
