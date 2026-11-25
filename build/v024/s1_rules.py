# -*- coding: utf-8 -*-
"""v0.24: 아이의 성비(남 105 : 여 100) · 딸 · 능력에 맞는 공용 초상(120장 가운데 덜 쓰인 것부터).   python3 build/v024/s1_rules.py   (apply.sh 가 v0.23 백업에서 되돌린 뒤 부른다)"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s)


def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:70], s.count(a))
    return s.replace(a, b)


# ───────── data.js ─────────
d = rd('src/data.js')
d = rep(d, "var GAME_VERSION = 'v0.23';", "var GAME_VERSION = 'v0.24';")
d = rep(d, "var BIRTH = { p: 1.5, lord: 4.5,", "var BIRTH = { boy: 105, girl: 100, p: 1.5, lord: 4.5,")
d = rep(d, "   inh = 아버지를 닮는 몫", "   boy : girl = 태어나는 아이의 성비(v0.24 — 남 105 : 여 100)\n   inh = 아버지를 닮는 몫")
d = rep(d, "var HEIR = {", """var GIRL_NAMES = ('연 란 향 영 옥 월 설 선 은 혜 아 숙 련 빙 교 채 예 완 형 희 화 주 정 소 진 하 미 봉 운 유 경 단 리 매 명 서 수 순 실 애 여 용 윤 인 임 자 지 춘 취 홍 효').split(' ');      // v0.24: 딸의 이름(한 글자)
/* v0.24 공용 초상(그림 묶음 pool — tools/por24_prompt.py): 가장 뛰어난 능력에 맞는 모습 다섯 갈래. 열쇠 = g + m(남)/f(여) + 갈래(1 ~ 5) + 번호(01 ~), 예: gm101 · gf512.
   n = 갈래마다의 장수(남 · 여 같다), key = 갈래를 정하는 능력(같으면 앞의 것). 이 판에서 태어난 아이가 쓰고, 덜 쓰인 그림부터 고른다(core.js 의 poolPick) */
var POOL = { n: [14, 14, 12, 10, 10], key: ['war', 'ldr', 'int', 'pol', 'cha'], name: ['무력', '통솔', '지력', '정치', '매력'] };
var HEIR = {""", 1)
wr('src/data.js', d)

# ───────── bios.js: 향총 → 곽유지(0.23 의 향총은 예전 명부의 상총과 같은 사람이었다 — tools/hist23.py) ─────────
import re, json
b = rd('src/bios.js')
nb = json.load(io.open(os.path.join(ROOT, 'build', 'v023', 'bios_new.json'), encoding='utf-8'))
m = re.search(r"'향총': '[^']*'", b); assert m and '곽유지' in nb and '향총' not in nb
b = b[:m.start()] + "'곽유지': '%s'" % nb['곽유지'] + b[m.end():]
wr('src/bios.js', b)

# ───────── core.js ─────────
c = rd('src/core.js')
c = rep(c, """function kidName(o, used) {
  var sur = surnameOf(o.n), N = KID_NAMES.length, h = strHash('kid|' + o.id + '|' + G.year + '|' + (G.seed0 | 0)) >>> 0, i, nm;
  for (i = 0; i < N; i++) { nm = sur + KID_NAMES[(h + i) % N]; if (!used[nm]) return nm; }
  for (i = 0; i < N * 4; i++) { nm = sur + KID_NAMES[(h + i) % N] + KID_NAMES[((h >>> 9) + i * 3) % N]; if (!used[nm]) return nm; }
  return null;
}""", """function kidName(o, used, girl) {           // v0.24: girl = 딸의 이름
  var L = girl ? GIRL_NAMES : KID_NAMES, sur = surnameOf(o.n), N = L.length, h = strHash('kid|' + o.id + '|' + G.year + '|' + (G.seed0 | 0)) >>> 0, i, nm;
  for (i = 0; i < N; i++) { nm = sur + L[(h + i) % N]; if (!used[nm]) return nm; }
  for (i = 0; i < N * 4; i++) { nm = sur + L[(h + i) % N] + L[((h >>> 9) + i * 3) % N]; if (!used[nm]) return nm; }
  return null;
}
/* v0.24 공용 초상 고르기: 가장 뛰어난 능력의 갈래에서 아직 덜 쓰인 그림을 준다. 그 갈래의 그림이 모두 쓰였으면 둘째로 뛰어난 능력의 갈래에 남은 그림을 먼저 쓴다.
   죽은 사람이 쓰던 그림은 다시 돈다. 같은 만큼 쓰인 그림 사이에서는 이름으로 정해지는 차례(판의 난수는 쓰지 않는다) */
function porCat(o) { var ks = POOL.key, c = 0, i; for (i = 1; i < ks.length; i++) if (o[ks[i]] > o[ks[c]]) c = i; return c; }
function poolPick(o) {
  var s = isWoman(o) ? 'gf' : 'gm', ks = POOL.key, c1 = porCat(o), c2 = -1, use = {}, best = null, i, r, j;
  for (i = 0; i < ks.length; i++) if (i !== c1 && (c2 < 0 || o[ks[i]] > o[ks[c2]])) c2 = i;
  for (i = 0; i < G.officers.length; i++) { var p = G.officers[i]; if (p !== o && p.kid && p.st !== 'dead' && p.por) use[p.por] = (use[p.por] || 0) + 1; }      // 아이들끼리만 센다(명부의 사람이 쓰는 것은 세지 않는다)
  for (r = 0; r < 2; r++) {
    var c = r ? c2 : c1;
    for (j = 1; j <= POOL.n[c]; j++) {
      var key = s + (c + 1) + (j < 10 ? '0' : '') + j, score = (use[key] || 0) * 2 + r, h = strHash(o.n + '|' + key) >>> 0;
      if (!best || score < best[0] || (score === best[0] && h < best[1])) best = [score, h, key];
    }
  }
  return best[2];
}""")
c = rep(c, "  var key = 'kid|' + o.id + '|' + G.year, nm = kidName(o, used); if (!nm) return null;\n  function roll(k) { return omenRoll(key + '|' + k) / 100; }",
        "  var key = 'kid|' + o.id + '|' + G.year;\n  function roll(k) { return omenRoll(key + '|' + k) / 100; }\n  var girl = roll('sex') * (BIRTH.boy + BIRTH.girl) >= BIRTH.boy, nm = kidName(o, used, girl); if (!nm) return null;      // v0.24: 성비")
c = rep(c, "  k.por = (k.war >= k.int ? 'gm' : 'gc') + (1 + Math.floor(roll('por') * 5));\n", "  if (girl) k.sex = 'f';\n  k.por = poolPick(k);                                                   // v0.24: 능력에 맞는 공용 초상\n")
c = rep(c, "  if (lifeNew) { var lcap = ", "  G.officers.forEach(function (ko) { if (ko.kid && /^g[mc]\\d$/.test(ko.por || '')) ko.por = poolPick(ko); });      // v0.24: 0.23 에서 태어난 아이(옛 공용 초상 열 장)도 새 공용 초상으로\n  if (lifeNew) { var lcap = ")
c = rep(c, "지금은 아들만(여성 공용 초상이 아직 없다).", "v0.24: 아들 · 딸이 BIRTH.boy : BIRTH.girl 로 태어난다.") if "지금은 아들만(여성 공용 초상이 아직 없다)." in c else c
wr('src/core.js', c)

# ───────── ui3d.js: 초상의 주소를 다 만들었다는 표시(그림 묶음이 늦게 올 때 쓴다) ─────────
u3 = rd('src/ui3d.js')
u3 = rep(u3, "  for (k in PORTRAITS) POR_URL[k] = URL.createObjectURL(b64blob(PORTRAITS[k], 'image/webp'));\n", "  for (k in PORTRAITS) POR_URL[k] = URL.createObjectURL(b64blob(PORTRAITS[k], 'image/webp'));\n  window.POR_BUILT = true;                                               // v0.24: 뒤늦게 오는 그림 묶음(아티팩트 판)은 이 뒤로는 제 손으로 주소를 만든다(tools/build.py 의 받아 오기)\n")
wr('src/ui3d.js', u3)

# ───────── ui_panels.js: 도움말 ─────────
u = rd('src/ui_panels.js')
u = rep(u, "' + BIRTH.grow + '년 뒤에 장성해 찾아오고, 초상은 공용입니다. 무장 창에 아버지와 자식이 적힙니다. 지금은 아들만 태어납니다.</p>' +",
        "' + BIRTH.grow + '년 뒤에 장성해 찾아옵니다. <b>아들과 딸</b>이 ' + BIRTH.boy + ' : ' + BIRTH.girl + ' 으로 태어납니다. 초상은 <b>공용 초상 ' + (POOL.n.reduce(function (a, b) { return a + b; }, 0) * 2) + '장</b>(남 · 여 절반씩) 가운데, 그 아이의 <b>가장 뛰어난 능력</b>(무력 · 통솔 · 지력 · 정치 · 매력)에 맞는 모습에서 아직 덜 쓰인 그림부터 고릅니다 — 무력이 으뜸이면 무기를 든 무인, 통솔이면 지휘하는 장수, 지력이면 책사, 정치면 문관, 매력이면 귀인의 모습입니다. 무장 창에 아버지와 자식이 적힙니다.</p>' +")
wr('src/ui_panels.js', u)
print('s1_rules ok')
