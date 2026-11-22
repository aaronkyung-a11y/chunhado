# v0.18 전법 — 이름을 한자 이름으로 바꾸고(번호 id 는 그대로), 무엇을 하는 전법인지 한눈에 보이게 한다
#   · 12가지 모두 새 이름(name) + 한자(han) + 짧은 효과 딱지(tag)
#   · 갈퀴 → 견인(牽引): '반격을 받지 않는다'뿐이어서 무엇을 하는지 보이지 않았다 → 한 칸 물러서며 적을 내 자리로 끌어당긴다(새 규칙)
#   · 결과에 tacId 를 실어 화면(fx.js · ui_panels.js)이 이름 글자가 아니라 id 로 가린다
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

# ───────────────────────── data.js ─────────────────────────
s = rd('src/data.js')
s = rep(s, "var GAME_VERSION = 'v0.17';", "var GAME_VERSION = 'v0.18';")
s = rep(s, "var TACTICS = {\n",
"""/* v0.18: 이름을 바꿨다(id 는 그대로) — 이름만 보고 효과가 떠오르도록 한자 두 글자로.
   돌출→격퇴 擊退 · 나선첨→난진 亂陣 · 이단첨→탈기 奪氣 / 갈퀴→견인 牽引 · 횡치→횡소 橫掃 · 선풍→일소 一掃
   화시→화전 火箭 · 관시→관통 貫通 · 난사→전우 箭雨 / 돌격→축출 逐出 · 돌파→관진 貫陣 · 돌진→유린 蹂躪
   han = 한자, tag = 단추에 적는 짧은 효과. 견인은 pull(끌어당김)이 새로 붙었다. 아래 주석의 옛 이름은 그때의 기록이다 */
var TACTICS = {
""")
NEW = [
 ("{ id: 'dolchul', name: '돌출', cost: 10,", "{ id: 'dolchul', name: '격퇴', han: '擊退', tag: '한 칸 밀어냄', cost: 10,"),
 ("{ id: 'naseon',  name: '나선첨', cost: 15,", "{ id: 'naseon',  name: '난진', han: '亂陣', tag: '혼란에 빠뜨림', cost: 15,"),
 ("{ id: 'idan',    name: '이단첨', cost: 20,", "{ id: 'idan',    name: '탈기', han: '奪氣', tag: '기력을 깎음', cost: 20,"),
 ("{ id: 'hoengchi', name: '횡치', cost: 15,", "{ id: 'hoengchi', name: '횡소', han: '橫掃', tag: '양옆의 적도 벰', cost: 15,"),
 ("{ id: 'seonpung', name: '선풍', cost: 20,", "{ id: 'seonpung', name: '일소', han: '一掃', tag: '둘레의 적 모두', cost: 20,"),
 ("{ id: 'hwasi',  name: '화시', cost: 10,", "{ id: 'hwasi',  name: '화전', han: '火箭', tag: '불을 붙임', cost: 10,"),
 ("{ id: 'gwansi', name: '관시', cost: 15,", "{ id: 'gwansi', name: '관통', han: '貫通', tag: '뒤의 적도 꿰뚫음', cost: 15,"),
 ("{ id: 'nansa',  name: '난사', cost: 20,", "{ id: 'nansa',  name: '전우', han: '箭雨', tag: '주위의 적도 맞음', cost: 20,"),
 ("{ id: 'dolgyeok', name: '돌격', cost: 10,", "{ id: 'dolgyeok', name: '축출', han: '逐出', tag: '밀어내고 전진', cost: 10,"),
 ("{ id: 'dolpa',    name: '돌파', cost: 15,", "{ id: 'dolpa',    name: '관진', han: '貫陣', tag: '뚫고 지나감 · 반격 없음', cost: 15,"),
 ("{ id: 'doljin',   name: '돌진', cost: 20,", "{ id: 'doljin',   name: '유린', han: '蹂躪', tag: '두 칸 밀고 혼란', cost: 20,"),
]
for a, b in NEW: s = rep(s, a, b)
# 견인(牽引): 끌어당김
s = rep(s, "{ id: 'galkwi',   name: '갈퀴', cost: 10, mult: 1.0, noCounter: true, need: 'C', great: { moraleDmg: 15 }, fx: '반격을 받지 않는다', gfx: '적 기력 -15', desc: '적을 걸어 넘어뜨린다. 반격을 받지 않는다. 대성공이면 적 기력 -15.' },",
           "{ id: 'galkwi',   name: '견인', han: '牽引', tag: '끌어당김 · 반격 없음', cost: 10, mult: 1.0, pull: true, noCounter: true, need: 'C', great: { moraleDmg: 15 }, fx: '한 칸 물러서며 적을 내가 섰던 자리로 끌어당긴다. 반격을 받지 않는다', gfx: '적 기력 -15', desc: '갈고리로 걸어 끌어당긴다 — 내가 한 칸 물러서고 적이 내가 섰던 자리로 온다(내 뒤가 막혔거나 불타고 있으면 끌지 못한다). 반격을 받지 않는다. 대성공이면 적 기력 -15.' },")
# 풀이 글 속의 옛 이름
s = rep(s, "fx: '적을 혼란에 빠뜨린다(10일)'", "fx: '적의 진을 흩뜨려 혼란에 빠뜨린다(10일)'")
s = rep(s, "var TACTIC_RATE = {",
"""/* 옛 이름 → id (v0.17 까지의 저장에 남은 지난 열흘의 기록을 다시 보여 줄 때) */
var TACTIC_OLD = { '돌출': 'dolchul', '나선첨': 'naseon', '이단첨': 'idan', '갈퀴': 'galkwi', '횡치': 'hoengchi', '선풍': 'seonpung', '화시': 'hwasi', '관시': 'gwansi', '난사': 'nansa', '돌격': 'dolgyeok', '돌파': 'dolpa', '돌진': 'doljin' };
var TACTIC_BY_ID = {};
(function () { for (var k in TACTICS) TACTICS[k].forEach(function (t) { TACTIC_BY_ID[t.id] = t; }); })();
function tacIdOf(res) { return res && res.kind === 'tactic' ? (res.tacId || TACTIC_OLD[res.tac] || '') : ''; }
var TACTIC_RATE = {""")
wr('src/data.js', s)

# ───────────────────────── core.js ─────────────────────────
s = rd('src/core.js')
s = rep(s, "  var res = { ok: true, kind: 'tactic', tac: tac.name, c: d.c, r: d.r, ac: u.c, ar: u.r, tname: uName(d), extra: [] };",
           "  var res = { ok: true, kind: 'tactic', tac: tac.name, tacId: tac.id, c: d.c, r: d.r, ac: u.c, ar: u.r, tname: uName(d), extra: [] };")
s = rep(s, "  res.dmg = dmg; res.tc = d.c; res.tr = d.r;\n  var dead = hurtUnit(d, dmg, u.f, u);\n  afterHit(u, d, dmg);\n",
"""  // v0.18 견인(牽引): 한 칸 물러서며 적을 내가 섰던 자리로 끌어당긴다. 내 뒤가 막혔거나(산·물목·부대·거점) 불타고 있으면 끌지 못한다 — 피해와 '반격 없음'은 그대로
  if (e.pull && !ranged) {
    var bk = stepDir(u.c, u.r, -dx, -dz), uc0 = u.c, ur0 = u.r;
    if (canPushInto(bk[0], bk[1], u) && moveCost(u, bk[0], bk[1]) < 99 && !G.fires[K(bk[0], bk[1])] && moveCost(d, uc0, ur0) < 99) { placeUnit(u, bk[0], bk[1]); placeUnit(d, uc0, ur0); res.pulled = true; }
    else res.noPull = true;
  }
  res.dmg = dmg; res.tc = d.c; res.tr = d.r;
  var dead = hurtUnit(d, dmg, u.f, u);
  afterHit(u, d, dmg);
""")
s = rep(s, "반격을 받지 않는 경우(갈퀴·돌파,", "반격을 받지 않는 경우(견인·관진,")
s = rep(s, "이 전법으로 혼란에 빠진 적은 반격하지 못한다(나선첨·돌진)", "이 전법으로 혼란에 빠진 적은 반격하지 못한다(난진·유린)")
# 견인으로 끌 수 있는가(화면이 미리 알려 준다)
s = rep(s, "/* 적 뒤로 n 칸까지 가운데 밀어낼 수 있는 칸 수 */\n",
"""/* v0.18 견인: 지금 자리에서 d 를 끌어당길 수 있는가 — unitTactic0 의 조건과 같다 */
function pullRoom(u, d) {
  if (hdist(u.c, u.r, d.c, d.r) !== 1) return false;
  var dx = cubeX(d.c, d.r) - cubeX(u.c, u.r), dz = d.r - u.r, bk = stepDir(u.c, u.r, -dx, -dz);
  return canPushInto(bk[0], bk[1], u) && moveCost(u, bk[0], bk[1]) < 99 && !G.fires[K(bk[0], bk[1])] && moveCost(d, u.c, u.r) < 99;
}
/* 적 뒤로 n 칸까지 가운데 밀어낼 수 있는 칸 수 */
""")
wr('src/core.js', s)

# ───────────────────────── ai.js: 기록 글 ─────────────────────────
s = rd('src/ai.js')
s = rep(s, "(res.confused ? ' — 혼란 ' + res.stN * 10 + '일' : '');", "(res.pulled ? ' — 끌어당김' : '') + (res.confused ? ' — 혼란 ' + res.stN * 10 + '일' : '');")
wr('src/ai.js', s)

# ───────────────────────── fx.js: 이름 글자 → id ─────────────────────────
s = rd('src/fx.js')
s = rep(s, "    var tac = res.kind === 'tactic' ? res.tac : '', pre = 0;", "    var tac = tacIdOf(res), pre = 0;                         // v0.18: 전법은 id 로 가린다(이름은 바뀔 수 있다)")
s = rep(s, "    var bowLike = ranged || tac === '화시' || tac === '관시' || tac === '난사';", "    var bowLike = ranged || tac === 'hwasi' || tac === 'gwansi' || tac === 'nansa';")
s = rep(s, "      var n = tac === '난사' ? 14 : (tac === '관시' ? 1 : (big ? 9 : 6)), colA = tac === '화시' && !res.fail ? FX_FIRE : FX_INK;",
           "      var n = tac === 'nansa' ? 14 : (tac === 'gwansi' ? 1 : (big ? 9 : 6)), colA = tac === 'hwasi' && !res.fail ? FX_FIRE : FX_INK;")
s = rep(s, "      if (tac === '관시' && !res.fail) {                       // 꿰뚫는 한 줄기", "      if (tac === 'gwansi' && !res.fail) {                     // 꿰뚫는 한 줄기")
s = rep(s, "      } else hit = fxVolley(tracks, pre + 60, pa, pt, n, colA, tac === '난사' ? 1.9 : 0.55) - 40;", "      } else hit = fxVolley(tracks, pre + 60, pa, pt, n, colA, tac === 'nansa' ? 1.9 : 0.55) - 40;")
s = rep(s, "      fxMark(tracks, hit, 320, 'spark', tac === '화시' ? FX_FIRE : FX_INK, TH, 0.6, 1.5, Math.random() * 6.28, {});", "      fxMark(tracks, hit, 320, 'spark', tac === 'hwasi' ? FX_FIRE : FX_INK, TH, 0.6, 1.5, Math.random() * 6.28, {});")
s = rep(s, "      if (tac === '화시' && !res.fail) for (i = 0; i < 3; i++)", "      if (tac === 'hwasi' && !res.fail) for (i = 0; i < 3; i++)")
s = rep(s, "    } else if (tac === '선풍' && !res.fail) {                 // 주위를 한 바퀴 휩쓴다", "    } else if (tac === 'seonpung' && !res.fail) {             // 주위를 한 바퀴 휩쓴다")
s = rep(s, "    } else if ((tac === '돌격' || tac === '돌진' || tac === '돌파') && !res.fail) {", "    } else if ((tac === 'dolgyeok' || tac === 'doljin' || tac === 'dolpa') && !res.fail) {")
s = rep(s, "      var dashTo = tac === '돌파' ? pa1 : fxLerp(pa, pt, 0.62);", "      var dashTo = tac === 'dolpa' ? pa1 : fxLerp(pa, pt, 0.62);")
s = rep(s, "      if (A && tac !== '돌파') tracks.push(", "      if (A && tac !== 'dolpa') tracks.push(")
s = rep(s, "      var k = (tac === '돌출' || tac === '나선첨' || tac === '이단첨') && !res.fail ? 0.5 : 0.4;\n      lunge(A, pa, TH, pre, k, tac !== '이단첨' || res.fail);",
           "      var k = (tac === 'dolchul' || tac === 'naseon' || tac === 'idan') && !res.fail ? 0.5 : 0.4;\n      lunge(A, pa, TH, pre, k, (tac !== 'idan' || res.fail) && !res.pulled);      // 견인으로 끌 때는 제자리로 돌아오지 않고 그대로 뒤로 물러선다(아래)")
s = rep(s, "      if (tac === '이단첨' && !res.fail && A) {                // 두 번 찌른다", "      if (tac === 'idan' && !res.fail && A) {                  // 두 번 찌른다")
s = rep(s, "      if ((tac === '돌출' || tac === '나선첨' || tac === '이단첨') && !res.fail) fxMark(", "      if ((tac === 'dolchul' || tac === 'naseon' || tac === 'idan') && !res.fail) fxMark(")
s = rep(s, "      if (tac === '나선첨' && !res.fail) fxMark(", "      if (tac === 'naseon' && !res.fail) fxMark(")
s = rep(s, "      if (tac === '횡치' && !res.fail) fxMark(", "      if (tac === 'hoengchi' && !res.fail) fxMark(")
s = rep(s, "      if (tac === '갈퀴' && !res.fail) fxMark(tracks, hit - 40, 440, 'arc', FX_SEAL, [TH[0], TH[1] - 0.15, TH[2]], 1.5, 2.9, ang + 1.57, { fade: 1.5 });   // 발을 거는 갈고리 획",
"""      if (tac === 'galkwi' && !res.fail) fxMark(tracks, hit - 40, 440, 'arc', FX_SEAL, [TH[0], TH[1] - 0.15, TH[2]], 1.5, 2.9, ang + 1.57, { fade: 1.5 });   // 거는 갈고리 획
      if (res.pulled && A) {                                   // v0.18 견인: 건 채로 뒷걸음질 — 나는 뒤 칸으로, 적은 내가 섰던 자리로(적은 아래 '자리 옮김'이 끈다)
        var pull0 = fxLerp(pa, TH, k);
        fxMark(tracks, hit + 40, 420, 'stroke', FX_SEAL, fxLerp(pa, TH, 0.5), 1.6, 2.6, ang, { aspect: 0.13, fade: 1.4 });
        tracks.push({ a: hit + 60, b: hit + 400, on: function () { sfx('step'); fxDust(pa[0], pa[1], pa[2], 1.0); }, step: function (u) { fxPut(A, fxLerp(pull0, pa1, easeIO(u))); } });
      }""")
s = rep(s, "    if (!bowLike && tac !== '선풍') slashAt(", "    if (!bowLike && tac !== 'seonpung') slashAt(")
s = rep(s, "    // 부가 대상(횡치·선풍·관시·난사)", "    // 부가 대상(횡소·일소·관통·전우)")
s = rep(s, "    // 밀려남\n    if (T && res.tAlive && (pt1[0] !== pt[0] || pt1[2] !== pt[2])) {\n      tracks.push({ a: hit + 40, b: hit + 300, on: function () { fxDust(pt[0], pt[1], pt[2], 1.1); }, step: function (u) { fxPut(T, fxLerp(pt, pt1, easeOut(u))); } });\n      end = Math.max(end, hit + 340);\n    }",
"""    // 자리 옮김: 밀려남 · (v0.18) 끌려옴 — 끌려올 때는 조금 늦게, 끄는 쪽을 따라온다
    if (T && res.tAlive && (pt1[0] !== pt[0] || pt1[2] !== pt[2])) {
      var mv0 = hit + (res.pulled ? 130 : 40), mv1 = hit + (res.pulled ? 440 : 300);
      tracks.push({ a: mv0, b: mv1, on: function () { fxDust(pt[0], pt[1], pt[2], 1.1); }, step: function (u) { fxPut(T, fxLerp(pt, pt1, res.pulled ? easeIO(u) : easeOut(u))); } });
      end = Math.max(end, mv1 + 40);
    }""")
wr('src/fx.js', s)

# ───────────────────────── ui_panels.js: 전법의 이름·효과가 보이는 곳 ─────────────────────────
s = rd('src/ui_panels.js')
# 이름 + 한자
s = rep(s, "/* 전법 풀이: 고른 상대에 대한 성공·대성공 확률과, 결과에 따라 달라지는 효과 */\n",
"""/* v0.18: 전법 이름에 한자를 곁들인다 */
function tacHan(tac) { return tac && tac.han ? ' <i class="hj">' + tac.han + '</i>' : ''; }
function tacNameH(tac) { return tac.name + tacHan(tac); }
/* 전법 풀이: 고른 상대에 대한 성공·대성공 확률과, 결과에 따라 달라지는 효과 */
""")
# 대상에게 할 수 있는 일: 전법 단추에 효과 딱지(끌 수 없는 자리의 견인은 그렇게 적는다)
s = rep(s, "      out.push({ kind: 'tactic', tac: tac, label: tac.name, sub: sub, ok: inT });",
           "      var tg = tac.tag || ''; if (tac.pull && inT && !pullRoom(u, t.u)) tg = '뒤가 막혀 끌지 못함 · 반격 없음';\n"
           "      out.push({ kind: 'tactic', tac: tac, label: tac.name, han: tac.han, fx: tg, sub: sub, ok: inT });")
s = rep(s, "h += '<button class=\"act' + (a.pri && a.ok ? ' pri' : '') + (a.ok ? '' : ' off') + '\" type=\"button\" data-a=\"act\" data-v=\"' + i + '\"><b>' + a.label + '</b>' + (a.sub ? '<small>' + a.sub + '</small>' : '') + '</button>'; }",
           "h += '<button class=\"act' + (a.pri && a.ok ? ' pri' : '') + (a.ok ? '' : ' off') + (a.fx ? ' tac' : '') + '\" type=\"button\" data-a=\"act\" data-v=\"' + i + '\"><b>' + a.label + (a.han ? ' <i class=\"hj\">' + a.han + '</i>' : '') + '</b>' + (a.fx ? '<small class=\"fx\">' + a.fx + '</small>' : '') + (a.sub ? '<small>' + a.sub + '</small>' : '') + '</button>'; }")
# 전법 풀이 창
s = rep(s, "        h += '<div class=\"tac' + (have ? '' : ' off') + '\"><div class=\"tn\"><b>' + tac.name + '</b><span>기력 '",
           "        h += '<div class=\"tac' + (have ? '' : ' off') + '\" data-t=\"' + tac.id + '\"><div class=\"tn\"><b>' + tacNameH(tac) + '</b><span>기력 '")
s = rep(s, "갈퀴·돌파, 멀리서 쏜 전법, 밀려나 떨어진 적은 반격하지 못합니다.</li>' +", "견인·관진, 멀리서 쏜 전법, 밀려나 떨어진 적은 반격하지 못합니다.</li>' +")
# 결과 한 줄 · 타격 글씨
s = rep(s, "    if (res.pushed >= 2) msg += ' · 두 칸 밀어냄';\n", "    if (res.pushed >= 2) msg += ' · 두 칸 밀어냄'; else if (res.pushed === 1) msg += ' · 밀어냄';\n    if (res.pulled) msg += ' · 끌어당김'; else if (res.noPull) msg += ' · 뒤가 막혀 끌지 못함';\n")
s = rep(s, "    if (res.kind === 'tactic') floatText(res.c, res.r, res.fail ? res.tac + ' 실패' : res.tac + (res.crit ? ' 대성공!' : '!'), res.fail ? C_DIM : (res.crit ? C_DMG : C_INK), 0, true, -34);",
           "    var tcH = res.kind === 'tactic' ? TACTIC_BY_ID[tacIdOf(res)] : null, tcN = tcH && tcH.han ? tcH.han + ' ' + tcH.name : res.tac;      // v0.18: 한자 이름을 앞세운다(옛 기록은 그때의 이름 그대로)\n"
           "    if (res.kind === 'tactic') floatText(res.c, res.r, res.fail ? res.tac + ' 실패' : tcN + (res.crit ? ' 대성공!' : '!'), res.fail ? C_DIM : (res.crit ? C_DMG : C_INK), 0, true, -34);")
s = rep(s, "    if (res.pushed >= 2) fxs.push('두 칸 밀어냄');\n", "    if (res.pushed >= 2) fxs.push('두 칸 밀어냄'); else if (res.pushed === 1) fxs.push('밀어냄');\n    if (res.pulled) fxs.push('끌어당김'); else if (res.noPull) fxs.push('끌지 못함');\n")
s = rep(s, "    var shot = far || (res.kind === 'tactic' && (res.tac === '화시' || res.tac === '관시' || res.tac === '난사'));",
           "    var tid0 = tacIdOf(res), shot = far || tid0 === 'hwasi' || tid0 === 'gwansi' || tid0 === 'nansa';")
# 도움말
s = rep(s, "반격은 통상 공격만큼 받습니다(갈퀴·돌파, 멀리서 쏜 전법,", "반격은 통상 공격만큼 받습니다(견인·관진, 멀리서 쏜 전법,")
s = rep(s, "돌출·돌격은 두 칸 밀어내고, 나선첨은 반드시 혼란시키고, 이단첨은 기력을 30 깎는 식입니다.", "격퇴·축출은 두 칸 밀어내고, 난진은 반드시 혼란시키고, 탈기는 기력을 30 깎는 식입니다.")
s = rep(s, "전법(나선첨 등)으로 걸면 10일입니다.", "전법(난진 등)으로 걸면 10일입니다.")
wr('src/ui_panels.js', s)

# ───────────────────────── style.css ─────────────────────────
s = rd('src/style.css')
s += """
/* ── v0.18 전법: 한자 이름 · 효과 딱지 ── */
.hj { font-style: normal; font-family: var(--font-display); font-weight: 600; font-size: .82em; color: var(--seal); letter-spacing: .04em; margin-left: 1px; }
.act.pri .hj, .act:active .hj { color: inherit; }
.act small.fx { display: block; color: var(--ink-2); font-size: 11px; font-weight: 700; line-height: 1.25; }
.act.pri small.fx, .act:active small.fx { color: inherit; }
.act.off small.fx { font-weight: 500; }
.tac .tn .hj { font-size: 13px; }
"""
wr('src/style.css', s)
print('p1_tactics18: ok')
