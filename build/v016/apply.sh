#!/bin/bash
# v0.15 의 소스에 build/v016/p*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v016/apply.sh
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice; do cp build/$f.v015.js src/$f.js; done
cp build/style.v015.css src/style.css; cp build/index.v015.html src/index.html; cp build/sfxdata.v015.js src/sfxdata.js
n=0
for p in build/v016/p*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels duel voice; do node --check src/$f.js; done
echo "applied: $n patches"
