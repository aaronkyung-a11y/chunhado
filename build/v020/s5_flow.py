# v0.20 (5) 출진 · 수송 · 이동 · 등용 창
#   · 출진("무장을 정하고 나면 다음 단계로 군량이나 방향 등을 정하는게 낫지 않나"): ① 병과 · 무장 → ② 병력 · 군량 · 나갈 자리. 수송도 ① 호송 무장 · 짐 → ② 내린 뒤 · 나갈 자리.
#   · 나갈 자리("지도 위에 표시해주는 게 낫지 않을까"): 창 속의 여섯 칸 그림 대신 지도에서 고른다 — 성 둘레 여섯 칸이 빛나고(금빛, 고른 칸은 붉게) 칸마다 방향과 땅이 적힌다.
#     ②단계의 창은 지도를 가리지 않는 낮은 창이 되고, 화면은 성과 그 둘레로 맞춰진다.
#   · 이동("도시 이름 나오게 하거나 지도로 선택하게"): 보낼 곳을 지도에서도 고른다(우리 성마다 이름과 걸리는 날수가 뜬다 — 누르면 고르고, [보낸다]로 확정). 목록은 그대로.
#     이동 중인 무장의 상태에 가는 곳을 적는다('허창으로 이동 중 (20일)').
#   · 등용("능력치 높은 순이나 적성에 따라 볼 수 있게"): 정렬 줄 — 가능성 · 능력 합 · 통솔 · 무력 · 지력 · 정치 · 매력 · 적성(창 · 극 · 노 · 기 · 병기).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)
def cut(s, a, b, new):
    assert s.count(a) == 1 and s.count(b) == 1, (s.count(a), s.count(b), a[:50], b[:50])
    i, j = s.index(a), s.index(b); assert i < j
    return s[:i] + new + s[j:]

# ---------- 지도 위의 표(붙박이 딱지) · 고르는 칸의 빛 ----------
s = rd('src/ui3d.js')
s = rep(s, "function anim(dur, step, done) {", """/* v0.20 지도 위의 붙박이 딱지: 고를 칸마다 글을 띄운다(나갈 자리 · 보낼 성). 화면이 움직이면 따라간다(tick) */
function marksClear() { var ms = UI.marks || []; for (var i = 0; i < ms.length; i++) ms[i].el.remove(); UI.marks = []; }
function marksSet(list) {
  marksClear();
  for (var i = 0; i < list.length; i++) {
    var m = list[i], el = document.createElement('div'); el.className = 'mk ' + (m.cls || ''); el.innerHTML = m.html; el.style.opacity = 0;
    $('fx').appendChild(el); UI.marks.push({ p: hexPos(m.c, m.r), el: el, dy: m.dy || 0 });
  }
  UI.render = true;
}
function anim(dur, step, done) {""")
s = rep(s, "  requestAnimationFrame(tick);\n}", """  if (UI.marks && UI.marks.length) for (i = 0; i < UI.marks.length; i++) {
    var mk = UI.marks[i], ms = w2s(mk.p[0], mk.p[1] + 0.05, mk.p[2]);
    if (!ms) { mk.el.style.opacity = 0; continue; }
    mk.el.style.opacity = 1; mk.el.style.transform = 'translate(-50%,-50%) translate(' + ms[0].toFixed(1) + 'px,' + (ms[1] + mk.dy).toFixed(1) + 'px)';
  }
  requestAnimationFrame(tick);
}""")
s = rep(s, "  if (SPOT.on && SPOT.v) for (i = 0; i < SPOT.v.lots.length; i++) {            // 건설 자리",
        """  var pkL = (typeof MODAL !== 'undefined' && MODAL && MODAL.pick) ? MODAL.pick.list() : null;      // v0.20: 지도에서 고르는 칸(나갈 자리 · 보낼 성)
  if (pkL) for (i = 0; i < pkL.length; i++) ovPut(K(pkL[i].c, pkL[i].r), pkL[i].on ? [181, 51, 42] : [212, 160, 44], pkL[i].on ? 205 : 160);
  if (SPOT.on && SPOT.v) for (i = 0; i < SPOT.v.lots.length; i++) {            // 건설 자리""")
s = rep(s, "  if (gh && SPOT.on && SPOT.v) { var gp = plotAt(gh[0], gh[1]);",
        "  if (gh && typeof MODAL !== 'undefined' && MODAL && MODAL.pick && MODAL.pick.has(gh[0], gh[1])) return gh;      // v0.20: 고르는 칸은 성의 그림에 가려 있어도 그 칸으로 집는다\n  if (gh && SPOT.on && SPOT.v) { var gp = plotAt(gh[0], gh[1]);")
wr('src/ui3d.js', s)

s = rd('src/ui_panels.js')
# ---------- 창: 지도에서 고르는 창(MODAL.pick) ----------
s = rep(s, "  m.classList.toggle('see', !!MODAL.see); $('app').classList.toggle('seeing', !!(devOf() || fselOf()));",
        """  m.classList.toggle('see', !!MODAL.see); $('app').classList.toggle('seeing', !!(devOf() || fselOf() || MODAL.pick));
  $('app').classList.toggle('picking', !!MODAL.pick);                // v0.20: 지도에서 고르는 창 — 고를 칸의 딱지를 띄운다(없으면 걷는다)
  if (MODAL.pick && MODAL.pick.show) MODAL.pick.show(); else marksClear();
  if (MODAL.pick || PICKING) requestDraw();                          // 지도는 고르는 창이 뜨거나 걷힐 때만 다시 그린다(여느 창을 열 때마다 그리면 느리다)
  PICKING = !!MODAL.pick;""")
s = rep(s, "function paintDialog(st) {", "var PICKING = false;                                              // v0.20: 지도에서 고르는 창이 떠 있는가(MODAL.pick)\nfunction paintDialog(st) {")
s = rep(s, "m.classList.remove('see'); $('app').classList.remove('seeing'); m.innerHTML = '';", "m.classList.remove('see'); $('app').classList.remove('seeing'); $('app').classList.remove('picking'); marksClear(); if (PICKING) { PICKING = false; requestDraw(); } m.innerHTML = '';")
s = rep(s, "  if (MODAL) { if (MODAL.dev) devTap(c, r); else if (MODAL.fsel) fselTap(c, r); return; }",
        "  if (MODAL) { if (MODAL.dev) devTap(c, r); else if (MODAL.fsel) fselTap(c, r); else if (MODAL.pick) MODAL.pick.tap(c, r); return; }")
s = rep(s, "  if (o.st === 'travel') return '이동 중 (' + days(o.eta) + ')';",
        "  if (o.st === 'travel') return (o.dest >= 0 && G.bases[o.dest] ? euro(G.bases[o.dest].n) + ' ' : '') + '이동 중 (' + days(o.eta) + ')';      // v0.20: 가는 곳을 적는다")

# ---------- 나갈 자리 · 출진 · 수송 ----------
NEW = r"""/* v0.20 나갈 자리: 지도 위에서 고른다(전에는 창 속에 여섯 칸을 그려 골랐다). 성 둘레 여섯 칸이 빛나고(나갈 수 있는 칸은 금빛 · 고른 칸은 붉게) 칸마다 방향과 땅이 적힌다.
   st.at = 고른 칸 [c, r] 또는 null(게임이 고른다). D = 떠 있는 창 — open() 이 D.pick 을 달아 지도 누름을 받는다(onTap). */
function stepTag(n, of, label) { return ' <small class="stp">' + n + '/' + of + ' ' + label + '</small>'; }
function exitPick(b, st, D) {
  function spots() { var ok = {}; deploySpots(b).forEach(function (q) { ok[K(q[0], q[1])] = 1; }); return ok; }
  function cur() { var ok = spots(); if (st.at && !ok[K(st.at[0], st.at[1])]) st.at = null; return st.at || deploySpot(b); }      // 고른 칸이 막혔으면(다른 부대가 섰으면) 자동으로 되돌린다
  function marks() {
    var ok = spots(), ns = nbrs(b.c, b.r), p0 = hexCenter(b.c, b.r), at = cur(), list = [];
    for (var i = 0; i < ns.length; i++) {
      var c = ns[i][0], r = ns[i][1], p = hexCenter(c, r), on = !!(at && at[0] === c && at[1] === r), good = !!ok[K(c, r)];
      list.push({ c: c, r: r, cls: 'ex' + (on ? ' on' : '') + (good ? '' : ' no'), html: '<b>' + dirName(p[0] - p0[0], p[1] - p0[1]) + '</b><small>' + spotWhat(c, r) + '</small>' });
    }
    marksSet(list); requestDraw();
  }
  var P = {
    list: function () { var ok = spots(), at = cur(), out = []; for (var k in ok) { var c = +k % W, r = (+k - c) / W; out.push({ c: c, r: r, on: !!(at && at[0] === c && at[1] === r) }); } return out; },
    has: function (c, r) { return hdist(c, r, b.c, b.r) === 1; },
    show: marks,
    tap: function (c, r) {
      if (c === b.c && r === b.r) return;
      if (hdist(c, r, b.c, b.r) !== 1) return toast('성 둘레의 빛나는 칸을 누르세요', 1600);
      if (!spots()[K(c, r)]) return toast('그 칸으로는 나갈 수 없습니다 — ' + spotWhat(c, r));
      st.at = [c, r]; sfx('ui'); refreshDialog(); marks();
    }
  };
  return {
    open: function () {
      D.see = true; D.pick = P; if (typeof talkHide === 'function') talkHide(); paintDialog(0);
      var dl = document.querySelector('#modal .dlg'), top = $('hud') ? $('hud').getBoundingClientRect().bottom : 90, bot = dl ? dl.getBoundingClientRect().top : CH * 0.5;
      frameHexes([[b.c, b.r]].concat(nbrs(b.c, b.r)), top + 30, bot - 12, 2.1);
    },
    close: function () { D.see = false; D.pick = null; },
    line: function () {
      var at = cur(), p0 = hexCenter(b.c, b.r), p = at ? hexCenter(at[0], at[1]) : null;
      return '<div class="sec">나갈 자리 <small>지도에서 빛나는 칸을 누르세요</small>' + (st.at ? '<button class="btn auto" type="button" data-a="atauto">자동</button>' : '') + '</div>' +
        '<p class="dpat-t wide" id="dpAt">' + (at ? '<b>' + dirName(p[0] - p0[0], p[1] - p0[1]) + '쪽</b> ' + spotWhat(at[0], at[1]) + ' <small>' + (st.at ? '고른 자리' : '자동 — 길이 난 쪽부터') + '</small>' : '<b class="bad">나갈 자리가 없습니다</b>') + '</p>';
    },
    auto: function () { st.at = null; refreshDialog(); marks(); }
  };
}
function flowDeploy(b) {
  var list = idleOfficers(b).sort(function (x, y) { return aiMilScore(y) - aiMilScore(x); });
  if (!list.length) return toast('행동할 수 있는 무장이 없습니다');
  if (b.troops < 100) return toast('주둔 병력이 없습니다');
  var st = { step: 1, type: 'sword', ids: [], troops: 0, turns: DEPLOY_FOOD[1], auto: true, at: null }, D, EX;
  function stock(t) { var wp = UNIT_TYPES[t].weapon; return wp === 'ram' ? b.w.ram : (wp ? b.w[wp] : 1e9); }
  function usable(t) { return t === 'ram' ? stock(t) >= 1 : stock(t) >= 100; }
  ['spear', 'halberd', 'bow', 'cav'].forEach(function (t) { if (usable(t) && (st.type === 'sword' || stock(t) > stock(st.type))) st.type = t; });
  function mx() {
    if (!st.ids.length) return 0;
    var m = Math.min(b.troops, cmdCap(off(st.ids[0]))), wp = UNIT_TYPES[st.type].weapon;
    if (wp && wp !== 'ram') m = Math.min(m, b.w[wp]);
    return Math.floor(m / 100) * 100;
  }
  function food() { return Math.min(b.food, Math.ceil(st.troops / 20) * st.turns); }
  function foodNote() {                                        // 도시 병량이 모자라면 실제로 실리는 날수를 적는다
    var per = Math.max(1, Math.ceil(st.troops / 20)), need = per * st.turns;
    return '도시 병량 ' + fmt(b.food) + (need > b.food ? ' · <b class="bad">모자랍니다 — ' + days(Math.floor(b.food / per)) + '분만 실립니다</b>' : ' · 이웃 거점까지 20~50일');
  }
  function fix() { var m = mx(); if (st.auto || st.troops > m) st.troops = m; }
  function pv() {
    if (!st.ids.length) return '주장을 고르세요';
    var tmp = { type: st.type, off: st.ids, troops: st.troops, max: st.troops };
    return '공격 <b>' + Math.round(uAtk(tmp)) + '</b> · 방어 <b>' + Math.round(uDef(tmp)) + '</b>' + (st.step === 2 ? ' · 군량 <b>' + fmt(food()) + '</b>' : ' · 이동 <b>' + uMaxMp(tmp) + '</b>');
  }
  D = {
    render: function () {
      var h, i;
      if (st.step === 1) {                                         // ① 병과 · 무장
        h = dlgHead('출진 — ' + b.n + stepTag(1, 2, '병과 · 무장')) + '<div class="dlg-b"><div class="sec">병과</div><div class="opts">';
        var UKEY = { sword: 'u_sword', spear: 'u_spear', halberd: 'u_halberd', bow: 'u_bow', cav: 'u_cav', ram: 'u_ram' };
        for (i = 0; i < COMBAT_TYPES.length; i++) {
          var t = COMBAT_TYPES[i], T = UNIT_TYPES[t], ok = usable(t);
          h += '<button class="opt' + (st.type === t ? ' on' : '') + (ok ? '' : ' off') + '" type="button" data-a="type" data-v="' + t + '">' + thumb(UKEY[t]) + '<b>' + T.name + '</b><small>' + (t === 'sword' ? '무기 불필요' : (t === 'ram' ? '충차 ' + b.w.ram + '대' : WEAPON_NAMES[T.weapon] + ' ' + fmt(stock(t)))) + '</small></button>';
        }
        h += '</div><div class="sec">무장 <small>첫 번째가 주장 · 3명까지</small><button class="btn auto" type="button" data-a="auto">자동 편성</button></div><div class="rows">';
        var ai = APT_IDX[st.type];
        for (i = 0; i < list.length; i++) {
          var o = list[i], si = st.ids.indexOf(o.id);
          h += offRow(o, { a: 'pick', sel: si >= 0, apt: ai, badge: si === 0 ? '주장' : (si > 0 ? '부장' : ''), rt: (ai !== undefined ? '적성 <b class="' + (o.apt.charAt(ai) === 'S' ? 'bad' : (o.apt.charAt(ai) === 'A' ? 'hi' : '')) + '">' + o.apt.charAt(ai) + '</b><br>' : '') + '지휘 ' + fmt(cmdCap(o)) });
        }
        return h + '</div></div><div class="dlg-f"><div class="pv" id="dpP">' + pv() + '</div><button class="btn pri" type="button" data-a="next"' + (st.ids.length && mx() >= 100 ? '' : ' disabled') + '>다음 ›</button></div>';
      }
      // ② 병력 · 군량 · 나갈 자리(지도에서)
      h = dlgHead('출진 — ' + b.n + stepTag(2, 2, '병력 · 군량 · 나갈 자리')) + '<div class="dlg-b"><p class="note team">' + UNIT_TYPES[st.type].name + ' · ' + st.ids.map(function (id, k) { return (k ? '부장 ' : '주장 ') + '<b>' + off(id).n + '</b>'; }).join(' · ') + '</p>';
      h += EX.line();
      h += '<div class="fld"><label><span>병력 (주둔 ' + fmt(b.troops) + ')</span><b id="dpV">' + fmt(st.troops) + '</b></label><input type="range" id="dpR" min="0" max="' + mx() + '" step="100" value="' + st.troops + '" data-i="troops"></div><div class="sec">군량</div><div class="opts c4">';
      DEPLOY_FOOD.forEach(function (n) { h += '<button class="opt' + (st.turns === n ? ' on' : '') + '" type="button" data-a="turns" data-v="' + n + '"><b>' + days(n) + '분</b><small>' + fmt(Math.ceil(st.troops / 20) * n) + '</small></button>'; });
      h += '</div><p class="note" id="dpN">' + foodNote() + '</p>';
      return h + '</div><div class="dlg-f"><button class="btn" type="button" data-a="prev">‹ 무장</button><div class="pv" id="dpP">' + pv() + '</div><button class="btn pri" type="button" data-a="ok"' + (st.ids.length && st.troops >= 100 ? '' : ' disabled') + '>출진</button></div>';
    },
    on: {
      type: function (el) { var t = el.getAttribute('data-v'); if (!usable(t)) return toast(t === 'ram' ? '충차가 없습니다' : WEAPON_NAMES[UNIT_TYPES[t].weapon] + ' 재고가 없습니다'); st.type = t; st.auto = true; fix(); refreshDialog(); },
      pick: function (el) { var id = +el.getAttribute('data-v'), i = st.ids.indexOf(id); if (i >= 0) st.ids.splice(i, 1); else if (st.ids.length < 3) st.ids.push(id); else return toast('최대 3명입니다'); st.auto = true; fix(); refreshDialog(); },
      turns: function (el) { st.turns = +el.getAttribute('data-v'); refreshDialog(); },
      atauto: function () { EX.auto(); },
      auto: function () { st.ids = autoTeam(b, st.type, Math.min(b.troops, 8000)); st.auto = true; fix(); toast(st.ids.length ? '자동 편성 ' + st.ids.length + '명' : '편성할 무장이 없습니다', 1800); refreshDialog(); },
      next: function () { if (!st.ids.length) return toast('주장을 고르세요'); fix(); if (st.troops < 100) return toast('데리고 나갈 병력이 없습니다'); st.step = 2; EX.open(); },
      prev: function () { st.step = 1; EX.close(); paintDialog(0); },
      troops: function (el) {
        st.troops = +el.value; st.auto = false; $('dpV').textContent = fmt(st.troops); $('dpP').innerHTML = pv();
        var bs = document.querySelectorAll('#modal [data-a="turns"]');                 // 군량 칸의 수량과 모자람 표시도 바로 고친다
        for (var k = 0; k < bs.length; k++) bs[k].querySelector('small').textContent = fmt(Math.ceil(st.troops / 20) * +bs[k].getAttribute('data-v'));
        if ($('dpN')) $('dpN').innerHTML = foodNote();
        var ok = document.querySelector('#modal [data-a="ok"]'); if (ok) ok.disabled = !(st.troops >= 100);
      },
      ok: function () {
        if (st.step !== 2) return;
        var r = cmdDeploy(b, { type: st.type, ids: st.ids, troops: st.troops, food: food(), at: st.at || undefined });
        if (!r.ok) return toast(r.msg);
        closeDialog(); sfx('deploy');
        var u = r.unit, name = uName(u);
        clearSel(); refreshHud(); syncScene();                       // 막 나온 부대를 지도에 세우고
        if (!onScreen(u.c, u.r, 20)) jumpTo(u.c, u.r, Math.max(cam.z, 0.8));
        UI.busy = true;
        fxDeploy(u, b, function () {                                // 성에서 걸어 나오는 모습을 보인 뒤 고른 상태로
          UI.busy = false;
          if (alive(u)) { selectUnit(u); UI.sret = backToBase(b.id); talk(uLeader(u), sayLine(uLeader(u), 'deploy'), name + ' 출진 — ' + UNIT_TYPES[u.type].name + ' ' + fmt(u.troops) + '명', 2600); }
          afterAction();
        });
      }
    }
  };
  EX = exitPick(b, st, D);
  showDialog(D);
}
function flowTransport(b) {
  var cp0 = baseCorps(b);                                       // v0.18: 군단에 맡긴 거점에서도 보낸다(군단장은 자리를 지킨다 · 행동력은 직할의 것 · 나간 수송대는 직할)
  var list = idleOfficers(b).filter(function (o) { return !(cp0 && cp0.lead === o.id); }).sort(function (x, y) { return aiMilScore(x) - aiMilScore(y); });
  if (!list.length) return toast('행동할 수 있는 무장이 없습니다');
  if (b.troops < 100) return toast('호위할 병력이 없습니다');
  var st = { step: 1, id: list[0].id, troops: Math.min(1000, Math.floor(b.troops / 100) * 100), gold: 0, food: 0, spear: 0, halberd: 0, bow: 0, horse: 0, ram: 0, at: null, back: !!UI.tback }, D, EX;
  var fs = [['troops', '병력', b.troops, 100], ['gold', '금', b.gold, 50], ['food', '병량', b.food, 500], ['spear', '창', b.w.spear, 100], ['halberd', '극', b.w.halberd, 100], ['bow', '노', b.w.bow, 100], ['horse', '군마', b.w.horse, 100], ['ram', '충차', b.w.ram, 1]];
  function load() { var a = []; fs.forEach(function (f) { if (st[f[0]] > 0) a.push(f[1] + ' ' + fmt(st[f[0]])); }); return a.join(' · '); }
  var on = {
    pick: function (el) { st.id = +el.getAttribute('data-v'); refreshDialog(); },
    auto: function () { var t = autoTeam(b, 'trans', 0); if (t.length) st.id = t[0]; toast('자동 선택', 1500); refreshDialog(); },
    next: function () { st.step = 2; EX.open(); },
    prev: function () { st.step = 1; EX.close(); paintDialog(0); },
    atauto: function () { EX.auto(); },
    ok: function () {
      if (st.step !== 2) return;
      var need = Math.ceil(st.troops / 20) * 8;
      var r = cmdDeploy(b, { type: 'trans', ids: [st.id], troops: st.troops, food: Math.max(st.food, Math.min(b.food, need)), gold: st.gold, cargo: { spear: st.spear, halberd: st.halberd, bow: st.bow, horse: st.horse, ram: st.ram }, at: st.at || undefined, back: st.back });
      if (!r.ok) return toast(r.msg);
      closeDialog(); sfx('drum'); talk(uLeader(r.unit), sayLine(uLeader(r.unit), 'trans'), st.back ? '수송대 출발 — 짐을 내리면 ' + euro(b.n) + ' 돌아옵니다' : '수송대 출발 — 거점에 들이거나, 아군 부대 옆에서 [보급]', 3200); syncScene(); selectUnit(r.unit); UI.sret = backToBase(b.id); afterAction();
    }
  };
  fs.forEach(function (f) { on[f[0]] = function (el) { st[f[0]] = +el.value; $('tv_' + f[0]).textContent = fmt(st[f[0]]); }; });
  on.tback = function (el) { st.back = el.getAttribute('data-v') === '1'; UI.tback = st.back; saveOpts(); refreshDialog(); };      // v0.18.1: 고른 것은 다음 수송 창에도 그대로
  D = {
    render: function () {
      var h, i;
      if (st.step === 1) {                                         // ① 호송 무장 · 실을 것
        h = dlgHead('수송 — ' + b.n + stepTag(1, 2, '호송 무장 · 짐')) + '<div class="dlg-b"><div class="sec">호송 무장<button class="btn auto" type="button" data-a="auto">자동</button></div><div class="rows">';
        for (i = 0; i < list.length; i++) h += offRow(list[i], { a: 'pick', sel: list[i].id === st.id });
        h += '</div><div class="sec">실을 것</div>';
        for (i = 0; i < fs.length; i++) { var f = fs[i], m = Math.floor(f[2] / f[3]) * f[3]; if (m <= 0 && f[0] !== 'troops') continue; h += '<div class="fld"><label><span>' + f[1] + ' (보유 ' + fmt(f[2]) + ')</span><b id="tv_' + f[0] + '">' + fmt(st[f[0]]) + '</b></label><input type="range" id="tr_' + f[0] + '" min="' + (f[0] === 'troops' ? 100 : 0) + '" max="' + m + '" step="' + f[3] + '" value="' + st[f[0]] + '" data-i="' + f[0] + '"></div>'; }
        return h + '<p class="note">군량 80일분은 자동으로 실립니다</p></div><div class="dlg-f"><div class="pv">행동력 ' + AP.deploy + '</div><button class="btn pri" type="button" data-a="next">다음 ›</button></div>';
      }
      // ② 내린 뒤 · 나갈 자리(지도에서)
      h = dlgHead('수송 — ' + b.n + stepTag(2, 2, '내린 뒤 · 나갈 자리')) + '<div class="dlg-b"><p class="note team">호송 <b>' + off(st.id).n + '</b> · ' + load() + '</p>';
      h += EX.line();
      h += '<div class="sec">짐을 내린 뒤 <small>호송 무장은</small></div><div class="seg tbk"><button type="button" data-a="tback" data-v="0"' + (st.back ? '' : ' class="on"') + '>그곳에 머문다</button><button type="button" data-a="tback" data-v="1"' + (st.back ? ' class="on"' : '') + '>' + euro(b.n) + ' 돌아온다</button></div>';
      return h + '<p class="note">아군 거점에 들이면 합쳐지고, <b>아군 부대 옆</b>에서는 [보급]으로 병량과 병력을 넘깁니다' + (st.back ? ' · <b>돌아온다</b>: 거점에 짐을 내린 무장은 걸어서, 부대에 보급한 수송대는 행군으로 돌아옵니다' : '') + '</p></div><div class="dlg-f"><button class="btn" type="button" data-a="prev">‹ 짐</button><div class="pv">행동력 ' + AP.deploy + '</div><button class="btn pri" type="button" data-a="ok">출발</button></div>';
    },
    on: on
  };
  EX = exitPick(b, st, D);
  showDialog(D);
}

"""
s = cut(s, "function deployRing(b, st) {", "/* ---------- 목록·기록·메뉴 ---------- */", NEW)

# ---------- 이동: 보낼 곳을 지도에서도 ----------
MOVE = r"""function flowMove(b) {
  var dests = facBases(b.owner).filter(function (x) { return x.id !== b.id; });
  if (!dests.length) return toast('옮겨 갈 다른 거점이 없습니다');
  pickOfficers({ keep: true, title: '이동 — 보낼 무장', list: idleOfficers(b), max: 6, key: function (o) { return o.ldr + o.war + o.int + o.pol; }, ok: '다음', preview: function (os) { return os.length + '명 선택'; } },
    function (os) {
      dests.sort(function (x, y) { return hdist(b.c, b.r, x.c, x.r) - hdist(b.c, b.r, y.c, y.r); });
      var mv = { sel: -1 };
      function go(id) { var r = cmdMoveOfficers(b, ids(os), id); if (r.ok) closeDialog(); done(r, r.ok ? os.length + '명 출발 — ' + euro(G.bases[id].n) + ' ' + days(r.turns) + ' 뒤 도착' : '', '', os[0], 'move'); }
      function marks() {                                         // v0.20: 지도에 우리 성마다 이름과 걸리는 날수
        var list = [{ c: b.c, r: b.r, cls: 'ex src', html: '<b>' + b.n + '</b><small>여기서</small>', dy: -30 }];
        dests.forEach(function (x) { list.push({ c: x.c, r: x.r, cls: 'ex' + (x.id === mv.sel ? ' on' : ''), html: '<b>' + x.n + '</b><small>' + days(travelTurns(b, x)) + '</small>', dy: -30 }); });
        marksSet(list); requestDraw();
      }
      var D = {
        see: true,
        pick: {
          list: function () { return dests.map(function (x) { return { c: x.c, r: x.r, on: x.id === mv.sel }; }); },
          has: function (c, r) { return dests.some(function (x) { return x.c === c && x.r === r; }); },
          show: marks,
          tap: function (c, r) {
            var bb = baseAt(c, r);
            if (!bb || dests.indexOf(bb) < 0) return toast(bb && bb.id === b.id ? '보내는 성입니다 — 다른 우리 성을 누르세요' : '우리 성을 누르세요(이름이 뜬 곳)', 1700);
            mv.sel = bb.id; sfx('ui'); refreshDialog(); marks();
            var row = document.querySelector('#modal .row.sel'); if (row && row.scrollIntoView) row.scrollIntoView({ block: 'nearest' });
          }
        },
        render: function () {
          var h = dlgHead('이동 — 어디로 보낼까요') + '<div class="dlg-b"><p class="note">지도에서 <b>우리 성</b>을 누르거나 아래에서 고르세요 · ' + os.length + '명</p><div class="rows">';
          for (var i = 0; i < dests.length; i++) h += '<button class="row' + (dests[i].id === mv.sel ? ' sel' : '') + '" type="button" data-a="d" data-v="' + dests[i].id + '"><span class="mid"><span class="nm">' + dests[i].n + '</span><span class="ds">' + SIZE_NAME[dests[i].sz] + ' · 무장 ' + baseOfficers(dests[i]).length + '명 · 병력 ' + fmt(dests[i].troops) + '</span></span><span class="rt"><b>' + days(travelTurns(b, dests[i])) + '</b></span></button>';
          h += '</div></div>';
          if (mv.sel >= 0) h += '<div class="dlg-f"><div class="pv">' + G.bases[mv.sel].n + ' — ' + days(travelTurns(b, G.bases[mv.sel])) + '</div><button class="btn pri" type="button" data-a="go">' + euro(G.bases[mv.sel].n) + ' 보낸다</button></div>';
          return h;
        },
        on: { d: function (el) { go(+el.getAttribute('data-v')); }, go: function () { if (mv.sel >= 0) go(mv.sel); } }
      };
      showDialog(D, true);
      var dl = document.querySelector('#modal .dlg'), top = $('hud') ? $('hud').getBoundingClientRect().bottom : 90, bot = dl ? dl.getBoundingClientRect().top : CH * 0.5;
      frameHexes([[b.c, b.r]].concat(dests.map(function (x) { return [x.c, x.r]; })), top + 64, bot - 34, 1.1);
    });
}
"""
s = cut(s, "function flowMove(b) {", "function flowCaptive(b) {", MOVE)

# ---------- 등용: 정렬 ----------
s = rep(s, """  showDialog({
    render: function () {
      var idle = idleOfficers(b).length, i, t, w, h = dlgHead('등용 — 누구를 부를까요') + '<div class="dlg-b">';
      if (!idle) h += '<p class="note">쉬는 무장이 없어 지금은 권할 수 없습니다</p>';
      if (here.length) {
        h += '<div class="sec">이 거점의 재야·포로</div><div class="rows">';
        for (i = 0; i < here.length; i++) { t = here[i]; w = why(t); h += offRow(t, { a: 't', dim: !!w,""",
"""  var srt = 'p';                                               // v0.20 정렬: p 가능성 · sum 능력 합 · ldr/war/int/pol/cha · a0~a4 적성(창 극 노 기 병기)
  var SRT = [['p', '가능성'], ['sum', '능력'], ['ldr', '통솔'], ['war', '무력'], ['int', '지력'], ['pol', '정치'], ['cha', '매력'], ['a0', '창'], ['a1', '극'], ['a2', '노'], ['a3', '기'], ['a4', '병기']];
  function sval(t) {
    if (srt === 'sum') return t.ldr + t.war + t.int + t.pol + t.cha;
    if (srt.charAt(0) === 'a') return APT_RANK[t.apt.charAt(+srt.charAt(1))] * 1000 + t.ldr + t.war;
    return t[srt];
  }
  function sopt() { return srt === 'p' || srt === 'sum' ? {} : (srt.charAt(0) === 'a' ? { apt: +srt.charAt(1) } : { hi: srt }); }
  function mixo(a, x) { for (var k in x) a[k] = x[k]; return a; }
  showDialog({
    render: function () {
      var idle = idleOfficers(b).length, i, t, w, h = dlgHead('등용 — 누구를 부를까요') + '<div class="dlg-b">';
      h += '<div class="srt" role="group" aria-label="정렬"><i>정렬</i>'; for (i = 0; i < SRT.length; i++) h += '<button type="button" data-a="srt" data-v="' + SRT[i][0] + '"' + (srt === SRT[i][0] ? ' class="on"' : '') + (i === 7 ? ' data-g="1"' : '') + '>' + SRT[i][1] + '</button>'; h += '</div>';
      if (!idle) h += '<p class="note">쉬는 무장이 없어 지금은 권할 수 없습니다</p>';
      if (here.length) {
        var HL = here.slice(); if (srt !== 'p') HL.sort(function (x, y) { return sval(y) - sval(x); });
        h += '<div class="sec">이 거점의 재야·포로</div><div class="rows">';
        for (i = 0; i < HL.length; i++) { t = HL[i]; w = why(t); h += offRow(t, mixo({ a: 't', dim: !!w,""")
s = rep(s, """(w || !idle ? (originTxt(t) ? '<br><small>' + originTxt(t) + '</small>' : '') : tieSub(t, true)) }); }
        h += '</div>';
      }""", """(w || !idle ? (originTxt(t) ? '<br><small>' + originTxt(t) + '</small>' : '') : tieSub(t, true)) }, sopt())); }
        h += '</div>';
      }""")
s = rep(s, """.sort(function (x, y) { return (x.w ? 1 : 0) - (y.w ? 1 : 0) || y.p - x.p || x.t.loy - y.t.loy; });""",
        """.sort(function (x, y) { return srt === 'p' ? ((x.w ? 1 : 0) - (y.w ? 1 : 0) || y.p - x.p || x.t.loy - y.t.loy) : (sval(y.t) - sval(x.t) || y.p - x.p); });""")
s = rep(s, """for (i = 0; i < L.length; i++) { t = L[i].t; w = L[i].w; h += offRow(t, { a: 't', dim: !!w || !L[i].p,""", """for (i = 0; i < L.length; i++) { t = L[i].t; w = L[i].w; h += offRow(t, mixo({ a: 't', dim: !!w || !L[i].p,""")
s = rep(s, """(idle ? (L[i].p ? bestM(t) : '') + pcBest(L[i].p) + (L[i].p ? tieSub(t, false) : '') : '')) }); }""", """(idle ? (L[i].p ? bestM(t) : '') + pcBest(L[i].p) + (L[i].p ? tieSub(t, false) : '') : '')) }, sopt())); }""")
s = rep(s, """    on: { t: function (el) {
      var t = off(+el.getAttribute('data-v')), w = why(t), farT = t.st === 'active';""", """    on: { srt: function (el) { srt = el.getAttribute('data-v'); refreshDialog(); var bd = document.querySelector('#modal .dlg-b'); if (bd) bd.scrollTop = 0; }, t: function (el) {
      var t = off(+el.getAttribute('data-v')), w = why(t), farT = t.st === 'active';""")
wr('src/ui_panels.js', s)

s = rd('src/style.css')
s = s.rstrip('\n') + """
/* ── v0.20 지도에서 고르기: 칸 위의 딱지 · 단계 표시 · 정렬 줄 ── */
.mk { position: absolute; left: 0; top: 0; will-change: transform; pointer-events: none; white-space: nowrap; text-align: center; line-height: 1.12; }
.mk.ex { padding: 1px 6px 2px; background: #f4efe3f2; border: 1.4px solid var(--ink); border-radius: var(--rad-s); box-shadow: 0 1px 4px #1b1a1840; }
.mk.ex b { display: block; font: 900 12.5px var(--font-display); color: var(--ink); }
.mk.ex small { display: block; font: 700 10px var(--font-body); color: var(--dim); }
.mk.ex.on { background: var(--seal); border-color: var(--seal-2); box-shadow: 0 0 0 2px #f4efe3, 0 2px 7px #1b1a1866; }
.mk.ex.on b, .mk.ex.on small { color: var(--seal-ink); }
.mk.ex.no { opacity: .55; border-style: dashed; }
.mk.ex.src { background: var(--ink); border-color: var(--ink); } .mk.ex.src b, .mk.ex.src small { color: var(--paper); }
#app.picking #mini { display: none; } #app.picking #toast { top: 96px; }
.dlg-h h2 small.stp { font: 700 12px var(--font-body); color: var(--dim); margin-left: 6px; white-space: nowrap; }
.note.team { margin: 2px 0 2px; font-size: 13px; color: var(--ink-2); } .note.team b { color: var(--ink); }
.dpat-t.wide { margin: 0 0 4px; } .dpat-t.wide small { display: inline; margin-left: 6px; }
.dlg-f .btn { flex: none; }
.srt { display: flex; gap: 5px; align-items: center; overflow-x: auto; margin: 0 -14px 4px; padding: 2px 14px 7px; scrollbar-width: none; -webkit-overflow-scrolling: touch; position: sticky; top: -9px; z-index: 2; background-color: var(--paper); }
.srt::-webkit-scrollbar { display: none; }
.srt i { font: 700 12px var(--font-body); font-style: normal; color: var(--dim); flex: none; margin-right: 1px; }
.srt button { flex: none; height: 30px; padding: 0 10px; font: 700 13px var(--font-body); color: var(--ink-2); border: 1.2px solid var(--line-2); border-radius: var(--rad-s); background: #fffdf680; }
.srt button[data-g] { margin-left: 7px; }
.srt button.on { background: var(--ink); border-color: var(--ink); color: var(--paper); }
"""
wr('src/style.css', s)
print('s5 ok')
