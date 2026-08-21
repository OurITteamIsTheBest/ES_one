#!/usr/bin/env bash
# ES One — one-shot deploy to Vercel + Neon Postgres.
# Что делает:
#   1. Логинит в GitHub CLI (открывается браузер)
#   2. Создаёт приватный репозиторий и пушит код
#   3. Логинит в Vercel CLI (магическая ссылка на почту)
#   4. Создаёт Vercel-проект, привязывает к репо, поднимает Neon Postgres
#   5. Проставляет все env-переменные (JWT_SECRET, BOOTSTRAP_*, ENV=production)
#   6. Деплой в production
#   7. Инициализирует БД (миграции + первый супер-админ)
#   8. Выводит URL и credentials супер-админа
#
# Использование:
#   cd "/Users/zhanat/Desktop/Фин дашборд"
#   bash deploy.sh

set -euo pipefail
cd "$(dirname "$0")"

# ---------- 0. sanity ----------
command -v git >/dev/null    || { echo "❌ git не найден"; exit 1; }
command -v gh >/dev/null     || { echo "❌ gh не найден. brew install gh"; exit 1; }
command -v vercel >/dev/null || { echo "❌ vercel не найден. npm i -g vercel"; exit 1; }
command -v python3 >/dev/null|| { echo "❌ python3 не найден"; exit 1; }

echo
echo "═══════════════════════════════════════════════════════════════"
echo "  ES One · автодеплой на Vercel + Neon Postgres"
echo "═══════════════════════════════════════════════════════════════"

# ---------- 1. GitHub ----------
if ! gh auth status &>/dev/null; then
  echo "▸ Шаг 1/6 · Логин в GitHub"
  echo "  → откроется браузер. Разрешите доступ. Возвращайтесь сюда."
  gh auth login --hostname github.com --git-protocol https --web --scopes "repo,workflow"
else
  echo "✔ Шаг 1/6 · GitHub уже залогинен как $(gh api user -q .login 2>/dev/null)"
fi

REPO_NAME=$(basename "$PWD" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')
[ -z "$REPO_NAME" ] && REPO_NAME="es-one"
GH_USER=$(gh api user -q .login)

echo
echo "▸ Шаг 2/6 · Публикация репозитория ($GH_USER/$REPO_NAME)"
if ! gh repo view "$GH_USER/$REPO_NAME" &>/dev/null; then
  gh repo create "$REPO_NAME" --private --source=. --remote=origin --push
  echo "  ✔ создан приватный репо и запушен"
else
  echo "  ↺ репо уже существует, пушу текущее состояние"
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$GH_USER/$REPO_NAME.git"
  git push -u origin main 2>&1 | tail -2 || true
fi

# ---------- 3. Vercel ----------
if ! vercel whoami &>/dev/null; then
  echo
  echo "▸ Шаг 3/6 · Логин в Vercel"
  echo "  → выберите Continue with GitHub, разрешите доступ."
  vercel login
else
  echo
  echo "✔ Шаг 3/6 · Vercel уже залогинен как $(vercel whoami 2>/dev/null | tail -1)"
fi

# ---------- 4. Link project ----------
echo
echo "▸ Шаг 4/6 · Привязка проекта"
if [ ! -f ".vercel/project.json" ]; then
  vercel link --yes --project "$REPO_NAME"
fi

# ---------- 5. Environment variables ----------
echo
echo "▸ Шаг 5/6 · Environment variables"

JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
BOOTSTRAP_PASSWORD=$(python3 -c "import secrets, string; a=string.ascii_letters+string.digits+'!@#\$%^&*'; print(''.join(secrets.choice(a) for _ in range(20)))")

# Ask super admin details (with sane defaults)
read -rp "  Email первого супер-админа [zhunussov_zh@eng-services.kz]: " BE
BOOTSTRAP_EMAIL=${BE:-zhunussov_zh@eng-services.kz}
read -rp "  Имя супер-админа [Жунусов Жанат]: " BN
BOOTSTRAP_NAME=${BN:-Жунусов Жанат}

set_env() {
  local k="$1" v="$2"
  printf "%s" "$v" | vercel env add "$k" production --force 2>&1 | tail -1
}

set_env ENV production
set_env JWT_SECRET "$JWT_SECRET"
set_env BOOTSTRAP_EMAIL "$BOOTSTRAP_EMAIL"
set_env BOOTSTRAP_NAME "$BOOTSTRAP_NAME"
set_env BOOTSTRAP_PASSWORD "$BOOTSTRAP_PASSWORD"
set_env COOKIE_SECURE true

# Neon integration — CLI не умеет создавать storage автоматически.
echo
if ! vercel env ls production 2>/dev/null | grep -q '^DATABASE_URL'; then
  echo "  ⚠ Neon Postgres нужно создать в браузере (30 секунд):"
  echo "    1) Открывается страница Storage вашего проекта"
  echo "    2) Create Database → Neon → Frankfurt → Create"
  echo "    3) Готово, нажмите Enter здесь"
  PROJECT_URL="https://vercel.com/$(vercel teams ls 2>/dev/null | grep -oE 'team_[a-z0-9]+' | head -1 || echo $GH_USER)/$REPO_NAME/stores"
  echo "    ссылка: $PROJECT_URL"
  open "$PROJECT_URL" 2>/dev/null || true
  read -rp "  ↩ После создания Neon нажмите Enter: " _
  vercel env pull .env.production --environment production --yes 2>&1 | tail -1
fi

# ---------- 6. Deploy ----------
echo
echo "▸ Шаг 6/6 · Production deploy"
DEPLOY_URL=$(vercel deploy --prod --yes 2>&1 | tee /tmp/vercel-deploy.log | grep -oE 'https://[a-z0-9.-]+\.vercel\.app' | tail -1)

# Update FRONTEND_ORIGINS to actual URL
if [ -n "$DEPLOY_URL" ]; then
  set_env FRONTEND_ORIGINS "$DEPLOY_URL"
  vercel deploy --prod --yes >/dev/null 2>&1 || true
fi

# ---------- 7. Init DB ----------
echo
echo "▸ Инициализация БД + создание супер-админа"
vercel env pull .env.production --environment production --yes >/dev/null 2>&1 || true

# Use NON-POOLING URL for CREATE EXTENSION (pooled URL doesn't support it)
NON_POOLING=$(grep -E '^POSTGRES_URL_NON_POOLING' .env.production 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"')
[ -z "$NON_POOLING" ] && NON_POOLING=$(grep -E '^DATABASE_URL' .env.production 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"')

if [ -n "$NON_POOLING" ]; then
  python3 -m pip install --quiet --user -r requirements.txt 2>&1 | tail -1
  DATABASE_URL="$NON_POOLING" \
    BOOTSTRAP_EMAIL="$BOOTSTRAP_EMAIL" \
    BOOTSTRAP_NAME="$BOOTSTRAP_NAME" \
    BOOTSTRAP_PASSWORD="$BOOTSTRAP_PASSWORD" \
    python3 -m backend.init_db
else
  echo "  ⚠ Не найден DATABASE_URL — проверьте, что Neon подключён к проекту"
fi

# ---------- Done ----------
echo
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅  Готово"
echo "═══════════════════════════════════════════════════════════════"
echo "  URL:      $DEPLOY_URL"
echo "  Логин:    $BOOTSTRAP_EMAIL"
echo "  Пароль:   $BOOTSTRAP_PASSWORD"
echo
echo "  ⚠ Смените пароль в разделе Профиль после первого входа."
echo "  ⚠ Не пересылайте этот пароль в открытых каналах."
echo "═══════════════════════════════════════════════════════════════"
