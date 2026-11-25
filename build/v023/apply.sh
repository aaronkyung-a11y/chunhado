#!/bin/bash
# v0.22.1 의 소스(build/*.v0221.*)에 명부(tools/roster23.py)와 build/v023/s*.py 를 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v023/apply.sh
# 명부(src/roster.js): 예전 명부(build/roster.v0221.js) + tools/hist23.py(생몰년 · 내력 · 새 무장 · 여덟 시대)
# 그림 · 소리 · 지도는 0.22.1 그대로다.
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice bios cine roster mapdata map3d sprites sfxdata assets; do cp build/$f.v0221.js src/$f.js; done
cp build/style.v0221.css src/style.css; cp build/index.v0221.html src/index.html
python3 tools/roster23.py > build/v023/roster.log
for p in build/v023/s*.py; do python3 "$p"; done
for f in roster ai core data fx ui3d ui_panels duel voice bios cine; do node --check src/$f.js; done
echo "v0.23 applied"
