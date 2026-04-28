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
# httpx test client uses "test" as host; cookies set for "localhost"
# won't be sent back. Clearing the domain makes cookies work on any host.
settings.cookie_domain = ""

from icebreakers.main import app  # noqa: E402 — must import after settings override


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


# ── Test database engine (SQLite async in-memory) ────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

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
        # Patch ARRAY columns to use JSON for SQLite (only once)
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


# ── HTTP client (with cookie persistence) ────────────────────
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
@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient) -> AsyncClient:
    """
    Register a test user and return a client with the auth cookie set.
    """
    response = await client.post(
        "/api/auth/register",
        json={
            "email": f"testuser_{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201, f"Registration failed: {response.text}"
    # Cookies are automatically captured by httpx client when domain matches
    return client
