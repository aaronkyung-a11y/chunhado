# v0.18 군단 — ① 출격 금지: 내정 방침에서는 성 밖으로 나가 싸우지 않는다. 군비 · 지원 방침에서는 [출격 금지]로 고를 수 있다
#              ② 군단에 맡긴 거점에서도 [수송]은 내가 직접 보낼 수 있다
#   그동안: 어느 방침이든 적 부대가 성 가까이(4칸) 오면 군단이 스스로 부대를 내어 싸웠다(aiDefense). 내정에 힘쓰라고 맡긴 군단도 그랬다.
#   이제: corpsSortie(cp) — 공격 방침은 늘 나간다 · 내정 방침은 나가지 않는다 · 군비 · 지원은 cp.hold(출격 금지)를 따른다.
#         나가지 않는 군단의 부대는 돌아오고(귀환), 돌아오는 길에도 먼저 치지 않는다(성은 전처럼 스스로 반격한다).
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

# ───────────────────────── core.js ─────────────────────────
s = rd('src/core.js')
s = rep(s, "function corpsDirOk(cp, dir, target) {",
"""/* v0.18 출격: 군단이 성 밖으로 부대를 내어 싸워도 되는가. 공격 방침은 늘 · 내정 방침은 나가지 않는다 · 군비 · 지원은 cp.hold(출격 금지)를 따른다 */
function corpsSortie(cp) { return !!cp && (cp.dir === 'atk' || (cp.dir !== 'dev' && !cp.hold)); }
function corpsHolds(u) { var cp = (u && u.f === G.player && u.corps) ? corpsById(u.corps) : null; return !!cp && !corpsSortie(cp); }      // 이 부대의 군단은 싸우러 나가지 않는가
function corpsRecall(cp) {                                 // 나가 있는 싸움 부대를 불러들인다(수송대는 가던 길을 간다)
  if (corpsSortie(cp)) return 0;
  var n = 0;
  corpsUnits(cp).forEach(function (u) { if (u.type !== 'trans' && u.ai && (u.ai.mode === 'defend' || u.ai.mode === 'attack')) { u.ai = { mode: 'return', home: u.home }; n++; } });
  return n;
}
function corpsSetHold(cp, on) { if (!cp) return ERR('없는 군단'); cp.hold = !!on; return { ok: true, back: corpsRecall(cp) }; }
function corpsDirOk(cp, dir, target) {""")
s = rep(s, "    else if (u.ai && u.ai.mode === 'attack') u.ai = { mode: 'return', home: u.home };\n  });\n  return { ok: true };",
           "    else if (u.ai && u.ai.mode === 'attack') u.ai = { mode: 'return', home: u.home };\n  });\n  corpsRecall(cp);                                                   // v0.18: 나가 싸우지 않는 방침이면 막으러 나간 부대도 불러들인다\n  return { ok: true };")
wr('src/core.js', s)

# ───────────────────────── ai.js ─────────────────────────
s = rd('src/ai.js')
s = rep(s, "  cp.wait = null;                                                     // 공격인데 아직 나서지 못한 까닭: { need, have }(병력) · { ap: 1 }(행동력)\n  aiDefense(f);\n",
           "  cp.wait = null;                                                     // 공격인데 아직 나서지 못한 까닭: { need, have }(병력) · { ap: 1 }(행동력)\n  if (corpsSortie(cp)) aiDefense(f);                                  // v0.18: 내정 방침 · 출격 금지에서는 막으러 나가지 않는다(성이 스스로 막는다)\n")
s = rep(s, "  // 1) 공격 기회\n  var best = null, bv = 0, rg = uRange(u);\n  if (mode !== 'supply') {",
           "  // 1) 공격 기회\n  var best = null, bv = 0, rg = uRange(u);\n  if (corpsHolds(u) && mode !== 'supply' && mode !== 'garrison') mode = 'return';      // v0.18: 싸우러 나가지 않는 군단의 부대 — 돌아간다\n  if (mode !== 'supply' && !corpsHolds(u)) {")
wr('src/ai.js', s)

# ───────────────────────── ui_panels.js ─────────────────────────
s = rd('src/ui_panels.js')
s = rep(s, "var DIR_SUB = { dev: '시설 · 치안', arm: '징병 · 병기 · 훈련', atk: '고른 거점을 친다', sup: '병력 · 물자를 보낸다' };",
           "var DIR_SUB = { dev: '시설 · 치안 · 출격 안 함', arm: '징병 · 병기 · 훈련', atk: '고른 거점을 친다', sup: '병력 · 물자를 보낸다' };")
# 군단 창: 출격 허용 · 금지
s = rep(s, "      h += '<div class=\"sec\">거점 <em class=\"cnt\">' + bs.length + '</em><button class=\"btn sm\" type=\"button\" data-a=\"add\">+ 넣기</button></div><div class=\"rows cpl\">';",
"""      if (cp.dir !== 'atk') h += '<div class="cpg cph"><p>출격 <b' + (corpsSortie(cp) ? '' : ' class="bad"') + '>' + (corpsSortie(cp) ? '허용' : '금지') + '</b>' + (cp.dir === 'dev' ? '' : '<button class="btn sm" type="button" data-a="hold">' + (cp.hold ? '허용으로' : '금지로') + '</button>') + '</p><p class="note">' +
        (cp.dir === 'dev' ? '내정 방침에서는 성 밖으로 나가 싸우지 않습니다 — 적이 오면 성이 스스로 막습니다. 나가서 막게 하려면 방침을 군비로 바꾸세요.' : (cp.hold ? '적이 다가와도 성 밖으로 나가 싸우지 않습니다(나가 있던 부대는 돌아옵니다).' : '적 부대가 성 가까이 오면 부대를 내어 막습니다.')) + '</p></div>';      // v0.18
      h += '<div class="sec">거점 <em class="cnt">' + bs.length + '</em><button class="btn sm" type="button" data-a="add">+ 넣기</button></div><div class="rows cpl">';""")
s = rep(s, "      tgt: function () { var cp = corpsById(id); if (!cp) return; if (cp.dir === 'atk') pickCorpsTarget(cp); else pickCorpsDest(cp); },\n      lead: function () {",
           "      tgt: function () { var cp = corpsById(id); if (!cp) return; if (cp.dir === 'atk') pickCorpsTarget(cp); else pickCorpsDest(cp); },\n"
           "      hold: function () { var cp = corpsById(id); if (!cp || cp.dir === 'dev' || cp.dir === 'atk') return; var r = corpsSetHold(cp, !cp.hold); sfx('ui'); toast(corpsName(cp) + ' — 출격 ' + (cp.hold ? '금지' + (r.back ? ' · ' + r.back + '개 부대를 불러들입니다' : '') : '허용'), 2400); corpsRefresh(); },\n"
           "      lead: function () {")
# 군단에 맡긴 거점: [수송]은 내가 직접
s = rep(s, "<button class=\"cmd\" type=\"button\" data-a=\"direct\"><b>직할로</b><small>내가 직접 다스린다</small></button></div>' +\n          '<div class=\"sec\">무장 <em class=\"cnt\">' + ob.length + '</em></div><div class=\"rows\">';",
           "<button class=\"cmd\" type=\"button\" data-a=\"direct\"><b>직할로</b><small>내가 직접 다스린다</small></button><button class=\"cmd\" type=\"button\" data-a=\"trans\"><b>수송</b><small>내가 직접 보낸다</small></button></div>' +      // v0.18: 군단의 거점에서도 수송은 내가\n"
           "          '<div class=\"sec\">무장 <em class=\"cnt\">' + ob.length + '</em></div><div class=\"rows\">';")
s = rep(s, "function flowTransport(b) {\n  var list = idleOfficers(b).sort(function (x, y) { return aiMilScore(x) - aiMilScore(y); });",
           "function flowTransport(b) {\n  var cp0 = baseCorps(b);                                       // v0.18: 군단에 맡긴 거점에서도 보낸다(군단장은 자리를 지킨다 · 행동력은 직할의 것 · 나간 수송대는 직할)\n"
           "  var list = idleOfficers(b).filter(function (o) { return !(cp0 && cp0.lead === o.id); }).sort(function (x, y) { return aiMilScore(x) - aiMilScore(y); });")
# 도움말
s = rep(s, "<b>지원</b>(병력과 물자를 고른 내 거점으로 보낸다).</p>' +",
           "<b>지원</b>(병력과 물자를 고른 내 거점으로 보낸다). <b>내정 방침의 군단은 성 밖으로 나가 싸우지 않습니다</b>(적이 오면 성이 스스로 막습니다). 군비 · 지원 방침에서는 군단 창의 <b>출격</b>에서 허용 · 금지를 고릅니다 — 허용이면 적 부대가 성 가까이 올 때 나가서 막습니다. 군단에 맡긴 거점에서도 <b>수송</b>은 직접 보낼 수 있습니다(거점 창의 수송 — 나간 수송대는 직할입니다).</p>' +")
wr('src/ui_panels.js', s)
print('p9_corps18: ok')
