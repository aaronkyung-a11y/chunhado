# v0.8.1 초반 보호 — 손질
#  ① '플레이어가 먼저 쳤다'는 판정을 행동 '전'의 주인으로 잰다(성을 빼앗거나 시설을 부순 뒤에 재면 주인이 바뀌었거나 시설이 사라져 놓친다). 화계로 남의 시설이 있는 칸을 태우는 것도 '시설을 친 것'으로 본다
#  ② 치러 가던 거점의 주인이 '아직 칠 수 없는 세력'으로 바뀌면(빈 성을 다투다 남이 먼저 들어간 경우) 그 앞에 눌러앉지 않고 돌아간다
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """function actEv(u, t, res, f, name, ac, ar, tf) {
  if (res && res.ok && G.peace && f === G.player && t) {           // 플레이어가 남의 거점·시설을 먼저 치면 그 세력에 대한 보호가 풀린다
    var pf = (t.kind === 'base' || t.kind === 'fac') ? (t.b ? t.b.owner : -1) : (!t.u && plotAt(t.c, t.r) && plotAt(t.c, t.r).plot.fac ? plotAt(t.c, t.r).base.owner : -1);
    if (pf >= 0 && pf !== f && !G.peace.broken[pf]) { G.peace.broken[pf] = true; if (G.turn < G.peace.until) res.brokePeace = pf; }
  }
""", """/* 이 행동이 건드리는 거점·시설의 주인(없으면 -1) — 행동 '전'에 잰다. 화계는 그 칸에 남의 시설이 있으면 시설을 친 것으로 본다 */
function actHoldF(t, ploy) {
  if (!t) return -1;
  if (t.kind === 'base' || t.kind === 'fac') return t.b ? t.b.owner : -1;
  if (ploy && ploy.id === 'fire') { var p = PAT[K(t.c, t.r)]; if (p && G.bases[p.b].plots[p.i].fac) return G.bases[p.b].owner; }
  return -1;
}
function actEv(u, t, res, f, name, ac, ar, tf, hf) {
  if (res && res.ok && G.peace && f === G.player && hf !== undefined && hf >= 0 && hf !== f && !G.peace.broken[hf]) {   // 플레이어가 남의 거점·시설을 먼저 치면 그 세력에 대한 보호가 풀린다
    G.peace.broken[hf] = true;
    if (G.turn < G.peace.until) res.brokePeace = hf;               // 보호 기간 안에 깼을 때만 화면에 알린다
  }
""")
s = rep(s, "function unitAttack(u, t) { var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t); return actEv(u, t, unitAttack0(u, t), f, n, ac, ar, tf); }",
           "function unitAttack(u, t) { var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t), hf = actHoldF(t, null); return actEv(u, t, unitAttack0(u, t), f, n, ac, ar, tf, hf); }")
s = rep(s, "function unitTactic(u, tac, t) { var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t); return actEv(u, t, unitTactic0(u, tac, t), f, n, ac, ar, tf); }",
           "function unitTactic(u, tac, t) { var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t); return actEv(u, t, unitTactic0(u, tac, t), f, n, ac, ar, tf, -1); }")
s = rep(s, "function unitPloy(u, ploy, t) { var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t); return actEv(u, t, unitPloy0(u, ploy, t), f, n, ac, ar, tf); }",
           "function unitPloy(u, ploy, t) { var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t), hf = actHoldF(t, ploy); return actEv(u, t, unitPloy0(u, ploy, t), f, n, ac, ar, tf, hf); }")
# 낡은 주석(성역에서 멈추던 때의 설명)
s = rep(s, """/* 성역(城域): 성 둘레 ZONE_R 칸. 값 = 그 성의 번호, 성역 밖은 -1. 관문에는 성역이 없다.
   성역의 경계를 넘는 걸음(들어가든 나오든)을 디디면 그 턴의 이동은 거기서 끝난다 →
   성에서 나와(1턴째에 경계 밖에서 멈춤) 다른 성의 성역에 들어서고(멈춤) 성에 닿기까지 적어도 3턴(30일)이 걸린다. */""",
"""/* 성역(城域): 성 둘레 ZONE_R 칸. 값 = 그 성의 번호, 성역 밖은 -1. 관문에는 성역이 없다.
   v0.8부터 이동을 막지 않는다(0.5~0.7에서는 경계를 넘으면 그 턴 이동이 끝났다) — 이름·고리 표시·긴장한 음악의 기준으로만 쓴다. */""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "  if (mode === 'attack') { if (!T) mode = 'return'; else if (T.owner === f) mode = 'garrison'; }",
           "  if (mode === 'attack') { if (!T) mode = 'return'; else if (T.owner === f) mode = 'garrison'; else if (T.owner >= 0 && !aiMayStrike(f, T.owner)) ai.mode = mode = 'return'; }   // 아직 칠 수 없는 세력이 먼저 들어간 성: 그 앞에 눌러앉지 않고 돌아간다")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
