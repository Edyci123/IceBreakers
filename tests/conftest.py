"""
Shared test fixtures for the IceBreakers test suite.
Uses an in-memory SQLite database for fast, isolated tests.

SQLite doesn't support PostgreSQL ARRAY, so we register a type adapter
that stores arrays as JSON text.
"""

import asyncio
import json
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.types import TypeDecorator

from icebreakers.shared.database import Base, get_db
from icebreakers.config import settings


# ── Override cookie domain for tests ─────────────────────────
settings.cookie_domain = ""

from icebreakers.main import app  # noqa: E402

# ── SQLite ARRAY workaround ──────────────────────────────────
from sqlalchemy.dialects.postgresql import ARRAY  # noqa: E402


class JSONEncodedArray(TypeDecorator):
    """Stores a list as a JSON-encoded string in SQLite."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value


# ── Disable rate limiting in tests ───────────────────────────
from icebreakers.shared.rate_limit import limiter  # noqa: E402

limiter.enabled = False


# ── Async event-loop scope ───────────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Test database engine (SQLite async) ────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///test.db"

from sqlalchemy.pool import StaticPool

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

_array_patched = False


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop them after."""
    global _array_patched
    if not _array_patched:
        from icebreakers.profile.domain.models import Profile
        for col in Profile.__table__.columns:
            if isinstance(col.type, ARRAY):
                col.type = JSONEncodedArray()
        _array_patched = True

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override the get_db dependency with the test session."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


# ── HTTP clients ─────────────────────────────────────────────
@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client with cookie jar support."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac


# ── Auth helpers ─────────────────────────────────────────────
async def _get_csrf(client: AsyncClient) -> dict[str, str]:
    """Fetch a CSRF token and return the header dict to include in requests."""
    resp = await client.get("/api/auth/csrf")
    csrf_token = resp.json()["csrf_token"]
    return {"x-csrf-token": csrf_token}


async def _register_user(
    client: AsyncClient,
    email: str | None = None,
    full_name: str = "Test User",
) -> str:
    """Register a user on the given client, return their user ID."""
    if email is None:
        email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    response = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": full_name,
        },
    )
    assert response.status_code == 201, f"Registration failed: {response.text}"
    return response.json()["id"]


@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient) -> AsyncClient:
    """Register a test user and return a client with the auth cookie set."""
    await _register_user(client)
    return client


@pytest_asyncio.fixture
async def two_clients():
    """
    Create two independent authenticated clients for two-party meeting tests.
    Returns (client_a, user_a_id, client_b, user_b_id).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client_a:
        async with AsyncClient(transport=transport, base_url="http://test") as client_b:
            user_a_id = await _register_user(client_a, email="user_a@example.com", full_name="User A")
            user_b_id = await _register_user(client_b, email="user_b@example.com", full_name="User B")
            yield client_a, user_a_id, client_b, user_b_id
