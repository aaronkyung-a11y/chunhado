# v0.9 손질 — 다른 세력 무장의 마음은 '한 달' 단위로 정한다 + 떠나면 남은 무장이 마음을 다잡는다
#  p1 대로면(대상의 주사위가 턴마다 새로 정해짐) 적중률 100%인 군사를 둔 쪽은 턴마다 공짜로 물어보고 '응하는 턴'에만 권하면 된다:
#  거절이 없으니 '3턴 기다림'도 '거절하면 충성 +3'도 걸리지 않고, 성공률 30%인 대상은 넉 턴 안에 76%가 넘어온다.
#  (조조로 시작하면 첫 턴에 여포의 무장 8명이 19~36% — 넉 턴이면 대부분 빼 올 수 있었다)
#  ① 다른 세력 무장의 주사위는 달마다 한 번 정해진다(그 달에는 누가 몇 번을 물어도 같다) → 성공률은 '한 달에 응할 확률'이 된다. 권하는 것도 한 달에 한 번.
#  ② 무장이 다른 세력으로 떠나면 그 세력에 남은 무장들의 충성이 POACH.tighten(2)씩 오른다(주군의 단속) → 한 세력에서 계속 빼 가기는 점점 어려워진다.
#  재야·포로(내 거점 안)는 그대로 턴마다, 한 턴에 한 번.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """   wait = 한 번 권한 뒤 다시 권할 수 있을 때까지의 턴 수, up = 거절한 무장의 충성이 오르는 폭 */
var POACH = { base: 15, cha: 0.5, pol: 0.2, lord: 0.25, loy0: 70, loyK: 2.5, talker: 20, bond: 30, max: 85, wall: 95, wait: 3, up: 3 };""",
"""   이 성공률은 '그 달에 응할 확률'이다 — 다른 세력 무장의 마음은 달마다 한 번 정해지고, 한 무장에게는 한 달에 한 번만 권할 수 있다.
   up = 거절한 무장의 충성이 오르는 폭, tighten = 무장이 떠났을 때 그 세력에 남은 무장들의 충성이 오르는 폭(주군의 단속) */
var POACH = { base: 15, cha: 0.5, pol: 0.2, lord: 0.25, loy0: 70, loyK: 2.5, talker: 20, bond: 30, max: 85, wall: 95, up: 3, tighten: 2 };""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
old = s[s.index("function strHash(s) {"):s.index("/* ---------- 초반 보호 ----------")] if False else None
s = rep(s, """function omenRoll(key) {                                           // 0 이상 100 미만
  var t = (G.seed0 | 0) ^ Math.imul((G.turn | 0) + 0x7F4A7C15, 0x9E3779B1) ^ strHash(key);
  t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); t = Math.imul(t ^ (t >>> 13), 0x5bd1e995 | 1);
  return ((t ^ (t >>> 15)) >>> 0) / 4294967296 * 100;
}
function recruitKey(t) { return 'r' + t.id; }                       // 등용: 대상에만 건다
function ployKey(ploy, t) { return 'p' + ploy.id + (t.u ? 'u' + t.u.id : 'k' + K(t.c, t.r)); }   // 계략: 종류 + 대상 부대(부대가 없으면 칸)""",
"""function omenRoll(key, monthly) {                                  // 0 이상 100 미만. monthly = 턴이 아니라 달마다 한 번 정해지는 것(그 달에는 같다)
  var e = monthly ? 0x40000 + G.year * 12 + G.month : (G.turn | 0);
  var t = (G.seed0 | 0) ^ Math.imul(e + 0x7F4A7C15, 0x9E3779B1) ^ strHash(key);
  t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); t = Math.imul(t ^ (t >>> 13), 0x5bd1e995 | 1);
  return ((t ^ (t >>> 15)) >>> 0) / 4294967296 * 100;
}
/* 등용의 주사위: 대상에만 건다. 재야·포로는 턴마다, 다른 세력의 무장(st 'active')은 달마다 한 번 */
function recruitRoll(t) { return omenRoll('r' + t.id, t.st === 'active'); }
function recruitRollA(t) { return omenRoll('a|r' + t.id, t.st === 'active'); }            // 군사의 조언이 맞는가
function ployKey(ploy, t) { return 'p' + ploy.id + (t.u ? 'u' + t.u.id : 'k' + K(t.c, t.r)); }   // 계략: 종류 + 대상 부대(부대가 없으면 칸). 턴마다
function ployRoll(ploy, t) { return omenRoll(ployKey(ploy, t)); }
function ployRollA(ploy, t) { return omenRoll('a|' + ployKey(ploy, t)); }""")
s = rep(s, """/* 조언: { adv, acc, says } — says = "통한다"고 말하는가. 군사가 없으면 null.
   실제 결과(omenRoll(key) < p)를 acc% 의 확률로 바르게, 나머지는 거꾸로 말한다. '맞는가'도 대상에만 걸려 있어, 군사를 바꿔 물어도 새 정보가 생기지 않는다 */
function advise(f, key, p, tInt) {
  var A = facAdv(f); if (!A) return null;
  var real = omenRoll(key) < p, acc = adviceAcc(A, tInt);
  return { adv: A, acc: acc, says: (omenRoll('a|' + key) < acc) ? real : !real };
}""", """/* 조언: { adv, acc, says } — says = "통한다"고 말하는가. 군사가 없으면 null.
   roll = 그 일의 주사위(recruitRoll·ployRoll), rollA = '조언이 맞는가'의 주사위(recruitRollA·ployRollA), p = 성공률, tInt = 상대의 지력.
   실제 결과(roll < p)를 acc% 의 확률로 바르게, 나머지는 거꾸로 말한다. '맞는가'도 대상에만 걸려 있어, 군사를 바꿔 물어도 새 정보가 생기지 않는다 */
function advise(f, roll, rollA, p, tInt) {
  var A = facAdv(f); if (!A) return null;
  var real = roll < p, acc = adviceAcc(A, tInt);
  return { adv: A, acc: acc, says: rollA < acc ? real : !real };
}""")
s = rep(s, "/* 등용을 권한 뒤 다시 권할 수 있는 턴(그 전에는 못 권한다). 재야·포로는 한 턴에 한 번, 다른 세력의 무장은 POACH.wait 턴에 한 번 */",
           "/* 등용을 권한 뒤 다시 권할 수 있을 때까지 남은 턴(0 이면 권할 수 있다). 재야·포로는 한 턴에 한 번, 다른 세력의 무장은 한 달에 한 번(다음 달 상순부터 다시) */")
s = rep(s, "  if (askWait(t)) return ERR(far ? '얼마 전에 권했습니다 — ' + askWait(t) + '턴 뒤에 다시 권할 수 있습니다' : '이번 턴에는 이미 권했습니다 — 다음 턴에 다시');",
           "  if (askWait(t)) return ERR(far ? '이번 달에는 이미 권했습니다 — 다음 달에 다시 권할 수 있습니다' : '이번 턴에는 이미 권했습니다 — 다음 턴에 다시');")
s = rep(s, """  var p = recruitChance(b, o, t), okR = omenRoll(recruitKey(t)) < p;    // 미리 정해 둔 결과(군사가 미리 말해 줄 수 있다)
  t.ask = G.turn + (far ? POACH.wait : 1);""", """  var p = recruitChance(b, o, t), okR = recruitRoll(t) < p;             // 미리 정해 둔 결과(군사가 미리 말해 줄 수 있다)
  t.ask = G.turn + (far ? 3 - G.xun : 1);                               // 다른 세력의 무장: 다음 달 상순부터 다시""")
s = rep(s, """    if (far) { t.job = null; t.loc = b.id; if (G.factions[from].adv === t.id) G.factions[from].adv = -1; }      // 맡던 공사·군사 자리를 두고 이쪽으로 넘어온다""",
"""    if (far) {                                                          // 맡던 공사·군사 자리를 두고 이쪽으로 넘어온다
      t.job = null; t.loc = b.id; if (G.factions[from].adv === t.id) G.factions[from].adv = -1;
      for (var qi = 0; qi < G.officers.length; qi++) { var q = G.officers[qi]; if (q.f === from && q !== t && (q.st === 'active' || q.st === 'travel') && G.factions[from].lord !== q.id && q.loy < 100) q.loy = Math.min(100, q.loy + POACH.tighten); }   // 남은 무장들이 마음을 다잡는다(주군의 단속)
    }""")
s = rep(s, """      if (from === G.player && !G.aiOnly) ev({ t: 'news', f: b.owner, c: fb.c, r: fb.r, warn: 1, text: '<b>' + fb.n + '의 ' + josa(t.n, '이가') + ' ' + facName(b.owner) + '군의 등용에 응해 떠났습니다</b>' });""",
"""      if (from === G.player && !G.aiOnly) ev({ t: 'news', f: b.owner, c: fb.c, r: fb.r, warn: 1, text: '<b>' + fb.n + '의 ' + josa(t.n, '이가') + ' ' + facName(b.owner) + '군의 등용에 응해 떠났습니다</b> — 남은 무장들의 충성 +' + POACH.tighten });""")
s = rep(s, "  if (omenRoll(ployKey(ploy, t)) < p) {                                 // v0.9: 미리 정해 둔 결과(같은 턴·같은 계략·같은 대상이면 같다)",
           "  if (ployRoll(ploy, t) < p) {                                          // v0.9: 미리 정해 둔 결과(같은 턴·같은 계략·같은 대상이면 같다)")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "function recruitAdvice(b, o, t) { return advise(G.player, recruitKey(t), recruitChance(b, o, t), t.int); }",
           "function recruitAdvice(b, o, t) { return advise(G.player, recruitRoll(t), recruitRollA(t), recruitChance(b, o, t), t.int); }")
s = rep(s, "function ployAdvice(u, pl, t) { return advise(G.player, ployKey(pl, t), ployChance(u, pl, t.u || null), t.u ? uInt(t.u) : 0); }",
           "function ployAdvice(u, pl, t) { return advise(G.player, ployRoll(pl, t), ployRollA(pl, t), ployChance(u, pl, t.u || null), t.u ? uInt(t.u) : 0); }")
s = rep(s, "    if (askWait(t)) return t.st === 'active' ? askWait(t) + '턴 뒤에 다시' : '다음 턴에 다시';",
           "    if (askWait(t)) return t.st === 'active' ? '다음 달에 다시' : '다음 턴에 다시';")
s = rep(s, "        h += '</div><p class=\"note\">한 번 권하면 ' + POACH.wait + '턴 뒤에 다시 권할 수 있고, 거절한 무장은 충성이 ' + POACH.up + ' 오릅니다. 제 주군과 인연이 있거나 충성이 ' + POACH.wall + ' 이상이면 응하지 않습니다. 출진 중인 무장과 군주에게는 권할 수 없습니다.</p>';",
           "        h += '</div><p class=\"note\">성공률은 <b>그 달에 응할 확률</b>입니다 — 마음은 달마다 바뀌고, 한 무장에게는 한 달에 한 번 권할 수 있습니다. 거절한 무장은 충성이 ' + POACH.up + ' 오르고, 한 사람이 넘어오면 그 세력에 남은 무장들의 충성이 ' + POACH.tighten + '씩 오릅니다. 제 주군과 인연이 있거나 충성이 ' + POACH.wall + ' 이상이면 응하지 않습니다. 출진 중인 무장과 군주에게는 권할 수 없습니다.</p>';")
s = rep(s, "(r.far ? ' — ' + POACH.wait + '턴 뒤에 다시 권할 수 있습니다 (충성 +' + POACH.up + ')' : ' — 다음 턴에 다시 권할 수 있습니다')",
           "(r.far ? ' — 다음 달에 다시 권할 수 있습니다 (충성 +' + POACH.up + ')' : ' — 다음 턴에 다시 권할 수 있습니다')")
s = rep(s, "제 주군과 인연이 있거나 충성이 ' + POACH.wall + ' 이상이면 응하지 않고, 군주와 출진 중인 무장에게는 권할 수 없습니다. 한 번 권하면 ' + POACH.wait + '턴 뒤에 다시 권할 수 있고, 거절한 무장은 충성이 ' + POACH.up + ' 오릅니다.</p>' +",
           "제 주군과 인연이 있거나 충성이 ' + POACH.wall + ' 이상이면 응하지 않고, 군주와 출진 중인 무장에게는 권할 수 없습니다. 성공률은 <b>그 달에 응할 확률</b>입니다 — 다른 세력 무장의 마음은 달마다 한 번 정해지고, 한 무장에게는 한 달에 한 번 권할 수 있습니다. 거절한 무장은 충성이 ' + POACH.up + ' 오르고, 한 사람이 넘어가면 그 세력에 남은 무장들의 충성이 ' + POACH.tighten + '씩 오릅니다.</p>' +")
s = rep(s, "  '<p>등용과 계략의 성패는 그 턴에 <b>대상마다 미리 정해져 있습니다</b>. 그래서 같은 턴에는 누구에게 다시 물어도 답이 같고, 가장 잘하는 무장이 안 되면 그 턴에는 누구도 안 됩니다.",
           "  '<p>등용과 계략의 성패는 <b>대상마다 미리 정해져 있습니다</b>(계략과 재야·포로 등용은 턴마다, 다른 세력 무장의 등용은 달마다). 그래서 그동안에는 누구에게 다시 물어도 답이 같고, 가장 잘하는 무장이 안 되면 누구도 안 됩니다.")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
