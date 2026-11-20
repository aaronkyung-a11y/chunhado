# v0.8 전법 균형 — AI 와 화면
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """      var m = tl[i].mult + (tl[i].all || tl[i].splash || tl[i].arc ? 0.2 : 0);
      if (m > bm) { bm = m; bt = tl[i]; }
    }
    if (bt && chance(75)) { aiReport(u, unitTactic(u, bt, tgt), tg); return; }""", """      // 기대 피해(보통 공격 = 1): 성공률 × 배수 × 병력 비 × 대성공 몫 + 실패했을 때의 피해. 여럿을 치는 전법은 조금 더 쳐 준다
      var od0 = tacticOdds(u, tg), p0 = od0.ok / 100;
      var m = p0 * tl[i].mult * tacticSizeK(u, tg) * (1 + (od0.mult - 1) * od0.crit / Math.max(1, od0.ok)) + (1 - p0) * TACTIC_K.failDmg + (tl[i].all || tl[i].splash || tl[i].arc ? 0.2 * p0 : 0);
      if (m > bm) { bm = m; bt = tl[i]; }
    }
    if (bt && bm >= 1.1 && chance(85)) { aiReport(u, unitTactic(u, bt, tgt), tg); return; }      // 보통 공격보다 나을 때만 쓴다(v0.7: 가장 센 전법을 75% 확률로 무조건)""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "'기력 ' + tac.cost + ' · ' + (od.sure ? '필중' : od.ok + '%') + '<br>대성공 ' + (od.sure ? '확정' : od.crit + '%')", "'기력 ' + tac.cost + ' · ' + od.ok + '%' + '<br>대성공 ' + od.crit + '%'")
i0 = s.index("      var all = TACTICS[u.type] || [], can = tacticList(u), od = tacticOdds(u, d), i;"); i1 = s.index("      for (i = 0; i < all.length; i++) {\n        var tac = all[i], have = can.indexOf(tac) >= 0, c0 = confuseOdds(tac, d)")
s = s[:i0] + """      var all = TACTICS[u.type] || [], can = tacticList(u), od = tacticOdds(u, d), P = od.parts, i;
      function sg(v) { return (v > 0 ? '+' : '') + v; }
      var h = dlgHead('전법 풀이') + '<div class="dlg-b"><div class="tacs">' +
        '<p class="who"><b>' + uName(u) + '</b> <span>' + UNIT_TYPES[u.type].name + ' 적성 ' + uApt(u) + ' · 무력 ' + uWar(u) + ' · 통솔 ' + uLeader(u).ldr + ' · ' + fmt(u.troops) + '명</span><br>→ <b>' + uName(d) + '</b> <span>' + UNIT_TYPES[d.type].name + ' 적성 ' + uApt(d) + ' · 통솔 ' + uLdr(d) + ' · 지력 ' + uInt(d) + ' · ' + fmt(d.troops) + '명</span></p>' +
        '<div class="odds"><span class="g"><i>대성공</i><b>' + od.crit + '%</b></span><span><i>성공</i><b>' + (od.ok - od.crit) + '%</b></span><span class="f"><i>실패</i><b>' + (100 - od.ok) + '%</b></span></div>' +
        '<p class="sum">성공률 ' + od.ok + '% = 적성 ' + P.apt + ' · 무장 ' + sg(P.stat) + ' · 병력 ' + sg(P.troops) + ' · 상대 적성 ' + sg(P.dapt) + (P.terr ? ' · 지형 ' + sg(P.terr) : '') + (P.conf ? ' · 혼란 ' + sg(P.conf) : '') + (P.skill ? ' · 특기 ' + sg(P.skill) : '') + '</p>';
""" + s[i1:]
s = rep(s, """      h += '<p class="note"><b>실패</b>하면 피해가 통상 공격의 60%로 줄고 효과가 없으며, 반격을 더 크게 받습니다. 기력은 그대로 씁니다.</p>' +
        '<p class="note">성공률은 <b>병과 적성과 무력</b>으로 정해집니다. 대성공률은 여기에 <b>내 무력과 상대 통솔의 차이</b>가 더해집니다. 혼란은 상대의 <b>지력·통솔</b>이 높을수록 덜 걸립니다. 창장·극장·궁장·기장 같은 특기가 맞으면 반드시 대성공입니다.</p>';""",
"""      h += '<p class="note"><b>성공</b>해도 반격은 받습니다(통상 공격 때의 ' + Math.round(TACTIC_K.okCounter / 0.55 * 100) + '%). <b>실패</b>하면 피해가 통상 공격의 ' + Math.round(TACTIC_K.failDmg * 100) + '%로 줄고 효과가 없으며, 반격을 통상 공격보다 크게(' + Math.round(TACTIC_K.failCounter / 0.55 * 100) + '%) 받습니다. 기력은 그대로 씁니다.</p>' +
        '<p class="note"><b>무장</b> = (내 부대 최고 무력×0.6 + 주장 통솔×0.4) − 상대 부대 최고 통솔. <b>병력</b> = 내 병력이 상대의 절반이면 −8, 두 배면 +8. 피해에도 병력 차가 들어갑니다(지금 ×' + tacticSizeK(u, d).toFixed(2) + '). 대성공률은 적성·무력·(내 무력 − 상대 통솔)로 정해지고, 혼란은 상대의 지력·통솔이 높을수록 덜 걸립니다. 창장·극장·궁장·기장 같은 특기가 맞으면 성공한 전법은 모두 대성공입니다.</p>';""")
s = rep(s, '<b>실패</b>하면 피해가 통상 공격의 60%로 줄고 효과가 없으며 반격을 크게 받습니다. <b>성공</b>하면 전법의 피해와 효과가 그대로 들어갑니다. <b>대성공</b>이면 피해가 1.3배가 되고 <b>효과 자체가 세집니다</b> — 돌출·돌격은 두 칸 밀어내고, 나선첨은 반드시 혼란시키고, 이단첨은 기력을 30 깎는 식입니다. 성공률은 병과 적성과 무력으로, 대성공률은 여기에 내 무력과 상대 통솔의 차이를 더해 정해지며, 혼란은 상대의 지력·통솔이 높을수록 덜 걸립니다.', '<b>실패</b>하면 피해가 통상 공격의 절반으로 줄고 효과가 없으며 반격을 통상 공격보다 크게 받습니다. <b>성공</b>하면 전법의 피해와 효과가 들어가고 반격은 통상 공격보다 작게 받습니다. <b>대성공</b>이면 피해가 1.3배가 되고 <b>효과 자체가 세집니다</b> — 돌출·돌격은 두 칸 밀어내고, 나선첨은 반드시 혼란시키고, 이단첨은 기력을 30 깎는 식입니다. <b>성공률은 양쪽을 다 봅니다</b>: 내 병과 적성, 내 무력·통솔과 상대 통솔의 차이, 양쪽 병력, 상대의 병과 적성, 상대가 선 지형. 병력이 훨씬 많은 부대나 통솔이 높은 장수에게는 잘 통하지 않고, 병력 차만큼 피해도 줄어듭니다. 대성공률은 적성·무력·(내 무력 − 상대 통솔)로 정해지며, 혼란은 상대의 지력·통솔이 높을수록 덜 걸립니다.')
io.open(p, 'w', encoding='utf-8').write(s)
p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
if '.tacs .sum' not in s:
    s += "\n.tacs .sum { margin: 6px 0 2px; font-size: 12px; color: var(--ink-2, #55504a); line-height: 1.5; }\n"
    io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
