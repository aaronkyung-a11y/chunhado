#!/bin/bash
# v0.12.1 의 소스에 build/v013/p*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v013/apply.sh
# 새 파일 셋은 패치가 아니라 그대로 두는 소스다: src/duel.js(대결 화면) · src/voice.js(음성 엔진) · src/voicedata.js(생성물 — tools/make_voice_v013.py)
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels; do cp build/$f.v0121.js src/$f.js; done
cp build/style.v0121.css src/style.css; cp build/index.v0121.html src/index.html; cp build/sfxdata.v0121.js src/sfxdata.js
n=0
for p in build/v013/p*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels duel voice; do node --check src/$f.js; done
echo "applied: $n patches"
