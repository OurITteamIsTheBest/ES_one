"""Postgres DB layer via psycopg 3 (sync).

Uses one connection per query — serverless-friendly (Vercel + Neon pooler).
For higher throughput switch to a psycopg_pool.ConnectionPool at module level.

Sample DATABASE_URL formats (both work with Neon):
  postgres://user:pw@ep-xyz.eu-central-1.aws.neon.tech/es_one?sslmode=require
  postgres://user:pw@ep-xyz-pooler.eu-central-1.aws.neon.tech/es_one?sslmode=require&pgbouncer=true
"""
from __future__ import annotations
import os
import contextlib
from datetime import datetime
from typing import Any, Iterable

import psycopg
from psycopg.rows import dict_row

SCHEMA = """
CREATE EXTENSION IF NOT EXISTS citext;

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email CITEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('super_admin','admin','manager')),
  password_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by INTEGER,
  last_login_at TIMESTAMPTZ,
  disabled BOOLEAN NOT NULL DEFAULT FALSE,
  failed_attempts INTEGER NOT NULL DEFAULT 0,
  locked_until TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
  jti TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL,
  revoked BOOLEAN NOT NULL DEFAULT FALSE,
  user_agent TEXT,
  ip TEXT
);
CREATE INDEX IF NOT EXISTS idx_refresh_user ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_expires ON refresh_tokens(expires_at);

CREATE TABLE IF NOT EXISTS audit_log (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  actor_id INTEGER,
  actor_email TEXT,
  event TEXT NOT NULL,
  target_id INTEGER,
  target_email TEXT,
  ip TEXT,
  meta TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(ts DESC);
"""


def _dsn() -> str:
    dsn = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    if not dsn:
        raise RuntimeError(
            'DATABASE_URL is not set. Set it to your Postgres connection string '
            '(Neon: use the pooled connection string with ?sslmode=require).'
        )
    return dsn


@contextlib.contextmanager
def _connect():
    with psycopg.connect(_dsn(), autocommit=True, row_factory=dict_row) as c:
        yield c


def _prepare_sql(sql: str) -> str:
    """Convert SQLite-style '?' placeholders to psycopg's '%s'.

    Safe because our SQL never uses literal '?' in identifiers/strings — all values are
    passed as parameters, and we don't build queries with user-supplied SQL.
    """
    return sql.replace('?', '%s')


def init():
    with _connect() as c, c.cursor() as cur:
        cur.execute(SCHEMA)


def query(sql: str, params: Iterable[Any] = ()) -> list[dict]:
    with _connect() as c, c.cursor() as cur:
        cur.execute(_prepare_sql(sql), tuple(params))
        return list(cur.fetchall())


def one(sql: str, params: Iterable[Any] = ()) -> dict | None:
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: Iterable[Any] = ()) -> int:
    """Execute INSERT/UPDATE/DELETE. Returns the value of the RETURNING id column when
    the query explicitly asks for it; otherwise 0.
    """
    sql_norm = _prepare_sql(sql)
    has_returning = 'RETURNING' in sql_norm.upper()
    with _connect() as c, c.cursor() as cur:
        cur.execute(sql_norm, tuple(params))
        if has_returning:
            row = cur.fetchone()
            if row and 'id' in row:
                return int(row['id'])
        return 0


def to_iso(dt) -> str | None:
    """Convert psycopg-returned datetime to ISO string with trailing Z, or None."""
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    if isinstance(dt, datetime):
        return dt.astimezone().isoformat() if dt.tzinfo else dt.isoformat() + 'Z'
    return str(dt)
