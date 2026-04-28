"""
Application configuration via pydantic-settings.
Loads values from environment variables or a .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ──────────────────────────────────────────────
    database_url: str = (
        "postgresql+asyncpg://icebreakers:icebreakers_secret@localhost:5432/icebreakers"
    )

    # ── Auth / JWT ────────────────────────────────────────────
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # ── Cookie ────────────────────────────────────────────────
    cookie_name: str = "icebreakers_session"
    cookie_domain: str = "localhost"
    cookie_secure: bool = False  # True in production (HTTPS only)
    cookie_httponly: bool = True
    cookie_samesite: str = "lax"

    # ── App ───────────────────────────────────────────────────
    app_name: str = "IceBreakers"
    debug: bool = True


settings = Settings()
