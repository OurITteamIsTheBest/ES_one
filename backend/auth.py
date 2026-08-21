from __future__ import annotations
"""Password hashing (Argon2id) + JWT."""
import time
import secrets
import jwt
from argon2 import PasswordHasher, exceptions as argon2_exc
from .config import settings

ph = PasswordHasher()  # sensible defaults (Argon2id, memory ~64 MiB, iters 3, parallelism 4)


def hash_password(pw: str) -> str:
    return ph.hash(pw)


def verify_password(pw: str, hash_: str) -> bool:
    try:
        return ph.verify(hash_, pw)
    except argon2_exc.VerifyMismatchError:
        return False
    except argon2_exc.InvalidHashError:
        return False


def needs_rehash(hash_: str) -> bool:
    try:
        return ph.check_needs_rehash(hash_)
    except Exception:
        return False


def _now() -> int:
    return int(time.time())


def make_access_token(user_id: int, role: str) -> str:
    now = _now()
    payload = {
        'sub': str(user_id),
        'role': role,
        'iat': now,
        'exp': now + settings.access_ttl_seconds,
        'type': 'access',
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm='HS256')


def make_refresh_token(user_id: int) -> tuple[str, str, int]:
    """Returns (jwt, jti, exp_ts)."""
    now = _now()
    jti = secrets.token_urlsafe(24)
    exp = now + settings.refresh_ttl_seconds
    payload = {
        'sub': str(user_id),
        'jti': jti,
        'iat': now,
        'exp': exp,
        'type': 'refresh',
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm='HS256'), jti, exp


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=['HS256'])


_COMMON_PW = {
    'password','12345678','123456789','qwerty','letmein','welcome','admin',
    'admin1234','es-one-2026','password123','changeme','iloveyou','1qaz2wsx',
    'zaq12wsx','p@ssw0rd','test1234','abcd1234','company123',
}

def validate_password_strength(pw: str) -> str | None:
    """Returns error message if weak, None if OK. Rules aligned to NIST 800-63B + OWASP."""
    if len(pw) < 12:
        return 'Пароль должен быть не короче 12 символов'
    if len(pw) > 200:
        return 'Пароль слишком длинный (максимум 200 символов)'
    classes = 0
    if any(c.islower() for c in pw): classes += 1
    if any(c.isupper() for c in pw): classes += 1
    if any(c.isdigit() for c in pw): classes += 1
    if any(not c.isalnum() for c in pw): classes += 1
    if classes < 3:
        return 'Пароль должен содержать 3 из 4 групп: строчные, заглавные, цифры, спецсимволы'
    if pw.lower() in _COMMON_PW:
        return 'Пароль слишком распространён — выберите другой'
    # runs of same char / simple sequences
    if any(pw[i] == pw[i+1] == pw[i+2] == pw[i+3] for i in range(len(pw)-3)):
        return 'Пароль не должен содержать 4+ одинаковых символа подряд'
    return None
