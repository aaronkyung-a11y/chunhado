# v0.8 전법 균형: "특기 공격이 너무 압도적으로 공격측에 유리 … 병사 수나 적장과 아군의 통솔, 무장의 적성에 비해 너무 강한 느낌 … 모든 사항을 고려해야" / "소속 무장들의 강력함이 영향을 크게 주어야"
#  재 본 것(v0.7, AI 대전 216턴): 보통 공격 평균 피해 543·반격 170(3.2:1), 전법 평균 피해 864·반격 73(11.8:1), 실패 18%.
#  식의 문제: 성공률이 상대를 안 봄 / 성공 시 반격 0.25(보통 0.55) / 병력이 내 쪽 제곱근으로만 들어가고 상대 병력은 안 들어감 / 특기가 있으면 무조건 성공+대성공
#  고침: ① 성공률 = 적성 + 무장(내 무력·통솔 − 적 통솔) + 병력 비 + 적 적성 + 지형·혼란   ② 피해에 병력 비   ③ 성공 시 반격 0.25→0.4, 실패 시 피해 0.6→0.5·반격 0.4→0.7
#        ④ 특기(창장·기장·신장…)는 '성공하면 반드시 대성공'으로(성공 자체는 확률대로, +5)
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var TACTIC_RATE = { C: 65, B: 72, A: 80, S: 88 };", """var TACTIC_RATE = { C: 55, B: 63, A: 71, S: 80 };   // 전법 성공률의 바탕(병과 적성). v0.7: 65/72/80/88 — 그때는 상대를 보지 않았다
var TACTIC_K = { okCounter: 0.4, failDmg: 0.5, failCounter: 0.7 };   // 성공했을 때 받는 반격 / 실패했을 때 주는 피해·받는 반격 (보통 공격의 반격은 0.55). v0.7: 0.25 / 0.6 / 0.4""")
for a, b in [("'신장': '무력이 낮은 적에게 통상 공격은 크리티컬, 전법은 반드시 대성공.'", "'신장': '무력이 낮은 적에게 통상 공격은 크리티컬, 전법은 성공하면 반드시 대성공(성공률 +5).'"),
             ("'투신': '창병·극병 전법이 반드시 대성공.'", "'투신': '창병·극병 전법이 성공하면 반드시 대성공(성공률 +5).'"),
             ("'창장': '창병 전법이 반드시 대성공.', '극장': '극병 전법이 반드시 대성공.', '궁장': '노병 전법이 반드시 대성공.', '기장': '기병 전법이 반드시 대성공.'", "'창장': '창병 전법이 성공하면 반드시 대성공(성공률 +5).', '극장': '극병 전법이 성공하면 반드시 대성공(성공률 +5).', '궁장': '노병 전법이 성공하면 반드시 대성공(성공률 +5).', '기장': '기병 전법이 성공하면 반드시 대성공(성공률 +5).'"),
             ("'기신': '기병 전법이 반드시 대성공이고 피해 +10%.', '궁신': '노병 전법이 반드시 대성공이고 피해 +10%.'", "'기신': '기병 전법이 성공하면 반드시 대성공이고 피해 +10%(성공률 +5).', '궁신': '노병 전법이 성공하면 반드시 대성공이고 피해 +10%(성공률 +5).'")]:
    s = rep(s, a, b)
# (v0.8.1에 바로잡음: 아래 ⑤의 '약 13%'는 틀린 셈이다 — 실제로 내린 폭은 전법마다 7~14%, 평균 9.7%)
# ⑤ 피해 배수를 약 13% 내린다 (AI 대전에서 재 보니 전법 한 번의 평균 피해 1,238 이 맞는 부대 평균 병력 2,700 의 46% — 두 번이면 궤멸)
for k, (a0, b0) in {'돌출': ('1.35', '1.25'), '나선첨': ('1.5', '1.35'), '이단첨': ('1.8', '1.55'), '갈퀴': ('1.35', '1.25'), '횡치': ('1.25', '1.15'), '선풍': ('1.15', '1.05'), '화시': ('1.2', '1.1'), '관시': ('1.45', '1.3'), '난사': ('1.15', '1.05'), '돌격': ('1.45', '1.3'), '돌파': ('1.5', '1.35'), '돌진': ('1.85', '1.6')}.items():
    i = s.index("name: '%s', cost: " % k); j = s.index('mult: ', i); e = j + 6 + len(a0)
    assert s[j + 6:e] == a0 and s[e] == ','
    s = s[:j + 6] + b0 + s[e:]
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
i0 = s.index("/* 전법의 성공·대성공 확률(%)."); i1 = s.index("/* 대성공이면 전법의 효과 자체가 세진다")
s = s[:i0] + """/* 전법의 성공·대성공 확률(%) — v0.8: 상대와 병력까지 본다. 대성공은 성공 안에 들어 있다.
   성공 = 적성(TACTIC_RATE)
        + 무장: (내 부대 최고 무력×0.6 + 내 주장 통솔×0.4 − 적 부대 최고 통솔) × 0.6      [−24 ~ +12]
        + 병력: log2(내 병력 ÷ 적 병력) × 8                                              [−16 ~ +8]   (절반이면 −8, 두 배면 +8)
        + 적의 병과 적성: C +3 · B 0 · A −3 · S −6
        + 적이 선 곳: 숲·구릉 −5, 강 +5   + 적이 혼란 중 +10   + 맞는 특기(창장·기장·신장…) +5
        → 10 ~ 95
   대성공 = 적성 + 무력 + (내 무력 − 상대 통솔). 맞는 특기가 있으면 성공한 전법은 모두 대성공 */
var TACTIC_CRIT = { C: 4, B: 8, A: 12, S: 18 };
function uLdr(u) { return bestOf(uMembers(u), 'ldr'); }
function tacticParts(u, d) {
  var pow = uWar(u) * 0.6 + uLeader(u).ldr * 0.4, td = terr(d.c, d.r);
  return { apt: TACTIC_RATE[uApt(u)],
    stat: Math.round(clamp((pow - uLdr(d)) * 0.6, -24, 12)),
    troops: Math.round(clamp(Math.log(Math.max(1, u.troops) / Math.max(1, d.troops)) / Math.LN2 * 8, -16, 8)),
    dapt: -3 * (APT_RANK[uApt(d)] - 1),
    terr: (td === 'f' || td === 'h') ? -5 : (td === 'w' ? 5 : 0),
    conf: d.status === 'confuse' ? 10 : 0,
    skill: tacticCrit(u, d) ? 5 : 0 };
}
function tacticOdds(u, d) {
  var forced = tacticCrit(u, d), P = tacticParts(u, d);
  var ok = Math.round(clamp(P.apt + P.stat + P.troops + P.dapt + P.terr + P.conf + P.skill, 10, 95));
  if (forced) return { ok: ok, crit: ok, mult: forced, sure: true, parts: P };
  var w = uWar(u);
  var cr = Math.round(clamp(TACTIC_CRIT[uApt(u)] + clamp((w - 70) * 0.5, -4, 15) + clamp((w - uLdr(d)) * 0.15, -6, 6), 2, 45));
  return { ok: ok, crit: Math.min(cr, ok), mult: 1.3, sure: false, parts: P };
}
/* 전법 피해에 얹는 병력 비: 큰 부대를 작은 부대가 전법 한 번으로 무너뜨리지 못한다(¼ 병력이면 ×0.75, 두 배 넘어도 ×1.1 까지) */
function tacticSizeK(u, d) { return clamp(Math.pow(Math.max(1, u.troops) / Math.max(1, d.troops), 0.25), 0.75, 1.1); }
""" + s[i1:]
s = rep(s, """  var od = tacticOdds(u, d), roll = od.sure ? 0 : rnd() * 100;
  res.pOk = od.ok; res.pCrit = od.crit;
  if (roll >= od.ok) {
    res.fail = true;
    var fdm = defMods(d, dmgUU(u, d, 0.6, ranged), 'normal');
    res.dmg = fdm; res.killed = hurtUnit(d, fdm, u.f, u);
    if (!res.killed && !ranged && d.status !== 'confuse') { var fc = defMods(u, dmgUU(d, u, 0.4, false), 'normal'); res.counter = fc; if (hurtUnit(u, fc, d.f, d)) res.selfDead = true; }
    return res;
  }
  var crit = roll < od.crit ? od.mult : 0, e = tacticEff(tac, !!crit);      // e = 이번에 적용되는 효과(대성공이면 강화된 것)
  res.crit = !!crit;
  var cm = crit || 1;
  var dmg = defMods(d, dmgUU(u, d, tac.mult * cm, ranged), 'tactic');""", """  var od = tacticOdds(u, d), roll = rnd() * 100;
  res.pOk = od.ok; res.pCrit = od.crit;
  if (roll >= od.ok) {                                         // 실패: 피해는 보통 공격의 절반, 반격은 보통 공격보다 크게 받는다(원거리는 노병에게만)
    res.fail = true;
    var fdm = defMods(d, dmgUU(u, d, TACTIC_K.failDmg, ranged), 'normal');
    res.dmg = fdm; res.killed = hurtUnit(d, fdm, u.f, u);
    if (!res.killed && d.status !== 'confuse' && d.status !== 'rumor' && (!ranged || d.type === 'bow')) {
      var fc = defMods(u, dmgUU(d, u, ranged ? 0.4 : (d.type === 'bow' ? TACTIC_K.failCounter * 0.6 : TACTIC_K.failCounter), ranged), 'normal');
      res.counter = fc; if (hurtUnit(u, fc, d.f, d)) res.selfDead = true;
    }
    return res;
  }
  var crit = roll < od.crit ? od.mult : 0, e = tacticEff(tac, !!crit);      // e = 이번에 적용되는 효과(대성공이면 강화된 것)
  res.crit = !!crit;
  var cm = crit || 1;
  var dmg = defMods(d, dmgUU(u, d, tac.mult * cm * tacticSizeK(u, d), ranged), 'tactic');""")
s = rep(s, "    var od = defMods(o2, dmgUU(u, o2, tac.mult * cm * others[i][1], hdist(u.c, u.r, o2.c, o2.r) > 1), 'tactic');",
           "    var od = defMods(o2, dmgUU(u, o2, tac.mult * cm * others[i][1] * tacticSizeK(u, o2), hdist(u.c, u.r, o2.c, o2.r) > 1), 'tactic');")
s = rep(s, "    var cd = defMods(u, dmgUU(d, u, 0.25, false), 'normal');\n    res.counter = cd;", "    var cd = defMods(u, dmgUU(d, u, d.type === 'bow' ? TACTIC_K.okCounter * 0.6 : TACTIC_K.okCounter, false), 'normal');\n    res.counter = cd;")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
