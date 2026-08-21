import os
BASE = os.path.dirname(os.path.abspath(__file__))
# Write to BOTH frontend/ (local dev serving via uvicorn) and public/ (Vercel static)
OUT_PATHS = [
    os.path.join(BASE, 'frontend', 'index.html'),
    os.path.join(BASE, 'public', 'index.html'),
]

HTML = r'''<meta charset="utf-8">
<title>ES One</title>
<style>
  :root {
    --bg: #ffffff; --panel: #ffffff; --border: #ececec;
    --text: #0a0a0a; --muted: #6b7280; --subtle: #f7f7f8;
    --pos: #059669; --neg: #dc2626; --accent: #111827; --chip: #f3f4f6;
  }
  :root[data-theme="dark"], :root:not([data-theme="light"]) {}
  * { box-sizing: border-box; }
  html, body { background: var(--bg); color: var(--text); margin: 0; padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Segoe UI", "Helvetica Neue", Arial, "Noto Sans", sans-serif;
    font-feature-settings: "cv11","ss01","ss03"; -webkit-font-smoothing: antialiased;
    font-size: 14px; line-height: 1.5;
  }
  .app { display: grid; grid-template-columns: 220px 1fr; min-height: 100vh; }
  aside { border-right: 1px solid var(--border); padding: 24px 16px;
    position: sticky; top: 0; height: 100vh; overflow-y: auto; background: #fafafa; }
  aside .brand { font-weight: 600; font-size: 13px; letter-spacing: .02em; margin-bottom: 4px; }
  aside .brand-sub { color: var(--muted); font-size: 11px; margin-bottom: 24px; }
  nav .group { margin-bottom: 14px; }
  nav .group-label { color: var(--muted); font-size: 10.5px; text-transform: uppercase; letter-spacing: .06em; font-weight: 600; padding: 4px 10px; margin-top: 4px; }
  nav a { display: flex; align-items: center; justify-content: space-between;
    padding: 7px 10px; margin: 1px 0; color: var(--text);
    text-decoration: none; border-radius: 6px; font-size: 13px; cursor: pointer; }
  nav a:hover { background: var(--chip); }
  nav a.active { background: var(--accent); color: #fff; }
  nav a .soon { font-size: 9.5px; padding: 1px 6px; border-radius: 999px; background: #fef3c7; color: #92400e; text-transform: uppercase; letter-spacing: .04em; font-weight: 600; }
  nav a.active .soon { background: rgba(255,255,255,.2); color: #fff; }
  main { padding: 0 40px 80px; max-width: 1500px; }
  .page-head { padding: 28px 0 12px; background: #fff; position: sticky; top: 0; z-index: 5; border-bottom: 1px solid var(--border); margin-bottom: 20px; }
  h1 { font-size: 22px; font-weight: 600; margin: 0 0 4px; letter-spacing: -0.01em; }
  h2 { font-size: 15px; font-weight: 600; margin: 24px 0 12px; letter-spacing: -0.005em; }
  .sub { color: var(--muted); font-size: 12px; }
  .filter-bar { display: flex; gap: 16px 20px; align-items: center; padding: 12px 0; flex-wrap: wrap; }
  .filter-group { display: flex; align-items: center; gap: 8px; font-size: 12px; flex-wrap: nowrap; min-width: 0; }
  .filter-label { color: var(--muted); text-transform: uppercase; letter-spacing: .04em; font-size: 10.5px; font-weight: 500; }
  .filter-chips { display: flex; gap: 4px; flex-wrap: wrap; }
  .chip-btn { padding: 4px 10px; border: 1px solid var(--border); background: #fff; border-radius: 999px; font-size: 12px; cursor: pointer; color: var(--text); font-family: inherit; transition: all .12s; }
  .chip-btn:hover { border-color: #bbb; }
  .chip-btn.on { background: var(--accent); color: #fff; border-color: var(--accent); }
  .chip-btn.quick { color: var(--muted); font-size: 11px; padding: 4px 8px; }
  .filter-select { padding: 5px 26px 5px 10px; border: 1px solid var(--border); border-radius: 6px; font-size: 12px; background: #fff; font-family: inherit; cursor: pointer; appearance: none; background-image: url('data:image/svg+xml;utf8,<svg width="8" height="8" xmlns="http://www.w3.org/2000/svg"><path d="M0 2 L4 6 L8 2" stroke="%236b7280" fill="none" stroke-width="1.5"/></svg>'); background-repeat: no-repeat; background-position: right 8px center; max-width: 260px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; }
  .filter-dropdown { position: relative; }
  .filter-dd-btn { padding: 5px 12px; border: 1px solid var(--border); background: #fff; border-radius: 6px; font-size: 12px; cursor: pointer; font-family: inherit; display: flex; align-items: center; gap: 6px; }
  .filter-dd-btn:hover { border-color: #bbb; }
  .filter-dd-menu { display: none; position: absolute; top: calc(100% + 4px); left: 0; background: #fff; border: 1px solid var(--border); border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,.08); min-width: 260px; max-height: 340px; overflow-y: auto; z-index: 100; padding: 6px; }
  .filter-dd-menu.open { display: block; }
  .filter-dd-item { display: flex; align-items: center; gap: 8px; padding: 6px 10px; cursor: pointer; border-radius: 4px; font-size: 12.5px; }
  .filter-dd-item:hover { background: var(--subtle); }
  .filter-dd-item input { margin: 0; cursor: pointer; }
  .filter-dd-quick { display: flex; gap: 6px; padding: 6px 10px; border-bottom: 1px solid var(--border); margin-bottom: 4px; }
  .filter-dd-quick a { color: #2563eb; font-size: 11px; cursor: pointer; text-decoration: underline; }
  .kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 0 0 20px; }
  .kpi { border: 1px solid var(--border); border-radius: 10px; padding: 16px; background: var(--panel); }
  .kpi .label { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .04em; }
  .kpi .value { font-size: 22px; font-weight: 600; margin-top: 8px; letter-spacing: -0.01em; }
  .kpi .delta { font-size: 11px; margin-top: 4px; color: var(--muted); }
  .kpi .delta.pos { color: var(--pos); }
  .kpi .delta.neg { color: var(--neg); }
  .grid-2 { display: grid; grid-template-columns: 1.4fr 1fr; gap: 16px; }
  .card { border: 1px solid var(--border); border-radius: 10px; padding: 20px; background: var(--panel); }
  .card-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 12px; gap: 12px; }
  .card-head h3 { font-size: 13px; font-weight: 600; margin: 0; }
  .card-head .more { font-size: 12px; color: var(--muted); cursor: pointer; background: none; border: none; padding: 4px 8px; border-radius: 6px; font-family: inherit; }
  .card-head .more:hover { background: var(--chip); color: var(--text); }
  .table-scroll { overflow-x: auto; margin: 0 -4px; }
  table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
  th, td { padding: 8px 10px; text-align: right; border-bottom: 1px solid var(--border); white-space: nowrap; vertical-align: top; }
  th:first-child, td:first-child { text-align: left; }
  th { color: var(--muted); font-weight: 500; font-size: 11px; text-transform: uppercase; letter-spacing: .03em; }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover { background: var(--subtle); }
  .wrap-cell { white-space: normal; word-break: break-word; max-width: 240px; line-height: 1.35; }
  .num { font-variant-numeric: tabular-nums; }
  .pos { color: var(--pos); } .neg { color: var(--neg); }
  .bar-row { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(60px, 2fr) auto; gap: 12px; align-items: center; margin: 8px 0; font-size: 12.5px; }
  .bar-name { color: var(--text); font-size: 12.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .bar-track { position: relative; height: 8px; background: var(--subtle); border-radius: 3px; overflow: hidden; }
  .bar-fill { position: absolute; top: 0; left: 0; height: 100%; background: #111827; border-radius: 3px; }
  .bar-fill.neg { background: #dc2626; }
  .bar-value { text-align: right; color: var(--text); font-variant-numeric: tabular-nums; font-size: 12.5px; font-weight: 500; }
  .modal-mask { position: fixed; inset: 0; background: rgba(10,10,10,0.4); display: none; align-items: flex-start; justify-content: center; z-index: 200; padding: 40px 20px; overflow-y: auto; }
  .modal-mask.open { display: flex; }
  .modal { background: #fff; border-radius: 12px; max-width: 1100px; width: 100%; padding: 24px; box-shadow: 0 20px 60px rgba(0,0,0,.15); }
  .modal h3 { margin: 0 0 4px; font-size: 16px; }
  .modal .msub { color: var(--muted); font-size: 12px; margin-bottom: 16px; }
  .modal .close { float: right; background: none; border: none; font-size: 22px; cursor: pointer; color: var(--muted); line-height: 1; padding: 0 6px; }
  .modal-table-wrap { max-height: 65vh; overflow: auto; border: 1px solid var(--border); border-radius: 8px; }
  .tabs { display: flex; gap: 2px; margin: 16px 0; border-bottom: 1px solid var(--border); }
  .tabs button { background: none; border: none; padding: 10px 14px; cursor: pointer; color: var(--muted); font-size: 13px; border-bottom: 2px solid transparent; margin-bottom: -1px; font-family: inherit; }
  .tabs button.active { color: var(--text); border-bottom-color: var(--accent); font-weight: 500; }
  svg { display: block; }
  .legend { display: flex; gap: 14px; flex-wrap: wrap; font-size: 11.5px; color: var(--muted); margin-top: 8px; }
  .legend .item { display: flex; align-items: center; gap: 5px; }
  .legend .dot { width: 8px; height: 8px; border-radius: 2px; }
  .search { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; margin-bottom: 12px; font-family: inherit; }
  .stat-inline { display: flex; gap: 20px; padding: 12px 16px; background: var(--subtle); border-radius: 8px; font-size: 12.5px; margin-bottom: 12px; flex-wrap: wrap; }
  .stat-inline > div { display: flex; flex-direction: column; }
  .stat-inline .k { color: var(--muted); font-size: 11px; }
  .stat-inline .v { font-weight: 600; font-variant-numeric: tabular-nums; }
  .footer-note { color: var(--muted); font-size: 11px; margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--border); }
  .empty-state { padding: 40px; text-align: center; color: var(--muted); font-size: 13px; background: var(--subtle); border-radius: 8px; }
  /* ===== Login ===== */
  .login-screen { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #fafafa; padding: 20px; }
  .login-card { background: #fff; border: 1px solid var(--border); border-radius: 12px; padding: 32px; width: 100%; max-width: 380px; box-shadow: 0 4px 24px rgba(0,0,0,.04); }
  .login-brand { font-weight: 600; font-size: 16px; margin-bottom: 4px; }
  .login-brand-sub { color: var(--muted); font-size: 12px; margin-bottom: 24px; }
  .login-field { margin-bottom: 12px; }
  .login-field label { display: block; font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; margin-bottom: 5px; }
  .login-field input { width: 100%; padding: 9px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; font-family: inherit; }
  .login-field input:focus { outline: none; border-color: var(--accent); }
  .login-btn { width: 100%; padding: 10px 16px; background: var(--accent); color: #fff; border: none; border-radius: 6px; font-size: 13px; cursor: pointer; margin-top: 8px; font-family: inherit; font-weight: 500; }
  .login-btn:hover { opacity: .92; }
  .login-err { color: var(--neg); font-size: 12px; margin-top: 10px; text-align: center; min-height: 16px; }
  .login-hint { color: var(--muted); font-size: 11px; margin-top: 16px; text-align: center; line-height: 1.5; }
  /* ===== User chip ===== */
  aside { display: flex; flex-direction: column; }
  aside nav { flex: 1; }
  .user-chip { padding: 12px 10px; border-top: 1px solid var(--border); display: flex; align-items: center; gap: 10px; font-size: 12px; }
  .user-chip .avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 12px; flex-shrink: 0; background: #dbeafe; color: #1e40af; }
  .user-chip .info { flex: 1; min-width: 0; }
  .user-chip .name { font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 12.5px; }
  .user-chip .role { color: var(--muted); font-size: 10.5px; text-transform: uppercase; letter-spacing: .04em; }
  .user-chip .logout-btn { background: none; border: 1px solid var(--border); cursor: pointer; padding: 4px 8px; color: var(--muted); font-family: inherit; font-size: 11px; border-radius: 4px; }
  .user-chip .logout-btn:hover { color: var(--text); background: var(--chip); }
  .role-badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 10.5px; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; }
  .role-super_admin { background: #fef3c7; color: #92400e; }
  .role-admin { background: #dbeafe; color: #1e40af; }
  .role-manager { background: #dcfce7; color: #166534; }
  .btn-primary { padding: 6px 12px; background: var(--accent); color: #fff; border: none; border-radius: 6px; font-size: 12px; cursor: pointer; font-family: inherit; font-weight: 500; }
  .btn-primary:hover { opacity: .92; }
  .btn-secondary { padding: 6px 12px; background: #fff; color: var(--text); border: 1px solid var(--border); border-radius: 6px; font-size: 12px; cursor: pointer; font-family: inherit; }
  .btn-secondary:hover { background: var(--chip); }
  .btn-danger { padding: 6px 12px; background: #fef2f2; color: var(--neg); border: 1px solid #fecaca; border-radius: 6px; font-size: 12px; cursor: pointer; font-family: inherit; }
  .btn-danger:hover { background: #fee2e2; }
</style>

<div id="appRoot"></div>
<div class="modal-mask" id="modalMask"><div class="modal" id="modalBox"></div></div>

<script>
// DATA is fetched from backend after login; starts empty
let DATA = {};
let ACCESS = null;   // in-memory access token (never localStorage — safer against XSS-token-theft)
let ME = null;       // current user object from server

const ROLES = {
  super_admin: { label: 'Супер-админ' },
  admin: { label: 'Админ' },
  manager: { label: 'Менеджер' },
};

async function api(path, opts={}) {
  const headers = { 'Content-Type': 'application/json', ...(opts.headers||{}) };
  if (ACCESS) headers['Authorization'] = 'Bearer ' + ACCESS;
  let resp = await fetch(path, { credentials: 'include', ...opts, headers });
  if (resp.status === 401 && ACCESS && path !== '/api/auth/refresh' && path !== '/api/auth/login') {
    // try refresh
    const r = await fetch('/api/auth/refresh', { method: 'POST', credentials: 'include' });
    if (r.ok) {
      const j = await r.json();
      ACCESS = j.access_token; ME = j.user;
      headers['Authorization'] = 'Bearer ' + ACCESS;
      resp = await fetch(path, { credentials: 'include', ...opts, headers });
    } else {
      ACCESS = null; ME = null;
      renderLogin();
      throw new Error('unauthorized');
    }
  }
  if (!resp.ok) {
    let msg = resp.statusText;
    try { const j = await resp.json(); msg = j.detail || msg; } catch {}
    throw new Error(msg);
  }
  if (resp.status === 204) return null;
  return await resp.json();
}

async function loginSubmit() {
  const email = document.getElementById('loginEmail').value.trim().toLowerCase();
  const pw = document.getElementById('loginPw').value;
  const errEl = document.getElementById('loginErr');
  errEl.textContent = '';
  if (!email || !pw) { errEl.textContent = 'Заполните оба поля'; return; }
  try {
    const j = await api('/api/auth/login', { method:'POST', body: JSON.stringify({email, password: pw}) });
    ACCESS = j.access_token; ME = j.user;
    await bootAfterLogin();
  } catch(e) { errEl.textContent = e.message || 'Ошибка входа'; }
}

async function logout() {
  try { await api('/api/auth/logout', { method:'POST' }); } catch {}
  ACCESS = null; ME = null; DATA = {};
  renderLogin();
}

async function bootAfterLogin() {
  DATA = await api('/api/data');
  initFiltersFromData();
  renderApp();
}
function initFiltersFromData() {
  filterState.months = new Set([1,2,3,4,5,6,7,8,9,10,11,12]);
  filterState.filials = new Set(DATA.filials || []);
}

async function tryAutoLogin() {
  try {
    const r = await fetch('/api/auth/refresh', { method:'POST', credentials:'include' });
    if (r.ok) {
      const j = await r.json();
      ACCESS = j.access_token; ME = j.user;
      DATA = await api('/api/data');
      initFiltersFromData();
      renderApp();
      return;
    }
  } catch {}
  renderLogin();
}

function renderLogin() {
  document.getElementById('appRoot').innerHTML = `
    <div class="login-screen">
      <div class="login-card">
        <div class="login-brand">ES One</div>
        <div class="login-brand-sub">Управленческий дашборд · вход</div>
        <div class="login-field">
          <label>Email</label>
          <input id="loginEmail" type="email" autocomplete="username" placeholder="name@company.kz">
        </div>
        <div class="login-field">
          <label>Пароль</label>
          <input id="loginPw" type="password" autocomplete="current-password" placeholder="••••••••" onkeydown="if(event.key==='Enter') loginSubmit()">
        </div>
        <button class="login-btn" onclick="loginSubmit()">Войти</button>
        <div class="login-err" id="loginErr"></div>
      </div>
    </div>
  `;
  setTimeout(() => document.getElementById('loginEmail')?.focus(), 50);
}

function initials(name) {
  const p = (name||'').trim().split(/\s+/);
  return ((p[0]?.[0]||'') + (p[1]?.[0]||'')).toUpperCase() || '—';
}

// XSS-safe HTML escape for any user-controlled string rendered via innerHTML/template literals.
// Rendering data unescaped when it came from another user is XSS; escape defensively.
function esc(s) {
  if (s === null || s === undefined) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderApp() {
  const u = ME;
  if (!u) { renderLogin(); return; }
  const isSA = u.role === 'super_admin';
  const isAdm = u.role === 'admin' || isSA;
  const canFin = isAdm;
  document.getElementById('appRoot').innerHTML = `
    <div class="app">
      <aside>
        <div>
          <div class="brand">ES One</div>
          <div class="brand-sub">Управленческий дашборд</div>
        </div>
        <nav id="nav">
          ${canFin ? `
          <div class="group">
            <div class="group-label">Финансы</div>
            <a data-page="overview">Обзор</a>
            <a data-page="revenue">Доходы</a>
            <a data-page="expense">Расходы</a>
            <a data-page="ebitda">EBITDA</a>
            <a data-page="cash">Остаток на счетах</a>
            <a data-page="dz">Дебиторка</a>
          </div>` : ''}
          <div class="group">
            <div class="group-label">HR</div>
            <a data-page="org">Оргструктура</a>
          </div>
          <div class="group">
            <div class="group-label">Продажи</div>
            <a data-page="sales_b2b"><span>B2B</span><span class="soon">soon</span></a>
            <a data-page="sales_b2g"><span>B2G</span><span class="soon">soon</span></a>
          </div>
          <div class="group">
            <div class="group-label">Процессы</div>
            <a data-page="processes_darlean"><span>Darlean</span><span class="soon">soon</span></a>
          </div>
          <div class="group">
            <div class="group-label">Настройки</div>
            <a data-page="profile">Профиль</a>
            ${isSA ? '<a data-page="users">Пользователи</a>' : ''}
            ${isSA ? '<a data-page="audit">Журнал событий</a>' : ''}
          </div>
        </nav>
        <div class="user-chip">
          <div class="avatar">${esc(initials(u.name))}</div>
          <div class="info">
            <div class="name">${esc(u.name)}</div>
            <div class="role">${esc(ROLES[u.role].label)}</div>
          </div>
          <button class="logout-btn" onclick="logout()">Выйти</button>
        </div>
      </aside>
      <main id="root"></main>
    </div>
  `;
  document.querySelectorAll('#nav a').forEach(a => a.onclick = () => goto(a.dataset.page));
  const first = canFin ? 'overview' : 'org';
  goto(first);
}

document.addEventListener('DOMContentLoaded', tryAutoLogin);

// ==== Global filter state ====
const filterState = {
  year: 2026,
  months: new Set([1,2,3,4,5,6,7,8,9,10,11,12]),
  filials: new Set(),  // populated in initFiltersFromData() after login
};
const dzState = {
  div: '__all__',
  org: '__all__',
  status: '__all__',
  responsible: '__all__',
  bucket: '__all__',  // '__all__' | '30-60' | '61-90' | '91-365' | '365+'
  search: '',
};

const orgState = {
  country: 'kz',
  dept: '__all__',
  view: 'tree',  // 'flat' | 'tree' — иерархия по умолчанию
  focusId: null,  // current focus node in tree view
};

// ==== Formatters ====
const fmt = (n, d=0) => (n===null||n===undefined||isNaN(n))?'—':(n<0?'−':'')+Math.abs(n).toLocaleString('ru-RU',{maximumFractionDigits:d,minimumFractionDigits:d});
const fmtCompact = (n) => {
  if (n===null||n===undefined||isNaN(n)) return '—';
  const s = n<0?'−':'', a = Math.abs(n);
  if (a>=1e6) return s+(a/1e6).toLocaleString('ru-RU',{maximumFractionDigits:2})+' млрд';
  if (a>=1e3) return s+(a/1e3).toLocaleString('ru-RU',{maximumFractionDigits:1})+' млн';
  return s+a.toLocaleString('ru-RU',{maximumFractionDigits:0})+' тыс';
};
const fmtPct = (n,d=1) => (n===null||n===undefined||isNaN(n))?'—':(n<0?'−':'')+Math.abs(n).toFixed(d)+'%';
const M = ['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек'];

// ==== Data slice helpers ====
// atoms = [m, g, ff, vid, statya, v]
const IDX = { m:0, g:1, ff:2, vid:3, st:4, v:5 };

function filteredAtoms() {
  return DATA.atoms.filter(a => filterState.months.has(a[0]) && filterState.filials.has(a[2]));
}

function sumBy(atoms, keyFn) {
  const m = new Map();
  for (const a of atoms) {
    const k = keyFn(a);
    m.set(k, (m.get(k)||0) + a[5]);
  }
  return m;
}

function activeMonths() { return [...filterState.months].sort((a,b)=>a-b); }
function activeMonthLabels() { return activeMonths().map(m => M[m-1]); }
function monthlySeries(atoms, group) {
  const months = activeMonths();
  const map = new Map(months.map(m => [m, 0]));
  for (const a of atoms) if (a[1] === group && map.has(a[0])) map.set(a[0], map.get(a[0]) + a[5]);
  return months.map(m => +map.get(m).toFixed(1));
}

function totalOf(atoms, group) {
  let s = 0;
  for (const a of atoms) if (a[1] === group) s += a[5];
  return s;
}

// ==== Charts (SVG) ====
function barChart(series, opts={}) {
  const {width=560, height=180, labels=M, colors=['#111827','#9ca3af']} = opts;
  const seriesArr = Array.isArray(series[0]) ? series : [series];
  const all = seriesArr.flat();
  const max = Math.max(...all, 0), min = Math.min(...all, 0);
  const pad = {l:52, r:12, t:12, b:24};
  const iw = width-pad.l-pad.r, ih = height-pad.t-pad.b;
  const n = seriesArr[0].length;
  const groupW = iw / n;
  const barW = Math.min(24, groupW * 0.75 / seriesArr.length);
  const scale = v => pad.t + ih - ((v-min)/(max-min||1)) * ih;
  const zeroY = scale(0);
  let out = `<svg viewBox="0 0 ${width} ${height}" width="100%" height="${height}">`;
  for (let g=0; g<=4; g++) {
    const y = pad.t + (ih/4)*g;
    out += `<line x1="${pad.l}" x2="${width-pad.r}" y1="${y}" y2="${y}" stroke="#f0f0f0"/>`;
    const val = max - ((max-min)/4)*g;
    out += `<text x="${pad.l-6}" y="${y+3}" font-size="10" fill="#6b7280" text-anchor="end">${fmtCompact(val)}</text>`;
  }
  if (zeroY > pad.t && zeroY < pad.t+ih) out += `<line x1="${pad.l}" x2="${width-pad.r}" y1="${zeroY}" y2="${zeroY}" stroke="#d1d5db"/>`;
  seriesArr.forEach((ser, si) => {
    ser.forEach((v,i) => {
      const cx = pad.l + groupW*i + groupW/2 - (seriesArr.length*barW)/2 + si*barW;
      const y = v>=0 ? scale(v) : zeroY;
      const h = Math.abs(scale(v) - zeroY);
      out += `<rect x="${cx}" y="${y}" width="${barW}" height="${h}" fill="${colors[si%colors.length]}" opacity="0.9" rx="1"><title>${labels[i]}: ${fmt(v,1)}</title></rect>`;
    });
  });
  labels.forEach((lb,i) => {
    const cx = pad.l + groupW*i + groupW/2;
    out += `<text x="${cx}" y="${height-6}" font-size="10" fill="#6b7280" text-anchor="middle">${lb}</text>`;
  });
  return out + '</svg>';
}

function lineChart(series, opts={}) {
  const {width=560, height=200, labels=M, colors=['#111827','#059669','#dc2626','#6b7280']} = opts;
  const seriesArr = Array.isArray(series[0]) ? series : [series];
  const all = seriesArr.flat();
  const max = Math.max(...all, 0), min = Math.min(...all, 0);
  const pad = {l:52, r:12, t:16, b:24};
  const iw = width-pad.l-pad.r, ih = height-pad.t-pad.b;
  const n = seriesArr[0].length;
  const scale = v => pad.t + ih - ((v-min)/(max-min||1)) * ih;
  const xat = i => pad.l + (n>1 ? (iw/(n-1)) * i : iw/2);
  let out = `<svg viewBox="0 0 ${width} ${height}" width="100%" height="${height}">`;
  for (let g=0; g<=4; g++) {
    const y = pad.t + (ih/4)*g;
    out += `<line x1="${pad.l}" x2="${width-pad.r}" y1="${y}" y2="${y}" stroke="#f0f0f0"/>`;
    const val = max - ((max-min)/4)*g;
    out += `<text x="${pad.l-6}" y="${y+3}" font-size="10" fill="#6b7280" text-anchor="end">${fmtCompact(val)}</text>`;
  }
  const zeroY = scale(0);
  if (zeroY > pad.t && zeroY < pad.t+ih) out += `<line x1="${pad.l}" x2="${width-pad.r}" y1="${zeroY}" y2="${zeroY}" stroke="#d1d5db"/>`;
  seriesArr.forEach((ser, si) => {
    const pts = ser.map((v,i) => `${xat(i)},${scale(v)}`).join(' ');
    out += `<polyline points="${pts}" fill="none" stroke="${colors[si%colors.length]}" stroke-width="2"/>`;
    ser.forEach((v,i) => {
      out += `<circle cx="${xat(i)}" cy="${scale(v)}" r="3" fill="${colors[si%colors.length]}"><title>${labels[i]}: ${fmt(v,0)}</title></circle>`;
    });
  });
  labels.forEach((lb,i) => {
    out += `<text x="${xat(i)}" y="${height-6}" font-size="10" fill="#6b7280" text-anchor="middle">${lb}</text>`;
  });
  return out + '</svg>';
}

function donut(items, opts={}) {
  const {size=180, inner=55, outer=85} = opts;
  const total = items.reduce((s,x)=>s+Math.abs(x.value),0);
  if (!total) return '<div class="empty-state" style="padding:20px">Нет данных</div>';
  const cx = size/2, cy = size/2;
  const palette = ['#111827','#374151','#6b7280','#9ca3af','#d1d5db','#e5e7eb','#0f766e','#14b8a6','#a3e635','#f59e0b','#ef4444','#8b5cf6'];
  let a0 = -Math.PI/2;
  let out = `<svg viewBox="0 0 ${size} ${size}" width="${size}" height="${size}">`;
  items.forEach((it,i) => {
    const frac = Math.abs(it.value)/total;
    const a1 = a0 + frac * Math.PI*2;
    const large = frac > 0.5 ? 1 : 0;
    const x0 = cx + outer*Math.cos(a0), y0 = cy + outer*Math.sin(a0);
    const x1 = cx + outer*Math.cos(a1), y1 = cy + outer*Math.sin(a1);
    const x2 = cx + inner*Math.cos(a1), y2 = cy + inner*Math.sin(a1);
    const x3 = cx + inner*Math.cos(a0), y3 = cy + inner*Math.sin(a0);
    const color = it.color || palette[i % palette.length];
    out += `<path d="M ${x0} ${y0} A ${outer} ${outer} 0 ${large} 1 ${x1} ${y1} L ${x2} ${y2} A ${inner} ${inner} 0 ${large} 0 ${x3} ${y3} Z" fill="${color}"><title>${it.label}: ${fmtCompact(it.value)} (${(frac*100).toFixed(1)}%)</title></path>`;
    a0 = a1;
  });
  return out + '</svg>';
}

// ==== Filter bar UI ====
function renderFilterBar(page) {
  const monthChips = M.map((m,i) => {
    const on = filterState.months.has(i+1);
    return `<button class="chip-btn ${on?'on':''}" onclick="toggleMonth(${i+1})">${m}</button>`;
  }).join('');
  const filialsCount = filterState.filials.size;
  const totalFilials = DATA.filials.length;
  const filialsLabel = filialsCount === totalFilials ? 'Все' : (filialsCount + ' из ' + totalFilials);
  const filialDD = `
    <div class="filter-dropdown">
      <button class="filter-dd-btn" onclick="toggleFilialsMenu()">
        <span>${filialsLabel}</span>
        <svg width="8" height="8" viewBox="0 0 8 8"><path d="M0 2 L4 6 L8 2" stroke="#6b7280" fill="none" stroke-width="1.5"/></svg>
      </button>
      <div class="filter-dd-menu" id="filialsMenu">
        <div class="filter-dd-quick"><a onclick="setAllFilials(true)">Все</a><a onclick="setAllFilials(false)">Ничего</a></div>
        ${DATA.filials.map(f => `<label class="filter-dd-item"><input type="checkbox" ${filterState.filials.has(f)?'checked':''} onchange="toggleFilial('${f.replace(/'/g,"\\'")}')"><span>${f}</span></label>`).join('')}
      </div>
    </div>`;
  return `
    <div class="filter-bar">
      <div class="filter-group">
        <span class="filter-label">Год</span>
        <select class="filter-select" onchange="setYear(this.value)">
          <option value="2026">2026 (бюджет)</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">Месяцы</span>
        <div class="filter-chips">
          ${monthChips}
          <button class="chip-btn quick" onclick="setAllMonths(true)">Все</button>
          <button class="chip-btn quick" onclick="setAllMonths(false)">Ничего</button>
        </div>
      </div>
      <div class="filter-group">
        <span class="filter-label">Филиалы</span>
        ${filialDD}
      </div>
    </div>`;
}

function toggleMonth(m) {
  if (filterState.months.has(m)) filterState.months.delete(m); else filterState.months.add(m);
  if (filterState.months.size === 0) filterState.months.add(m);
  rerender();
}
function setAllMonths(on) {
  filterState.months.clear();
  if (on) for (let i=1; i<=12; i++) filterState.months.add(i);
  else filterState.months.add(1);
  rerender();
}
function toggleFilial(f) {
  if (filterState.filials.has(f)) filterState.filials.delete(f); else filterState.filials.add(f);
  if (filterState.filials.size === 0) filterState.filials.add(f);
  rerender();
}
function setAllFilials(on) {
  filterState.filials.clear();
  if (on) DATA.filials.forEach(f => filterState.filials.add(f));
  else filterState.filials.add(DATA.filials[0]);
  rerender();
}
function toggleFilialsMenu() { document.getElementById('filialsMenu').classList.toggle('open'); }
function setYear(y) { filterState.year = +y; rerender(); }
document.addEventListener('click', e => {
  if (!e.target.closest('.filter-dropdown')) {
    document.querySelectorAll('.filter-dd-menu').forEach(m => m.classList.remove('open'));
  }
});

// ==== Pages ====
const pages = {};

pages.overview = () => {
  const at = filteredAtoms();
  const rev = totalOf(at, 'Доходы');
  const expDept = totalOf(at, 'Расходы');
  const expKC = totalOf(at, 'Расходы КЦ');
  const totalExp = expDept + expKC;
  const eb = totalOf(at, 'EBITDA');
  const margin = rev ? eb/rev*100 : 0;
  const ost = DATA.ostatok['ИТОГО остаток ДС'] || 0;
  const revM = monthlySeries(at, 'Доходы');
  const expM = monthlySeries(at, 'Расходы').map((v,i) => v + monthlySeries(at, 'Расходы КЦ')[i]);
  const ebM = monthlySeries(at, 'EBITDA');

  // Top filials by revenue (within filter)
  const byFf = sumBy(at.filter(a => a[1]==='Доходы'), a => a[2]);
  const ffArr = [...byFf.entries()].sort((a,b) => b[1]-a[1]);

  // Structure of revenue by service
  const bySt = sumBy(at.filter(a => a[1]==='Доходы' && a[5] > 0), a => a[4]);
  const stArr = [...bySt.entries()].filter(([k,v]) => v>0).sort((a,b) => b[1]-a[1]).slice(0,8);
  const stTotal = stArr.reduce((s,x)=>s+x[1],0);

  const ys = ['2020','2021','2022','2023','2024','2025','2026'];
  const revYearly = ys.map(y => DATA.pl_yearly['Доход от основной деятельности'][y] || 0);
  const ebYearly = ys.map(y => DATA.pl_ebitda[y] || 0);

  return `
    <div class="page-head">
      <h1>Обзор</h1>
      <div class="sub">Бюджет 2026 · валюта — тыс. ₸</div>
      ${renderFilterBar('overview')}
    </div>

    <div class="kpi-grid">
      <div class="kpi"><div class="label">Выручка</div>
        <div class="value num">${fmtCompact(rev)} ₸</div>
        <div class="delta">${filterState.months.size < 12 ? filterState.months.size + ' мес.' : 'Год'} · ${filterState.filials.size < DATA.filials.length ? filterState.filials.size + '/' + DATA.filials.length + ' филиалов' : 'все филиалы'}</div>
      </div>
      <div class="kpi"><div class="label">Расходы</div>
        <div class="value num">${fmtCompact(-totalExp)} ₸</div>
        <div class="delta">из них КЦ ${fmtCompact(-expKC)} ₸</div>
      </div>
      <div class="kpi"><div class="label">EBITDA</div>
        <div class="value num">${fmtCompact(eb)} ₸</div>
        <div class="delta ${margin>=15?'pos':(margin>0?'':'neg')}">Маржа ${fmtPct(margin)}</div>
      </div>
      <div class="kpi"><div class="label">Остаток на счетах</div>
        <div class="value num">${fmt(ost/1e6,1)} млн ₸</div>
        <div class="delta">на снимок · всё по группе</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-head"><h3>Помесячно: выручка · расходы · EBITDA</h3>
          <button class="more" onclick="openModal('overview_monthly')">Подробнее →</button></div>
        ${lineChart([revM, expM.map(v => -v), ebM], {height:220, colors:['#111827','#dc2626','#059669'], labels: activeMonthLabels()})}
        <div class="legend">
          <div class="item"><span class="dot" style="background:#111827"></span>Выручка</div>
          <div class="item"><span class="dot" style="background:#dc2626"></span>Расходы (модуль)</div>
          <div class="item"><span class="dot" style="background:#059669"></span>EBITDA</div>
        </div>
      </div>
      <div class="card">
        <div class="card-head"><h3>Топ филиалов по выручке</h3>
          <button class="more" onclick="openModal('overview_depts')">Все →</button></div>
        ${ffArr.slice(0,7).map(([f,v]) => {
          const max = ffArr[0][1] || 1;
          return `<div class="bar-row">
            <div class="bar-name" title="${f}">${f}</div>
            <div class="bar-track"><div class="bar-fill" style="width:${Math.max(0,v)/max*100}%"></div></div>
            <div class="bar-value">${fmtCompact(v)}</div>
          </div>`;
        }).join('')}
      </div>
    </div>

    <div class="grid-2" style="margin-top:16px">
      <div class="card">
        <div class="card-head"><h3>Многолетняя динамика · Выручка и EBITDA</h3>
          <button class="more" onclick="openModal('overview_multiyear')">Подробнее →</button>
        </div>
        <div style="font-size:11px; color:var(--muted); margin-bottom:8px">2020–2025 факт (PL_ES) · 2026 прогноз · не зависит от фильтров</div>
        ${barChart([revYearly, ebYearly], {height:220, labels:ys, colors:['#111827','#059669']})}
        <div class="legend">
          <div class="item"><span class="dot" style="background:#111827"></span>Выручка</div>
          <div class="item"><span class="dot" style="background:#059669"></span>EBITDA</div>
        </div>
      </div>
      <div class="card">
        <div class="card-head"><h3>Структура выручки · виды услуг</h3>
          <button class="more" onclick="openModal('overview_services')">Все →</button></div>
        <div style="display:flex; align-items:center; gap:24px">
          ${donut(stArr.map(([k,v]) => ({label:k, value:v})), {size:180})}
          <div style="flex:1; font-size:12px">
            ${stArr.map(([k,v],i) => {
              const palette = ['#111827','#374151','#6b7280','#9ca3af','#d1d5db','#e5e7eb','#0f766e','#14b8a6'];
              return `<div style="display:flex; align-items:center; gap:6px; margin:4px 0">
                <span style="width:8px;height:8px;border-radius:2px;background:${palette[i]}; display:inline-block"></span>
                <span style="flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap">${k.replace('Доход от услуг ','').replace('Доход от ','')}</span>
                <span style="color:var(--muted)">${stTotal?(v/stTotal*100).toFixed(1):0}%</span>
              </div>`;
            }).join('')}
          </div>
        </div>
      </div>
    </div>

    <div class="footer-note">
      <b>Источники:</b> PBI — детальный бюджет 2026 (17 205 агрегированных записей, ${fmtCompact(rev)} выручки в фильтре).
      PL_ES — многолетний тренд 2020–2026 (только для графика годовой динамики).
      Остаток на счете — снимок ДС на текущий момент.
      Оргструктура — только действующие сотрудники (ACTIVE в исходной таблице).
    </div>
  `;
};

pages.revenue = () => {
  const at = filteredAtoms();
  const revAtoms = at.filter(a => a[1]==='Доходы');
  const rev = revAtoms.reduce((s,a)=>s+a[5],0);
  const revM = monthlySeries(at, 'Доходы');
  const byFf = [...sumBy(revAtoms, a=>a[2]).entries()].sort((a,b) => b[1]-a[1]);
  const byStAll = [...sumBy(revAtoms, a=>a[4]).entries()].filter(([k,v]) => v>0).sort((a,b) => b[1]-a[1]);
  const ys = ['2020','2021','2022','2023','2024','2025','2026'];
  const revY = ys.map(y => DATA.pl_yearly['Доход от основной деятельности'][y] || 0);
  const maxM = Math.max(...revM);
  const minM = Math.min(...revM.filter(v => v !== 0));

  return `
    <div class="page-head">
      <h1>Доходы</h1>
      <div class="sub">Структура выручки · всё в тыс. ₸</div>
      ${renderFilterBar('revenue')}
    </div>

    <div class="stat-inline">
      <div><span class="k">Выручка в фильтре</span><span class="v num">${fmt(rev,0)}</span></div>
      <div><span class="k">Средняя за месяц</span><span class="v num">${fmt(rev/Math.max(1,filterState.months.size),0)}</span></div>
      <div><span class="k">Пик месяц</span><span class="v num">${maxM ? activeMonthLabels()[revM.indexOf(maxM)] + ' · ' + fmt(maxM,0) : '—'}</span></div>
      <div><span class="k">Минимум</span><span class="v num">${isFinite(minM) ? activeMonthLabels()[revM.indexOf(minM)] + ' · ' + fmt(minM,0) : '—'}</span></div>
      <div><span class="k">Филиалов в фильтре</span><span class="v">${byFf.filter(([k,v])=>v>0).length}</span></div>
      <div><span class="k">Видов услуг</span><span class="v">${byStAll.length}</span></div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-head"><h3>Выручка по месяцам</h3>
          <button class="more" onclick="openModal('rev_monthly')">Подробнее →</button></div>
        ${barChart(revM, {height:220, labels: activeMonthLabels()})}
      </div>
      <div class="card">
        <div class="card-head"><h3>Годовая динамика</h3></div>
        <div style="font-size:11px; color:var(--muted); margin-bottom:8px">Не зависит от фильтров · источник PL_ES</div>
        ${barChart(revY, {height:220, labels: ys})}
      </div>
    </div>

    <div class="grid-2" style="margin-top:16px">
      <div class="card">
        <div class="card-head"><h3>Выручка по филиалам</h3>
          <button class="more" onclick="openModal('rev_depts')">Все →</button></div>
        ${byFf.slice(0,10).map(([f,v]) => {
          const max = byFf[0][1] || 1;
          return `<div class="bar-row">
            <div class="bar-name" title="${f}">${f}</div>
            <div class="bar-track"><div class="bar-fill" style="width:${Math.max(0,v)/max*100}%"></div></div>
            <div class="bar-value">${fmtCompact(v)}</div>
          </div>`;
        }).join('')}
      </div>
      <div class="card">
        <div class="card-head"><h3>Топ видов услуг</h3>
          <button class="more" onclick="openModal('rev_services')">Все ${byStAll.length} →</button></div>
        <div class="table-scroll"><table><thead><tr><th>Услуга</th><th>Сумма</th><th>%</th></tr></thead><tbody>
          ${byStAll.slice(0,10).map(([k,v]) => {
            const sum = byStAll.reduce((s,x)=>s+x[1],0);
            return `<tr><td>${k || '(без указания)'}</td><td class="num">${fmtCompact(v)}</td><td class="num" style="color:var(--muted)">${sum?(v/sum*100).toFixed(1):0}%</td></tr>`;
          }).join('')}
        </tbody></table></div>
      </div>
    </div>
  `;
};

pages.expense = () => {
  const at = filteredAtoms();
  const expAtoms = at.filter(a => a[1]==='Расходы' || a[1]==='Расходы КЦ');
  const totalExp = expAtoms.reduce((s,a)=>s+a[5],0);
  const rev = totalOf(at, 'Доходы');
  const expM = monthlySeries(at, 'Расходы').map((v,i) => v + monthlySeries(at, 'Расходы КЦ')[i]);
  const byVid = [...sumBy(expAtoms, a=>a[3]).entries()].sort((a,b) => a[1]-b[1]);
  const byStAll = [...sumBy(expAtoms, a=>a[4]).entries()].filter(([k,v]) => v<0).sort((a,b) => a[1]-b[1]);
  const byFf = [...sumBy(expAtoms, a=>a[2]).entries()].sort((a,b) => a[1]-b[1]);

  return `
    <div class="page-head">
      <h1>Расходы</h1>
      <div class="sub">Структура расходов · всё в тыс. ₸</div>
      ${renderFilterBar('expense')}
    </div>

    <div class="stat-inline">
      <div><span class="k">Расходы в фильтре</span><span class="v num neg">${fmt(totalExp,0)}</span></div>
      <div><span class="k">Средние за месяц</span><span class="v num">${fmt(totalExp/Math.max(1,filterState.months.size),0)}</span></div>
      <div><span class="k">% от выручки</span><span class="v num">${rev ? fmtPct(-totalExp/rev*100) : '—'}</span></div>
      <div><span class="k">Статей расходов</span><span class="v">${byStAll.length}</span></div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-head"><h3>Структура по типам</h3>
          <button class="more" onclick="openModal('exp_vid')">Помесячно →</button></div>
        ${donut(byVid.filter(x=>x[1]<0).map(([k,v]) => ({label:k, value:-v})), {size:180})}
        <div class="legend">
          ${byVid.filter(x=>x[1]<0).map(([k,v],i) => {
            const palette = ['#111827','#374151','#6b7280','#9ca3af','#d1d5db','#0f766e'];
            return `<div class="item"><span class="dot" style="background:${palette[i]}"></span>${k}: ${fmtCompact(-v)}</div>`;
          }).join('')}
        </div>
      </div>
      <div class="card">
        <div class="card-head"><h3>Расходы по месяцам</h3>
          <button class="more" onclick="openModal('exp_monthly')">Подробнее →</button></div>
        ${barChart(expM.map(v => -v), {height:220, colors:['#dc2626'], labels: activeMonthLabels()})}
      </div>
    </div>

    <div class="grid-2" style="margin-top:16px">
      <div class="card">
        <div class="card-head"><h3>Топ статей расходов</h3>
          <button class="more" onclick="openModal('exp_statya')">Все ${byStAll.length} →</button></div>
        <div class="table-scroll"><table><thead><tr><th>Статья</th><th>Сумма</th></tr></thead><tbody>
          ${byStAll.slice(0,12).map(([k,v]) => `<tr><td>${k || '(без указания)'}</td><td class="num neg">${fmtCompact(-v)}</td></tr>`).join('')}
        </tbody></table></div>
      </div>
      <div class="card">
        <div class="card-head"><h3>Расходы по филиалам</h3>
          <button class="more" onclick="openModal('exp_depts')">Все →</button></div>
        ${byFf.slice(0,10).map(([f,v]) => {
          const max = Math.abs(byFf[0][1]) || 1;
          return `<div class="bar-row">
            <div class="bar-name" title="${f}">${f}</div>
            <div class="bar-track"><div class="bar-fill neg" style="width:${Math.abs(v)/max*100}%"></div></div>
            <div class="bar-value neg">${fmtCompact(v)}</div>
          </div>`;
        }).join('')}
      </div>
    </div>
  `;
};

pages.ebitda = () => {
  const at = filteredAtoms();
  const rev = totalOf(at, 'Доходы');
  const eb = totalOf(at, 'EBITDA');
  const ebDept = totalOf(at, 'EBITDA_dept');
  const margin = rev ? eb/rev*100 : 0;
  const ebM = monthlySeries(at, 'EBITDA');
  const marginM = ebM.map((v,i) => {
    const rM = monthlySeries(at, 'Доходы')[i];
    return rM ? v/rM*100 : 0;
  });
  const ys = ['2020','2021','2022','2023','2024','2025','2026'];
  const ebY = ys.map(y => DATA.pl_ebitda[y] || 0);
  const revY = ys.map(y => DATA.pl_yearly['Доход от основной деятельности'][y] || 0);
  const marginY = ebY.map((v,i) => revY[i] ? v/revY[i]*100 : 0);
  const ebByFf = [...sumBy(at.filter(a => a[1]==='EBITDA'), a=>a[2]).entries()].sort((a,b) => b[1]-a[1]);
  const revByFf = new Map([...sumBy(at.filter(a => a[1]==='Доходы'), a=>a[2]).entries()]);

  return `
    <div class="page-head">
      <h1>EBITDA · Прибыльность</h1>
      <div class="sub">Многолетняя динамика и структура по филиалам · тыс. ₸</div>
      ${renderFilterBar('ebitda')}
    </div>

    <div class="stat-inline">
      <div><span class="k">EBITDA в фильтре</span><span class="v num ${eb>=0?'pos':'neg'}">${fmt(eb,0)}</span></div>
      <div><span class="k">Маржа</span><span class="v num">${fmtPct(margin)}</span></div>
      <div><span class="k">EBITDA_dept (до КЦ)</span><span class="v num">${fmt(ebDept,0)}</span></div>
      <div><span class="k">EBITDA 2025 факт</span><span class="v num">${fmt(DATA.pl_ebitda['2025'],0)}</span></div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-head"><h3>EBITDA · многолетняя динамика</h3></div>
        <div style="font-size:11px; color:var(--muted); margin-bottom:8px">Не зависит от фильтров · источник PL_ES</div>
        ${barChart(ebY, {height:220, labels:ys, colors:['#059669']})}
      </div>
      <div class="card">
        <div class="card-head"><h3>Маржа EBITDA по годам</h3></div>
        <div style="font-size:11px; color:var(--muted); margin-bottom:8px">Не зависит от фильтров · источник PL_ES</div>
        ${lineChart(marginY, {height:220, labels:ys, colors:['#0f766e']})}
      </div>
    </div>

    <div class="grid-2" style="margin-top:16px">
      <div class="card">
        <div class="card-head"><h3>EBITDA по месяцам</h3>
          <button class="more" onclick="openModal('ebitda_monthly')">Подробнее →</button></div>
        ${barChart(ebM, {height:220, colors:['#059669'], labels: activeMonthLabels()})}
      </div>
      <div class="card">
        <div class="card-head"><h3>EBITDA по филиалам</h3>
          <button class="more" onclick="openModal('ebitda_depts')">Все →</button></div>
        <div class="table-scroll"><table><thead><tr><th>Филиал</th><th>Выручка</th><th>EBITDA</th><th>Маржа</th></tr></thead><tbody>
          ${ebByFf.map(([f,v]) => {
            const r = revByFf.get(f) || 0;
            const m = r ? v/r*100 : 0;
            return `<tr><td>${f}</td>
              <td class="num">${fmtCompact(r)}</td>
              <td class="num ${v>=0?'pos':'neg'}">${fmtCompact(v)}</td>
              <td class="num ${m>=0?'':'neg'}">${fmtPct(m)}</td></tr>`;
          }).join('')}
        </tbody></table></div>
      </div>
    </div>
  `;
};

pages.cash = () => {
  const rows = Object.entries(DATA.ostatok).filter(([k]) => k !== 'ИТОГО остаток ДС');
  const total = DATA.ostatok['ИТОГО остаток ДС'];
  // For coverage: use unfiltered total 2026 expenses
  const totalExp2026 = DATA.atoms.filter(a => a[1]==='Расходы' || a[1]==='Расходы КЦ').reduce((s,a)=>s+a[5],0);
  const totalRev2026 = DATA.atoms.filter(a => a[1]==='Доходы').reduce((s,a)=>s+a[5],0);
  return `
    <div class="page-head">
      <h1>Остаток денежных средств</h1>
      <div class="sub">Текущий кассовый остаток по группе · валюта — ₸ (единицы, не тыс.)</div>
    </div>

    <div class="kpi-grid">
      <div class="kpi"><div class="label">ИТОГО остаток ДС</div><div class="value num">${fmt(total/1e6,1)} млн ₸</div><div class="delta">${fmt(total,0)} ₸</div></div>
      ${rows.map(([k,v]) => `
        <div class="kpi"><div class="label">${k}</div><div class="value num">${fmt(v/1e6,1)} млн ₸</div><div class="delta">${(v/total*100).toFixed(1)}% от общего</div></div>
      `).join('')}
    </div>

    <div class="card">
      <div class="card-head"><h3>Разбивка остатка</h3></div>
      ${rows.map(([k,v]) => {
        return `<div class="bar-row">
          <div class="bar-name">${k}</div>
          <div class="bar-track"><div class="bar-fill" style="width:${v/total*100}%"></div></div>
          <div class="bar-value">${fmt(v/1e6,1)} млн ₸</div>
        </div>`;
      }).join('')}
    </div>

    <div class="card" style="margin-top:16px">
      <div class="card-head"><h3>Метрики покрытия · относительно годового бюджета 2026</h3></div>
      <table><tbody>
        <tr><td>Средние месячные расходы 2026 (план)</td><td class="num">${fmt(-totalExp2026/12*1000,0)} ₸</td></tr>
        <tr><td>Средняя месячная выручка 2026 (план)</td><td class="num">${fmt(totalRev2026/12*1000,0)} ₸</td></tr>
        <tr><td>Покрытие остатком месяцев расходов</td><td class="num">${(total/(-totalExp2026/12*1000)).toFixed(2)} мес.</td></tr>
        <tr><td>Соотношение остаток / плановая выручка</td><td class="num">${(total/(totalRev2026*1000)*100).toFixed(2)}%</td></tr>
      </tbody></table>
    </div>
  `;
};

// ==== DZ (accounts receivable) page ====
function dzFilteredItems() {
  const it = DATA.dz.line_items;
  return it.filter(x => {
    if (dzState.div !== '__all__' && x.div !== dzState.div) return false;
    if (dzState.org !== '__all__' && x.org !== dzState.org) return false;
    if (dzState.status !== '__all__') {
      const s = x.status || '(без статуса)';
      if (s !== dzState.status) return false;
    }
    if (dzState.responsible !== '__all__') {
      const r = x.responsible || '(не назначен)';
      if (r !== dzState.responsible) return false;
    }
    if (dzState.bucket !== '__all__') {
      const bkey = {'30-60':'d_30_60','61-90':'d_61_90','91-365':'d_91_365','365+':'d_365'}[dzState.bucket];
      if (!(x[bkey] > 0)) return false;
    }
    if (dzState.search) {
      const q = dzState.search.toLowerCase();
      if (!(x.buyer.toLowerCase().includes(q) || x.contract.toLowerCase().includes(q) || (x.comment||'').toLowerCase().includes(q))) return false;
    }
    return true;
  });
}

pages.dz = () => {
  const items = dzFilteredItems();
  const totals = { d_30_60:0, d_61_90:0, d_91_365:0, d_365:0, total:0 };
  items.forEach(x => { totals.d_30_60 += x.d_30_60; totals.d_61_90 += x.d_61_90; totals.d_91_365 += x.d_91_365; totals.d_365 += x.d_365; totals.total += x.total; });

  // Unique dimensions from full dataset
  const allDivs = [...new Set(DATA.dz.line_items.map(x => x.div))].sort();
  const allOrgs = [...new Set(DATA.dz.line_items.map(x => x.org))].sort();
  const allStatuses = [...new Set(DATA.dz.line_items.map(x => x.status || '(без статуса)'))].sort();
  // Ответственные: динамически из данных, отсортированы по числу позиций (desc)
  const respCounts = {};
  DATA.dz.line_items.forEach(x => { const r = x.responsible || '(не назначен)'; respCounts[r] = (respCounts[r]||0)+1; });
  const allResponsibles = Object.entries(respCounts).sort((a,b) => b[1]-a[1]).map(([k]) => k);

  // Latest comment date across all items (dd.mm.yyyy)
  const parseDt = s => {
    if (!s || s.length < 10) return null;
    const p = s.slice(0,10);
    if (p[2] === '.' && p[5] === '.') {
      const [d,m,y] = p.split('.');
      return y+m+d;  // yyyymmdd for sortable comparison
    }
    if (p[4] === '-' && p[7] === '-') {
      return p.replace(/-/g,'');
    }
    return null;
  };
  const commentDates = DATA.dz.line_items.map(x => x.comment_date).filter(Boolean);
  const parsedDates = commentDates.map(d => [parseDt(d), d]).filter(x => x[0]);
  parsedDates.sort((a,b) => b[0].localeCompare(a[0]));
  const latestCommentDate = parsedDates[0] ? parsedDates[0][1] : '—';
  const commentsCount = commentDates.length;

  const bucketBtn = (key, label) => `<button class="chip-btn ${dzState.bucket===key?'on':''}" onclick="setDzBucket('${key}')">${label}</button>`;

  // Aggregations within filter
  const byDiv = {};
  items.forEach(x => { byDiv[x.div] = (byDiv[x.div]||0) + x.total; });
  const divArr = Object.entries(byDiv).sort((a,b) => b[1]-a[1]);

  const byOrg = {};
  items.forEach(x => { byOrg[x.org] = (byOrg[x.org]||0) + x.total; });
  const orgArr = Object.entries(byOrg).sort((a,b) => b[1]-a[1]);

  const byBuyer = {};
  items.forEach(x => { byBuyer[x.buyer] = (byBuyer[x.buyer]||0) + x.total; });
  const buyerArr = Object.entries(byBuyer).sort((a,b) => b[1]-a[1]);

  const byStatus = {};
  items.forEach(x => { byStatus[x.status || '(без статуса)'] = (byStatus[x.status || '(без статуса)']||0) + x.total; });
  const statusArr = Object.entries(byStatus).sort((a,b) => b[1]-a[1]);

  const fmtM = v => (v/1e6).toLocaleString('ru-RU',{maximumFractionDigits: v/1e6>=100?0:1}) + ' млн';

  return `
    <div class="page-head">
      <h1>Дебиторская задолженность</h1>
      <div class="sub">
        Источник: <b>${DATA.dz.source_file}</b> · последний недельный срез в папке ДЗ ·
        значения в ₸ (не тыс.) ·
        последнее обновление статуса: <b>${latestCommentDate}</b> (${commentsCount} позиций с комментарием)
      </div>
      <div class="filter-bar">
        <div class="filter-group">
          <span class="filter-label">Возраст</span>
          <div class="filter-chips">
            ${bucketBtn('__all__','Все 30+')}
            ${bucketBtn('30-60','30–60 дн')}
            ${bucketBtn('61-90','61–90 дн')}
            ${bucketBtn('91-365','91–365 дн')}
            ${bucketBtn('365+','365+ дн')}
          </div>
        </div>
        <div class="filter-group">
          <span class="filter-label">Дивизион</span>
          <select class="filter-select" onchange="setDzDiv(this.value)">
            <option value="__all__">Все</option>
            ${allDivs.map(d => `<option value="${d.replace(/"/g,'&quot;')}"${dzState.div===d?' selected':''}>${d}</option>`).join('')}
          </select>
        </div>
        <div class="filter-group">
          <span class="filter-label">Юрлицо</span>
          <select class="filter-select" onchange="setDzOrg(this.value)">
            <option value="__all__">Все</option>
            ${allOrgs.map(o => `<option value="${o.replace(/"/g,'&quot;')}"${dzState.org===o?' selected':''}>${o}</option>`).join('')}
          </select>
        </div>
        <div class="filter-group">
          <span class="filter-label">Статус</span>
          <select class="filter-select" onchange="setDzStatus(this.value)">
            <option value="__all__">Все</option>
            ${allStatuses.map(s => `<option value="${s.replace(/"/g,'&quot;')}"${dzState.status===s?' selected':''}>${s}</option>`).join('')}
          </select>
        </div>
        <div class="filter-group">
          <span class="filter-label">Ответственный</span>
          <select class="filter-select" onchange="setDzResponsible(this.value)">
            <option value="__all__">Все (${allResponsibles.length})</option>
            ${allResponsibles.map(r => `<option value="${r.replace(/"/g,'&quot;')}"${dzState.responsible===r?' selected':''}>${r} · ${respCounts[r]}</option>`).join('')}
          </select>
        </div>
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi"><div class="label">ИТОГО 30+ дней</div>
        <div class="value num">${fmtM(totals.total)} ₸</div>
        <div class="delta">${items.length} позиций в фильтре</div></div>
      <div class="kpi"><div class="label">30–60 дней</div>
        <div class="value num">${fmtM(totals.d_30_60)} ₸</div>
        <div class="delta">${totals.total?(totals.d_30_60/totals.total*100).toFixed(1):0}%</div></div>
      <div class="kpi"><div class="label">61–90 дней</div>
        <div class="value num">${fmtM(totals.d_61_90)} ₸</div>
        <div class="delta">${totals.total?(totals.d_61_90/totals.total*100).toFixed(1):0}%</div></div>
      <div class="kpi"><div class="label">91–365 дней</div>
        <div class="value num" style="color:#b45309">${fmtM(totals.d_91_365)} ₸</div>
        <div class="delta">${totals.total?(totals.d_91_365/totals.total*100).toFixed(1):0}%</div></div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-head"><h3>Структура по возрасту</h3></div>
        <div style="display:flex; align-items:center; gap:24px">
          ${donut([
            {label:'30–60 дн', value: totals.d_30_60, color: '#9ca3af'},
            {label:'61–90 дн', value: totals.d_61_90, color: '#6b7280'},
            {label:'91–365 дн', value: totals.d_91_365, color: '#b45309'},
            {label:'365+ дн', value: totals.d_365, color: '#dc2626'},
          ].filter(x => x.value>0), {size:180})}
          <div style="flex:1">
            <div style="display:flex; align-items:center; gap:8px; padding:4px 0"><span style="width:10px; height:10px; background:#9ca3af; border-radius:2px"></span>30–60 дн · <b>${fmtM(totals.d_30_60)} ₸</b></div>
            <div style="display:flex; align-items:center; gap:8px; padding:4px 0"><span style="width:10px; height:10px; background:#6b7280; border-radius:2px"></span>61–90 дн · <b>${fmtM(totals.d_61_90)} ₸</b></div>
            <div style="display:flex; align-items:center; gap:8px; padding:4px 0"><span style="width:10px; height:10px; background:#b45309; border-radius:2px"></span>91–365 дн · <b>${fmtM(totals.d_91_365)} ₸</b></div>
            <div style="display:flex; align-items:center; gap:8px; padding:4px 0"><span style="width:10px; height:10px; background:#dc2626; border-radius:2px"></span>365+ дн · <b>${fmtM(totals.d_365)} ₸</b></div>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-head"><h3>По дивизионам</h3></div>
        ${divArr.map(([d,v]) => {
          const max = divArr[0][1] || 1;
          return `<div class="bar-row">
            <div class="bar-name" title="${d}">${d}</div>
            <div class="bar-track"><div class="bar-fill" style="width:${v/max*100}%"></div></div>
            <div class="bar-value">${fmtM(v)}</div>
          </div>`;
        }).join('')}
      </div>
    </div>

    <div class="grid-2" style="margin-top:16px">
      <div class="card">
        <div class="card-head"><h3>По юрлицам</h3>
          <button class="more" onclick="openModal('dz_org')">Все →</button></div>
        ${orgArr.map(([o,v]) => {
          const max = orgArr[0][1] || 1;
          return `<div class="bar-row">
            <div class="bar-name" title="${o}">${o}</div>
            <div class="bar-track"><div class="bar-fill" style="width:${v/max*100}%"></div></div>
            <div class="bar-value">${fmtM(v)}</div>
          </div>`;
        }).join('')}
      </div>
      <div class="card">
        <div class="card-head"><h3>По статусу работы с ДЗ</h3>
          <button class="more" onclick="openModal('dz_status')">Все →</button></div>
        <div class="table-scroll"><table><thead><tr><th>Статус</th><th>Сумма</th><th>%</th></tr></thead><tbody>
          ${statusArr.slice(0,8).map(([s,v]) => `<tr><td>${s}</td><td class="num">${fmtM(v)}</td><td class="num" style="color:var(--muted)">${totals.total?(v/totals.total*100).toFixed(1):0}%</td></tr>`).join('')}
        </tbody></table></div>
      </div>
    </div>

    <div class="card" style="margin-top:16px">
      <div class="card-head"><h3>Топ должников</h3>
        <button class="more" onclick="openModal('dz_all')">Все ${items.length} позиций →</button></div>
      <div class="table-scroll"><table><thead><tr><th>Покупатель</th><th style="text-align:left">Юрлицо</th><th style="text-align:left">Дивизион</th><th>30–60</th><th>61–90</th><th>91–365</th><th>365+</th><th>Всего</th></tr></thead><tbody>
        ${buyerArr.slice(0,15).map(([b,total]) => {
          const rowItems = items.filter(x => x.buyer === b);
          const bd = { d_30_60:0, d_61_90:0, d_91_365:0, d_365:0 };
          rowItems.forEach(x => { bd.d_30_60+=x.d_30_60; bd.d_61_90+=x.d_61_90; bd.d_91_365+=x.d_91_365; bd.d_365+=x.d_365; });
          const orgs = [...new Set(rowItems.map(x=>x.org))];
          const divs = [...new Set(rowItems.map(x=>x.div))];
          const orgTxt = orgs.length <= 1 ? orgs[0] : orgs[0] + ' + ещё ' + (orgs.length-1);
          const divTxt = divs.length <= 1 ? divs[0] : divs[0] + ' + ' + (divs.length-1);
          return `<tr>
            <td class="wrap-cell" style="max-width:280px">${b}</td>
            <td style="text-align:left; color:var(--muted); font-size:11.5px" title="${orgs.join(', ')}">${orgTxt}</td>
            <td style="text-align:left; color:var(--muted); font-size:11.5px" title="${divs.join(', ')}">${divTxt}</td>
            <td class="num">${bd.d_30_60 ? fmtM(bd.d_30_60) : '—'}</td>
            <td class="num">${bd.d_61_90 ? fmtM(bd.d_61_90) : '—'}</td>
            <td class="num" style="${bd.d_91_365?'color:#b45309':''}">${bd.d_91_365 ? fmtM(bd.d_91_365) : '—'}</td>
            <td class="num" style="${bd.d_365?'color:#dc2626':''}">${bd.d_365 ? fmtM(bd.d_365) : '—'}</td>
            <td class="num" style="font-weight:600">${fmtM(total)}</td>
          </tr>`;
        }).join('')}
      </tbody></table></div>
    </div>

    <div class="footer-note">
      Данные из последнего недельного среза <b>${DATA.dz.source_file}</b>. Каждую неделю в исходной папке появляется новый файл — при обновлении дашборда автоматически берётся самый свежий.
      Показаны только позиции с задолженностью 30+ дней (структура исходной таблицы).
    </div>
  `;
};

function setDzDiv(v) { dzState.div = v; rerender(); }
function setDzOrg(v) { dzState.org = v; rerender(); }
function setDzStatus(v) { dzState.status = v; rerender(); }
function setDzResponsible(v) { dzState.responsible = v; rerender(); }
function setDzBucket(v) { dzState.bucket = v; rerender(); }

pages.org = () => {
  const arr = orgState.country === 'kz' ? DATA.org_kz : DATA.org_uz;
  const allDepts = [...new Set(arr.map(e => e.dept))].sort();
  const filtered = orgState.dept === '__all__' ? arr : arr.filter(e => e.dept === orgState.dept);
  const noDeptCount = filtered.filter(e => e.dept === '(не указан)').length;

  const deptSelectOptions = ['<option value="__all__">Все отделы</option>'].concat(
    allDepts.map(d => `<option value="${d.replace(/"/g,'&quot;')}"${orgState.dept===d?' selected':''}>${d}</option>`)
  ).join('');

  return `
    <div class="page-head">
      <h1>Оргструктура</h1>
      <div class="sub">Действующие сотрудники</div>
      <div class="filter-bar">
        <div class="filter-group">
          <span class="filter-label">Страна</span>
          <div class="filter-chips">
            <button class="chip-btn ${orgState.country==='kz'?'on':''}" onclick="setOrgCountry('kz')">Казахстан · ${DATA.org_kz.length}</button>
            <button class="chip-btn ${orgState.country==='uz'?'on':''}" onclick="setOrgCountry('uz')">Узбекистан · ${DATA.org_uz.length}</button>
          </div>
        </div>
        <div class="filter-group">
          <span class="filter-label">Отдел</span>
          <select class="filter-select" onchange="setOrgDept(this.value)">${deptSelectOptions}</select>
        </div>
        <div class="filter-group">
          <span class="filter-label">Вид</span>
          <div class="filter-chips">
            <button class="chip-btn ${orgState.view==='tree'?'on':''}" onclick="setOrgView('tree')">Иерархия</button>
            <button class="chip-btn ${orgState.view==='flat'?'on':''}" onclick="setOrgView('flat')">Численность</button>
          </div>
        </div>
      </div>
    </div>
    ${orgState.view === 'flat' ? renderOrgFlat(filtered, noDeptCount) : renderOrgTree()}
  `;
};

function renderOrgFlat(filtered, noDeptCount) {
  const depts = {};
  filtered.forEach(e => { depts[e.dept] = (depts[e.dept]||0)+1; });
  const list = Object.entries(depts).sort((a,b) => b[1]-a[1]);
  const named = list.filter(([d]) => d !== '(не указан)');
  const top = named[0] || list[0] || ['—', 0];
  return `
    <div class="kpi-grid">
      <div class="kpi"><div class="label">Сотрудников</div><div class="value num pos">${filtered.length}</div>
        <div class="delta">${orgState.dept === '__all__' ? 'все отделы' : orgState.dept}</div></div>
      <div class="kpi"><div class="label">Названных отделов</div><div class="value num">${named.length}</div>
        ${noDeptCount ? `<div class="delta">${noDeptCount} без отдела</div>` : ''}
      </div>
      <div class="kpi"><div class="label">Средний размер отдела</div><div class="value num">${named.length?(filtered.filter(e=>e.dept!=='(не указан)').length/named.length).toFixed(1):'—'}</div></div>
      <div class="kpi"><div class="label">Крупнейший отдел</div><div class="value" style="font-size:15px; font-weight:600">${top[0]}<br><span style="color:var(--muted); font-size:12px; font-weight:400">${top[1]} чел.</span></div></div>
    </div>

    ${noDeptCount ? `<div style="background:#fef3c7; border:1px solid #fde68a; border-radius:8px; padding:12px 16px; font-size:12.5px; margin-bottom:16px; color:#78350f">
      <b>«(не указан)» = ${noDeptCount} сотрудников,</b> у которых в исходной таблице поле <i>Department (eng)</i> пустое. Это не отдельное подразделение, а пробел в данных — часть из них топ-менеджмент, часть — сотрудники дочерних юрлиц (Prime Design, Darlean, Invecon), часть — просто не заполнено. Заполните поле «Отдел» в исходной таблице, чтобы они попали в свои филиалы.
    </div>` : ''}

    <div class="card">
      <div class="card-head"><h3>Численность по подразделениям</h3>
        <button class="more" onclick="openModal('org_depts')">Все →</button></div>
      ${list.map(([d,c]) => {
        const max = list[0][1] || 1;
        return `<div class="bar-row">
          <div class="bar-name" title="${d}">${d}</div>
          <div class="bar-track"><div class="bar-fill" style="width:${c/max*100}%"></div></div>
          <div class="bar-value">${c}</div>
        </div>`;
      }).join('')}
    </div>

    <div class="card" style="margin-top:16px">
      <div class="card-head"><h3>Сотрудники</h3>
        <button class="more" onclick="openModal('org_people')">Полный список →</button></div>
      <input class="search" placeholder="Поиск по имени, должности, руководителю..." id="orgSearch" oninput="orgRenderList(this.value)">
      <div class="modal-table-wrap" style="max-height:500px" id="orgList"></div>
    </div>
  `;
}

// ==== Tree state + navigation ====
function orgTreeChildren() {
  const tree = DATA.org_tree;
  const children = {};
  tree.forEach(n => {
    if (n.parent !== null && n.parent !== undefined) (children[n.parent] = children[n.parent] || []).push(n.id);
  });
  Object.keys(children).forEach(k => children[k].sort((a,b) => (tree[b].total||0) - (tree[a].total||0)));
  return children;
}
function orgAncestors(id) {
  const path = [];
  let cur = id;
  const seen = new Set();
  while (cur !== null && cur !== undefined && !seen.has(cur)) {
    seen.add(cur);
    path.unshift(cur);
    cur = DATA.org_tree[cur].parent;
  }
  return path;
}
function orgRoots(country) {
  const tree = DATA.org_tree;
  const children = orgTreeChildren();
  function subCountries(id, seen) {
    if (seen.has(id)) return new Set(); seen.add(id);
    const s = new Set();
    if (tree[id].country && tree[id].country !== '?') s.add(tree[id].country);
    (children[id]||[]).forEach(c => subCountries(c, seen).forEach(x => s.add(x)));
    return s;
  }
  return tree.filter(n => n.parent === null && n.total > 0)
    .filter(r => subCountries(r.id, new Set()).has(country))
    .sort((a,b) => b.total - a.total);
}

// Avatar SVG: colored circle with initials
function orgAvatar(name, size=56) {
  const parts = (name||'').trim().split(/\s+/);
  const initials = ((parts[0]?.[0]||'') + (parts[1]?.[0]||'')).toUpperCase();
  // Deterministic color from name
  let hash = 0;
  for (const ch of name||'') hash = (hash*31 + ch.charCodeAt(0)) & 0xffffffff;
  const hue = Math.abs(hash) % 360;
  return `<div style="width:${size}px; height:${size}px; border-radius:50%; background:hsl(${hue}, 40%, 88%); color:hsl(${hue}, 40%, 30%); display:flex; align-items:center; justify-content:center; font-weight:600; font-size:${size*0.36}px; flex-shrink:0">${initials||'—'}</div>`;
}

function orgCard(id, opts={}) {
  const n = DATA.org_tree[id];
  const children = orgTreeChildren();
  const kids = children[id] || [];
  const isFocus = opts.focus === true;
  const width = isFocus ? 280 : 220;
  const header = n.phantom
    ? `<div style="background:#fef3c7; color:#78350f; padding:6px 10px; font-size:11px; display:flex; justify-content:space-between; align-items:center; border-radius:8px 8px 0 0"><span>Руководитель вне базы</span><span>${n.total}</span></div>`
    : `<div style="background:#1e293b; color:#fff; padding:6px 12px; font-size:11px; display:flex; justify-content:space-between; align-items:center; border-radius:8px 8px 0 0">
        <span>Прямых: ${kids.length}</span>
        <span>Всего: ${n.total}</span>
      </div>`;
  const clickable = kids.length > 0 && !isFocus;
  return `<div style="border:1px solid var(--border); border-radius:8px; background:#fff; width:${width}px; overflow:hidden; ${clickable?'cursor:pointer':''}; transition: box-shadow .12s, transform .12s"
    ${clickable ? `onclick="setOrgFocus(${id})" onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,.08)'; this.style.transform='translateY(-2px)'" onmouseout="this.style.boxShadow=''; this.style.transform=''"` : ''}>
    ${header}
    <div style="padding:14px 12px 12px; text-align:center">
      <div style="display:flex; justify-content:center; margin-bottom:10px">${orgAvatar(n.name, isFocus ? 68 : 52)}</div>
      <div style="font-weight:600; font-size:${isFocus?14:13}px; line-height:1.3; margin-bottom:4px; ${n.phantom?'color:#a16207':''}">${n.name}</div>
      <div style="color:var(--muted); font-size:11.5px; min-height:14px; line-height:1.3">${n.pos || ''}</div>
    </div>
    ${(n.dept && n.dept !== '(не указан)' && n.dept !== '(вне базы)') ? `
    <div style="background:var(--subtle); padding:8px 12px; font-size:11px; color:var(--muted); border-top:1px solid var(--border); line-height:1.4">
      ${n.dept}
    </div>` : ''}
  </div>`;
}

function renderOrgTree() {
  const tree = DATA.org_tree;
  const country = orgState.country === 'kz' ? 'KZ' : 'UZ';
  const children = orgTreeChildren();

  // Auto-select focus if none, or if focus doesn't include this country
  const roots = orgRoots(country);
  if (orgState.focusId === null || (tree[orgState.focusId] && tree[orgState.focusId].total === 0) || !roots.some(r => orgAncestors(orgState.focusId).some(a => a === r.id) || r.id === orgState.focusId)) {
    orgState.focusId = roots[0]?.id ?? null;
  }
  if (orgState.focusId === null) {
    return '<div class="empty-state">Нет корневых узлов для выбранной страны</div>';
  }

  const focus = tree[orgState.focusId];
  const focusKids = children[orgState.focusId] || [];
  const path = orgAncestors(orgState.focusId);

  // Root selector
  const rootSelector = `
    <div class="filter-group" style="margin-bottom:12px">
      <span class="filter-label">Корневой руководитель</span>
      <select class="filter-select" onchange="setOrgFocus(+this.value)" style="min-width:280px">
        ${roots.map(r => `<option value="${r.id}"${orgState.focusId === r.id || path[0] === r.id ? ' selected':''}>${r.name} (${r.total})</option>`).join('')}
      </select>
    </div>`;

  // Breadcrumb
  const crumb = path.length > 1 ? `
    <div style="display:flex; align-items:center; gap:6px; margin-bottom:16px; font-size:12.5px; flex-wrap:wrap">
      ${path.map((id,i) => i === path.length-1
        ? `<span style="font-weight:600">${tree[id].name}</span>`
        : `<a onclick="setOrgFocus(${id})" style="color:#2563eb; cursor:pointer">${tree[id].name}</a> <span style="color:var(--muted)">›</span>`
      ).join(' ')}
    </div>` : '';

  // Focus card
  const focusHtml = `<div style="display:flex; justify-content:center; margin-bottom:${focusKids.length?32:0}px; position:relative">${orgCard(orgState.focusId, {focus: true})}</div>`;

  // Children row with connection lines drawn via SVG overlay
  let kidsHtml = '';
  if (focusKids.length) {
    // Row of children cards, wrap if too many
    const cardW = 220, gap = 16;
    const maxPerRow = Math.floor((1400 - 80) / (cardW + gap)) || 4;
    const rows = [];
    for (let i=0; i<focusKids.length; i+=maxPerRow) rows.push(focusKids.slice(i, i+maxPerRow));
    kidsHtml = `
      <div style="position:relative; padding-top:24px">
        <!-- vertical trunk from focus down -->
        <div style="position:absolute; left:50%; top:-32px; width:2px; height:32px; background:#d1d5db; transform:translateX(-1px)"></div>
        ${rows.map((row, ri) => `
          <div style="display:flex; gap:${gap}px; justify-content:center; flex-wrap:nowrap; margin-bottom:${ri < rows.length-1 ? 20 : 0}px; position:relative">
            ${row.length > 1 ? `<div style="position:absolute; left:0; right:0; top:-12px; height:2px; background:#d1d5db; margin: 0 ${cardW/2}px"></div>` : ''}
            ${row.map(id => `
              <div style="display:flex; flex-direction:column; align-items:center; position:relative">
                <div style="width:2px; height:12px; background:#d1d5db; margin-bottom:0"></div>
                ${orgCard(id)}
              </div>
            `).join('')}
          </div>
        `).join('')}
      </div>`;
  }

  const resolved = tree.filter(n => !n.phantom && n.parent !== null).length;

  return `
    <div style="background:var(--subtle); border-radius:8px; padding:10px 14px; font-size:12px; margin-bottom:16px; color:var(--muted)">
      <b style="color:var(--text)">Как читать:</b> клик по карточке подчинённого — он становится фокусом, ниже раскрываются его подчинённые. Хлебные крошки сверху ведут обратно.
      Иерархия строится по полю <b>PPPD</b> · разрешено ${resolved} из 607 связей.
    </div>
    ${rootSelector}
    ${crumb}
    <div style="overflow-x:auto; padding:8px 8px 24px">
      ${focusHtml}
      ${kidsHtml}
    </div>
  `;
}

function setOrgFocus(id) {
  orgState.focusId = id;
  rerender();
}
function setOrgView(v) {
  orgState.view = v;
  if (v === 'tree' && orgState.focusId === null) {
    const roots = orgRoots(orgState.country === 'kz' ? 'KZ' : 'UZ');
    orgState.focusId = roots[0]?.id ?? null;
  }
  rerender();
}

// ==== Placeholder pages for sections in development ====
function placeholderPage(title, subtitle, description, planned) {
  return `
    <div class="page-head">
      <h1>${title}</h1>
      <div class="sub">${subtitle}</div>
    </div>
    <div style="max-width:720px; margin: 40px auto; text-align:center">
      <div style="display:inline-flex; align-items:center; gap:8px; padding: 4px 12px; background: #fef3c7; color:#92400e; border-radius: 999px; font-size:11px; text-transform:uppercase; letter-spacing:.06em; font-weight:600; margin-bottom:24px">
        Раздел в разработке
      </div>
      <h2 style="margin: 0 0 12px; font-size: 20px; font-weight: 600; letter-spacing: -0.01em">${description}</h2>
      <div style="color: var(--muted); font-size: 14px; line-height: 1.6; margin-bottom: 40px">
        Данные для этого раздела ещё не переданы. Как только источники будут подключены, здесь появится полноценная страница с KPI, графиками, фильтрами и деталями.
      </div>
      <div style="text-align:left; background: var(--subtle); border-radius: 10px; padding: 20px 24px">
        <div style="color: var(--muted); font-size: 11px; text-transform:uppercase; letter-spacing:.06em; margin-bottom: 10px; font-weight:600">Планируется</div>
        ${planned.map(p => `<div style="padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 13.5px; display:flex; gap:10px">
          <span style="color:var(--muted); flex-shrink:0">·</span>
          <span>${p}</span>
        </div>`).join('')}
      </div>
    </div>
  `;
}

pages.profile = () => {
  const u = ME;
  const last = u.last_login_at ? new Date(u.last_login_at).toLocaleString('ru-RU') : '—';
  const created = u.created_at ? new Date(u.created_at).toLocaleString('ru-RU') : '—';
  return `
    <div class="page-head"><h1>Профиль</h1><div class="sub">Ваши данные и смена пароля</div></div>
    <div style="max-width:560px">
      <div class="card">
        <div class="card-head"><h3>Учётная запись</h3></div>
        <table>
          <tbody>
            <tr><td>Имя</td><td>${esc(u.name)}</td></tr>
            <tr><td>Email</td><td>${esc(u.email)}</td></tr>
            <tr><td>Роль</td><td><span class="role-badge role-${esc(u.role)}">${esc(ROLES[u.role].label)}</span></td></tr>
            <tr><td>Создан</td><td>${created}</td></tr>
            <tr><td>Последний вход</td><td>${last}</td></tr>
          </tbody>
        </table>
      </div>
      <div class="card" style="margin-top:16px">
        <div class="card-head"><h3>Сменить пароль</h3></div>
        <div class="login-field"><label>Текущий пароль</label><input type="password" id="pwCur"></div>
        <div class="login-field"><label>Новый пароль</label><input type="password" id="pwNew" placeholder="Минимум 12 символов, 3 из 4 групп"></div>
        <div class="login-field"><label>Подтверждение</label><input type="password" id="pwConfirm"></div>
        <button class="btn-primary" onclick="changePasswordSubmit()">Сохранить</button>
        <div id="pwMsg" style="margin-top:10px; font-size:12px"></div>
      </div>
    </div>
  `;
};

async function changePasswordSubmit() {
  const cur = document.getElementById('pwCur').value;
  const nw = document.getElementById('pwNew').value;
  const cf = document.getElementById('pwConfirm').value;
  const el = document.getElementById('pwMsg');
  el.textContent = ''; el.style.color = '';
  if (nw !== cf) { el.textContent = 'Пароли не совпадают'; el.style.color = 'var(--neg)'; return; }
  try {
    await api('/api/auth/change-password', { method:'POST', body: JSON.stringify({current_password: cur, new_password: nw}) });
    el.textContent = 'Пароль изменён. Войдите заново.'; el.style.color = 'var(--pos)';
    setTimeout(async () => { await logout(); }, 1500);
  } catch(e) { el.textContent = e.message; el.style.color = 'var(--neg)'; }
}

pages.users = async () => {
  const list = await api('/api/users');
  return `
    <div class="page-head"><h1>Пользователи</h1><div class="sub">Управление доступом к системе</div></div>
    <div class="card">
      <div class="card-head"><h3>Все пользователи · ${list.length}</h3>
        <button class="btn-primary" onclick="openModal('user_create')">+ Добавить</button></div>
      <div class="table-scroll"><table>
        <thead><tr>
          <th>Имя</th><th style="text-align:left">Email</th><th style="text-align:left">Роль</th>
          <th style="text-align:left">Создан</th><th style="text-align:left">Последний вход</th>
          <th style="text-align:left">Статус</th><th></th>
        </tr></thead>
        <tbody>
          ${list.map(u => {
            const last = u.last_login_at ? new Date(u.last_login_at).toLocaleString('ru-RU') : '—';
            const created = u.created_at ? new Date(u.created_at).toLocaleDateString('ru-RU') : '—';
            const canDel = u.id !== ME.id;
            return `<tr>
              <td>${esc(u.name)}</td>
              <td style="text-align:left">${esc(u.email)}</td>
              <td style="text-align:left"><span class="role-badge role-${esc(u.role)}">${esc(ROLES[u.role].label)}</span></td>
              <td style="text-align:left; color:var(--muted)">${created}</td>
              <td style="text-align:left; color:var(--muted)">${last}</td>
              <td style="text-align:left">${u.disabled ? '<span style="color:var(--neg)">Отключён</span>' : '<span style="color:var(--pos)">Активен</span>'}</td>
              <td style="text-align:left; display:flex; gap:6px; flex-wrap:wrap">
                <button class="btn-secondary" onclick="openModal('user_edit', ${u.id})">Изм.</button>
                <button class="btn-secondary" onclick="openModal('user_pw', ${u.id})">Пароль</button>
                ${canDel ? `<button class="btn-danger" onclick="deleteUserFlow(${u.id})">Удалить</button>` : ''}
              </td>
            </tr>`;
          }).join('')}
        </tbody>
      </table></div>
    </div>
  `;
};

async function deleteUserFlow(uid) {
  if (!confirm('Удалить пользователя? Действие необратимо.')) return;
  try { await api('/api/users/' + uid, { method:'DELETE' }); rerender(); }
  catch(e) { alert(e.message); }
}

pages.audit = async () => {
  const rows = await api('/api/audit?limit=200');
  return `
    <div class="page-head"><h1>Журнал событий</h1><div class="sub">Последние 200 событий</div></div>
    <div class="card">
      <div class="table-scroll"><table>
        <thead><tr>
          <th style="text-align:left">Время</th>
          <th style="text-align:left">Событие</th>
          <th style="text-align:left">Кто</th>
          <th style="text-align:left">Над кем</th>
          <th style="text-align:left">IP</th>
          <th style="text-align:left">Детали</th>
        </tr></thead>
        <tbody>
          ${rows.map(r => `<tr>
            <td style="text-align:left; font-size:11.5px; color:var(--muted); white-space:nowrap">${new Date(r.ts).toLocaleString('ru-RU')}</td>
            <td style="text-align:left"><code style="font-size:11px">${r.event}</code></td>
            <td style="text-align:left">${r.actor_email || '—'}</td>
            <td style="text-align:left">${r.target_email || '—'}</td>
            <td style="text-align:left; font-size:11px; color:var(--muted)">${r.ip || '—'}</td>
            <td style="text-align:left; font-size:11px; color:var(--muted); max-width:400px; white-space:normal; word-break:break-word">${r.meta || ''}</td>
          </tr>`).join('')}
        </tbody>
      </table></div>
    </div>
  `;
};

pages.sales_b2b = () => placeholderPage(
  'Продажи · B2B',
  'Работа с корпоративными клиентами',
  'Здесь будет обзор B2B-продаж',
  [
    'Воронка сделок по стадиям · конверсия из этапа в этап',
    'Средний чек, цикл сделки, LTV по клиенту',
    'Активные и просроченные сделки, следующие шаги',
    'Топ-клиенты по выручке, план-факт по менеджерам',
    'Разрез по отраслям / регионам / продуктам',
  ]
);

pages.sales_b2g = () => placeholderPage(
  'Продажи · B2G',
  'Работа с государственными заказчиками',
  'Здесь будет обзор B2G-продаж',
  [
    'Активные тендеры, статусы, суммы, дедлайны',
    'История подач · выигранные / проигранные лоты',
    'Разрез по заказчикам (акиматы, министерства, госкомпании)',
    'Календарь ключевых закупок',
    'Портфель контрактов и график исполнения',
  ]
);

pages.processes_darlean = () => placeholderPage(
  'Процессы · Darlean',
  'Бизнес-процессы из внутренней системы Darlean',
  'Здесь будет обзор процессов из Darlean',
  [
    'Активные процессы по статусам · висящие задачи',
    'Среднее время прохождения этапов',
    'Узкие места · где процессы буксуют',
    'Загрузка исполнителей и SLA',
    'Ссылки на процессы прямо в Darlean',
  ]
);

function setOrgCountry(c) {
  orgState.country = c;
  orgState.dept = '__all__';
  rerender();
}
function setOrgDept(d) {
  orgState.dept = d;
  rerender();
}
function orgRenderList(q) {
  const arr = orgState.country === 'kz' ? DATA.org_kz : DATA.org_uz;
  const filt = orgState.dept === '__all__' ? arr : arr.filter(e => e.dept === orgState.dept);
  const ql = (q||'').toLowerCase().trim();
  const list = ql ? filt.filter(e =>
    (e.name||'').toLowerCase().includes(ql) ||
    (e.position||'').toLowerCase().includes(ql) ||
    (e.manager||'').toLowerCase().includes(ql) ||
    (e.dept||'').toLowerCase().includes(ql)
  ) : filt;
  let html = '<table><thead><tr><th>Имя</th><th style="text-align:left">Отдел</th><th style="text-align:left">Руководитель</th></tr></thead><tbody>';
  list.slice(0, 200).forEach(e => {
    html += '<tr><td>' + e.name + '</td>' +
      '<td style="text-align:left">' + e.dept + '</td>' +
      '<td style="text-align:left">' + (e.manager || '—') + '</td></tr>';
  });
  if (list.length > 200) html += '<tr><td colspan="3" style="color:var(--muted); text-align:center">…ещё ' + (list.length-200) + '. Откройте «Полный список»</td></tr>';
  html += '</tbody></table>';
  const el = document.getElementById('orgList');
  if (el) el.innerHTML = html;
}

// ==== Modals ====
async function openModal(id, arg) {
  const box = document.getElementById('modalBox');
  document.getElementById('modalMask').classList.add('open');
  box.innerHTML = '<div class="empty-state">Загрузка…</div>';
  try {
    const fn = modals[id];
    const res = fn ? fn(arg) : '<h3>Данные</h3><div class="empty-state">Раздел в разработке</div>';
    const html = res && typeof res.then === 'function' ? await res : res;
    if (html !== null && html !== undefined) box.innerHTML = html;
  } catch(e) {
    box.innerHTML = '<div class="empty-state" style="color:var(--neg)">Ошибка: ' + (e.message||e) + '</div>';
  }
}
function closeModal() { document.getElementById('modalMask').classList.remove('open'); }
document.getElementById('modalMask').onclick = (e) => { if (e.target.id === 'modalMask') closeModal(); };
const closeBtn = '<button class="close" onclick="closeModal()">&times;</button>';

const modals = {
  overview_monthly: () => {
    const at = filteredAtoms();
    const rev = monthlySeries(at, 'Доходы');
    const expD = monthlySeries(at, 'Расходы');
    const expK = monthlySeries(at, 'Расходы КЦ');
    const eb = monthlySeries(at, 'EBITDA');
    const labels = activeMonthLabels();
    return `${closeBtn}<h3>Помесячная P&L</h3><div class="msub">В рамках текущего фильтра · тыс. ₸</div>
      <div class="modal-table-wrap"><table><thead><tr><th>Месяц</th><th>Выручка</th><th>Расходы деп.</th><th>Расходы КЦ</th><th>EBITDA</th><th>Маржа</th></tr></thead><tbody>
        ${labels.map((m,i) => {
          const r = rev[i], e = (expD[i]||0)+(expK[i]||0), ebv = eb[i];
          const mar = r ? ebv/r*100 : 0;
          return `<tr><td>${m}</td>
            <td class="num">${fmt(r,0)}</td>
            <td class="num neg">${fmt(expD[i]||0,0)}</td>
            <td class="num neg">${fmt(expK[i]||0,0)}</td>
            <td class="num ${ebv>=0?'pos':'neg'}">${fmt(ebv,0)}</td>
            <td class="num">${fmtPct(mar)}</td></tr>`;
        }).join('')}
        <tr style="font-weight:600; background:var(--subtle)"><td>Итого</td>
          <td class="num">${fmt(rev.reduce((s,x)=>s+x,0),0)}</td>
          <td class="num neg">${fmt(expD.reduce((s,x)=>s+x,0),0)}</td>
          <td class="num neg">${fmt(expK.reduce((s,x)=>s+x,0),0)}</td>
          <td class="num pos">${fmt(eb.reduce((s,x)=>s+x,0),0)}</td>
          <td class="num">${fmtPct(eb.reduce((s,x)=>s+x,0)/Math.max(1,rev.reduce((s,x)=>s+x,0))*100)}</td></tr>
      </tbody></table></div>`;
  },
  overview_depts: () => {
    const at = filteredAtoms();
    const rows = DATA.filials.filter(f => filterState.filials.has(f)).map(f => {
      const sub = at.filter(a => a[2]===f);
      return {
        f,
        rev: sub.filter(a=>a[1]==='Доходы').reduce((s,a)=>s+a[5],0),
        exp: sub.filter(a=>a[1]==='Расходы'||a[1]==='Расходы КЦ').reduce((s,a)=>s+a[5],0),
        eb: sub.filter(a=>a[1]==='EBITDA').reduce((s,a)=>s+a[5],0),
      };
    }).sort((a,b) => b.rev-a.rev);
    return `${closeBtn}<h3>Филиалы · сводка</h3><div class="msub">В рамках фильтра, тыс. ₸</div>
      <div class="modal-table-wrap"><table><thead><tr><th>Филиал</th><th>Выручка</th><th>Расходы</th><th>EBITDA</th><th>Маржа</th></tr></thead><tbody>
        ${rows.map(d => {
          const m = d.rev ? d.eb/d.rev*100 : 0;
          return `<tr><td>${d.f}</td>
            <td class="num">${fmt(d.rev,0)}</td>
            <td class="num neg">${fmt(d.exp,0)}</td>
            <td class="num ${d.eb>=0?'pos':'neg'}">${fmt(d.eb,0)}</td>
            <td class="num ${m>=0?'':'neg'}">${fmtPct(m)}</td></tr>`;
        }).join('')}
      </tbody></table></div>`;
  },
  overview_multiyear: () => {
    const ys = ['2020','2021','2022','2023','2024','2025','2026'];
    const rows = ['Доход от основной деятельности','Переменные производственные расходы','Маржинальная прибыль','Постоянные производственные расходы','Валовая прибыль','Расходы по реализации','Административные расходы','Прочие доходы','Прочие расходы'];
    return `${closeBtn}<h3>БДР 2020–2026 · PL_ES</h3><div class="msub">Тыс. ₸. 2020–2025 — факт, 2026 — прогноз. Не зависит от фильтров.</div>
      <div class="modal-table-wrap"><table><thead><tr><th>Показатель</th>${ys.map(y => `<th>${y}</th>`).join('')}</tr></thead><tbody>
        ${rows.map(rn => `<tr><td>${rn}</td>${ys.map(y => `<td class="num">${fmt(DATA.pl_yearly[rn][y]||0,0)}</td>`).join('')}</tr>`).join('')}
        <tr style="font-weight:600; background:var(--subtle)"><td>EBITDA (расчёт)</td>${ys.map(y => `<td class="num pos">${fmt(DATA.pl_ebitda[y]||0,0)}</td>`).join('')}</tr>
      </tbody></table></div>`;
  },
  overview_services: () => {
    const at = filteredAtoms();
    const items = [...sumBy(at.filter(a => a[1]==='Доходы' && a[5]>0), a=>a[4]).entries()].filter(([k,v])=>v>0).sort((a,b) => b[1]-a[1]);
    const total = items.reduce((s,x)=>s+x[1],0);
    return `${closeBtn}<h3>Все виды услуг · выручка</h3><div class="msub">В рамках фильтра, тыс. ₸</div>
      <div class="modal-table-wrap"><table><thead><tr><th>Услуга</th><th>Сумма</th><th>Доля</th></tr></thead><tbody>
        ${items.map(([k,v]) => `<tr><td>${k || '(без указания)'}</td><td class="num">${fmt(v,0)}</td><td class="num" style="color:var(--muted)">${total?(v/total*100).toFixed(2):0}%</td></tr>`).join('')}
      </tbody></table></div>`;
  },
  rev_monthly: () => modals.overview_monthly(),
  rev_yearly: () => modals.overview_multiyear(),
  rev_depts: () => modals.overview_depts(),
  rev_services: () => modals.overview_services(),
  exp_vid: () => {
    const at = filteredAtoms();
    const expAtoms = at.filter(a => a[1]==='Расходы' || a[1]==='Расходы КЦ');
    const vids = [...new Set(expAtoms.map(a=>a[3]))].sort();
    const mm = activeMonths();
    const ml = activeMonthLabels();
    return `${closeBtn}<h3>Расходы по типам и месяцам</h3><div class="msub">В рамках фильтра, тыс. ₸</div>
      <div class="modal-table-wrap"><table><thead><tr><th>Тип</th>${ml.map(m => `<th>${m}</th>`).join('')}<th>Итого</th></tr></thead><tbody>
        ${vids.map(vid => {
          const monthly = mm.map(m => expAtoms.filter(a => a[3]===vid && a[0]===m).reduce((s,a)=>s+a[5],0));
          return `<tr><td>${vid}</td>${monthly.map(v => `<td class="num neg">${fmt(v,0)}</td>`).join('')}<td class="num neg" style="font-weight:600">${fmt(monthly.reduce((s,x)=>s+x,0),0)}</td></tr>`;
        }).join('')}
      </tbody></table></div>`;
  },
  exp_monthly: () => modals.overview_monthly(),
  exp_statya: () => {
    const at = filteredAtoms();
    const expAtoms = at.filter(a => a[1]==='Расходы' || a[1]==='Расходы КЦ');
    const items = [...sumBy(expAtoms, a=>a[4]).entries()].filter(([k,v])=>v<0).sort((a,b) => a[1]-b[1]);
    const total = items.reduce((s,x)=>s+x[1],0);
    return `${closeBtn}<h3>Все статьи расходов</h3><div class="msub">В рамках фильтра, тыс. ₸</div>
      <div class="modal-table-wrap"><table><thead><tr><th>Статья</th><th>Сумма</th><th>Доля</th></tr></thead><tbody>
        ${items.map(([k,v]) => `<tr><td>${k || '(без указания)'}</td><td class="num neg">${fmt(v,0)}</td><td class="num" style="color:var(--muted)">${total?(v/total*100).toFixed(2):0}%</td></tr>`).join('')}
      </tbody></table></div>`;
  },
  exp_depts: () => modals.overview_depts(),
  ebitda_monthly: () => modals.overview_monthly(),
  ebitda_depts: () => modals.overview_depts(),
  dz_org: () => {
    const items = dzFilteredItems();
    const byOrg = {};
    items.forEach(x => { byOrg[x.org] = (byOrg[x.org]||0) + x.total; });
    const arr = Object.entries(byOrg).sort((a,b) => b[1]-a[1]);
    const total = arr.reduce((s,x)=>s+x[1],0);
    return `${closeBtn}<h3>ДЗ по юрлицам</h3><div class="msub">В рамках фильтра, ₸</div>
      <div class="modal-table-wrap"><table><thead><tr><th>Юрлицо</th><th>Сумма</th><th>Доля</th></tr></thead><tbody>
        ${arr.map(([k,v]) => `<tr><td>${k}</td><td class="num">${fmt(v,0)}</td><td class="num" style="color:var(--muted)">${total?(v/total*100).toFixed(2):0}%</td></tr>`).join('')}
      </tbody></table></div>`;
  },
  dz_status: () => {
    const items = dzFilteredItems();
    const byStatus = {};
    items.forEach(x => { byStatus[x.status || '(без статуса)'] = (byStatus[x.status || '(без статуса)']||0) + x.total; });
    const arr = Object.entries(byStatus).sort((a,b) => b[1]-a[1]);
    const total = arr.reduce((s,x)=>s+x[1],0);
    return `${closeBtn}<h3>ДЗ по статусу работы</h3><div class="msub">В рамках фильтра, ₸</div>
      <div class="modal-table-wrap"><table><thead><tr><th>Статус</th><th>Позиций</th><th>Сумма</th><th>Доля</th></tr></thead><tbody>
        ${arr.map(([k,v]) => {
          const cnt = items.filter(x => (x.status || '(без статуса)') === k).length;
          return `<tr><td>${k}</td><td class="num">${cnt}</td><td class="num">${fmt(v,0)}</td><td class="num" style="color:var(--muted)">${total?(v/total*100).toFixed(2):0}%</td></tr>`;
        }).join('')}
      </tbody></table></div>`;
  },
  dz_all: () => {
    const items = dzFilteredItems().sort((a,b) => b.total - a.total);
    return `${closeBtn}<h3>Полный список ДЗ · ${items.length} позиций</h3>
      <div class="msub">В рамках фильтра, ₸. Отсортировано по сумме.</div>
      <input class="search" placeholder="Поиск..." id="mSearch" oninput="filterModalPeople(this.value)">
      <div class="modal-table-wrap"><table id="mTable"><thead><tr>
        <th>Покупатель</th>
        <th style="text-align:left">Юрлицо</th>
        <th style="text-align:left">Дивизион</th>
        <th style="text-align:left">Ответственный</th>
        <th>30–60</th><th>61–90</th><th>91–365</th><th>365+</th><th>Итого</th>
        <th style="text-align:left">Статус</th>
        <th style="text-align:left">Комментарий</th>
      </tr></thead><tbody>
        ${items.map(x => `<tr>
          <td>${x.buyer}</td>
          <td style="text-align:left">${x.org}</td>
          <td style="text-align:left">${x.div}</td>
          <td style="text-align:left">${x.responsible || '—'}</td>
          <td class="num">${x.d_30_60 ? fmt(x.d_30_60,0) : '—'}</td>
          <td class="num">${x.d_61_90 ? fmt(x.d_61_90,0) : '—'}</td>
          <td class="num" style="${x.d_91_365?'color:#b45309':''}">${x.d_91_365 ? fmt(x.d_91_365,0) : '—'}</td>
          <td class="num" style="${x.d_365?'color:#dc2626':''}">${x.d_365 ? fmt(x.d_365,0) : '—'}</td>
          <td class="num" style="font-weight:600">${fmt(x.total,0)}</td>
          <td style="text-align:left; font-size:11.5px">${x.status || '—'}</td>
          <td style="text-align:left; font-size:11.5px; color:var(--muted); max-width:300px; white-space:normal">${x.comment || '—'}</td>
        </tr>`).join('')}
      </tbody></table></div>`;
  },
  org_depts: () => {
    const arr = orgState.country === 'kz' ? DATA.org_kz : DATA.org_uz;
    const filtered = orgState.dept === '__all__' ? arr : arr.filter(e => e.dept === orgState.dept);
    const depts = {};
    filtered.forEach(e => { depts[e.dept] = (depts[e.dept]||0)+1; });
    const list = Object.entries(depts).sort((a,b) => b[1]-a[1]);
    return `${closeBtn}<h3>Подразделения · ${orgState.country==='kz'?'Казахстан':'Узбекистан'}</h3>
      <div class="msub">Действующие сотрудники · ${filtered.length}${orgState.dept!=='__all__'?' · фильтр отдела: '+orgState.dept:''}</div>
      <div class="modal-table-wrap"><table><thead><tr><th>Подразделение</th><th>Сотрудников</th><th>%</th></tr></thead><tbody>
        ${list.map(([d,c]) => `<tr><td>${d}</td><td class="num">${c}</td><td class="num" style="color:var(--muted)">${(c/filtered.length*100).toFixed(1)}%</td></tr>`).join('')}
      </tbody></table></div>`;
  },
  org_people: () => {
    const arr = orgState.country === 'kz' ? DATA.org_kz : DATA.org_uz;
    const filtered = orgState.dept === '__all__' ? arr : arr.filter(e => e.dept === orgState.dept);
    return `${closeBtn}<h3>Полный список · ${orgState.country==='kz'?'Казахстан':'Узбекистан'}</h3>
      <div class="msub">${filtered.length} действующих сотрудников${orgState.dept!=='__all__'?' · '+orgState.dept:''}</div>
      <input class="search" placeholder="Поиск..." id="mSearch" oninput="filterModalPeople(this.value)">
      <div class="modal-table-wrap"><table id="mTable"><thead><tr><th>Имя</th><th style="text-align:left">Отдел</th><th style="text-align:left">Должность</th><th style="text-align:left">Руководитель</th></tr></thead><tbody>
        ${filtered.map(e => `<tr>
          <td>${e.name}</td>
          <td style="text-align:left">${e.dept}</td>
          <td style="text-align:left">${e.position || '—'}</td>
          <td style="text-align:left">${e.manager || '—'}</td>
        </tr>`).join('')}
      </tbody></table></div>`;
  },
};
function filterModalPeople(q) {
  const rows = document.querySelectorAll('#mTable tbody tr');
  const ql = q.toLowerCase().trim();
  rows.forEach(r => { r.style.display = !ql || r.textContent.toLowerCase().includes(ql) ? '' : 'none'; });
}

// ==== Navigation & rerender ====
let currentPage = 'overview';
async function goto(page) {
  currentPage = page;
  document.querySelectorAll('#nav a').forEach(a => a.classList.toggle('active', a.dataset.page === page));
  const root = document.getElementById('root');
  root.innerHTML = '<div class="empty-state">Загрузка…</div>';
  try {
    const fn = pages[page];
    const html = fn ? await Promise.resolve(fn()) : '<div class="empty-state">Раздел не найден</div>';
    root.innerHTML = html;
    if (page === 'org') orgRenderList('');
  } catch(e) {
    root.innerHTML = '<div class="empty-state" style="color:var(--neg)">Ошибка: ' + (e.message||e) + '</div>';
  }
  window.scrollTo(0,0);
}
async function rerender() {
  const scroll = window.scrollY;
  const root = document.getElementById('root');
  try {
    const fn = pages[currentPage];
    const html = fn ? await Promise.resolve(fn()) : '';
    root.innerHTML = html;
    if (currentPage === 'org') orgRenderList('');
  } catch(e) {
    root.innerHTML = '<div class="empty-state" style="color:var(--neg)">Ошибка: ' + (e.message||e) + '</div>';
  }
  window.scrollTo(0, scroll);
}

// ==== User modals (create/edit/pw) ====
Object.assign(modals, {
  user_create: () => `
    ${closeBtn}<h3>Новый пользователь</h3>
    <div class="msub">Email должен быть уникален</div>
    <div class="login-field"><label>Имя</label><input id="uc_name" placeholder="Иванов Иван"></div>
    <div class="login-field"><label>Email</label><input id="uc_email" type="email" placeholder="name@company.kz"></div>
    <div class="login-field"><label>Роль</label>
      <select id="uc_role" class="filter-select" style="max-width:100%">
        <option value="manager">Менеджер · HR + Продажи + Процессы</option>
        <option value="admin">Админ · все дашборды</option>
        <option value="super_admin">Супер-админ · всё + пользователи</option>
      </select>
    </div>
    <div class="login-field"><label>Пароль</label><input id="uc_pw" type="password" placeholder="Минимум 12 символов, 3 из 4 групп"></div>
    <div style="display:flex; gap:8px; margin-top:12px">
      <button class="btn-primary" onclick="createUserSubmit()">Создать</button>
      <button class="btn-secondary" onclick="closeModal()">Отмена</button>
    </div>
    <div id="uc_msg" style="margin-top:10px; font-size:12px; color:var(--neg)"></div>
  `,
  user_edit: (uid) => {
    return api('/api/users').then(list => {
      const u = list.find(x => x.id === uid);
      if (!u) return `${closeBtn}<h3>Не найдено</h3>`;
      const box = document.getElementById('modalBox');
      box.innerHTML = `
        ${closeBtn}<h3>Изменить · ${u.name}</h3>
        <div class="msub">${u.email}</div>
        <div class="login-field"><label>Имя</label><input id="ue_name" value="${u.name.replace(/"/g,'&quot;')}"></div>
        <div class="login-field"><label>Роль</label>
          <select id="ue_role" class="filter-select" style="max-width:100%">
            <option value="manager"${u.role==='manager'?' selected':''}>Менеджер</option>
            <option value="admin"${u.role==='admin'?' selected':''}>Админ</option>
            <option value="super_admin"${u.role==='super_admin'?' selected':''}>Супер-админ</option>
          </select>
        </div>
        <div class="login-field"><label><input type="checkbox" id="ue_dis" ${u.disabled?'checked':''}> Отключить аккаунт</label></div>
        <div style="display:flex; gap:8px; margin-top:12px">
          <button class="btn-primary" onclick="editUserSubmit(${u.id})">Сохранить</button>
          <button class="btn-secondary" onclick="closeModal()">Отмена</button>
        </div>
        <div id="ue_msg" style="margin-top:10px; font-size:12px; color:var(--neg)"></div>
      `;
      return null;
    });
  },
  user_pw: (uid) => `
    ${closeBtn}<h3>Сбросить пароль</h3>
    <div class="msub">Пользователь будет разлогинен на всех устройствах</div>
    <div class="login-field"><label>Новый пароль</label><input id="up_pw" type="password" placeholder="Минимум 12 символов"></div>
    <div style="display:flex; gap:8px; margin-top:12px">
      <button class="btn-primary" onclick="resetPwSubmit(${uid})">Сбросить</button>
      <button class="btn-secondary" onclick="closeModal()">Отмена</button>
    </div>
    <div id="up_msg" style="margin-top:10px; font-size:12px; color:var(--neg)"></div>
  `,
});

async function createUserSubmit() {
  const body = {
    name: document.getElementById('uc_name').value.trim(),
    email: document.getElementById('uc_email').value.trim().toLowerCase(),
    role: document.getElementById('uc_role').value,
    password: document.getElementById('uc_pw').value,
  };
  const msg = document.getElementById('uc_msg');
  msg.textContent = '';
  try { await api('/api/users', {method:'POST', body: JSON.stringify(body)}); closeModal(); rerender(); }
  catch(e) { msg.textContent = e.message; }
}

async function editUserSubmit(uid) {
  const body = {
    name: document.getElementById('ue_name').value.trim(),
    role: document.getElementById('ue_role').value,
    disabled: document.getElementById('ue_dis').checked,
  };
  const msg = document.getElementById('ue_msg');
  msg.textContent = '';
  try { await api('/api/users/' + uid, {method:'PATCH', body: JSON.stringify(body)}); closeModal(); rerender(); }
  catch(e) { msg.textContent = e.message; }
}

async function resetPwSubmit(uid) {
  const pw = document.getElementById('up_pw').value;
  const msg = document.getElementById('up_msg');
  msg.textContent = '';
  try { await api('/api/users/' + uid + '/reset-password', {method:'POST', body: JSON.stringify({new_password: pw})}); closeModal(); }
  catch(e) { msg.textContent = e.message; }
}
</script>
'''

for p in OUT_PATHS:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p,'w',encoding='utf-8') as f:
        f.write(HTML)
    print(f"written {p} ({len(HTML)} chars)")
