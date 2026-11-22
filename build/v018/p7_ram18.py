# v0.18 충차 — 쓸모가 없다는 말을 들었다: 내구가 잘 깎이지 않고, 오는 데 너무 느리다.
#   잰 값(v0.17): 이웃 거점 사이(길 61개)를 가는 데 창병 평균 49일 · 기병 38일 · 충차 92일(가장 긴 곳 250일). 충차 한 번의 내구 피해는 창병의 2.4배쯤(중도시 2,400을 혼자 7~8번).
#   ① 길에서는 수레도 잘 구른다: 충차의 이동력 9 → 10, 길의 칸값 3 → 2(보병 · 기병과 같다). 길 밖(평지 4 · 숲 · 구릉 8)은 그대로 — 평균 92일 → 57일(build/logs/v018/ramspeed.js)
#   ② 성의 내구를 깎는 힘 두 배: 공성 배수 4.0 → 8.0
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)
s = rd('src/data.js')
s = rep(s, "  ram:     { name: '충차', g: '차', cls: 'siege', mp: 9,  atk: 0.40, def: 0.70, range: 1, weapon: 'ram',     siege: 4.0, vsBase: 0.3 },",
           "  ram:     { name: '충차', g: '차', cls: 'siege', mp: 10, atk: 0.40, def: 0.70, range: 1, weapon: 'ram',     siege: 8.0, vsBase: 0.3 },      // v0.18: 이동력 9 → 10 · 공성 4 → 8(성의 내구를 두 배로 깎는다)")
s = rep(s, "var ROAD_COST = [2, 2, 3];", "var ROAD_COST = [2, 2, 2];      // 길의 칸값: 보병 · 기병 · 수레. v0.18: 수레(충차)도 길에서는 2(전에는 3 — 이웃 거점까지 보병의 두 배 가까이 걸렸다)")
wr('src/data.js', s)
s = rd('src/ui_panels.js')
s = rep(s, "<li>충차는 성의 내구를 크게 깎습니다.</li>", "<li><b>충차</b>는 성의 내구를 크게 깎습니다 — 한 번에 창병의 네댓 배(중도시의 내구 2,400이 네 번쯤이면 무너집니다). 싸움에는 약하니 다른 부대로 지켜 주세요. 길에서는 보병보다 조금 느린 정도로 가고, 길 밖에서는 느립니다.</li>")
wr('src/ui_panels.js', s)
print('p7_ram18: ok')
