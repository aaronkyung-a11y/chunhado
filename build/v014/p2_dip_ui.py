#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.14 — 외교의 화면(ui_panels.js · style.css · voice.js).
   · 거점 창의 [인재] 탭에 [외교] — 세력 표(우호 막대 · 협정) → 세력 하나의 창(친선 · 정전 · 동맹 · 파기) → 사신 고르기(설전으로 담판)
   · AI 가 청해 온 제안: '지금 할 일'과 외교 창 맨 위에 뜨고, 받거나 물리친다
   · 협정을 맺은 세력의 부대 · 거점을 눌렀을 때: 칠 수 없는 까닭을 적는다
   · 도움말"""
import os, io
ROOT = os.environ.get('CH_ROOT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
def rd(n): return io.open(os.path.join(ROOT, 'src', n), encoding='utf-8').read()
def wr(n, s): io.open(os.path.join(ROOT, 'src', n), 'w', encoding='utf-8').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:70])
    return s.replace(a, b)

s = rd('ui_panels.js')
# ---------- 말: 사신 · 저쪽 군주의 답 ----------
s = rep(s, "  csup:     { W: ['{x}{으로} 병력과 물자를 보내겠소.'], C: ['{x}{으로} 병력과 물자를 보내겠습니다.'], L: ['…'] }\n};",
           "  csup:     { W: ['{x}{으로} 병력과 물자를 보내겠소.'], C: ['{x}{으로} 병력과 물자를 보내겠습니다.'], L: ['…'] },\n"
           "  envoy:    { W: ['말솜씨는 없으나, 다녀오겠소.', '{x} 공을 만나고 오겠소.'], C: ['사신의 소임을 다하겠습니다.', '{x} 공을 뵙고 오겠습니다.'], L: ['내가 직접 만나 보겠다.'] },\n"
           "  dipYes:   { W: ['좋소. 그리합시다.'], C: ['뜻을 받들겠습니다.'], L: ['좋소. 그리합시다.', '귀공의 뜻, 잘 알았소.'] },\n"
           "  dipNo:    { W: ['그럴 수는 없소.'], C: ['받아들이기 어렵습니다.'], L: ['그럴 수는 없소.', '아직은 때가 아니오.'] },\n"
           "  dipGift:  { W: ['후한 선물이오. 잊지 않겠소.'], C: ['후의에 감사드립니다.'], L: ['후한 선물, 고맙게 받겠소.'] },\n"
           "  dipAsk:   { W: ['서로 칼을 거둡시다.'], C: ['서로 칼을 거두기를 청합니다.'], L: ['서로 칼을 거둡시다. 어떻소?', '손을 잡읍시다. 어떻소?'] },\n"
           "  dipBreak: { W: ['이 일은 잊지 않겠소!'], C: ['신의를 저버리시다니…'], L: ['신의를 저버리다니… 이 일은 잊지 않겠소.'] }\n};")

DIP_UI = r'''
/* ================= 외교(v0.14) ================= */
function relBar(v) { return '<span class="relbar" title="우호 ' + v + '"><i class="' + (v >= 60 ? 'hi' : (v < 20 ? 'lo' : '')) + '" style="width:' + v + '%"></i><em style="left:' + DIP_K.rel0 + '%"></em></span>'; }
function pactChip(a, b) { var p = pactOf(a, b); return p ? '<span class="pact ' + p.t + '">' + PACT_NAME[p.t] + ' <small>' + days(p.until - G.turn) + '</small></span>' : ''; }
function facLord(f) { return off(G.factions[f].lord); }
function dipFacs() {
  var me = G.player, out = [];
  for (var i = 0; i < G.factions.length; i++) if (i !== me && G.factions[i].alive) out.push(i);
  return out.sort(function (a, b) { return (pactOn(me, b) ? 1 : 0) - (pactOn(me, a) ? 1 : 0) || relOf(me, b) - relOf(me, a) || dipPower(b) - dipPower(a); });
}
/* 외교 단추 아래의 한 줄 */
function dipSub() {
  var n = dipOffers().length, me = G.player, ps = dipFacs().filter(function (f) { return pactOn(me, f); }).length;
  return n ? '청해 온 제안 ' + n : (ps ? '협정 ' + ps : '친선 · 정전 · 동맹');
}
function termsTxt(x) {
  function sg(v) { return (v > 0 ? '+' : (v < 0 ? '−' : '')) + Math.abs(v); }
  return '우호 ' + x.rel + ' · 바탕 ' + sg(x.base) + (x.envoy ? ' · 사신 ' + sg(x.envoy) : '') + (x.pow ? ' · 힘의 비 ' + sg(x.pow) : '') + (x.busy ? ' · 저쪽이 싸우는 중 ' + sg(x.busy) : '');
}
/* 청해 온 제안에 답한다 */
function flowDipOffer(from, kind) {
  var L = facLord(from), me = G.player;
  showDialog({
    render: function () {
      var live = dipOffers().some(function (x) { return x.from === from && x.kind === kind; });
      return dlgHead(facName(from) + '군의 제안 — ' + PACT_NAME[kind]) + '<div class="dlg-b">' + sayRow(L, sayLine(L, 'dipAsk'), PACT_NAME[kind] + ' ' + days(kind === 'ally' ? DIP_K.allyTurns : DIP_K.truceTurns)) +
        '<div class="stats dipst"><div><span>우호</span><b>' + relOf(me, from) + ' <small>' + relWord(relOf(me, from)) + '</small></b></div><div><span>병력</span><b>' + fmt(dipPower(me)) + ' : ' + fmt(dipPower(from)) + '</b></div></div>' +
        '<p class="note">' + (kind === 'ally' ? '동맹' : '정전') + '을 맺으면 ' + days(kind === 'ally' ? DIP_K.allyTurns : DIP_K.truceTurns) + ' 동안 서로의 부대 · 거점 · 시설을 칠 수 없습니다. 물리치면 우호 −' + DIP_K.refuse + '. <b>이번 턴 안에</b> 답하지 않으면 없던 일이 됩니다.</p>' +
        (live ? '<div class="cmds two"><button class="cmd pri" type="button" data-a="yes"><b>받아들인다</b></button><button class="cmd" type="button" data-a="no"><b>물리친다</b></button></div>' : '<p class="note bad">이미 지나간 제안입니다</p>') + '</div>';
    },
    on: {
      yes: function () { var r = dipAnswer(from, kind, true); closeDialog(); if (!r.ok) return toast(r.msg); sfx('gong'); talk(L, sayLine(L, 'dipYes'), facName(from) + '군과 ' + (kind === 'ally' ? '동맹을 맺었습니다' : '정전했습니다') + ' — ' + days(pactLeft(me, from))); refreshSheet(); afterAction(); },
      no: function () { var r = dipAnswer(from, kind, false); closeDialog(); if (!r.ok) return toast(r.msg); sfx('ui'); toast(facName(from) + '군의 제안을 물리쳤습니다 (우호 −' + DIP_K.refuse + ')'); refreshSheet(); afterAction(); }
    }
  }, true);
}
/* 외교 창: 세력 표 */
function flowDip(b) {
  var me = G.player;
  showDialog({
    render: function () {
      var fs = dipFacs(), ofs = dipOffers(), h = dlgHead('외교 — ' + b.n) + '<div class="dlg-b"><p class="note">금 ' + fmt(b.gold) + ' · 행동력 ' + G.factions[me].ap + ' · 사신은 ' + b.n + '의 쉬는 무장(' + idleOfficers(b).length + '명)</p>';
      if (ofs.length) {
        h += '<div class="sec">청해 온 제안 <em class="cnt">' + ofs.length + '</em></div><div class="rows">';
        ofs.forEach(function (x) { h += '<button class="row offer" type="button" data-a="offer" data-v="' + x.from + '" data-k="' + x.kind + '">' + porTag(facLord(x.from), 'sm') + '<span class="mid"><span class="nm">' + facChip(x.from) + ' ' + PACT_NAME[x.kind] + '을 청해 왔습니다</span><span class="ds">이번 턴 안에 답해야 합니다</span></span><span class="rt hi">답하기</span></button>'; });
        h += '</div>';
      }
      h += '<div class="sec">세력 <em class="cnt">' + fs.length + '</em></div><div class="rows dipl">';
      fs.forEach(function (f) {
        var v = relOf(me, f);
        h += '<button class="row" type="button" data-a="f" data-v="' + f + '">' + porTag(facLord(f), 'sm') + '<span class="mid"><span class="nm">' + facChip(f) + pactChip(me, f) + '</span><span class="ds">' + relBar(v) + '<b>' + v + '</b> ' + relWord(v) + ' · 도시 ' + facCities(f).length + ' · 병력 ' + fmt(dipPower(f)) + '</span></span></button>';
      });
      return h + '</div><p class="note">우호는 처음 ' + DIP_K.rel0 + '. 친선으로 올리고, 치면 내려가며, 달마다 ' + DIP_K.rel0 + ' 쪽으로 ' + DIP_K.drift + '씩 돌아갑니다(협정 중에는 그대로).</p></div>';
    },
    on: {
      f: function (el) { flowDipFac(b, +el.getAttribute('data-v')); },
      offer: function (el) { flowDipOffer(+el.getAttribute('data-v'), el.getAttribute('data-k')); }
    }
  });
}
/* 세력 하나와의 외교 */
function flowDipFac(b, t) {
  var me = G.player, L = facLord(t);
  function bestEnvoy(kind) { var os = idleOfficers(b), best = null, bp = -1; os.forEach(function (o) { var p = dipChance(me, t, kind, o); if (p > bp) { bp = p; best = o; } }); return { o: best, p: Math.max(0, bp) }; }
  function askSub(kind) {
    if (kind === 'ally' && !pactOf(me, t) && relOf(me, t) < DIP_K.allyRel || (kind === 'ally' && pactOf(me, t) && pactOf(me, t).t !== 'ally' && relOf(me, t) < DIP_K.allyRel)) return '우호 ' + DIP_K.allyRel + ' 이상 필요';      // 단추에는 짧게
    var why = dipCan(me, t, kind); if (why) return why.replace(' 청할 수 있습니다', '');
    if (!idleOfficers(b).length) return '쉬는 무장이 없습니다';
    return '받아들일 확률 최고 <em class="pc">' + bestEnvoy(kind).p + '%</em> · 행 ' + AP.treaty;
  }
  function ask(kind) {
    var why = dipCan(me, t, kind); if (why) return toast(why);
    pickOfficers({ push: true, title: facName(t) + '군에 ' + PACT_NAME[kind] + ' 제안 — 누구를 보낼까요', list: idleOfficers(b), max: 1, hi: kind === 'ally' ? 'cha' : 'pol', key: function (o) { return dipChance(me, t, kind, o) * 100 + (kind === 'ally' ? o.cha : o.pol); },
      rt: function (o) { return '<b>' + dipChance(me, t, kind, o) + '%</b>'; }, rtHead: '받아들일 확률', auto: function () { var e = bestEnvoy(kind).o; return e ? [e.id] : []; },
      preview: function (os) { var x = dipTerms(me, t, kind, os[0]); return '받아들일 확률 <b>' + x.p + '%</b> · ' + PACT_NAME[kind] + ' ' + days(kind === 'ally' ? DIP_K.allyTurns : DIP_K.truceTurns) + '<br><small>' + termsTxt(x) + '</small>'; },
      alt: { label: '설전',
        can: function (os) { return dipTalkOk(b, os[0], t, kind) && G.factions[me].ap >= AP.treaty; },
        why: function (os) { var p0 = dipChance(me, t, kind, os[0]); return G.factions[me].ap < AP.treaty ? '행동력이 부족합니다' : (p0 >= 100 ? '설전이 필요 없습니다' : '말이 통할 형편이 아닙니다 — 받아들일 확률이 ' + DIP_K.talkMin + '% 이상일 때만 설전을 걸 수 있습니다'); },
        go: function (os) { flowDipTalk(b, os[0], t, kind); } } },
      function (os) {
        var r = cmdTreaty(b, os[0].id, t, kind);
        if (!r.ok) { toast(r.msg); return false; }
        dipTold(r, t, kind);
        return true;
      });
  }
  showDialog({
    render: function () {
      var v = relOf(me, t), p = pactOf(me, t), idle = idleOfficers(b), giftAdd = idle.length ? DIP_K.giftBase + Math.round(idle.slice().sort(function (x, y) { return y.pol - x.pol; })[0].pol / DIP_K.giftPol) : 0;
      var gifted = dipOf().gift[me + ':' + t] === G.turn;
      var giftSub = gifted ? '이번 턴에는 이미 보냈습니다' : (v >= 100 ? '우호가 가장 높습니다' : (!idle.length ? '쉬는 무장이 없습니다' : (b.gold < DIP_K.giftGold ? '금 부족' : '금 ' + fmt(DIP_K.giftGold) + ' · 행 ' + AP.gift + ' · 우호 +' + giftAdd + ' 안팎')));
      function cmd(a, name, sub, pri, offc) { return '<button class="cmd' + (pri ? ' pri' : '') + (offc ? ' off' : '') + '" type="button" data-a="' + a + '"><b>' + name + '</b><small>' + sub + '</small></button>'; }
      return dlgHead(facName(t) + '군과의 외교') + '<div class="dlg-b"><div class="diph">' + porTag(L, 'md') + '<div><div class="nm">' + facChip(t) + ' <b>' + L.n + '</b>' + pactChip(me, t) + '</div><div class="rl">' + relBar(v) + '<b>' + v + '</b> ' + relWord(v) + '</div>' +
        '<div class="pw">병력 ' + fmt(dipPower(me)) + ' : ' + fmt(dipPower(t)) + ' · 도시 ' + facCities(me).length + ' : ' + facCities(t).length + (dipBusy(t, me) ? ' · <em>다른 세력과 싸우는 중</em>' : '') + '</div></div></div>' +
        '<div class="cmds">' + cmd('gift', '친선', giftSub, false, gifted || v >= 100 || !idle.length || b.gold < DIP_K.giftGold) +
        cmd('truce', '정전 제안', askSub('truce'), !p, !!dipCan(me, t, 'truce') || !idle.length) + cmd('ally', '동맹 제안', askSub('ally'), false, !!dipCan(me, t, 'ally') || !idle.length) +
        (p ? cmd('brk', PACT_NAME[p.t] + ' 파기', '우호 −' + DIP_K.breakRel + ' · 다른 세력 −' + DIP_K.breakOthers, false, false) : '') + '</div>' +
        '<p class="note">' + (p ? '<b>' + PACT_NAME[p.t] + ' 중</b> — ' + days(p.until - G.turn) + ' 남았습니다. 그동안 서로의 부대 · 거점 · 시설을 칠 수 없습니다.' : '정전 ' + days(DIP_K.truceTurns) + ' · 동맹 ' + days(DIP_K.allyTurns) + '(우호 ' + DIP_K.allyRel + ' 이상). 맺으면 서로의 부대 · 거점 · 시설을 칠 수 없습니다. 거절당하면 우호 −' + DIP_K.refuse + ', ' + days(DIP_K.cool) + ' 뒤에 다시 청할 수 있습니다.') + '</p></div>';
    },
    on: {
      gift: function () {
        var r0 = cmdGiftCheck(b, t); if (r0) return toast(r0);
        pickOfficers({ push: true, title: facName(t) + '군에 선물 — 누구를 보낼까요', list: idleOfficers(b), max: 1, hi: 'pol', key: function (o) { return o.pol; },
          rt: function (o) { return '우호 <b>+' + (DIP_K.giftBase + Math.round(o.pol / DIP_K.giftPol)) + '</b>'; }, rtHead: '효과', auto: function () { var L2 = idleOfficers(b).slice().sort(function (x, y) { return y.pol - x.pol; }); return L2.length ? [L2[0].id] : []; },
          preview: function (os) { return '금 ' + fmt(DIP_K.giftGold) + ' · 행동력 ' + AP.gift + ' → 우호 <b>+' + (DIP_K.giftBase + Math.round(os[0].pol / DIP_K.giftPol)) + '</b> <small>(' + DIP_K.giftBase + ' + 정치 ÷ ' + DIP_K.giftPol + ')</small>'; } },
          function (os) {
            var v0 = relOf(me, t), r = cmdGift(b, os[0].id, t);
            if (!r.ok) { toast(r.msg); return false; }
            sfx('coin'); talk(L, sayLine(L, 'dipGift'), josa(os[0].n, '이가') + ' ' + facName(t) + '군에 선물을 전했습니다 — 우호 ' + v0 + ' → ' + r.rel);
            refreshSheet(); afterAction(); return true;
          });
      },
      truce: function () { ask('truce'); },
      ally: function () { ask('ally'); },
      brk: function () {
        var p = pactOf(me, t); if (!p) return;
        showDialog({
          render: function () { return dlgHead(PACT_NAME[p.t] + ' 파기 — ' + facName(t) + '군') + '<div class="dlg-b"><p>' + facName(t) + '군과의 ' + PACT_NAME[p.t] + '(' + days(p.until - G.turn) + ' 남음)을 깹니다.</p><ul class="plain"><li>' + facName(t) + '군과의 우호 <b class="bad">−' + DIP_K.breakRel + '</b></li><li>다른 모든 세력과의 우호 <b class="bad">−' + DIP_K.breakOthers + '</b></li><li>' + days(DIP_K.breakCool) + ' 동안 ' + facName(t) + '군에 다시 청하지 못합니다</li><li>깨는 그 순간부터 서로 칠 수 있습니다</li></ul><div class="cmds two"><button class="cmd" type="button" data-a="go"><b>깬다</b></button><button class="cmd pri" type="button" data-a="back"><b>그만둔다</b></button></div></div>'; },
          on: { go: function () { var r = cmdBreak(me, t); backDialog(); if (!r.ok) return toast(r.msg); sfx('fail'); talk(L, sayLine(L, 'dipBreak'), facName(t) + '군과의 ' + PACT_NAME[r.kind] + '을 깼습니다 — 우호 ' + relOf(me, t)); refreshDialog(); refreshSheet(); afterAction(); requestDraw(); },
                back: function () { backDialog(); } }
        }, true);
      }
    }
  }, true);
}
function cmdGiftCheck(b, t) {
  if (dipOf().gift[G.player + ':' + t] === G.turn) return '이번 턴에는 이미 선물을 보냈습니다';
  if (relOf(G.player, t) >= 100) return '우호가 이미 가장 높습니다';
  if (b.gold < DIP_K.giftGold) return '금이 부족합니다(금 ' + fmt(DIP_K.giftGold) + ')';
  if (!needAP(G.player, AP.gift)) return '행동력이 부족합니다';
  return '';
}
/* 제안의 결과를 알린다(저쪽 군주의 한마디) */
function dipTold(r, t, kind) {
  var L = facLord(t), me = G.player, o = off(r.o);
  if (r.success) { sfx('gong'); sfx('cheerlate'); talk(L, sayLine(L, 'dipYes'), facName(t) + '군과 ' + (kind === 'ally' ? '동맹을 맺었습니다' : '정전했습니다') + ' — ' + days(pactLeft(me, t)) + ' (사신 ' + o.n + ')', 4200); }
  else { sfx('fail'); talk(L, sayLine(L, 'dipNo'), facName(t) + '군이 ' + PACT_NAME[kind] + ' 제안을 물리쳤습니다 — 우호 −' + DIP_K.refuse + ' · ' + days(DIP_K.cool) + ' 뒤에 다시', 4200); }
  refreshSheet(); afterAction(); requestDraw();
}
/* 설전으로 담판 */
function flowDipTalk(b, o, t, kind) {
  var S = dipTalkNew(b, o, t, kind), r = null;
  duelOpen(S, 'a', { sub: facName(t) + '군과 ' + PACT_NAME[kind] + ' 담판 · 그냥 청하면 ' + S.dp + '%',
    onEnd: function () {
      r = cmdTreaty(b, o.id, t, kind, S);
      if (!r.ok) return '<p class="bad">' + r.msg + '</p>';
      return r.success ? '<p><b>' + facName(t) + '군과 ' + (kind === 'ally' ? '동맹을 맺었습니다' : '정전했습니다') + '</b> — ' + days(pactLeft(G.player, t)) + '</p>' : '<p><b>' + facName(t) + '군은 뜻을 굽히지 않았습니다</b> — 우호 −' + DIP_K.refuse + ' · ' + days(DIP_K.cool) + ' 뒤에 다시 청할 수 있습니다</p>';
    } },
    function () { if (r && r.ok && r.success) sfx('cheer'); if (MODAL) refreshDialog(); refreshSheet(); afterAction(); requestDraw(); });
}
'''
s = rep(s, "function flowRecruit(b) {\n", DIP_UI.strip('\n') + "\nfunction flowRecruit(b) {\n")
# 거점 창의 [인재] 탭에 [외교]
s = rep(s, "cmd('reward', '포상', '금 ' + COST.reward + ' · 행 ' + AP.reward) +", "cmd('reward', '포상', '금 ' + COST.reward + ' · 행 ' + AP.reward) + cmd('dip', '외교', dipSub(), dipOffers().length > 0) +")
s = rep(s, "    reward: function () { flowReward(B()); }, move: function () { flowMove(B()); }, captive: function () { flowCaptive(B()); },",
           "    reward: function () { flowReward(B()); }, move: function () { flowMove(B()); }, captive: function () { flowCaptive(B()); }, dip: function () { flowDip(B()); },")
# 지금 할 일: 청해 온 제안
s = rep(s, "  pendingUnits().forEach(function (u) {\n    if (seen[u.id]) return; seen[u.id] = 1;",
           "  dipOffers().forEach(function (x) {                            // v0.14: AI 가 청해 온 정전 · 동맹\n"
           "    out.push({ cls: 'cool', ic: '盟', t: facName(x.from) + '군이 ' + PACT_NAME[x.kind] + '을 청해 왔습니다', s: '이번 턴 안에 답해야 합니다 · 우호 ' + relOf(f, x.from), go: ['dip', x.from, x.kind], lb: '답하기', say: facName(x.from) + '군이 ' + PACT_NAME[x.kind] + '을 청해 왔습니다. 답을 정하십시오.' });\n"
           "  });\n"
           "  pendingUnits().forEach(function (u) {\n    if (seen[u.id]) return; seen[u.id] = 1;")
s = rep(s, "  else if (g[0] === 'corpsnew') showCorpsNew();\n}", "  else if (g[0] === 'corpsnew') showCorpsNew();\n  else if (g[0] === 'dip') flowDipOffer(g[1], g[2]);\n}")
# 협정을 맺은 세력을 눌렀을 때: 칠 수 없는 까닭
s = rep(s, "function targetActions(u, t) {\n  var out = [], d = hdist(u.c, u.r, t.c, t.r), rg = uRange(u), i;\n",
           "function targetActions(u, t) {\n  var out = [], d = hdist(u.c, u.r, t.c, t.r), rg = uRange(u), i;\n"
           "  var tf0 = t.kind === 'unit' ? t.u.f : (t.b ? t.b.owner : -1), pk = tf0 >= 0 ? pactOf(u.f, tf0) : null;\n"
           "  if (pk) return [{ kind: 'attack', label: PACT_NAME[pk.t] + ' 중', sub: days(pk.until - G.turn) + ' 남음 · 칠 수 없습니다', ok: false, pri: true }];      // v0.14: 협정을 맺은 세력\n")
s = rep(s, "          if (t.kind === 'unit' && (TACTICS[x.type] || []).length) h += '<button class=\"act\" type=\"button\" data-a=\"tacinfo\"><b>전법 풀이</b></button>';",
           "          if (t.kind === 'unit' && (TACTICS[x.type] || []).length && !pactOn(x.f, t.u.f)) h += '<button class=\"act\" type=\"button\" data-a=\"tacinfo\"><b>전법 풀이</b></button>';      // 칠 수 없는 상대에게는 풀이도 내지 않는다")
# 남의 부대 · 거점 창의 이름 옆에 협정 딱지
s = rep(s, "'<div><div class=\"sh-title\">' + uName(x) + ' ' + facChip(x.f) + '</div>", "'<div><div class=\"sh-title\">' + uName(x) + ' ' + facChip(x.f) + pactChip(G.player, x.f) + '</div>")
s = rep(s, "'<div><div class=\"sh-title\">' + b.n + ' ' + facChip(b.owner) + '</div>", "'<div><div class=\"sh-title\">' + b.n + ' ' + facChip(b.owner) + pactChip(G.player, b.owner) + '</div>")
# 도움말
s = rep(s, "'<h3>소리</h3>", "'<h3>외교</h3><p>거점 창의 [인재] 탭 → <b>[외교]</b>. 사신은 그 거점의 쉬는 무장이고, 금도 그 거점에서 나갑니다.</p><ul>' +\n"
           "  '<li><b>우호</b>(0~100, 처음 ' + DIP_K.rel0 + ') — 세력 사이의 값입니다. <b>친선</b>(금 ' + DIP_K.giftGold + ' · 행동력 ' + AP.gift + ')으로 ' + DIP_K.giftBase + ' + 사신의 정치 ÷ ' + DIP_K.giftPol + '만큼 오르고(한 세력에 턴마다 한 번), 칠 때마다 −' + DIP_K.hitRel + ', 거점을 빼앗으면 −' + DIP_K.fallRel + ' 더, 달마다 ' + DIP_K.rel0 + ' 쪽으로 ' + DIP_K.drift + '씩 돌아갑니다.</li>' +\n"
           "  '<li><b>정전</b>(' + (DIP_K.truceTurns * 10) + '일) · <b>동맹</b>(' + (DIP_K.allyTurns * 10) + '일, 우호 ' + DIP_K.allyRel + ' 이상) — 맺으면 그동안 서로의 부대 · 거점 · 시설을 칠 수 없고 계략도 걸 수 없으며, 서로의 무장에게 등용을 권하지 않습니다. AI 도 지킵니다.</li>' +\n"
           "  '<li><b>받아들일 확률</b> = 우호 + 바탕(정전 ' + DIP_K.truceBase + ' · 동맹 ' + DIP_K.allyBase + ') + 사신의 능력(정전은 정치, 동맹은 매력이 70을 넘는 만큼 × ' + DIP_K.envoyK + ') + 힘의 비(우리가 두 배면 +' + DIP_K.powK + ', 저쪽이 두 배면 −' + DIP_K.powK + ') + 저쪽이 다른 세력과 싸우는 중이면 ' + DIP_K.busy + '. 거절당하면 우호 −' + DIP_K.refuse + ', ' + (DIP_K.cool * 10) + '일 뒤에 다시 청할 수 있습니다.</li>' +\n"
           "  '<li><b>설전으로 담판</b> — 확률이 ' + DIP_K.talkMin + '% 이상이면 주사위 대신 말로 겨룰 수 있습니다. 상대는 저쪽의 군사(없으면 지력이 가장 높은 무장)이고, 받아들일 마음이 적을수록 오래 버팁니다.</li>' +\n"
           "  '<li><b>파기</b> — 그 세력과의 우호 −' + DIP_K.breakRel + ', 다른 모든 세력과의 우호 −' + DIP_K.breakOthers + ', ' + (DIP_K.breakCool * 10) + '일 동안 그 세력에 다시 청하지 못합니다. 깨는 순간부터 서로 칠 수 있습니다.</li>' +\n"
           "  '<li>AI 세력이 달이 바뀔 때 <b>정전 · 동맹을 청해 오기도</b> 합니다(약하거나 다른 싸움에 바쁜 세력, 우호가 높은 세력). [지금 할 일]에 뜨고, 그 턴 안에 답해야 합니다. AI 끼리는 협정을 맺지 않습니다.</li></ul>' +\n"
           "  '<h3>소리</h3>")
wr('ui_panels.js', s)

# ---------- style.css ----------
s = rd('style.css')
s += '''
/* ---------- 외교(v0.14) ---------- */
.relbar { position: relative; display: inline-block; width: 64px; height: 7px; margin-right: 6px; background: #1b1a1814; border: 1px solid #1b1a1840; vertical-align: 1px; }
.relbar > i { display: block; height: 100%; background: var(--ink-2); }
.relbar > i.hi { background: #2f6f4f; } .relbar > i.lo { background: var(--seal); }
.relbar > em { position: absolute; top: -2px; bottom: -2px; width: 1px; background: #1b1a1870; }
.pact { display: inline-block; margin-left: 6px; padding: 1px 6px; font: 700 11.5px var(--font-body); color: #fff; background: #2f4f6f; border-radius: 2px; vertical-align: 1px; }
.pact.ally { background: #2f6f4f; } .pact small { font-weight: 500; opacity: .9; }
.diph { display: flex; gap: 10px; align-items: center; margin: 2px 0 10px; }
.diph .por { flex: none; }
.diph .nm { font-size: 15px; } .diph .nm b { font-family: var(--font-display); font-weight: 900; }
.diph .rl { margin-top: 5px; font-size: 13.5px; } .diph .rl .relbar { width: 110px; }
.diph .pw { margin-top: 4px; font-size: 12.5px; color: var(--ink-2); } .diph .pw em { color: var(--seal); font-style: normal; font-weight: 700; }
.rows.dipl .row .ds b { margin-right: 2px; }
.row.offer { border-left: 3px solid #2f4f6f; }
.stats.dipst { margin: 8px 0; }
.cmds.two { grid-template-columns: 1fr 1fr; }
ul.plain { margin: 6px 0 12px 18px; padding: 0; font-size: 14px; line-height: 1.6; }
'''
wr('style.css', s)

# ---------- voice.js: 사신으로 떠나는 말에는 '명령 받음' ----------
p = os.path.join(ROOT, 'src', 'voice.js'); s = io.open(p, encoding='utf-8').read()
s = rep(s, "catk: 'order', csup: 'order' };", "catk: 'order', csup: 'order', envoy: 'order' };")
io.open(p, 'w', encoding='utf-8').write(s)
print('p2_dip_ui ok')
