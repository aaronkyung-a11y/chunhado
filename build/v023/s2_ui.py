# -*- coding: utf-8 -*-
"""v0.23 (2) 화면: 시대 고르기 · 나이 · 후계 정하기 · 후계 알림 · 도움말.   python3 build/v023/s2_ui.py"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s)


def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:70], s.count(a))
    return s.replace(a, b)


def cut(s, a, b, new):                    # a 로 시작해 b 바로 앞까지를 new 로 바꾼다
    i = s.index(a); j = s.index(b, i)
    assert s.count(a) == 1
    return s[:i] + new + s[j:]


u = rd('src/ui_panels.js')
u = rep(u, "  $('tVer').textContent = GAME_VERSION + ' · 삼국지 천하도 · 194년 군웅할거';", "  $('tVer').textContent = GAME_VERSION + ' · 삼국지 천하도';")

# ───────── 시대 고르기 ─────────
u = cut(u, "function showFactionSelect() {", "function showIntro() {", r"""function showFactionSelect() {
  var st = { f: -1, scen: UI.scenPick || '194' }, S = null, info = [];
  function load() {                                              // v0.23: 시대를 바꾸면 그 시대의 세력으로 다시 채운다(판은 건드리지 않는다)
    S = scenarioPeek(st.scen);
    info = S.factions.map(function (sf, i) {
      var os = S.officers.filter(function (o) { return o.f === i; }), lord = null, tr = startTroops(i, S);
      os.forEach(function (o) { if (o.n === sf.n) lord = o; });
      return { i: i, n: sf.n, color: sf.color, cities: sf.cities, cnt: os.length, lord: lord, troops: tr, peace: peaceFor(tr), desc: sf.desc || FACTION_DESC[sf.n] || '' };
    });
  }
  load();
  showDialog({
    render: function () {
      var h = dlgHead(S.year + '년 ' + S.name + ' — 군주를 고르세요') + '<div class="dlg-b"><div class="scn">';
      scenarioList().forEach(function (x) { h += '<button type="button" class="scb' + (x.id === st.scen ? ' on' : '') + '" data-a="scen" data-v="' + x.id + '"' + (x.id === st.scen ? ' aria-pressed="true"' : '') + '><b>' + x.year + '</b><span>' + x.name + '</span></button>'; });
      h += '</div><p class="scsub"><b>' + S.han + '</b> ' + S.sub + '</p><div class="rows">';
      for (var i = 0; i < info.length; i++) {
        var x = info[i], ct = x.cities.length > 4 ? x.cities.slice(0, 3).join('·') + ' 외 ' + (x.cities.length - 3) : x.cities.join('·');
        h += '<button class="row' + (st.f === x.i ? ' sel' : '') + '" type="button" data-a="f" data-v="' + x.i + '">' + porTag(x.lord) + '<span class="mid"><span class="nm">' + x.n + ' <span class="chip" style="background:' + x.color + '">' + ct + '</span></span><span class="ds" style="white-space:normal">' + x.desc + '</span><span class="ds fs-st">병력 <b>' + fmt(x.troops) + '</b> · 초반 보호 <b' + (x.peace > PEACE_ALL ? ' class="ok"' : '') + '>' + months(x.peace) + '</b></span></span><span class="rt">무장<br><b>' + x.cnt + '</b></span></button>';
      }
      return h + '</div></div><div class="dlg-f"><div class="pv">' + (st.f >= 0 ? '<b>' + info[st.f].n + '</b> · 도시 ' + info[st.f].cities.length + ' · 무장 ' + info[st.f].cnt + '명<br>병력 ' + fmt(info[st.f].troops) + ' · 초반 보호 ' + months(info[st.f].peace) + '(' + dateOfTurn(info[st.f].peace, S.year) + '까지)' : '시대와 군주를 고르세요') + '</div><button class="btn pri" type="button" data-a="go"' + (st.f < 0 ? ' disabled' : '') + '>시작</button></div>';
    },
    on: {
      scen: function (el) { st.scen = el.getAttribute('data-v'); st.f = -1; UI.scenPick = st.scen; load(); sfx('ui'); refreshDialog(); },
      f: function (el) { st.f = +el.getAttribute('data-v'); refreshDialog(); },
      go: function () { if (st.f < 0) return; closeDialog(); keepPrev(); newGame(st.f, undefined, st.scen); saveGame(); startGame(); sfx('gong'); cinePlay('opening', { cap: S.han, sub: S.year + '년 — ' + S.sub }, function () { showIntro(); }); }      // v0.19: 오프닝 영상(끄면 곧바로 다음 창)
    }
  });
}
""")
u = rep(u, "'<div><p>' + FACTION_DESC[F.name] + '</p>", "'<div><p>' + ((SCENARIO.factions[G.player] && SCENARIO.factions[G.player].desc) || FACTION_DESC[F.n0 || F.name] || '') + '</p>")

# ───────── 무장 창: 나이 · 후계 ─────────
u = rep(u, "  var where = o.st === 'free' ? '재야 (' + G.bases[o.loc].n + ')' :", "  var where = o.st === 'dead' ? '세상을 떠남' : o.st === 'free' ? '재야 (' + G.bases[o.loc].n + ')' :")
u = rep(u, "    '<div class=\"stats\"><div><span>소재</span><b>' + where + '</b></div>' + (o.f >= 0 ?", "    '<div class=\"stats\">' + lifeCell(o) + '<div><span>소재</span><b>' + where + '</b></div>' + (o.f >= 0 ?")
u = rep(u, "    (servedF(o).length ? '<p class=\"note\">섬겼던 세력 — ' + servedTxt(o) + '</p>' : '');\n}",
        "    heirNote(o) +\n    (servedF(o).length ? '<p class=\"note\">섬겼던 세력 — ' + servedTxt(o) + '</p>' : '');\n}")
u = cut(u, "function showOfficer(o) {", "/* v0.18 무장 카드:", r"""/* v0.23: 나이(세는나이) · 태어난 해. 사서에 없어 어림한 해에는 '추정'을 붙인다. 세상을 떠난 사람은 생몰년 */
function lifeCell(o) {
  if (!o.by) return '';
  var est = (o.e & 1) ? ' · 추정' : '', so = SCENARIO.officers[o.id], dyr = o.died || (so && so.n === o.n ? so.hd : 0);
  if (o.st === 'dead') return '<div><span>생몰</span><b>' + o.by + (dyr ? ' ~ ' + dyr : '') + '<small>' + (dyr ? '향년 ' + (dyr - o.by + 1) + '세' : '') + est + '</small></b></div>';
  return '<div><span>나이</span><b>' + ageOf(o) + '세' + (o.sick ? ' <em class="sick">병석</em>' : '') + '<small>' + o.by + '년생' + est + '</small></b></div>';
}
function heirTag(o) { return (o.f >= 0 && G.factions[o.f].heir === o.id && heirOk(o, o.f)) ? '후계' : ''; }
function roleTag(o) { var a = advTag(o), h = heirTag(o); return a && h ? a + '·' + h : (a || h); }
function heirLine(fc, L, who) {            // 뒤를 이으면 어떻게 되는가 한 줄. who = 군주와의 사이를 따로 적을 때(후계 창: 아들 · 형제 …)
  return (who ? '<b>' + who + '</b>' : (fc.kin ? L.n + '의 혈연' : (fc.house ? L.n + '의 ' + (fc.rel || '일가') : '<b class="bad">한집안이 아님</b>'))) + ' · 인연이 이어짐 ' + fc.keep + '명' + (fc.fam.length ? ' · <b class="bad">일가 반발 ' + fc.fam.length + '명</b>' : '') +
    (fc.vas.length ? ' · <b class="bad">심복 동요 ' + fc.vas.length + '명</b>' : '') + (fc.n ? ' · 그 밖 ' + fc.n + '명은 ' + fc.p + '%로 동요' : '');
}
function heirNote(o) {                     // 내 무장의 창에: 이 사람이 뒤를 이으면
  if (!G || o.f !== G.player || G.aiOnly) return '';
  var F = G.factions[G.player], L = off(F.lord);
  if (L === o) { var cur = heirOf(G.player), nx = heirNext(G.player); return '<p class="note heir">후계 — ' + (cur ? '<b>' + cur.n + '</b>(정해 둠)' : (nx ? '정하지 않음 · 지금 차례는 <b>' + nx.n + '</b>' : '<b class="bad">뒤를 이을 무장이 없습니다</b>')) + '</p>'; }
  if (!heirOk(o, G.player)) return '';
  return '<p class="note heir">' + (F.heir === o.id ? '<b>정해 둔 후계</b> — ' : (heirNext(G.player) === o ? '지금 차례의 후계 — ' : '뒤를 이으면 — ')) + heirLine(heirForecast(G.player, o), L) + '</p>';
}
function showOfficer(o) {
  showDialog({
    render: function () {
      var mine = o.f === G.player && advOk(o, G.player), lordMine = o.f === G.player && isLord(o), isH = !!heirTag(o);
      return dlgHead(o.n + ' ' + (o.f >= 0 ? facChip(o.f) : '') + (advTag(o) ? ' <em class="advt">군사</em>' : '') + (isH ? ' <em class="advt">후계</em>' : '')) + '<div class="dlg-b">' + officerBody(o) + '</div>' +
        (mine ? '<div class="dlg-f"><div class="pv">' + (advTag(o) ? '지금의 <b>군사</b>' : '') + (isH ? (advTag(o) ? ' · ' : '') + '정해 둔 <b>후계</b>' : '') + '</div>' + (advTag(o) ? '' : '<button class="btn" type="button" data-a="adv">군사로 삼기</button>') + '<button class="btn" type="button" data-a="heir">' + (isH ? '후계 풀기' : '후계로 세우기') + '</button></div>'
          : (lordMine ? '<div class="dlg-f"><div class="pv">' + ageOf(o) + '세</div><button class="btn" type="button" data-a="heirs">후계 정하기</button></div>' : ''));
    },
    on: {
      adv: function () { var r = setAdvisor(G.player, o.id); if (!r.ok) return toast(r.msg); sfx('ui'); talk(o, sayLine(o, 'advisor'), josa(o.n, '을를') + ' 군사로 삼았습니다 (지력 ' + o.int + ')'); refreshDialog(); refreshSheet(); },
      heir: function () { var r = cmdHeir(o.id); if (!r.ok) return toast(r.msg); sfx('ui'); saveGame(); toast(r.off ? josa(o.n, '을를') + ' 후계에서 풀었습니다' : josa(o.n, '을를') + ' 후계로 세웠습니다'); refreshDialog(); refreshSheet(); },
      heirs: function () { showHeir(); }
    }
  }, true);                                              // 목록 같은 창 위에서 열었으면 ×로 그 창에 돌아간다
}
/* v0.23 후계 정하기: 뒤를 이을 차례대로 늘어놓고, 누가 이으면 어떻게 될지 줄마다 적는다. 누르면 정하고, 다시 누르면 푼다 */
function showHeir() {
  var f = G.player;
  showDialog({
    render: function () {
      var F = G.factions[f], L = off(F.lord), rk = heirRank(f), cur = heirOf(f), CL = ['', '아들', '형제', '혈연', '혈연', '', ''], i;
      var show = rk.slice(0, 14); if (cur && show.indexOf(cur) < 0) show.unshift(cur);
      var h = dlgHead('후계 — ' + L.n + ' ' + ageOf(L) + '세') + '<div class="dlg-b"><p class="note stn">군주가 세상을 떠나면 뒤를 이을 사람입니다. 정해 두지 않으면 <b>아들 → 형제 → 혈연 → 매력이 높은 무장</b>의 차례로 잇습니다. 새 군주가 선대와 <b>한집안</b>(혈연 · 의형제 · 부부)이 아니면 선대의 일가와 심복이 등을 돌릴 수 있습니다.</p><div class="rows hrl">';
      for (i = 0; i < show.length; i++) {
        var o = show[i], cl = heirClass(o, L, { heir: -1 }), fc = heirForecast(f, o), who = fc.kin ? (CL[cl] || '혈연') : (fc.house ? (fc.rel || '일가') : '');
        h += offRow(o, { a: 'pick', sel: cur === o, badge: cur === o ? '후계' : (rk[0] === o ? '지금 차례' : ''), noapt: true, ds: heirLine(fc, L, who), rt: ageOf(o) + '세<br>매력 <b>' + o.cha + '</b>' });
      }
      if (!show.length) h += '<p class="note"><b class="bad">뒤를 이을 무장이 없습니다.</b> 군주가 세상을 떠나면 세력이 사라집니다.</p>';
      return h + '</div></div><div class="dlg-f"><div class="pv">' + (cur ? '정해 둔 후계 <b>' + cur.n + '</b> — 다시 누르면 풉니다' : '정해 둔 후계가 없습니다') + '</div><button class="btn" type="button" data-a="close">닫기</button></div>';
    },
    on: { pick: function (el) { var id = +el.getAttribute('data-v'), r = cmdHeir(id); if (!r.ok) return toast(r.msg); sfx('ui'); saveGame(); toast(r.off ? '후계를 풀었습니다' : josa(off(id).n, '을를') + ' 후계로 세웠습니다'); refreshDialog(); refreshSheet(); } }
  }, true);
}
/* v0.23 후계 알림: 내 군주가 세상을 떠나 뒤를 이었다(core.js 의 succeed 가 G.succ 에 적어 둔다) — 내 차례가 올 때 한 번 보여 준다 */
function succShow(cb) {
  var S = G.succ;
  if (!S || S.seen || G.aiOnly || !off(S.heir) || !off(S.old)) { if (cb) cb(); return; }
  var old = off(S.old), h = off(S.heir);
  showDialog({
    render: function () {
      var rows = S.rows.slice().sort(function (a, b) { return (a[2] - a[1]) - (b[2] - b[1]); }), down = rows.filter(function (r) { return r[2] < r[1]; }).length, up = rows.length - down, i;
      var s = dlgHead('후계 — ' + h.n) + '<div class="dlg-b"><div class="card">' + sceneTag(h) + '<div><p><b>' + josa(old.n, '이가') + '</b> 세상을 떠나고(향년 ' + ageOf(old) + '세) <b>' + josa(h.n, '이가') + '</b> 뒤를 이었습니다.' + (S.named ? ' 미리 정해 둔 후계입니다.' : '') + (S.house ? '' : ' <b class="bad">선대와 한집안이 아닙니다.</b>') + '</p>' +
        '<p class="note">인연이 이어진 무장 ' + S.keep + '명 · 충성이 내린 무장 <b' + (down ? ' class="bad"' : '') + '>' + down + '명</b>' + (up ? ' · 오른 무장 ' + up + '명' : '') + '</p></div></div>';
      if (rows.length) {
        s += '<div class="sec">충성의 변화</div><div class="rows">';
        for (i = 0; i < rows.length; i++) { var o = off(rows[i][0]); if (o) s += offRow(o, { a: 'off', noapt: true, ds: rows[i][3] || '', rt: '<span class="' + (rows[i][2] < rows[i][1] ? 'bad' : 'ok') + '">' + rows[i][1] + ' → <b>' + rows[i][2] + '</b></span>' }); }
        s += '</div>';
      }
      return s + '</div><div class="dlg-f"><div class="pv">이제 <b>' + h.n + '군</b>입니다</div><button class="btn pri" type="button" data-a="close">확인</button></div>';
    },
    onClose: function () { S.seen = 1; saveGame(); if (cb) setTimeout(cb, 80); },
    on: { off: function (el) { var o = off(+el.getAttribute('data-v')); if (o) ocardOpen(o); } }
  });
}
""")
u = rep(u, "(advTag(o) ? ' <em class=\"advt\">군사</em>' : '') + '</h2><button class=\"x\" data-oc=\"x\"", "(advTag(o) ? ' <em class=\"advt\">군사</em>' : '') + (heirTag(o) ? ' <em class=\"advt\">후계</em>' : '') + '</h2><button class=\"x\" data-oc=\"x\"")
u = rep(u, "(cpB.lead === ob[i].id ? '군단장' : advTag(ob[i]))", "(cpB.lead === ob[i].id ? '군단장' : roleTag(ob[i]))")
u = rep(u, "badge: isLord(all[i]) ? '군주' : advTag(all[i]), dim:", "badge: isLord(all[i]) ? '군주' : roleTag(all[i]), dim:")
u = rep(u, "badge: isLord(o) ? '군주' : advTag(o), rt: (o.unit !== null ?", "badge: isLord(o) ? '군주' : roleTag(o), rt: (o.unit !== null ?")
u = rep(u, "nf !== SCENARIO.factions.length || no < 1) return false;", "nf !== scenarioPeek(g.scen).factions.length || no < 1) return false;")
u = rep(u, "  askNext(function () { showReport(REPORT); });      // v0.21: 수송을 마친 무장이 있으면 먼저 묻는다", "  askNext(function () { succShow(function () { showReport(REPORT); }); });      // v0.21: 수송을 마친 무장이 있으면 먼저 묻는다 · v0.23: 군주가 바뀌었으면 그것부터")

# ───────── 도움말 ─────────
u = rep(u, "  '<h3>무장 명부</h3><p>무장은 모두 ' + SCENARIO.officers.length + '명입니다(v0.17에서 124명이 늘었습니다 — 여성 ' + SCENARIO.women.length + '명). 194년에 이미 세력에 있는 사람 말고는 <b>등장 연도</b>가 되어야 나옵니다: 재야의 사람은 그 도시에서 <b>탐색</b>으로 찾고, 군주의 집안사람은 해가 바뀔 때 스스로 찾아옵니다.",
        "  '<h3>시대</h3><p>새 판을 시작할 때 <b>여덟 시대</b> 가운데 하나를 고릅니다 — 184년 황건의 난 · 190년 반동탁 연합 · 194년 군웅할거 · 200년 관도대전 · 207년 삼고초려 · 219년 한중 쟁탈 · 227년 출사표 · 234년 오장원. 시대마다 세력 · 땅 · 무장의 자리가 다릅니다. 그 해에 이미 세상을 떠난 사람은 나오지 않고, 아직 어린 사람은 <b>등장 연도</b>에 나옵니다. 예전 저장은 모두 194년 판입니다.</p>' +\n" +
        "  '<h3>수명</h3><p>무장에게는 <b>태어난 해와 수명</b>이 있습니다(무장 창의 나이 — 태어난 해가 한 살인 세는나이). 사서에 병으로 · 늙어서 죽었다고 적힌 사람은 <b>역사의 그 해</b>에 세상을 떠납니다. 처형 · 전사 · 암살로 죽은 사람은 이 판에서 그 일을 겪지 않으므로 <b>역사보다 ' + LIFE.add + '년 더</b>, 그래도 ' + LIFE.min + '세가 안 되면 <b>' + LIFE.min + '세까지</b> 삽니다. 숨을 거두기 ' + LIFE.warn + '달쯤 앞서 <b>병석에 눕고</b>(알림), 출진 · 이동 중이면 거점에 돌아올 때까지 버팁니다. 태어난 해 · 죽은 해가 사서에 없는 사람이 많습니다 — 벼슬길과 싸움의 기록으로 어림했고, 그런 해에는 <b>추정</b>이라고 적었습니다. 예전 저장을 열면, 이미 수명이 지난 사람은 한꺼번에 떠나지 않고 ' + LIFE.old + '년에 걸쳐 차례로 떠납니다.</p>' +\n" +
        "  '<h3>후계</h3><p>군주가 세상을 떠나면 <b>후계</b>가 뒤를 잇고 세력의 이름이 바뀝니다. 군주의 무장 창(STATUS 창의 초상)에서 <b>후계 정하기</b>, 또는 무장 창의 <b>후계로 세우기</b>로 미리 정할 수 있습니다 — 행동력은 들지 않고 언제든 바꿉니다. 정해 두지 않으면 <b>아들(나이순) → 형제 → 그 밖의 혈연(매력순) → 매력이 높은 무장</b>(통솔 · 정치도 조금 봅니다)의 차례입니다. 뒤를 이을 무장이 한 사람도 없으면 세력은 사라지고 그 땅은 주인 없는 땅이 됩니다.</p>' +\n" +
        "  '<p><b>후계와 충성</b> — 새 군주가 선대와 <b>한집안</b>(혈연 · 의형제 · 부부)이면 선대의 인연이 그대로 이어집니다(의형제 · 심복은 <b>세신</b>이 됩니다 — 충성 100). 한집안이 아니면 인연이 끊겨, 선대의 <b>일가</b>(혈연 · 의형제 · 부부 · 인척)는 충성이 ' + HEIR.kin[0] + ' ~ ' + HEIR.kin[1] + ' 내리고, <b>심복</b>은 ' + HEIR.bondP + '%로 ' + HEIR.bond[0] + ' ~ ' + HEIR.bond[1] + ' 내립니다. 새 군주와 직접 인연이 있는 사람은 흔들리지 않습니다. 인연이 없던 무장은 <b>흔들릴 수도, 그대로일 수도</b> 있습니다 — ' + HEIR.base + '%에서 새 군주의 매력이 선대보다 낮은 만큼 늘고(1마다 ' + HEIR.cha + '%p), 미리 정해 둔 후계면 ' + HEIR.named + '%p 줄며, 새 군주보다 공적이 높은 사람은 ' + HEIR.merit + '%p 더합니다. 그렇게 흔들리면 ' + HEIR.drop[0] + ' ~ ' + HEIR.drop[1] + ' 내립니다. 새 군주의 매력이 선대보다 ' + HEIR.upAt + ' 넘게 높으면 오르는 사람도 있습니다. 후계를 고르는 창에 누가 뒤를 이으면 어떻게 될지 줄마다 적혀 있습니다.</p>' +\n" +
        "  '<h3>무장 명부</h3><p>무장은 모두 ' + SCENARIO.officers.length + '명입니다(여성 ' + SCENARIO.women.length + '명 · v0.23에서 다른 시대의 사람 ' + (SCENARIO.officers.length - 425) + '명이 늘었습니다). 그 시대에 이미 세력에 있는 사람 말고는 <b>등장 연도</b>가 되어야 나옵니다: 재야의 사람은 그 도시에서 <b>탐색</b>으로 찾고, 군주의 집안사람과 <b>아버지가 벼슬하고 있는 사람</b>은 해가 바뀔 때 스스로 찾아옵니다(아버지가 섬기는 세력으로).")
wr('src/ui_panels.js', u)

# ───────── style.css ─────────
s = rd('src/style.css')
s += """
/* v0.23 시대 고르기 · 나이 · 후계 */
.scn { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin: 0 0 7px; }
.scb { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 44px; padding: 4px 2px 5px; border: 1px solid var(--line-2); border-radius: 2px; background: var(--paper-2); color: var(--ink-2); font-family: var(--font-body); }
.scb b { font: 800 15px var(--font-body); line-height: 1.15; font-variant-numeric: tabular-nums; }
.scb span { font-size: 11px; white-space: nowrap; letter-spacing: -0.02em; }
.scb.on { background: var(--ink); color: var(--paper); border-color: var(--ink); }
.scsub { margin: 0 0 6px; font-size: 12.5px; line-height: 1.4; color: var(--ink-2); }
.scsub b { font-family: var(--font-display); font-weight: 400; color: var(--seal); margin-right: 4px; }
.sick { font-style: normal; font-size: 10.5px; font-weight: 700; color: var(--seal); border: 1px solid var(--seal); border-radius: 2px; padding: 0 3px; margin-left: 2px; }
.note.heir { margin: -2px 0 8px; color: var(--ink-2); line-height: 1.45; }
.rows.hrl .row .ds { white-space: normal; line-height: 1.35; }
"""
wr('src/style.css', s)
print('s2_ui ok')
