from __future__ import annotations
"""FastAPI dependencies for auth and RBAC."""
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError, ExpiredSignatureError

from . import auth, db

security = HTTPBearer(auto_error=False)


def get_current_user(creds: HTTPAuthorizationCredentials | None = Depends(security)):
    if not creds or not creds.credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Требуется авторизация')
    try:
        payload = auth.decode_token(creds.credentials)
    except ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Сессия истекла')
    except InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Недействительный токен')
    if payload.get('type') != 'access':
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Некорректный тип токена')
    user = db.one('SELECT * FROM users WHERE id = ? AND NOT disabled', (int(payload['sub']),))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Пользователь не найден или отключён')
    return dict(user)


def require_role(*roles: str):
    def _dep(user: dict = Depends(get_current_user)):
        if user['role'] not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, 'Недостаточно прав')
        return user
    return _dep


def can_view_finance(user: dict) -> bool:
    return user['role'] in ('super_admin', 'admin')


def can_manage_users(user: dict) -> bool:
    return user['role'] == 'super_admin'


def client_ip(request: Request) -> str:
    fwd = request.headers.get('x-forwarded-for')
    if fwd:
        return fwd.split(',')[0].strip()
    return request.client.host if request.client else ''
