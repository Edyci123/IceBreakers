"""
Auth service — business logic for registration, login, and token management.
"""

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import logging
from jose import JWTError, jwt

from icebreakers.auth.domain.models import User
from icebreakers.auth.domain.schemas import UserRegisterRequest
from icebreakers.auth.infrastructure.repository import UserRepository
from icebreakers.config import settings

logger = logging.getLogger("icebreakers")


class AuthService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    # ── Password helpers ──────────────────────────────────────

    @staticmethod
    def hash_password(plain: str) -> str:
        # bcrypt requires bytes
        pwd_bytes = plain.encode("utf-8")
        # Ensure password is <= 72 bytes as bcrypt limits it
        if len(pwd_bytes) > 72:
            pwd_bytes = pwd_bytes[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        pwd_bytes = plain.encode("utf-8")
        if len(pwd_bytes) > 72:
            pwd_bytes = pwd_bytes[:72]
        return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))

    # ── JWT helpers ───────────────────────────────────────────

    @staticmethod
    def create_access_token(user_id: uuid.UUID) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def decode_access_token(token: str) -> uuid.UUID | None:
        """Return the user UUID from a valid token, or None."""
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.jwt_algorithm]
            )
            user_id = payload.get("sub")
            if user_id is None:
                return None
            return uuid.UUID(user_id)
        except (JWTError, ValueError):
            return None

    # ── Use-cases ─────────────────────────────────────────────

    async def register(self, data: UserRegisterRequest) -> User:
        if await self._repo.email_exists(data.email):
            raise ValueError("A user with this email already exists.")

        user = User(
            email=data.email,
            hashed_password=self.hash_password(data.password),
            full_name=data.full_name,
        )
        return await self._repo.create(user)

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self._repo.get_by_email(email)
        if user is None or user.hashed_password is None:
            logger.warning(f"Failed login attempt for unknown email: {email}")
            return None
        if not self.verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {email} (invalid password)")
            return None
        if not user.is_active:
            logger.warning(f"Failed login attempt for user: {email} (account inactive)")
            return None
        logger.info(f"Successful login for user: {email}")
        return user

    async def get_current_user(self, token: str) -> User | None:
        user_id = self.decode_access_token(token)
        if user_id is None:
            return None
        user = await self._repo.get_by_id(user_id)
        if user is None or not user.is_active:
            return None
        return user
