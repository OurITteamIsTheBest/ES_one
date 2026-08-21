from __future__ import annotations
import os
import secrets
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / '.env', extra='ignore')

    # Environment flag — "production" enables strict security checks (HTTPS, no default secrets)
    env: str = 'development'
    # JWT
    jwt_secret: str = secrets.token_urlsafe(48)
    access_ttl_seconds: int = 15 * 60
    refresh_ttl_seconds: int = 7 * 24 * 3600

    # DB (only used for local dev — production uses TURSO_URL / TURSO_AUTH_TOKEN)
    db_path: str = str(BASE_DIR / 'backend' / 'esone.db')

    # Data
    data_json: str = str(BASE_DIR / 'data' / 'dashboard_data.json')

    # First super admin
    bootstrap_email: str = 'zhunussov_zh@eng-services.kz'
    bootstrap_name: str = 'Жунусов Жанат'
    bootstrap_password: str = 'ES-One-2026'

    # Cookies & CORS
    cookie_secure: bool = False
    cookie_domain: Optional[str] = None
    frontend_origins: str = 'http://localhost:8000,http://127.0.0.1:8000'

    # Login security
    login_max_failed: int = 5
    login_lockout_seconds: int = 15 * 60


settings = Settings()

# Production safety checks — fail fast if secrets aren't set properly
_prod = settings.env.lower() in ('production', 'prod')
if _prod:
    if not os.environ.get('JWT_SECRET'):
        raise RuntimeError(
            'JWT_SECRET must be set explicitly in production (never leave it as auto-generated default).'
        )
    if len(settings.jwt_secret) < 32:
        raise RuntimeError('JWT_SECRET is too short — use at least 32 random characters.')
    if not settings.cookie_secure:
        raise RuntimeError('COOKIE_SECURE must be true in production (HTTPS only).')
    if settings.bootstrap_password.lower() in ('es-one-2026', 'changeme', 'password'):
        raise RuntimeError('Change BOOTSTRAP_PASSWORD from its default before running in production.')
