"""
Shared FastAPI dependencies.
"""

import logging

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from icebreakers.auth.application.service import AuthService
from icebreakers.auth.domain.models import User
from icebreakers.auth.infrastructure.repository import UserRepository
from icebreakers.config import settings
from icebreakers.shared.database import get_db

logger = logging.getLogger("icebreakers")


async def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserRepository:
    return UserRepository(db)


async def get_auth_service(
    repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repo)


async def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    Extract the JWT from the HttpOnly cookie and resolve the current user.
    Raises 401 if the cookie is missing, invalid, or the user is inactive.
    """
    token = request.cookies.get(settings.cookie_name)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )

    user = await auth_service.get_current_user(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
        )
    return user


async def verify_csrf(request: Request):
    """
    Ensure the incoming request has a matching CSRF cookie and X-CSRF-Token header.
    """
    csrf_cookie = request.cookies.get("csrf_token")
    csrf_header = request.headers.get("x-csrf-token")
    if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
        client_ip = request.client.host if request.client else "unknown"
        logger.warning(f"CSRF token mismatch or missing for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token verification failed.",
        )
