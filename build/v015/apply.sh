#!/bin/bash
# v0.14 의 소스에 build/v015/p*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v015/apply.sh
# 지도(src/mapdata.js · src/map3d.js · build/terrain.jpg)는 패치가 아니라 도구로 다시 만든 것이다 — 한 번만 하면 된다:
#   python3 tools/terrain15.py steep src/map3d.js src/mapdata.js src/mapdata.json build/mapdata.json     # 산을 넓힌다(build/mapdata.v014.* 가 그 전의 것)
#   python3 tools/bake3d_ink.py <geo_dir> build/mapdata.json build/terrain.jpg src/map3d.js 3072           # 그림과 높이맵을 다시 굽는다
#   python3 tools/terrain15.py elev src/map3d.js src/mapdata.js src/mapdata.json build/mapdata.json      # 칸마다 높이 단계
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice; do cp build/$f.v014.js src/$f.js; done
cp build/style.v014.css src/style.css; cp build/index.v014.html src/index.html; cp build/sfxdata.v014.js src/sfxdata.js
n=0
for p in build/v015/p*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels duel voice; do node --check src/$f.js; done
echo "applied: $n patches"
