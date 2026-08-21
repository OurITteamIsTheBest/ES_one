# Развёртывание ES One: Vercel + Neon Postgres (бесплатно, 24/7)

Стек:
- **Vercel Hobby** — фронт + Python-serverless API (бесплатно)
- **Neon Postgres** — hosted БД, auto-suspend, 0.5 GB / 191 compute-часов в месяц (бесплатно)
- **GitHub Actions** — cron для обновления данных из Google Sheets (бесплатно, 2000 мин/мес)

Итог: публичный URL `https://your-app.vercel.app`, работает 24/7, стоит $0.

---

## Шаг 1 · Git-репозиторий

```bash
cd "/Users/zhanat/Desktop/Фин дашборд"
git init && git add . && git commit -m "Initial ES One"
# создайте пустой репозиторий на github.com/new и подключите:
git remote add origin git@github.com:YOUR_LOGIN/es-one.git
git branch -M main
git push -u origin main
```

⚠ `data/dashboard_data.json` по `.gitignore` не попадает — включите принудительно:
```bash
git add -f data/dashboard_data.json
git commit -m "seed data" && git push
```

---

## Шаг 2 · Vercel + Neon Postgres

Vercel сам предлагает Neon как одноклик-интеграцию — не надо отдельно регистрироваться в Neon.

1. Зайдите на [vercel.com](https://vercel.com) → **Log in with GitHub**.
2. **Add New → Project** → выберите свой репозиторий `es-one` → **Import**.
3. **Framework Preset** оставьте *Other* — `vercel.json` уже готов.
4. **НЕ нажимайте Deploy пока не добавите env-переменные** (см. шаг 3 ниже).

### Создание Neon-базы через Vercel

5. В том же проекте → **Storage** → **Create Database** → **Neon** → **Continue** → **Create**.
   - Регион: **AWS Europe (Frankfurt)** — ближе к KZ.
   - Vercel автоматически добавит переменные `DATABASE_URL`, `POSTGRES_URL`, `POSTGRES_URL_NON_POOLING` во все окружения вашего проекта.

---

## Шаг 3 · Environment Variables

В Vercel → **Project → Settings → Environment Variables** добавьте (или проверьте):

| Ключ | Значение | Куда |
|---|---|---|
| `ENV` | `production` | Production |
| `JWT_SECRET` | Сгенерировать: `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` | Production |
| `DATABASE_URL` | (Neon интеграция уже проставила) — используем **POOLED** | Production |
| `BOOTSTRAP_EMAIL` | ваш email | Production |
| `BOOTSTRAP_NAME` | Ваше Имя Фамилия | Production |
| `BOOTSTRAP_PASSWORD` | пароль 12+ символов, потом смените в UI | Production |
| `COOKIE_SECURE` | `true` | Production |
| `FRONTEND_ORIGINS` | `https://your-app.vercel.app` | Production |

⚠ `JWT_SECRET`, `BOOTSTRAP_PASSWORD`, `COOKIE_SECURE=true` — обязательны. Backend **не запустится в production без них** (fail-fast защита).

---

## Шаг 4 · Deploy

Vercel → **Deployments → Redeploy** (или push любого коммита).

Первый деплой = 2–3 мин.

---

## Шаг 5 · Инициализация БД (один раз)

Backend сам создаст таблицы + первого супер-админа при первом обращении к БД. Но если хотите увидеть в БД сразу, запустите локально:

```bash
# Скопируйте POSTGRES_URL_NON_POOLING из Vercel → Storage → Neon → .env.local tab
export DATABASE_URL="postgres://user:pw@ep-xyz.eu-central-1.aws.neon.tech/neondb?sslmode=require"
export BOOTSTRAP_EMAIL="ваш@email"
export BOOTSTRAP_NAME="Ваше Имя"
export BOOTSTRAP_PASSWORD="ваш_надёжный_пароль_12+"
cd "/Users/zhanat/Desktop/Фин дашборд"
pip3 install -r requirements.txt --user
python3 -m backend.init_db
```

**Используйте `POSTGRES_URL_NON_POOLING`** (без `-pooler` в hostname) для миграций/init_db — pooled URL не поддерживает `CREATE EXTENSION`.

---

## Шаг 6 · Открыть

Откройте `https://your-app.vercel.app` — окно входа. Введите `BOOTSTRAP_EMAIL` и `BOOTSTRAP_PASSWORD`.

**Первое действие:** Профиль → сменить пароль на что-то, что знаете только вы.

**Второе:** Пользователи → добавить команду (admin / manager).

---

## Обновление данных дашборда

### Ручное
```bash
python3 refresh_data.py                  # тянет свежие CSV из Google Sheets → JSON
git add -f data/dashboard_data.json
git commit -m "data $(date +%F)" && git push
# Vercel сам передеплоит через ~1 мин
```

### Автоматически — GitHub Actions

Создайте `.github/workflows/refresh.yml`:

```yaml
name: refresh-data
on:
  schedule: [{ cron: "0 6 * * *" }]   # 06:00 UTC = 11:00 Алматы
  workflow_dispatch:
permissions: { contents: write }
jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: python3 refresh_data.py
      - name: Commit
        run: |
          git config user.name "es-one-bot"
          git config user.email "bot@es-one"
          git add -f data/dashboard_data.json
          git diff --cached --quiet || (git commit -m "auto-refresh $(date +%F)" && git push)
```

Каждое утро свежие данные → автодеплой Vercel.

---

## Ограничения Neon Free tier

| Ресурс | Лимит | Хватит? |
|---|---|---|
| Storage | 0.5 GB | Наша БД — считанные MB. С огромным запасом |
| Compute | 191 час/мес | Neon auto-suspend после 5 мин простоя → редко превышаете 30 ч/мес |
| Cold start | 300–500 мс | Первый запрос после долгой паузы. Ок для дашборда |
| Одновременных соединений | 100 (pooled) | Наши запросы короткие, реально <10 одновременно |
| Point-in-time backup | 7 дней | Ок |
| Регионы | 5 | Frankfurt для KZ |
| Branching | ✓ | Можно поднять dev-ветку БД бесплатно |

Апгрейд на **Launch $19/мес**: 10 GB / 300 ч compute / 30 дней бэкапов — понадобится только если станет >100 активных пользователей.

## Ограничения Vercel Hobby

| Ресурс | Лимит | Хватит? |
|---|---|---|
| Bandwidth | 100 GB/мес | ~2 MB × 5000 визитов | 
| Function invocations | 1M/мес | ~10 инвокаций на визит × 5000 = 50k | 
| Function timeout | **60 сек** | Наши API отвечают <500 мс |
| Memory | 1024 MB | Мы используем ~200 MB |
| Cron jobs | 2 | Не используем (крон в GitHub Actions) |

---

## Локальная разработка (после миграции на Postgres)

Локальный Postgres проще всего через Homebrew:
```bash
brew install postgresql@17 && brew services start postgresql@17
createdb esone
export DATABASE_URL="postgres://$(whoami)@localhost:5432/esone"
export BOOTSTRAP_EMAIL="dev@es.kz" BOOTSTRAP_NAME="Dev" BOOTSTRAP_PASSWORD="Local-Dev-Pass-1"
python3 -m backend.init_db
python3 -m uvicorn backend.main:app --reload
```

Открыть http://localhost:8000.

Альтернатива — использовать **Neon dev-ветку** из production БД: Vercel → Storage → Neon → **Branches → Create branch**.

---

## Troubleshooting

**500 при логине после деплоя** → Vercel → Deployments → Runtime Logs. Скорее всего `DATABASE_URL` не проставлен или неверный.

**«JWT_SECRET must be set explicitly in production»** — переменная пустая. Settings → Environment Variables → добавить.

**«COOKIE_SECURE must be true in production»** — на Vercel всегда `true` (HTTPS).

**CORS-ошибки** — `FRONTEND_ORIGINS` должен точно совпадать с URL вашего проекта, без слэша в конце.

**«column disabled = 0 is malformed»** — не должно возникнуть, но если что: в Postgres мы используем `NOT disabled` и `revoked = TRUE`, а не 0/1.

**Функция таймаутит 60 сек** — большой JSON `data/dashboard_data.json`? Разбить на chunks или закешировать в Neon.

---

## Готово

`https://your-app.vercel.app` работает 24/7, бесплатно, с полноценной production-безопасностью (Argon2, JWT-rotation с reuse detection, HSTS/CSP, rate limits, audit log, RBAC на бэке).
