#!/bin/bash
# v0.13 의 소스에 build/v014/p*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v014/apply.sh
# src/voicedata.js(생성물)는 그대로 둔다.
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice; do cp build/$f.v013.js src/$f.js; done
cp build/style.v013.css src/style.css; cp build/index.v013.html src/index.html; cp build/sfxdata.v013.js src/sfxdata.js
n=0
for p in build/v014/p*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels duel voice; do node --check src/$f.js; done
echo "applied: $n patches"
