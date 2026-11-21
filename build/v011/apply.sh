#!/bin/bash
# v0.10.1 의 소스에 build/v011/p*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v011/apply.sh
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels; do cp build/$f.v0101.js src/$f.js; done
cp build/style.v0101.css src/style.css; cp build/index.v0101.html src/index.html
n=0
for p in build/v011/p*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels; do node --check src/$f.js; done
echo "applied: $n patches"
