# v0.9.1 전법(1/2): 숫자를 한곳(data.js)으로 모은다 — 이 단계에서는 값이 0.9 와 같다(같은 씨앗의 AI 대전이 0.9 와 똑같이 흘러가는지로 확인).
#  core.js 안에 박혀 있던 것: 무장 항의 계수 0.6 과 범위 −24~+12, 대성공 배수 1.3(궁신·기신 1.43)
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var TACTIC_K = { okCounter: 0.4, failDmg: 0.5, failCounter: 0.7 };",
           "var TACTIC_K = { okCounter: 0.4, failDmg: 0.5, failCounter: 0.7, crit: 1.3, critGod: 1.43, stat: 0.6, statLo: -24, statHi: 12 };")
io.open(p, 'w', encoding='utf-8').write(s)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """  if (uHas(u, '신장') && uWar(u) > uWar(d)) return 1.3;
  if (u.type === 'spear' && (uHas(u, '창장') || uHas(u, '투신'))) return 1.3;
  if (u.type === 'halberd' && (uHas(u, '극장') || uHas(u, '투신'))) return 1.3;
  if (u.type === 'bow') { if (uHas(u, '궁신')) return 1.43; if (uHas(u, '궁장')) return 1.3; }
  if (u.type === 'cav') { if (uHas(u, '기신')) return 1.43; if (uHas(u, '기장')) return 1.3; }
  return 0;""", """  var c = TACTIC_K.crit, g = TACTIC_K.critGod;
  if (uHas(u, '신장') && uWar(u) > uWar(d)) return c;
  if (u.type === 'spear' && (uHas(u, '창장') || uHas(u, '투신'))) return c;
  if (u.type === 'halberd' && (uHas(u, '극장') || uHas(u, '투신'))) return c;
  if (u.type === 'bow') { if (uHas(u, '궁신')) return g; if (uHas(u, '궁장')) return c; }
  if (u.type === 'cav') { if (uHas(u, '기신')) return g; if (uHas(u, '기장')) return c; }
  return 0;""")
s = rep(s, "    stat: Math.round(clamp((pow - uLdr(d)) * 0.6, -24, 12)),", "    stat: Math.round(clamp((pow - uLdr(d)) * TACTIC_K.stat, TACTIC_K.statLo, TACTIC_K.statHi)),")
s = rep(s, "  return { ok: ok, crit: Math.min(cr, ok), mult: 1.3, sure: false, parts: P };", "  return { ok: ok, crit: Math.min(cr, ok), mult: TACTIC_K.crit, sure: false, parts: P };")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
