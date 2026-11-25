#!/bin/bash
# v0.25 의 소스(build/*.v025.*)에 build/v026/s*.py 를 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v026/apply.sh
# 그림 묶음(src/assets_p253.js): 다시 그린 개별 초상 253장 — tools/por26_prompt.py(글 · 자세 표) → art/raw26(그림) → tools/facebox.py → tools/make_pack24.py. 원본 그림이 없으면 build/assets_p253.v026.js 를 쓴다.
# 지도의 4배 조각(art/map4/tiles · tiles.json): tools/map4.py 가 만든다 — 판을 만들 때 tools/build.py 가 아티팩트 판(data/t4-<지문>/) · 앱(tiles/t4-<지문>/)으로 옮긴다.
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice bios cine roster mapdata map3d sprites sfxdata assets assets_pool assets_p253; do cp build/$f.v025.js src/$f.js; done
cp build/style.v025.css src/style.css; cp build/index.v025.html src/index.html; cp build/sw.v025.js pwa/sw.js
if [ -d art/raw26 ] && [ -f art/por26_faces.tsv ] && [ "$(ls art/raw26 | wc -l)" = "253" ]; then python3 tools/make_pack24.py p253 art/raw26 art/por26_faces.tsv art/por26_out > build/v026/pack.log 2>&1; elif [ -f build/assets_p253.v026.js ]; then cp build/assets_p253.v026.js src/assets_p253.js; fi
for p in build/v026/s*.py; do python3 "$p"; done
for f in roster ai core data fx ui3d ui_panels duel voice bios cine; do node --check src/$f.js; done
node --check pwa/sw.js
echo "v0.26 applied"
