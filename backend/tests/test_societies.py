"""Integration and multi-tenant isolation tests for housing societies and memberships."""

import pytest
from httpx import AsyncClient


async def _get_auth_header(client: AsyncClient, email: str, role: str = "RESIDENT") -> dict:
    """Helper to register and login a user, returning Authorization header."""
    password = "TestPassword123!"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": f"User {email.split('@')[0]}",
            "role": role,
        },
    )
    res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_society_lifecycle_and_multitenant_isolation(client: AsyncClient):
    """Verifies society creation, wings, memberships, and strict tenant isolation."""
    # 1. Setup Organizer / Society Admin 1
    admin_headers_1 = await _get_auth_header(client, "admin1@falcon.example.com", role="SOCIETY_ADMIN")

    # 2. Create Society 1 (Prestige Falcon City)
    soc1_payload = {
        "name": "Prestige Falcon City",
        "code": "PFC-BLR",
        "address_line1": "Kanakanagar, Konanakunte",
        "locality": "Anjanapura",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560062",
        "timezone": "Asia/Kolkata",
    }
    soc1_res = await client.post("/api/v1/societies", headers=admin_headers_1, json=soc1_payload)
    assert soc1_res.status_code == 201
    soc1_id = soc1_res.json()["data"]["id"]

    # 3. Add Wing and Unit to Society 1
    wing_res = await client.post(
        f"/api/v1/societies/{soc1_id}/wings",
        headers=admin_headers_1,
        json={"name": "Tower A"},
    )
    assert wing_res.status_code == 201
    wing_id = wing_res.json()["data"]["id"]

    unit_res = await client.post(
        f"/api/v1/societies/{soc1_id}/wings/{wing_id}/units",
        headers=admin_headers_1,
        json={"unit_number": "A-1204"},
    )
    assert unit_res.status_code == 201
    unit_id = unit_res.json()["data"]["id"]

    # 4. Resident 1 joins Society 1
    resident_headers_1 = await _get_auth_header(client, "resident1@falcon.example.com", role="RESIDENT")
    join_res = await client.post(
        f"/api/v1/societies/{soc1_id}/join",
        headers=resident_headers_1,
        json={"unit_id": unit_id, "role": "RESIDENT"},
    )
    assert join_res.status_code == 201
    membership1_id = join_res.json()["data"]["id"]
    assert join_res.json()["data"]["status"] == "PENDING"

    # 5. Society Admin 1 approves Resident 1
    approve_res = await client.patch(
        f"/api/v1/societies/{soc1_id}/members/{membership1_id}",
        headers=admin_headers_1,
        json={"status": "APPROVED"},
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["data"]["status"] == "APPROVED"

    # 6. Setup Society 2 (Sobha Forest Edge) with Admin 2
    admin_headers_2 = await _get_auth_header(client, "admin2@sobha.example.com", role="SOCIETY_ADMIN")
    soc2_payload = {
        "name": "Sobha Forest Edge",
        "code": "SFE-BLR",
        "address_line1": "Kanakapura Road",
        "locality": "Thalaghattapura",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560061",
        "timezone": "Asia/Kolkata",
    }
    soc2_res = await client.post("/api/v1/societies", headers=admin_headers_2, json=soc2_payload)
    assert soc2_res.status_code == 201
    soc2_id = soc2_res.json()["data"]["id"]

    # =========================================================================
    # NEGATIVE ACCESS CONTROL & MULTI-TENANT ISOLATION TESTS
    # =========================================================================

    # Test A: Resident 1 (from Society 1) cannot list members of Society 2
    unauth_members_res = await client.get(
        f"/api/v1/societies/{soc2_id}/members",
        headers=resident_headers_1,
    )
    assert unauth_members_res.status_code == 403
    assert unauth_members_res.json()["code"] == "PERMISSION_DENIED"

    # Test B: Resident 1 cannot list members of their OWN Society 1 (only Society Admins can)
    resident_list_members_res = await client.get(
        f"/api/v1/societies/{soc1_id}/members",
        headers=resident_headers_1,
    )
    assert resident_list_members_res.status_code == 403

    # Test C: Society Admin 1 cannot manage or modify Society 2 members
    admin1_access_soc2 = await client.get(
        f"/api/v1/societies/{soc2_id}/members",
        headers=admin_headers_1,
    )
    assert admin1_access_soc2.status_code == 403

    # Test D: Resident 1 cannot create wings in Society 1
    resident_add_wing = await client.post(
        f"/api/v1/societies/{soc1_id}/wings",
        headers=resident_headers_1,
        json={"name": "Rogue Tower"},
    )
    assert resident_add_wing.status_code == 403

    # Test E: Public listing works with filter
    list_res = await client.get("/api/v1/societies?city=Bengaluru")
    assert list_res.status_code == 200
    assert list_res.json()["pagination"]["total_records"] >= 2
