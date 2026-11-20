# v0.9.2 글 덜어내기(2/…): 부대 창 · 대상 창 · 상태 이상 띠 · 전법 풀이
#  - 부대 창 머리말의 긴 한 줄("창병 적성 S · 병력 6,000 · 기력 100 · 군량 4,000 (130일분)" — 두 줄로 넘어갔다)을 병과·적성 한 줄 + 숫자 세 칸(병력·기력·군량 며칠분)으로
#  - 단추 아래의 설명("이번 턴 마침", "먼 곳까지 알아서", "지금 한 구간 · 나머지는 턴 종료 때", "확률·효과·기대값")을 뺀다. 값(예상 피해·기력·성공률)만 남긴다
#  - 전법 단추: "기력 10 · 40% / 대성공 2%" → "40% · 기력 10"(대성공률은 전법 풀이에)
#  - 설명 문단을 한 줄로: 이동 안내, 행군 안내, 혼란·위보 중인 대상, 초반 보호 경고, 군사의 조언, 행동을 마친 부대
#  - 상태 이상 띠의 효과 풀이를 짧게
#  - 전법 풀이: 문단 넷과 전법마다 넉 줄이던 것을 → 확률 세 칸 + 표 하나(보통 공격과 전법의 피해·받는 반격) + 전법마다 효과 두 줄. 능력치·성공률 내역·규칙은 접어 둔 '셈법'에
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)
def cut(s, a, b):            # a 로 시작해 b 바로 앞에서 끝나는 토막
    i = s.index(a); j = s.index(b, i); return s[i:j]
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()

# ---- 대상에게 할 수 있는 일 ----
s = rep(s, "(!inT ? (d > rg ? '사거리 밖' : '숲에서는 불가') : '기력 ' + tac.cost + ' · ' + od.ok + '%' + '<br>대성공 ' + od.crit + '%'));",
           "(!inT ? (d > rg ? '사거리 밖' : '숲에서는 불가') : '<em class=\"pc\">' + od.ok + '%</em> · 기력 ' + tac.cost));")
s = rep(s, "sub: inP ? '기력 ' + pl.cost + ' · ' + ployChance(u, pl, t.u) + '%' + advMark(ployAdvice(u, pl, t)) :",
           "sub: inP ? '<em class=\"pc\">' + ployChance(u, pl, t.u) + '%</em>' + advMark(ployAdvice(u, pl, t)) + ' · 기력 ' + pl.cost :")
s = rep(s, "sub: fresh ? '출진한 턴 — 다음 턴부터' : (d <= rg ?", "sub: fresh ? '다음 턴부터' : (d <= rg ?")
s = rep(s, "sub: justOut(u) ? '출진한 턴 — 다음 턴부터' : (d <= 1 ? '공격' : '옆 칸에서만'),", "sub: justOut(u) ? '다음 턴부터' : (d <= 1 ? '' : '옆 칸에서만'),")

# ---- 전법 풀이 ----
old = cut(s, "function showTacticInfo(u, d) {", "/* 행동 결과를 한 줄로 */")
new = """function showTacticInfo(u, d) {
  showDialog({
    render: function () {
      var all = TACTICS[u.type] || [], can = tacticList(u), od = tacticOdds(u, d), P = od.parts, i, tac, N = attackExpect(u, d), rows = '';
      function vs(a, b, moreIsGood) { if (b < 1) return ''; var q = Math.round((a / b - 1) * 100); return q ? ' <em class="' + ((q > 0) === moreIsGood ? 'good' : 'bad') + '">' + (q > 0 ? '+' : '−') + Math.abs(q) + '%</em>' : ''; }      // 보통 공격과 견준 %: 피해는 많을수록, 반격은 적을수록 좋다
      function sg(v) { return (v > 0 ? '+' : '') + v; }
      var h = dlgHead('전법 풀이') + '<div class="dlg-b"><div class="tacs">' +
        '<p class="who"><b>' + uName(u) + '</b> → <b>' + uName(d) + '</b></p>' +
        '<div class="odds"><span class="g"><i>대성공</i><b>' + od.crit + '%</b></span><span><i>성공</i><b>' + (od.ok - od.crit) + '%</b></span><span class="f"><i>실패</i><b>' + (100 - od.ok) + '%</b></span></div>';
      // 보통 공격과 나란히: 쓸 수 있는 전법마다 기대 피해 · 받는 반격
      for (i = 0; i < all.length; i++) {
        tac = all[i];
        if (can.indexOf(tac) < 0 || u.morale < tac.cost || !tacticTargets(u, tac).some(function (x) { return x.u === d; })) continue;
        var X = tacticExpect(u, d, tac);
        rows += '<tr data-t="' + tac.name + '"><th>' + tac.name + (X.others ? ' <small>+' + X.others + '부대</small>' : '') + '</th><td><b>' + fmt(Math.round(X.dealt)) + '</b>' + vs(X.dealt, N.dealt, true) + '</td><td><b>' + fmt(Math.round(X.recv)) + '</b>' + vs(X.recv, N.recv, false) + '</td></tr>';
      }
      h += '<table class="tcmp"><tr><th></th><th>피해</th><th>받는 반격</th></tr><tr class="nrm"><th>보통 공격</th><td><b>' + fmt(Math.round(N.dealt)) + '</b></td><td><b>' + fmt(Math.round(N.recv)) + '</b></td></tr>' + rows + '</table>' +
        (rows ? '<p class="cap">전법은 성공·실패를 확률대로 섞은 값 · 대성공이면 피해 ×' + od.mult + '</p>' : '');
      for (i = 0; i < all.length; i++) {
        tac = all[i];
        var have = can.indexOf(tac) >= 0, c0 = confuseOdds(tac, d), c1 = confuseOdds(tacticEff(tac, true), d);
        h += '<div class="tac' + (have ? '' : ' off') + '"><div class="tn"><b>' + tac.name + '</b><span>기력 ' + tac.cost + ' · 피해 ×' + tac.mult + (have ? '' : ' · 적성 ' + tac.need + ' 필요') + '</span></div>' +
          '<div class="tl"><i>성공</i><span>' + tac.fx + (c0 ? ' — <b>' + c0 + '%</b>' : '') + '</span></div>' +
          '<div class="tl g"><i>대성공</i><span>' + tac.gfx + (c1 && c1 < 100 ? ' — <b>' + c1 + '%</b>' : '') + '</span></div></div>';
      }
      h += '<details class="more"><summary>셈법</summary>' +
        '<p class="sum"><b>' + uName(u) + '</b> ' + UNIT_TYPES[u.type].name + ' 적성 ' + uApt(u) + ' · 무력 ' + uWar(u) + ' · 통솔 ' + uLeader(u).ldr + ' · ' + fmt(u.troops) + '명<br><b>' + uName(d) + '</b> ' + UNIT_TYPES[d.type].name + ' 적성 ' + uApt(d) + ' · 통솔 ' + uLdr(d) + ' · 지력 ' + uInt(d) + ' · ' + fmt(d.troops) + '명</p>' +
        '<p class="sum">성공률 ' + od.ok + '% = 적성 ' + P.apt + ' · 무장 ' + sg(P.stat) + ' · 병력 ' + sg(P.troops) + ' · 상대 적성 ' + sg(P.dapt) + (P.terr ? ' · 지형 ' + sg(P.terr) : '') + (P.conf ? ' · 혼란 ' + sg(P.conf) : '') + (P.skill ? ' · 특기 ' + sg(P.skill) : '') + '</p>' +
        '<ul class="rules"><li>성공해도 반격은 통상 공격만큼 받습니다. 갈퀴·돌파, 멀리서 쏜 전법, 밀려나 떨어진 적은 반격하지 못합니다.</li>' +
        '<li>실패하면 피해가 통상 공격의 ' + Math.round(TACTIC_K.failDmg * 100) + '%, 반격은 ' + (TACTIC_K.failCounter / 0.55).toFixed(2).replace(/0$/, '') + '배. 기력은 그대로 씁니다.</li>' +
        '<li>무장 = (내 부대 최고 무력×0.6 + 주장 통솔×0.4 − 상대 부대 최고 통솔) × ' + TACTIC_K.stat + ' (' + TACTIC_K.statLo + ' ~ +' + TACTIC_K.statHi + ')</li>' +
        '<li>병력 = 내 병력이 상대의 절반이면 −8, 두 배면 +8. 피해에도 병력 차가 들어갑니다(지금 ×' + tacticSizeK(u, d).toFixed(2) + ').</li>' +
        '<li>창장·극장·궁장·기장 같은 특기가 맞으면 성공한 전법은 모두 대성공입니다.</li></ul></details>';
      return h + '</div></div>';
    }, on: {}
  });
}
"""
s = rep(s, old, new)

# ---- 상태 이상 띠 ----
s = rep(s, "<span>움직이지도 싸우지도 못합니다 · 받는 피해 +25% · 반격하지 못합니다 · 전법 성공률 +10</span></div>';", "<span>행동 불가 · 받는 피해 +25% · 반격 없음</span></div>';")
s = rep(s, "<span>거짓 소식에 속아 명령을 듣지 않고 가까운 자기 거점 쪽으로 물러납니다 · 반격하지 못합니다</span></div>';", "<span>명령 불가 · 자기 거점 쪽으로 후퇴 · 반격 없음</span></div>';")
s = rep(s, "'</i><span>' + (uHas(u, '화신') ? '화신 특기라 불에 다치지 않습니다' : '불 위에 머무는 동안 턴마다 병력 250~400명과 기력 5를 잃습니다' + (mine ? ' — 불 밖으로 옮기거나 소화하세요' : '')) + '</span></div>';",
           "'</i><span>' + (uHas(u, '화신') ? '화신 — 불에 다치지 않음' : '턴마다 병력 −250~400 · 기력 −5') + '</span></div>';")
s = rep(s, "  var h = '', mine = u.f === G.player;\n  if (u.status === 'confuse')", "  var h = '';\n  if (u.status === 'confuse')")

# ---- 부대 창 ----
s = rep(s, """<div class="sh-sub">' + T.name + (APT_IDX[x.type] !== undefined ? ' 적성 ' + uApt(x) : '') +
        ' · 병력 <b>' + fmt(x.troops) + '</b> · 기력 <b>' + x.morale + '</b> · 군량 ' + fmt(x.food) + ' (<b' + (turns <= 3 ? ' class="bad"' : '') + '>' + days(turns) + '분</b>)' + (stChips(x) ? ' ' + stChips(x) : '') + '</div></div>' +
        '<button class="x" data-a="close" type="button" aria-label="닫기">×</button></div><div class="sh-body">' + statusBanner(x);""",
"""<div class="sh-sub">' + T.name + (APT_IDX[x.type] !== undefined ? ' 적성 ' + uApt(x) : '') + (stChips(x) ? ' ' + stChips(x) : '') + '</div></div>' +
        '<button class="x" data-a="close" type="button" aria-label="닫기">×</button></div><div class="sh-body">' +
        '<div class="stats ust"><div><span>' + ico('troops') + '병력</span><b>' + fmt(x.troops) + '</b></div><div><span>' + ico('morale') + '기력</span><b>' + x.morale + '</b></div><div><span>' + ico('food') + '군량</span><b' + (turns <= 3 ? ' class="bad"' : '') + '>' + days(turns) + '분</b></div></div>' + statusBanner(x);""")
s = rep(s, """          h += '<div class="tgt">행군 — <b>' + UI.march.name + '</b>까지 약 <b>' + days(UI.march.turns) + '</b>' + (UI.march.turns > turns ? ' · <b class="bad">군량이 모자랍니다</b>' : '') + '</div><div class="acts">' +
            '<button class="act pri" type="button" data-a="march"><b>행군 시작</b><small>지금 한 구간 · 나머지는 턴 종료 때</small></button>' +
            (UI.march.base >= 0 ? '<button class="act" type="button" data-a="viewbase"><b>거점 보기</b><small>' + UI.march.name + '</small></button>' : '') +
            '<button class="act" type="button" data-a="unmarch"><b>취소</b><small>&nbsp;</small></button></div>';""",
"""          h += '<div class="tgt">행군 — <b>' + UI.march.name + '</b>까지 약 <b>' + days(UI.march.turns) + '</b>' + (UI.march.turns > turns ? ' · <b class="bad">군량 부족</b>' : '') + '</div><div class="acts">' +
            '<button class="act pri" type="button" data-a="march"><b>행군 시작</b></button>' +
            (UI.march.base >= 0 ? '<button class="act" type="button" data-a="viewbase"><b>거점 보기</b></button>' : '') +
            '<button class="act" type="button" data-a="unmarch"><b>취소</b></button></div>';""")
s = rep(s, """          if (t.kind === 'unit' && t.u.status) h += '<p class="note stn">' + (t.u.status === 'confuse' ? '<b>혼란 중</b> — 반격하지 못하고 피해를 25% 더 받습니다. 전법도 더 잘 통합니다.' : '<b>위보에 속은 중</b> — 반격하지 못하고 자기 거점 쪽으로 물러나고 있습니다.') + ' ' + statusLeftText(t.u) + '.</p>';
          if (t.kind !== 'unit' && peaceWouldBreak(t.b.owner)) h += '<p class="note pzw"><b>초반 보호 중</b> — ' + facName(t.b.owner) + '군은 아직 우리 거점을 치지 못합니다. 우리가 먼저 치면 <b>' + facName(t.b.owner) + '군에 대한 보호가 풀려</b> 그쪽도 우리를 칠 수 있게 됩니다.</p>';""",
"""          if (t.kind === 'unit' && t.u.status) h += '<p class="note stn">' + (t.u.status === 'confuse' ? '반격 없음 · 받는 피해 +25% · 전법 성공률 +10' : '반격 없음') + '</p>';
          if (t.kind !== 'unit' && peaceWouldBreak(t.b.owner)) h += '<p class="note pzw">먼저 치면 <b>' + facName(t.b.owner) + '군과의 보호가 풀립니다</b></p>';""")
s = rep(s, """          if (adv1) h += '<p class="note advn">군사 <b>' + adv1.adv.n + '</b>의 조언 — 계략 단추의 <i class="adv y">○</i> 통한다 · <i class="adv n">×</i> 어렵다 <small>적중률 ' + adv1.acc + '%</small></p>';""",
           """          if (adv1) h += '<p class="note advn">군사 <b>' + adv1.adv.n + '</b> — <i class="adv y">○</i> 통함 · <i class="adv n">×</i> 어려움 <small>적중률 ' + adv1.acc + '%</small></p>';""")
s = rep(s, """h += '<button class="act' + (a.pri && a.ok ? ' pri' : '') + (a.ok ? '' : ' off') + '" type="button" data-a="act" data-v="' + i + '"><b>' + a.label + '</b><small>' + a.sub + '</small></button>'; }
          if (t.kind === 'unit' && (TACTICS[x.type] || []).length) h += '<button class="act" type="button" data-a="tacinfo"><b>전법 풀이</b><small>확률·효과·기대값</small></button>';
          h += '<button class="act" type="button" data-a="untarget"><b>대상 취소</b><small>&nbsp;</small></button></div>';""",
"""h += '<button class="act' + (a.pri && a.ok ? ' pri' : '') + (a.ok ? '' : ' off') + '" type="button" data-a="act" data-v="' + i + '"><b>' + a.label + '</b>' + (a.sub ? '<small>' + a.sub + '</small>' : '') + '</button>'; }
          if (t.kind === 'unit' && (TACTICS[x.type] || []).length) h += '<button class="act" type="button" data-a="tacinfo"><b>전법 풀이</b></button>';
          h += '<button class="act" type="button" data-a="untarget"><b>대상 취소</b></button></div>';""")
s = rep(s, """          h += '<div class="acts"><button class="act" type="button" data-a="wait"><b>대기</b><small>이번 턴 마침</small></button>' +
            '<button class="act' + (x.ox >= 0 ? '' : ' off') + '" type="button" data-a="undo"><b>이동 취소</b><small>' + (x.ox >= 0 ? '되돌리기' : '&nbsp;') + '</small></button>' +
            (canDouse ? '<button class="act" type="button" data-a="douse"><b>소화</b><small>기력 10</small></button>' : '') +
            (x.dest >= 0 ? '<button class="act" type="button" data-a="unmarch"><b>행군 취소</b><small>' + destName(x.dest) + ' 방면</small></button>' : '<button class="act' + (UI.pickMarch ? ' pri' : '') + '" type="button" data-a="pickmarch"><b>행군</b><small>' + (UI.pickMarch ? '목적지를 누르세요' : '먼 곳까지 알아서') + '</small></button>') + '</div>' +
            (x.dest >= 0 ? '<p class="note"><b class="hi">' + destName(x.dest) + ' 방면 행군 중</b>' + marchLeft(x) + ' — 턴을 마치면 다음 구간을 갑니다. 그 전에 직접 움직이거나 공격해도 됩니다.</p>' : (UI.pickMarch ? '<p class="note"><b class="hi">행군 목적지를 지도에서 누르세요.</b> 거점이나 길 위의 칸을 고르면 걸리는 날수를 보여 줍니다. 그만두려면 행군을 한 번 더 누르세요.</p>' : '<p class="note"><b>파란 칸</b>을 누르면 이동하고, <b>적</b>을 누르면 공격·전법·계략을 고릅니다. 먼 곳은 <b>행군</b>을 누르고 목적지를 고르면 턴마다 알아서 갑니다.</p>'));""",
"""          h += '<div class="acts"><button class="act" type="button" data-a="wait"><b>대기</b></button>' +
            '<button class="act' + (x.ox >= 0 ? '' : ' off') + '" type="button" data-a="undo"><b>이동 취소</b></button>' +
            (canDouse ? '<button class="act" type="button" data-a="douse"><b>소화</b><small>기력 10</small></button>' : '') +
            (x.dest >= 0 ? '<button class="act" type="button" data-a="unmarch"><b>행군 취소</b></button>' : '<button class="act' + (UI.pickMarch ? ' pri' : '') + '" type="button" data-a="pickmarch"><b>행군</b></button>') + '</div>' +
            (x.dest >= 0 ? '<p class="note"><b class="hi">' + destName(x.dest) + ' 방면 행군 중</b>' + marchLeft(x) + '</p>' : (UI.pickMarch ? '<p class="note"><b class="hi">행군 목적지를 지도에서 누르세요</b></p>' : '<p class="note">파란 칸 = 이동 · 적 = 공격 · 먼 곳은 <b>행군</b></p>'));""")
s = rep(s, """      } else if (mine && x.done && x.status) h += '<p class="note">' + statusName(x.status) + '에 걸려 명령을 내릴 수 없습니다.</p>';
      else if (mine && x.done) h += '<p class="note">이번 턴 행동을 마쳤습니다.' + (x.dest >= 0 ? ' ' + destName(x.dest) + ' 방면 행군은 다음 턴에 이어집니다.' : '') + '</p>';""",
"""      } else if (mine && x.done && x.status) h += '<p class="note">' + statusName(x.status) + ' — 명령을 내릴 수 없습니다</p>';
      else if (mine && x.done) h += '<p class="note">이번 턴 행동 끝' + (x.dest >= 0 ? ' · ' + destName(x.dest) + ' 방면 행군 중' : '') + '</p>';""")
# 부대 창에서 쓰는 알림
s = rep(s, "toast(G.bases[res.front].n + ' 바로 앞입니다 — 성을 눌러 공격하세요', 3200);", "toast(G.bases[res.front].n + ' 앞 — 성을 눌러 공격', 3200);")
s = rep(s, "else toast(x.dest >= 0 ? '행군 시작 — 남은 길은 턴을 마칠 때마다 이어서 갑니다' : '도착했습니다', 3200);", "else toast(x.dest >= 0 ? '행군 시작' : '도착', 2200);")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """
/* ---- v0.9.2 부대 창의 숫자 세 칸, 단추의 큰 숫자 ---- */
.stats.ust { margin-bottom: 8px; }
.act small .pc { font-style: normal; font-weight: 800; font-size: 13px; color: var(--ink); }
.act.pri small .pc, .act:active small .pc { color: inherit; }
/* ---- v0.9.2 전법 풀이: 보통 공격과 나란히 놓은 표 ---- */
.tacs .who { margin: 0 0 8px; font-size: 14px; }
.tcmp { width: 100%; border-collapse: collapse; margin: 2px 0 4px; font-variant-numeric: tabular-nums; }
.tcmp th, .tcmp td { padding: 6px 2px; border-bottom: 1px solid var(--line); text-align: right; font-size: 14px; white-space: nowrap; }
.tcmp th:first-child { text-align: left; font-weight: 800; }
.tcmp tr:first-child th { font-weight: 500; font-size: 11.5px; color: var(--dim); padding: 2px; border-bottom-color: var(--ink); }
.tcmp tr.nrm th, .tcmp tr.nrm td { color: var(--ink-2); font-weight: 500; }
.tcmp tr.nrm b { font-weight: 600; }
.tcmp th small { font-weight: 500; font-size: 11px; color: var(--dim); }
.tcmp em { font-style: normal; font-size: 11.5px; font-weight: 800; display: inline-block; min-width: 38px; }
.tcmp em.good { color: #2f6b4f; } .tcmp em.bad { color: var(--seal); }
.tacs .cap { margin: 0 0 10px; font-size: 11.5px; color: var(--dim); }
details.more { margin-top: 12px; border-top: 1px solid var(--line-2); }
details.more > summary { list-style: none; cursor: pointer; padding: 9px 0 6px; font-size: 13px; font-weight: 700; color: var(--ink-2); }
details.more > summary::-webkit-details-marker { display: none; }
details.more > summary::after { content: " ▸"; color: var(--seal); }
details.more[open] > summary::after { content: " ▾"; }
details.more .rules { margin: 6px 0 0; padding-left: 18px; font-size: 12px; line-height: 1.5; color: var(--ink-2); }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
