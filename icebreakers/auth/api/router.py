"""
Auth API router — register, login, logout, me.
Sessions are managed via HttpOnly + Secure cookies (architecture §3.4).
"""

import secrets
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status

from icebreakers.auth.application.service import AuthService
from icebreakers.auth.domain.models import User
from icebreakers.auth.domain.schemas import (
    MessageResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from icebreakers.config import settings
from icebreakers.shared.dependencies import get_auth_service, get_current_user, verify_csrf
from icebreakers.shared.rate_limit import limiter

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_auth_cookie(response: Response, token: str) -> None:
    """Attach the JWT as an HttpOnly cookie to the response."""
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


def _clear_auth_cookie(response: Response) -> None:
    """Remove the auth cookie."""
    response.delete_cookie(
        key=settings.cookie_name,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        path="/",
    )


# ── Endpoints ─────────────────────────────────────────────────

@router.get(
    "/csrf",
    summary="Get a CSRF token",
)
async def get_csrf_token(response: Response):
    """Generates a CSRF token and sets it as a cookie for the client to return in headers."""
    token = secrets.token_urlsafe(32)
    response.set_cookie(
        key="csrf_token",
        value=token,
        httponly=False,  # Client JS needs to read this cookie
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        path="/",
    )
    return {"csrf_token": token}


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: UserRegisterRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    try:
        user = await auth_service.register(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    token = auth_service.create_access_token(user.id)
    _set_auth_cookie(response, token)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=UserResponse,
    summary="Login with email and password",
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: UserLoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    user = await auth_service.authenticate(data.email, data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = auth_service.create_access_token(user.id)
    _set_auth_cookie(response, token)
    return UserResponse.model_validate(user)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout (clear session cookie)",
    dependencies=[Depends(verify_csrf)],
)
async def logout(
    response: Response,
    _current_user: User = Depends(get_current_user),
) -> MessageResponse:
    _clear_auth_cookie(response)
    return MessageResponse(message="Successfully logged out.")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
async def me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)
