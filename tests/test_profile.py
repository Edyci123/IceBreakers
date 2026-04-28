"""
Tests for the profile module.
Covers GET /api/profile, PUT /api/profile, validations, and the
'profile complete' flag.
"""

import pytest
from httpx import AsyncClient


# ── Helper ────────────────────────────────────────────────────

async def _get_csrf(client: AsyncClient) -> dict[str, str]:
    """Fetch a CSRF token and return the header dict to include in requests."""
    resp = await client.get("/api/auth/csrf")
    csrf_token = resp.json()["csrf_token"]
    return {"x-csrf-token": csrf_token}


# ── GET /api/profile ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_profile_unauthenticated(client: AsyncClient):
    """GET /api/profile without auth should return 401."""
    response = await client.get("/api/profile")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile_auto_creates(authenticated_client: AsyncClient):
    """GET /api/profile for a new user should auto-create an empty profile."""
    response = await authenticated_client.get("/api/profile")
    assert response.status_code == 200

    data = response.json()
    assert data["first_name"] is None
    assert data["middle_name"] is None
    assert data["last_name"] is None
    assert data["bio"] is None
    assert data["interests"] is None
    assert data["avatar_url"] is None
    assert data["location"] is None
    assert data["is_profile_complete"] is False
    assert "user_id" in data
    assert "id" in data


@pytest.mark.asyncio
async def test_get_profile_idempotent(authenticated_client: AsyncClient):
    """Calling GET /api/profile twice should return the same profile."""
    resp1 = await authenticated_client.get("/api/profile")
    resp2 = await authenticated_client.get("/api/profile")
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json()["id"] == resp2.json()["id"]


# ── PUT /api/profile ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_profile_unauthenticated(client: AsyncClient):
    """PUT /api/profile without auth should be rejected (CSRF check runs first → 403)."""
    response = await client.put(
        "/api/profile",
        json={"bio": "Hello"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_profile_valid(authenticated_client: AsyncClient):
    """PUT /api/profile with valid data should update and return the profile."""
    csrf_headers = await _get_csrf(authenticated_client)

    response = await authenticated_client.put(
        "/api/profile",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "bio": "I love networking!",
            "interests": ["AI", "hiking"],
        },
        headers=csrf_headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["bio"] == "I love networking!"
    assert data["interests"] == ["AI", "hiking"]
    assert data["is_profile_complete"] is True


@pytest.mark.asyncio
async def test_update_profile_partial(authenticated_client: AsyncClient):
    """PUT with only some fields should preserve others."""
    csrf_headers = await _get_csrf(authenticated_client)

    # First update: set bio
    await authenticated_client.put(
        "/api/profile",
        json={"bio": "My bio"},
        headers=csrf_headers,
    )

    # Second update: set first_name only
    response = await authenticated_client.put(
        "/api/profile",
        json={"first_name": "Alice"},
        headers=csrf_headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["first_name"] == "Alice"
    assert data["bio"] == "My bio"  # preserved from first update


@pytest.mark.asyncio
async def test_profile_complete_flag(authenticated_client: AsyncClient):
    """Profile should be marked complete only when all required fields are set."""
    csrf_headers = await _get_csrf(authenticated_client)

    # Partial — not complete
    await authenticated_client.put(
        "/api/profile",
        json={"first_name": "John", "last_name": "Doe"},
        headers=csrf_headers,
    )
    response = await authenticated_client.get("/api/profile")
    assert response.json()["is_profile_complete"] is False

    # Add bio — still not complete (no interests)
    await authenticated_client.put(
        "/api/profile",
        json={"bio": "Hello!"},
        headers=csrf_headers,
    )
    response = await authenticated_client.get("/api/profile")
    assert response.json()["is_profile_complete"] is False

    # Add interests — now complete
    await authenticated_client.put(
        "/api/profile",
        json={"interests": ["coding"]},
        headers=csrf_headers,
    )
    response = await authenticated_client.get("/api/profile")
    assert response.json()["is_profile_complete"] is True


# ── Validation ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_profile_bio_too_long(authenticated_client: AsyncClient):
    """Bio exceeding 1000 chars should be rejected with 422."""
    csrf_headers = await _get_csrf(authenticated_client)

    response = await authenticated_client.put(
        "/api/profile",
        json={"bio": "x" * 1001},
        headers=csrf_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_profile_too_many_interests(authenticated_client: AsyncClient):
    """More than 20 interest tags should be rejected with 422."""
    csrf_headers = await _get_csrf(authenticated_client)

    response = await authenticated_client.put(
        "/api/profile",
        json={"interests": [f"tag_{i}" for i in range(21)]},
        headers=csrf_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_profile_interest_tag_too_long(authenticated_client: AsyncClient):
    """An interest tag exceeding 50 chars should be rejected with 422."""
    csrf_headers = await _get_csrf(authenticated_client)

    response = await authenticated_client.put(
        "/api/profile",
        json={"interests": ["x" * 51]},
        headers=csrf_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_profile_empty_interest_tag(authenticated_client: AsyncClient):
    """Empty string interest tags should be rejected."""
    csrf_headers = await _get_csrf(authenticated_client)

    response = await authenticated_client.put(
        "/api/profile",
        json={"interests": ["valid", "  ", ""]},
        headers=csrf_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_profile_first_name_too_long(authenticated_client: AsyncClient):
    """First name exceeding 100 chars should be rejected."""
    csrf_headers = await _get_csrf(authenticated_client)

    response = await authenticated_client.put(
        "/api/profile",
        json={"first_name": "A" * 101},
        headers=csrf_headers,
    )
    assert response.status_code == 422
