# v0.16 화면 — AI 가 걸어온 일기토에 답하기 · 동맹에 출병 요청 · AI 끼리의 협정 보기
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

s = rd('src/ui_panels.js')

# ── 말 ──
s = rep(s, "  dipBreak: { W: ['이 일은 잊지 않겠소!'], C: ['신의를 저버리시다니…'], L: ['신의를 저버리다니… 이 일은 잊지 않겠소.'] }\n};",
           "  dipBreak: { W: ['이 일은 잊지 않겠소!'], C: ['신의를 저버리시다니…'], L: ['신의를 저버리다니… 이 일은 잊지 않겠소.'] },\n"
           "  duelAsk:  { W: ['나와라! 나와 겨룰 자가 없느냐!', '네 솜씨를 보자. 나와라!'], C: ['한 수 겨루어 보시겠소?'], L: ['장수끼리 겨루어 승부를 가립시다.'] },\n"
           "  duelNo:   { W: ['…오늘은 상대하지 않겠다.'], C: ['장수의 싸움에 말려들 까닭이 없습니다.'], L: ['필부의 용맹에 응할 것 없다.'] },\n"
           "  aimYes:   { W: ['좋소. 군사를 내겠소.'], C: ['뜻을 받들어 군사를 내겠습니다.'], L: ['좋소. 함께 칩시다.', '때가 좋소. 군사를 내겠소.'] },\n"
           "  aimNo:    { W: ['지금은 군사를 낼 수 없소.'], C: ['지금은 군사를 내기 어렵습니다.'], L: ['지금은 군사를 낼 형편이 아니오.'] }\n};")

# ── 결과 한 줄: 일기토 신청 ──
s = rep(s, "function resultMsg(name, res) {\n  var msg = name + ' ';\n",
           "function resultMsg(name, res) {\n"
           "  if (res.kind === 'challenge') return name + ' 일기토 신청 → ' + res.tname + (res.accepted ? (res.duel ? ' — ' + (res.duel.draw ? '비김' : (res.duel.win ? res.duel.a : res.duel.d) + ' 승' + (res.duel.ko ? '(쓰러뜨림)' : '')) : ' — 응함') : ' — 받지 않음 (기력 -' + res.mor + ')');      // v0.16: AI 도 건다\n"
           "  var msg = name + ' ';\n")

# ── 지금 할 일 ──
s = rep(s, "  dipOffers().forEach(function (x) {                            // v0.14: AI 가 청해 온 정전 · 동맹\n",
           "  duelAsks().forEach(function (x) {                             // v0.16: AI 가 걸어온 일기토\n"
           "    var a = UMAP[x.a], d = UMAP[x.d], la = uLeader(a), ld = uLeader(d);\n"
           "    out.push({ cls: 'warn', ic: '鬪', t: facName(a.f) + '군 ' + josa(la.n, '이가') + ' ' + ld.n + '에게 일기토를 걸어왔습니다', s: '무력 ' + la.war + ' 대 ' + ld.war + ' · 이번 턴 안에 답해야 합니다', go: ['duelask', x.a, x.d], lb: '답하기', say: josa(la.n, '이가') + ' ' + ld.n + '에게 일기토를 걸어왔습니다. 받을지 정하십시오.' });\n"
           "  });\n"
           "  dipOffers().forEach(function (x) {                            // v0.14: AI 가 청해 온 정전 · 동맹\n")
s = rep(s, "  else if (g[0] === 'dip') flowDipOffer(g[1], g[2]);\n",
           "  else if (g[0] === 'dip') flowDipOffer(g[1], g[2]);\n  else if (g[0] === 'duelask') flowDuelAsk(g[1], g[2]);\n")

# ── 걸어온 일기토에 답한다 · 출병 요청 · 다른 세력끼리의 협정 ──
s = rep(s, "/* 외교 창: 세력 표 */\n",
"""/* v0.16: AI 가 걸어온 일기토에 답한다. 받으면 내가 수를 고르며 겨룬다(상대가 건 쪽 a, 내가 d) */
function askLive(aid, did) { return duelAsks().some(function (x) { return x.a === aid && x.d === did; }); }
function askSoon(wait) {                                           // 내 차례 첫머리: 창이 닫힌 뒤에 한 번 띄운다
  var turn = G.turn;
  setTimeout(function () {
    if (!G || G.over || UI.play || G.turn !== turn || !inGame() || UI.busy) return;
    if (MODAL) { askSoon(600); return; }
    var x = duelAsks()[0]; if (!x) return;
    flowDuelAsk(x.a, x.d);
  }, wait || 400);
}
function flowDuelAsk(aid, did) {
  if (!askLive(aid, did)) { toast('이미 지나간 신청입니다'); refreshSheet(); return; }
  var a = UMAP[aid], d = UMAP[did], la = uLeader(a), ld = uLeader(d), an = uName(a), dn = uName(d), K = DUEL_K;
  jumpTo(d.c, d.r, Math.max(cam.z, 0.8)); flashHex(a.c, a.r, '#b5332a');
  function card(u, o, mine) { return '<div class="dk' + (mine ? ' me' : '') + '">' + porTag(o, 'md') + '<div><b>' + o.n + '</b><span>무력 <em>' + o.war + '</em></span><small>지력 ' + o.int + ' · ' + UNIT_TYPES[u.type].name + ' ' + fmt(u.troops) + '명 · 기력 ' + u.morale + '</small></div></div>'; }
  showDialog({
    render: function () {
      var live = askLive(aid, did);
      return dlgHead('일기토 신청 — ' + la.n) + '<div class="dlg-b">' + sayRow(la, sayLine(la, 'duelAsk'), facName(a.f) + '군 ' + an) +
        '<div class="dks">' + card(a, la, false) + '<span class="vs">對</span>' + card(d, ld, true) + '</div>' +
        '<ul class="plain"><li><b>이기면</b> 상대 부대 기력 -' + K.morLose + ' · 병력 -' + Math.round(K.loss * 100) + '% (쓰러뜨리면 기력 -' + K.koMor + ' · 병력 -' + Math.round(K.koLoss * 100) + '% · 혼란), 우리 부대 기력 +' + K.morWin + '</li>' +
        '<li><b>지면</b> 그 반대입니다. 비기면 두 주장의 공적만 오릅니다.</li>' +
        '<li><b>받지 않으면</b> 우리 부대 기력 -' + K.refuse + '. 답하지 않고 턴을 넘겨도 받지 않은 것이 됩니다.</li></ul>' +
        '<p class="note">피해는 두 사람의 무력 차로 정해집니다 — ' + (la.war === ld.war ? '무력이 같습니다' : (la.war > ld.war ? '상대가 ' + (la.war - ld.war) + ' 높습니다' : '우리가 ' + (ld.war - la.war) + ' 높습니다')) + '. 받으면 합마다 수를 직접 고릅니다.</p>' +
        (live ? '<div class="cmds two"><button class="cmd pri" type="button" data-a="yes"><b>받아들인다</b><small>직접 겨룹니다</small></button><button class="cmd" type="button" data-a="no"><b>받지 않는다</b><small>기력 -' + K.refuse + '</small></button></div>' : '<p class="note bad">이미 지나간 신청입니다</p>') + '</div>';
    },
    on: {
      yes: function () {
        var res = duelAskAnswer(aid, did, true); closeDialog();
        if (!res.ok) { toast(res.msg); refreshSheet(); return; }
        var S = res.duelS;
        UI.battleTurn = G.turn; playBgm('battle');
        duelOpen(S, 'd', { sub: an + ' 대 ' + dn, onEnd: function () { return duelOutHtml(S, duelFinish(S, res), an, dn); } }, function () {
          syncScene(); toast(an + duelTxt(res.duel).replace(' · ', ' — '), 3200); refreshSheet(); afterAction(); askSoon(900);
        });
      },
      no: function () {
        var r = duelAskAnswer(aid, did, false); closeDialog();
        if (!r.ok) { toast(r.msg); refreshSheet(); return; }
        sfx('ui'); talk(ld, sayLine(ld, 'duelNo'), josa(dn, '이가') + ' 일기토를 받지 않았습니다 — 기력 -' + r.mor, 3000);
        refreshSheet(); afterAction(); askSoon(900);
      }
    }
  });
}
/* v0.16: 다른 세력끼리 맺은 협정과, 동맹의 청으로 치기로 한 상대 */
function pactsOthers(f) {
  var me = G.player, out = [];
  for (var i = 0; i < G.factions.length; i++) { if (i === f || i === me || !G.factions[i].alive) continue; var p = pactOf(f, i); if (p) out.push({ f: i, t: p.t, left: p.until - G.turn }); }
  return out;
}
function pactsLine(f, brief) {
  var L = pactsOthers(f), x = dipAimOf(f), h = [];
  L.forEach(function (p) { h.push(facName(p.f) + '군과 ' + PACT_NAME[p.t] + (brief ? '' : ' ' + days(p.left))); });
  if (x >= 0) h.push('<em>' + facName(x) + '군을 치기로 함' + (brief ? '' : ' ' + days(dipAimLeft(f))) + '</em>');
  return h.length ? '<span class="ds px">' + h.join(' · ') + '</span>' : '';
}
/* v0.16: 동맹에게 — 어느 세력을 쳐 달라고 청한다 */
function aimList(t) {                                              // 동맹 t 의 이웃 세력: 청할 수 있는 것 먼저
  var me = G.player, N = dipNbrs(), out = [];
  for (var i = 0; i < G.factions.length; i++) if (i !== me && i !== t && G.factions[i].alive && dipNear(t, i, N)) out.push({ f: i, why: aimCan(me, t, i) });
  return out.sort(function (a, b) { return (a.why ? 1 : 0) - (b.why ? 1 : 0) || dipPower(a.f) - dipPower(b.f); });
}
function aimSub(b, t) {
  var me = G.player, p = pactOf(me, t);
  if (!p || p.t !== 'ally') return '동맹을 맺은 세력에게만';
  if (dipAimOf(t) >= 0) return facName(dipAimOf(t)) + '군을 치기로 함 · ' + days(dipAimLeft(t)) + ' 남음';
  var L = aimList(t), ok = L.filter(function (x) { return !x.why; });
  if (!ok.length) return L.length ? L[0].why.replace(' 청할 수 있습니다', '') : '이웃한 다른 세력이 없습니다';
  if (!idleOfficers(b).length) return '쉬는 무장이 없습니다';
  return '이웃 ' + ok.length + '세력 가운데 칠 상대를 고릅니다 · 행 ' + AP.treaty;
}
function aimOff(b, t) { var me = G.player, p = pactOf(me, t); return !p || p.t !== 'ally' || dipAimOf(t) >= 0 || !idleOfficers(b).length || !aimList(t).some(function (x) { return !x.why; }); }
function aimTermsTxt(q) {
  function sg(v) { return (v > 0 ? '+' : (v < 0 ? '−' : '')) + Math.abs(v); }
  return '우호 ' + q.rel + ' · 바탕 ' + sg(q.base) + (q.envoy ? ' · 사신 ' + sg(q.envoy) : '') + (q.pow ? ' · 힘의 비 ' + sg(q.pow) : '') + (q.war ? ' · 이미 싸우는 사이 ' + sg(q.war) : '');
}
function flowAim(b, t) {
  var me = G.player, L = facLord(t);
  function best(x) { var os = idleOfficers(b), bp = -1, bo = null; os.forEach(function (o) { var p = aimTerms(me, t, x, o).p; if (p > bp) { bp = p; bo = o; } }); return { o: bo, p: Math.max(0, bp) }; }
  showDialog({
    render: function () {
      var rows = aimList(t), h = dlgHead(facName(t) + '군에 출병 요청') + '<div class="dlg-b"><p class="note">동맹 ' + facName(t) + '군이 받아들이면 <b>' + days(DIP_K.aimTurns) + '</b> 동안 그 세력을 먼저 노립니다(' + facName(t) + '군의 거점과 이웃한 세력만). 우리 성에 원군이 들어오는 것은 아닙니다.</p><div class="rows dipl">';
      if (!rows.length) h += '<p class="note bad">' + facName(t) + '군과 이웃한 다른 세력이 없습니다</p>';
      rows.forEach(function (x) {
        h += '<button class="row' + (x.why ? ' off' : '') + '" type="button" data-a="x" data-v="' + x.f + '">' + porTag(facLord(x.f), 'sm') + '<span class="mid"><span class="nm">' + facChip(x.f) + pactChip(me, x.f) + '</span><span class="ds">' +
          (x.why ? x.why : '받아들일 확률 최고 <b>' + best(x.f).p + '%</b> · 병력 ' + fmt(dipPower(t)) + ' : ' + fmt(dipPower(x.f))) + '</span></span></button>';
      });
      return h + '</div><p class="note">받아들일 확률 = 우호 + 바탕 ' + DIP_K.aimBase + ' + 사신의 매력 + 힘의 비 + 이미 싸우는 사이면 ' + DIP_K.aimWar + '. 거절당하면 우호 −' + DIP_K.aimRefuse + ', ' + days(DIP_K.aimCool) + ' 뒤에 다시 청할 수 있습니다.</p></div>';
    },
    on: {
      x: function (el) {
        var x = +el.getAttribute('data-v'), why = aimCan(me, t, x); if (why) return toast(why);
        if (!idleOfficers(b).length) return toast('쉬는 무장이 없습니다');
        pickOfficers({ push: true, title: facName(t) + '군에 출병 요청(' + facName(x) + '군) — 누구를 보낼까요', list: idleOfficers(b), max: 1, hi: 'cha', key: function (o) { return aimTerms(me, t, x, o).p * 100 + o.cha; },
          rt: function (o) { return '<b>' + aimTerms(me, t, x, o).p + '%</b>'; }, rtHead: '받아들일 확률', auto: function () { var e = best(x).o; return e ? [e.id] : []; },
          preview: function (os) { var q = aimTerms(me, t, x, os[0]); return '받아들일 확률 <b>' + q.p + '%</b> · 행동력 ' + AP.treaty + '<br><small>' + aimTermsTxt(q) + '</small>'; } },
          function (os) {
            var r = cmdAim(b, os[0].id, t, x);
            if (!r.ok) { toast(r.msg); return false; }
            if (r.success) { sfx('gong'); talk(L, sayLine(L, 'aimYes'), facName(t) + '군이 ' + days(DIP_K.aimTurns) + ' 동안 ' + facName(x) + '군을 먼저 치기로 했습니다 (사신 ' + os[0].n + ')', 4200); }
            else { sfx('fail'); talk(L, sayLine(L, 'aimNo'), facName(t) + '군이 출병 요청을 물리쳤습니다 — 우호 −' + DIP_K.aimRefuse + ' · ' + days(DIP_K.aimCool) + ' 뒤에 다시 (받아들일 확률 ' + r.p + '%)', 4200); }
            refreshSheet(); afterAction(); requestDraw();
            return true;
          });
      }
    }
  }, true);
}
/* 외교 창: 세력 표 */
""")

# 세력 표: 다른 세력과의 협정을 한 줄 더
s = rep(s, "' · 도시 ' + facCities(f).length + ' · 병력 ' + fmt(dipPower(f)) + '</span></span></button>';",
           "' · 도시 ' + facCities(f).length + ' · 병력 ' + fmt(dipPower(f)) + '</span>' + pactsLine(f, true) + '</span></button>';")
# 세력 하나: 협정 줄 + [출병 요청]
s = rep(s, "(dipBusy(t, me) ? ' · <em>다른 세력과 싸우는 중</em>' : '') + '</div></div></div>' +",
           "(dipBusy(t, me) ? ' · <em>다른 세력과 싸우는 중</em>' : '') + '</div>' + pactsLine(t) + '</div></div>' +")
s = rep(s, "        (p ? cmd('brk', PACT_NAME[p.t] + ' 파기', '우호 −' + DIP_K.breakRel + ' · 다른 세력 −' + DIP_K.breakOthers, false, false) : '') + '</div>' +",
           "        cmd('aim', '출병 요청', aimSub(b, t), false, aimOff(b, t)) +\n"
           "        (p ? cmd('brk', PACT_NAME[p.t] + ' 파기', '우호 −' + DIP_K.breakRel + ' · 다른 세력 −' + DIP_K.breakOthers, false, false) : '') + '</div>' +")
s = rep(s, "      truce: function () { ask('truce'); },\n",
           "      truce: function () { ask('truce'); },\n"
           "      aim: function () { var p0 = pactOf(me, t); if (!p0 || p0.t !== 'ally') return toast('동맹을 맺은 세력에게만 청할 수 있습니다'); if (dipAimOf(t) >= 0) return toast('이미 ' + facName(dipAimOf(t)) + '군을 치기로 했습니다 (' + days(dipAimLeft(t)) + ' 남음)'); flowAim(b, t); },\n")

# ── 지난 열흘: 걸어온 일기토 · AI 가 건 일기토 ──
s = rep(s, "  if (e.t === 'fallen' || e.t === 'news') return 2;\n",
           "  if (e.t === 'fallen' || e.t === 'news' || e.t === 'ask') return 2;\n")
s = rep(s, "  } else if (e.t === 'act') {\n    if ((e.f === G.player || e.tf === G.player) && UI.battleTurn !== G.turn) { UI.battleTurn = G.turn; playBgm('battle'); }   // 내가 얽힌 싸움이면 전투 음악으로\n",
           "  } else if (e.t === 'ask') {                                      // v0.16: 내 부대에 일기토를 걸어왔다 — 답은 내 차례에\n"
           "    if (UI.battleTurn !== G.turn) { UI.battleTurn = G.turn; playBgm('battle'); }\n"
           "    focusNear(e.tc, e.tr, pg(function () {\n"
           "      setCaption(e.f, '<b>' + e.name + '</b> 일기토 신청 → ' + e.tname + ' <small>내 차례에 답합니다</small>', 'hit');\n"
           "      sfx('duel'); floatText(e.c, e.r, '일기토 신청!', '#b5332a', 0, true, -20); flashHex(e.tc, e.tr, '#b5332a');\n"
           "      var au = UMAP[e.id]; if (au && typeof voiceSay === 'function') voiceSay(uLeader(au), 'duel', { at: [e.c, e.r] });\n"
           "      pwait(1500, cb);\n"
           "    }));\n"
           "  } else if (e.t === 'act' && e.res && e.res.kind === 'challenge') {   // v0.16: AI 가 건 일기토(공격 연출 없이)\n"
           "    var mineD = e.f === G.player || e.tf === G.player;\n"
           "    if (mineD && UI.battleTurn !== G.turn) { UI.battleTurn = G.turn; playBgm('battle'); }\n"
           "    focusNear(e.tc, e.tr, pg(function () {\n"
           "      var r = e.res;\n"
           "      setCaption(e.f, resultMsg(e.name, r), e.tf === G.player ? 'hit' : '');\n"
           "      floatText(r.ac, r.ar, '일기토 신청', '#1b1a18', 0, true, -20);\n"
           "      if (!r.accepted) { sfx('miss'); floatText(r.c, r.r, '받지 않음 · 기력 -' + r.mor, '#2f4f6f', 320, false, 22); pwait(1100 * k, cb); return; }\n"
           "      if (r.duelRec && r.duel && !P.skip && mineD) {                // 내 군단이 얽혔으면 처음부터 그려 보인다\n"
           "        duelReplay(r.duelRec, { sub: e.name + ' 대 ' + (r.tname || ''), out: duelOutHtml(null, r.duel, e.name, r.tname || '') }, pg(function () { pwait(300 * k, cb); }));\n"
           "        return;\n"
           "      }\n"
           "      sfx('duel');\n"
           "      if (r.duel && !r.duel.draw) floatText(r.duel.win ? r.c : r.ac, r.duel.win ? r.r : r.ar, '일기토 패 -' + fmt(r.duel.loss), '#b5332a', 420, true, 22);\n"
           "      else if (r.duel) floatText(r.c, r.r, '비김', '#6a645a', 420, false, 22);\n"
           "      pwait(1300 * k, cb);\n"
           "    }));\n"
           "  } else if (e.t === 'act') {\n    if ((e.f === G.player || e.tf === G.player) && UI.battleTurn !== G.turn) { UI.battleTurn = G.turn; playBgm('battle'); }   // 내가 얽힌 싸움이면 전투 음악으로\n")
# 요약을 닫은 뒤(또는 조용한 열흘이면 곧바로) 걸어온 일기토를 묻는다
s = rep(s, "  if (!n) { toast(dateStr() + ' — 조용한 열흘', 2200); advBrief(1200); return; }\n",
           "  if (!n) { toast(dateStr() + ' — 조용한 열흘', 2200); advBrief(1200); askSoon(900); return; }\n")
s = rep(s, "    onClose: function () { advBrief(300); },\n", "    onClose: function () { advBrief(300); askSoon(500); },\n")

# ── 도움말 ──
s = rep(s, " 약한 상대일수록 응하지 않습니다.</p>' +",
           " 약한 상대일수록 응하지 않습니다.</p>' +\n"
           "  '<p><b>AI 도 일기토를 걸어옵니다</b> — 주장의 무력이 ' + DUEL_K.aiMinWar + ' 이상이고 상대보다 ' + (-DUEL_K.aiLead) + ' 넘게 처지지 않을 때(' + DUEL_K.aiAsk + '%). 내 부대에 걸어오면 [지금 할 일]에 뜨고 내 차례에 답합니다: <b>받아들이면</b> 합마다 수를 직접 고르며 겨루고, <b>받지 않으면</b> 내 부대의 기력이 ' + DUEL_K.refuse + ' 내립니다(답하지 않고 턴을 넘겨도 같습니다). 두 부대가 떨어지면 없던 일이 됩니다.</p>' +")
s = rep(s, " [지금 할 일]에 뜨고, 그 턴 안에 답해야 합니다. AI 끼리는 협정을 맺지 않습니다.</li></ul>' +",
           " [지금 할 일]에 뜨고, 그 턴 안에 답해야 합니다.</li>' +\n"
           "  '<li><b>출병 요청</b>(행동력 ' + AP.treaty + ') — <b>동맹</b>에게 그 동맹과 이웃한 세력 하나를 쳐 달라고 청합니다. 받아들이면 ' + (DIP_K.aimTurns * 10) + '일 동안 그 세력을 먼저 노립니다(우리 성에 원군이 들어오는 것은 아닙니다). 받아들일 확률 = 우호 + 바탕 ' + DIP_K.aimBase + ' + 사신의 매력(70을 넘는 만큼 × ' + DIP_K.envoyK + ') + 힘의 비 + 둘이 이미 싸우는 사이면 ' + DIP_K.aimWar + '. 거절당하면 우호 −' + DIP_K.aimRefuse + ', ' + (DIP_K.aimCool * 10) + '일 뒤에 다시.</li>' +\n"
           "  '<li><b>AI 끼리도 손을 잡습니다</b> — 병력이 ' + DIP_K.threat + '배 이상인 같은 이웃을 둔 세력끼리 달이 바뀔 때 ' + DIP_K.aiPact + '%로 정전하고, 정전 중이면 ' + DIP_K.aiPactUp + '%로 동맹으로 올립니다. 외교 창의 세력마다 누구와 협정을 맺었는지 적혀 있습니다.</li></ul>' +")
s = rep(s, "<h3>이번 판에 아직 없는 것</h3><p>외교, 기교·능력 연구,", "<h3>이번 판에 아직 없는 것</h3><p>기교·능력 연구,")
wr('src/ui_panels.js', s)

# ── CSS ──
c = rd('src/style.css')
c += """
/* v0.16 — 걸어온 일기토 · 다른 세력끼리의 협정 */
.dks { display: flex; align-items: stretch; gap: 8px; margin: 10px 0 8px; }
.dks .vs { flex: none; align-self: center; font: 900 20px var(--font-display); color: var(--seal); }
.dk { flex: 1; min-width: 0; display: flex; gap: 8px; align-items: center; padding: 8px; border: 1px solid #1b1a1830; background: #ffffff66; }
.dk.me { border-color: var(--seal); }
.dk .por { flex: none; }
.dk b { display: block; font: 900 16px var(--font-display); }
.dk span { display: block; font-size: 13px; } .dk em { font-style: normal; font-weight: 800; color: var(--seal); }
.dk small { display: block; margin-top: 2px; color: var(--dim); font-size: 11.5px; line-height: 1.35; }
.row .ds.px { margin-top: 1px; color: var(--ink-2); white-space: normal; }
.row .ds.px em, .diph .ds.px em { font-style: normal; color: var(--seal); font-weight: 700; }
.diph .ds.px { display: block; margin-top: 4px; font-size: 12.5px; color: var(--ink-2); }
@media (max-width: 380px) { .dks { flex-direction: column; } .dks .vs { align-self: center; } }
"""
wr('src/style.css', c)
print('ok p2_ui16')
