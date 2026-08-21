# ES One

Управленческий дашборд с backend-авторизацией, ролевым доступом и автообновлением данных из Google Sheets.

## Архитектура

```
├── backend/           FastAPI · SQLite · Argon2 · JWT (access + refresh, rotating)
│   ├── main.py         · routes и middleware
│   ├── auth.py         · password hashing + JWT
│   ├── db.py           · схема SQLite и helpers
│   ├── models.py       · Pydantic-модели
│   ├── deps.py         · auth + RBAC
│   ├── config.py       · настройки из .env
│   └── init_db.py      · создание первого супер-админа
├── frontend/          SPA (vanilla JS, без сборщиков) — обращается к /api/*
├── data/              json + csv, обновляется скриптом refresh_data.py
├── refresh_data.py    Скачивает свежие CSV из Google Sheets + собирает JSON
└── build_dashboard.py Собирает frontend/index.html из шаблона
```

## Быстрый старт (локально)

```bash
cd "/Users/zhanat/Desktop/Фин дашборд"

# 1) Установить зависимости
pip3 install --user -r backend/requirements.txt

# 2) Настроить окружение (обязательно замените JWT_SECRET и BOOTSTRAP_PASSWORD)
cp .env.example .env
# отредактируйте .env

# 3) Скачать актуальные данные из Google Sheets
python3 refresh_data.py

# 4) Собрать фронтенд
python3 build_dashboard.py

# 5) Инициализировать БД и создать первого супер-админа
python3 -m backend.init_db

# 6) Запустить сервер
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Откройте [http://localhost:8000](http://localhost:8000).

**Первый вход:**
- Email: `zhunussov_zh@eng-services.kz`
- Пароль: `ES-One-2026`

**Сразу же смените пароль** в разделе «Профиль».

## Роли

| Роль | Доступ |
|---|---|
| `super_admin` | Всё + управление пользователями + журнал событий |
| `admin` | Все дашборды (Финансы, HR, Продажи, Процессы) |
| `manager` | Только HR + Продажи + Процессы (без Финансов) |

Ролевой доступ проверяется **на бэкенде** для каждого запроса `/api/*`, а не только скрытием кнопок в UI.

## Безопасность

- **Пароли:** Argon2id (в OWASP-рекомендованном режиме)
- **Access-токен:** JWT, 15 минут, в памяти клиента (не в localStorage — защита от XSS-кражи)
- **Refresh-токен:** JWT в **HttpOnly + SameSite=Lax** cookie, 7 дней, с ротацией на каждом refresh (обнаружение повторного использования украденного токена)
- **Brute-force:** 5 неудачных попыток → блок аккаунта на 15 минут + rate limit `/api/auth/login` 10 req/min с IP
- **Валидация пароля:** мин. 10 символов, ≥3 групп из {строчные, заглавные, цифры, спецсимволы}
- **Аудит:** каждый вход/выход/CRUD пользователя пишется в `audit_log`
- **Смена пароля** отзывает все refresh-токены пользователя
- **Заголовки:** X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy
- **CORS:** origins жёстко из `.env`
- **Timing-safe login:** одинаковое время ответа для «неизвестный email» и «неверный пароль»

## Обновление данных

Данные (финансы, оргструктура, ДЗ) обновляются скриптом `refresh_data.py`. Он сам находит **самый свежий файл** в папке ДЗ по дате в имени.

**Ручной запуск:**
```bash
python3 refresh_data.py
```

**Автоматизация через cron:**
```
0 9 * * * cd "/Users/zhanat/Desktop/Фин дашборд" && python3 refresh_data.py >> refresh.log 2>&1
```

После запуска бэкенд подхватит новые данные автоматически (`/api/data` перечитывает `dashboard_data.json` по mtime).

## Развёртывание для команды

Сейчас всё работает локально на вашем Mac по `http://localhost:8000`. Чтобы дать доступ другим:

**Быстро (LAN):** запустите `uvicorn --host 0.0.0.0` — коллеги в вашей сети открывают `http://<ваш-ip>:8000`.

**Правильно (public):** разверните на Fly.io / Railway / Render / VPS с HTTPS.
Обязательные шаги для production:
1. Установите `COOKIE_SECURE=true` в `.env`
2. За reverse-proxy (nginx / caddy) с валидным TLS
3. Сгенерируйте свежий `JWT_SECRET` (`python -c "import secrets; print(secrets.token_urlsafe(48))"`)
4. Смените `BOOTSTRAP_PASSWORD` до первого запуска
5. Регулярный бэкап `backend/esone.db`
6. Ограничьте `FRONTEND_ORIGINS` только вашим доменом
7. (опционально) переезд с SQLite на PostgreSQL, если >20 одновременных пользователей

## Что ещё можно добавить

- 2FA (TOTP)
- OAuth/SSO (Google Workspace)
- Email-восстановление пароля (нужен SMTP)
- Экспорт таблиц в Excel/CSV
- Push-уведомления в Telegram/Slack при критических событиях
