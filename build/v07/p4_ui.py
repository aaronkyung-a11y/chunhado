# v0.7 화면: 전법 결과·확률 표시, 전법 풀이, 부대 목록, STATUS 창의 부대 단추, 소리 큐, 음악 장면(긴장)
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:90])
    return s.replace(a, b)
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()

# ---------- 전법: 버튼에 성공·대성공 확률 ----------
s = rep(s, """      var crit = tacticCrit(u, t.u), rate = Math.round(TACTIC_RATE[uApt(u)] + clamp((uWar(u) - 70) / 3, -5, 8));
      var sub = !have ? '적성 ' + tac.need + ' 필요' : (u.morale < tac.cost ? '기력 부족' : (!inT ? (d > rg ? '사거리 밖' : '숲에서는 불가') : '기력 ' + tac.cost + ' · ' + (crit ? '필중' : rate + '%')));""",
"""      var od = tacticOdds(u, t.u);
      var sub = !have ? '적성 ' + tac.need + ' 필요' : (u.morale < tac.cost ? '기력 부족' : (!inT ? (d > rg ? '사거리 밖' : '숲에서는 불가') : '기력 ' + tac.cost + ' · ' + (od.sure ? '필중' : od.ok + '%') + '<br>대성공 ' + (od.sure ? '확정' : od.crit + '%')));""")
s = rep(s, """          h += '<button class="act" type="button" data-a="untarget"><b>대상 취소</b><small>&nbsp;</small></button></div>';""",
"""          if (t.kind === 'unit' && (TACTICS[x.type] || []).length) h += '<button class="act" type="button" data-a="tacinfo"><b>전법 풀이</b><small>효과·확률</small></button>';
          h += '<button class="act" type="button" data-a="untarget"><b>대상 취소</b><small>&nbsp;</small></button></div>';""")
s = rep(s, """      untarget: function () { UI.target = null; refreshSheet(); requestDraw(); },
      off: function (el) { showOfficer(off(+el.getAttribute('data-v'))); }
    },
    render: function () {
      var x = UMAP[u.id];""", """      untarget: function () { UI.target = null; refreshSheet(); requestDraw(); },
      tacinfo: function () { var x = selUnit(), t = UI.target; if (x && t && t.kind === 'unit' && alive(t.u)) showTacticInfo(x, t.u); },
      off: function (el) { showOfficer(off(+el.getAttribute('data-v'))); }
    },
    render: function () {
      var x = UMAP[u.id];""")

# ---------- 전법: 결과 한 줄 ----------
s = rep(s, """    if (res.kind === 'tactic') msg += res.tac + (res.fail ? ' 실패' : (res.crit ? ' 크리티컬' : ' 성공')); else msg += '공격';
    msg += ' → ' + res.tname + ' -' + fmt(res.dmg);
    if (res.dur) msg += ' · 내구 -' + fmt(res.dur);
    if (res.dmg2) msg += ' · 연전 -' + fmt(res.dmg2);
    if (res.slam) msg += ' · 뒤가 막혀 추가 피해';
    if (res.confused) msg += ' · 혼란';""", """    if (res.kind === 'tactic') msg += res.tac + (res.fail ? ' 실패' : (res.crit ? ' 대성공' : ' 성공')); else msg += '공격';
    msg += ' → ' + res.tname + ' -' + fmt(res.dmg);
    if (res.fail && res.pOk !== undefined) msg += ' (성공률 ' + res.pOk + '%)';
    if (res.dur) msg += ' · 내구 -' + fmt(res.dur);
    if (res.dmg2) msg += ' · 연전 -' + fmt(res.dmg2);
    if (res.pushed >= 2) msg += ' · 두 칸 밀어냄';
    if (res.slam) msg += ' · 뒤가 막혀 추가 피해';
    if (res.mor) msg += ' · 기력 -' + res.mor;
    if (res.confused) msg += ' · 혼란';""")

# ---------- 전법: 타격 순간의 글씨·소리 ----------
s = rep(s, """      sfx(res.ploy === '화계' || res.ploy === '소화' ? 'fire' : 'hit');
    } else {
      floatText(res.c, res.r, '실패', C_DIM); sfx('fail');""", """      sfx(res.ploy === '화계' ? 'fire' : (res.ploy === '소화' ? 'douse' : 'wind'));
    } else {
      floatText(res.c, res.r, '실패', C_DIM); sfx('miss');""")
s = rep(s, """    if (res.kind === 'tactic') floatText(res.c, res.r, res.fail ? '전법 실패' : res.tac + (res.crit ? ' 크리티컬!' : '!'), res.fail ? C_DIM : C_INK, 0, true, -34);""",
"""    if (res.kind === 'tactic') floatText(res.c, res.r, res.fail ? res.tac + ' 실패' : res.tac + (res.crit ? ' 대성공!' : '!'), res.fail ? C_DIM : (res.crit ? C_DMG : C_INK), 0, true, -34);""")
s = rep(s, """    if (res.extra) res.extra.forEach(function (x, i) { floatText(x.c, x.r, '-' + fmt(x.dmg), C_DMG, 300 + i * 80); });
    if (res.confused) floatText(tc, tr, '혼란', C_PLOY, 700, false, 48);
    if (res.fire) sfx('fire');
    sfx(res.fail ? 'fail' : (res.kind === 'tactic' || res.crit ? 'big' : 'hit'));
  }""", """    if (res.extra) res.extra.forEach(function (x, i) { floatText(x.c, x.r, '-' + fmt(x.dmg), C_DMG, 300 + i * 80); if (x.mor) floatText(x.c, x.r, '기력 -' + x.mor, C_PLOY, 560 + i * 80, false, 26); });
    // 전법에 딸린 효과를 글씨로(차례로 아래에)
    var fxs = [];
    if (res.pushed >= 2) fxs.push('두 칸 밀어냄');
    if (res.slam) fxs.push('뒤가 막혀 충돌!');
    if (res.mor) fxs.push('기력 -' + res.mor);
    if (res.confused) fxs.push('혼란');
    fxs.forEach(function (tx, i) { floatText(tc, tr, tx, C_PLOY, 480 + i * 240, false, 26 + i * 22); });
    if (res.fire) sfx('fire');
    var far = res.ac0 !== undefined && hdist(res.ac0, res.ar0, res.c, res.r) > 1;
    sfx(res.fail ? 'fail' : (res.kind === 'tactic' ? (res.crit ? 'great' : 'big') : (res.crit ? 'big' : (res.tk === 'base' || res.tk === 'fac' ? 'siege' : (far ? 'arrowhit' : 'hit')))));
  }""")
s = rep(s, """  if (res.duel) { floatText(res.duel.win ? tc : ac, res.duel.win ? tr : ar, '일기토 패 -' + fmt(res.duel.loss), C_INK, 1150, true, -8); sfx('big'); }
  if (res.selfDmg) floatText(res.ac, res.ar, '-' + fmt(res.selfDmg), C_CNT, 500);
  if (res.fell) sfx('fall');""", """  if (res.duel) floatText(res.duel.win ? tc : ac, res.duel.win ? tr : ar, '일기토 패 -' + fmt(res.duel.loss), C_INK, 1150, true, -8);   // 소리는 연출(fx.js) 쪽에서 엇갈리는 순간에
  if (res.selfDmg) floatText(res.ac, res.ar, '-' + fmt(res.selfDmg), C_CNT, 500);
  if (res.fell) { sfx('fall'); if (res.af === G.player) sfx('cheerlate'); }""")

# ---------- 전법 풀이 창 ----------
s = rep(s, """/* 행동 결과를 한 줄로 */
function resultMsg(name, res) {""", """/* 전법 풀이: 고른 상대에 대한 성공·대성공 확률과, 결과에 따라 달라지는 효과 */
function showTacticInfo(u, d) {
  showDialog({
    render: function () {
      var all = TACTICS[u.type] || [], can = tacticList(u), od = tacticOdds(u, d), i;
      var h = dlgHead('전법 풀이') + '<div class="dlg-b"><div class="tacs">' +
        '<p class="who"><b>' + uName(u) + '</b> <span>' + UNIT_TYPES[u.type].name + ' 적성 ' + uApt(u) + ' · 무력 ' + uWar(u) + '</span><br>→ <b>' + uName(d) + '</b> <span>통솔 ' + uLdr(d) + ' · 지력 ' + uInt(d) + '</span></p>' +
        '<div class="odds">' + (od.sure ? '<span class="g"><i>대성공</i><b>확정</b></span><span><i>특기</i><b>필중</b></span>' :
          '<span class="g"><i>대성공</i><b>' + od.crit + '%</b></span><span><i>성공</i><b>' + (od.ok - od.crit) + '%</b></span><span class="f"><i>실패</i><b>' + (100 - od.ok) + '%</b></span>') + '</div>';
      for (i = 0; i < all.length; i++) {
        var tac = all[i], have = can.indexOf(tac) >= 0, c0 = confuseOdds(tac, d), c1 = confuseOdds(tacticEff(tac, true), d);
        h += '<div class="tac' + (have ? '' : ' off') + '"><div class="tn"><b>' + tac.name + '</b><span>기력 ' + tac.cost + ' · 피해 ×' + tac.mult + (have ? '' : ' · 적성 ' + tac.need + ' 필요') + '</span></div>' +
          '<div class="tl"><i>성공</i><span>' + tac.fx + (c0 ? ' — 이 상대에게는 <b>' + c0 + '%</b>' : '') + '</span></div>' +
          '<div class="tl g"><i>대성공</i><span>피해 ' + od.mult + '배, ' + tac.gfx + (c1 && c1 < 100 ? ' — 이 상대에게는 <b>' + c1 + '%</b>' : '') + '</span></div></div>';
      }
      h += '<p class="note"><b>실패</b>하면 피해가 통상 공격의 60%로 줄고 효과가 없으며, 반격을 더 크게 받습니다. 기력은 그대로 씁니다.</p>' +
        '<p class="note">성공률은 <b>병과 적성과 무력</b>으로 정해집니다. 대성공률은 여기에 <b>내 무력과 상대 통솔의 차이</b>가 더해집니다. 혼란은 상대의 <b>지력·통솔</b>이 높을수록 덜 걸립니다. 창장·극장·궁장·기장 같은 특기가 맞으면 반드시 대성공입니다.</p>';
      return h + '</div></div>';
    }, on: {}
  });
}
/* 행동 결과를 한 줄로 */
function resultMsg(name, res) {""")

# ---------- 부대 목록 ----------
s = rep(s, """      } else if (st.tab === 'unit') {
        var us = facUnits(G.player);
        if (!us.length) h += '<p class="note">출진한 부대가 없습니다.</p>';
        us.forEach(function (u) { h += '<button class="row' + (u.done ? ' dim' : '') + '" type="button" data-a="u" data-v="' + u.id + '">' + porTag(uLeader(u)) + '<span class="mid"><span class="nm">' + uName(u) + ' <em>' + UNIT_TYPES[u.type].name + '</em></span><span class="ds">기력 ' + u.morale + ' · 군량 ' + days(unitFoodTurns(u)) + '분' + (u.dest >= 0 ? ' · ' + destName(u.dest) + ' 방면 행군' : (u.done ? ' · 행동 완료' : '')) + '</span></span><span class="rt"><b>' + fmt(u.troops) + '</b></span></button>'; });
      } else if (st.tab === 'off') {""", """      } else if (st.tab === 'unit') {
        // 내 부대(명령을 기다리는 부대가 위로) + 다른 세력의 부대(가까운 순)
        var us = facUnits(G.player).sort(function (x, y) { return (x.done ? 1 : 0) - (y.done ? 1 : 0); }), ready = us.filter(function (u) { return !u.done && !u.status; }).length;
        h += '</div><div class="sec">내 부대 ' + us.length + '개' + (us.length ? ' <small>명령을 기다리는 부대 ' + ready + '개</small>' : '') + '</div><div class="rows">';
        if (!us.length) h += '<p class="note">출진한 부대가 없습니다. 거점의 <b>군사 → 출진</b>에서 내보냅니다.</p>';
        us.forEach(function (u) { h += unitRow(u); });
        var total = G.units.length - us.length, foes = nearbyFoes(st.allU ? 9999 : FOE_NEAR);
        h += '</div><div class="sec">' + (st.allU ? '다른 세력의 부대 ' + foes.length + '개' : '가까이 있는 다른 세력 부대 ' + foes.length + '개') + ' <small>가까운 순</small></div><div class="rows">';
        if (!foes.length) h += '<p class="note">' + (st.allU ? '지도에 다른 세력의 부대가 없습니다.' : '내 거점과 부대에서 ' + FOE_NEAR + '칸 안에는 다른 세력의 부대가 없습니다.') + '</p>';
        foes.forEach(function (x) { h += unitRow(x.u, x); });
        if (!st.allU && total > foes.length) h += '<button class="row more" type="button" data-a="allu"><span class="mid"><span class="nm">다른 세력 부대 모두 보기</span><span class="ds">천하에 ' + total + '개</span></span><span class="rt">▸</span></button>';
      } else if (st.tab === 'off') {""")
s = rep(s, """      tab: function (el) { st.tab = el.getAttribute('data-v'); refreshDialog(); },
      b: function (el) { var b = G.bases[+el.getAttribute('data-v')]; jumpFromDialog('목록', function () { gotoBase(b); }); },""",
"""      tab: function (el) { st.tab = el.getAttribute('data-v'); refreshDialog(); },
      allu: function () { st.allU = true; refreshDialog(); },
      b: function (el) { var b = G.bases[+el.getAttribute('data-v')]; jumpFromDialog('목록', function () { gotoBase(b); }); },""")
s = rep(s, """function showLists(tab) {
  clearRet();""", """/* 부대가 있는 곳을 말로: 성역 안이면 그 성, 아니면 가장 가까운 거점에서 몇 칸 */
function unitWhere(u) {
  var z = zoneAt(u.c, u.r);
  if (z >= 0) return G.bases[z].n + ' 성역';
  var best = null, bd = 1e9;
  for (var i = 0; i < G.bases.length; i++) { var b = G.bases[i], d = hdist(u.c, u.r, b.c, b.r); if (d < bd) { bd = d; best = b; } }
  return best ? best.n + '에서 ' + bd + '칸' : '';
}
function unitState(u) {
  if (u.status) return '<b class="bad">' + (u.status === 'confuse' ? '혼란' : '위보') + '</b>';
  if (u.f !== G.player) return '';
  if (u.dest >= 0) return destName(u.dest) + ' 방면 행군';
  return u.done ? '행동 완료' : '<b class="hi">명령 대기</b>';
}
var FOE_NEAR = 10;
/* 내 거점·부대에서 rad 칸 안에 있는 다른 세력의 부대(가까운 순). to = 가장 가까운 내 거점·부대 */
function nearbyFoes(rad) {
  var mine = [], out = [];
  facBases(G.player).forEach(function (b) { mine.push({ c: b.c, r: b.r, n: b.n }); });
  facUnits(G.player).forEach(function (u) { mine.push({ c: u.c, r: u.r, n: uName(u) }); });
  G.units.forEach(function (u) {
    if (u.f === G.player) return;
    var bd = 1e9, bn = '';
    for (var i = 0; i < mine.length; i++) { var d = hdist(u.c, u.r, mine[i].c, mine[i].r); if (d < bd) { bd = d; bn = mine[i].n; } }
    if (bd <= rad) out.push({ u: u, d: bd, to: bn });
  });
  return out.sort(function (a, b) { return a.d - b.d || b.u.troops - a.u.troops; });
}
function unitRow(u, x) {
  var mine = u.f === G.player, stt = unitState(u);
  var l2 = mine ? '기력 ' + u.morale + ' · 군량 ' + days(unitFoodTurns(u)) + '분' : '기력 ' + u.morale + (x && x.to ? ' · 내 ' + x.to + '에서 ' + x.d + '칸' : '');
  return '<button class="row' + (mine && u.done ? ' dim' : '') + '" type="button" data-a="u" data-v="' + u.id + '">' + porTag(uLeader(u)) + '<span class="mid"><span class="nm">' + uName(u) + ' <em>' + UNIT_TYPES[u.type].name + '</em>' + (mine ? '' : ' ' + facChip(u.f)) + '</span>' +
    '<span class="ds">' + unitWhere(u) + (stt ? ' · ' + stt : '') + '</span><span class="ds">' + l2 + '</span></span><span class="rt"><b>' + fmt(u.troops) + '</b></span></button>';
}
function showLists(tab) {
  clearRet();""")

# ---------- STATUS 창: 부대 단추 ----------
a = s.index("""        '<div class="hm-links"><button type="button" data-a="lists" data-v="city">'""")
b = s.index("""        '<div class="sec">지금 할 일</div><div class="todos">';""")
s = s[:a] + """        '<div class="hm-links"><button type="button" data-a="lists" data-v="city"><span>' + ico('dur') + '거점</span><b>' + T.cities + '성' + (T.gates ? ' ' + T.gates + '관' : '') + '</b></button>' +
        '<button type="button" data-a="lists" data-v="unit"><span>' + ico('troops') + '부대</span><b>' + T.units + '개</b></button>' +
        '<button type="button" data-a="lists" data-v="off"><span>' + ico('order') + '무장</span><b>' + T.off + '명</b></button>' +
        '<button type="button" data-a="lists" data-v="fac"><span>' + ico('morale') + '천하</span><b>' + G.factions.filter(function (x) { return x.alive; }).length + '세력</b></button></div>' +
""" + s[b:]

# ---------- 소리 큐 ----------
s = rep(s, """function done(res, msg) {
  if (!res.ok) { toast(res.msg); return false; }
  if (msg) toast(msg);""", """function done(res, msg, snd) {
  if (!res.ok) { toast(res.msg); return false; }
  if (snd) sfx(snd);
  if (msg) toast(msg);""")
s = rep(s, "return done(r, r.ok ? '징병 +' + fmt(r.n) + '명' : ''); });", "return done(r, r.ok ? '징병 +' + fmt(r.n) + '명' : '', 'drums'); });")
s = rep(s, "return done(r, r.ok ? '치안 +' + r.n : ''); });", "return done(r, r.ok ? '치안 +' + r.n : '', 'step'); });")
s = rep(s, "return done(r, r.ok ? '기력 +' + r.n : ''); });", "return done(r, r.ok ? '기력 +' + r.n : '', 'shout'); });")
s = rep(s, "return done(r, r.ok ? k[1] + ' +' + fmt(r.n) : ''); });", "return done(r, r.ok ? k[1] + ' +' + fmt(r.n) : '', 'hammer'); });")
s = rep(s, "done(r, r.ok ? (st.dir === 'buy' ? '병량 +' : '금 +') + fmt(r.n) : ''); }", "done(r, r.ok ? (st.dir === 'buy' ? '병량 +' : '금 +') + fmt(r.n) : '', 'coin'); }")
s = rep(s, "if (r.ok && r.joined) sfx('drum'); return done(", "if (r.ok && r.joined) sfx('cheer'); return done(")
s = rep(s, "if (!r.ok) return toast(r.msg); toast('충성 +' + r.n); refreshDialog();", "if (!r.ok) return toast(r.msg); sfx('coin'); toast('충성 +' + r.n); refreshDialog();")
s = rep(s, "return done(r, r.ok ? F.name + ' 착공 — ' + days(r.turns) + ' 뒤 완공' : ''); });", "return done(r, r.ok ? F.name + ' 착공 — ' + days(r.turns) + ' 뒤 완공' : '', 'hammer'); });")
s = rep(s, "return done(r, r.ok ? F.name + ' Lv' + r.lv + '로 올랐습니다' : ''); });", "return done(r, r.ok ? F.name + ' Lv' + r.lv + '로 올랐습니다' : '', 'hammer'); });")
s = rep(s, "cmdDemolish(b, pi); closeDialog(); toast(F.name + ' 철거');", "cmdDemolish(b, pi); closeDialog(); sfx('miss'); toast(F.name + ' 철거');")
s = rep(s, """        if (!r.ok) return toast(r.msg);
        closeDialog(); sfx('drum');
        var u = r.unit, name = uName(u);""", """        if (!r.ok) return toast(r.msg);
        closeDialog(); sfx('deploy');
        var u = r.unit, name = uName(u);""")
s = rep(s, "closeDialog(); toast('수송대 출발 — 파란 칸을 눌러 이동하세요.", "closeDialog(); sfx('drum'); toast('수송대 출발 — 파란 칸을 눌러 이동하세요.")
# 점령(내가): 무너지는 소리 + 함성
s = rep(s, "else if (res.captured !== undefined) { sfx('fall'); fxFall(G.bases[res.captured], '점령'); toast(G.bases[res.captured].n + ' 점령!'); selectBase(G.bases[res.captured]); }",
           "else if (res.captured !== undefined) { sfx('fall'); sfx('cheerlate'); fxFall(G.bases[res.captured], '점령'); toast(G.bases[res.captured].n + ' 점령!'); selectBase(G.bases[res.captured]); }")
s = rep(s, "else if (res && res.ok && res.captured !== undefined) { sfx('fall'); fxFall(G.bases[res.captured], '점령');", "else if (res && res.ok && res.captured !== undefined) { sfx('fall'); sfx('cheerlate'); fxFall(G.bases[res.captured], '점령');")
s = rep(s, "P.ans = []; if (res.captured !== undefined) { sfx('fall'); fxFall(G.bases[res.captured], '점령'); }", "P.ans = []; if (res.captured !== undefined) { sfx('fall'); sfx('cheerlate'); fxFall(G.bases[res.captured], '점령'); }")
s = rep(s, "      sfx('fall'); fxFall(b, e.old < 0 || b.kind === 'gate' ? '점령' : '함락');", "      sfx('fall'); if (e.by === G.player) sfx('cheerlate');\n      fxFall(b, e.old < 0 || b.kind === 'gate' ? '점령' : '함락');")
s = rep(s, "animAct(res, function () { UI.busy = false; toast('주위의 불을 껐습니다'); clearSel(); afterAction(); }, function () { sfx('fire'); });", "animAct(res, function () { UI.busy = false; toast('주위의 불을 껐습니다'); clearSel(); afterAction(); }, function () { sfx('douse'); });")
# 재생: 출진은 북, 멸망·새 턴은 징
s = rep(s, """      setCaption(e.f, G.bases[e.base].n + '에서 <b>' + e.n + '</b> 출진');
      sfx('drum');""", """      setCaption(e.f, G.bases[e.base].n + '에서 <b>' + e.n + '</b> 출진');
      sfx('drums');""")
s = rep(s, "setCaption(-1, '<b>' + facName(e.f) + '군 멸망</b>', 'big'); sfx('big');", "setCaption(-1, '<b>' + facName(e.f) + '군 멸망</b>', 'big'); sfx('gong');")
s = rep(s, """  setCaption(G.player, '<b>' + dateStr() + '</b> — 새 턴이 시작됩니다');
  sfx('drum');""", """  setCaption(G.player, '<b>' + dateStr() + '</b> — 새 턴이 시작됩니다');
  sfx('gong');""")
s = rep(s, "  sfx('drum'); saveGame(); refreshHud();\n  if (P.shown) jumpBack(P.cam0);", "  sfxMoveStop(); sfx('drum'); saveGame(); refreshHud();\n  if (P.shown) jumpBack(P.cam0);")
s = rep(s, "closeDialog(); newGame(st.f); startGame(); sfx('drum'); showIntro(); }", "closeDialog(); newGame(st.f); startGame(); sfx('gong'); showIntro(); }")
# 재생 중 내가 얽힌 싸움 → 전투 음악
s = rep(s, """  } else if (e.t === 'act') {
    focusNear(e.tc, e.tr, pg(function () {""", """  } else if (e.t === 'act') {
    if ((e.f === G.player || e.tf === G.player) && UI.battleTurn !== G.turn) { UI.battleTurn = G.turn; playBgm('battle'); }   // 내가 얽힌 싸움이면 전투 음악으로
    focusNear(e.tc, e.tr, pg(function () {""")

# ---------- 음악 장면: 평시 / 긴장 / 전투 ----------
a = s.index("function bgmForState() {"); b = s.index("function saveGame() {")
s = s[:a] + """/* 지금 틀 음악의 장면: 싸운 지 한 턴 안이거나 적이 내 성 코앞이면 전투, 적이 가까이 있으면 긴장, 아니면 평시 */
function bgmForState() {
  if (!G) return 'title';
  if (G.turn - (UI.battleTurn === undefined ? -9 : UI.battleTurn) <= 1) return 'battle';
  var bs = facBases(G.player), us = facUnits(G.player), i, tense = false;
  for (i = 0; i < bs.length; i++) {
    if (enemyUnitsNear(G.player, bs[i].c, bs[i].r, 2).length) return 'battle';
    if (!tense && enemyUnitsNear(G.player, bs[i].c, bs[i].r, 7).length) tense = true;
  }
  for (i = 0; i < us.length && !tense; i++) {
    var z = zoneAt(us[i].c, us[i].r);
    if ((z >= 0 && G.bases[z].owner >= 0 && G.bases[z].owner !== G.player) || enemyUnitsNear(G.player, us[i].c, us[i].r, 4).length) tense = true;   // 남의 성역에 들어섰거나 적 부대가 가깝다
  }
  return tense ? 'tense' : 'field';
}
""" + s[b:]

# ---------- 도움말 ----------
s = rep(s, """전법은 기력을 쓰고, 병과 적성(C→S)이 높을수록 쓸 수 있는 전법이 늘고 잘 통합니다.</p>' +""",
"""전법은 기력을 쓰고, 병과 적성(C→S)이 높을수록 쓸 수 있는 전법이 늘고 잘 통합니다.</p>' +
  '<p><b>전법의 결과는 세 가지</b>입니다. <b>실패</b>하면 피해가 통상 공격의 60%로 줄고 효과가 없으며 반격을 크게 받습니다. <b>성공</b>하면 전법의 피해와 효과가 그대로 들어갑니다. <b>대성공</b>이면 피해가 1.3배가 되고 <b>효과 자체가 세집니다</b> — 돌출·돌격은 두 칸 밀어내고, 나선첨은 반드시 혼란시키고, 이단첨은 기력을 30 깎는 식입니다. 성공률은 병과 적성과 무력으로, 대성공률은 여기에 내 무력과 상대 통솔의 차이를 더해 정해지며, 혼란은 상대의 지력·통솔이 높을수록 덜 걸립니다. 적을 고른 뒤 <b>전법 풀이</b>를 누르면 그 상대에 대한 확률과 효과를 볼 수 있습니다.</p>' +""")
s = rep(s, """거점이나 부대를 고르면 같은 자리에 그 정보와 명령이 나옵니다. 오른쪽 위 ▾로 접을 수 있고,""",
"""거점이나 부대를 고르면 같은 자리에 그 정보와 명령이 나옵니다. <b>거점·부대·무장·천하</b> 단추는 그 목록을 엽니다 — 부대 목록에는 내 부대의 위치와 상태, 그리고 가까이 있는 다른 세력의 부대가 나옵니다. 오른쪽 위 ▾로 접을 수 있고,""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "(res.fail ? ' 실패' : (res.crit ? ' 크리티컬' : ''))", "(res.fail ? ' 실패' : (res.crit ? ' 대성공' : ''))")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "  fall:     { s: [['fall', 0.95, 0]], gap: 1500, syn: 'fall' },\n  capture:  { s: [['fall', 0.95, 0], ['cheer', 0.6, 0.02, 1.0]], gap: 1500, syn: 'fall' },",
           "  fall:     { s: [['fall', 0.95, 0]], gap: 3500, syn: 'fall' },          // 함락 장면이 곧바로 한 번 더 불러도 겹치지 않게\n  cheerlate: { s: [['cheer', 0.6, 0.02, 1.0]], gap: 3500, syn: '' },")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """.hm-links { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-top: 8px; }
.hm-links button { display: flex; align-items: center; justify-content: center; gap: 2px; height: 38px; border: 1px solid var(--line-2); border-radius: 2px; color: var(--dim); font-size: 13px; white-space: nowrap; }
.hm-links button b { color: var(--ink); font-weight: 800; margin: 0 2px; }""", """.hm-links { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 8px; }
.hm-links button { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1px; height: 46px; border: 1px solid var(--line-2); border-radius: 2px; color: var(--dim); font-size: 12px; line-height: 1.15; white-space: nowrap; min-width: 0; }
.hm-links button span { display: flex; align-items: center; gap: 2px; }
.hm-links button b { color: var(--ink); font-weight: 800; font-size: 13.5px; font-variant-numeric: tabular-nums; }""")
s += """
/* v0.7 — 부대 목록, 전법 풀이 */
.sec small { font: 500 11.5px var(--font-body); color: var(--dim); margin-left: 2px; }
.row .nm .chip { font-size: 10.5px; padding: 0 5px; margin-left: 4px; vertical-align: 1px; }
.row.more { min-height: 50px; color: var(--seal); }
.row.more .nm { color: var(--seal); }
.tacs .who { font-size: 13.5px; line-height: 1.5; margin: 2px 0 8px; }
.tacs .who span { color: var(--dim); font-size: 12px; }
.tacs .odds { display: flex; gap: 6px; margin-bottom: 10px; }
.tacs .odds span { flex: 1; border: 1px solid var(--line-2); border-radius: 2px; padding: 6px 4px; text-align: center; }
.tacs .odds i { display: block; font-style: normal; font-size: 11.5px; color: var(--dim); }
.tacs .odds b { font: 900 18px var(--font-display); font-variant-numeric: tabular-nums; }
.tacs .odds .g { border-color: var(--seal); } .tacs .odds .g b { color: var(--seal); }
.tacs .odds .f b { color: var(--dim); }
.tac { border-top: 1px solid var(--line); padding: 8px 0; }
.tac.off { opacity: .45; }
.tac .tn { display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; }
.tac .tn b { font: 900 16px var(--font-display); }
.tac .tn span { color: var(--dim); font-size: 12px; font-variant-numeric: tabular-nums; }
.tac .tl { display: flex; gap: 8px; font-size: 13px; line-height: 1.45; color: var(--ink-2); margin-top: 2px; }
.tac .tl i { flex: none; width: 44px; font-style: normal; font-size: 11.5px; color: var(--dim); padding-top: 1px; }
.tac .tl.g i { color: var(--seal); font-weight: 800; }
.tacs .note { margin-top: 8px; }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
