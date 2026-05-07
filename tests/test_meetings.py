"""
Tests for the meetings module.
Covers proposal creation, accept/reject flow, deletion, filtering,
time-gate logic, and access control.
"""

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient

from conftest import _get_csrf

@pytest.mark.asyncio
async def test_create_proposal_unauthenticated(client: AsyncClient):
    """POST without auth should return 401."""
    response = await client.post(
        "/api/meetings/proposals",
        json={"receiver_id": "00000000-0000-0000-0000-000000000001"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_proposal_valid(two_clients):
    """Creating a proposal should return 201 with correct statuses."""
    client_a, user_a_id, client_b, user_b_id = two_clients
    csrf = await _get_csrf(client_a)

    response = await client_a.post(
        "/api/meetings/proposals",
        json={
            "receiver_id": user_b_id,
            "meeting_type": "coffeebreak",
            "duration_minutes": 15,
            "message": "Let's grab coffee!",
        },
        headers=csrf,
    )
    assert response.status_code == 201

    data = response.json()
    assert data["proposer_id"] == user_a_id
    assert data["receiver_id"] == user_b_id
    assert data["proposer_status"] == "accepted"  # auto-joined
    assert data["receiver_status"] == "pending"
    assert data["source"] == "user"
    assert data["meeting_type"] == "coffeebreak"
    assert data["duration_minutes"] == 15
    assert data["message"] == "Let's grab coffee!"


@pytest.mark.asyncio
async def test_create_proposal_self(two_clients):
    """Cannot create a meeting with yourself."""
    client_a, user_a_id, _, _ = two_clients
    csrf = await _get_csrf(client_a)

    response = await client_a.post(
        "/api/meetings/proposals",
        json={"receiver_id": user_a_id},
        headers=csrf,
    )
    assert response.status_code == 400
    assert "yourself" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_proposal_duplicate_pending(two_clients):
    """Duplicate pending proposal to same user should return 409."""
    client_a, _, _, user_b_id = two_clients
    csrf = await _get_csrf(client_a)

    # First proposal
    resp1 = await client_a.post(
        "/api/meetings/proposals",
        json={"receiver_id": user_b_id},
        headers=csrf,
    )
    assert resp1.status_code == 201

    # Duplicate
    resp2 = await client_a.post(
        "/api/meetings/proposals",
        json={"receiver_id": user_b_id},
        headers=csrf,
    )
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_create_proposal_nonexistent_receiver(two_clients):
    """Receiver that doesn't exist should return 404."""
    client_a, _, _, _ = two_clients
    csrf = await _get_csrf(client_a)

    response = await client_a.post(
        "/api/meetings/proposals",
        json={"receiver_id": "00000000-0000-0000-0000-000000000099"},
        headers=csrf,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_coffeebreak_over_30min(two_clients):
    """Coffeebreak with > 30 min duration should be rejected."""
    client_a, _, _, user_b_id = two_clients
    csrf = await _get_csrf(client_a)

    response = await client_a.post(
        "/api/meetings/proposals",
        json={
            "receiver_id": user_b_id,
            "meeting_type": "coffeebreak",
            "duration_minutes": 45,
        },
        headers=csrf,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_other_type_over_30min(two_clients):
    """Other type with > 30 min duration should be allowed."""
    client_a, _, _, user_b_id = two_clients
    csrf = await _get_csrf(client_a)

    response = await client_a.post(
        "/api/meetings/proposals",
        json={
            "receiver_id": user_b_id,
            "meeting_type": "other",
            "duration_minutes": 60,
        },
        headers=csrf,
    )
    assert response.status_code == 201
    assert response.json()["meeting_type"] == "other"

@pytest.mark.asyncio
async def test_get_proposals_empty(two_clients):
    """No proposals should return an empty list."""
    client_a, _, _, _ = two_clients

    response = await client_a.get("/api/meetings/proposals")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_proposals_lists_own(two_clients):
    """Should return proposals involving the user."""
    client_a, user_a_id, client_b, user_b_id = two_clients
    csrf_a = await _get_csrf(client_a)

    # Create a proposal
    await client_a.post(
        "/api/meetings/proposals",
        json={"receiver_id": user_b_id},
        headers=csrf_a,
    )

    # User A sees it (as proposer)
    resp_a = await client_a.get("/api/meetings/proposals")
    assert resp_a.status_code == 200
    assert len(resp_a.json()) == 1

    # User B also sees it (as receiver)
    resp_b = await client_b.get("/api/meetings/proposals")
    assert resp_b.status_code == 200
    assert len(resp_b.json()) == 1


@pytest.mark.asyncio
async def test_get_proposals_filter_status(two_clients):
    """?status=pending should only return meetings where user's status is pending."""
    client_a, _, client_b, user_b_id = two_clients
    csrf_a = await _get_csrf(client_a)

    # Create a proposal (A is auto-accepted, B is pending)
    await client_a.post(
        "/api/meetings/proposals",
        json={"receiver_id": user_b_id},
        headers=csrf_a,
    )

    # User A filters by pending — should be empty (A is accepted)
    resp = await client_a.get("/api/meetings/proposals?status=pending")
    assert resp.status_code == 200
    assert len(resp.json()) == 0

    # User B filters by pending — should find it
    resp_b = await client_b.get("/api/meetings/proposals?status=pending")
    assert resp_b.status_code == 200
    assert len(resp_b.json()) == 1


@pytest.mark.asyncio
async def test_get_proposals_filter_role(two_clients):
    """?role=receiver should only return meetings where user is the receiver."""
    client_a, _, client_b, user_b_id = two_clients
    csrf_a = await _get_csrf(client_a)

    await client_a.post(
        "/api/meetings/proposals",
        json={"receiver_id": user_b_id},
        headers=csrf_a,
    )

    # User A as receiver — should be empty
    resp = await client_a.get("/api/meetings/proposals?role=receiver")
    assert resp.status_code == 200
    assert len(resp.json()) == 0

    # User A as proposer — should find it
    resp2 = await client_a.get("/api/meetings/proposals?role=proposer")
    assert resp2.status_code == 200
    assert len(resp2.json()) == 1

@pytest.mark.asyncio
async def test_accept_proposal(two_clients):
    """Receiver accepts → their status becomes accepted."""
    client_a, _, client_b, user_b_id = two_clients
    csrf_a = await _get_csrf(client_a)
    csrf_b = await _get_csrf(client_b)

    # Create
    create_resp = await client_a.post(
        "/api/meetings/proposals",
        json={
            "receiver_id": user_b_id,
            "proposed_time": (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat(),
        },
        headers=csrf_a,
    )
    meeting_id = create_resp.json()["id"]

    # Receiver accepts
    accept_resp = await client_b.put(
        f"/api/meetings/proposals/{meeting_id}/accept",
        headers=csrf_b,
    )
    assert accept_resp.status_code == 200
    assert accept_resp.json()["receiver_status"] == "accepted"
    assert accept_resp.json()["proposer_status"] == "accepted"


@pytest.mark.asyncio
async def test_accept_proposal_wrong_user(two_clients):
    """A non-participant cannot accept."""
    client_a, _, client_b, user_b_id = two_clients
    csrf_a = await _get_csrf(client_a)

    create_resp = await client_a.post(
        "/api/meetings/proposals",
        json={
            "receiver_id": user_b_id,
            "proposed_time": (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat(),
        },
        headers=csrf_a,
    )
    meeting_id = create_resp.json()["id"]

    # Create a third user
    transport = client_a._transport
    async with AsyncClient(transport=transport, base_url="http://test") as client_c:
        from conftest import _register_user
        await _register_user(client_c, email="user_c@example.com", full_name="User C")
        csrf_c = await _get_csrf(client_c)

        resp = await client_c.put(
            f"/api/meetings/proposals/{meeting_id}/accept",
            headers=csrf_c,
        )
        assert resp.status_code == 409  # "not a participant"


@pytest.mark.asyncio
async def test_reject_proposal(two_clients):
    """Receiver rejects → their status becomes rejected."""
    client_a, _, client_b, user_b_id = two_clients
    csrf_a = await _get_csrf(client_a)
    csrf_b = await _get_csrf(client_b)

    create_resp = await client_a.post(
        "/api/meetings/proposals",
        json={
            "receiver_id": user_b_id,
            "proposed_time": (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat(),
        },
        headers=csrf_a,
    )
    meeting_id = create_resp.json()["id"]

    reject_resp = await client_b.put(
        f"/api/meetings/proposals/{meeting_id}/reject",
        headers=csrf_b,
    )
    assert reject_resp.status_code == 200
    assert reject_resp.json()["receiver_status"] == "rejected"

@pytest.mark.asyncio
async def test_change_decision_allowed(two_clients):
    """Should allow changing accepted → rejected when >= 1h away."""
    client_a, _, client_b, user_b_id = two_clients
    csrf_a = await _get_csrf(client_a)
    csrf_b = await _get_csrf(client_b)

    create_resp = await client_a.post(
        "/api/meetings/proposals",
        json={
            "receiver_id": user_b_id,
            "proposed_time": (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat(),
        },
        headers=csrf_a,
    )
    meeting_id = create_resp.json()["id"]

    # Accept first
    await client_b.put(
        f"/api/meetings/proposals/{meeting_id}/accept",
        headers=csrf_b,
    )

    # Change to reject — should work (3 hours away)
    reject_resp = await client_b.put(
        f"/api/meetings/proposals/{meeting_id}/reject",
        headers=csrf_b,
    )
    assert reject_resp.status_code == 200
    assert reject_resp.json()["receiver_status"] == "rejected"


@pytest.mark.asyncio
async def test_change_decision_too_late(two_clients):
    """Should block status change when < 1h before meeting."""
    client_a, _, client_b, user_b_id = two_clients
    csrf_a = await _get_csrf(client_a)
    csrf_b = await _get_csrf(client_b)

    # Create meeting starting in 30 minutes
    create_resp = await client_a.post(
        "/api/meetings/proposals",
        json={
            "receiver_id": user_b_id,
            "proposed_time": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
        },
        headers=csrf_a,
    )
    meeting_id = create_resp.json()["id"]

    # Try to accept — should be blocked (only 30 min away)
    resp = await client_b.put(
        f"/api/meetings/proposals/{meeting_id}/accept",
        headers=csrf_b,
    )
    assert resp.status_code == 409
    assert "1 hour" in resp.json()["detail"].lower()

@pytest.mark.asyncio
async def test_delete_own_meeting(two_clients):
    """Creator can delete a meeting if receiver hasn't joined."""
    client_a, _, _, user_b_id = two_clients
    csrf_a = await _get_csrf(client_a)

    create_resp = await client_a.post(
        "/api/meetings/proposals",
        json={"receiver_id": user_b_id},
        headers=csrf_a,
    )
    meeting_id = create_resp.json()["id"]

    delete_resp = await client_a.delete(
        f"/api/meetings/proposals/{meeting_id}",
        headers=csrf_a,
    )
    assert delete_resp.status_code == 204

    # Verify it's gone
    get_resp = await client_a.get(f"/api/meetings/proposals/{meeting_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_meeting_receiver_joined(two_clients):
    """Cannot delete if receiver has accepted."""
    client_a, _, client_b, user_b_id = two_clients
    csrf_a = await _get_csrf(client_a)
    csrf_b = await _get_csrf(client_b)

    create_resp = await client_a.post(
        "/api/meetings/proposals",
        json={
            "receiver_id": user_b_id,
            "proposed_time": (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat(),
        },
        headers=csrf_a,
    )
    meeting_id = create_resp.json()["id"]

    # Receiver accepts
    await client_b.put(
        f"/api/meetings/proposals/{meeting_id}/accept",
        headers=csrf_b,
    )

    # Creator tries to delete — should fail
    delete_resp = await client_a.delete(
        f"/api/meetings/proposals/{meeting_id}",
        headers=csrf_a,
    )
    assert delete_resp.status_code == 409


@pytest.mark.asyncio
async def test_delete_meeting_not_creator(two_clients):
    """Non-creator cannot delete a meeting."""
    client_a, _, client_b, user_b_id = two_clients
    csrf_a = await _get_csrf(client_a)
    csrf_b = await _get_csrf(client_b)

    create_resp = await client_a.post(
        "/api/meetings/proposals",
        json={"receiver_id": user_b_id},
        headers=csrf_a,
    )
    meeting_id = create_resp.json()["id"]

    delete_resp = await client_b.delete(
        f"/api/meetings/proposals/{meeting_id}",
        headers=csrf_b,
    )
    assert delete_resp.status_code == 409

@pytest.mark.asyncio
async def test_get_single_proposal(two_clients):
    """GET by ID should return the correct proposal."""
    client_a, user_a_id, _, user_b_id = two_clients
    csrf_a = await _get_csrf(client_a)

    create_resp = await client_a.post(
        "/api/meetings/proposals",
        json={"receiver_id": user_b_id, "message": "Hello!"},
        headers=csrf_a,
    )
    meeting_id = create_resp.json()["id"]

    get_resp = await client_a.get(f"/api/meetings/proposals/{meeting_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == meeting_id
    assert data["proposer_id"] == user_a_id
    assert data["message"] == "Hello!"


@pytest.mark.asyncio
async def test_get_single_proposal_not_participant(two_clients):
    """Non-participant GET should return 403."""
    client_a, _, _, user_b_id = two_clients
    csrf_a = await _get_csrf(client_a)

    create_resp = await client_a.post(
        "/api/meetings/proposals",
        json={"receiver_id": user_b_id},
        headers=csrf_a,
    )
    meeting_id = create_resp.json()["id"]

    # Third user
    transport = client_a._transport
    async with AsyncClient(transport=transport, base_url="http://test") as client_c:
        from conftest import _register_user
        await _register_user(client_c, email="user_c2@example.com", full_name="User C")

        resp = await client_c.get(f"/api/meetings/proposals/{meeting_id}")
        assert resp.status_code == 403
