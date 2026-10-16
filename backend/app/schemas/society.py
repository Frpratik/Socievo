"""Pydantic schemas for Housing Societies, Wings, Units, and Memberships."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.society import MembershipRole, MembershipStatus
from app.schemas.auth import UserResponse


class SocietyCreateRequest(BaseModel):
    """Schema for registering a new residential society."""
    name: str = Field(min_length=3, max_length=200)
    code: str = Field(min_length=3, max_length=50)
    address_line1: str = Field(min_length=5, max_length=255)
    locality: str = Field(min_length=2, max_length=150)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)
    pincode: str = Field(min_length=6, max_length=10)
    timezone: str = Field(default="Asia/Kolkata", max_length=50)


class SocietyResponse(BaseModel):
    """Public society profile representation."""
    id: UUID
    name: str
    code: str
    address_line1: str
    locality: str
    city: str
    state: str
    pincode: str
    timezone: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UnitCreateRequest(BaseModel):
    """Payload to create a residential flat/unit."""
    unit_number: str = Field(min_length=1, max_length=50)


class UnitResponse(BaseModel):
    """Representation of an individual flat/unit."""
    id: UUID
    wing_id: UUID
    unit_number: str

    model_config = {"from_attributes": True}


class WingCreateRequest(BaseModel):
    """Payload to add a wing or tower to a society."""
    name: str = Field(min_length=1, max_length=100)


class WingResponse(BaseModel):
    """Representation of a tower/wing including its residential units."""
    id: UUID
    society_id: UUID
    name: str
    units: List[UnitResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class MembershipJoinRequest(BaseModel):
    """Payload for a resident to join or request membership in a society."""
    unit_id: Optional[UUID] = None
    role: MembershipRole = Field(default=MembershipRole.RESIDENT)


class MembershipStatusUpdateRequest(BaseModel):
    """Payload for a society admin to review resident membership requests."""
    status: MembershipStatus = Field(description="APPROVED, REJECTED, or SUSPENDED")


class MembershipResponse(BaseModel):
    """Society enrollment details with nested user, society, and unit metadata."""
    id: UUID
    society_id: UUID
    user_id: UUID
    unit_id: Optional[UUID] = None
    role: str
    status: str
    verified_at: Optional[datetime] = None
    created_at: datetime
    user: Optional[UserResponse] = None
    society: Optional[SocietyResponse] = None
    unit: Optional[UnitResponse] = None

    model_config = {"from_attributes": True}
