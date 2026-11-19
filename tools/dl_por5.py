#!/usr/bin/env python3
"""v0.5 장면 초상(3:4) 내려받기: jobs_wait 결과 줄(index,job_id,status,type,model,"url")을 표준입력으로 받는다.
   art/por5_plan.tsv 의 index → key 로 art/raw3/<key>.png 저장, art/por5_jobs.tsv 에 기록, 대조용 시트 생성."""
import sys, re, os, subprocess, csv
from PIL import Image
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
plan = {}
for ln in open(os.path.join(ROOT, 'art/por5_plan.tsv'), encoding='utf8'):
    p = ln.rstrip('\n').split('\t')
    plan[int(p[0])] = (p[1], p[2], p[3])
jobs_path = os.path.join(ROOT, 'art/por5_jobs.tsv')
done = {}
if os.path.exists(jobs_path):
    for ln in open(jobs_path, encoding='utf8'):
        p = ln.rstrip('\n').split('\t')
        if len(p) >= 3: done[p[0]] = p
got = []
rows = []
txt = sys.stdin.read()
for m in re.finditer(r'^\s*(\d+),([0-9a-f-]{36}),(\w+),\w+,\w+,"?(https?://[^"\s]+)?"?', txt, re.M):
    rows.append((int(m.group(1)), m.group(2), m.group(3), m.group(4)))
for m in re.finditer(r'index:\s*(\d+)\s*\n\s*job_id:\s*([0-9a-f-]{36})\s*\n\s*status:\s*(\w+)(?:\s*\n\s*type:\s*\w+)?(?:\s*\n\s*model:\s*\w+)?(?:\s*\n\s*result_url:\s*"?(https?://[^"\s]+)"?)?', txt):
    rows.append((int(m.group(1)), m.group(2), m.group(3), m.group(4)))
for m in re.finditer(r'^\s*(\d+)\s+(https?://\S+?_([0-9a-f]{8}-[0-9a-f-]{27})\.png)\s*$', txt, re.M):
    rows.append((int(m.group(1)), m.group(3), 'completed', m.group(2)))
sub = {}
sp = os.path.join(ROOT, 'art/por5_submit.tsv')
if os.path.exists(sp):
    for ln in open(sp, encoding='utf8'):
        q = ln.split()
        if len(q) >= 2: sub[int(q[0])] = q[1]          # 같은 index 가 다시 나오면 나중 것(재시도)이 이긴다
DATE = os.environ.get('DATE', '20261119')
BASEURL = os.environ.get('HF_BASE', '')        # 결과 이미지 주소의 앞부분(…/user_<계정>/hf_) — 계정 경로라 소스에 적지 않고 환경 변수로 받는다
if not BASEURL:                                  # 환경 변수가 없으면 지난 기록(게시하지 않는 파일)의 주소에서 앞부분을 읽는다
    _m = re.search(r'(https://\S+?/hf_)\d{8}_', open(os.path.join(ROOT, 'art/por3_jobs.tsv'), encoding='utf8').read())
    BASEURL = _m.group(1) if _m else ''
for m in re.finditer(r'^\s*(\d+)\s+(\d{6})\s*$', txt, re.M):
    i2 = int(m.group(1)); rows.append((i2, sub[i2], 'completed', BASEURL + DATE + '_' + m.group(2) + '_' + sub[i2] + '.png'))
# "~HHMMSS idx idx …": 같은 묶음의 작업은 주소의 시각이 1~2초 안에서 같다 → 그 둘레를 더듬어 찾는다(아직 안 끝난 것은 PENDING)
def _try(url, out):
    tmp = out + '.part'
    r = subprocess.run(['curl', '-sS', '-f', '-o', tmp, '-w', '%{http_code}', url], capture_output=True, text=True)
    if r.stdout.strip() == '200' and os.path.exists(tmp) and os.path.getsize(tmp) > 1000: os.replace(tmp, out); return True
    if os.path.exists(tmp): os.remove(tmp)
    return False
probed = []
for m in re.finditer(r'^\s*~(\d{6})((?:\s+\d+)+)\s*$', txt, re.M):
    t0 = int(m.group(1)[:2]) * 3600 + int(m.group(1)[2:4]) * 60 + int(m.group(1)[4:])
    for i2 in [int(v) for v in m.group(2).split()]:
        key = plan[i2][0]; out = os.path.join(ROOT, 'art/raw5', key + '.png'); ok = False
        for dt in (0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6):
            t = t0 + dt; hms = '%02d%02d%02d' % (t // 3600 % 24, t // 60 % 60, t % 60)
            url = BASEURL + DATE + '_' + hms + '_' + sub[i2] + '.png'
            if _try(url, out):
                Image.open(out).load(); done[key] = [key, plan[i2][1], sub[i2], url]; got.append(key); probed.append('%d@%s' % (i2, hms)); ok = True; break
        if not ok: print('PENDING', i2, key)
if probed: print('probed', ' '.join(probed))
for idx, job, st, url in rows:
    key, name, ref = plan[idx]
    if st != 'completed' or not url:
        print('SKIP', idx, key, st); continue
    out = os.path.join(ROOT, 'art/raw5', key + '.png')
    r = subprocess.run(['curl', '-sS', '-o', out, '-w', '%{http_code}', url], capture_output=True, text=True)
    if r.stdout.strip() != '200': print('FAIL', idx, key, r.stdout, r.stderr); continue
    im = Image.open(out); im.load()
    done[key] = [key, name, job, url]
    got.append(key)
with open(jobs_path, 'w', encoding='utf8') as f:
    for k in sorted(done): f.write('\t'.join(done[k]) + '\n')
print('saved', len(got), 'total', len(done), '/', len(plan))
if got and len(sys.argv) > 1:
    T = 300; TH = 400; cols = 6; rows = (len(got) + cols - 1) // cols
    sh = Image.new('RGB', (cols * (T + 6), rows * (TH + 6)), (120, 120, 120))
    for i, k in enumerate(got):
        im = Image.open(os.path.join(ROOT, 'art/raw5', k + '.png')).convert('RGB').resize((T, TH), Image.LANCZOS)
        sh.paste(im, ((i % cols) * (T + 6), (i // cols) * (TH + 6)))
    sh.save(sys.argv[1], quality=85)
    print('sheet', sys.argv[1], 'order:', ' '.join(got))
