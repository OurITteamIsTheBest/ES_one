from __future__ import annotations
"""FastAPI backend for ES One.

Runs on http://localhost:8000. Serves /api/* and static /index.html frontend.
"""
import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from jwt import InvalidTokenError, ExpiredSignatureError

from . import auth, db, models, deps
from .config import settings, BASE_DIR

app = FastAPI(title='ES One API', version='1.0')

# Rate limit: brute-force protection on login
limiter = Limiter(key_func=get_remote_address, default_limits=[])
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={'detail': 'Слишком много запросов, попробуйте позже'})


# CORS (locked to configured origins)
_origins = [o.strip() for o in settings.frontend_origins.split(',') if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
    allow_headers=['Authorization', 'Content-Type'],
)


# Security headers
_PROD = settings.env.lower() in ('production', 'prod')
_CSP = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"

@app.middleware('http')
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['Referrer-Policy'] = 'no-referrer'
    resp.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=(), payment=(), usb=()'
    resp.headers['Content-Security-Policy'] = _CSP
    if _PROD:
        resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    resp.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    resp.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
    return resp


@app.on_event('startup')
def startup():
    # Best-effort init: don't crash the function if the DB is temporarily unreachable
    # (e.g. Neon cold-start). Migrations and bootstrap are also runnable via `python -m backend.init_db`.
    try:
        db.init()
        if not db.one('SELECT id FROM users WHERE role = ? LIMIT 1', ('super_admin',)):
            from .init_db import main as boot
            boot()
    except Exception as e:
        print(f'[startup] db init deferred: {e!r}')


# ==================== Audit ====================

def log_event(event: str, *, actor: dict | None = None, target: dict | None = None,
              ip: str | None = None, meta: dict | str | None = None):
    m = json.dumps(meta, ensure_ascii=False) if isinstance(meta, dict) else meta
    db.execute(
        'INSERT INTO audit_log (event, actor_id, actor_email, target_id, target_email, ip, meta) VALUES (?,?,?,?,?,?,?)',
        (event,
         actor['id'] if actor else None,
         actor['email'] if actor else None,
         target['id'] if target else None,
         target['email'] if target else None,
         ip,
         m),
    )


# ==================== Auth ====================

REFRESH_COOKIE = 'esone_rt'


def _set_refresh_cookie(response: Response, refresh_jwt: str):
    # SameSite=strict for refresh cookie — this endpoint doesn't need cross-site navigation.
    # Combined with the fact that access token lives only in JS memory (not in a cookie),
    # this eliminates CSRF risk on state-changing endpoints.
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh_jwt,
        max_age=settings.refresh_ttl_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite='strict',
        domain=settings.cookie_domain,
        path='/api/auth',
    )


def _clear_refresh_cookie(response: Response):
    response.delete_cookie(REFRESH_COOKIE, path='/api/auth', domain=settings.cookie_domain)


@app.post('/api/auth/login', response_model=models.LoginOut)
@limiter.limit('10/minute')
def login(request: Request, response: Response, body: models.LoginIn):
    ip = deps.client_ip(request)
    ua = request.headers.get('user-agent', '')[:255]
    user = db.one('SELECT * FROM users WHERE email = ?', (body.email,))
    # generic error message to avoid user-enumeration; but still check lockout on real users
    if not user:
        # tiny sleep to make timing similar to argon2 verify (~30ms)
        time.sleep(0.05)
        log_event('login_fail_unknown', ip=ip, meta={'email': body.email, 'ua': ua[:80]})
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Неверный email или пароль')
    if bool(user['disabled']):
        log_event('login_fail_disabled', target=dict(user), ip=ip)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Аккаунт отключён')
    # locked out?
    if user['locked_until']:
        lu = user['locked_until']
        try:
            if isinstance(lu, str):
                lu = datetime.fromisoformat(lu.replace('Z', '+00:00'))
            now = datetime.utcnow() if lu.tzinfo is None else datetime.now(lu.tzinfo)
            if now < lu:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Аккаунт временно заблокирован из-за неудачных попыток. Попробуйте позже.')
        except (ValueError, TypeError):
            pass

    if not auth.verify_password(body.password, user['password_hash']):
        fails = user['failed_attempts'] + 1
        lock_until = None
        if fails >= settings.login_max_failed:
            lock_until = datetime.utcnow() + timedelta(seconds=settings.login_lockout_seconds)
        db.execute('UPDATE users SET failed_attempts = ?, locked_until = ? WHERE id = ?', (fails, lock_until, user['id']))
        log_event('login_fail_bad_password', target=dict(user), ip=ip, meta={'failed_attempts': fails})
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Неверный email или пароль')

    # Rehash if params changed
    if auth.needs_rehash(user['password_hash']):
        db.execute('UPDATE users SET password_hash = ? WHERE id = ?', (auth.hash_password(body.password), user['id']))

    # success
    now_dt = datetime.utcnow()
    db.execute('UPDATE users SET failed_attempts = 0, locked_until = NULL, last_login_at = ? WHERE id = ?',
               (now_dt, user['id']))

    access = auth.make_access_token(user['id'], user['role'])
    refresh_jwt, jti, exp_ts = auth.make_refresh_token(user['id'])
    db.execute(
        'INSERT INTO refresh_tokens (jti, user_id, expires_at, user_agent, ip) VALUES (?,?,?,?,?)',
        (jti, user['id'], datetime.utcfromtimestamp(exp_ts), ua, ip),
    )
    _set_refresh_cookie(response, refresh_jwt)
    log_event('login_success', actor=dict(user), ip=ip, meta={'ua': ua[:80]})

    return models.LoginOut(
        access_token=access,
        user=models.UserOut(
            id=user['id'], email=user['email'], name=user['name'], role=user['role'],
            created_at=db.to_iso(user['created_at']),
            last_login_at=db.to_iso(now_dt),
            disabled=bool(user['disabled']),
        ),
    )


@app.post('/api/auth/refresh', response_model=models.LoginOut)
@limiter.limit('30/minute')
def refresh(request: Request, response: Response):
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Нет refresh-токена')
    try:
        payload = auth.decode_token(token)
    except (ExpiredSignatureError, InvalidTokenError):
        _clear_refresh_cookie(response)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Сессия истекла')
    if payload.get('type') != 'refresh':
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Неверный тип токена')
    jti = payload.get('jti')
    row = db.one('SELECT * FROM refresh_tokens WHERE jti = ?', (jti,))
    if not row:
        _clear_refresh_cookie(response)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Токен неизвестен')
    if bool(row['revoked']):
        # Refresh-token reuse detected → assume compromise. Nuke all sessions for this user.
        db.execute('UPDATE refresh_tokens SET revoked = TRUE WHERE user_id = ?', (row['user_id'],))
        log_event('refresh_reuse_detected', target={'id': row['user_id'], 'email': None},
                  ip=deps.client_ip(request), meta={'jti': jti})
        _clear_refresh_cookie(response)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Токен уже использован — все сессии закрыты в целях безопасности')
    user = db.one('SELECT * FROM users WHERE id = ? AND NOT disabled', (row['user_id'],))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Пользователь не найден')
    # Rotate: revoke old, issue new
    db.execute('UPDATE refresh_tokens SET revoked = TRUE WHERE jti = ?', (jti,))
    access = auth.make_access_token(user['id'], user['role'])
    new_refresh_jwt, new_jti, exp_ts = auth.make_refresh_token(user['id'])
    db.execute(
        'INSERT INTO refresh_tokens (jti, user_id, expires_at, user_agent, ip) VALUES (?,?,?,?,?)',
        (new_jti, user['id'], datetime.utcfromtimestamp(exp_ts),
         request.headers.get('user-agent', '')[:255], deps.client_ip(request)),
    )
    _set_refresh_cookie(response, new_refresh_jwt)
    return models.LoginOut(
        access_token=access,
        user=models.UserOut(
            id=user['id'], email=user['email'], name=user['name'], role=user['role'],
            created_at=db.to_iso(user['created_at']),
            last_login_at=db.to_iso(user['last_login_at']),
            disabled=bool(user['disabled']),
        ),
    )


@app.post('/api/auth/logout')
def logout(request: Request, response: Response, user: dict = Depends(deps.get_current_user)):
    token = request.cookies.get(REFRESH_COOKIE)
    if token:
        try:
            payload = auth.decode_token(token)
            db.execute('UPDATE refresh_tokens SET revoked = TRUE WHERE jti = ?', (payload.get('jti'),))
        except Exception:
            pass
    _clear_refresh_cookie(response)
    log_event('logout', actor=user, ip=deps.client_ip(request))
    return {'ok': True}


@app.get('/api/auth/me', response_model=models.UserOut)
def me(user: dict = Depends(deps.get_current_user)):
    return models.UserOut(
        id=user['id'], email=user['email'], name=user['name'], role=user['role'],
        created_at=db.to_iso(user['created_at']),
        last_login_at=db.to_iso(user['last_login_at']),
        disabled=bool(user['disabled']),
    )


@app.post('/api/auth/change-password')
@limiter.limit('10/minute')
def change_password(request: Request, body: models.PasswordChange, user: dict = Depends(deps.get_current_user)):
    if not auth.verify_password(body.current_password, user['password_hash']):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Текущий пароль неверный')
    err = auth.validate_password_strength(body.new_password)
    if err:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, err)
    db.execute('UPDATE users SET password_hash = ? WHERE id = ?', (auth.hash_password(body.new_password), user['id']))
    # revoke all refresh tokens for this user
    db.execute('UPDATE refresh_tokens SET revoked = TRUE WHERE user_id = ?', (user['id'],))
    log_event('password_changed', actor=user, target=user, ip=deps.client_ip(request))
    return {'ok': True}


# ==================== Users (super_admin only) ====================

@app.get('/api/users', response_model=list[models.UserOut])
def list_users(user: dict = Depends(deps.require_role('super_admin'))):
    rows = db.query('SELECT * FROM users ORDER BY id')
    return [models.UserOut(
        id=r['id'], email=r['email'], name=r['name'], role=r['role'],
        created_at=db.to_iso(r['created_at']),
        last_login_at=db.to_iso(r['last_login_at']),
        disabled=bool(r['disabled']),
    ) for r in rows]


@app.post('/api/users', response_model=models.UserOut, status_code=201)
@limiter.limit('20/minute')
def create_user(request: Request, body: models.UserCreate, actor: dict = Depends(deps.require_role('super_admin'))):
    err = auth.validate_password_strength(body.password)
    if err:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, err)
    exists = db.one('SELECT id FROM users WHERE email = ?', (body.email,))
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, 'Пользователь с таким email уже существует')
    uid = db.execute(
        'INSERT INTO users (email, name, role, password_hash, created_by) VALUES (?,?,?,?,?) RETURNING id',
        (body.email, body.name, body.role, auth.hash_password(body.password), actor['id']),
    )
    log_event('user_created', actor=actor, target={'id': uid, 'email': body.email},
              ip=deps.client_ip(request), meta={'role': body.role})
    r = db.one('SELECT * FROM users WHERE id = ?', (uid,))
    return models.UserOut(
        id=r['id'], email=r['email'], name=r['name'], role=r['role'],
        created_at=db.to_iso(r['created_at']),
        last_login_at=db.to_iso(r['last_login_at']),
        disabled=bool(r['disabled']),
    )


@app.patch('/api/users/{uid}', response_model=models.UserOut)
def update_user(request: Request, uid: int, body: models.UserUpdate,
                actor: dict = Depends(deps.require_role('super_admin'))):
    target = db.one('SELECT * FROM users WHERE id = ?', (uid,))
    if not target:
        raise HTTPException(404, 'Пользователь не найден')
    changes = {}
    if body.name is not None: changes['name'] = body.name
    if body.role is not None: changes['role'] = body.role
    if body.disabled is not None: changes['disabled'] = bool(body.disabled)
    # can't demote last super admin
    if 'role' in changes and target['role'] == 'super_admin' and changes['role'] != 'super_admin':
        cnt = db.one("SELECT COUNT(*) AS c FROM users WHERE role = 'super_admin' AND NOT disabled")
        if cnt['c'] <= 1:
            raise HTTPException(400, 'Нельзя понизить последнего супер-админа')
    if 'disabled' in changes and changes['disabled'] and target['role'] == 'super_admin':
        cnt = db.one("SELECT COUNT(*) AS c FROM users WHERE role = 'super_admin' AND NOT disabled AND id != ?", (uid,))
        if cnt['c'] < 1:
            raise HTTPException(400, 'Нельзя отключить последнего супер-админа')
    if changes:
        sets = ', '.join(f'{k} = ?' for k in changes)
        db.execute(f'UPDATE users SET {sets} WHERE id = ?', (*changes.values(), uid))
        # if disabled or role changed → revoke sessions
        if 'disabled' in changes or 'role' in changes:
            db.execute('UPDATE refresh_tokens SET revoked = TRUE WHERE user_id = ?', (uid,))
    log_event('user_updated', actor=actor, target=dict(target), ip=deps.client_ip(request), meta=changes)
    r = db.one('SELECT * FROM users WHERE id = ?', (uid,))
    return models.UserOut(
        id=r['id'], email=r['email'], name=r['name'], role=r['role'],
        created_at=db.to_iso(r['created_at']),
        last_login_at=db.to_iso(r['last_login_at']),
        disabled=bool(r['disabled']),
    )


@app.post('/api/users/{uid}/reset-password')
@limiter.limit('20/minute')
def reset_password(request: Request, uid: int, body: models.PasswordReset,
                   actor: dict = Depends(deps.require_role('super_admin'))):
    target = db.one('SELECT * FROM users WHERE id = ?', (uid,))
    if not target:
        raise HTTPException(404, 'Пользователь не найден')
    err = auth.validate_password_strength(body.new_password)
    if err:
        raise HTTPException(400, err)
    db.execute('UPDATE users SET password_hash = ?, failed_attempts = 0, locked_until = NULL WHERE id = ?',
               (auth.hash_password(body.new_password), uid))
    db.execute('UPDATE refresh_tokens SET revoked = TRUE WHERE user_id = ?', (uid,))
    log_event('password_reset_by_admin', actor=actor, target=dict(target), ip=deps.client_ip(request))
    return {'ok': True}


@app.delete('/api/users/{uid}', status_code=204)
def delete_user(request: Request, uid: int, actor: dict = Depends(deps.require_role('super_admin'))):
    target = db.one('SELECT * FROM users WHERE id = ?', (uid,))
    if not target:
        raise HTTPException(404, 'Пользователь не найден')
    if uid == actor['id']:
        raise HTTPException(400, 'Нельзя удалить самого себя')
    if target['role'] == 'super_admin':
        cnt = db.one("SELECT COUNT(*) AS c FROM users WHERE role = 'super_admin' AND NOT disabled AND id != ?", (uid,))
        if cnt['c'] < 1:
            raise HTTPException(400, 'Нельзя удалить последнего супер-админа')
    db.execute('DELETE FROM users WHERE id = ?', (uid,))
    log_event('user_deleted', actor=actor, target=dict(target), ip=deps.client_ip(request))
    return Response(status_code=204)


@app.get('/api/audit')
def audit(limit: int = 200, user: dict = Depends(deps.require_role('super_admin'))):
    rows = db.query('SELECT * FROM audit_log ORDER BY ts DESC LIMIT ?', (min(limit, 500),))
    out = []
    for r in rows:
        d = dict(r)
        d['ts'] = db.to_iso(d.get('ts'))
        out.append(d)
    return out


# ==================== Data (dashboard) ====================

_data_cache = {'mtime': 0, 'blob': None}


def load_data_blob() -> dict:
    # Search for dashboard_data.json in the deployed layout (data/ may sit next to
    # api/ on Vercel, or in /var/task/data at runtime).
    candidates = [
        Path(settings.data_json),
        Path(__file__).resolve().parent.parent / 'data' / 'dashboard_data.json',
        Path('/var/task/data/dashboard_data.json'),
    ]
    for p in candidates:
        if p.exists():
            mtime = p.stat().st_mtime
            if _data_cache['mtime'] != mtime:
                with open(p, encoding='utf-8') as f:
                    _data_cache['blob'] = json.load(f)
                _data_cache['mtime'] = mtime
            return _data_cache['blob']
    return {'error': 'data-not-found', 'searched': [str(p) for p in candidates]}


@app.get('/api/data')
def get_data(user: dict = Depends(deps.get_current_user)):
    """Returns dashboard payload gated by role.

    - super_admin, admin: full payload
    - manager: only org + placeholders (no PBI/PL/ostatok/DZ)
    """
    blob = load_data_blob()
    if user['role'] == 'manager':
        return {
            'meta': blob.get('meta', {}),
            'filials': [],
            'atoms': [],
            'pl_yearly': {},
            'pl_ebitda': {},
            'ostatok': {},
            'dz': {'source_file': 'скрыто', 'line_items': []},
            'org_kz': blob.get('org_kz', []),
            'org_uz': blob.get('org_uz', []),
            'org_tree': blob.get('org_tree', []),
        }
    return blob


# ==================== Static frontend ====================

FRONTEND_DIR = BASE_DIR / 'frontend'
if FRONTEND_DIR.exists():
    app.mount('/', StaticFiles(directory=str(FRONTEND_DIR), html=True), name='frontend')
