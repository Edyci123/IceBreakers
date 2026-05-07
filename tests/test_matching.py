import pytest
from httpx import AsyncClient
from sqlalchemy import update

from icebreakers.auth.domain.models import User
from icebreakers.auth.domain.enums import UserRole
from tests.conftest import TestSessionLocal


async def make_admin(email: str):
    async with TestSessionLocal() as session:
        await session.execute(
            update(User).where(User.email == email).values(role=UserRole.ADMIN)
        )
        await session.commit()


async def register_and_profile(client: AsyncClient, email: str, bio: str, interests: list[str]):
    # Note: registering logs us in automatically
    res = await client.post("/api/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": email.split("@")[0]
    })
    assert res.status_code == 201

    csrf_res = await client.get("/api/auth/csrf")
    csrf_token = csrf_res.json()["csrf_token"]

    res = await client.put("/api/profile", json={
        "first_name": email.split("@")[0],
        "bio": bio,
        "interests": interests
    }, headers={"x-csrf-token": csrf_token})
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_trigger_matching_not_admin(authenticated_client: AsyncClient):
    """A regular user calling the endpoint should get 403 Forbidden."""
    res = await authenticated_client.post("/matching/trigger")
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_trigger_matching_success(client: AsyncClient):
    """Admin triggering the endpoint should succeed and create pairs."""
    # 1. Setup Admin
    admin_email = "admin@example.com"
    await register_and_profile(client, admin_email, "I am admin", ["management"])
    await make_admin(admin_email)

    # 2. Setup users
    await register_and_profile(client, "alice@example.com", "Love AI", ["AI", "ML"])
    await register_and_profile(client, "bob@example.com", "Love Data", ["AI", "Data"])
    await register_and_profile(client, "charlie@example.com", "Cars", ["auto", "racing"])
    await register_and_profile(client, "dave@example.com", "Motorsport", ["auto", "F1"])

    # 3. Log back in as admin
    res = await client.post("/api/auth/login", json={
        "email": admin_email,
        "password": "Password123!"
    })
    assert res.status_code == 200

    # 4. Trigger matching
    res = await client.post("/matching/trigger")
    assert res.status_code == 200
    data = res.json()
    assert data["message"] == "Matching triggered successfully"
    assert data["proposals_created"] > 0
    
    # 5. Trigger again, should create new pairs from remaining combinations
    res_second = await client.post("/matching/trigger")
    assert res_second.status_code == 200
    assert res_second.json()["proposals_created"] > 0
