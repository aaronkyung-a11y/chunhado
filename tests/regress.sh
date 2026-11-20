#!/bin/bash
# 전체 회귀: bash tests/regress.sh [로그 폴더=build/logs/v010/reg]     (먼저 tools/build.py, --embed, --pwa 로 세 판을 모두 만든 뒤)
# 끝나면 <로그 폴더>/_summary.txt 에 시험마다 종료 코드가 한 줄씩, 마지막 줄에 DONE.
cd "$(dirname "$0")/.."; L=${1:-build/logs/v010/reg}; mkdir -p $L; : > $L/_summary.txt
run() { name=$1; shift; ( "$@" > $L/$name.log 2>&1 ); echo "$name exit $?" >> $L/_summary.txt; }
sha256sum dist/index.html dist/offline.html dist/pwa/index.html > $L/_build.sha
run job8 node tests/job8.js
run loy8 node tests/loy8.js
run tac7 node tests/tac7.js
run adv9 node tests/adv9.js
run exp91 timeout 900 node tests/exp91.js
run peace91 node tests/peace91.js
run corps10 timeout 900 node tests/corps10.js
run corpsrun10 timeout 1500 node tests/corpsrun10.js 100
run rush8_ai timeout 900 node tests/rush8.js 48 2
PASSIVE=1 run rush8_passive timeout 900 node tests/rush8.js 48 2
run sim_12345 timeout 900 node tests/sim.js 360 12345
run sim_777 timeout 900 node tests/sim.js 360 777
run sim_4 timeout 900 node tests/sim.js 360 4
run fuzz_1_0 timeout 900 node tests/fuzz.js 200 1 0
run fuzz_5_14 timeout 900 node tests/fuzz.js 200 5 14
run fuzz_3_4 timeout 900 node tests/fuzz.js 200 3 4
run fuzz_7_2 timeout 900 node tests/fuzz.js 200 7 2
run floor timeout 1500 node tests/floor.js
run zonecheck_1 timeout 900 node tests/zonecheck.js 360 1
run zonecheck_9 timeout 900 node tests/zonecheck.js 360 9
for t in d1 d2 d2b d3 d4 d6 d7 d9 d10 d14 d15 d16 d17 d18 d19 d20; do run $t timeout 1800 python3 tests/$t.py; done
run d11_1_4 timeout 2400 python3 tests/d11.py 400 1 4
run d11_2_0 timeout 2400 python3 tests/d11.py 300 2 0
run d11_3_2 timeout 2400 python3 tests/d11.py 300 3 2
for m in ok fail1 failall; do PAGE=index.html CDN=$m run b9_$m timeout 900 python3 tests/b9.py; done
run d12_nomusic timeout 1500 python3 tests/d12.py
PAGE=pwa/index.html run d12_music timeout 1500 python3 tests/d12.py
run d13 timeout 1500 python3 tests/d13.py
run text92 timeout 900 python3 tests/text92.py
for v in 0.9.3 0.9.2 0.9.1 0.9 0.8.1 0.8 0.7 0.6 0.5 0.4 0.3 0.2; do run d8_v$v timeout 900 python3 tests/d8.py chunhado-v$v-offline.html; done
echo DONE >> $L/_summary.txt
