# v0.7 전법 보강: 누구나 능력치에 따라 대성공, 대성공이면 효과 자체가 세짐, 혼란은 상대 지력·통솔에 따라
import io, sys
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:70])
    return s.replace(a, b)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()

s = rep(s, """function tacticTargets(u, tac) {""", """/* 전법의 성공·대성공 확률(%). 대성공은 성공 안에 들어 있다(성공 80·대성공 15 → 실패 20, 보통 성공 65, 대성공 15).
   - 성공: 병과 적성 + 무력
   - 대성공: 병과 적성 + 무력 + (내 무력 − 상대 통솔). 특기(창장·기장·신장…)가 맞으면 반드시 대성공 */
var TACTIC_CRIT = { C: 4, B: 8, A: 12, S: 18 };
function uLdr(u) { return bestOf(uMembers(u), 'ldr'); }
function tacticOdds(u, d) {
  var forced = tacticCrit(u, d);
  if (forced) return { ok: 100, crit: 100, mult: forced, sure: true };
  var w = uWar(u), ok = Math.round(TACTIC_RATE[uApt(u)] + clamp((w - 70) / 3, -5, 8));
  var cr = Math.round(clamp(TACTIC_CRIT[uApt(u)] + clamp((w - 70) * 0.5, -4, 15) + clamp((w - uLdr(d)) * 0.15, -6, 6), 2, 45));
  return { ok: ok, crit: Math.min(cr, ok), mult: 1.3, sure: false };
}
/* 대성공이면 전법의 효과 자체가 세진다(TACTICS 의 great 가 덮어쓴다) */
function tacticEff(tac, crit) {
  if (!crit || !tac.great) return tac;
  var o = {}, k;
  for (k in tac) o[k] = tac[k];
  for (k in tac.great) o[k] = tac.great[k];
  return o;
}
/* 전법으로 혼란시킬 확률(%): 맞는 쪽의 지력·통솔이 높을수록 낮다. confuse 가 1 이상이면 반드시 */
function confuseOdds(e, d) {
  if (!e.confuse) return 0;
  if (e.confuse >= 1) return 100;
  return Math.round(clamp(e.confuse * 100 + (70 - (uInt(d) + uLdr(d)) / 2) * 0.6, 5, 95));
}
function tacticTargets(u, tac) {""")

s = rep(s, """  var crit = tacticCrit(u, d);
  var rate = TACTIC_RATE[uApt(u)] + clamp((uWar(u) - 70) / 3, -5, 8);
  if (!crit && !chance(rate)) {
    res.fail = true;""", """  var od = tacticOdds(u, d), roll = od.sure ? 0 : rnd() * 100;
  res.pOk = od.ok; res.pCrit = od.crit;
  if (roll >= od.ok) {
    res.fail = true;""")

s = rep(s, """  res.crit = !!crit;
  var cm = crit || 1;
  var dmg = defMods(d, dmgUU(u, d, tac.mult * cm, ranged), 'tactic');""", """  var crit = roll < od.crit ? od.mult : 0, e = tacticEff(tac, !!crit);      // e = 이번에 적용되는 효과(대성공이면 강화된 것)
  res.crit = !!crit;
  var cm = crit || 1;
  var dmg = defMods(d, dmgUU(u, d, tac.mult * cm, ranged), 'tactic');""")

s = rep(s, """  if (tac.arc) { ns = nbrs(u.c, u.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d && hdist(q.c, q.r, d.c, d.r) === 1) others.push([q, 0.8]); } }""",
"""  if (tac.arc) { ns = nbrs(u.c, u.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d && hdist(q.c, q.r, d.c, d.r) === 1) others.push([q, e.side || 0.8]); } }""")
s = rep(s, """if (q && q.f !== u.f) others.push([q, 0.8]); } }""", """if (q && q.f !== u.f) others.push([q, e.side || 0.8]); } }""")
s = rep(s, """if (q && q.f !== u.f && q !== d) others.push([q, 0.6]); } }""", """if (q && q.f !== u.f && q !== d) others.push([q, e.side || 0.6]); } }""")

s = rep(s, """  if (tac.push && !ranged) {
    for (i = 0; i < tac.push; i++) {""", """  if (e.push && !ranged) {
    for (i = 0; i < e.push; i++) {""")

s = rep(s, """  if (!dead) {
    if (tac.moraleDmg) d.morale = Math.max(0, d.morale - tac.moraleDmg);
    if (tac.confuse && chance(tac.confuse * 100 + (crit ? 20 : 0))) { setStatus(d, 'confuse', 1); res.confused = true; }
  }
  if (tac.fire) { if (setFire(oc, or_, 2)) res.fire = true; }""", """  if (!dead) {
    if (e.moraleDmg) { var md = Math.min(d.morale, e.moraleDmg); d.morale -= md; if (md) res.mor = md; }
    var cp = confuseOdds(e, d);
    if (cp) { res.pConf = cp; if (cp >= 100 || chance(cp)) { setStatus(d, 'confuse', 1); res.confused = true; } }
  }
  if (tac.fire) { if (setFire(oc, or_, e.fireT || 2)) res.fire = true; }""")

s = rep(s, """    res.extra.push({ c: o2.c, r: o2.r, dmg: od });
    hurtUnit(o2, od, u.f, u); afterHit(u, o2, od);""", """    var ex = { c: o2.c, r: o2.r, dmg: od };
    res.extra.push(ex);
    var dead2 = hurtUnit(o2, od, u.f, u); afterHit(u, o2, od);
    if (!dead2 && e.moraleAll) { var m2 = Math.min(o2.morale, e.moraleAll); o2.morale -= m2; if (m2) ex.mor = m2; }""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
a = s.index('var TACTICS = {'); b = s.index('var TACTIC_RATE')
new = """var TACTICS = {
  /* great = 대성공일 때 덮어쓰는 효과. fx·gfx = 창에 보여 주는 풀이(성공일 때 / 대성공일 때 더해지는 것) */
  spear: [
    { id: 'dolchul', name: '돌출', cost: 10, mult: 1.35, push: 1, need: 'C', great: { push: 2 }, fx: '적을 한 칸 밀어낸다. 뒤가 막혀 있으면 피해 +20%', gfx: '두 칸 밀어낸다', desc: '적을 한 칸 밀어낸다. 뒤가 막혀 있으면 추가 피해. 대성공이면 두 칸.' },
    { id: 'naseon',  name: '나선첨', cost: 15, mult: 1.5, confuse: 0.35, need: 'B', great: { confuse: 1 }, fx: '적을 혼란에 빠뜨린다(1턴)', gfx: '반드시 혼란', desc: '적을 혼란에 빠뜨린다(기본 35%, 상대의 지력·통솔이 높으면 낮아진다). 대성공이면 반드시.' },
    { id: 'idan',    name: '이단첨', cost: 20, mult: 1.8, moraleDmg: 15, need: 'A', great: { moraleDmg: 30 }, fx: '적 기력 -15', gfx: '적 기력 -30', desc: '큰 피해를 주고 적 기력을 15 깎는다. 대성공이면 30.' }
  ],
  halberd: [
    { id: 'galkwi',   name: '갈퀴', cost: 10, mult: 1.35, noCounter: true, need: 'C', great: { moraleDmg: 15 }, fx: '반격을 받지 않는다', gfx: '적 기력 -15', desc: '적을 걸어 넘어뜨린다. 반격을 받지 않는다. 대성공이면 적 기력 -15.' },
    { id: 'hoengchi', name: '횡치', cost: 15, mult: 1.25, arc: true, need: 'B', great: { side: 1 }, fx: '양옆의 적에게도 피해 80%', gfx: '양옆의 적에게도 피해 100%', desc: '정면의 적과 그 양옆의 적까지 벤다(양옆 80%). 대성공이면 양옆도 100%.' },
    { id: 'seonpung', name: '선풍', cost: 20, mult: 1.15, all: true, need: 'A', great: { moraleDmg: 10, moraleAll: 10 }, fx: '주위의 모든 적을 공격한다', gfx: '맞은 적 모두 기력 -10', desc: '주위의 모든 적을 공격한다. 대성공이면 맞은 적 모두 기력 -10.' }
  ],
  bow: [
    { id: 'hwasi',  name: '화시', cost: 10, mult: 1.2, fire: true, need: 'C', great: { fireT: 3, moraleDmg: 10 }, fx: '적이 선 칸에 불(2턴)', gfx: '불이 3턴 타고 적 기력 -10', desc: '불화살. 적이 선 칸에 불을 붙인다(2턴). 대성공이면 3턴 타고 적 기력 -10.' },
    { id: 'gwansi', name: '관시', cost: 15, mult: 1.45, pierce: true, need: 'B', great: { side: 1 }, fx: '뒤의 적에게도 피해 80%', gfx: '뒤의 적에게도 피해 100%', desc: '대상과 그 뒤의 적까지 꿰뚫는다(뒤 80%). 대성공이면 뒤도 100%.' },
    { id: 'nansa',  name: '난사', cost: 20, mult: 1.15, splash: true, need: 'A', great: { side: 0.8 }, fx: '주위의 적에게도 피해 60%', gfx: '주위의 적에게도 피해 80%', desc: '대상과 그 주위의 적을 함께 공격한다(주위 60%). 대성공이면 주위 80%.' }
  ],
  cav: [
    { id: 'dolgyeok', name: '돌격', cost: 10, mult: 1.45, push: 1, follow: true, need: 'C', noForest: true, great: { push: 2 }, fx: '적을 한 칸 밀어내고 그 자리로 전진', gfx: '두 칸 밀어내며 전진', desc: '적을 밀어내고 그 자리로 전진한다. 대성공이면 두 칸.' },
    { id: 'dolpa',    name: '돌파', cost: 15, mult: 1.5, pass: true, noCounter: true, need: 'B', noForest: true, great: { moraleDmg: 15 }, fx: '적을 뚫고 반대편으로. 반격을 받지 않는다', gfx: '적 기력 -15', desc: '적을 뚫고 반대편으로 빠져나간다. 반격을 받지 않는다. 대성공이면 적 기력 -15.' },
    { id: 'doljin',   name: '돌진', cost: 20, mult: 1.85, push: 2, follow: true, confuse: 0.2, need: 'A', noForest: true, great: { confuse: 0.5 }, fx: '두 칸 밀어내며 전진. 혼란(기본 20%)', gfx: '혼란 확률이 기본 50%로', desc: '적을 두 칸 밀어내며 큰 피해. 혼란(기본 20%, 상대의 지력·통솔이 높으면 낮아진다). 대성공이면 기본 50%.' }
  ]
};
"""
s = s[:a] + new + s[b:]
s = rep(s, "var GAME_VERSION = 'v0.6';", "var GAME_VERSION = 'v0.7';")
s = rep(s, "'신장': '무력이 낮은 적에게 통상 공격·전법이 모두 크리티컬.',", "'신장': '무력이 낮은 적에게 통상 공격은 크리티컬, 전법은 반드시 대성공.',")
s = rep(s, "'투신': '창병·극병 전법이 크리티컬.',", "'투신': '창병·극병 전법이 반드시 대성공.',")
s = rep(s, "'창장': '창병 전법이 크리티컬.', '극장': '극병 전법이 크리티컬.', '궁장': '노병 전법이 크리티컬.', '기장': '기병 전법이 크리티컬.',", "'창장': '창병 전법이 반드시 대성공.', '극장': '극병 전법이 반드시 대성공.', '궁장': '노병 전법이 반드시 대성공.', '기장': '기병 전법이 반드시 대성공.',")
s = rep(s, "'기신': '기병 전법이 크리티컬이고 피해 +10%.', '궁신': '노병 전법이 크리티컬이고 피해 +10%.',", "'기신': '기병 전법이 반드시 대성공이고 피해 +10%.', '궁신': '노병 전법이 반드시 대성공이고 피해 +10%.',")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
