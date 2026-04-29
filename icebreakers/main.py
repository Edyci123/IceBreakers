"""
IceBreakers — FastAPI application entry point.
"""

import logging
import logging.handlers
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from icebreakers.auth.api.router import router as auth_router
from icebreakers.meetings.api.router import router as meetings_router
from icebreakers.profile.api.router import router as profile_router
from icebreakers.shared.database import engine, Base
from icebreakers.shared.rate_limit import limiter

logger = logging.getLogger("icebreakers")
logger.setLevel(logging.INFO)
file_handler = logging.handlers.RotatingFileHandler(
    "icebreakers.log", maxBytes=10485760, backupCount=5
)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Shutdown: dispose of the engine connection pool.
    await engine.dispose()


app = FastAPI(
    title="IceBreakers API",
    description="AI-powered networking and meeting platform",
    version="0.1.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(meetings_router)

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "healthy"}
