#!/usr/bin/env python3
"""
ES One · автообновление данных.
Каждый запуск: заходит в папки Google Drive, находит самые свежие файлы, скачивает,
пересобирает JSON и dashboard.html. Работает пока папки открыты «по ссылке».

Использование:  python3 refresh_data.py
Для планировщика: добавьте в cron / launchd / GitHub Actions чтобы запускался раз в день.
"""
import csv, json, re, urllib.request, os, sys, unicodedata, collections
from html.parser import HTMLParser

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Известные файлы (постоянные) и папки (для еженедельных срезов)
FILES = {
    'ostatok.csv':  '1ONOjZmkIjAipeBQaDOTavmox1MP263noVaryD12Fv6I',
    'org_kz.csv':   '1IC4FAf6pmTfb3idEZsW48pIng9lpa58nC6y7k0hfkRc',
    'org_uz.csv':   '1wHp14fo6rPr9Y0F34-VbhbTECqU2S_OixHxjgm5Me_4',
    'pl_es.csv':    '132wMV__e1X4J_vnbRvGvIAqd1lL2XUNbxxqMlB4XEiU',
    'pbi.csv':      '1rw8MSKbr-XWn9Ganq7Xc7fmn7_0RmmhNHatwemjeb6k',
}
FOLDERS_LATEST = {
    'dz_latest.csv': '1Tl3muILKxEe9wEbZpMiRrggl6XVRVJER',  # ДЗ_комментарии_YYYY-MM-DD
}

def fetch_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=60).read()

def download_sheet(sheet_id, out_path):
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
    data = fetch_url(url)
    with open(out_path, 'wb') as f: f.write(data)
    print(f'  {out_path} · {len(data)} bytes')

class FolderParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.entries = []  # (name, href)
        self._in_a = False
        self._current = {}
        self._buf = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            a = dict(attrs)
            if 'href' in a and '/spreadsheets/d/' in a['href']:
                self._in_a = True
                self._current = {'href': a['href']}
                self._buf = []
    def handle_data(self, data):
        if self._in_a: self._buf.append(data)
    def handle_endtag(self, tag):
        if tag == 'a' and self._in_a:
            name = ''.join(self._buf).strip()
            if name: self._current['name'] = name; self.entries.append(self._current)
            self._in_a = False

def find_latest_in_folder(folder_id, name_pattern=r'(\d{4}-\d{2}-\d{2})'):
    """Возвращает (file_id, name) самого свежего файла по дате в имени."""
    url = f'https://drive.google.com/embeddedfolderview?id={folder_id}#list'
    html = fetch_url(url).decode('utf-8', errors='ignore')
    p = FolderParser(); p.feed(html)
    # Прогоняем через regex на дату в имени, отбрасывая архивные
    candidates = []
    for e in p.entries:
        name = e['name']
        if 'архив' in name.lower(): continue
        m = re.search(name_pattern, name)
        if not m: continue
        date_str = m.group(1)
        m2 = re.search(r'/d/([a-zA-Z0-9_-]+)', e['href'])
        if not m2: continue
        candidates.append((date_str, m2.group(1), name))
    if not candidates:
        raise RuntimeError(f'Не нашли файлов с датой в папке {folder_id}')
    candidates.sort(reverse=True)  # yyyy-mm-dd сортируется лексикографически
    return candidates[0][1], candidates[0][2]

print('== Скачивание постоянных файлов ==')
for name, sid in FILES.items():
    download_sheet(sid, os.path.join(DATA_DIR, name))

print('== Поиск самых свежих файлов в папках ==')
for out_name, fld in FOLDERS_LATEST.items():
    sid, orig_name = find_latest_in_folder(fld)
    print(f'  latest in folder {fld}: {orig_name}')
    download_sheet(sid, os.path.join(DATA_DIR, out_name))
    # Save latest source name for JSON metadata
    with open(os.path.join(DATA_DIR, out_name + '.name.txt'), 'w', encoding='utf-8') as f:
        f.write(orig_name)

print('== Сборка dashboard_data.json ==')
os.chdir(DATA_DIR)

# ---- Ostatok ----
with open('ostatok.csv', encoding='utf-8') as f: rows = list(csv.reader(f))
ostatok = {}
for row in rows[1:]:
    if len(row) >= 2 and row[0].strip():
        raw = row[1].replace('\xa0','').replace(' ','').replace(',','.')
        try: ostatok[row[0].strip()] = float(raw)
        except: pass

# ---- PL_ES yearly ----
with open('pl_es.csv', encoding='utf-8') as f: r = list(csv.reader(f))
years = {'2020':1,'2021':2,'2022':17,'2023':31,'2024':47,'2025':62,'2026':77}
metrics = {11:'Доход от основной деятельности',27:'Переменные производственные расходы',66:'Маржинальная прибыль',94:'Постоянные производственные расходы',122:'Валовая прибыль',149:'Расходы по реализации',163:'Административные расходы',177:'Прочие доходы',191:'Прочие расходы'}
def pnum(v):
    if not v: return 0
    s = str(v).replace('\xa0','').replace(' ','').replace(',','.').strip()
    if not s or s == '-': return 0
    try: return float(s)
    except: return 0
pl_yearly = {name: {y: pnum(r[rn][c]) if c < len(r[rn]) else 0 for y,c in years.items()} for rn,name in metrics.items()}
pl_ebitda = {y: pl_yearly['Валовая прибыль'][y] - pl_yearly['Расходы по реализации'][y] - pl_yearly['Административные расходы'][y] + pl_yearly['Прочие доходы'][y] - pl_yearly['Прочие расходы'][y] for y in years}

# ---- PBI atoms ----
atoms = collections.defaultdict(float)
filials = set()
with open('pbi.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        try: v = float(row['sum_k'].replace(' ','').replace(',','.'))
        except: continue
        try: m = int(row['m'])
        except: continue
        key = (m, row['Группа'], row['fin_file'], row['Вид расходов'], row['Статьи доходов и затрат'])
        atoms[key] += v
        filials.add(row['fin_file'])
atom_list = [[m,g,ff,vid,st,round(v,2)] for (m,g,ff,vid,st),v in atoms.items() if abs(v) >= 0.01]

# ---- Org: load + resolve manager tree with strong matcher ----
CYR_TO_LAT = {
    'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z','и':'i',
    'й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t',
    'у':'u','ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh','щ':'sh','ъ':'','ы':'y','ь':'',
    'э':'e','ю':'yu','я':'ya','ә':'a','ғ':'g','қ':'k','ң':'n','ө':'o','ұ':'u','ү':'u','һ':'h','і':'i',
}
LAT_TO_CYR = {
    'kh':'х','yo':'ё','zh':'ж','ch':'ч','sh':'ш','yu':'ю','ya':'я','ts':'ц',
    'a':'а','b':'б','v':'в','g':'г','d':'д','e':'е','z':'з','i':'и',
    'y':'й','k':'к','l':'л','m':'м','n':'н','o':'о','p':'п','r':'р','s':'с','t':'т',
    'u':'у','f':'ф','h':'х','x':'х','w':'в','c':'к','q':'к','j':'ж',
}
def strip_double(s):
    # collapse doubles: "kassimov" → "kasimov", "тобышшша" — normalize
    return re.sub(r'(.)\1+', r'\1', s)
def norm_key(s):
    s = (s or '').strip().lower()
    s = ''.join(CYR_TO_LAT.get(c, c) for c in s)
    s = re.sub(r'[^\w\s]',' ', s)
    s = re.sub(r'\s+',' ', s).strip()
    return strip_double(s)
def tokens(s):
    return [t for t in norm_key(s).split() if len(t) > 1]

# Manual aliases (mapping raw manager string in PPPD → normalized full name we look up)
ALIASES = {
    'b bauyrzhan': 'berdinov bauyrzhan',   # shortened → full
    'абзал': None,   # too ambiguous — leave for now
}
# Try alias in both token orders
def alias_lookup(target, by_full, by_sorted, self_idx):
    if not target: return None
    if target in by_full and by_full[target] != self_idx:
        return by_full[target]
    sorted_key = ' '.join(sorted(target.split()))
    if sorted_key in by_sorted and by_sorted[sorted_key] != self_idx:
        return by_sorted[sorted_key]
    return None

def load(path, country):
    with open(path, encoding='utf-8') as f:
        return [{
            'name': (r.get('Employee name (rus/kaz)') or r.get('Employee name (eng)') or '').strip(),
            'name_en': (r.get('Employee name (eng)') or '').strip(),
            'dept': (r.get('Department (eng)') or '').strip() or '(не указан)',
            'pos': (r.get('Position title (rus)') or r.get('Position title (eng)') or '').strip(),
            'manager': (r.get('PPPD') or '').strip(),
            'country': country,
            'email': (r.get('Email') or '').strip().lower(),
        } for r in csv.DictReader(f) if r.get('Status','').strip()=='ACTIVE']

emps_raw = load('org_kz.csv','KZ') + load('org_uz.csv','UZ')

# Dedup: сотрудники встречаются в обеих странах с одинаковым именем — объединяем
seen_key = {}
merged = []
for e in emps_raw:
    key = norm_key(e['name']) + '|' + norm_key(e['name_en'])
    if key in seen_key:
        idx = seen_key[key]
        # merge: prefer non-empty
        for k in ['dept','pos','manager','email']:
            if not merged[idx][k] and e[k]:
                merged[idx][k] = e[k]
        # multi-country
        if e['country'] not in merged[idx].get('countries',[merged[idx]['country']]):
            merged[idx].setdefault('countries', [merged[idx]['country']]).append(e['country'])
    else:
        seen_key[key] = len(merged)
        e['countries'] = [e['country']]
        merged.append(e)
emps = merged
print(f'Employees after dedup: {len(emps)} (from {len(emps_raw)})')

# Build lookup tables
by_full = {}
by_sorted = {}
by_token = collections.defaultdict(list)
for i,e in enumerate(emps):
    for candidate in [e['name'], e['name_en']]:
        if not candidate: continue
        ts = tokens(candidate)
        if not ts: continue
        by_full[' '.join(ts)] = i
        by_sorted[' '.join(sorted(ts))] = i
        for t in ts:
            if len(t) >= 3: by_token[t].append(i)

def resolve(mgr_str, self_idx):
    if not mgr_str: return None
    raw_norm = norm_key(mgr_str)
    if raw_norm in ALIASES:
        target = ALIASES[raw_norm]
        if target is None: return None
        hit = alias_lookup(target, by_full, by_sorted, self_idx)
        if hit is not None: return hit
    ts = tokens(mgr_str)
    if not ts: return None
    # exact match on full or sorted tokens
    key = ' '.join(ts)
    if key in by_full and by_full[key] != self_idx: return by_full[key]
    key2 = ' '.join(sorted(ts))
    if key2 in by_sorted and by_sorted[key2] != self_idx: return by_sorted[key2]
    # token-based scoring
    cand = collections.Counter()
    def common_prefix(a, b):
        i = 0
        while i < min(len(a), len(b)) and a[i] == b[i]: i += 1
        return i
    for t in ts:
        if len(t) < 3: continue
        for i in by_token.get(t, []):
            if i != self_idx: cand[i] += 5   # exact token match
        # prefix/suffix and fuzzy (common prefix ≥ 4 chars)
        if len(t) >= 4:
            for tok, ids in by_token.items():
                if tok == t: continue
                cp = common_prefix(t, tok)
                if cp >= min(len(t), len(tok)) - 1 and cp >= 4:
                    # near-typo match ("ordiyanc" ~ "ordiyans"): differ by ≤1 tail char
                    for i in ids:
                        if i != self_idx: cand[i] += 4
                elif tok.startswith(t) or t.startswith(tok):
                    for i in ids:
                        if i != self_idx: cand[i] += 2
                elif cp >= 5:
                    for i in ids:
                        if i != self_idx: cand[i] += 1
    if not cand: return None
    top = cand.most_common(3)
    if len(top) == 1 or top[0][1] > top[1][1]:
        return top[0][0]
    return None

for i,e in enumerate(emps):
    e['parent'] = resolve(e['manager'], i)
    e['resolved'] = e['parent'] is not None

unresolved = collections.Counter()
for e in emps:
    if not e['resolved'] and e['manager']:
        unresolved[e['manager']] += 1

# Add phantom nodes for multi-report unresolved managers
phantom_nodes = []
phantom_ids = {}
for mgr_str, cnt in unresolved.items():
    if cnt >= 2:
        phantom_ids[mgr_str] = len(emps) + len(phantom_nodes)
        phantom_nodes.append({'name': mgr_str, 'dept': '(вне базы)', 'pos':'', 'countries':['?'], 'parent': None, 'phantom': True})
for e in emps:
    if e['parent'] is None and e['manager'] in phantom_ids:
        e['parent'] = phantom_ids[e['manager']]

all_nodes = emps + phantom_nodes
children_map = collections.defaultdict(list)
for i,e in enumerate(all_nodes):
    if e.get('parent') is not None:
        children_map[e['parent']].append(i)

def desc(idx, seen=None):
    if seen is None: seen=set()
    if idx in seen: return 0
    seen.add(idx)
    return len(children_map[idx]) + sum(desc(c, seen) for c in children_map[idx])

resolved_cnt = sum(1 for e in emps if e.get('parent') is not None)
print(f'Resolved: {resolved_cnt} of {len(emps)}')
print(f'Phantom nodes: {len(phantom_nodes)}')
print(f'Top unresolved (top10): {list(unresolved.most_common(10))}')

tree_out = []
for i,e in enumerate(all_nodes):
    is_phantom = i >= len(emps)
    tree_out.append({
        'id': i,
        'name': e['name'],
        'dept': e.get('dept',''),
        'pos': e.get('pos',''),
        'country': ','.join(e.get('countries',[e.get('country','?')])) if not is_phantom else '?',
        'parent': e.get('parent'),
        'directs': len(children_map[i]),
        'total': desc(i),
        'phantom': is_phantom,
    })

# Flat lists for the flat view (only real employees)
org_flat_kz = [{'name': e['name'], 'dept': e['dept'], 'position': e['pos'], 'manager': e['manager']} for e in emps if 'KZ' in e.get('countries',[])]
org_flat_uz = [{'name': e['name'], 'dept': e['dept'], 'position': e['pos'], 'manager': e['manager']} for e in emps if 'UZ' in e.get('countries',[])]

# ---- DZ ----
with open('dz_latest.csv', encoding='utf-8') as f:
    dz_rows = list(csv.DictReader(f))
def pnum2(v):
    if not v: return 0
    s = str(v).replace(',','').replace(' ','').strip()
    try: return float(s)
    except: return 0
dz_items = []
for r in dz_rows:
    if r.get('тип') != '1': continue
    dz_items.append({
        'buyer': r['Покупатель'].strip(),
        'org': r['Организация'].strip(),
        'project': r['Договор.Проект'].strip(),
        'contract': r['Договор'].strip(),
        'responsible': r['Заполняет'].strip(),
        'div': r['Дивизион'].strip() or '(без дивизиона)',
        'd_30_60': pnum2(r.get('От 31 до 60 дней','')),
        'd_61_90': pnum2(r.get('От 61 до 90 дней','')),
        'd_91_365': pnum2(r.get('От 91 до 365 дней','')),
        'd_365': pnum2(r.get('Свыше 365 дней','')),
        'total': pnum2(r.get('ИТОГО 30+','')),
        'status': r['Статус'].strip(),
        'comment': r['Коммент'].strip(),
        'comment_date': r['Дата коммента'].strip(),
    })

# read source name we saved earlier
dz_source_name = 'ДЗ (последний срез)'
name_path = os.path.join(DATA_DIR, 'dz_latest.csv.name.txt')
if os.path.exists(name_path):
    with open(name_path, encoding='utf-8') as f: dz_source_name = f.read().strip()

# ---- Combine ----
data = {
    'meta': {'year_pbi':2026, 'unit':'тыс. ₸'},
    'ostatok': ostatok,
    'pl_yearly': pl_yearly,
    'pl_ebitda': {y: round(v,0) for y,v in pl_ebitda.items()},
    'pbi_years':[2026],
    'pl_years': list(years.keys()),
    'filials': sorted(filials),
    'atoms': atom_list,
    'org_kz': org_flat_kz,
    'org_uz': org_flat_uz,
    'org_tree': tree_out,
    'dz': {
        'source_file': dz_source_name,
        'line_items': dz_items,
    },
}
with open('dashboard_data.json','w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',',':'))
print(f'JSON size: {os.path.getsize("dashboard_data.json")/1024:.0f} KB')

print('== Сборка dashboard.html ==')
os.chdir(BASE)
import subprocess
r = subprocess.run(['python3', 'build_dashboard.py'], capture_output=True, text=True)
print(r.stdout)
if r.returncode != 0:
    print('ERROR:', r.stderr); sys.exit(1)

print('\n✔ Готово. Файлы обновлены.')
print('  data/dashboard_data.json — свежие данные')
print('  dashboard.html — пересобранный HTML')
print('\nЧтобы опубликовать обновление на claude.ai/code/artifact — попросите Claude:')
print('  «Обновлюсь по последним данным» — и он перезальёт по существующей ссылке.')
