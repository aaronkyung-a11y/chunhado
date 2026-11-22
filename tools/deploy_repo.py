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
GENERATED = ('src/assets.js', 'src/sprites.js', 'src/map3d.js', 'src/sfxdata.js', 'build/sfxdata.v011.js', 'build/sfxdata.v012.js', 'build/sfxdata.v017.js', 'build/sfxdata.v018.js', 'src/voicedata.js', 'index.html')      # base64 가 든 큰 파일: 글자 검사에서 뺀다(사람이 쓴 글이 아님)
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
add_glob('tests/*.js'); add_glob('tests/*.py'); add_glob('tests/*.sh')
for f in ('build/terrain.jpg', 'build/patch_v04_ui3d.py', 'build/patch_v04_panels.py'): add(f)
add_glob('build/v07/*.py'); add_glob('build/v071/*.py'); add_glob('build/v081/*.py'); add_glob('build/v09/*.py'); add_glob('build/v091/*.py'); add_glob('build/v092/*.py'); add_glob('build/v093/*.py'); add('build/v093/apply.sh'); add_glob('build/v010/*.py'); add('build/v010/apply.sh'); add_glob('build/v0101/*.py'); add('build/v0101/apply.sh'); add_glob('build/v011/*.py'); add('build/v011/apply.sh'); add_glob('build/v012/*.py'); add('build/v012/apply.sh'); add_glob('build/v0121/*.py'); add('build/v0121/apply.sh'); add('build/sfxdata.v012.js'); add('build/sfxdata.v011.js'); add('dev/v012_voice_plan.md'); add_glob('build/v013/*.py'); add('build/v013/apply.sh'); add_glob('build/v014/*.py'); add('build/v014/apply.sh'); add_glob('build/v015/*.py'); add('build/v015/apply.sh'); add_glob('build/v016/*.py'); add('build/v016/apply.sh'); add_glob('build/v017/*.py'); add('build/v017/apply.sh'); add_glob('build/v018/*.py'); add('build/v018/apply.sh'); add_glob('build/v0181/*.py'); add('build/v0181/apply.sh'); add_glob('build/v019/*.py'); add('build/v019/apply.sh'); add_glob('build/v0191/*.py'); add('build/v0191/apply.sh'); add_glob('build/v020/*.py'); add('build/v020/apply.sh'); add('build/v020/terrain.sh'); add('build/sfxdata.v017.js'); add('build/sfxdata.v018.js'); add('voice13/lines.py'); add('voice13/jobs.tsv'); add('voice13/qa.py'); add('voice13/voiceqa.py'); add_glob('voice13/raw/*.mp3')
# 옛 판의 보관(v0.13~): 아티팩트 한 판에 담을 수 있는 크기(256MiB)가 차서, 오래된 스냅샷과 소스 묶음은 여기에 둔다
ARCHIVE = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.8.1', '0.9', '0.9.1', '0.9.2', '0.9.3', '0.10', '0.10.1', '0.11', '0.12', '0.12.1']      # v0.15: 0.7 ~ 0.9.3 도 옮겼다 · v0.19: 0.10 ~ 0.12.1 도(아티팩트 한 판은 256MiB 까지)
for _v in ARCHIVE: add('versions/chunhado-v%s.html' % _v); add('dev/sources-v%s.txt' % _v)      # v0.12: 소리를 다시 만드는 바탕(tools/make_audio_v012.py) · 중국어 음성 계획
add('vendor/package/build/three.min.js')
def clean(rel):                                       # 그림 기록 가운데 내려받은 주소가 적힌 것(로컬 전용)은 빼고 올린다
    s = open(os.path.join(ROOT, rel), encoding='utf-8').read()
    ok = not any(b in s for b in BAD)
    if not ok: skipped.append(rel)
    return ok
skipped = []
add_glob('art/*.tsv', clean); add_glob('art/*.txt', clean); add_glob('art/*.md', clean)
add('audio7/jobs.tsv'); add('art/por8_out/crops.tsv'); add('art/por93_out/crops.tsv'); add('art/por17_out/crops.tsv'); add('art/por18_out/crops.tsv'); add('art/por19_out/crops.tsv'); add('art/title18/title.jpg')
# 3) 글자 검사: 주소·열쇠 같은 것이 섞여 있으면 멈춘다
bad = []
for p, rel in files:
    if rel in GENERATED or rel.split('.')[-1] in ('png', 'jpg', 'mp3', 'mp4', 'webm', 'webmanifest') or rel == '.nojekyll': continue
    try: s = open(p, encoding='utf-8').read()
    except UnicodeDecodeError: bad.append((rel, '글이 아닌 파일')); continue
    if rel.startswith('versions/'): s = ''.join(l for l in s.split('\n') if len(l) < 4000)      # 스냅샷: base64 가 든 긴 줄은 빼고 본다
    if rel.startswith('dev/sources-v'):                                                           # 소스 묶음: 그 안에 든 pack_sources.py(검사할 낱말의 표가 적혀 있다)는 빼고 본다
        parts = s.split('\n=====8<===== '); s = '\n'.join(q for q in parts if not q.startswith('tools/pack_sources.py'))
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
