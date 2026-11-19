#!/usr/bin/env python3
"""v0.4 수묵 초상 내려받기: jobs_wait 결과 줄(index,job_id,status,type,model,"url")을 표준입력으로 받는다.
   art/por3_plan.tsv 의 index → key 로 art/raw3/<key>.png 저장, art/por3_jobs.tsv 에 기록, 대조용 시트 생성."""
import sys, re, os, subprocess, csv
from PIL import Image
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
plan = {}
for ln in open(os.path.join(ROOT, 'art/por3_plan.tsv'), encoding='utf8'):
    p = ln.rstrip('\n').split('\t')
    plan[int(p[0])] = (p[1], p[2], p[3])
jobs_path = os.path.join(ROOT, 'art/por3_jobs.tsv')
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
sp = os.path.join(ROOT, 'art/por3_submit.tsv')
if os.path.exists(sp):
    for ln in open(sp, encoding='utf8'):
        q = ln.split()
        if len(q) >= 2: sub[int(q[0])] = q[1]          # 같은 index 가 다시 나오면 나중 것(재시도)이 이긴다
DATE = os.environ.get('DATE', '20261119')
BASEURL = os.environ.get('HF_BASE', '')        # 결과 이미지 주소의 앞부분(…/user_<계정>/hf_) — 계정 경로라 소스에 적지 않고 환경 변수로 받는다
for m in re.finditer(r'^\s*(\d+)\s+(\d{6})\s*$', txt, re.M):
    i2 = int(m.group(1)); rows.append((i2, sub[i2], 'completed', BASEURL + DATE + '_' + m.group(2) + '_' + sub[i2] + '.png'))
for idx, job, st, url in rows:
    key, name, ref = plan[idx]
    if st != 'completed' or not url:
        print('SKIP', idx, key, st); continue
    out = os.path.join(ROOT, 'art/raw3', key + '.png')
    r = subprocess.run(['curl', '-sS', '-o', out, '-w', '%{http_code}', url], capture_output=True, text=True)
    if r.stdout.strip() != '200': print('FAIL', idx, key, r.stdout, r.stderr); continue
    im = Image.open(out); im.load()
    done[key] = [key, name, job, url]
    got.append(key)
with open(jobs_path, 'w', encoding='utf8') as f:
    for k in sorted(done): f.write('\t'.join(done[k]) + '\n')
print('saved', len(got), 'total', len(done), '/', len(plan))
if got and len(sys.argv) > 1:
    T = 256; cols = 6; rows = (len(got) + cols - 1) // cols
    sh = Image.new('RGB', (cols * T, rows * T), 'white')
    for i, k in enumerate(got):
        im = Image.open(os.path.join(ROOT, 'art/raw3', k + '.png')).convert('RGB').resize((T, T), Image.LANCZOS)
        sh.paste(im, ((i % cols) * T, (i // cols) * T))
    sh.save(sys.argv[1], quality=85)
    print('sheet', sys.argv[1], 'order:', ' '.join(got))
