#!/usr/bin/env python3
"""GitHub 저장소에 올릴 폴더를 채운다(커밋·푸시는 따로): python3 tools/deploy_repo.py <저장소 폴더>
   맨 위 = 게임(dist/pwa 그대로: index.html, manifest.webmanifest, sw.js, icons/, bgm/, .nojekyll) → GitHub Pages(main / 루트)가 이것을 내보낸다.
   그 밖 = 소스(src, pwa, tools, tests, build 의 필요한 것, vendor 의 three.js, 그림·소리 기록).
   올리지 않는 것: 그림·소리 원본(art/raw*, audio7/raw — 크고, 작업 번호로 다시 받을 수 있음), 내려받은 주소가 적힌 로컬 기록(*_jobs.tsv 등),
   옛 판 스냅샷(versions/ — 아티팩트에 있음), 시험 화면 그림, 판별 백업(build/*.v0x.*).
   먼저 python3 tools/build.py --pwa 로 dist/pwa 를 만들어 둔다."""
import os, sys, shutil, glob
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
dst = os.path.abspath(sys.argv[1])
assert os.path.isdir(os.path.join(dst, '.git')), dst + ' 는 git 저장소가 아님'
BAD = ('X-Amz-', 'Signature=', 'AWSAccessKeyId', 'Bearer ', 'cloudfront.net', 'api_key', 'secret', 'ghp_', 'github_pat_')
GENERATED = ('src/assets.js', 'src/sprites.js', 'src/map3d.js', 'src/sfxdata.js', 'index.html')      # base64 가 든 큰 파일: 글자 검사에서 뺀다(사람이 쓴 글이 아님)
files = []                                            # (원본 경로, 저장소 안 경로)
def add(src_rel, dst_rel=None):
    p = os.path.join(ROOT, src_rel); assert os.path.isfile(p), src_rel
    files.append((p, dst_rel or src_rel))
def add_glob(pat, keep=lambda rel: True):
    for p in sorted(glob.glob(os.path.join(ROOT, pat))):
        rel = os.path.relpath(p, ROOT)
        if os.path.isfile(p) and keep(rel): files.append((p, rel))
# 1) 게임
pwa = os.path.join(ROOT, 'dist', 'pwa'); assert os.path.isfile(os.path.join(pwa, 'index.html')), '먼저 tools/build.py --pwa'
for d, _, fs in os.walk(pwa):
    for f in sorted(fs): files.append((os.path.join(d, f), os.path.relpath(os.path.join(d, f), pwa)))
# 2) 소스
for f in ('README.md', 'CHANGELOG.md'): add(f)
add_glob('src/*')
add_glob('pwa/*'); add_glob('pwa/icons/*')
add_glob('tools/*.py')
add_glob('tests/*.js'); add_glob('tests/*.py')
for f in ('build/terrain.jpg', 'build/patch_v04_ui3d.py', 'build/patch_v04_panels.py'): add(f)
add_glob('build/v07/*.py')
add('vendor/package/build/three.min.js')
def clean(rel):                                       # 그림 기록 가운데 내려받은 주소가 적힌 것(로컬 전용)은 빼고 올린다
    s = open(os.path.join(ROOT, rel), encoding='utf-8').read()
    ok = not any(b in s for b in BAD)
    if not ok: skipped.append(rel)
    return ok
skipped = []
add_glob('art/*.tsv', clean); add_glob('art/*.txt', clean); add_glob('art/*.md', clean)
add('audio7/jobs.tsv')
# 3) 글자 검사: 주소·열쇠 같은 것이 섞여 있으면 멈춘다
bad = []
for p, rel in files:
    if rel in GENERATED or rel.split('.')[-1] in ('png', 'jpg', 'mp3', 'webmanifest') or rel == '.nojekyll': continue
    try: s = open(p, encoding='utf-8').read()
    except UnicodeDecodeError: bad.append((rel, '글이 아닌 파일')); continue
    for b in BAD:
        if b in s and rel not in ('tools/pack_sources.py', 'tools/deploy_repo.py'): bad.append((rel, b))
if bad:
    for b in bad: print('올릴 수 없음:', b)
    raise SystemExit(1)
# 4) 저장소 폴더를 비우고(.git 은 그대로) 다시 채운다
for n in os.listdir(dst):
    if n == '.git': continue
    p = os.path.join(dst, n)
    shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
tot = 0
for p, rel in files:
    q = os.path.join(dst, rel); os.makedirs(os.path.dirname(q), exist_ok=True); shutil.copyfile(p, q); tot += os.path.getsize(q)
big = sorted(((os.path.getsize(p), rel) for p, rel in files), reverse=True)[:6]
print('%d개 파일, %d바이트 → %s' % (len(files), tot, dst))
print('뺀 기록(주소가 적힌 로컬 전용):', ' '.join(skipped))
for sz, rel in big: print('  %10d  %s' % (sz, rel))
