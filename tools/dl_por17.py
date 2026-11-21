#!/usr/bin/env python3
"""v0.17 여성 초상 내려받기: jobs_wait 가 준 결과 줄(번호,job_id,상태,…,"url")을 표준입력으로 받아 art/raw17/<key>.png 로 저장하고 확인용 시트를 만든다.
usage: dl_por17.py <sheet.jpg> < jobs_wait_lines.txt      (주소는 저장소에 남기지 않는다 — 로컬 전용 기록은 PRIV_LOG 로 준 파일에만)"""
import sys, os, re, subprocess
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ids = {}; names = {}
for l in open(os.path.join(ROOT, 'art/por17_ids.tsv'), encoding='utf8'):
    if l.strip() and not l.startswith('#'): a = l.split(); ids[a[2]] = a[1]
for l in open(os.path.join(ROOT, 'art/por17_scenes.tsv'), encoding='utf8'):
    if l.strip() and not l.startswith('#'): a = l.rstrip('\n').split('\t'); names[a[1]] = a[2]
RAW = os.path.join(ROOT, 'art/raw17'); os.makedirs(RAW, exist_ok=True)
log = open(os.environ['PRIV_LOG'], 'a', encoding='utf8') if os.environ.get('PRIV_LOG') else None
got = []
def base():
    b = os.environ.get('HF_BASE')
    if b: return b
    m = re.search(r'(https://\S+?)/hf_\d{8}_', open(os.environ['PRIV_LOG'], encoding='utf8').read())      # 로컬 전용 기록에서 주소 앞부분을 얻는다
    return m.group(1)
def probe(job, hms, span=12):
    import datetime
    t0 = datetime.datetime.strptime(os.environ.get('DATE', '20261121') + hms, '%Y%m%d%H%M%S')
    for d in sorted(range(-span, span + 1), key=abs):
        url = '%s/hf_%s_%s.png' % (base(), (t0 + datetime.timedelta(seconds=d)).strftime('%Y%m%d_%H%M%S'), job)
        r = subprocess.run(['curl', '-sS', '-I', '-o', '/dev/null', '-w', '%{http_code}', url], capture_output=True, text=True)
        if r.stdout.strip() == '200': return url
    return None
rev = {v: k for k, v in ids.items()}
lines = []
for l in sys.stdin:
    if l.startswith('~'):                       # ~HHMMSS key key …  : 그 시각 앞뒤로 찾아본다(주소를 다시 적지 않아도 되게)
        a = l[1:].split()
        for k in a[1:]:
            url = probe(rev[k], a[0])
            if url: lines.append('%s,completed,"%s"' % (rev[k], url))
            else: print('NOT FOUND', k)
    else: lines.append(l)
for l in lines:
    m = re.search(r'([0-9a-f]{8}-[0-9a-f-]{27}),(\w+),.*?"(https://[^"]+)"', l)
    if not m:
        m2 = re.search(r'([0-9a-f]{8}-[0-9a-f-]{27}),(\w+)', l)
        if m2 and m2.group(2) != 'completed' and m2.group(1) in ids: print('NOT DONE', ids[m2.group(1)], m2.group(2))
        continue
    job, st, url = m.groups()
    if job not in ids: print('unknown job', job); continue
    key = ids[job]; out = os.path.join(RAW, key + '.png')
    r = subprocess.run(['curl', '-sS', '-o', out, '-w', '%{http_code}', url], capture_output=True, text=True)
    ok = r.stdout.strip() == '200'
    if ok:
        try: im = Image.open(out); im.load(); got.append((key, names.get(key, key), im.size))
        except Exception: ok = False
    if log: log.write('%s\t%s\t%s\n' % (key, job, url))
    if not ok: print('FAILED', key, r.stdout, r.stderr[:100])
print('saved', len(got), [g[0] for g in got], set(g[2] for g in got))
if len(sys.argv) > 1 and got:
    F = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 20)
    tw, th, cols = 300, 400, min(6, len(got))
    rows = (len(got) + cols - 1) // cols
    s = Image.new('RGB', (cols * (tw + 6) + 6, rows * (th + 30) + 6), (40, 40, 40)); d = ImageDraw.Draw(s)
    for i, (key, name, sz) in enumerate(got):
        x, y = 6 + (i % cols) * (tw + 6), 6 + (i // cols) * (th + 30)
        s.paste(Image.open(os.path.join(RAW, key + '.png')).convert('RGB').resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x + 4, y + th + 2), name, fill=(255, 255, 255), font=F)
    s.save(sys.argv[1], quality=85); print('sheet', s.size)
