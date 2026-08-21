from __future__ import annotations
"""One-shot init: creates schema and first super admin. Idempotent."""
from . import db, auth
from .config import settings


def main():
    db.init()
    existing = db.one('SELECT id FROM users WHERE email = ?', (settings.bootstrap_email,))
    if existing:
        print(f'✔ Super admin exists (id={existing["id"]}, email={settings.bootstrap_email}).')
        return
    hash_ = auth.hash_password(settings.bootstrap_password)
    uid = db.execute(
        'INSERT INTO users (email, name, role, password_hash, created_by) VALUES (?, ?, ?, ?, ?) RETURNING id',
        (settings.bootstrap_email, settings.bootstrap_name, 'super_admin', hash_, None),
    )
    db.execute(
        "INSERT INTO audit_log (event, actor_email, target_id, target_email, meta) VALUES ('bootstrap_super_admin', 'system', ?, ?, ?)",
        (uid, settings.bootstrap_email, 'first user'),
    )
    print('=========================================================')
    print(f'✔ First super admin created (id={uid})')
    print(f'  Email:    {settings.bootstrap_email}')
    print(f'  Name:     {settings.bootstrap_name}')
    print(f'  Password: {settings.bootstrap_password}')
    print('  ⚠  Смените пароль в разделе «Профиль» после первого входа.')
    print('=========================================================')


if __name__ == '__main__':
    main()
