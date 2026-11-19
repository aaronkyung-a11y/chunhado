#!/usr/bin/env python3
"""초상 원본 내려받기: 표준입력으로 결과 URL(한 줄에 하나)을 받아 art/por2_jobs.tsv 의 작업 id 와 맞춰 art/raw2/<key>.png 로 저장."""
import sys, re, os, subprocess
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jobs = {}
for ln in open(os.path.join(root, 'art', 'por2_jobs.tsv'), encoding='utf-8'):
    p = ln.rstrip('\n').split('\t')
    if len(p) == 3: jobs[p[2]] = p[0]
out = os.path.join(root, 'art', 'raw2'); os.makedirs(out, exist_ok=True)
ok = bad = 0
for ln in sys.stdin:
    m = re.search(r'(https://\S+?_([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.png)', ln)
    if not m: continue
    url, jid = m.group(1), m.group(2)
    key = jobs.get(jid)
    if not key: print('모르는 작업', jid); bad += 1; continue
    dst = os.path.join(out, key + '.png')
    if os.path.exists(dst) and os.path.getsize(dst) > 50000: ok += 1; continue
    r = subprocess.run(['curl', '-sS', '--fail', '--max-time', '90', '-o', dst, url])
    if r.returncode == 0 and os.path.getsize(dst) > 50000: ok += 1
    else: print('실패', key, r.returncode); bad += 1
print('받음', ok, '실패', bad, '· 폴더 안 파일', len([f for f in os.listdir(out) if f.endswith('.png')]))
