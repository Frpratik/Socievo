"""Housing Societies, Wings, Units, and Memberships REST endpoints."""

import math
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import (
    get_current_active_user,
    require_role,
    require_society_admin,
    require_society_member,
)
from app.db.session import get_async_session
from app.models.society import SocietyMembership
from app.models.user import User, UserRole
from app.schemas.common import APIResponse, PaginatedResponse, PaginationMeta
from app.schemas.society import (
    MembershipJoinRequest,
    MembershipResponse,
    MembershipStatusUpdateRequest,
    SocietyCreateRequest,
    SocietyResponse,
    UnitCreateRequest,
    UnitResponse,
    WingCreateRequest,
    WingResponse,
)
from app.services.society_service import SocietyService

router = APIRouter(prefix="/societies", tags=["Societies & Memberships"])


@router.post(
    "",
    response_model=APIResponse[SocietyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new residential society",
)
async def create_society(
    req: SocietyCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[SocietyResponse]:
    """Creates a new society and assigns the creator as initial society admin."""
    society = await SocietyService.create_society(db, req, creator=current_user)
    return APIResponse(
        status="success",
        data=SocietyResponse.model_validate(society),
        message=f"Society '{society.name}' created successfully.",
    )


@router.get(
    "",
    response_model=PaginatedResponse[SocietyResponse],
    summary="List registered societies with search and city filter",
)
async def list_societies(
    city: Optional[str] = Query(None, description="Filter by city name"),
    search: Optional[str] = Query(None, description="Search by name, code, locality"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
) -> PaginatedResponse[SocietyResponse]:
    """Returns a paginated directory of societies."""
    societies, total_count = await SocietyService.list_societies(
        db, city=city, search=search, page=page, page_size=page_size
    )
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0

    return PaginatedResponse(
        status="success",
        items=[SocietyResponse.model_validate(s) for s in societies],
        pagination=PaginationMeta(
            total_records=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        ),
    )


@router.get(
    "/my-memberships",
    response_model=APIResponse[List[MembershipResponse]],
    summary="List societies the current user belongs to",
)
async def get_my_memberships(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[List[MembershipResponse]]:
    """Retrieves all society enrollments for the authenticated resident."""
    memberships = await SocietyService.get_user_memberships(db, current_user.id)
    return APIResponse(
        status="success",
        data=[MembershipResponse.model_validate(m) for m in memberships],
    )


@router.get(
    "/{society_id}",
    response_model=APIResponse[SocietyResponse],
    summary="Get society details by ID",
)
async def get_society(
    society_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[SocietyResponse]:
    """Fetches society metadata."""
    society = await SocietyService.get_society_by_id(db, society_id)
    return APIResponse(
        status="success",
        data=SocietyResponse.model_validate(society),
    )


@router.post(
    "/{society_id}/wings",
    response_model=APIResponse[WingResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add a wing/tower to the society",
)
async def add_wing(
    req: WingCreateRequest,
    society_id: uuid.UUID,
    _membership: SocietyMembership = Depends(require_society_admin),
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[WingResponse]:
    """Adds a tower/building to the society (Society Admin required)."""
    wing = await SocietyService.add_wing(db, society_id, req)
    return APIResponse(
        status="success",
        data=WingResponse.model_validate(wing),
        message=f"Wing '{wing.name}' added successfully.",
    )


@router.post(
    "/{society_id}/wings/{wing_id}/units",
    response_model=APIResponse[UnitResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add a residential unit to a wing",
)
async def add_unit(
    req: UnitCreateRequest,
    society_id: uuid.UUID,
    wing_id: uuid.UUID,
    _membership: SocietyMembership = Depends(require_society_admin),
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[UnitResponse]:
    """Adds a flat/unit to a tower/wing (Society Admin required)."""
    unit = await SocietyService.add_unit(db, wing_id, req)
    return APIResponse(
        status="success",
        data=UnitResponse.model_validate(unit),
        message=f"Unit '{unit.unit_number}' registered successfully.",
    )


@router.get(
    "/{society_id}/wings",
    response_model=APIResponse[List[WingResponse]],
    summary="List wings and units in a society",
)
async def list_wings(
    society_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[List[WingResponse]]:
    """Returns all wings and their residential units."""
    wings = await SocietyService.list_wings(db, society_id)
    return APIResponse(
        status="success",
        data=[WingResponse.model_validate(w) for w in wings],
    )


@router.post(
    "/{society_id}/join",
    response_model=APIResponse[MembershipResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit membership request to join a society",
)
async def join_society(
    req: MembershipJoinRequest,
    society_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[MembershipResponse]:
    """Allows a resident to request membership in a society."""
    membership = await SocietyService.request_membership(
        db, society_id=society_id, user=current_user, req=req
    )
    return APIResponse(
        status="success",
        data=MembershipResponse.model_validate(membership),
        message="Membership request submitted. Awaiting approval by Society Admin.",
    )


@router.get(
    "/{society_id}/members",
    response_model=APIResponse[List[MembershipResponse]],
    summary="List members and membership requests (Society Admin only)",
)
async def list_members(
    society_id: uuid.UUID,
    status_filter: Optional[str] = Query(None, alias="status"),
    _admin_guard: SocietyMembership = Depends(require_society_admin),
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[List[MembershipResponse]]:
    """Multi-tenant protected: lists members for the authorized society."""
    members = await SocietyService.list_society_members(
        db, society_id=society_id, status=status_filter
    )
    return APIResponse(
        status="success",
        data=[MembershipResponse.model_validate(m) for m in members],
    )


@router.patch(
    "/{society_id}/members/{membership_id}",
    response_model=APIResponse[MembershipResponse],
    summary="Approve or reject a resident membership request (Society Admin only)",
)
async def update_membership_status(
    req: MembershipStatusUpdateRequest,
    society_id: uuid.UUID,
    membership_id: uuid.UUID,
    _admin_guard: SocietyMembership = Depends(require_society_admin),
    db: AsyncSession = Depends(get_async_session),
) -> APIResponse[MembershipResponse]:
    """Multi-tenant protected: updates membership approval state."""
    membership = await SocietyService.update_membership_status(
        db, membership_id=membership_id, society_id=society_id, req=req
    )
    return APIResponse(
        status="success",
        data=MembershipResponse.model_validate(membership),
        message=f"Membership status updated to {req.status.value}.",
    )
