#!/usr/bin/env python3
"""v0.7 초상 내려받기: jobs_wait 가 준 결과 줄(…,job_id,…,"url")을 표준입력으로 받아 art/raw7/<key>.png 로 저장하고 확인용 시트를 만든다.
usage: dl_por7.py <sheet.jpg> < jobs_wait_lines.txt      (주소는 저장소에 남기지 않는다 — art/por7_jobs.tsv 는 로컬 전용)"""
import sys, os, re, subprocess
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
plan = {}
for l in open(os.path.join(ROOT, 'art/por5_plan.tsv'), encoding='utf8'):
    if l.strip(): p = l.rstrip('\n').split('\t'); plan[int(p[0])] = (p[1], p[2])
sub = {}
for l in open(os.path.join(ROOT, 'art/por7_submit.tsv'), encoding='utf8'):
    if l.strip() and not l.startswith('#'): a = l.split(); sub[a[1]] = int(a[0])
os.makedirs(os.path.join(ROOT, 'art/raw7'), exist_ok=True)
got = []
log = open(os.path.join(ROOT, 'art/por7_jobs.tsv'), 'a', encoding='utf8')
def base():
    b = os.environ.get('HF_BASE')
    if b: return b
    for fn in ('art/por7_jobs.tsv', 'art/por5_jobs.tsv', 'art/por3_jobs.tsv'):          # 로컬 전용 기록에서 주소 앞부분을 얻는다
        p = os.path.join(ROOT, fn)
        if os.path.exists(p):
            m = re.search(r'(https://\S+?)/hf_\d{8}_', open(p, encoding='utf8').read())
            if m: return m.group(1)
    raise SystemExit('HF_BASE 가 필요합니다')
def probe(job, hms, span=10):
    import datetime
    t0 = datetime.datetime.strptime(os.environ.get('DATE', '20261119') + hms, '%Y%m%d%H%M%S')
    for d in sorted(range(-span, span + 1), key=abs):
        t = t0 + datetime.timedelta(seconds=d)
        url = '%s/hf_%s_%s.png' % (base(), t.strftime('%Y%m%d_%H%M%S'), job)
        r = subprocess.run(['curl', '-sS', '-I', '-o', '/dev/null', '-w', '%{http_code}', url], capture_output=True, text=True)
        if r.stdout.strip() == '200': return url
    return None
lines = []
rev = {v: k for k, v in sub.items()}
for l in sys.stdin:
    if l.startswith('~'):                       # ~HHMMSS idx idx …  : 그 시각 앞뒤로 찾아본다
        a = l[1:].split()
        for idx in a[1:]:
            job = rev[int(idx)]; url = probe(job, a[0])
            if url: lines.append('%s,completed,"%s"' % (job, url))
            else: print('NOT FOUND', plan[int(idx)])
    else: lines.append(l)
for l in lines:
    m = re.search(r'([0-9a-f]{8}-[0-9a-f-]{27}),(\w+),.*?"(https://[^"]+)"', l)
    if not m:
        m2 = re.search(r'([0-9a-f]{8}-[0-9a-f-]{27}),(\w+)', l)
        if m2 and m2.group(2) != 'completed' and m2.group(1) in sub: print('NOT DONE', plan[sub[m2.group(1)]], m2.group(2))
        continue
    job, st, url = m.group(1), m.group(2), m.group(3)
    if job not in sub: print('unknown job', job); continue
    key, name = plan[sub[job]]
    out = os.path.join(ROOT, 'art/raw7', key + '.png')
    r = subprocess.run(['curl', '-sS', '-o', out, '-w', '%{http_code}', url], capture_output=True, text=True)
    ok = r.stdout.strip() == '200'
    if ok:
        try: im = Image.open(out); im.load(); got.append((key, name, im.size))
        except Exception as e: ok = False
    log.write('%d\t%s\t%s\t%s\n' % (sub[job], key, job, url))
    if not ok: print('FAILED', key, r.stdout, r.stderr[:100])
print('saved', len(got), [g[0] for g in got], set(g[2] for g in got))
if len(sys.argv) > 1 and got:
    fp = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
    F = ImageFont.truetype(fp, 20)
    tw, th, cols = 252, 336, 6
    rows = (len(got) + cols - 1) // cols
    s = Image.new('RGB', (cols * (tw + 6) + 6, rows * (th + 30) + 6), (40, 40, 40)); d = ImageDraw.Draw(s)
    for i, (key, name, sz) in enumerate(got):
        x, y = 6 + (i % cols) * (tw + 6), 6 + (i // cols) * (th + 30)
        s.paste(Image.open(os.path.join(ROOT, 'art/raw7', key + '.png')).convert('RGB').resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x + 4, y + th + 2), name, fill=(255, 255, 255), font=F)
    s.save(sys.argv[1], quality=85); print('sheet', s.size)
