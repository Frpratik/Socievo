"""Society, Wing, Unit, and Resident Membership Service."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from app.models.society import (
    MembershipRole,
    MembershipStatus,
    Society,
    SocietyMembership,
    SocietyUnit,
    SocietyWing,
)
from app.models.user import User
from app.schemas.society import (
    MembershipJoinRequest,
    MembershipStatusUpdateRequest,
    SocietyCreateRequest,
    UnitCreateRequest,
    WingCreateRequest,
)


class SocietyService:
    """Manages society directories, building hierarchies, and resident enrollments."""

    @staticmethod
    async def create_society(
        db: AsyncSession,
        req: SocietyCreateRequest,
        creator: User,
    ) -> Society:
        """Registers a new housing society and enrolls the creator as society admin."""
        # Check code uniqueness
        query = select(Society).where(Society.code == req.code.upper().strip())
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise ConflictError(f"A society with code '{req.code}' already exists.")

        society = Society(
            name=req.name.strip(),
            code=req.code.upper().strip(),
            address_line1=req.address_line1.strip(),
            locality=req.locality.strip(),
            city=req.city.strip(),
            state=req.state.strip(),
            pincode=req.pincode.strip(),
            timezone=req.timezone,
        )
        db.add(society)
        await db.flush()

        # Creator automatically becomes approved SOCIETY_ADMIN member
        membership = SocietyMembership(
            society_id=society.id,
            user_id=creator.id,
            role=MembershipRole.SOCIETY_ADMIN.value,
            status=MembershipStatus.APPROVED.value,
            verified_at=datetime.now(timezone.utc),
        )
        db.add(membership)
        await db.commit()
        await db.refresh(society)
        return society

    @staticmethod
    async def list_societies(
        db: AsyncSession,
        city: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Society], int]:
        """Lists societies with optional query filtering and pagination."""
        query = select(Society)
        count_query = select(func.count(Society.id))

        if city:
            query = query.where(func.lower(Society.city) == city.lower().strip())
            count_query = count_query.where(func.lower(Society.city) == city.lower().strip())

        if search:
            search_term = f"%{search.lower().strip()}%"
            filter_cond = or_(
                func.lower(Society.name).like(search_term),
                func.lower(Society.code).like(search_term),
                func.lower(Society.locality).like(search_term),
            )
            query = query.where(filter_cond)
            count_query = count_query.where(filter_cond)

        total_count = (await db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.order_by(Society.name.asc()).offset(offset).limit(page_size)

        result = await db.execute(query)
        societies = list(result.scalars().all())
        return societies, total_count

    @staticmethod
    async def get_society_by_id(
        db: AsyncSession,
        society_id: uuid.UUID,
    ) -> Society:
        """Retrieves a society by UUID."""
        query = select(Society).where(Society.id == society_id)
        result = await db.execute(query)
        society = result.scalar_one_or_none()
        if not society:
            raise NotFoundError("Society", society_id)
        return society

    @staticmethod
    async def add_wing(
        db: AsyncSession,
        society_id: uuid.UUID,
        req: WingCreateRequest,
    ) -> SocietyWing:
        """Adds a wing/tower to a society."""
        await SocietyService.get_society_by_id(db, society_id)
        wing = SocietyWing(
            society_id=society_id,
            name=req.name.strip(),
        )
        db.add(wing)
        await db.commit()
        await db.refresh(wing)
        wing.units = []
        return wing

    @staticmethod
    async def add_unit(
        db: AsyncSession,
        wing_id: uuid.UUID,
        req: UnitCreateRequest,
    ) -> SocietyUnit:
        """Adds a flat/unit to a wing, enforcing uniqueness."""
        query = select(SocietyWing).where(SocietyWing.id == wing_id)
        result = await db.execute(query)
        wing = result.scalar_one_or_none()
        if not wing:
            raise NotFoundError("SocietyWing", wing_id)

        # Check unit duplicate in wing
        check_query = select(SocietyUnit).where(
            SocietyUnit.wing_id == wing_id,
            SocietyUnit.unit_number == req.unit_number.strip(),
        )
        if (await db.execute(check_query)).scalar_one_or_none():
            raise ConflictError(f"Unit '{req.unit_number}' already exists in this wing.")

        unit = SocietyUnit(
            wing_id=wing_id,
            unit_number=req.unit_number.strip(),
        )
        db.add(unit)
        await db.commit()
        await db.refresh(unit)
        return unit

    @staticmethod
    async def list_wings(
        db: AsyncSession,
        society_id: uuid.UUID,
    ) -> List[SocietyWing]:
        """Lists all wings and nested units for a society."""
        query = (
            select(SocietyWing)
            .where(SocietyWing.society_id == society_id)
            .options(selectinload(SocietyWing.units))
            .order_by(SocietyWing.name.asc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def request_membership(
        db: AsyncSession,
        society_id: uuid.UUID,
        user: User,
        req: MembershipJoinRequest,
    ) -> SocietyMembership:
        """Creates a resident membership request for approval by society admins."""
        await SocietyService.get_society_by_id(db, society_id)

        # Check existing membership
        query = select(SocietyMembership).where(
            SocietyMembership.society_id == society_id,
            SocietyMembership.user_id == user.id,
        )
        if (await db.execute(query)).scalar_one_or_none():
            raise ConflictError("You have already submitted a membership request for this society.")

        membership = SocietyMembership(
            society_id=society_id,
            user_id=user.id,
            unit_id=req.unit_id,
            role=req.role.value,
            status=MembershipStatus.PENDING.value,
        )
        db.add(membership)
        await db.commit()
        await db.refresh(membership)
        return membership

    @staticmethod
    async def update_membership_status(
        db: AsyncSession,
        membership_id: uuid.UUID,
        society_id: uuid.UUID,
        req: MembershipStatusUpdateRequest,
    ) -> SocietyMembership:
        """Allows society admin to approve, reject, or suspend a resident's membership."""
        query = select(SocietyMembership).where(
            SocietyMembership.id == membership_id,
            SocietyMembership.society_id == society_id,
        )
        result = await db.execute(query)
        membership = result.scalar_one_or_none()
        if not membership:
            raise NotFoundError("SocietyMembership", membership_id)

        membership.status = req.status.value
        if req.status == MembershipStatus.APPROVED:
            membership.verified_at = datetime.now(timezone.utc)
        elif req.status in [MembershipStatus.REJECTED, MembershipStatus.SUSPENDED]:
            membership.verified_at = None

        db.add(membership)
        await db.commit()
        await db.refresh(membership)
        return membership

    @staticmethod
    async def list_society_members(
        db: AsyncSession,
        society_id: uuid.UUID,
        status: Optional[str] = None,
    ) -> List[SocietyMembership]:
        """Lists members belonging to a society with eager user and unit loading."""
        query = (
            select(SocietyMembership)
            .where(SocietyMembership.society_id == society_id)
            .options(
                selectinload(SocietyMembership.user),
                selectinload(SocietyMembership.unit),
            )
            .order_by(SocietyMembership.created_at.desc())
        )
        if status:
            query = query.where(SocietyMembership.status == status)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_user_memberships(
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> List[SocietyMembership]:
        """Lists all societies that a user is enrolled in."""
        query = (
            select(SocietyMembership)
            .where(SocietyMembership.user_id == user_id)
            .options(
                selectinload(SocietyMembership.society),
                selectinload(SocietyMembership.unit),
            )
            .order_by(SocietyMembership.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())
