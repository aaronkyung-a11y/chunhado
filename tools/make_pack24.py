#!/usr/bin/env python3
"""v0.24 그림 묶음(pack): 새 초상(공용 초상 · 뒤에는 개별 초상)을 src/assets.js 와 따로 src/assets_<pack>.js 에 둔다 — var PACK_<pack>={"por":{흉상},"scn":{장면}};
   왜 따로인가: 아티팩트의 페이지 하나는 16MiB 까지인데 흉상(256²)만 한 장에 23KB 다 — 수백 장을 더 넣을 자리가 없다. tools/build.py 가 묶음을
   한 파일짜리 판(오프라인 · PWA)에는 그대로 넣고, 아티팩트 판(--split)에는 data/por-<pack>-<지문>.json · data/scn-<pack>-<지문>.json 으로 떼어 페이지가 뜬 뒤에 받아 오게 한다.
   자르는 법은 그대로다: tools/make_assets_v08.py 를 0.19 와 같은 인자(SKEW=0.12 · 256 320 72 52)로 돌려 거기서 나온 흉상 · 장면을 옮긴다.
   usage: make_pack24.py <pack> <raw_dir> <faces.tsv> <out_dir>      (환경 변수 FOCUS=<손으로 고친 얼굴 상자.tsv>)"""
import sys, os, io, re, json, subprocess, tempfile
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PACK, RAW, FACES, OUT = sys.argv[1:5]
keys = sorted(f[:-4] for f in os.listdir(RAW) if f.endswith('.png'))
td = tempfile.mkdtemp(prefix='pack24_')
ros = os.path.join(td, 'roster.js'); tmp = os.path.join(td, 'assets.js')
io.open(ros, 'w', encoding='utf-8').write('var X=[' + ','.join('{"por":"%s"}' % k for k in keys) + '];')
env = dict(os.environ, SKEW='0.12')
r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools/make_assets_v08.py'), RAW, FACES, OUT, tmp, os.path.join(ROOT, 'build/assets.v023.js'), ros, '256', '320', '72', '52'], env=env, capture_output=True, text=True, cwd=ROOT)
assert r.returncode == 0, r.stderr[-800:]
s = io.open(tmp, encoding='utf-8').read()
i0, i1, i2 = s.index('var PORTRAITS'), s.index('var SCENES'), s.index('var TITLE_IMG')
def grab(lo, hi):
    d = {}
    for k in keys:
        m = re.search(r'"%s":"([A-Za-z0-9+/=]+)"' % re.escape(k), s[lo:hi]); assert m, k; d[k] = m.group(1)
    return d
por, scn = grab(i0, i1), grab(i1, i2)
out = os.path.join(ROOT, 'src', 'assets_%s.js' % PACK)
io.open(out, 'w', encoding='utf-8', newline='\n').write('var PACK_%s={"por":%s,\n"scn":%s};\n' % (PACK, json.dumps(por, separators=(',', ':')), json.dumps(scn, separators=(',', ':'))))
print('pack %s: %d장 · 흉상 %d바이트(장당 %d) · 장면 %d바이트(장당 %d) → %s %d바이트' % (PACK, len(keys), sum(map(len, por.values())), sum(map(len, por.values())) // len(keys), sum(map(len, scn.values())), sum(map(len, scn.values())) // len(keys), os.path.relpath(out, ROOT), os.path.getsize(out)))
print(r.stdout[-300:])
