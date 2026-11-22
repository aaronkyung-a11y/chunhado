# v0.20 (6) 싸움터의 조언은 군사가 아니라 그 부대의 부장이 한다
#   "전투에서 적을 선택할 때도 군사가 하나하나 조언하는 건 말이 안 맞고 한다면 부장이 부장의 능력으로 제안하는 게 맞다. 통솔, 지력 등의 영향을 받으면서"
#   · 참모(uStaff): 부대의 부장 가운데 지력과 통솔이 높은 사람. 부장이 없으면 주장이 스스로 헤아린다.
#   · 지력 → 계략이 통할지의 ○×(맞을 확률) · 가능성을 또렷이 보는가(지력 70 이상) / 어림으로만 보는가
#   · 통솔 → 예상 피해를 얼마나 정확히 내다보는가(통솔 88 이상이면 그대로, 낮을수록 '약 N'이 실제와 벌어진다 — 가장 낮으면 ±40%) ·
#            어느 수가 가장 나은지(薦)를 바르게 짚는가(통솔 0.6 + 지력 0.4 의 값이 87 이상이면 늘 바르게, 낮을수록 가끔 다른 수를 권한다)
#   규칙의 확률과 피해는 그대로다 — 보이는 가늠만 달라진다. 숫자로 보기(메뉴 → 확률 표시)를 켜면 예상 피해는 전처럼 정확한 값이다.
#   내정(등용 · 탐색)의 조언은 전처럼 군사가 한다.
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

s = rd('src/core.js')
s = rep(s, """function advise(f, roll, rollA, p, tInt) {
  var A = facAdv(f); if (!A) return null;
  var real = roll < p, acc = adviceAcc(A, tInt);
  return { adv: A, acc: acc, says: rollA < acc ? real : !real };
}""", """function advise(f, roll, rollA, p, tInt) { return adviseBy(facAdv(f), roll, rollA, p, tInt); }
function adviseBy(A, roll, rollA, p, tInt) {                       // v0.20: 조언하는 이를 정해서(싸움터에서는 부대의 참모)
  if (!A) return null;
  var real = roll < p, acc = adviceAcc(A, tInt);
  return { adv: A, acc: acc, says: rollA < acc ? real : !real };
}
/* v0.20 부대의 참모: 싸움터에서 헤아리는 사람 — 부장 가운데 지력과 통솔이 높은 쪽(지력을 조금 더 친다). 부장이 없으면 주장 자신.
   staffRead = 어느 수가 가장 나은지 바르게 짚을 확률(%) · staffErr = 예상 피해가 벌어지는 폭(0 ~ 0.4) */
var STAFF = { readK: 1.15, readMin: 50, errAt: 88, errMax: 0.4 };
function uStaff(u) {
  var best = null, bv = -1;
  for (var i = 1; i < u.off.length; i++) { var o = off(u.off[i]); if (!o) continue; var v = o.int * 1.2 + o.ldr; if (v > bv) { bv = v; best = o; } }
  return best || uLeader(u);
}
function staffRead(o) { return clamp(Math.round((o.ldr * 0.6 + o.int * 0.4) * STAFF.readK), STAFF.readMin, 100); }
function staffErr(o) { return clamp((STAFF.errAt - o.ldr) / 100, 0, STAFF.errMax); }""")
wr('src/core.js', s)

s = rd('src/ui_panels.js')
s = rep(s, "function sayRow(o, say, sub, cls) { return '<div class=\"say' + (cls ? ' ' + cls : '') + '\">' + porTag(o, 'sm') + '<div><b>' + o.n + '</b> <span>'",
        "function sayRow(o, say, sub, cls, role) { return '<div class=\"say' + (cls ? ' ' + cls : '') + '\">' + porTag(o, 'sm') + '<div>' + (role ? '<em class=\"role\">' + role + '</em>' : '') + '<b>' + o.n + '</b> <span>'")
s = rep(s, """function oddsEye() {
  if (!G || !(G.player >= 0)) return { o: null, adv: false, fine: true };
""", """function oddsEye() {
  if (!G || !(G.player >= 0)) return { o: null, adv: false, fine: true };
  var su = typeof selUnit === 'function' ? selUnit() : null;       // v0.20: 부대를 고른 동안(싸움터)에는 그 부대의 참모가 가늠한다
  if (su && su.f === G.player && su.off && su.off.length) { var S = uStaff(su); return { o: S, adv: false, staff: true, lead: S === uLeader(su), fine: S.int >= ODDS_FINE }; }
""")
s = rep(s, """  return '<p class="note eye">가늠 — ' + (e.adv ? '군사 ' : '군주 ') + '<b>' + e.o.n + '</b> (지력 ' + e.o.int + ') · ' + (e.fine ? '또렷이 봅니다' : '어림으로만 봅니다 <small>지력 ' + ODDS_FINE + ' 이상의 군사를 두면 또렷해집니다</small>') + '</p>';""",
"""  if (e.staff) return '<p class="note eye">가늠 — ' + (e.lead ? '주장 ' : '부장 ') + '<b>' + e.o.n + '</b> (통솔 ' + e.o.ldr + ' · 지력 ' + e.o.int + ') · ' + (e.fine ? '또렷이 봅니다' : '어림으로만 봅니다 <small>지력 ' + ODDS_FINE + ' 이상의 부장을 붙이면 또렷해집니다</small>') + '</p>';
  return '<p class="note eye">가늠 — ' + (e.adv ? '군사 ' : '군주 ') + '<b>' + e.o.n + '</b> (지력 ' + e.o.int + ') · ' + (e.fine ? '또렷이 봅니다' : '어림으로만 봅니다 <small>지력 ' + ODDS_FINE + ' 이상의 군사를 두면 또렷해집니다</small>') + '</p>';""")
s = rep(s, "function ployAdvice(u, pl, t) { return advise(G.player, ployRoll(pl, t), ployRollA(pl, t), ployChance(u, pl, t.u || null), t.u ? uInt(t.u) : 0); }",
        """function ployAdvice(u, pl, t) { return adviseBy(uStaff(u), ployRoll(pl, t), ployRollA(pl, t), ployChance(u, pl, t.u || null), t.u ? uInt(t.u) : 0); }      // v0.20: 싸움터의 조언은 부대의 참모가
/* v0.20 예상 피해: 참모의 통솔이 낮을수록 실제와 벌어진다(같은 턴 · 같은 상대에게는 같은 값). 숫자로 보기를 켜면 정확한 값 */
function dmgEst(u, t, v) {
  var err = staffErr(uStaff(u)); v = Math.round(v);
  if (UI.pct || err <= 0 || v <= 0) return '-' + fmt(v);
  var g = v * (1 + (omenRoll('est|' + u.id + '|' + (t && t.id !== undefined ? t.id : 'b')) / 50 - 1) * err), st = g >= 1000 ? 100 : (g >= 200 ? 50 : 10);
  return '약 -' + fmt(Math.max(st, Math.round(g / st) * st));
}""")
s = rep(s, "out.push({ kind: 'attack', label: '공격', sub: d <= rg ? '예상 -' + fmt(Math.round(attackExpect(u, t.u).dealt)) : '사거리 밖', ok: d <= rg, pri: true });",
        "out.push({ kind: 'attack', label: '공격', sub: d <= rg ? '예상 ' + dmgEst(u, t.u, attackExpect(u, t.u).dealt) : '사거리 밖', ok: d <= rg, pri: true });")
s = rep(s, """    var advR = facAdv(u.f);
    if (advR && d <= rg) {                                       // v0.18 군사의 추천 = 공격 명령이 고르는 수(bestStrike)
      var bs0 = bestStrike(u, t.u), recA = bs0.tac ? out.filter(function (a0) { return a0.tac === bs0.tac; })[0] : out[0];
      if (recA && bs0.v > 0) recA.rec = true;
    }""", """    if (d <= rg) {                                               // v0.20 참모(부장)의 추천: 공격 명령이 고르는 수(bestStrike)를 짚되, 헤아림(통솔 · 지력)이 모자라면 가끔 다른 수를 권한다
      var bs0 = bestStrike(u, t.u), recA = bs0.tac ? out.filter(function (a0) { return a0.tac === bs0.tac; })[0] : out[0];
      if (recA && bs0.v > 0) {
        if (omenRoll('rec|' + u.id + '|' + t.u.id) >= staffRead(uStaff(u))) {
          var alts = out.filter(function (a0) { return a0.ok && a0 !== recA && (a0.kind === 'attack' || a0.kind === 'tactic'); });
          if (alts.length) recA = alts[Math.floor(omenRoll('rec2|' + u.id + '|' + t.u.id) / 100 * alts.length) % alts.length];
        }
        recA.rec = true;
      }
    }""")
s = rep(s, """          var advO = adv1 ? adv1.adv : (recA ? facAdv(x.f) : null);
          if (advO) h += sayRow(advO, """, """          var advO = adv1 ? adv1.adv : (recA ? uStaff(x) : null);      // v0.20: 말하는 이는 이 부대의 참모(부장 — 없으면 주장)
          if (advO) h += sayRow(advO, """)
s = rep(s, "(ns.length ? '<b class=\"bad\">' + ns.join('·') + josa(ns[ns.length - 1], '은는').slice(-1) + ' 어렵겠습니다.</b>' : ''), adv1 ? accT(adv1.acc) : '', 'adv advn');",
        "(ns.length ? '<b class=\"bad\">' + ns.join('·') + josa(ns[ns.length - 1], '은는').slice(-1) + ' 어렵겠습니다.</b>' : ''), adv1 ? accT(adv1.acc) : '', 'adv advn', advO === uLeader(x) ? '주장' : '부장');")
s = rep(s, "function talk(o, say, sub, ms) {", "function talk(o, say, sub, ms, role) {      // v0.20: role = 이름 옆 딱지를 따로 정할 때(싸움터의 조언: 부장 · 주장)")
s = rep(s, "  var t = $('talk'), rl = roleOf(o);", "  var t = $('talk'), rl = role || roleOf(o);")
s = rep(s, "  var name = uName(u), res, pa = a.kind === 'ploy' ? (a.adv || null) : null;", "  var name = uName(u), res, pa = a.kind === 'ploy' ? (a.adv || null) : null, paRole = pa ? (pa.adv === uLeader(u) ? '주장' : '부장') : '';")
s = rep(s, "        if (miss) talk(pa.adv, miss, msg, 3600); else toast(msg, 3200);", "        if (miss) talk(pa.adv, miss, msg, 3600, paRole); else toast(msg, 3200);")
s = rep(s, """(a.rec ? '<i class="rec" title="군사의 추천">薦</i>' : '')""", """(a.rec ? '<i class="rec" title="부장의 추천">薦</i>' : '')""")
s = rep(s, "가늠하는 이는 군사와 군주 가운데 지력이 높은 쪽입니다 — 그 지력이 ' + ODDS_FINE + ' 미만이면 <b>높은 듯 · 반반인 듯 · 낮은 듯</b> 셋으로만 어림합니다. 적을 고르면 뜨는 단추 가운데 <i class=\"rec\" style=\"position:static;display:inline-flex;transform:none\">薦</i>이 붙은 것은 <b>군사가 권하는 수</b>입니다(주는 피해에서 받는 반격을 뺀 기대값이 가장 큰 것 — 군사가 없으면 권하지 않습니다).",
        "가늠하는 이는 군사와 군주 가운데 지력이 높은 쪽입니다 — 그 지력이 ' + ODDS_FINE + ' 미만이면 <b>높은 듯 · 반반인 듯 · 낮은 듯</b> 셋으로만 어림합니다.</p><p><b>싸움터에서는 그 부대의 부장이 헤아립니다</b>(부장이 없으면 주장이 스스로). 부장의 <b>지력</b>이 높을수록 계략이 통할지(○ ×)를 잘 맞히고 가능성을 또렷이 보며, <b>통솔</b>이 높을수록 예상 피해를 정확히 내다보고(통솔 ' + STAFF.errAt + ' 이상이면 그대로 · 낮으면 \\'약 N\\'이 실제와 벌어집니다) 어느 수가 가장 나은지를 바르게 짚습니다. 적을 고르면 뜨는 단추 가운데 <i class=\"rec\" style=\"position:static;display:inline-flex;transform:none\">薦</i>이 붙은 것이 <b>부장이 권하는 수</b>입니다(주는 피해에서 받는 반격을 뺀 기대값이 가장 큰 것 — 헤아림이 모자란 부장은 가끔 다른 수를 권합니다).")
wr('src/ui_panels.js', s)

s = rd('src/style.css')
s = s.rstrip('\n') + """
/* v0.20 싸움터의 조언: 말하는 이의 자리(부장 · 주장) */
.say em.role { font: 700 10.5px var(--font-body); font-style: normal; color: var(--paper); background: var(--indigo); padding: 0 5px; border-radius: var(--rad-s); margin-right: 4px; vertical-align: 1px; }
"""
wr('src/style.css', s)
print('s6 ok')
