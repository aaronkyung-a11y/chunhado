# v0.9 화면: 군사(임명 · 조언) · 이웃 거점의 다른 세력 무장 등용 · 데려갈 위험 알림
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "/* 등용을 권한 뒤 다시 권할 수 있는 턴", """/* 무장 o 를 이웃 세력이 데려갈 위험: 이웃 거점에 있는 다른 세력 무장 가운데 가장 잘 권하는 사람과 그 성공률 { p, by, base }. 위험이 없으면 null */
function poachRisk(o) {
  if (!o || o.st !== 'active' || o.unit !== null || o.f < 0 || isLord(o) || bondOf(o) || o.loy >= POACH.wall) return null;
  var best = null;
  ADJ[o.loc].forEach(function (e) {
    var nb = G.bases[e.to]; if (nb.owner < 0 || nb.owner === o.f) return;
    baseOfficers(nb).forEach(function (r) { var q = recruitChance(nb, r, o); if (q > 0 && (!best || q > best.p)) best = { p: q, by: r, base: nb }; });
  });
  return best;
}
/* 등용을 권한 뒤 다시 권할 수 있는 턴""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
# ---------- 공용: 조언을 글로 ----------
s = rep(s, "/* ---------- 상태 이상(혼란·위보·불길)을 글로 ---------- */", """/* ---------- 군사의 조언(v0.9) ---------- */
function advMark(a) { return a ? '<i class="adv ' + (a.says ? 'y' : 'n') + '">' + (a.says ? '○' : '×') + '</i>' : ''; }
function advLine(a) { return a ? '군사 ' + a.adv.n + ': <b class="' + (a.says ? 'ok' : 'bad') + '">' + (a.says ? '통할 것입니다' : '어렵겠습니다') + '</b> <small>적중률 ' + a.acc + '%</small>' : ''; }
function recruitAdvice(b, o, t) { return advise(G.player, recruitKey(t), recruitChance(b, o, t), t.int); }
function ployAdvice(u, pl, t) { return advise(G.player, ployKey(pl, t), ployChance(u, pl, t.u || null), t.u ? uInt(t.u) : 0); }
function advTag(o) { return (o.f >= 0 && facAdv(o.f) === o) ? '군사' : ''; }
function showAdvisor() {
  var f = G.player;
  showDialog({
    render: function () {
      var A = facAdv(f), cs = advCandidates(f), i, h = dlgHead('군사(軍師)') + '<div class="dlg-b"><div class="help"><p>군사는 <b>등용</b>과 <b>계략</b>을 하기 전에 통할지 미리 말해 줍니다 — <i class="adv y">○</i> 통한다 · <i class="adv n">×</i> 어렵다. 맞힐 확률은 <b>군사의 지력 + (군사의 지력 − 상대의 지력) × ' + ADVISE.k + '</b>이고 ' + ADVISE.min + '~100% 사이입니다. 지력이 높을수록, 상대의 지력이 낮을수록 잘 맞습니다. 군주는 군사가 될 수 없습니다.</p></div>';
      if (A) h += '<div class="card advc">' + porTag(A, 'md') + '<div><p><b class="hi">지금의 군사 · ' + A.n + '</b> 지력 ' + A.int + '</p><p class="note">조언 적중률 — 지력 60인 상대 <b>' + adviceAcc(A, 60) + '%</b> · 75인 상대 <b>' + adviceAcc(A, 75) + '%</b> · 90인 상대 <b>' + adviceAcc(A, 90) + '%</b></p></div></div>';
      else h += '<p class="note">군사가 없습니다 — 아래에서 고르세요.</p>';
      h += '<div class="sec">군사로 삼을 무장 <small>지력 순 · 누르면 바꿉니다(행동력을 쓰지 않습니다)</small></div><div class="rows">';
      for (i = 0; i < cs.length; i++) { var o = cs[i], cur = A && A.id === o.id; h += offRow(o, { a: 'set', sel: cur, badge: cur ? '군사' : '', hi: 'int', rt: '지력 <b>' + o.int + '</b><br>' + (o.unit !== null ? '출진' : G.bases[o.st === 'travel' ? o.dest : o.loc].n) }); }
      if (!cs.length) h += '<p class="note">군사로 삼을 무장이 없습니다.</p>';
      return h + '</div></div>';
    },
    on: { set: function (el) { var o = off(+el.getAttribute('data-v')), r = setAdvisor(f, o.id); if (!r.ok) return toast(r.msg); sfx('ui'); toast(josa(o.n, '을를') + ' 군사로 삼았습니다 (지력 ' + o.int + ')'); refreshDialog(); refreshSheet(); } }
  }, true);
}
/* ---------- 상태 이상(혼란·위보·불길)을 글로 ---------- */""")
# ---------- STATUS 창: 군사 단추 ----------
s = rep(s, """        (HOME.open ? '<div class="hm-ap">행동력 <span class="gauge"><u style="width:' + Math.round(F.ap / 255 * 100) + '%"></u></span><b>' + F.ap + '</b></div>' : '') + '</div>' +""",
"""        (HOME.open ? '<div class="hm-ap">행동력 <span class="gauge"><u style="width:' + Math.round(F.ap / 255 * 100) + '%"></u></span><b>' + F.ap + '</b></div>' +
          '<button class="hm-adv" type="button" data-a="adv">군사 ' + (facAdv(f) ? '<b>' + facAdv(f).n + '</b> <small>지력 ' + facAdv(f).int + '</small>' : '<b class="bad">없음</b>') + ' <span>▸</span></button>' : '') + '</div>' +""")
s = rep(s, """      lord: function () { showOfficer(off(G.factions[G.player].lord)); },
      lists: function (el) { showLists(el.getAttribute('data-v')); }""", """      lord: function () { showOfficer(off(G.factions[G.player].lord)); },
      adv: function () { showAdvisor(); },
      lists: function (el) { showLists(el.getAttribute('data-v')); }""")
# ---------- 무장 창: 군사 표시·임명 ----------
s = rep(s, """      return dlgHead(o.n + ' ' + (o.f >= 0 ? facChip(o.f) : '')) + '<div class="dlg-b"><div class="card">' + sceneTag(o) + '<div class="bars">' + bars + '</div></div>' +""",
"""      return dlgHead(o.n + ' ' + (o.f >= 0 ? facChip(o.f) : '') + (advTag(o) ? ' <em class="advt">군사</em>' : '')) + '<div class="dlg-b"><div class="card">' + sceneTag(o) + '<div class="bars">' + bars + '</div></div>' +""")
s = rep(s, """<div><span>공적</span><b>' + fmt(o.merit) + '</b></div>' : '') + '</div></div>';
    }, on: {}
  }, true);                                              // 목록 같은 창 위에서 열었으면 ×로 그 창에 돌아간다""",
"""<div><span>공적</span><b>' + fmt(o.merit) + '</b></div>' : '') + '</div></div>' +
        ((o.f === G.player && advOk(o, G.player)) ? '<div class="dlg-f"><div class="pv">' + (advTag(o) ? '지금의 <b>군사</b>입니다 · 적중률은 지력에 따릅니다' : '군사로 삼으면 등용·계략 전에 조언합니다') + '</div>' + (advTag(o) ? '' : '<button class="btn" type="button" data-a="adv">군사로 삼기</button>') + '</div>' : '');
    }, on: { adv: function () { var r = setAdvisor(G.player, o.id); if (!r.ok) return toast(r.msg); sfx('ui'); toast(josa(o.n, '을를') + ' 군사로 삼았습니다 (지력 ' + o.int + ')'); refreshDialog(); refreshSheet(); } }
  }, true);                                              // 목록 같은 창 위에서 열었으면 ×로 그 창에 돌아간다""")
# ---------- 목록·인재 탭의 딱지 ----------
s = rep(s, "os.forEach(function (o) { h += offRow(o, { badge: isLord(o) ? '군주' : '', rt: (o.unit !== null ? '출진' :", "os.forEach(function (o) { h += offRow(o, { badge: isLord(o) ? '군주' : advTag(o), rt: (o.unit !== null ? '출진' :")
s = rep(s, "for (i = 0; i < all.length; i++) h += offRow(all[i], { badge: isLord(all[i]) ? '군주' : '', dim: all[i].acted || all[i].st === 'travel',",
           "for (i = 0; i < all.length; i++) h += offRow(all[i], { badge: isLord(all[i]) ? '군주' : advTag(all[i]), dim: all[i].acted || all[i].st === 'travel',")
# ---------- 등용: 이웃 거점의 다른 세력 무장 ----------
s = rep(s, """        var fr = freeOfficers(b), cp = b.captives.length;
        h += '<div class="cmds">' + (city ? cmd('search', '탐색', '행 ' + AP.search) : '') + cmd('recruit', '등용', (fr.length || cp) ? '재야 ' + fr.length + ' · 포로 ' + cp : '대상 없음', fr.length + cp > 0, !(fr.length + cp)) + cmd('reward', '포상', '금 ' + COST.reward + ' · 행 ' + AP.reward) +""",
"""        var fr = freeOfficers(b), cp = b.captives.length, nbO = poachTargets(b).length;
        h += '<div class="cmds">' + (city ? cmd('search', '탐색', '행 ' + AP.search) : '') + cmd('recruit', '등용', (fr.length || cp || nbO) ? [fr.length ? '재야 ' + fr.length : '', cp ? '포로 ' + cp : '', nbO ? '이웃 ' + nbO : ''].filter(function (x) { return x; }).join(' · ') : '대상 없음', fr.length + cp > 0, !(fr.length + cp + nbO)) + cmd('reward', '포상', '금 ' + COST.reward + ' · 행 ' + AP.reward) +""")
old_flow = s[s.index("function flowRecruit(b) {"):s.index("function flowReward(b) {")]
new_flow = """function flowRecruit(b) {
  var here = freeOfficers(b).concat(baseCaptives(b).filter(function (o) { return o.capF === b.owner; })), far = poachTargets(b);
  if (!here.length && !far.length) return toast('등용할 대상이 없습니다 — 탐색으로 재야 인재를 찾으세요');
  function bestP(t) { var m = 0; idleOfficers(b).forEach(function (o) { m = Math.max(m, recruitChance(b, o, t)); }); return m; }
  function why(t) {                                            // 권할 수 없는 까닭(없으면 '')
    if (askWait(t)) return t.st === 'active' ? askWait(t) + '턴 뒤에 다시' : '다음 턴에 다시';
    if (t.st === 'active' && bondOf(t)) return '주군과 ' + bondOf(t);
    if (t.st === 'active' && t.loy >= POACH.wall && !bondWith(t, b.owner)) return '충성 ' + POACH.wall + ' 이상';
    return '';
  }
  showDialog({
    render: function () {
      var idle = idleOfficers(b).length, i, t, w, h = dlgHead('등용 — 누구를 부를까요') + '<div class="dlg-b">';
      if (!idle) h += '<p class="note">이 거점에 쉬는 무장이 없어 지금은 권할 수 없습니다.</p>';
      if (here.length) {
        h += '<div class="sec">이 거점의 재야·포로</div><div class="rows">';
        for (i = 0; i < here.length; i++) { t = here[i]; w = why(t); h += offRow(t, { a: 't', dim: !!w, badge: t.st === 'captive' ? '포로' : '재야', rt: w ? '<span class="bad">' + w + '</span>' : (idle ? '최고 <b>' + bestP(t) + '%</b>' : '') }); }
        h += '</div>';
      }
      if (far.length) {
        var L = far.map(function (x) { return { t: x, p: bestP(x), w: why(x) }; }).sort(function (x, y) { return (x.w ? 1 : 0) - (y.w ? 1 : 0) || y.p - x.p || x.t.loy - y.t.loy; });
        h += '<div class="sec">이웃 거점의 다른 세력 무장 <small>응하면 이 거점으로 넘어옵니다</small></div><div class="rows">';
        for (i = 0; i < L.length; i++) { t = L[i].t; w = L[i].w; h += offRow(t, { a: 't', dim: !!w || !L[i].p, badge: facName(t.f) + '·' + G.bases[t.loc].n, rt: '충성 <b>' + t.loy + '</b><br>' + (w ? '<span class="bad">' + w + '</span>' : (idle ? '최고 <b>' + L[i].p + '%</b>' : '')) }); }
        h += '</div><p class="note">한 번 권하면 ' + POACH.wait + '턴 뒤에 다시 권할 수 있고, 거절한 무장은 충성이 ' + POACH.up + ' 오릅니다. 제 주군과 인연이 있거나 충성이 ' + POACH.wall + ' 이상이면 응하지 않습니다. 출진 중인 무장과 군주에게는 권할 수 없습니다.</p>';
      }
      return h + '</div>';
    },
    on: { t: function (el) {
      var t = off(+el.getAttribute('data-v')), w = why(t), farT = t.st === 'active';
      if (w) return toast(t.n + ' — ' + w + (farT && !askWait(t) ? '이라 응하지 않습니다' : ''));
      if (farT && !canPoach(b, t)) return toast('지금은 권할 수 없습니다 — 자리를 옮겼습니다');
      pickOfficers({ push: true, title: t.n + ' 등용 — 누구를 보낼까요', list: idleOfficers(b), max: 1, hi: 'cha', key: function (o) { return recruitChance(b, o, t); },
        rt: function (o) { return advMark(recruitAdvice(b, o, t)) + '<b>' + recruitChance(b, o, t) + '%</b>'; }, rtHead: '성공률', auto: function () { return autoPick('recruit', b, { target: t }, 1); },
        preview: function (os) { var a = recruitAdvice(b, os[0], t); return '성공률 <b>' + recruitChance(b, os[0], t) + '%</b>' + (farT ? ' · 충성 ' + t.loy : '') + (a ? '<br>' + advLine(a) : ''); } },
        function (os) {
          var r = cmdRecruit(b, os[0].id, t.id); if (r.ok && r.joined) sfx('cheer');
          var ok = done(r, r.ok ? (r.joined ? (r.far ? josa(t.n, '이가') + ' ' + facName(r.from) + '군을 떠나 합류했습니다!' : josa(t.n, '이가') + ' 합류했습니다!') : josa(t.n, '이가') + ' 거절했습니다' + (r.far ? ' — ' + POACH.wait + '턴 뒤에 다시 권할 수 있습니다 (충성 +' + POACH.up + ')' : ' — 다음 턴에 다시 권할 수 있습니다')) : '');
          if (ok) { here = freeOfficers(b).concat(baseCaptives(b).filter(function (o) { return o.capF === b.owner; })); far = poachTargets(b); }
          return ok;
        });
    } }
  });
}
"""
s = s.replace(old_flow, new_flow)
# ---------- 계략: 군사의 조언 ----------
s = rep(s, "      out.push({ kind: 'ploy', ploy: pl, label: pl.name, sub: inP ? '기력 ' + pl.cost + ' · ' + ployChance(u, pl, t.u) + '%' :",
           "      out.push({ kind: 'ploy', ploy: pl, label: pl.name, adv: inP ? ployAdvice(u, pl, t) : null, sub: inP ? '기력 ' + pl.cost + ' · ' + ployChance(u, pl, t.u) + '%' + advMark(ployAdvice(u, pl, t)) :")
s = rep(s, "    out.push({ kind: 'ploy', ploy: PLOYS[0], label: '화계', sub: inF ? '기력 10' : '불가', ok: inF });",
           "    out.push({ kind: 'ploy', ploy: PLOYS[0], label: '화계', adv: inF ? ployAdvice(u, PLOYS[0], t) : null, sub: inF ? '기력 10' + advMark(ployAdvice(u, PLOYS[0], t)) : '불가', ok: inF });")
s = rep(s, """          h += '<div class="acts">';
          for (i = 0; i < st.acts.length; i++) { var a = st.acts[i];""", """          var adv1 = null; st.acts.forEach(function (a0) { if (a0.adv && !adv1) adv1 = a0.adv; });
          if (adv1) h += '<p class="note advn">군사 <b>' + adv1.adv.n + '</b>의 조언 — 계략 단추의 <i class="adv y">○</i> 통한다 · <i class="adv n">×</i> 어렵다 <small>적중률 ' + adv1.acc + '%</small></p>';
          h += '<div class="acts">';
          for (i = 0; i < st.acts.length; i++) { var a = st.acts[i];""")
# ---------- 지금 할 일: 데려갈 위험 ----------
s = rep(s, """  if (F.ap >= 10) {
    var nb = 0, more = 0, lordLoc""", """  if (!peaceLeft()) bs.forEach(function (b) {                  // 이웃 세력이 데려갈 수 있는 무장(초반 보호 중에는 권하지 않으므로 그 뒤부터)
    var rk = baseOfficers(b).map(function (o) { return { o: o, r: poachRisk(o) }; }).filter(function (x) { return x.r && x.r.p >= POACH_AI.min; }).sort(function (x, y) { return y.r.p - x.r.p; });
    if (rk.length) out.push({ cls: 'warn', ic: '離', t: b.n + ' — 다른 세력이 데려갈 수 있는 무장 ' + rk.length + '명', s: rk.slice(0, 3).map(function (x) { return x.o.n + ' 충성 ' + x.o.loy + '(' + x.r.p + '%)'; }).join(' · ') + ' — 포상으로 충성을 ' + POACH.wall + '까지 올리면 응하지 않습니다', go: ['base', b.id, 'men'], lb: '포상', info: 1 });
  });
  if (F.ap >= 10) {
    var nb = 0, more = 0, lordLoc""")
# ---------- 도움말 ----------
s = rep(s, "  '<h3>인재</h3><p>탐색으로 재야의 인재를 찾아 등용합니다. 사로잡은 적장도 등용할 수 있습니다. 해가 바뀌면 새 인물이 세상에 나옵니다.</p>' +",
"""  '<h3>인재</h3><p>탐색으로 재야의 인재를 찾아 등용합니다. 사로잡은 적장도 등용할 수 있습니다. 해가 바뀌면 새 인물이 세상에 나옵니다.</p>' +
  '<p><b>다른 세력의 무장</b>도 등용할 수 있습니다 — 내 거점과 길로 바로 이어진 <b>이웃 거점에 머무는 무장</b>이 대상입니다(인재 → 등용). 응하면 그 자리에서 내 거점으로 넘어옵니다. 성공률은 보내는 무장의 매력·정치, 두 군주의 매력 차이, 그리고 <b>대상의 충성</b>으로 정해집니다. 제 주군과 인연이 있거나 충성이 ' + POACH.wall + ' 이상이면 응하지 않고, 군주와 출진 중인 무장에게는 권할 수 없습니다. 한 번 권하면 ' + POACH.wait + '턴 뒤에 다시 권할 수 있고, 거절한 무장은 충성이 ' + POACH.up + ' 오릅니다.</p>' +
  '<p>다른 세력도 같은 규칙으로 <b>내 무장을 데려갑니다</b>(초반 보호 기간에는 권하지 않습니다). 위험한 무장이 있으면 지금 할 일에 "다른 세력이 데려갈 수 있는 무장"이 뜹니다 — <b>포상</b>으로 충성을 ' + POACH.wall + '까지 올리면 응하지 않습니다.</p>' +
  '<h3>군사(軍師)</h3><p>세력마다 군사를 한 사람 둡니다(STATUS 창의 <b>군사</b> 단추, 또는 무장 창의 <b>군사로 삼기</b>). 처음에는 지력이 가장 높은 무장이 맡고, 군주는 될 수 없습니다. 군사는 <b>등용과 계략을 하기 전에</b> 통할지 미리 말해 줍니다 — 무장을 고르는 표와 계략 단추의 <i class="adv y">○</i>(통한다)·<i class="adv n">×</i>(어렵다). 맞힐 확률은 <b>군사의 지력 + (군사의 지력 − 상대의 지력) × ' + ADVISE.k + '</b>, ' + ADVISE.min + '~100%입니다(지력 90인 군사가 지력 70인 상대를 보면 100%, 지력 70인 군사가 지력 90인 상대를 보면 60%).</p>' +
  '<p>등용과 계략의 성패는 그 턴에 <b>대상마다 미리 정해져 있습니다</b>. 그래서 같은 턴에는 누구에게 다시 물어도 답이 같고, 가장 잘하는 무장이 안 되면 그 턴에는 누구도 안 됩니다. 군사를 바꿔 물어도 새로 알 수 있는 것은 없습니다 — 지력이 더 높은 군사의 말이 더 자주 맞을 뿐입니다.</p>' +""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """
/* v0.9 군사와 조언 */
.adv { font-style: normal; font-weight: 900; margin: 0 3px; }
.adv.y { color: var(--jade); }
.adv.n { color: var(--seal); }
.hm-adv { display: inline-flex; align-items: baseline; gap: 5px; margin-top: 4px; padding: 1px 8px 1px 0; color: var(--ink-2); font-size: 13px; }
.hm-adv b { color: var(--ink); font-weight: 800; font-size: 14px; }
.hm-adv small { color: var(--dim); font-size: 12px; }
.hm-adv span { color: var(--seal); font-weight: 800; }
.advt { font-style: normal; font-weight: 700; font-size: 11px; color: var(--indigo); border: 1px solid var(--indigo); border-radius: 2px; padding: 0 4px; margin-left: 4px; font-family: var(--font-body); vertical-align: 2px; }
.card.advc { align-items: center; }
.card.advc p { margin: 0 0 3px; }
.note.advn { margin: -2px 0 8px; color: var(--ink-2); }
.dlg-f .pv small { margin-left: 2px; }
.act small .adv { font-size: 13px; }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
