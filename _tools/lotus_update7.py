#!/usr/bin/env python3
"""Daily preview update for the Lotus Arena materials page (runs on the Mac in /Volumes/LaCieCCM/_LotusHub).
Works only on files the page lists without a preview, so it never walks the whole drive.
  BUDGET=110 python3 update.py run   -> repeat until it prints ALL DONE; writes out_new/data.json and out_new/tb/b<N>.json
"""
import os, sys, re, json, time, base64, unicodedata, collections, importlib.util
B = os.path.dirname(os.path.abspath(__file__)); DRIVE = os.path.dirname(B)
spec = importlib.util.spec_from_file_location('tv3', os.path.join(B, 'thumbs_v3.py')); T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
N = lambda s: unicodedata.normalize('NFC', s).strip()
PREV = {'img', 'psd', 'vid', 'pdf', 'vec'}
SEQ_EXT = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.exr', '.dpx'}
CITY = [('Пхукет', r'пхукет|phuket'), ('Паттайя', r'паттай|pattaya'), ('Нячанг', r'нячанг|начанг|nha ?trang|nhatrang|вьетнам|vietnam'), ('Бали', r'бали|bali'), ('Азия', r'азия|asia')]
ALIAS = {'potap & nastya': 'Потап и Настя', 'ddt': 'ДДТ', 'instasamka': 'Инстасамка', 'limba 2': 'Limba', 'limba': 'Limba',
         'avg': 'Grand opening', 'grand opening': 'Grand opening', 'все наши': 'Новый год 2027', 'общие · пхукет': 'Общие промо Lotus Arena', 'общие · паттайя': 'Общие промо Lotus Arena', 'общие · нячанг': 'Общие промо Lotus Arena', 'guf': 'GUF', 'macan': 'Macan', 'meladze': 'Меладзе', 'nervy': 'NERVY'}
disp = lambda n: ALIAS.get(n.strip().lower(), n.strip())
SYS = lambda n: bool(re.match(r'\s*([_.~]|(claude|clode|клод)\b)', n or '', re.I))
SKIP = re.compile(r'(^|/)(claude|clode|old|logo|фото|photo|пресс|press|графика для монтажа|mt src|video|motion|субтитры|subs|txt|text|слои|исходник)', re.I)

def city_of(*t):
    t = ' '.join(t).lower()
    for c, rx in CITY:
        if re.search(rx, t): return c
    return ''
def ratio(w, h):
    r = w / h
    for n, v in (('4:5', 0.8), ('1:1', 1.0), ('9:16', 0.5625), ('16:9', 16 / 9)):
        if abs(r - v) / v < 0.03: return n
    return None

def resolve(rel):
    """Find the real on-disk path for a folder path + file name (handles NFC/NFD and trailing spaces)."""
    cur = DRIVE
    for part in rel.split('/'):
        p = os.path.join(cur, part)
        if os.path.exists(p): cur = p; continue
        try: names = os.listdir(cur)
        except OSError: return None
        m = next((x for x in names if N(x) == N(part)), None)
        if not m: return None
        cur = os.path.join(cur, m)
    return cur

def main():
    t0 = time.time(); budget = float(os.environ.get('BUDGET', '110'))
    DIN = os.path.join(B, os.environ.get('DATA_IN', 'data_in.json'))
    d = json.load(open(DIN))
    R = {r['id']: r for r in d['roots']}; F = {f[0]: f for f in d['folders']}
    promo_root = next(r['id'] for r in d['roots'] if r['key'] == 'promo')
    tb = d.setdefault('tb', {})
    _p = {}
    def fpath(i):
        if i in _p: return _p[i]
        p = R[i].get('path', R[i]['folder']) if i in R else (None if i not in F else (lambda pp: None if pp is None else pp + '/' + F[i][2])(fpath(F[i][1])))
        _p[i] = p; return p
    have = {x[:-5] for x in os.listdir(T.OUT)}
    fp = os.path.join(B, 'failed_update.txt')
    failed = set(open(fp).read().split()) if os.path.exists(fp) else set()
    # 1) collapse new frame sequences (>=40 numbered images in one folder, still without previews)
    seq_ids = {s[0] for s in d.get('seqs', [])}
    byp = collections.defaultdict(list)
    for r in d['files']:
        if not r[6] and r[3] == 'img' and os.path.splitext(r[2])[1].lower() in SEQ_EXT and re.search(r'\d{2,}$', os.path.splitext(r[2])[0]):
            byp[r[1]].append(r)
    for par, rows in byp.items():
        if len(rows) >= 40 or par in seq_ids:
            ids = {r[0] for r in rows}
            d['files'] = [r for r in d['files'] if r[0] not in ids]
            if par not in seq_ids:
                first = sorted(rows, key=lambda r: r[2])[0]
                d.setdefault('seqs', []).append([par, len(rows), os.path.splitext(first[2])[1].lstrip('.').lower(), '', first[2]])
                seq_ids.add(par)
    # 2) jobs: files, sequence first frames and promo videos without previews
    jobs = []
    def add(target, idx, par, title, kind):
        if kind not in PREV or not fpath(par): return
        rel = fpath(par) + '/' + title
        jobs.append((target, idx, rel, kind))
    for r in d['files']:
        if not r[6]: add(r, 6, r[1], r[2], r[3])
    for s in d.get('seqs', []):
        if not s[3] and len(s) >= 5: add(s, 3, s[0], s[4], 'img')
    for a in d.get('promo', []):
        for v in a['videos']:
            if not v[5] and len(v) >= 8 and v[6]: add(v, 5, v[6], v[7], 'vid')
    done = 0; pending = 0; new_fail = []
    for target, idx, rel, kind in jobs:
        p = resolve(rel)
        if not p: continue          # not on this disk (yet)
        st = os.stat(p); key = T.keyof(N(os.path.relpath(p, DRIVE)), st.st_size, int(st.st_mtime))
        if key in failed: continue
        if key not in have:
            if time.time() - t0 > budget: pending += 1; continue
            ok = False
            try: ok = T.make(p, kind, key)
            except Exception: ok = False
            if not ok: new_fail.append(key); continue
            have.add(key); done += 1
        target[idx] = key
        if target in d['files'] and not target[5]: target[5] = st.st_size
    if new_fail: open(fp, 'w').write('\n'.join(sorted(failed | set(new_fail))))
    if pending:
        json.dump(d, open(DIN, 'w'), ensure_ascii=False, separators=(',', ':'))
        print(f'made {done}, {pending} still to do -> NOT FINISHED, run again'); return
    # 3) posters: new PROMO images with a known format
    def top(fid):
        x = fid; g = 0
        while x in F and g < 60:
            if F[x][1] == promo_root: return x
            x = F[x][1]; g += 1
        return None
    known = {p[0] for a in d.get('promo', []) for p in a['posters']} | set(d.get('hidden_posters', []))
    arts = {a['name']: a for a in d.get('promo', [])}
    folder_of = {}
    for c in [k for k, f in F.items() if f[1] == promo_root]: folder_of.setdefault(disp(F[c][2]), c)
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    for r in d['files']:
        if r[0] in known or r[3] != 'img' or not r[2].lower().endswith(('.jpg', '.jpeg')) or not r[6] or ROOT(r[1], F, R) != promo_root: continue
        dp = fpath(r[1]) or ''
        rest = dp.split('/', 2)[2] if dp.count('/') >= 2 else ''
        if SKIP.search(rest): continue
        p = resolve(dp + '/' + r[2])
        if not p: continue
        try: w, h = Image.open(p).size
        except Exception: continue
        fmt = ratio(w, h)
        af = top(r[1])
        if not fmt or max(w, h) < 1000 or not af or SYS(F[af][2]): continue
        name = disp(F[af][2])
        a = arts.setdefault(name, {'folder': folder_of.get(name, ''), 'name': name, 'videos': [], 'posters': []})
        a['posters'].insert(0, [r[0], r[2], fmt, city_of(dp, r[2]), r[6]])
    d['promo'] = sorted([a for a in arts.values() if (a['videos'] or a['posters']) and not SYS(a['name'])], key=lambda a: a['name'].lower())
    # 4) bundle previews that the page does not have yet
    used = {r[6] for r in d['files'] if r[6]} | {s[3] for s in d.get('seqs', []) if s[3]} | {v[5] for a in d.get('promo', []) for v in a['videos'] if v[5]}
    new = sorted(k for k in used if k not in tb)
    out = os.path.join(B, 'out_new', 'tb'); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        try: os.remove(os.path.join(out, f))
        except OSError: pass
    n = max([int(v) for v in tb.values()] + [-1]) + 1; cur = {}; size = 0; written = []
    def flush():
        nonlocal n, cur, size
        if cur:
            json.dump(cur, open(os.path.join(out, f'b{n}.json'), 'w')); written.append(f'b{n}.json'); n += 1; cur = {}; size = 0
    for k in new:
        wp = os.path.join(T.OUT, k + '.webp')
        for _ in range(15):
            if os.path.exists(wp): break
            time.sleep(1)
        s = base64.b64encode(open(wp, 'rb').read()).decode()
        if size + len(s) > 2_000_000: flush()
        cur[k] = s; size += len(s); tb[k] = n
    flush()
    json.dump(d, open(os.path.join(B, 'out_new', 'data.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print(f'ALL DONE: new previews {len(new)}, bundles: {" ".join(written) or "none"}')

def ROOT(fid, F, R):
    g = 0
    while fid in F and g < 60: fid = F[fid][1]; g += 1
    return fid if fid in R else None

if __name__ == '__main__':
    main()
