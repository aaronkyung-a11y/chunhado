#!/usr/bin/env python3
"""v0.7 소리 내려받기: audio7/jobs.tsv 의 작업을 audio7/raw/<kind>_<name>.mp3 로. 주소의 시각은 앞뒤로 찾아본다.
usage: DATE=20261119 dl_audio7.py <HHMMSS> <name…>     (주소 앞부분은 HF_BASE 또는 로컬 전용 기록에서)"""
import sys, os, re, subprocess, datetime
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
def base():
    b = os.environ.get('HF_BASE')
    if b: return b
    for fn in ('art/por7_jobs.tsv', 'art/por5_jobs.tsv'):
        p = os.path.join(ROOT, fn)
        if os.path.exists(p):
            m = re.search(r'(https://\S+?)/hf_\d{8}_', open(p, encoding='utf8').read())
            if m: return m.group(1)
    raise SystemExit('HF_BASE 가 필요합니다')
jobs = {}
for l in open(os.path.join(ROOT, 'audio7/jobs.tsv'), encoding='utf8'):
    if l.strip() and not l.startswith('#'): k, i, n, s, j = l.split(); jobs[n] = (k, j)      # 뒤에 나온 줄이 덮는다
os.makedirs(os.path.join(ROOT, 'audio7/raw'), exist_ok=True)
t0 = datetime.datetime.strptime(os.environ.get('DATE', '20261119') + sys.argv[1], '%Y%m%d%H%M%S')
span = int(os.environ.get('SPAN', '25'))
for n in sys.argv[2:]:
    k, j = jobs[n]; out = os.path.join(ROOT, 'audio7/raw', '%s_%s.mp3' % (k, n)); ok = False
    for d in sorted(range(-span, span + 1), key=abs):
        t = t0 + datetime.timedelta(seconds=d)
        url = '%s/hf_%s_%s.mp3' % (base(), t.strftime('%Y%m%d_%H%M%S'), j)
        r = subprocess.run(['curl', '-sS', '-o', out, '-w', '%{http_code}', url], capture_output=True, text=True)
        if r.stdout.strip() == '200': ok = True; break
    print(n, 'ok %d bytes (%+ds)' % (os.path.getsize(out), d) if ok else 'NOT FOUND')
    if not ok and os.path.exists(out): os.remove(out)
