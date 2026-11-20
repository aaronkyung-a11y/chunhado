# v0.8.1 손질
#  ① 보호 중에는 AI 가 플레이어의 시설 위에 화계를 놓지도 않는다(시설이 300 깎이므로 '시설을 친 것'과 같다)
#  ② 완충 기간 풀이를 규칙 그대로: "2배를 넘게 모아야 출진" → "출진에 필요한 병력 우위가 평소의 1.25배 대신 2배에서 시작해 차츰 내려온다"
#     (실제 조건은 '한 성에서 낼 수 있는 병력 ≥ 수비 × 배수 + 2,500'이고, 세력 전체가 압도적으로 크면 그보다 적어도 출진하는 길이 따로 있다 — 그 문턱도 같은 비율로 올라간다)
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """      for (i = 0; i < pts.length; i++) if (pts[i].u === tg) pt = pts[i];
      if (pt && ployChance(u, pl, tg) >= 55) { aiReport(u, unitPloy(u, pl, pt), tg); return; }""",
"""      for (i = 0; i < pts.length; i++) if (pts[i].u === tg) pt = pts[i];
      if (pt && pl.id === 'fire') { var hf = actHoldF(pt, pl); if (hf >= 0 && hf !== f && !aiMayStrike(f, hf)) pt = null; }   // 초반 보호: 남의 시설 위에는 불을 놓지 않는다
      if (pt && ployChance(u, pl, tg) >= 55) { aiReport(u, unitPloy(u, pl, pt), tg); return; }""")
io.open(p, 'w', encoding='utf-8').write(s)
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "<b>완충 기간</b>입니다 — 한 번에 한 세력만 우리를 치러 오고, 우리 수비 병력의 2배(차츰 1.25배로 내려옴)를 넘게 모아야 출진합니다.</li></ul></div>';",
           "<b>완충 기간</b>입니다 — 한 번에 한 세력만 우리를 치러 오고, 출진에 필요한 병력 우위가 평소의 1.25배 대신 <b>2배에서 시작해 차츰 내려옵니다</b>.</li></ul></div>';")
s = rep(s, "완충 기간입니다 — 한 번에 한 세력만 우리를 치러 오고, 우리 수비 병력의 2배(차츰 1.25배로)를 넘게 모아야 출진합니다.</li>",
           "완충 기간입니다 — 한 번에 한 세력만 우리를 치러 오고, 출진에 필요한 병력 우위가 평소의 1.25배 대신 2배에서 시작해 차츰 내려옵니다.</li>")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
