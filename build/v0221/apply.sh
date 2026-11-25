#!/bin/bash
# v0.22 의 소스(build/*.v022.*)에 build/v0221/s*.py 를 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v0221/apply.sh
# 소리(src/sfxdata.js): 0.22 의 소리 29개에 tools/make_audio_v0221.py(순찰의 딱따기 clack).
# 초상(src/assets.js): 0.22 의 그림에서 이각만 다시 자른다 — tools/por0221_fix.py(원본 그림 art/raw18m 이 있을 때만. 없으면 build/assets.v0221.js 를 그대로 쓴다)
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice bios cine roster mapdata map3d sprites; do cp build/$f.v022.js src/$f.js; done
cp build/style.v022.css src/style.css; cp build/index.v022.html src/index.html
python3 tools/make_audio_v0221.py > build/v0221/audio.log
if [ -e art/raw18m/lijue.png ]; then python3 tools/por0221_fix.py build/assets.v022.js src/assets.js lijue > build/v0221/por.log; else cp build/assets.v0221.js src/assets.js; fi
for p in build/v0221/s*.py; do python3 "$p"; done
for f in ai core data fx ui3d ui_panels duel voice bios cine; do node --check src/$f.js; done
echo "v0.22.1 applied"
