#!/bin/bash
# v0.23 의 소스(build/*.v023.*)에 build/v024/s*.py 를 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v024/apply.sh
# 명부(src/roster.js): tools/roster23.py 를 POOL=1 로 — 공용 초상을 쓰던 253명에게 능력에 맞는 공용 초상(gm101 …)을 준다.
# 그림 묶음(src/assets_pool.js): 공용 초상 120장 — tools/por24_prompt.py(글) → art/raw24(그림) → tools/facebox.py → tools/make_pack24.py. 원본 그림이 없으면 있던 것을 그대로 쓴다.
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice bios cine roster mapdata map3d sprites sfxdata assets; do cp build/$f.v023.js src/$f.js; done
cp build/style.v023.css src/style.css; cp build/index.v023.html src/index.html
POOL=1 python3 tools/roster23.py > build/v024/roster.log
if [ -d art/raw24 ] && [ -f art/por24_faces.tsv ]; then python3 tools/make_pack24.py pool art/raw24 art/por24_faces.tsv art/por24_out > build/v024/pack.log 2>&1; fi
for p in build/v024/s*.py; do python3 "$p"; done
for f in roster ai core data fx ui3d ui_panels duel voice bios cine; do node --check src/$f.js; done
echo "v0.24 applied"
