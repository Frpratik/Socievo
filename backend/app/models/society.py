"""Domain models for Housing Societies, Wings, Units, and Memberships."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class MembershipStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"


class MembershipRole(str, enum.Enum):
    RESIDENT = "RESIDENT"
    SOCIETY_ADMIN = "SOCIETY_ADMIN"


class Society(Base, TimestampMixin, UUIDMixin):
    """Housing society / gated apartment community entity."""

    __tablename__ = "societies"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    locality: Mapped[str] = mapped_column(String(150), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    pincode: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)

    # Relationships
    wings: Mapped[List["SocietyWing"]] = relationship(
        "SocietyWing",
        back_populates="society",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    memberships: Mapped[List["SocietyMembership"]] = relationship(
        "SocietyMembership",
        back_populates="society",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Society {self.name} [{self.code}]>"


class SocietyWing(Base, UUIDMixin):
    """Building / Tower / Wing inside a residential society."""

    __tablename__ = "society_wings"

    society_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("societies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    society: Mapped["Society"] = relationship("Society", back_populates="wings")
    units: Mapped[List["SocietyUnit"]] = relationship(
        "SocietyUnit",
        back_populates="wing",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<SocietyWing {self.name}>"


class SocietyUnit(Base, UUIDMixin):
    """Specific flat / apartment / residential unit."""

    __tablename__ = "society_units"

    wing_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("society_wings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    unit_number: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    wing: Mapped["SocietyWing"] = relationship("SocietyWing", back_populates="units")

    __table_args__ = (
        UniqueConstraint("wing_id", "unit_number", name="uq_wing_unit_number"),
    )

    def __repr__(self) -> str:
        return f"<SocietyUnit {self.unit_number}>"


class SocietyMembership(Base, TimestampMixin, UUIDMixin):
    """Association between User and Society with verification status."""

    __tablename__ = "society_memberships"

    society_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("societies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("society_units.id", ondelete="SET NULL"),
        nullable=True,
    )
    role: Mapped[str] = mapped_column(
        String(30),
        default=MembershipRole.RESIDENT.value,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default=MembershipStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    society: Mapped["Society"] = relationship("Society", back_populates="memberships", lazy="selectin")
    user: Mapped["User"] = relationship("User", back_populates="memberships", lazy="selectin")
    unit: Mapped[Optional["SocietyUnit"]] = relationship("SocietyUnit", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("society_id", "user_id", name="uq_society_user_membership"),
    )

    def __repr__(self) -> str:
        return f"<SocietyMembership user={self.user_id} society={self.society_id} status={self.status}>"
