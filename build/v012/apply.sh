#!/bin/bash
# v0.11 의 소스에 build/v012/p*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v012/apply.sh
# 효과음(src/sfxdata.js)은 따로: python3 tools/make_audio_v012.py  (build/sfxdata.v011.js 에서 출발, ffmpeg 필요)
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels; do cp build/$f.v011.js src/$f.js; done
cp build/style.v011.css src/style.css; cp build/index.v011.html src/index.html
n=0
for p in build/v012/p*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels; do node --check src/$f.js; done
echo "applied: $n patches"
