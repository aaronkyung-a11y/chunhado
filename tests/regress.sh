#!/bin/bash
# 전체 회귀: bash tests/regress.sh [로그 폴더=build/logs/v015/reg]     (먼저 tools/build.py, --embed, --pwa 로 세 판을 모두 만든 뒤)
# 끝나면 <로그 폴더>/_summary.txt 에 시험마다 종료 코드가 한 줄씩, 마지막 줄에 DONE.
cd "$(dirname "$0")/.."; L=${1:-build/logs/v015/reg}; mkdir -p $L; : > $L/_summary.txt
run() { name=$1; shift; ( "$@" > $L/$name.log 2>&1 ); echo "$name exit $?" >> $L/_summary.txt; }
sha256sum dist/index.html dist/offline.html dist/pwa/index.html > $L/_build.sha
# 규칙 시험(node). NODE_FROM=<폴더> 를 주면, 그 폴더의 _rules.sha(규칙 소스 core · ai · data 의 지문)가 지금과 같을 때 그때의 결과(_node.txt)를 그대로 쓴다 — 화면 쪽만 고쳐 다시 돌릴 때
if [ -n "$NODE_FROM" ] && sha256sum -c --status "$NODE_FROM/_rules.sha"; then
  cat "$NODE_FROM/_node.txt" >> $L/_summary.txt; echo "(규칙 시험은 $NODE_FROM 의 결과 — 규칙 소스가 같다)" > $L/_node_from.txt
else
  run job8 node tests/job8.js
  run loy8 node tests/loy8.js
  run tac7 node tests/tac7.js
  run adv9 node tests/adv9.js
  run tie11 env OLD=build/logs/v011/src0101 node tests/tie11.js
  run sup11 node tests/sup11.js
  run cns11 node tests/cns11.js
  run fac12 env OLD=build/logs/v012/src011 node tests/fac12.js
  run duel13 timeout 900 node tests/duel13.js
  run dip14 timeout 900 node tests/dip14.js
  run terr15 timeout 900 node tests/terr15.js
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
  sha256sum src/core.js src/ai.js src/data.js > $L/_rules.sha; cp $L/_summary.txt $L/_node.txt
fi
for t in d1 d2 d2b d3 d4 d6 d7 d9 d10 d14 d15 d16 d17 d18 d19 d20 d21 d22 d23 d24 d25 d26 d27; do run $t timeout 1800 python3 tests/$t.py; done
run d11_1_4 timeout 2400 python3 tests/d11.py 400 1 4
run d11_2_0 timeout 2400 python3 tests/d11.py 300 2 0
run d11_3_2 timeout 2400 python3 tests/d11.py 300 3 2
for m in ok fail1 failall; do PAGE=index.html CDN=$m run b9_$m timeout 900 python3 tests/b9.py; done
run d12_nomusic timeout 1500 python3 tests/d12.py
PAGE=pwa/index.html run d12_music timeout 1500 python3 tests/d12.py
run d13 timeout 1500 python3 tests/d13.py
run text92 timeout 900 python3 tests/text92.py
for v in 0.14 0.13 0.12.1 0.12 0.11 0.10.1 0.10 0.9.3 0.9.2 0.9.1 0.9 0.8.1 0.8 0.7 0.6 0.5 0.4 0.3 0.2; do run d8_v$v timeout 900 python3 tests/d8.py chunhado-v$v-offline.html; done
echo DONE >> $L/_summary.txt
