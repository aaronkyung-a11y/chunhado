/* ===== 천하도 — 패널·대화상자·조작 흐름 ===== */
var SHEET = null, MODAL = null, toastT = 0;
var SIZE_NAME = { L: '대도시', M: '중도시', S: '소도시', G: '관문' };
var ICO = {
  gold: '<svg viewBox="0 0 16 16"><circle cx="8" cy="8" r="6.5" fill="#c9a23f" stroke="#1b1a18"/><rect x="5.6" y="5.6" width="4.8" height="4.8" fill="#1b1a18"/></svg>',
  food: '<svg viewBox="0 0 16 16"><path d="M5 2.6h6l-1.2 2.3c2.6 1.4 3.7 4 3.2 6.5-.4 1.8-1.7 2.8-5 2.8s-4.6-1-5-2.8c-.5-2.5.6-5.1 3.2-6.5z" fill="#e6dcc0" stroke="#1b1a18"/><path d="M6 5h4" stroke="#1b1a18"/></svg>',
  troops: '<svg viewBox="0 0 16 16"><circle cx="8" cy="5" r="2.7" fill="#e2ddd0" stroke="#1b1a18"/><path d="M2.8 14c.3-3.4 2.3-5 5.2-5s4.9 1.6 5.2 5z" fill="#b9b3a4" stroke="#1b1a18"/></svg>',
  morale: '<svg viewBox="0 0 16 16"><path d="M8 1.5c.6 2.8 4 4.2 4 7.8A4 4 0 0 1 8 13.5 4 4 0 0 1 4 9.3c0-1.7 1-2.6 1.7-3.6.4 1 .9 1.5 1.5 1.7C6.9 5.2 7.3 3.2 8 1.5z" fill="#b5332a" stroke="#1b1a18"/></svg>',
  order: '<svg viewBox="0 0 16 16"><path d="M8 1.5l5 1.8v4.2c0 3.2-2.1 5.5-5 6.9-2.9-1.4-5-3.7-5-6.9V3.3z" fill="#8fa698" stroke="#1b1a18"/></svg>',
  dur: '<svg viewBox="0 0 16 16"><path d="M2 14V5h2.4v2h2.2V5h2.8v2h2.2V5H14v9z" fill="#d3ccba" stroke="#1b1a18"/></svg>',
  spear: '<svg viewBox="0 0 16 16"><path d="M3 13L11 5" stroke="#4a4037" stroke-width="1.6"/><path d="M10 6l4-4-1 5z" fill="#e2ddd0" stroke="#1b1a18" stroke-width=".8"/></svg>',
  halberd: '<svg viewBox="0 0 16 16"><path d="M3 13L12 4" stroke="#4a4037" stroke-width="1.6"/><path d="M11 5l3-3-.5 3.5z" fill="#e2ddd0" stroke="#1b1a18" stroke-width=".8"/><path d="M7.6 5.4c1.9-1 3.6-.4 4.2 1.4-1.4-.4-2.4 0-3.1 1z" fill="#e2ddd0" stroke="#1b1a18" stroke-width=".8"/></svg>',
  bow: '<svg viewBox="0 0 16 16"><path d="M2.5 6c3-3.2 8-3.2 11 0" fill="none" stroke="#4a4037" stroke-width="1.7"/><path d="M8 3.5v10" stroke="#4a4037" stroke-width="1.7"/><path d="M2.5 6L8 8.6 13.5 6" fill="none" stroke="#e2ddd0" stroke-width=".9"/></svg>',
  horse: '<svg viewBox="0 0 16 16"><path d="M3.6 13.5V7.2a4.4 4.4 0 0 1 8.8 0v6.3h-2.3V7.2a2.1 2.1 0 0 0-4.2 0v6.3z" fill="#b9a37c" stroke="#1b1a18"/></svg>',
  ram: '<svg viewBox="0 0 16 16"><rect x="2" y="5.6" width="9.6" height="3.8" rx="1" fill="#a8946c" stroke="#1b1a18"/><path d="M11.6 5.6l2.9 1.9-2.9 1.9z" fill="#e2ddd0" stroke="#1b1a18" stroke-width=".8"/><circle cx="4.8" cy="12" r="1.7" fill="#3a332a"/><circle cx="9.6" cy="12" r="1.7" fill="#3a332a"/></svg>'
};
function ico(k) { return '<i class="ico">' + ICO[k] + '</i>'; }
function thumb(key, cls) { return '<img class="th' + (cls ? ' ' + cls : '') + '" alt="" src="' + SPRITES[key].u + '">'; }
function days(turns) { return fmt(turns * 10) + '일'; }
function unitFoodTurns(x) { return x.troops > 0 ? Math.floor(x.food / Math.ceil(x.troops / (uHas(x, '둔전') ? 40 : 20))) : 0; }

function toast(msg, ms) {
  var t = $('toast'); t.textContent = msg; t.classList.add('on');
  clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove('on'); }, ms || 2400);
}
function showSheet(s) { SHEET = s; var el = $('sheet'); el.className = 'on' + (s.cls ? ' ' + s.cls : ''); el.innerHTML = s.render(); }
function refreshSheet() {
  if (!SHEET) return;
  var el = $('sheet'), body = el.querySelector('.sh-body'), st = body ? body.scrollTop : 0;
  el.innerHTML = SHEET.render();
  body = el.querySelector('.sh-body'); if (body) body.scrollTop = st;
}
function closeSheet() { showHome(); }
/* 창은 겹쳐 열 수 있다. push 로 열면 지금 창을 아래에 깔아 두고, ×(또는 바깥 누르기)는 한 단계만 뒤로 간다.
   명령을 마쳤을 때처럼 한꺼번에 닫을 때는 closeDialog(). */
var MSTACK = [], MPAINT = 0;
function dlgScroll() { var b = $('modal').querySelector('.dlg-b'); return b ? b.scrollTop : 0; }
function paintDialog(st) {
  var m = $('modal'); m.innerHTML = '<div class="dlg">' + MODAL.render() + '</div>'; m.classList.add('on');
  if (st) { var b = m.querySelector('.dlg-b'); if (b) b.scrollTop = st; }
  MPAINT = Date.now();
  paintRet();
}
function showDialog(d, push) { if (push && MODAL) MSTACK.push({ d: MODAL, st: dlgScroll() }); else MSTACK.length = 0; MODAL = d; paintDialog(0); }
function backDialog() {
  if (MODAL && MODAL.lock) return;                                   // 끝난 판의 창처럼 닫으면 안 되는 창
  if (MSTACK.length) { var p = MSTACK.pop(); MODAL = p.d; paintDialog(p.st); } else closeDialog();
}
function refreshDialog() {
  if (!MODAL) return;
  var m = $('modal'), b = m.querySelector('.dlg-b'), st = b ? b.scrollTop : 0;
  m.innerHTML = '<div class="dlg">' + MODAL.render() + '</div>';
  b = m.querySelector('.dlg-b'); if (b) b.scrollTop = st;
}
function closeDialog() { MSTACK.length = 0; MODAL = null; var m = $('modal'); m.classList.remove('on'); m.innerHTML = ''; paintRet(); }
function dlgHead(title) { return '<div class="dlg-h"><h2>' + title + '</h2><button class="x" data-a="close" type="button" aria-label="닫기">×</button></div>'; }
function delegate(root, getH, onClose) {
  root.addEventListener('click', function (e) {
    var el = e.target.closest ? e.target.closest('[data-a]') : null;
    if (root.id === 'modal' && Date.now() - MPAINT < 200) return;      // 창이 막 바뀐 직후의 누름(연달아 두 번 누름)은 버린다 — 새 창의 엉뚱한 단추에 닿지 않게
    if (!el || !root.contains(el)) { if (root.id === 'modal' && e.target === root) backDialog(); return; }
    var a = el.getAttribute('data-a'), hs = getH();
    if (root.id === 'sheet' && UI.busy) return;                         // 움직이는 장면이 나오는 동안에는 아래 창의 단추를 받지 않는다
    audioInit(); bgmKick(); sfx('ui');
    if (a === 'close') { onClose(); return; }
    if (hs && hs.on && hs.on[a]) hs.on[a](el);
  });
  root.addEventListener('input', function (e) {
    var el = e.target.closest ? e.target.closest('[data-i]') : null; if (!el) return;
    var hs = getH(), a = el.getAttribute('data-i');
    if (hs && hs.on && hs.on[a]) hs.on[a](el);
  });
}

/* ---------- 공통 조각 ---------- */
function porTag(o, cls) { var u = o ? POR_URL[o.por] : ''; return '<i class="por' + (cls ? ' ' + cls : '') + '"' + (u ? ' style="background-image:url(' + u + '),var(--porbg)"' : '') + '></i>'; }
/* 장면 초상(3:4): 장수 정보·소개 창에서 쓴다. 장면이 없으면 큰 흉상 */
function sceneTag(o) { var u = o ? sceneUrl(o.por) : ''; return u ? '<i class="por sc" style="background-image:url(' + u + '),var(--porbg)"></i>' : porTag(o, 'lg'); }
function st5(o, hi) {
  var ks = [['ldr', '통'], ['war', '무'], ['int', '지'], ['pol', '정'], ['cha', '매']], s = '<span class="st5">';
  for (var i = 0; i < 5; i++) s += '<span><i>' + ks[i][1] + '</i> <b' + (hi === ks[i][0] ? ' class="hi"' : '') + '>' + o[ks[i][0]] + '</b></span>';
  return s + '</span>';
}
function skTag(o) { return o.sk ? '<em>' + o.sk + '</em>' : ''; }
function facChip(f) { return '<span class="chip" style="background:' + (f >= 0 ? G.factions[f].color : '#8d877b') + '">' + (f >= 0 ? G.factions[f].name : '빈 땅') + '</span>'; }
function offStatus(o) {
  if (o.st === 'travel') return '이동 중 (' + days(o.eta) + ')';
  if (o.unit !== null) return '출진 중';
  return o.acted ? '행동 완료' : '대기';
}
function offRow(o, opt) {
  opt = opt || {};
  return '<button class="row' + (opt.sel ? ' sel' : '') + (opt.dim ? ' dim' : '') + '" type="button" data-a="' + (opt.a || 'off') + '" data-v="' + o.id + '">' + porTag(o) +
    '<span class="mid"><span class="nm">' + (opt.badge ? '<span class="hi">' + opt.badge + '</span> ' : '') + o.n + skTag(o) + '</span><span class="ds">' + (opt.ds !== undefined ? opt.ds : st5(o, opt.hi)) + '</span></span>' +
    (opt.rt ? '<span class="rt">' + opt.rt + '</span>' : '') + '</button>';
}

/* 무장 선택 표(열 제목을 누르면 정렬). opts: {title, list, min, max, hi, key(o), rt(o), rtHead, preview(os), ok, auto(n)→ids} */
function pickOfficers(opts, cb) {
  var sel = [], max = opts.max || 1, min = opts.min || 1, sortK = null, sortDir = -1, autoN = 0;
  if (!opts.list.length) { toast('행동할 수 있는 무장이 없습니다'); return; }
  var COLS = [['ldr', '통'], ['war', '무'], ['int', '지'], ['pol', '정'], ['cha', '매']];
  function sorted() {
    var L = opts.list.slice();
    if (sortK) L.sort(function (a, b) { return (b[sortK] - a[sortK]) * -sortDir; }); else L.sort(function (a, b) { return opts.key(b) - opts.key(a); });
    return L;
  }
  showDialog({
    render: function () {
      var list = sorted(), i, j, h = dlgHead(opts.title) + '<div class="dlg-b tbl"><div class="th-row"><span class="c-n">무장</span>';
      for (j = 0; j < 5; j++) h += '<button type="button" class="c-s' + (sortK === COLS[j][0] ? ' on' : (!sortK && opts.hi === COLS[j][0] ? ' hi' : '')) + '" data-a="sort" data-v="' + COLS[j][0] + '">' + COLS[j][1] + (sortK === COLS[j][0] ? (sortDir < 0 ? '▾' : '▴') : '') + '</button>';
      h += '<span class="c-x">' + (opts.rtHead || '특기') + '</span></div>';
      for (i = 0; i < list.length; i++) {
        var o = list[i], si = sel.indexOf(o.id);
        h += '<button class="tr' + (si >= 0 ? ' sel' : '') + '" type="button" data-a="pick" data-v="' + o.id + '">' + porTag(o, 'sm') + '<span class="c-n">' + (si >= 0 && max > 1 ? '<i class="ord">' + (si + 1) + '</i>' : '') + o.n + '</span>';
        for (j = 0; j < 5; j++) h += '<span class="c-s' + (opts.hi === COLS[j][0] ? ' hi' : '') + '">' + o[COLS[j][0]] + '</span>';
        h += '<span class="c-x">' + (opts.rt ? opts.rt(o) : (o.sk || '—')) + '</span></button>';
      }
      var os = sel.map(off), strip = '';
      if (os.length) { strip = '<div class="selstrip">'; for (i = 0; i < os.length; i++) strip += '<span>' + porTag(os[i], 'md') + '<b>' + (max > 1 ? (i + 1) + '. ' : '') + os[i].n + '</b></span>'; strip += '</div>'; }
      h += '</div>' + strip + '<div class="dlg-f"><div class="pv">' + (os.length ? (opts.preview ? opts.preview(os) : os.length + '명 선택') : (max > 1 ? '무장을 고르세요 (최대 ' + max + '명)' : '무장을 고르세요')) + '</div>' +
        (opts.auto ? '<button class="btn auto" type="button" data-a="auto">자동</button>' : '') +
        '<button class="btn pri" type="button" data-a="ok"' + (os.length < min ? ' disabled' : '') + '>' + (opts.ok || '실행') + '</button></div>';
      return h;
    },
    on: {
      sort: function (el) { var k = el.getAttribute('data-v'); if (sortK === k) sortDir = -sortDir; else { sortK = k; sortDir = -1; } refreshDialog(); },
      pick: function (el) {
        var id = +el.getAttribute('data-v'), i = sel.indexOf(id);
        if (i >= 0) sel.splice(i, 1); else if (max === 1) sel = [id]; else if (sel.length < max) sel.push(id); else { toast('최대 ' + max + '명입니다'); return; }
        refreshDialog();
      },
      auto: function () {                       // 누를 때마다: 효과가 가장 큰 조합 ↔ 한 명만
        var n = (max > 1 && autoN % 2 === 1) ? 1 : max; autoN++;
        sel = opts.auto(n);
        toast(max === 1 ? '가장 알맞은 무장을 골랐습니다' : (n > 1 ? '효과가 가장 큰 조합 ' + sel.length + '명 — 한 번 더 누르면 한 명만' : '한 명만 쓸 때 가장 나은 무장'), 2200);
        refreshDialog();
      },
      ok: function () {
        if (sel.length < min) return;
        var os = sel.map(off);
        if (opts.keep) { cb(os); return; }                       // 다음 창이 이 표 위에 겹쳐 열린다
        var m = MODAL, stk = MSTACK.slice(), sc = dlgScroll();
        closeDialog();
        if (cb(os) === false && !MODAL) { MSTACK = stk; MODAL = m; paintDialog(sc); }   // 명령이 안 됐으면(금·행동력 부족 등) 표를 그대로 둔다
      }
    }
  }, !!opts.push);
}
function ids(os) { return os.map(function (o) { return o.id; }); }

/* 무장 상세 */
function showOfficer(o) {
  var apt = ['창', '극', '노', '기', '병기'], a = '';
  for (var i = 0; i < 5; i++) a += '<div class="' + o.apt.charAt(i) + '">' + apt[i] + '<b>' + o.apt.charAt(i) + '</b></div>';
  var bars = '', ks = [['ldr', '통솔'], ['war', '무력'], ['int', '지력'], ['pol', '정치'], ['cha', '매력']];
  for (i = 0; i < 5; i++) bars += '<div class="bar"><span>' + ks[i][1] + '</span><i><u style="width:' + o[ks[i][0]] + '%"></u></i><b>' + o[ks[i][0]] + '</b></div>';
  var where = o.st === 'free' ? '재야 (' + G.bases[o.loc].n + ')' : o.st === 'captive' ? '포로 (' + G.bases[o.loc].n + ')' : (o.unit !== null ? '출진 중' : G.bases[o.loc].n);
  showDialog({
    render: function () {
      return dlgHead(o.n + ' ' + (o.f >= 0 ? facChip(o.f) : '')) + '<div class="dlg-b"><div class="card">' + sceneTag(o) + '<div class="bars">' + bars + '</div></div>' +
        '<div class="apt">' + a + '</div>' +
        (o.sk ? '<p><b class="hi">특기 · ' + o.sk + '</b><br>' + SKILLS[o.sk] + '</p>' : '<p class="note">특기 없음</p>') +
        '<div class="stats"><div><span>소재</span><b>' + where + '</b></div>' + (o.f >= 0 ? '<div><span>충성</span><b>' + o.loy + '</b></div><div><span>지휘</span><b>' + fmt(cmdCap(o)) + '</b></div><div><span>공적</span><b>' + fmt(o.merit) + '</b></div>' : '') + '</div></div>';
    }, on: {}
  }, true);                                              // 목록 같은 창 위에서 열었으면 ×로 그 창에 돌아간다
}

/* ---------- HUD ---------- */
function pendingUnits() { return facUnits(G.player).filter(function (u) { return !u.done && !(u.dest >= 0) && !u.moved; }); }
function refreshHud() {
  if (!G) return;
  var F = G.factions[G.player], L = off(F.lord);
  $('hudY').textContent = G.year + '년'; $('hudM').textContent = G.month + '월 ' + ['상순', '중순', '하순'][G.xun];
  var hf = $('hudFac'); hf.children[0].style.background = F.color; hf.children[1].style.backgroundImage = POR_URL[L.por] ? 'url(' + POR_URL[L.por] + '),var(--porbg)' : ''; hf.children[2].textContent = F.name + '군';
  $('hudAPv').textContent = F.ap; $('hudAPb').style.width = Math.round(F.ap / 255 * 100) + '%';
  var g = 0, fd = 0, t = 0;
  facBases(G.player).forEach(function (b) { g += b.gold; fd += b.food; t += b.troops; });
  facUnits(G.player).forEach(function (u) { t += u.troops; });
  $('hudRes').innerHTML = '<span>' + ico('gold') + '<b>' + fmt(g) + '</b></span><span>' + ico('food') + '<b>' + fmt(fd) + '</b></span><span>' + ico('troops') + '<b>' + fmt(t) + '</b></span><span>' + ico('dur') + '<b>' + facCities(G.player).length + '</b>성</span>';
  var n = pendingUnits().length;
  $('btnNext').querySelector('.n').textContent = n ? n : '';
  $('btnNext').style.display = facUnits(G.player).length ? '' : 'none';
}
function afterAction() { requestDraw(); refreshHud(); if (SHEET && SHEET.home) refreshSheet(); if (G.over) showGameOver(); }

/* ---------- STATUS 창: 늘 떠 있는 세력 현황 + 지금 할 일 ---------- */
var HOME = { open: true };
function facTotals(f) {
  var t = { gold: 0, food: 0, troops: 0, gi: 0, fi: 0, cities: 0, gates: 0, off: 0, units: 0, idle: 0 };
  facBases(f).forEach(function (b) {
    t.gold += b.gold; t.food += b.food; t.troops += b.troops; t.gi += goldIncome(b); t.fi += foodIncome(b);
    if (b.kind === 'city') t.cities++; else t.gates++;
    t.idle += idleOfficers(b).length;
  });
  facUnits(f).forEach(function (u) { t.troops += u.troops; t.units++; });
  t.off = facOfficers(f).length;
  return t;
}
function minFacCost() { var m = 1e9; for (var i = 0; i < FAC_ORDER.length; i++) m = Math.min(m, FAC[FAC_ORDER[i]].cost); return m; }
/* 쉬는 무장이 있는 거점에서 지금 해 볼 만한 일 (많아야 두 가지). tab = 첫 번째 일을 할 수 있는 탭 */
function baseAdvice(b) {
  var n = idleOfficers(b).length, tips = [];
  if (!n) return null;
  if (b.kind === 'city') {
    var empty = b.plots.filter(function (p) { return !p.fac; }).length, men = freeOfficers(b).length + b.captives.length;
    if (b.order < 60) tips.push(['치안 ' + b.order + ' → 순찰', 'home']);
    if (men) tips.push(['등용할 인재 ' + men + '명', 'men']);
    if (empty && b.gold >= minFacCost()) tips.push(['빈 부지 ' + empty + '곳 → 시설 건설', 'fac']);
    if (hasFac(b, 'barracks') && b.gold >= 300 && b.order >= 60) tips.push(['징병', 'home']);
    if (b.morale < 60 && b.troops >= 1000) tips.push(['기력 ' + b.morale + ' → 훈련', 'home']);
    if (!tips.length) tips.push(['탐색으로 인재·재물 찾기', 'men']);
  } else {
    if (b.morale < 60 && b.troops >= 1000) tips.push(['기력 ' + b.morale + ' → 훈련', 'mil']);
    if (b.troops >= 1000) tips.push(['출진 가능', 'mil']);
    if (!tips.length) return null;
  }
  return { n: n, tips: tips.slice(0, 2).map(function (t) { return t[0]; }), tab: tips[0][1] };
}
/* 지금 할 일: 급한 것부터. 항목 {cls, ic, num, t, s, go:[종류, id], lb} */
function todoList() {
  var f = G.player, F = G.factions[f], out = [], bs = facBases(f), us = facUnits(f), seen = {};
  bs.forEach(function (b) {
    var es = enemyUnitsNear(f, b.c, b.r, 4); if (!es.length) return;
    var t = 0; es.forEach(function (e) { t += e.troops; });
    es.sort(function (x, y) { return hdist(b.c, b.r, x.c, x.r) - hdist(b.c, b.r, y.c, y.r); });
    out.push({ cls: 'warn', ic: '!', t: b.n + ' 가까이에 다른 세력 부대 ' + es.length + '개', s: facName(es[0].f) + '군 ' + uName(es[0]) + (es.length > 1 ? ' 등' : '') + ' · 모두 ' + fmt(t) + '명 · ' + hdist(b.c, b.r, es[0].c, es[0].r) + '칸 거리', go: ['unit', es[0].id], lb: '보기' });
  });
  us.forEach(function (u) {
    if (u.done || !attackTargets(u).length) return;
    seen[u.id] = 1;
    out.push({ cls: 'warn', ic: '⚔', t: uName(u) + ' — 적과 맞닿았습니다', s: '부대를 고른 뒤 붉은 칸의 적을 누르면 공격·전법·계략', go: ['unit', u.id], lb: '명령' });
  });
  pendingUnits().forEach(function (u) {
    if (seen[u.id]) return; seen[u.id] = 1;
    out.push({ ic: '▶', t: uName(u) + ' — 명령을 기다립니다', s: UNIT_TYPES[u.type].name + ' ' + fmt(u.troops) + '명 · 갈 곳을 눌러 행군시키거나 대기', go: ['unit', u.id], lb: '명령' });
  });
  us.forEach(function (u) {
    var ft = unitFoodTurns(u);
    if (ft <= 3) out.push({ cls: 'warn', ic: '!', t: uName(u) + ' — 군량이 ' + days(ft) + '분뿐', s: '아군 거점에 들어가면 보급됩니다', go: ['unit', u.id], lb: '보기' });
  });
  if (F.ap >= 10) {
    var nb = 0, more = 0, lordLoc = off(F.lord).unit === null ? off(F.lord).loc : -1;
    bs.slice().sort(function (x, y) { return (y.id === lordLoc) - (x.id === lordLoc) || (y.kind === 'city') - (x.kind === 'city') || idleOfficers(y).length - idleOfficers(x).length; }).forEach(function (b) {
      var a = baseAdvice(b); if (!a) return;
      if (nb >= 5) { more++; return; }
      nb++;
      out.push({ ic: String(a.n), num: 1, t: b.n + ' — 쉬는 무장 ' + a.n + '명', s: a.tips.join(' · '), go: ['base', b.id, a.tab], lb: '열기' });
    });
    if (more) out.push({ ic: '+', t: '다른 거점 ' + more + '곳에도 쉬는 무장이 있습니다', s: '목록에서 거점을 고르세요', go: ['list', 'city'], lb: '목록' });
  } else out.push({ ic: '…', t: '행동력이 거의 없습니다 (' + F.ap + ')', s: '내정·출진 명령은 다음 턴에 다시 내릴 수 있습니다' });
  var mar = us.filter(function (u) { return u.dest >= 0; });
  if (mar.length) out.push({ cls: 'cool', ic: '▸', t: '행군 중인 부대 ' + mar.length + '개', s: mar.slice(0, 2).map(function (u) { return uName(u) + ' → ' + destName(u.dest); }).join(' · ') + (mar.length > 2 ? ' …' : '') + ' — 턴을 마치면 나아갑니다', go: ['unit', mar[0].id], lb: '보기' });
  var need = 0; out.forEach(function (t) { if (t.cls !== 'cool' && t.go) need++; });
  out.need = need;
  out.push({ cls: 'end', ic: '✓', t: need ? '할 일을 마쳤으면 턴 종료' : '할 일을 모두 마쳤습니다', s: '턴 종료를 누르면 열흘이 흐르고, 그동안 일어난 일을 차례로 보여 줍니다', go: ['end'], lb: '턴 종료' });
  return out;
}
function gotoBase(b, tab) { selectBase(b, true, tab); jumpTo(b.c, b.r, Math.max(cam.z, 0.8)); }
function gotoUnit(u) { selectUnit(u, true); jumpTo(u.c, u.r, Math.max(cam.z, 0.8)); }
function goTodo(g) {
  if (g[0] === 'unit') { var u = UMAP[g[1]]; if (u) gotoUnit(u); }
  else if (g[0] === 'base') gotoBase(G.bases[g[1]], g[2]);
  else if (g[0] === 'list') showLists(g[1]);
  else if (g[0] === 'end') doEndTurn();
}
function homeSheet() {
  var st = { todo: [] };
  return {
    home: true, cls: 'home' + (HOME.open ? '' : ' fold'),
    on: {
      fold: function () { HOME.open = !HOME.open; saveOpts(); showHome(); requestDraw(); },
      go: function (el) { var t = st.todo[+el.getAttribute('data-v')]; if (t && t.go) goTodo(t.go); },
      lord: function () { showOfficer(off(G.factions[G.player].lord)); },
      lists: function (el) { showLists(el.getAttribute('data-v')); }
    },
    render: function () {
      if (!G) return '';
      var f = G.player, F = G.factions[f], L = off(F.lord), T = facTotals(f), i;
      st.todo = todoList();
      var need = st.todo.need;
      var h = '<div class="sh-head hm-head"><button class="porb" type="button" data-a="lord" aria-label="군주 정보">' + porTag(L, HOME.open ? 'xl' : 'md') + '</button><div class="hm-id">' +
        '<div class="sh-title">' + F.name + '군 <span class="chip" style="background:' + F.color + '">군주 ' + L.n + '</span></div>' +
        '<div class="sh-sub">' + dateStr() + ' · ' + (need ? '<b class="hi">할 일 ' + need + '건</b>' : '<b class="ok">할 일 없음</b>') + '</div>' +
        (HOME.open ? '<div class="hm-ap">행동력 <span class="gauge"><u style="width:' + Math.round(F.ap / 255 * 100) + '%"></u></span><b>' + F.ap + '</b></div>' : '') + '</div>' +
        '<button class="x fold" data-a="fold" type="button" aria-label="' + (HOME.open ? 'STATUS 창 접기' : 'STATUS 창 펼치기') + '">' + (HOME.open ? '▾' : '▴') + '</button></div>';
      if (!HOME.open) return h;
      h += '<div class="sh-body"><div class="hm-stats">' +
        '<div><span>' + ico('gold') + '금</span><b>' + fmt(T.gold) + '</b><small>매월 +' + fmt(T.gi) + '</small></div>' +
        '<div><span>' + ico('food') + '병량</span><b>' + fmt(T.food) + '</b><small>분기 +' + fmt(T.fi) + '</small></div>' +
        '<div><span>' + ico('troops') + '병력</span><b>' + fmt(T.troops) + '</b><small>부대 ' + T.units + '개</small></div></div>' +
        '<div class="hm-links"><button type="button" data-a="lists" data-v="city"><span>' + ico('dur') + '거점</span><b>' + T.cities + '성' + (T.gates ? ' ' + T.gates + '관' : '') + '</b></button>' +
        '<button type="button" data-a="lists" data-v="unit"><span>' + ico('troops') + '부대</span><b>' + T.units + '개</b></button>' +
        '<button type="button" data-a="lists" data-v="off"><span>' + ico('order') + '무장</span><b>' + T.off + '명</b></button>' +
        '<button type="button" data-a="lists" data-v="fac"><span>' + ico('morale') + '천하</span><b>' + G.factions.filter(function (x) { return x.alive; }).length + '세력</b></button></div>' +
        '<div class="sec">지금 할 일</div><div class="todos">';
      for (i = 0; i < st.todo.length; i++) {
        var t = st.todo[i];
        h += '<button class="todo' + (t.cls ? ' ' + t.cls : '') + '" type="button" data-a="go" data-v="' + i + '"' + (t.go ? '' : ' disabled') + '><span class="n' + (t.num ? ' num' : '') + '">' + t.ic + '</span><span class="mid"><b>' + t.t + '</b><small>' + t.s + '</small></span>' + (t.go ? '<span class="go">' + t.lb + ' ▸</span>' : '') + '</button>';
      }
      return h + '</div></div>';
    }
  };
}
function hideSheet() { SHEET = null; var el = $('sheet'); el.className = ''; el.innerHTML = ''; }
function showHome() { if (!G || UI.play) { hideSheet(); return; } showSheet(homeSheet()); }

/* ---------- 뒤로 가기 ---------- */
/* 목록·기록·요약에서 줄을 눌러 지도로 건너뛰면 그 창을 '돌아갈 곳'(UI.ret)으로 남긴다.
   - 왼쪽 위 '‹ 목록' 단추를 누르면 그 창이 보던 자리 그대로 다시 열린다.
   - 건너뛰면서 열린 거점·부대 창(UI.via)의 ×도 그 창으로 돌아간다. */
function paintRet() {
  var el = $('ret'); if (!el) return;
  var on = !!(UI.ret && G && !G.over && !UI.play && !MODAL);
  el.className = on ? 'on' : ''; el.textContent = on ? '\u2039 ' + UI.ret.label : '';
}
function clearRet() { UI.ret = null; UI.via = false; paintRet(); }
function goRet() { var r = UI.ret; if (!r) return false; UI.ret = null; clearSel(); r.open(); return true; }
function jumpFromDialog(label, fn) {
  var keep = { d: MODAL, st: dlgScroll() };
  closeDialog();
  UI.ret = { label: label, open: function () { showDialog(keep.d); var b = $('modal').querySelector('.dlg-b'); if (b) b.scrollTop = keep.st; } };
  fn(); UI.via = !!UI.sel; paintRet();
}
/* 아래 창의 ×: 한 단계만 뒤로 */
function backSheet() {
  if (selUnit() && (UI.target || UI.march || UI.pickMarch)) {        // 대상·행군을 고르던 중이면 그것만 물린다
    UI.target = null; UI.march = null; UI.pickMarch = false; refreshSheet(); requestDraw(); return;
  }
  if (UI.sret) { var r = UI.sret; UI.sret = null; r(); return; }     // 잠깐 다른 것을 보러 갔던 경우(거점 보기·출진 직후) → 보던 곳으로
  if (UI.via && UI.ret) { goRet(); return; }                         // 목록에서 건너온 경우 → 목록으로
  clearSel();
}

/* ---------- 선택 ---------- */
function selUnit() {
  if (!G || !UI.sel || UI.sel.kind !== 'unit') return null;
  var u = UMAP[UI.sel.id];
  return (u && u.f === G.player && !u.done) ? u : null;
}
function clearSel() { UI.sel = null; UI.rc = null; UI.atk = null; UI.target = null; UI.march = null; UI.pickMarch = false; UI.via = false; UI.sret = null; closeSheet(); requestDraw(); }
function selectBase(b, noCam, tab) {
  UI.sel = { kind: 'base', id: b.id }; UI.rc = null; UI.atk = null; UI.target = null; UI.march = null; UI.via = false; UI.sret = null;
  showSheet(baseSheet(b, tab)); if (!noCam) ensureVisible(b.c, b.r); requestDraw();
}
function selectUnit(u, noCam) {
  UI.sel = { kind: 'unit', id: u.id }; UI.target = null; UI.march = null; UI.pickMarch = false; UI.via = false; UI.sret = null;
  if (u.f === G.player && !u.done) { UI.rc = unitReach(u); UI.atk = allTargets(u); } else { UI.rc = null; UI.atk = null; }
  showSheet(unitSheet(u)); if (!noCam) ensureVisible(u.c, u.r); requestDraw();
}
/* 공격·계략이 닿는 대상 전부 */
function allTargets(u) {
  var out = attackTargets(u), seen = {};
  out.forEach(function (t) { seen[K(t.c, t.r)] = 1; });
  for (var i = 0; i < 3; i++) ployTargets(u, PLOYS[i]).forEach(function (t) { var k = K(t.c, t.r); if (!seen[k]) { seen[k] = 1; out.push(t.u ? { kind: 'unit', u: t.u, c: t.c, r: t.r } : { kind: 'fac', b: plotAt(t.c, t.r).base, i: plotAt(t.c, t.r).i, c: t.c, r: t.r }); } });
  return out;
}
function onTap(c, r) {
  if (UI.play) { playNudge(); return; }
  if (UI.busy || !G || G.over || MODAL) return;
  var k = K(c, r), u = UAT[k] || null, b = baseAt(c, r), pl = plotAt(c, r), su = selUnit();
  if (su) {
    if (u === su) return;
    var t = null;
    if (u && u.f !== G.player) t = { kind: 'unit', u: u, c: c, r: r };
    else if (b && b.owner >= 0 && b.owner !== G.player) t = { kind: 'base', b: b, c: c, r: r };
    else if (pl && pl.plot.fac && pl.base.owner >= 0 && pl.base.owner !== G.player) t = { kind: 'fac', b: pl.base, i: pl.i, c: c, r: r };
    if (t) {
      var acts = targetActions(su, t), any = acts.some(function (a) { return a.ok; });
      if (!any) {
        if (t.kind === 'base' && zoneFresh(su, t.b) && hdist(su.c, su.r, c, r) <= uRange(su)) toast('성역에 막 들어선 부대는 이번 턴에 성을 칠 수 없습니다 — 다음 턴에 공격하세요', 2800);
        else if (!(UI.pickMarch && t.kind === 'base' && proposeMarch(su, c, r))) toast('닿지 않습니다 — 먼저 가까이 이동하세요');
        return;
      }
      UI.target = t; UI.march = null; refreshSheet(); requestDraw(); return;
    }
    if (UI.pickMarch && !u && MC[clsIdx(su)][k] < 99 && !(pl && pl.plot.fac)) { proposeMarch(su, c, r); return; }   // [행군]을 누른 뒤: 목적지 고르기
    if (UI.rc && UI.rc.stop[k]) { UI.march = null; doMove(su, c, r); return; }
    if (!u && !b && !(pl && pl.base.owner === G.player) && MC[clsIdx(su)][k] < 99) { toast('닿지 않습니다 — 이번 턴에는 파란 칸까지만 갈 수 있습니다', 2200); return; }
  }
  UI.target = null;
  if (u) { selectUnit(u); return; }
  if (b) { selectBase(b); return; }
  if (pl && pl.base.owner === G.player) {                              // 내 부지: 고른 것은 그대로 두고 창만 띄운다 — 창을 닫으면 보던 곳 그대로다
    if (su) { refreshSheet(); requestDraw(); }
    if (pl.plot.fac) flowFacility(pl.base, pl.i); else flowDevelop(pl.base, pl.i);
    return;
  }
  if (su || UI.sel) { clearSel(); return; }
  var tt = terr(c, r);
  toast(TERRAIN_NAME[tt] + (isRoad(c, r) && tt !== 'w' ? ' (길)' : (isRoad(c, r) ? ' (나루)' : '')) + ' — ' + TERRAIN_DESC[tt], 1800);
}

/* ---------- 행군(여러 턴 걸리는 이동) ---------- */
function proposeMarch(u, c, r) {
  var k = K(c, r), path = marchPath(u, k);
  if (!path) { toast('그곳으로 가는 길이 없습니다'); return false; }
  var b = baseAt(c, r);
  UI.march = { k: k, path: path, turns: marchTurns(u, path), name: b ? b.n : TERRAIN_NAME[terr(c, r)], base: b ? b.id : -1 };
  UI.target = null; UI.pickMarch = false; refreshSheet(); requestDraw();
  return true;
}
function destName(k) { var c = k % W, r = (k - c) / W, b = baseAt(c, r); return b ? b.n : TERRAIN_NAME[terr(c, r)]; }
function marchStep(u, animate, cb) {
  if (animate && R3 && R3.ready && !R3.units[u.id]) syncScene();          // 막 출진한 부대는 먼저 지도에 세운다
  var vis = unitVis(u), name = uName(u), res = unitMarch(u);
  if (!res || !res.ok) { if (cb) cb(res); return; }
  function fin() { marchLog(u, name, res); if (cb) cb(res); }
  if (animate) { UI.hide = alive(u) ? u.id : -1; UI.rc = null; UI.atk = null; animMove(vis, res.from, res.path, fin); } else fin();
}

/* ---------- 부대 조작 ---------- */
function doMove(u, c, r) {
  var vis = unitVis(u), rc = UI.rc;
  var res = unitMove(u, c, r, rc);
  if (!res.ok) { toast(res.msg); return; }
  UI.hide = alive(u) ? u.id : -1; UI.rc = null; UI.atk = null; UI.target = null;
  animMove(vis, res.from, res.path, function () {
    if (res.entered !== undefined) { toast(G.bases[res.entered].n + ' 입성'); selectBase(G.bases[res.entered]); }
    else if (res.captured !== undefined) { sfx('fall'); sfx('cheerlate'); fxFall(G.bases[res.captured], '점령'); toast(G.bases[res.captured].n + ' 점령!'); selectBase(G.bases[res.captured]); }
    else if (res.dead) { toast('불길 속에서 부대가 흩어졌습니다'); clearSel(); }
    else {
      if (res.burn) { floatText(c, r, '-' + fmt(res.burn), '#b5332a'); sfx('fire'); }
      UI.rc = unitReach(u); UI.atk = allTargets(u); refreshSheet();
      if (zoneAt(res.from[0], res.from[1]) !== zoneAt(c, r)) zoneToast(res.from, c, r);
    }
    afterAction();
  });
}
/* 성역의 경계를 넘었을 때의 안내 */
function zoneToast(from, c, r) {
  var z1 = zoneAt(c, r), z0 = zoneAt(from[0], from[1]);
  var foe = z1 >= 0 && G.bases[z1].owner >= 0 && G.bases[z1].owner !== G.player;
  toast(z1 >= 0 ? G.bases[z1].n + '의 성역에 들어섰습니다 — 이번 턴 이동은 여기까지' + (foe ? ', 성 공격은 다음 턴부터입니다' : '입니다') : G.bases[z0].n + '의 성역을 벗어났습니다 — 이번 턴 이동은 여기까지입니다', 2800);
}
function estBase(u, b) {
  var T = UNIT_TYPES[u.type];
  return { t: Math.min(b.troops, Math.round(620 * Math.pow(uAtk(u) / baseDefVal(b), 0.9) * troopFactor(u.troops) * T.vsBase)), d: durDmgUB(u) };
}
function targetActions(u, t) {
  var out = [], d = hdist(u.c, u.r, t.c, t.r), rg = uRange(u), i;
  if (t.kind === 'unit') {
    out.push({ kind: 'attack', label: '공격', sub: d <= rg ? '예상 -' + fmt(estUU(u, t.u, 1, d > 1)) : '사거리 밖', ok: d <= rg, pri: true });
    var all = TACTICS[u.type] || [], can = tacticList(u);
    for (i = 0; i < all.length; i++) {
      var tac = all[i], have = can.indexOf(tac) >= 0, inT = have && tacticTargets(u, tac).some(function (x) { return x.u === t.u; });
      var od = tacticOdds(u, t.u);
      var sub = !have ? '적성 ' + tac.need + ' 필요' : (u.morale < tac.cost ? '기력 부족' : (!inT ? (d > rg ? '사거리 밖' : '숲에서는 불가') : '기력 ' + tac.cost + ' · ' + (od.sure ? '필중' : od.ok + '%') + '<br>대성공 ' + (od.sure ? '확정' : od.crit + '%')));
      out.push({ kind: 'tactic', tac: tac, label: tac.name, sub: sub, ok: inT });
    }
    for (i = 0; i < 3; i++) {
      var pl = PLOYS[i], inP = ployTargets(u, pl).some(function (x) { return x.u === t.u; });
      out.push({ kind: 'ploy', ploy: pl, label: pl.name, sub: inP ? '기력 ' + pl.cost + ' · ' + ployChance(u, pl, t.u) + '%' : (u.morale < pl.cost ? '기력 부족' : (t.u.status && i > 0 ? '이미 걸림' : '사거리 밖')), ok: inP });
    }
  } else if (t.kind === 'base') {
    var e = estBase(u, t.b), fresh = zoneFresh(u, t.b);
    out.push({ kind: 'attack', label: '공격', sub: fresh ? '성역에 막 들어섬 — 다음 턴부터' : (d <= rg ? '병력 -' + fmt(e.t) + ' · 내구 -' + fmt(e.d) : '사거리 밖'), ok: d <= rg && !fresh, pri: true });
  } else {
    out.push({ kind: 'attack', label: '시설 파괴', sub: d <= 1 ? '공격' : '옆 칸에서만', ok: d <= 1, pri: true });
    var inF = ployTargets(u, PLOYS[0]).some(function (x) { return x.c === t.c && x.r === t.r; });
    out.push({ kind: 'ploy', ploy: PLOYS[0], label: '화계', sub: inF ? '기력 10' : '불가', ok: inF });
  }
  return out;
}
/* 전법 풀이: 고른 상대에 대한 성공·대성공 확률과, 결과에 따라 달라지는 효과 */
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
function resultMsg(name, res) {
  var msg = name + ' ';
  if (res.kind === 'ploy') {
    if (res.success) msg += res.ploy + ' 성공' + (res.dmg ? ' (-' + fmt(res.dmg) + ')' : '') + (res.chain ? ' · 연환!' : '');
    else msg += res.ploy + ' 실패 (성공률 ' + res.p + '%)' + (res.reflected ? ' — 반계에 당했습니다!' : '');
  } else {
    if (res.kind === 'tactic') msg += res.tac + (res.fail ? ' 실패' : (res.crit ? ' 대성공' : ' 성공')); else msg += '공격';
    msg += ' → ' + res.tname + ' -' + fmt(res.dmg);
    if (res.fail && res.pOk !== undefined) msg += ' (성공률 ' + res.pOk + '%)';
    if (res.dur) msg += ' · 내구 -' + fmt(res.dur);
    if (res.dmg2) msg += ' · 연전 -' + fmt(res.dmg2);
    if (res.pushed >= 2) msg += ' · 두 칸 밀어냄';
    if (res.slam) msg += ' · 뒤가 막혀 추가 피해';
    if (res.mor) msg += ' · 기력 -' + res.mor;
    if (res.confused) msg += ' · 혼란';
  }
  if (res.counter) msg += ' (반격 -' + fmt(res.counter) + ')';
  if (res.duel) msg += ' · 일기토! ' + res.duel.a + ' 대 ' + res.duel.d + ' — ' + (res.duel.win ? res.duel.a : res.duel.d) + ' 승';
  if (res.killed) msg += ' · 궤멸!';
  if (res.destroyed) msg += ' · 파괴!';
  if (res.selfDead) msg += ' · 아군 부대 궤멸…';
  if (res.fell) msg = res.tname + ' 함락!';
  return msg;
}
/* 타격 순간에 띄우는 숫자·글씨와 소리. 피해는 인주색, 전법 이름은 먹, 계략은 쪽빛 */
function resultFx(res) {
  var C_DMG = '#b5332a', C_INK = '#1b1a18', C_PLOY = '#2f4f6f', C_DIM = '#6a645a', C_CNT = '#8a5a12';
  var tc = res.tc1 !== undefined ? res.tc1 : (res.tc !== undefined ? res.tc : res.c), tr = res.tr1 !== undefined ? res.tr1 : (res.tr !== undefined ? res.tr : res.r);
  var ac = res.ac1 !== undefined ? res.ac1 : res.ac, ar = res.ar1 !== undefined ? res.ar1 : res.ar;
  if (res.kind === 'ploy') {
    if (res.success) {
      floatText(res.c, res.r, res.ploy + '!', res.ploy === '화계' ? '#c8551f' : C_PLOY, 0, true, -34);
      if (res.dmg) floatText(res.c, res.r, '-' + fmt(res.dmg), C_DMG, 260);
      sfx(res.ploy === '화계' ? 'fire' : (res.ploy === '소화' ? 'douse' : 'wind'));
    } else {
      floatText(res.c, res.r, '실패', C_DIM); sfx('miss');
      if (res.reflected) floatText(res.ac, res.ar, '반계!', C_PLOY, 300, true);
    }
  } else {
    // 글씨가 한자리에 겹치지 않게: 전법 이름은 위, 피해는 가운데, 덧붙는 것은 아래로 차례차례
    if (res.kind === 'tactic') floatText(res.c, res.r, res.fail ? res.tac + ' 실패' : res.tac + (res.crit ? ' 대성공!' : '!'), res.fail ? C_DIM : (res.crit ? C_DMG : C_INK), 0, true, -34);
    else if (res.crit) floatText(res.c, res.r, '크리티컬!', C_INK, 0, true, -34);
    floatText(tc, tr, '-' + fmt(res.dmg), C_DMG, res.kind === 'tactic' || res.crit ? 200 : 0, res.crit || (res.kind === 'tactic' && !res.fail));
    if (res.dur) floatText(tc, tr, '내구 -' + fmt(res.dur), C_CNT, 380, false, 26);
    if (res.dmg2) floatText(tc, tr, '연전 -' + fmt(res.dmg2), C_DMG, 620, false, 26);
    if (res.extra) res.extra.forEach(function (x, i) { floatText(x.c, x.r, '-' + fmt(x.dmg), C_DMG, 300 + i * 80); if (x.mor) floatText(x.c, x.r, '기력 -' + x.mor, C_PLOY, 560 + i * 80, false, 26); });
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
  }
  if (res.counter) floatText(ac, ar, '-' + fmt(res.counter), C_CNT, 520);
  if (res.duel) floatText(res.duel.win ? tc : ac, res.duel.win ? tr : ar, '일기토 패 -' + fmt(res.duel.loss), C_INK, 1150, true, -8);   // 소리는 연출(fx.js) 쪽에서 엇갈리는 순간에
  if (res.selfDmg) floatText(res.ac, res.ar, '-' + fmt(res.selfDmg), C_CNT, 500);
  if (res.fell) { sfx('fall'); if (res.af === G.player) sfx('cheerlate'); }
}
function presentResult(name, res, quiet) { var msg = resultMsg(name, res); resultFx(res); if (!quiet) toast(msg, 3200); return msg; }
function doAct(a) {
  var u = selUnit(), t = UI.target;
  if (!u || !t || UI.busy) return;
  var name = uName(u), res;
  if (a.kind === 'attack') res = unitAttack(u, t);
  else if (a.kind === 'tactic') res = unitTactic(u, a.tac, t);
  else res = unitPloy(u, a.ploy, t);
  if (!res.ok) { toast(res.msg); return; }
  UI.battleTurn = G.turn; playBgm('battle');
  var msg = resultMsg(name, res), fellB = res.fell && t.kind === 'base' ? t.b : null;
  UI.busy = true; UI.rc = null; UI.atk = null; UI.target = null;
  requestDraw();
  actZoom(res.ac0, res.ar0, t.c, t.r, function (back) {      // 싸우는 곳을 가까이 당겨서 보여 준다
    animAct(res, function () {
      UI.busy = false;
      if (fellB) fxFall(fellB, fellB.kind === 'gate' ? '점령' : '함락');
      toast(msg, 3200);
      clearSel();
      if (fellB && fellB.owner === G.player) selectBase(fellB);
      back();
      afterAction();
    }, function () { resultFx(res); });
  });
}
/* 두 칸 사이를 화면 가운데로 당긴다. 이미 충분히 가까우면 그대로. cb(back) — back() 을 부르면 원래 시점으로 돌아간다 */
function actZoom(c1, r1, c2, r2, cb) {
  var c0 = { x: cam.x, y: cam.y, z: cam.z }, near = cam.z >= 1.45 && onScreen(c1, r1, 30) && onScreen(c2, r2, 30);
  function back() { if (near) return; var x0 = cam.x, y0 = cam.y, z0 = cam.z; anim(360, function (t) { var e = t * (2 - t); cam.x = x0 + (c0.x - x0) * e; cam.y = y0 + (c0.y - y0) * e; cam.z = z0 + (c0.z - z0) * e; clampCam(); }); }
  if (near) { cb(back); return; }
  var a = hexCenter(c1, r1), b = hexCenter(c2, r2), z1 = Math.max(cam.z, 1.75), x0 = cam.x, y0 = cam.y, z0 = cam.z;
  var D = 62 / z1, pt = (68 - 27 * clamp(Math.log(z1 / Z_MIN) / Math.log(Z_MAX / Z_MIN), 0, 1)) * Math.PI / 180;
  var tx = (a[0] + b[0]) / 2, ty = (a[1] + b[1]) / 2 + (0.5 - safeArea().fy) * D * K3 / Math.sin(pt);
  anim(300, function (t) { var e = t * (2 - t); cam.x = x0 + (tx - x0) * e; cam.y = y0 + (ty - y0) * e; cam.z = z0 + (z1 - z0) * e; clampCam(); }, function () { cb(back); });
}
/* 행군 중인 부대의 남은 길(어림) */
function marchLeft(x) {
  var p = marchPath(x, x.dest); if (!p) return '';
  return ' (약 ' + days(marchTurns(x, p)) + ' 남음)';
}
function unitSheet(u) {
  var st = { acts: [] };
  return {
    cls: 'unit',
    on: {
      wait: function () { var x = UMAP[u.id]; if (x) unitWait(x); clearSel(); afterAction(); },
      undo: function () { var x = UMAP[u.id]; if (x && unitUndoMove(x)) { UI.rc = unitReach(x); UI.atk = allTargets(x); UI.target = null; refreshSheet(); requestDraw(); } },
      march: function () {
        var x = selUnit(), m = UI.march; if (!x || !m) return;
        x.dest = m.k; UI.march = null; sfx('drum');
        marchStep(x, true, function (res) {
          if (res && res.ok && res.entered !== undefined) { toast(G.bases[res.entered].n + ' 입성'); selectBase(G.bases[res.entered]); }
          else if (res && res.ok && res.captured !== undefined) { sfx('fall'); sfx('cheerlate'); fxFall(G.bases[res.captured], '점령'); toast(G.bases[res.captured].n + ' 점령!'); selectBase(G.bases[res.captured]); }
          else if (alive(x)) {
            if (res && res.front !== undefined) toast(G.bases[res.front].n + ' 바로 앞입니다 — 성을 눌러 공격하세요', 3200);
            else if (res && res.lost) toast('그곳으로 가는 길이 없습니다');
            else toast(x.dest >= 0 ? '행군 시작 — 남은 길은 턴을 마칠 때마다 이어서 갑니다' : '도착했습니다', 3200);
            UI.rc = unitReach(x); UI.atk = allTargets(x); refreshSheet();
          } else clearSel();
          afterAction();
        });
      },
      unmarch: function () { UI.march = null; UI.pickMarch = false; var x = UMAP[u.id]; if (x) x.dest = -1; refreshSheet(); requestDraw(); },
      pickmarch: function () { UI.pickMarch = !UI.pickMarch; UI.march = null; UI.target = null; refreshSheet(); requestDraw(); },
      viewbase: function () {
        var m = UI.march, x = selUnit(); if (!m || m.base < 0 || !x) return;
        var uid = x.id; selectBase(G.bases[m.base]);
        UI.sret = function () { var u2 = UMAP[uid]; if (u2 && u2.f === G.player && !u2.done) { selectUnit(u2); UI.march = m; refreshSheet(); requestDraw(); } else clearSel(); };
      },
      douse: function () { var x = selUnit(); if (!x || UI.busy) return; var res = unitPloy(x, PLOYS[3], { c: x.c, r: x.r }); if (!res.ok) { toast(res.msg); return; } UI.busy = true; animAct(res, function () { UI.busy = false; toast('주위의 불을 껐습니다'); clearSel(); afterAction(); }, function () { sfx('douse'); }); requestDraw(); },
      act: function (el) { var a = st.acts[+el.getAttribute('data-v')]; if (a && a.ok) doAct(a); else if (a) toast(a.sub); },
      untarget: function () { UI.target = null; refreshSheet(); requestDraw(); },
      tacinfo: function () { var x = selUnit(), t = UI.target; if (x && t && t.kind === 'unit' && alive(t.u)) showTacticInfo(x, t.u); },
      off: function (el) { showOfficer(off(+el.getAttribute('data-v'))); }
    },
    render: function () {
      var x = UMAP[u.id];
      if (!x) return '';
      var T = UNIT_TYPES[x.type], mine = x.f === G.player, ms = uMembers(x), i;
      var turns = unitFoodTurns(x);
      var h = '<div class="sh-head">' + porTag(ms[0], 'hd') + '<div><div class="sh-title">' + uName(x) + ' ' + facChip(x.f) + '</div><div class="sh-sub">' + T.name + (APT_IDX[x.type] !== undefined ? ' 적성 ' + uApt(x) : '') +
        ' · 병력 <b>' + fmt(x.troops) + '</b> · 기력 <b>' + x.morale + '</b> · 군량 ' + fmt(x.food) + ' (<b' + (turns <= 3 ? ' class="bad"' : '') + '>' + days(turns) + '분</b>)' + (x.status ? ' · <b class="bad">' + (x.status === 'confuse' ? '혼란' : '위보') + '</b>' : '') + '</div></div>' +
        '<button class="x" data-a="close" type="button" aria-label="닫기">×</button></div><div class="sh-body">';
      var su = selUnit();
      if (su === x) {
        if (UI.march) {
          h += '<div class="tgt">행군 — <b>' + UI.march.name + '</b>까지 약 <b>' + days(UI.march.turns) + '</b>' + (UI.march.turns > turns ? ' · <b class="bad">군량이 모자랍니다</b>' : '') + '</div><div class="acts">' +
            '<button class="act pri" type="button" data-a="march"><b>행군 시작</b><small>지금 한 구간 · 나머지는 턴 종료 때</small></button>' +
            (UI.march.base >= 0 ? '<button class="act" type="button" data-a="viewbase"><b>거점 보기</b><small>' + UI.march.name + '</small></button>' : '') +
            '<button class="act" type="button" data-a="unmarch"><b>취소</b><small>&nbsp;</small></button></div>';
        } else if (UI.target) {
          var t = UI.target;
          var tn = t.kind === 'unit' ? uName(t.u) + ' · ' + UNIT_TYPES[t.u.type].name + ' ' + fmt(t.u.troops) + '명 · 기력 ' + t.u.morale : (t.kind === 'base' ? t.b.n + ' · 병력 ' + fmt(t.b.troops) + ' · 내구 ' + fmt(t.b.dur) : t.b.n + '의 ' + FAC[t.b.plots[t.i].fac.t].name);
          st.acts = targetActions(x, t);
          h += '<div class="tgt">대상 — <b>' + tn + '</b></div><div class="acts">';
          for (i = 0; i < st.acts.length; i++) { var a = st.acts[i]; h += '<button class="act' + (a.pri && a.ok ? ' pri' : '') + (a.ok ? '' : ' off') + '" type="button" data-a="act" data-v="' + i + '"><b>' + a.label + '</b><small>' + a.sub + '</small></button>'; }
          if (t.kind === 'unit' && (TACTICS[x.type] || []).length) h += '<button class="act" type="button" data-a="tacinfo"><b>전법 풀이</b><small>효과·확률</small></button>';
          h += '<button class="act" type="button" data-a="untarget"><b>대상 취소</b><small>&nbsp;</small></button></div>';
        } else {
          var canDouse = ployTargets(x, PLOYS[3]).length > 0;
          h += '<div class="acts"><button class="act" type="button" data-a="wait"><b>대기</b><small>이번 턴 마침</small></button>' +
            '<button class="act' + (x.ox >= 0 ? '' : ' off') + '" type="button" data-a="undo"><b>이동 취소</b><small>' + (x.ox >= 0 ? '되돌리기' : '&nbsp;') + '</small></button>' +
            (canDouse ? '<button class="act" type="button" data-a="douse"><b>소화</b><small>기력 10</small></button>' : '') +
            (x.dest >= 0 ? '<button class="act" type="button" data-a="unmarch"><b>행군 취소</b><small>' + destName(x.dest) + ' 방면</small></button>' : '<button class="act' + (UI.pickMarch ? ' pri' : '') + '" type="button" data-a="pickmarch"><b>행군</b><small>' + (UI.pickMarch ? '목적지를 누르세요' : '먼 곳까지 알아서') + '</small></button>') + '</div>' +
            (x.zin >= 0 && G.bases[x.zin].owner >= 0 && G.bases[x.zin].owner !== x.f ? '<p class="note"><b class="hi">' + G.bases[x.zin].n + '의 성역에 막 들어섰습니다.</b> 성 공격은 다음 턴부터 할 수 있습니다.</p>' : '') +
            (x.dest >= 0 ? '<p class="note"><b class="hi">' + destName(x.dest) + ' 방면 행군 중</b>' + marchLeft(x) + ' — 턴을 마치면 다음 구간을 갑니다. 그 전에 직접 움직이거나 공격해도 됩니다.</p>' : (UI.pickMarch ? '<p class="note"><b class="hi">행군 목적지를 지도에서 누르세요.</b> 거점이나 길 위의 칸을 고르면 걸리는 날수를 보여 줍니다. 그만두려면 행군을 한 번 더 누르세요.</p>' : '<p class="note"><b>파란 칸</b>을 누르면 이동하고, <b>적</b>을 누르면 공격·전법·계략을 고릅니다. 옅은 파란 칸은 성역의 경계 — 넘으면 이번 턴 이동이 끝납니다.</p>'));
        }
      } else if (mine && x.done) h += '<p class="note">이번 턴 행동을 마쳤습니다.' + (x.dest >= 0 ? ' ' + destName(x.dest) + ' 방면 행군은 다음 턴에 이어집니다.' : '') + '</p>';
      h += '<div class="rows">';
      for (i = 0; i < ms.length; i++) h += offRow(ms[i], { badge: i === 0 ? '주장' : '부장' });
      h += '</div></div>';
      return h;
    }
  };
}

/* ---------- 거점 패널 ---------- */
function baseSheet(b0, tab0) {
  var st = { tab: b0.kind === 'gate' ? (tab0 === 'men' ? 'men' : 'mil') : (tab0 || 'home') };
  function B() { return G.bases[b0.id]; }
  var on = {
    tab: function (el) { st.tab = el.getAttribute('data-v'); refreshSheet(); },
    off: function (el) { showOfficer(off(+el.getAttribute('data-v'))); },
    draft: function () { flowDraft(B()); }, patrol: function () { flowPatrol(B()); }, train: function () { flowTrain(B()); },
    produce: function () { flowProduce(B()); }, trade: function () { flowTrade(B()); }, deploy: function () { flowDeploy(B()); },
    trans: function () { flowTransport(B()); }, search: function () { flowSearch(B()); }, recruit: function () { flowRecruit(B()); },
    reward: function () { flowReward(B()); }, move: function () { flowMove(B()); }, captive: function () { flowCaptive(B()); },
    plot: function (el) { var i = +el.getAttribute('data-v'), b = B(); if (b.plots[i].fac) flowFacility(b, i); else flowDevelop(b, i); }
  };
  function cmd(a, name, sub, pri, offc) { return '<button class="cmd' + (pri ? ' pri' : '') + (offc ? ' off' : '') + '" type="button" data-a="' + a + '"><b>' + name + '</b><small>' + sub + '</small></button>'; }
  return {
    on: on,
    render: function () {
      var b = B(), mine = b.owner === G.player, city = b.kind === 'city', i;
      var gov = null; baseOfficers(b).forEach(function (o) { if (!gov || (isLord(o) ? 1000 : 0) + o.ldr + o.pol > (isLord(gov) ? 1000 : 0) + gov.ldr + gov.pol) gov = o; });
      var h = '<div class="sh-head">' + (gov ? porTag(gov, 'hd') : thumb(city ? 'city_' + b.sz : 'gate')) + '<div><div class="sh-title">' + b.n + ' ' + facChip(b.owner) + '</div><div class="sh-sub">' + SIZE_NAME[b.sz] + (gov ? ' · ' + (isLord(gov) ? '군주 ' : '태수 ') + gov.n : '') + (mine ? ' · 대기 무장 ' + idleOfficers(b).length + '명' : '') + '</div></div><button class="x" data-a="close" type="button" aria-label="닫기">×</button></div><div class="sh-body">';
      h += '<div class="stats">' +
        '<div class="w"><span>' + ico('gold') + '금</span><b>' + fmt(b.gold) + (city && b.owner >= 0 ? ' <small>+' + fmt(goldIncome(b)) + '</small>' : '') + '</b></div><div class="w"><span>' + ico('food') + '병량</span><b>' + fmt(b.food) + (city && b.owner >= 0 ? ' <small>+' + fmt(foodIncome(b)) + '</small>' : '') + '</b></div>' +
        '<div><span>' + ico('troops') + '병력</span><b>' + fmt(b.troops) + '</b></div><div><span>' + ico('morale') + '기력</span><b>' + b.morale + '</b></div>' + (city ? '<div><span>' + ico('order') + '치안</span><b' + (b.order < 50 ? ' class="bad"' : '') + '>' + b.order + '</b></div>' : '') +
        '<div><span>' + ico('dur') + '내구</span><b>' + fmt(b.dur) + '</b></div></div>';
      h += '<div class="wp"><span>' + ico('spear') + '창 <b>' + fmt(b.w.spear) + '</b></span><span>' + ico('halberd') + '극 <b>' + fmt(b.w.halberd) + '</b></span><span>' + ico('bow') + '노 <b>' + fmt(b.w.bow) + '</b></span><span>' + ico('horse') + '군마 <b>' + fmt(b.w.horse) + '</b></span><span>' + ico('ram') + '충차 <b>' + b.w.ram + '</b></span></div>';
      if (!mine) {
        var os = baseOfficers(b);
        h += '<div class="sec">' + (b.owner >= 0 ? '주둔 무장 ' + os.length + '명' : '주인 없는 거점 — 부대를 들여보내면 점령합니다') + '</div><div class="rows">';
        os.sort(function (x, y) { return (isLord(y) ? 1000 : 0) + aiMilScore(y) - (isLord(x) ? 1000 : 0) - aiMilScore(x); });
        for (i = 0; i < os.length; i++) h += offRow(os[i], { badge: isLord(os[i]) ? '군주' : '' });
        var fr0 = freeOfficers(b); for (i = 0; i < fr0.length; i++) h += offRow(fr0[i], { badge: '재야' });
        return h + '</div></div>';
      }
      var tabs = city ? [['home', '내정'], ['mil', '군사'], ['men', '인재'], ['fac', '시설']] : [['mil', '군사'], ['men', '인재']];
      h += '<div class="tabs">'; for (i = 0; i < tabs.length; i++) h += '<button type="button" data-a="tab" data-v="' + tabs[i][0] + '"' + (st.tab === tabs[i][0] ? ' class="on"' : '') + '>' + tabs[i][1] + '</button>'; h += '</div>';
      if (st.tab === 'home') {
        h += '<div class="cmds">' + cmd('draft', '징병', '금 300 · 행 ' + AP.draft, false, !hasFac(b, 'barracks')) + cmd('patrol', '순찰', '금 100 · 행 ' + AP.patrol) + cmd('train', '훈련', '행 ' + AP.train) +
          cmd('produce', '생산', '금 300~ · 행 ' + AP.produce, false, !hasFac(b, 'smithy') && !hasFac(b, 'stable') && !hasFac(b, 'workshop')) + cmd('trade', '거래', '행 ' + AP.trade, false, !hasFac(b, 'market')) + '</div>' +
          '<p class="note">금은 매월 초, 병량은 1·4·7·10월 초에 들어옵니다. 치안이 낮으면 수입과 징병량이 줄어듭니다.</p>';
      } else if (st.tab === 'mil') {
        h += '<div class="cmds">' + cmd('deploy', '출진', '행 ' + AP.deploy, true) + cmd('trans', '수송', '행 ' + AP.deploy) + (city ? '' : cmd('train', '훈련', '행 ' + AP.train)) + '</div>';
        var mu = facUnits(G.player).filter(function (u) { return u.home === b.id; });
        if (mu.length) h += '<p class="note">이 거점에서 나간 부대 ' + mu.length + '개</p>';
      } else if (st.tab === 'men') {
        var fr = freeOfficers(b), cp = b.captives.length;
        h += '<div class="cmds">' + (city ? cmd('search', '탐색', '행 ' + AP.search) : '') + cmd('recruit', '등용', (fr.length || cp) ? '재야 ' + fr.length + ' · 포로 ' + cp : '대상 없음', fr.length + cp > 0, !(fr.length + cp)) + cmd('reward', '포상', '금 100 · 행 ' + AP.reward) +
          cmd('move', '이동', '행 ' + AP.move) + (cp ? cmd('captive', '포로', cp + '명') : '') + '</div><div class="sec">무장</div><div class="rows">';
        var all = G.officers.filter(function (o) { return o.f === b.owner && ((o.st === 'active' && o.loc === b.id && o.unit === null) || (o.st === 'travel' && o.dest === b.id)); });
        all.sort(function (x, y) { return (isLord(y) ? 1000 : 0) + (y.ldr + y.war + y.int + y.pol) / 4 - (isLord(x) ? 1000 : 0) - (x.ldr + x.war + x.int + x.pol) / 4; });
        for (i = 0; i < all.length; i++) h += offRow(all[i], { badge: isLord(all[i]) ? '군주' : '', dim: all[i].acted || all[i].st === 'travel', rt: '<span class="' + (all[i].loy < 70 ? 'bad' : '') + '">충 ' + all[i].loy + '</span><br>' + offStatus(all[i]) });
        if (fr.length) { h += '</div><div class="sec">재야</div><div class="rows">'; for (i = 0; i < fr.length; i++) h += offRow(fr[i], {}); }
        h += '</div>';
      } else {
        h += '<div class="rows">';
        for (var pass = 0; pass < 2; pass++) for (i = 0; i < b.plots.length; i++) {
          var fc = b.plots[i].fac;
          if ((pass === 0) !== !fc) continue;
          if (!fc) h += '<button class="row" type="button" data-a="plot" data-v="' + i + '"><span class="th" style="display:flex;align-items:center;justify-content:center;font-size:22px;color:var(--seal)">＋</span><span class="mid"><span class="nm">빈 부지</span><span class="ds">누르면 시설을 짓습니다</span></span></button>';
          else h += '<button class="row" type="button" data-a="plot" data-v="' + i + '">' + thumb(fc.t) + '<span class="mid"><span class="nm">' + FAC[fc.t].name + ' Lv' + fc.lv + '</span><span class="ds">' + (fc.done ? FAC[fc.t].desc : '건설 중 — ' + days(Math.max(1, Math.ceil((fc.need - fc.prog) / fc.rate))) + ' 남음') + '</span></span>' + (mergeCandidates(b, i).length ? '<span class="rt hi">합병 가능</span>' : '') + '</button>';
        }
        h += '</div>';
      }
      return h + '</div>';
    }
  };
}
function done(res, msg, snd) {
  if (!res.ok) { toast(res.msg); return false; }
  if (snd) sfx(snd);
  if (msg) toast(msg);
  refreshSheet(); afterAction();
  return true;
}

/* ---------- 내정 흐름 ---------- */
function flowDraft(b) {
  if (!hasFac(b, 'barracks')) return toast('병영이 필요합니다 — 시설 탭에서 지으세요');
  pickOfficers({ title: '징병 — 담당 무장', list: idleOfficers(b), max: 3, hi: 'cha', key: function (o) { return o.cha + (o.sk === '명성' ? 40 : 0); }, auto: function (n) { return autoPick('draft', b, null, n); },
    preview: function (os) { return '예상 <b>+' + fmt(draftAmount(b, os)) + '명</b> · 치안 -' + (anyHas(os, '인덕') ? 5 : 10) + ' · 금 300'; } },
    function (os) { var r = cmdDraft(b, ids(os)); return done(r, r.ok ? '징병 +' + fmt(r.n) + '명' : '', 'drums'); });
}
function flowPatrol(b) {
  pickOfficers({ title: '순찰 — 담당 무장', list: idleOfficers(b), max: 3, hi: 'war', key: function (o) { return Math.max(o.war, o.ldr) + (o.sk === '위압' ? 40 : 0); }, auto: function (n) { return autoPick('patrol', b, null, n); },
    preview: function (os) { var v = Math.round(5 + Math.max(bestOf(os, 'war'), bestOf(os, 'ldr')) / 9 + (os.length - 1) * 2); if (anyHas(os, '위압')) v *= 2; return '치안 <b>+' + Math.min(v, 100 - b.order) + '</b> · 금 100'; } },
    function (os) { var r = cmdPatrol(b, ids(os)); return done(r, r.ok ? '치안 +' + r.n : '', 'step'); });
}
function flowTrain(b) {
  pickOfficers({ title: '훈련 — 담당 무장', list: idleOfficers(b), max: 3, hi: 'ldr', key: function (o) { return o.ldr; }, auto: function (n) { return autoPick('train', b, null, n); },
    preview: function (os) { return '기력 <b>+' + Math.min(Math.round(8 + bestOf(os, 'ldr') / 8 + (os.length - 1) * 2), 100 - b.morale) + '</b>'; } },
    function (os) { var r = cmdTrain(b, ids(os)); return done(r, r.ok ? '기력 +' + r.n : '', 'shout'); });
}
function flowProduce(b) {
  var kinds = [['spear', '창', 'smithy'], ['halberd', '극', 'smithy'], ['bow', '노', 'smithy'], ['horse', '군마', 'stable'], ['ram', '충차', 'workshop']];
  showDialog({
    render: function () {
      var h = dlgHead('생산 — 무엇을 만들까요') + '<div class="dlg-b"><div class="opts">';
      for (var i = 0; i < kinds.length; i++) { var ok = !!hasFac(b, kinds[i][2]); h += '<button class="opt' + (ok ? '' : ' off') + '" type="button" data-a="k" data-v="' + i + '"><b>' + ico(kinds[i][0]) + kinds[i][1] + '</b><small>' + (ok ? '재고 ' + fmt(b.w[kinds[i][0]]) : FAC[kinds[i][2]].name + ' 필요') + '</small></button>'; }
      return h + '</div><p class="note">창·극·노·군마는 금 300, 충차는 금 600. 지력이 높은 무장일수록 많이 만듭니다.</p></div>';
    },
    on: { k: function (el) {
      var k = kinds[+el.getAttribute('data-v')];
      if (!hasFac(b, k[2])) return toast(josa(FAC[k[2]].name, '이가') + ' 필요합니다');
      pickOfficers({ push: true, title: k[1] + ' 생산 — 담당 무장', list: idleOfficers(b), max: k[0] === 'ram' ? 1 : 3, hi: 'int', key: function (o) { return o.int; }, auto: function (n) { return autoPick('produce', b, { kind: k[0] }, n); },
        preview: function (os) { return k[0] === 'ram' ? '충차 1대 · 금 ' + (anyHas(os, '발명') ? 300 : 600) : '예상 <b>+' + fmt(produceAmount(b, k[0], os)) + '</b> · 금 300'; } },
        function (os) { var r = cmdProduce(b, k[0], ids(os)); return done(r, r.ok ? k[1] + ' +' + fmt(r.n) : '', 'hammer'); });
    } }
  });
}
function flowTrade(b) {
  if (!hasFac(b, 'market')) return toast('시장이 필요합니다');
  var st = { dir: 'buy', v: 0 };
  function mx() { return st.dir === 'buy' ? Math.floor(b.gold / 50) * 50 : Math.floor(b.food / 6 / 50) * 50; }
  function pv() { return st.dir === 'buy' ? '금 -' + fmt(st.v) + ' → 병량 <b>+' + fmt(st.v * 4) + '</b>' : '병량 -' + fmt(st.v * 6) + ' → 금 <b>+' + fmt(st.v) + '</b>'; }
  st.v = Math.min(300, mx());
  showDialog({
    render: function () {
      return dlgHead('거래 — ' + b.n) + '<div class="dlg-b"><div class="opts"><button class="opt' + (st.dir === 'buy' ? ' on' : '') + '" type="button" data-a="dir" data-v="buy"><b>병량 구입</b><small>금 1 → 병량 4</small></button>' +
        '<button class="opt' + (st.dir === 'sell' ? ' on' : '') + '" type="button" data-a="dir" data-v="sell"><b>병량 판매</b><small>병량 6 → 금 1</small></button></div>' +
        '<div class="fld"><label><span>금 기준 수량</span><b id="trV">' + fmt(st.v) + '</b></label><input type="range" id="trR" min="0" max="' + mx() + '" step="50" value="' + st.v + '" data-i="v"></div>' +
        '<p class="note">보유: 금 ' + fmt(b.gold) + ' · 병량 ' + fmt(b.food) + '</p></div><div class="dlg-f"><div class="pv" id="trP">' + pv() + '</div><button class="btn pri" type="button" data-a="ok">거래</button></div>';
    },
    on: {
      dir: function (el) { st.dir = el.getAttribute('data-v'); st.v = Math.min(300, mx()); refreshDialog(); },
      v: function (el) { st.v = +el.value; $('trV').textContent = fmt(st.v); $('trP').innerHTML = pv(); },
      ok: function () { if (st.v <= 0) return toast('수량을 정하세요'); var r = cmdTrade(b, st.dir, st.v); if (r.ok) closeDialog(); done(r, r.ok ? (st.dir === 'buy' ? '병량 +' : '금 +') + fmt(r.n) : '', 'coin'); }
    }
  });
}
function flowSearch(b) {
  pickOfficers({ title: '탐색 — 담당 무장', list: idleOfficers(b), max: 1, hi: 'pol', key: function (o) { return o.pol + (o.sk === '안력' ? 50 : 0); }, auto: function (n) { return autoPick('search', b, null, 1); }, preview: function () { return '재야의 인재나 숨은 재물을 찾습니다'; } },
    function (os) {
      var r = cmdSearch(b, os[0].id);
      if (!r.ok) return done(r);
      if (r.found !== undefined) { sfx('drum'); done(r, josa(off(r.found).n, '을를') + ' 찾았습니다! 등용해 보세요'); }
      else if (r.gold) done(r, '금 ' + josa(String(r.gold), '을를') + ' 찾았습니다');
      else done(r, '아무것도 찾지 못했습니다');
    });
}
function flowRecruit(b) {
  var ts = freeOfficers(b).concat(baseCaptives(b).filter(function (o) { return o.capF === b.owner; }));
  if (!ts.length) return toast('등용할 대상이 없습니다 — 탐색으로 재야 인재를 찾으세요');
  showDialog({
    render: function () {
      var h = dlgHead('등용 — 누구를 부를까요') + '<div class="dlg-b"><div class="rows">';
      for (var i = 0; i < ts.length; i++) h += offRow(ts[i], { a: 't', badge: ts[i].st === 'captive' ? '포로' : '재야' });
      return h + '</div></div>';
    },
    on: { t: function (el) {
      var t = off(+el.getAttribute('data-v'));
      pickOfficers({ push: true, title: t.n + ' 등용 — 누구를 보낼까요', list: idleOfficers(b), max: 1, hi: 'cha', key: function (o) { return recruitChance(b, o, t); }, rt: function (o) { return '<b>' + recruitChance(b, o, t) + '%</b>'; }, rtHead: '성공률', auto: function () { return autoPick('recruit', b, { target: t }, 1); },
        preview: function (os) { return '성공률 <b>' + recruitChance(b, os[0], t) + '%</b>'; } },
        function (os) { var r = cmdRecruit(b, os[0].id, t.id); if (r.ok && r.joined) sfx('cheer'); return done(r, r.ok ? (r.joined ? josa(t.n, '이가') + ' 합류했습니다!' : josa(t.n, '이가') + ' 거절했습니다') : ''); });
    } }
  });
}
function flowReward(b) {
  showDialog({
    render: function () {
      var os = baseOfficers(b).filter(function (o) { return !isLord(o); }).sort(function (x, y) { return x.loy - y.loy; });
      var h = dlgHead('포상 — 금 100 · 행동력 ' + AP.reward) + '<div class="dlg-b"><p class="note">보유 금 ' + fmt(b.gold) + ' · 행동력 ' + G.factions[b.owner].ap + '</p><div class="rows">';
      for (var i = 0; i < os.length; i++) h += offRow(os[i], { a: 'r', dim: os[i].loy >= 100, rt: '<span class="' + (os[i].loy < 70 ? 'bad' : '') + '">충성 <b>' + os[i].loy + '</b></span>' });
      if (!os.length) h += '<p class="note">포상할 무장이 없습니다.</p>';
      return h + '</div></div>';
    },
    on: { r: function (el) { var r = cmdReward(b, +el.getAttribute('data-v')); if (!r.ok) return toast(r.msg); sfx('coin'); toast('충성 +' + r.n); refreshDialog(); refreshSheet(); refreshHud(); } }
  });
}
function flowMove(b) {
  var dests = facBases(b.owner).filter(function (x) { return x.id !== b.id; });
  if (!dests.length) return toast('옮겨 갈 다른 거점이 없습니다');
  pickOfficers({ keep: true, title: '이동 — 보낼 무장', list: idleOfficers(b), max: 6, key: function (o) { return o.ldr + o.war + o.int + o.pol; }, ok: '다음', preview: function (os) { return os.length + '명 선택'; } },
    function (os) {
      dests.sort(function (x, y) { return hdist(b.c, b.r, x.c, x.r) - hdist(b.c, b.r, y.c, y.r); });
      showDialog({
        render: function () {
          var h = dlgHead('이동 — 어디로 보낼까요') + '<div class="dlg-b"><div class="rows">';
          for (var i = 0; i < dests.length; i++) h += '<button class="row" type="button" data-a="d" data-v="' + dests[i].id + '"><span class="mid"><span class="nm">' + dests[i].n + '</span><span class="ds">' + SIZE_NAME[dests[i].sz] + ' · 무장 ' + baseOfficers(dests[i]).length + '명 · 병력 ' + fmt(dests[i].troops) + '</span></span><span class="rt"><b>' + days(travelTurns(b, dests[i])) + '</b></span></button>';
          return h + '</div></div>';
        },
        on: { d: function (el) { var r = cmdMoveOfficers(b, ids(os), +el.getAttribute('data-v')); if (r.ok) closeDialog(); done(r, r.ok ? os.length + '명 출발 — ' + days(r.turns) + ' 뒤 도착' : ''); } }
      }, true);
    });
}
function flowCaptive(b) {
  showDialog({
    render: function () {
      var cs = baseCaptives(b), h = dlgHead('포로 ' + cs.length + '명') + '<div class="dlg-b"><p class="note">등용은 인재 → 등용에서 합니다. 풀어 주면 원래 세력으로 돌아갑니다.</p>';
      for (var i = 0; i < cs.length; i++) h += '<div class="row">' + porTag(cs[i]) + '<span class="mid"><span class="nm">' + cs[i].n + skTag(cs[i]) + '</span><span class="ds">' + st5(cs[i]) + '</span></span><button class="btn" type="button" data-a="rel" data-v="' + cs[i].id + '">해방</button><button class="btn" type="button" data-a="exe" data-v="' + cs[i].id + '">참수</button></div>';
      return h + '</div>';
    },
    on: {
      rel: function (el) { var o = off(+el.getAttribute('data-v')); cmdCaptive(b, o.id, 'release'); toast(josa(o.n, '을를') + ' 풀어 주었습니다'); if (!b.captives.length) closeDialog(); else refreshDialog(); refreshSheet(); },
      exe: function (el) { var o = off(+el.getAttribute('data-v')); if (el.getAttribute('data-c')) { cmdCaptive(b, o.id, 'execute'); toast(josa(o.n, '을를') + ' 참수했습니다'); if (!b.captives.length) closeDialog(); else refreshDialog(); refreshSheet(); } else { el.setAttribute('data-c', '1'); el.textContent = '정말?'; el.classList.add('pri'); } }
    }
  });
}

/* ---------- 시설 ---------- */
function flowDevelop(b, pi) {
  if (b.owner !== G.player) return;
  if (!idleOfficers(b).length) return toast('행동할 수 있는 무장이 없습니다');
  showDialog({
    render: function () {
      var h = dlgHead(b.n + ' — 무엇을 지을까요') + '<div class="dlg-b"><p class="note">보유 금 ' + fmt(b.gold) + ' · 행동력 ' + AP.develop + ' 소모</p><div class="lst-opt">';
      for (var i = 0; i < FAC_ORDER.length; i++) { var F = FAC[FAC_ORDER[i]], ok = b.gold >= F.cost; h += '<button class="row' + (ok ? '' : ' dim') + '" type="button" data-a="f" data-v="' + FAC_ORDER[i] + '">' + thumb(FAC_ORDER[i], 'lg') + '<span class="mid"><span class="nm">' + F.name + '</span><span class="ds">' + F.desc + '</span></span><span class="rt">금 <b>' + F.cost + '</b></span></button>'; }
      return h + '</div></div>';
    },
    on: { f: function (el) {
      var t = el.getAttribute('data-v'), F = FAC[t];
      if (b.gold < F.cost) return toast('금이 부족합니다 (' + F.cost + ' 필요)');
      pickOfficers({ push: true, title: F.name + ' 건설 — 담당 무장', list: idleOfficers(b), max: 3, hi: 'pol', key: function (o) { return o.pol + (o.sk === '축성' ? 60 : 0); }, auto: function (n) { return autoPick('develop', b, null, n); },
        preview: function (os) { var rate = 60 + Math.round((bestOf(os, 'pol') + sumOthers(os, 'pol') * 0.5) * 0.6); if (anyHas(os, '축성')) rate *= 2; return '완공까지 <b>' + days(Math.ceil(F.build / rate)) + '</b> · 금 ' + F.cost; } },
        function (os) { var r = cmdDevelop(b, pi, t, ids(os)); return done(r, r.ok ? F.name + ' 착공 — ' + days(r.turns) + ' 뒤 완공' : '', 'hammer'); });
    } }
  });
}
function flowFacility(b, pi) {
  var fc = b.plots[pi].fac; if (!fc) return;
  var F = FAC[fc.t];
  showDialog({
    render: function () {
      var cands = mergeCandidates(b, pi);
      var h = dlgHead(b.n + ' ' + F.name + ' Lv' + fc.lv) + '<div class="dlg-b"><div class="card">' + thumb(fc.t, 'lg') + '<p>' + F.desc + '</p></div>' + (fc.done ? '' : '<p class="note">건설 중 — ' + days(Math.max(1, Math.ceil((fc.need - fc.prog) / fc.rate))) + ' 남음</p>') +
        '<div class="cmds"><button class="cmd' + (cands.length ? ' pri' : ' off') + '" type="button" data-a="merge"><b>흡수합병</b><small>' + (fc.lv >= 3 ? '최고 레벨' : (cands.length ? '금 ' + 150 * fc.lv + ' · 행 ' + AP.merge : '인접한 같은 시설 필요')) + '</small></button>' +
        '<button class="cmd" type="button" data-a="demo"><b>철거</b><small>부지를 비웁니다</small></button></div>' +
        '<p class="note">흡수합병: 바로 옆의 같은 종류 시설 하나를 흡수해 레벨을 올립니다(최대 3). 흡수된 부지는 비워집니다.</p></div>';
      return h;
    },
    on: {
      merge: function () {
        var cands = mergeCandidates(b, pi);
        if (!cands.length) return toast(fc.lv >= 3 ? '이미 최고 레벨입니다' : '바로 옆에 같은 종류의 완성된 시설이 있어야 합니다');
        pickOfficers({ push: true, title: '흡수합병 — 담당 무장', list: idleOfficers(b), max: 1, hi: 'pol', key: function (o) { return -statSum(o); }, auto: function () { return autoPick('merge', b, null, 1); }, preview: function () { return F.name + ' Lv' + fc.lv + ' → <b>Lv' + (fc.lv + 1) + '</b> · 금 ' + 150 * fc.lv; } },
          function (os) { var r = cmdMerge(b, pi, cands[0], ids(os)); return done(r, r.ok ? F.name + ' Lv' + r.lv + '로 올랐습니다' : '', 'hammer'); });
      },
      demo: function (el) { if (el.getAttribute('data-c')) { cmdDemolish(b, pi); closeDialog(); sfx('miss'); toast(F.name + ' 철거'); refreshSheet(); afterAction(); } else { el.setAttribute('data-c', '1'); el.querySelector('b').textContent = '정말 철거?'; } }
    }
  });
}

/* ---------- 출진·수송 ---------- */
/* 앱으로 설치해 열었을 때 휴대폰의 '뒤로' 단추: ×와 같은 규칙으로 한 단계 물러난다(tools/build.py 의 앱판 스크립트가 부른다).
   물러났으면 true, 더 물러날 곳이 없으면 false(그러면 앱이 '한 번 더 누르면 나갑니다'를 띄운다) */
function appBack() {
  if (!G || !$('title').classList.contains('off')) {       // 제목 화면: 떠 있는 창(군주 고르기·도움말)만 닫는다
    if (MODAL && !MODAL.lock) { backDialog(); return true; }
    return false;
  }
  if (UI.play) return true;                                 // 지난 열흘을 보여 주는 중에는 그대로 둔다
  if (MODAL) { backDialog(); return true; }                 // 끝난 판의 창(lock)은 backDialog 가 닫지 않는다
  if (UI.busy) return true;                                 // 움직이는 장면이 나오는 중
  if (SHEET && !SHEET.home) { backSheet(); return true; }
  return false;
}
function backToBase(id) { return function () { var bb = G.bases[id]; if (bb && bb.owner === G.player) selectBase(bb, false, 'mil'); else clearSel(); }; }
function flowDeploy(b) {
  var list = idleOfficers(b).sort(function (x, y) { return aiMilScore(y) - aiMilScore(x); });
  if (!list.length) return toast('행동할 수 있는 무장이 없습니다');
  if (b.troops < 100) return toast('주둔 병력이 없습니다');
  var st = { type: 'sword', ids: [], troops: 0, turns: 12, auto: true };
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
  function fix() { var m = mx(); if (st.auto || st.troops > m) st.troops = m; }
  function pv() {
    if (!st.ids.length) return '주장을 고르세요';
    var tmp = { type: st.type, off: st.ids, troops: st.troops, max: st.troops };
    return '공격 <b>' + Math.round(uAtk(tmp)) + '</b> · 방어 <b>' + Math.round(uDef(tmp)) + '</b> · 이동 <b>' + uMaxMp(tmp) + '</b> · 군량 <b>' + fmt(food()) + '</b>';
  }
  showDialog({
    render: function () {
      var h = dlgHead('출진 — ' + b.n) + '<div class="dlg-b"><div class="sec">병과</div><div class="opts">', i;
      var UKEY = { sword: 'u_sword', spear: 'u_spear', halberd: 'u_halberd', bow: 'u_bow', cav: 'u_cav', ram: 'u_ram' };
      for (i = 0; i < COMBAT_TYPES.length; i++) {
        var t = COMBAT_TYPES[i], T = UNIT_TYPES[t], ok = usable(t);
        h += '<button class="opt' + (st.type === t ? ' on' : '') + (ok ? '' : ' off') + '" type="button" data-a="type" data-v="' + t + '">' + thumb(UKEY[t]) + '<b>' + T.name + '</b><small>' + (t === 'sword' ? '무기 불필요' : (t === 'ram' ? '충차 ' + b.w.ram + '대' : WEAPON_NAMES[T.weapon] + ' ' + fmt(stock(t)))) + '</small></button>';
      }
      h += '</div><div class="sec">무장 — 첫 번째가 주장, 최대 3명<button class="btn auto" type="button" data-a="auto">자동 편성</button></div><div class="rows">';
      var ai = APT_IDX[st.type];
      for (i = 0; i < list.length; i++) {
        var o = list[i], si = st.ids.indexOf(o.id);
        h += offRow(o, { a: 'pick', sel: si >= 0, badge: si === 0 ? '주장' : (si > 0 ? '부장' : ''), rt: (ai !== undefined ? '적성 <b class="' + (o.apt.charAt(ai) === 'S' ? 'bad' : (o.apt.charAt(ai) === 'A' ? 'hi' : '')) + '">' + o.apt.charAt(ai) + '</b><br>' : '') + '지휘 ' + fmt(cmdCap(o)) });
      }
      h += '</div>';
      if (st.ids.length) {
        h += '<div class="fld"><label><span>병력 (주둔 ' + fmt(b.troops) + ')</span><b id="dpV">' + fmt(st.troops) + '</b></label><input type="range" id="dpR" min="0" max="' + mx() + '" step="100" value="' + st.troops + '" data-i="troops"></div><div class="sec">군량</div><div class="opts c4">';
        [6, 12, 18, 24].forEach(function (n) { h += '<button class="opt' + (st.turns === n ? ' on' : '') + '" type="button" data-a="turns" data-v="' + n + '"><b>' + days(n) + '분</b><small>' + fmt(Math.ceil(st.troops / 20) * n) + '</small></button>'; });
        h += '</div><p class="note">도시 병량 ' + fmt(b.food) + '. 이웃 성까지는 적어도 30일, 보통 40~60일이 걸립니다. 군량이 떨어지면 병사가 흩어집니다.</p>';
      }
      return h + '</div><div class="dlg-f"><div class="pv" id="dpP">' + pv() + '</div><button class="btn pri" type="button" data-a="ok"' + (st.ids.length && st.troops >= 100 ? '' : ' disabled') + '>출진</button></div>';
    },
    on: {
      type: function (el) { var t = el.getAttribute('data-v'); if (!usable(t)) return toast(t === 'ram' ? '충차가 없습니다 — 공방에서 생산하세요' : WEAPON_NAMES[UNIT_TYPES[t].weapon] + ' 재고가 없습니다'); st.type = t; st.auto = true; fix(); refreshDialog(); },
      pick: function (el) { var id = +el.getAttribute('data-v'), i = st.ids.indexOf(id); if (i >= 0) st.ids.splice(i, 1); else if (st.ids.length < 3) st.ids.push(id); else return toast('최대 3명입니다'); st.auto = true; fix(); refreshDialog(); },
      turns: function (el) { st.turns = +el.getAttribute('data-v'); refreshDialog(); },
      auto: function () { st.ids = autoTeam(b, st.type, Math.min(b.troops, 8000)); st.auto = true; fix(); toast(st.ids.length ? UNIT_TYPES[st.type].name + '에 가장 알맞은 ' + st.ids.length + '명을 골랐습니다' : '편성할 무장이 없습니다', 2200); refreshDialog(); },
      troops: function (el) { st.troops = +el.value; st.auto = false; $('dpV').textContent = fmt(st.troops); $('dpP').innerHTML = pv(); },
      ok: function () {
        var r = cmdDeploy(b, { type: st.type, ids: st.ids, troops: st.troops, food: food() });
        if (!r.ok) return toast(r.msg);
        closeDialog(); sfx('deploy');
        var u = r.unit, name = uName(u);
        clearSel(); refreshHud(); syncScene();                       // 막 나온 부대를 지도에 세우고
        if (!onScreen(u.c, u.r, 20)) jumpTo(u.c, u.r, Math.max(cam.z, 0.8));
        UI.busy = true;
        fxDeploy(u, b, function () {                                // 성에서 걸어 나오는 모습을 보인 뒤 고른 상태로
          UI.busy = false;
          if (alive(u)) { selectUnit(u); UI.sret = backToBase(b.id); toast(name + ' 출진 — 파란 칸을 눌러 이동하세요', 2600); }
          afterAction();
        });
      }
    }
  });
}
function flowTransport(b) {
  var list = idleOfficers(b).sort(function (x, y) { return aiMilScore(x) - aiMilScore(y); });
  if (!list.length) return toast('행동할 수 있는 무장이 없습니다');
  if (b.troops < 100) return toast('호위할 병력이 없습니다');
  var st = { id: list[0].id, troops: Math.min(1000, Math.floor(b.troops / 100) * 100), gold: 0, food: 0, spear: 0, halberd: 0, bow: 0, horse: 0, ram: 0 };
  var fs = [['troops', '병력', b.troops, 100], ['gold', '금', b.gold, 50], ['food', '병량', b.food, 500], ['spear', '창', b.w.spear, 100], ['halberd', '극', b.w.halberd, 100], ['bow', '노', b.w.bow, 100], ['horse', '군마', b.w.horse, 100], ['ram', '충차', b.w.ram, 1]];
  var on = {
    pick: function (el) { st.id = +el.getAttribute('data-v'); refreshDialog(); },
    auto: function () { var t = autoTeam(b, 'trans', 0); if (t.length) st.id = t[0]; toast('싸움에 덜 쓰이는 무장을 골랐습니다', 2000); refreshDialog(); },
    ok: function () {
      var need = Math.ceil(st.troops / 20) * 8;
      var r = cmdDeploy(b, { type: 'trans', ids: [st.id], troops: st.troops, food: Math.max(st.food, Math.min(b.food, need)), gold: st.gold, cargo: { spear: st.spear, halberd: st.halberd, bow: st.bow, horse: st.horse, ram: st.ram } });
      if (!r.ok) return toast(r.msg);
      closeDialog(); sfx('drum'); toast('수송대 출발 — 파란 칸을 눌러 이동하세요. 아군 거점으로 들여보내면 물자가 합쳐집니다', 3200); syncScene(); selectUnit(r.unit); UI.sret = backToBase(b.id); afterAction();
    }
  };
  fs.forEach(function (f) { on[f[0]] = function (el) { st[f[0]] = +el.value; $('tv_' + f[0]).textContent = fmt(st[f[0]]); }; });
  showDialog({
    render: function () {
      var h = dlgHead('수송 — ' + b.n) + '<div class="dlg-b"><div class="sec">호송 무장<button class="btn auto" type="button" data-a="auto">자동</button></div><div class="rows">', i;
      for (i = 0; i < list.length; i++) h += offRow(list[i], { a: 'pick', sel: list[i].id === st.id });
      h += '</div><div class="sec">실을 것</div>';
      for (i = 0; i < fs.length; i++) { var f = fs[i], m = Math.floor(f[2] / f[3]) * f[3]; if (m <= 0 && f[0] !== 'troops') continue; h += '<div class="fld"><label><span>' + f[1] + ' (보유 ' + fmt(f[2]) + ')</span><b id="tv_' + f[0] + '">' + fmt(st[f[0]]) + '</b></label><input type="range" id="tr_' + f[0] + '" min="' + (f[0] === 'troops' ? 100 : 0) + '" max="' + m + '" step="' + f[3] + '" value="' + st[f[0]] + '" data-i="' + f[0] + '"></div>'; }
      return h + '<p class="note">수송대는 싸움에 약합니다. 병력이 먹을 군량은 최소 80일분이 자동으로 실립니다.</p></div><div class="dlg-f"><div class="pv">행동력 ' + AP.deploy + '</div><button class="btn pri" type="button" data-a="ok">출발</button></div>';
    },
    on: on
  });
}

/* ---------- 목록·기록·메뉴 ---------- */
/* 부대가 있는 곳을 말로: 성역 안이면 그 성, 아니면 가장 가까운 거점에서 몇 칸 */
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
  clearRet();
  var st = { tab: tab || 'city' };
  showDialog({
    render: function () {
      var h = dlgHead('목록') + '<div class="dlg-b"><div class="tabs">', tabs = [['city', '거점'], ['unit', '부대'], ['off', '무장'], ['fac', '세력']], i;
      for (i = 0; i < 4; i++) h += '<button type="button" data-a="tab" data-v="' + tabs[i][0] + '"' + (st.tab === tabs[i][0] ? ' class="on"' : '') + '>' + tabs[i][1] + '</button>';
      h += '</div><div class="rows">';
      if (st.tab === 'city') {
        facBases(G.player).forEach(function (b) { h += '<button class="row" type="button" data-a="b" data-v="' + b.id + '"><span class="mid"><span class="nm">' + b.n + ' <em>' + SIZE_NAME[b.sz] + '</em></span><span class="ds">금 ' + fmt(b.gold) + ' · 병량 ' + fmt(b.food) + ' · 치안 ' + b.order + '</span></span><span class="rt"><b>' + fmt(b.troops) + '</b><br>대기 ' + idleOfficers(b).length + '명</span></button>'; });
      } else if (st.tab === 'unit') {
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
      } else if (st.tab === 'off') {
        var os = facOfficers(G.player).sort(function (x, y) { return (isLord(y) ? 1000 : 0) + (y.ldr + y.war + y.int + y.pol) - (isLord(x) ? 1000 : 0) - (x.ldr + x.war + x.int + x.pol); });
        os.forEach(function (o) { h += offRow(o, { badge: isLord(o) ? '군주' : '', rt: (o.unit !== null ? '출진' : G.bases[o.st === 'travel' ? o.dest : o.loc].n) + '<br><span class="' + (o.loy < 70 ? 'bad' : '') + '">충 ' + o.loy + '</span>' }); });
      } else {
        G.factions.filter(function (F) { return F.alive; }).map(function (F) { var t = 0; facBases(F.id).forEach(function (b) { t += b.troops; }); facUnits(F.id).forEach(function (u) { t += u.troops; }); return { F: F, t: t, c: facCities(F.id).length }; })
          .sort(function (x, y) { return y.c - x.c || y.t - x.t; })
          .forEach(function (x) { var L = off(x.F.lord); h += '<button class="row" type="button" data-a="f" data-v="' + x.F.id + '">' + porTag(L) + '<span class="mid"><span class="nm">' + x.F.name + (x.F.id === G.player ? ' <em>나</em>' : '') + '</span><span class="ds">도시 ' + x.c + ' · 무장 ' + facOfficers(x.F.id).length + '명</span></span><span class="rt"><b>' + fmt(x.t) + '</b><br><span class="chip" style="background:' + x.F.color + '">&nbsp;</span></span></button>'; });
      }
      return h + '</div></div>';
    },
    on: {
      tab: function (el) { st.tab = el.getAttribute('data-v'); refreshDialog(); },
      allu: function () { st.allU = true; refreshDialog(); },
      b: function (el) { var b = G.bases[+el.getAttribute('data-v')]; jumpFromDialog('목록', function () { gotoBase(b); }); },
      u: function (el) { var u = UMAP[+el.getAttribute('data-v')]; if (u) jumpFromDialog('목록', function () { gotoUnit(u); }); },
      off: function (el) { showOfficer(off(+el.getAttribute('data-v'))); },
      f: function (el) { var f = +el.getAttribute('data-v'), L = off(G.factions[f].lord), b = L.unit !== null ? null : G.bases[L.loc]; if (!b) b = facBases(f)[0]; if (b) jumpFromDialog('목록', function () { gotoBase(b); }); }
    }
  });
}
function logRows(list) {
  var h = '';
  for (var i = list.length - 1; i >= 0; i--) { var e = list[i]; h += '<button class="row" type="button" data-a="j" data-v="' + i + '"><span class="mid"><span class="ds">' + e.d + '</span><span style="white-space:normal;display:block' + (e.imp >= 3 ? ';color:var(--gold);font-weight:700' : '') + '">' + e.t + '</span></span></button>'; }
  return h || '<p class="note">아직 기록이 없습니다.</p>';
}
function showLog(list, title) {
  clearRet();
  showDialog({
    render: function () { return dlgHead(title) + '<div class="dlg-b"><div class="rows">' + logRows(list) + '</div></div>'; },
    on: { j: function (el) { var e = list[+el.getAttribute('data-v')]; if (e && e.c !== undefined) jumpFromDialog(title, function () { clearSel(); jumpTo(e.c, e.r, Math.max(cam.z, 0.8)); flashHex(e.c, e.r, '#b5332a'); }); } }
  });
}
var HELP_HTML = '<div class="help">' +
  '<h3>목표</h3><p>도시 42곳을 모두 차지하면 천하통일입니다. 거점을 모두 잃으면 끝납니다.</p>' +
  '<h3>턴 종료와 지난 열흘</h3><p>턴 종료를 누르면 열흘이 흐릅니다. 먼저 행군을 맡겨 둔 내 부대가 움직이고, 이어서 다른 세력의 움직임 가운데 <b>나와 관련된 일, 내 땅 가까이에서 일어난 일, 성의 주인이 바뀐 일</b>을 차례로 보여 줍니다. 화면을 누르면 다음 장면으로 넘어가고, 건너뛰기를 누르면 바로 내 차례가 됩니다. 속도는 재생 중 아래 버튼이나 메뉴에서 바꿉니다. 끝나면 지난 열흘의 일을 한데 모아 보여 줍니다.</p>' +
  '<h3>턴과 행동력</h3><p>한 턴은 10일입니다. 내정·출진 명령은 행동력을 씁니다. 행동력은 매 턴 돌아오고, 도시가 많고 군주의 매력이 높을수록 많이 돌아옵니다. 무장 한 사람은 한 턴에 한 가지 일만 합니다.</p>' +
  '<h3>자동</h3><p>무장을 고르는 창의 <b>자동</b> 버튼은 그 일을 가장 잘하는 무장을 골라 줍니다. 한 번 더 누르면 한 명만 쓰는 편성으로 바뀝니다. 열 제목(통·무·지·정·매)을 누르면 그 능력으로 정렬합니다.</p>' +
  '<h3>도시와 시설</h3><p>도시를 누르면 명령 패널이 열립니다. 도시 둘레의 밝은 칸이 부지이고, 누르면 시설을 짓습니다. 같은 시설이 붙어 있으면 흡수합병으로 레벨을 올립니다(최대 3). 조폐는 옆의 시장, 곡창은 옆의 농장 수입을 50% 늘립니다. 금은 매월 초, 병량은 1·4·7·10월 초에 들어옵니다.</p>' +
  '<h3>STATUS 창</h3><p>화면 아래에 늘 떠 있는 창입니다. 아무것도 고르지 않았을 때는 세력 현황과 <b>지금 할 일</b>이 보이고, 줄을 누르면 그 거점이나 부대로 바로 갑니다. 거점이나 부대를 고르면 같은 자리에 그 정보와 명령이 나옵니다. <b>거점·부대·무장·천하</b> 단추는 그 목록을 엽니다 — 부대 목록에는 내 부대의 위치와 상태, 그리고 가까이 있는 다른 세력의 부대가 나옵니다. 오른쪽 위 ▾로 접을 수 있고, 맨 위 날짜 줄을 누르면 다시 펼쳐집니다.</p>' +
  '<h3>출진과 이동</h3><p>군사 → 출진에서 병과, 무장(주장과 부장 둘), 병력, 군량을 정하면 부대가 성 앞에 나옵니다. 창병·극병·노병·기병은 무기 재고가 병력만큼 필요합니다. 부대를 누르면 이번 턴에 갈 수 있는 칸이 <b>파랗게</b> 보이고, 그 칸을 누르면 움직입니다. 적이나 적의 성을 누르면 공격합니다. 적 부대 옆 칸에 들어서면 그 턴에는 더 나아가지 못합니다. 자기 거점으로 들어가면 입성하고, 주인 없는 거점은 들어가면 차지합니다.</p>' +
  '<h3>성역과 행군 일수</h3><p>성 둘레 ' + ZONE_R + '칸(붓으로 두른 고리 안)은 그 성의 <b>성역</b>입니다. 성역의 경계를 넘으면 — 나가든 들어가든 — 그 턴의 이동은 거기서 끝납니다(옅은 파란 칸). 성역에 막 들어선 부대는 그 턴에 그 성을 칠 수 없습니다(노병의 두 칸 사격도 마찬가지). 그래서 성에서 나와 다른 성에 닿기까지 가장 가까운 곳도 <b>30일</b>(3턴), 보통은 40~60일이 걸립니다. 적이 성역에 들어서면 한 턴의 여유가 생기니 그때 막을 준비를 하세요. 관문에는 성역이 없습니다.</p>' +
  '<h3>행군(선택)</h3><p>먼 곳까지 매 턴 직접 움직이기 번거로우면 부대 창의 <b>행군</b>을 누르고 목적지를 누르세요. 걸리는 날수를 보여 주고, 턴을 마칠 때마다 한 구간씩 알아서 갑니다. 도중에 직접 움직이거나 공격해도 됩니다.</p>' +
  '<h3>전투</h3><p>부대를 고르고 적을 누르면 공격·전법·계략 가운데 고를 수 있습니다. 전법은 기력을 쓰고, 병과 적성(C→S)이 높을수록 쓸 수 있는 전법이 늘고 잘 통합니다.</p>' +
  '<p><b>전법의 결과는 세 가지</b>입니다. <b>실패</b>하면 피해가 통상 공격의 60%로 줄고 효과가 없으며 반격을 크게 받습니다. <b>성공</b>하면 전법의 피해와 효과가 그대로 들어갑니다. <b>대성공</b>이면 피해가 1.3배가 되고 <b>효과 자체가 세집니다</b> — 돌출·돌격은 두 칸 밀어내고, 나선첨은 반드시 혼란시키고, 이단첨은 기력을 30 깎는 식입니다. 성공률은 병과 적성과 무력으로, 대성공률은 여기에 내 무력과 상대 통솔의 차이를 더해 정해지며, 혼란은 상대의 지력·통솔이 높을수록 덜 걸립니다. 적을 고른 뒤 <b>전법 풀이</b>를 누르면 그 상대에 대한 확률과 효과를 볼 수 있습니다.</p>' +
  '<ul><li>창병은 기병에, 기병은 극병에, 극병은 창병에 강합니다.</li><li>노병은 두 칸 밖에서 반격 없이 쏩니다.</li><li>충차는 성의 내구를 크게 깎습니다.</li><li>거점은 병력이나 내구가 0이 되면 함락됩니다.</li><li>숲·구릉의 부대는 피해를 덜 받고, 강 위의 부대는 약해집니다.</li></ul>' +
  '<h3>인재</h3><p>탐색으로 재야의 인재를 찾아 등용합니다. 사로잡은 적장도 등용할 수 있습니다. 충성이 낮은 무장은 떠날 수 있으니 포상하세요. 해가 바뀌면 새 인물이 세상에 나옵니다.</p>' +
  '<h3>닫기(×)와 뒤로 가기</h3><p><b>×는 한 단계만 뒤로</b> 갑니다. 무장 정보를 닫으면 보던 목록으로, 무장 고르는 표를 닫으면 그 앞 창으로 돌아갑니다. 부대에서 대상이나 행군을 고르던 중이면 그것만 물립니다. 막 출진한 부대의 창을 닫으면 나온 성의 군사 탭으로 돌아갑니다.</p>' +
  '<p>목록·기록·지난 열흘의 일에서 줄을 눌러 지도로 건너뛰면 왼쪽 위에 <b>‹ 목록</b> 같은 단추가 생깁니다. 누르면 보던 자리 그대로 다시 열립니다. 그렇게 열린 거점·부대 창은 ×로도 목록에 돌아갑니다.</p>' +
  '<h3>조작</h3><p>끌어서 지도를 옮기고, 두 손가락으로 확대·축소합니다. 오른쪽 위 작은 지도를 누르면 그곳으로 건너뜁니다. 거점 이름표의 붉은 낙관 숫자는 아직 일하지 않은 무장 수입니다. 부대 이름표에는 주장의 얼굴이 붙습니다.</p>' +
  '<h3>지도</h3><p>실제 지형(고도·강·해안)과 거점의 실제 위치를 바탕으로 만들었습니다. 한 칸은 약 ' + MAPDATA.km + 'km입니다. 황하 하류는 후한 때의 물길을 따릅니다.</p>' +
  '<h3>일기토</h3><p>무력 75 이상의 주장끼리 붙어 싸우면 낮은 확률로 일기토가 벌어집니다. 지금은 자동으로 판정되며, 진 쪽은 병력과 기력을 잃습니다.</p>' +
  '<h3>소리</h3><p>효과음과 음악은 메뉴에서 따로 끌 수 있습니다. 음악은 형편에 따라 바뀝니다 — 평시에는 두 곡이 번갈아 나오고, 다른 세력의 부대가 가까이 오면 긴장된 곡으로, 싸움이 벌어지면 전투 곡으로 넘어갑니다.</p>' +
  '<h3>앱으로 설치</h3><p>휴대폰 브라우저에서 <b>aaronkyung-a11y.github.io/chunhado</b> 를 열면 제목 화면에 <b>앱으로 설치</b> 단추가 나옵니다(안 나오면 브라우저 메뉴의 <b>홈 화면에 추가</b>). 설치하면 앱처럼 전체 화면으로 열리고, 한 번 연 뒤에는 인터넷이 없어도 됩니다. 저장은 여는 곳마다 따로라서, 다른 주소에서 하던 판은 넘어오지 않습니다.</p>' +
  '<h3>이번 판에 아직 없는 것</h3><p>직접 조작하는 일기토·설전, 외교, 기교·능력 연구, 군사 시설, 항구와 수군은 다음 판에서 넣습니다.</p></div>';
function showHelp() { showDialog({ render: function () { return dlgHead('도움말') + '<div class="dlg-b">' + HELP_HTML + '</div>'; }, on: {} }, true); }
function showMenu() {
  showDialog({
    render: function () {
      return dlgHead('메뉴 — ' + GAME_VERSION) + '<div class="dlg-b"><div class="cmds"><button class="cmd" type="button" data-a="save"><b>저장</b><small>이 기기에 저장</small></button><button class="cmd" type="button" data-a="load"><b>불러오기</b><small>마지막 저장</small></button>' +
        '<button class="cmd" type="button" data-a="snd"><b>효과음 ' + (UI.sound ? '켜짐' : '꺼짐') + '</b><small>누르면 전환</small></button><button class="cmd" type="button" data-a="mus"><b>음악 ' + (UI.music ? '켜짐' : '꺼짐') + '</b><small>' + (!UI.music ? '누르면 켬' : (BGM.mode === 'file' ? '연주곡 · 누르면 끔' : (BGM.mode === 'syn' ? '곡 파일을 못 읽어 만든 음악 · 누르면 끔' : '누르면 끔'))) + '</small></button><button class="cmd" type="button" data-a="spd"><b>열흘 재생</b><small>' + SPEEDS[UI.pspeed][0] + ' · 누르면 전환</small></button><button class="cmd" type="button" data-a="help"><b>도움말</b><small>규칙·조작</small></button>' +
        '<button class="cmd" type="button" data-a="title"><b>처음으로</b><small>타이틀 화면</small></button></div><p class="note">턴을 마칠 때마다 자동으로 저장됩니다. 저장은 이 기기의 브라우저에만 남습니다.</p></div>';
    },
    on: {
      save: function () { toast(saveGame() ? '저장했습니다' : '이 환경에서는 저장할 수 없습니다'); },
      load: function () { if (loadGame()) { closeDialog(); clearSel(); startGame(); toast('불러왔습니다'); } else toast('저장된 게임이 없습니다'); },
      snd: function () { UI.sound = !UI.sound; if (UI.sound) audioInit(); saveOpts(); refreshDialog(); },
      mus: function () { UI.music = !UI.music; saveOpts(); if (UI.music) playBgm(bgmForState()); else stopBgm(); refreshDialog(); },
      spd: function () { UI.pspeed = (UI.pspeed + 1) % 4; saveOpts(); toast(UI.pspeed ? '턴을 마치면 지난 열흘을 ' + SPEEDS[UI.pspeed][0] + ' 보여 줍니다' : '재생을 끕니다 — 턴을 마치면 바로 요약만 보여 줍니다', 2600); refreshDialog(); },
      help: function () { showHelp(); },
      title: function () { saveGame(); closeDialog(); clearRet(); clearSel(); showTitle(); playBgm('title'); }
    }
  });
}

/* ---------- 저장 ---------- */
function saveOpts() { try { localStorage.setItem('chunhado_opts', JSON.stringify({ sound: UI.sound, music: UI.music, pspeed: UI.pspeed, home: HOME.open })); } catch (e) { /* */ } }
function loadOpts() {
  try {
    var o = JSON.parse(localStorage.getItem('chunhado_opts') || '{}');
    if (o.sound === false) UI.sound = false; if (o.music === false) UI.music = false;
    if (o.pspeed >= 0 && o.pspeed <= 3) UI.pspeed = o.pspeed | 0;
    if (o.home === false) HOME.open = false;
  } catch (e) { /* */ }
}
/* 지금 틀 음악의 장면: 싸운 지 한 턴 안이거나 적이 내 성 코앞이면 전투, 적이 가까이 있으면 긴장, 아니면 평시 */
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
function saveGame() { if (!G || G.over || UI.play) return false; try { localStorage.setItem(SAVE_KEY, serialize()); return true; } catch (e) { return false; } }
function hasSave() { try { return !!localStorage.getItem(SAVE_KEY); } catch (e) { return false; } }
function loadGame() { try { var s = localStorage.getItem(SAVE_KEY); return s ? deserialize(s) : false; } catch (e) { return false; } }
function dropSave() { try { localStorage.removeItem(SAVE_KEY); } catch (e) { /* */ } }

/* ---------- 턴 종료: 지난 열흘을 차례로 보여 주기 ----------
   1) 행군 중인 내 부대가 한 구간 나아간다  2) 다른 세력이 차례로 움직인다(나와 관련된 일·가까운 일·성의 주인이 바뀐 일만 보여 줌)
   3) 날짜가 넘어간다  4) 요약.  화면을 누르면 다음 장면으로, '건너뛰기'는 남은 장면을 모두 넘긴다. */
var endAsk = '';
var SPEEDS = [['끄기', 0], ['느리게', 1.5], ['보통', 1], ['빠르게', 0.5]];
function spdK() { return SPEEDS[UI.pspeed][1] || 1; }
function doEndTurn() {
  if (UI.busy || !G || G.over || MODAL || UI.play) return;
  var left = pendingUnits().length;
  if (left && endAsk !== G.turn + ':' + left) { endAsk = G.turn + ':' + left; toast('명령을 기다리는 부대가 ' + left + '개 있습니다 — 한 번 더 누르면 턴을 넘깁니다', 3500); return; }
  endAsk = '';
  clearRet(); clearSel();
  startPlayback();
}
/* 재생 중 콜백 보호: 재생이 끝났으면 무시, 오류가 나면 재생을 정리하고 알린다 */
function pg(fn) {
  return function () {
    if (!UI.play) return;
    try { return fn.apply(null, arguments); } catch (e) { UI.play.err = e; if (window.console) console.error(e); finishPlayback(); }
  };
}
function pwait(ms, cb, fixed) {
  var P = UI.play; if (!P) return;
  if (P.skip) { cb(); return; }
  var f = pg(function () { P.wake = null; cb(); });
  P.wake = function () { clearTimeout(P.timer); f(); };
  P.timer = setTimeout(f, fixed ? ms : ms * spdK());
}
function playNudge() {
  var P = UI.play; if (!P) return;
  if (P.wake) P.wake();
  else if (P.ans.length) { P.ans.forEach(function (a) { a.t0 = -1e12; }); UI.render = true; }
}
function playSkip() {
  var P = UI.play; if (!P || P.skip) return;
  P.skip = true; $('veil').classList.add('on');
  playNudge();
}
function setCaption(f, html, cls) {
  var F = f >= 0 ? G.factions[f] : null, L = F ? off(F.lord) : null, u = L ? POR_URL[L.por] : '';
  $('plPor').style.backgroundImage = u ? 'url(' + u + '),var(--porbg)' : '';
  $('plFac').innerHTML = F ? '<span class="chip" style="background:' + F.color + '">' + F.name + '군' + (f === G.player ? ' · 아군' : '') + '</span>' : '<span class="chip" style="background:#8d877b">천하</span>';
  var m = $('plMsg'); m.innerHTML = html; m.className = 'pl-msg' + (cls ? ' ' + cls : '');
}
function showBanner(t, sub) { var b = $('banner'); b.innerHTML = t + (sub ? '<small>' + sub + '</small>' : ''); b.classList.add('on'); }
function hideBanner() { $('banner').classList.remove('on'); }
function clearAnimFlags() { if (!R3) return; for (var id in R3.units) { var o = R3.units[id]; o.held = false; if (o.anim) { o.anim = false; o.c = -1; o.sig = ''; } } }
/* 그 칸이 화면에 보이게 한 뒤 cb. 이미 잘 보이면 바로. */
function focus(c, r, cb, zWant) {
  var P = UI.play;
  if (P && P.skip) { cb(); return; }
  if (onScreen(c, r, 26) && cam.z >= 0.55 && cam.z <= 1.7) { cb(); return; }
  jumpTo(c, r, zWant || clamp(cam.z, 0.78, 1.25), 0, 340);
  pwait(400, cb, true);
}
/* 싸움 장면용: 충분히 가까이(확대 1.3 이상) 보이게 한 뒤 cb */
function focusNear(c, r, cb) {
  var P = UI.play;
  if (P && P.skip) { cb(); return; }
  if (onScreen(c, r, 40) && cam.z >= 1.3) { cb(); return; }
  jumpTo(c, r, 1.6, 0, 340);
  pwait(400, cb, true);
}
function startPlayback() {
  saveGame();                                             // 재생 도중 창을 닫아도 '턴 종료 직전'으로 돌아오게
  var P = UI.play = { next: null, skip: UI.pspeed === 0, cam0: { x: cam.x, y: cam.y, z: cam.z }, timer: 0, wake: null, ans: [], batch: [], err: null, minor: 0, shown: 0, save0: null };
  try { P.save0 = serialize(); } catch (e) { P.save0 = null; }
  UI.busy = true; REPORT = []; EVQ = [];
  hideSheet(); $('app').classList.add('playing');
  $('plSpeed').textContent = '속도: ' + SPEEDS[UI.pspeed || 1][0];
  setCaption(G.player, '턴을 마칩니다 — <b>열흘</b>이 흐릅니다');
  requestDraw();
  var go = pg(function () { playMarch(pg(function () { EVQ.length = 0; P.next = turnStepper(); pump(); })); });
  if (P.skip) { $('veil').classList.add('on'); setTimeout(go, 40); } else pwait(420, go);
}
function marchLog(u, name, res) {
  var b;
  if (res.entered !== undefined) { b = G.bases[res.entered]; logMsg(name + ' ' + b.n + ' 입성', b.c, b.r, G.player, 1); }
  else if (res.captured !== undefined) { /* 차지한 일은 규칙 쪽에서 이미 기록한다 */ }
  else if (res.dead) logMsg(name + ' 불길 속에서 흩어짐', res.from[0], res.from[1], G.player, 2);
  else if (res.front !== undefined) { b = G.bases[res.front]; logMsg(name + ' ' + b.n + ' 앞에 도착 — 공격 명령을 내리세요', b.c, b.r, G.player, 2); }
  else if (alive(u) && u.dest < 0) logMsg(name + ' 목적지에 도착', u.c, u.r, G.player, 1);
}
/* 1) 행군 중인 내 부대: 한 부대씩 한 구간 */
function playMarch(done) {
  var P = UI.play, us = marchList(G.player), i = 0;
  var step = pg(function () {
    while (i < us.length) {
      var u = us[i++];
      if (!alive(u) || u.done || u.dest < 0) continue;
      var name = uName(u), dn = destName(u.dest), vis = unitVis(u), o = R3.units[u.id];
      var res = unitMarch(u);
      if (!res) continue;
      if (!res.ok) {
        if (res.front !== undefined) logMsg(name + ' ' + G.bases[res.front].n + ' 앞에 도착 — 공격 명령을 내리세요', u.c, u.r, G.player, 2);
        else if (res.lost) logMsg(name + ' 길이 막혀 행군을 멈춤', u.c, u.r, G.player, 1);
        continue;
      }
      marchLog(u, name, res);
      if (P.skip || !o) continue;
      o.anim = true;                                     // 연출이 시작될 때까지 제자리에 둔다
      P.shown++;
      playMarchShow(name, dn, vis, res, step);
      return;
    }
    done();
  });
  step();
}
function playMarchShow(name, dn, vis, res, next) {
  var P = UI.play, mid = res.path[Math.floor(res.path.length / 2)], mc = mid % W;
  focus(mc, (mid - mc) / W, pg(function () {
    var tail = res.entered !== undefined ? ' — <b>' + G.bases[res.entered].n + '</b> 입성' : (res.captured !== undefined ? ' — <b>' + G.bases[res.captured].n + '</b> 점령!' : (res.front !== undefined ? ' — <b>' + G.bases[res.front].n + '</b> 앞에 도착' : ''));
    setCaption(G.player, '<b>' + name + '</b> ' + dn + ' 방면으로 행군' + tail);
    animMove(vis, res.from, res.path, pg(function () {
      P.ans = []; if (res.captured !== undefined) { sfx('fall'); sfx('cheerlate'); fxFall(G.bases[res.captured], '점령'); }
      requestDraw(); pwait(tail ? 800 : 240, next);
    }), 1.2 * spdK());
    P.ans = [UI.anims[UI.anims.length - 1]];
  }));
}
/* 2)~3) 다른 세력의 차례를 한 단계씩 돌리며 보여 줄 것만 골라 보여 준다 */
function nearMine(c, r, d) {
  var i, f = G.player;
  for (i = 0; i < G.bases.length; i++) if (G.bases[i].owner === f && hdist(c, r, G.bases[i].c, G.bases[i].r) <= d) return true;
  for (i = 0; i < G.units.length; i++) if (G.units[i].f === f && hdist(c, r, G.units[i].c, G.units[i].r) <= d) return true;
  return false;
}
/* 2 = 나와 직접 관련(천천히) · 1 = 가까운 곳의 일(짧게) · 0 = 보여 주지 않음 */
function evClass(e) {
  if (e.t === 'fall') {
    var fb = G.bases[e.b];
    if (e.old === G.player || e.by === G.player) return 2;
    if (e.old >= 0 && fb.kind === 'city') return 2;                 // 성의 주인이 바뀜: 어디서든 보여 준다
    return nearMine(fb.c, fb.r, 12) ? 1 : 0;                        // 빈 성을 차지했거나 관문: 가까울 때만 짧게
  }
  if (e.t === 'fallen' || e.t === 'news') return 2;
  if (e.t === 'act') return e.tf === G.player ? 2 : (nearMine(e.tc, e.tr, 7) ? 1 : 0);
  if (e.t === 'move') return nearMine(e.c, e.r, 6) ? 1 : 0;
  if (e.t === 'deploy') return nearMine(e.c, e.r, 8) ? 1 : 0;
  return 0;
}
/* 사건에 얽힌 부대 그림을 붙잡아 둔다(규칙 쪽 상태는 이미 앞서가 있으므로) */
function holdEv(e) {
  if (!R3 || !e.cls) return;
  var o;
  if (e.t === 'move') { o = R3.units[e.id]; if (o) o.anim = true; }
  else if (e.t === 'act' && e.res) { o = R3.units[e.res.aid]; if (o) o.anim = true; if (e.res.tid >= 0) { o = R3.units[e.res.tid]; if (o) o.anim = true; } }
}
function pump() {
  var P = UI.play;
  for (;;) {
    var s = P.next(), evs = EVQ.splice(0, EVQ.length), show = [], i, e, big = false, onlyMoves = false;
    if (P.skip) { P.batch = []; if (!s) { finishPlayback(); return; } continue; }
    if (s) {
      for (i = 0; i < evs.length; i++) { evs[i].cls = evClass(evs[i]); if (evs[i].cls === 2) big = true; }
      for (i = 0; i < evs.length; i++) holdEv(evs[i]);          // 보여 줄 때까지 그림을 지금 모습 그대로 둔다
      for (i = 0; i < evs.length; i++) {
        e = evs[i];
        if (e.cls === 2 || (e.cls === 1 && (big || P.minor < 16))) { show.push(e); if (e.cls === 1 && !big) P.minor++; }
      }
      if (!show.length && s.kind !== 'round') continue;
      onlyMoves = show.length > 0 && show.every(function (x) { return x.t === 'move' && x.cls === 1; });
      if (onlyMoves && P.batch.length < 4 && (!P.batch.length || P.batch[0].f === show[0].f) && !P.batch.some(function (b) { return show.some(function (x) { return x.id === b.id; }); })) { P.batch = P.batch.concat(show); continue; }
    }
    pumpShow(s, show, onlyMoves);
    return;
  }
}
/* 모아 둔 이동을 먼저 보여 주고, 이어서 이번 단계의 장면을 보여 준다 */
function pumpShow(s, show, onlyMoves) {
  var P = UI.play;
  var after = pg(function () {
    if (!s) { finishPlayback(); return; }
    if (s.kind === 'round') { presentRound(pg(pump)); return; }
    if (onlyMoves) { P.batch = show; pump(); return; }
    if (show.length) presentEvents(show, pg(pump)); else pump();
  });
  if (P.batch.length) { var b = P.batch; P.batch = []; presentMoves(b, after); } else after();
}
function presentMoves(evs, done) {
  var P = UI.play, live = [], names = [], i;
  for (i = 0; i < evs.length; i++) { var o = R3.units[evs[i].id]; if (o) { o.anim = true; live.push(evs[i]); if (names.length < 3) names.push(evs[i].n); } }
  if (!live.length) { done(); return; }
  P.shown += live.length;
  var e0 = live[0];
  focus(e0.c, e0.r, pg(function () {
    var tail = live.length === 1 && e0.into !== undefined ? G.bases[e0.into].n + (G.bases[e0.into].owner === e0.f ? ' 입성' : ' 점령') : '이동';
    setCaption(e0.f, '<b>' + names.join(' · ') + '</b>' + (live.length > names.length ? ' 등 ' + live.length + '개 부대' : '') + ' ' + tail);
    var left = live.length, n0 = UI.anims.length;
    for (var j = 0; j < live.length; j++) animMove({ id: live[j].id }, live[j].from, live[j].path, pg(function () { if (--left > 0) return; P.ans = []; requestDraw(); pwait(160, done); }), 0.8 * spdK());
    P.ans = UI.anims.slice(n0);
  }));
}
function presentEvents(evs, done) {
  var P = UI.play, i;
  for (i = 0; i < evs.length; i++) holdEv(evs[i]);
  syncScene();                                             // 새로 나온 부대를 만들고, 움직일 부대는 출발점에 둔 채로
  for (i = 0; i < evs.length; i++) if (evs[i].t === 'deploy') {   // 막 출진한 부대는 성 앞 칸에 세워 둔다(뒤따르는 이동은 거기서 시작)
    var od = R3.units[evs[i].id];
    if (od && !od.held) { od.anim = true; od.held = true; fxPut(od, hexPos(evs[i].c, evs[i].r)); }
  }
  i = 0;
  var one = pg(function () {
    if (P.skip || i >= evs.length) { clearAnimFlags(); requestDraw(); done(); return; }
    P.shown++;
    presentEvent(evs[i++], one);
  });
  one();
}
function presentEvent(e, cb) {
  var P = UI.play, b, k = e.cls === 2 ? 1 : 0.45;
  if (e.t === 'move') {
    var o = R3.units[e.id];
    if (!o) { cb(); return; }
    focus(e.c, e.r, pg(function () {
      setCaption(e.f, '<b>' + e.n + '</b> ' + (e.into !== undefined ? G.bases[e.into].n + (G.bases[e.into].owner === e.f ? ' 입성' : ' 점령') : '이동'));
      animMove({ id: e.id }, e.from, e.path, pg(function () { P.ans = []; requestDraw(); pwait(140, cb); }), 0.8 * spdK());
      P.ans = [UI.anims[UI.anims.length - 1]];
    }));
  } else if (e.t === 'act') {
    if ((e.f === G.player || e.tf === G.player) && UI.battleTurn !== G.turn) { UI.battleTurn = G.turn; playBgm('battle'); }   // 내가 얽힌 싸움이면 전투 음악으로
    focusNear(e.tc, e.tr, pg(function () {
      setCaption(e.f, resultMsg(e.name, e.res), e.tf === G.player ? 'hit' : '');
      var n0 = UI.anims.length;
      animAct(e.res, pg(function () { P.ans = []; requestDraw(); pwait((e.res.fell ? 200 : 700) * k, cb); }), function () { resultFx(e.res); });   // 함락이면 바로 뒤에 함락 장면이 따로 나온다
      P.ans = UI.anims.slice(n0);
    }));
  } else if (e.t === 'fall') {
    b = G.bases[e.b];
    focus(b.c, b.r, pg(function () {
      var mine = e.old === G.player;
      setCaption(e.by, e.old < 0 ? '<b>' + josa(facName(e.by) + '군', '이가') + ' 주인 없는 ' + josa(b.n, '을를') + ' 차지</b>' : '<b>' + josa(facName(e.by) + '군', '이가') + ' ' + josa(b.n, '을를') + (b.kind === 'gate' ? ' 점령' : ' 함락') + '!</b> (' + facName(e.old) + '군 → ' + facName(e.by) + '군)' + (mine ? '<br>우리 거점을 잃었습니다' : ''), mine ? 'hit' : 'big');
      sfx('fall'); if (e.by === G.player) sfx('cheerlate');
      fxFall(b, e.old < 0 || b.kind === 'gate' ? '점령' : '함락');
      requestDraw(); pwait(2000 * k, cb);
    }), 0.8);
  } else if (e.t === 'deploy') {
    focus(e.c, e.r, pg(function () {
      setCaption(e.f, G.bases[e.base].n + '에서 <b>' + e.n + '</b> 출진');
      sfx('drums');
      var odp = R3.units[e.id], bb = G.bases[e.base];
      if (odp && bb) {                                           // 성에서 걸어 나온다(뒤따르는 이동 장면을 위해 붙잡아 둔 채로)
        var q0 = hexPos(bb.c, bb.r), q1 = hexPos(e.c, e.r);
        anim(420, function (t) { var w = 1 - (1 - t) * (1 - t), px = q0[0] + (q1[0] - q0[0]) * w, pz = q0[2] + (q1[2] - q0[2]) * w; fxPut(odp, [px, groundY(px, pz) + Math.sin(Math.PI * t) * 0.16, pz]); });
        P.ans = [UI.anims[UI.anims.length - 1]];
      }
      pwait(640, cb);
    }));
  } else if (e.t === 'news') {
    focus(e.c, e.r, pg(function () {
      setCaption(e.f, e.text, e.warn ? 'hit' : '');
      flashHex(e.c, e.r, '#b5332a'); sfx('drum');
      requestDraw(); pwait(1900, cb);
    }));
  } else if (e.t === 'fallen') {
    setCaption(-1, '<b>' + facName(e.f) + '군 멸망</b>', 'big'); sfx('gong');
    pwait(1800, cb);
  } else cb();
}
function presentRound(cb) {
  refreshHud(); requestDraw();
  showBanner(dateStr(), '열흘이 지났습니다');
  setCaption(G.player, '<b>' + dateStr() + '</b> — 새 턴이 시작됩니다');
  sfx('gong');
  pwait(1000, function () { hideBanner(); cb(); });
}
function finishPlayback() {
  var P = UI.play; if (!P) return;
  UI.play = null; clearTimeout(P.timer);
  clearAnimFlags(); UI.hide = -1; UI.busy = false; EVQ.length = 0;
  hideBanner(); $('veil').classList.remove('on'); $('app').classList.remove('playing');
  if (P.err) toast('오류가 발생했습니다: ' + P.err.message, 6000);
  sfxMoveStop(); sfx('drum'); saveGame(); refreshHud();
  if (P.shown) jumpBack(P.cam0);
  showHome(); requestDraw();
  if (G.over) { showGameOver(); return; }
  playBgm(bgmForState());
  showReport(REPORT);
}
function jumpBack(c0) {
  var x0 = cam.x, y0 = cam.y, z0 = cam.z;
  anim(380, function (t) { var e = t * (2 - t); cam.x = x0 + (c0.x - x0) * e; cam.y = y0 + (c0.y - y0) * e; cam.z = z0 + (c0.z - z0) * e; clampCam(); });
}
/* 4) 요약: 중요한 일 → 우리 세력 → 천하 */
function showReport(list) {
  var secs = [['중요한 일', []], ['우리 세력', []], ['천하의 움직임', []]], i, n = 0;
  for (i = 0; i < list.length; i++) {
    var e = list[i]; if (e.imp < 1) continue;
    secs[e.imp >= 2 ? 0 : (e.f === G.player ? 1 : 2)][1].push(i); n++;
  }
  if (!n) { toast(dateStr() + ' — 새 턴입니다. 지난 열흘은 조용했습니다', 2600); return; }
  clearRet();
  showDialog({
    render: function () {
      var h = dlgHead('지난 열흘의 일') + '<div class="dlg-b"><div class="rep-date">' + dateStr() + '<small>' + n + '건 · 줄을 누르면 그곳을 보여 줍니다</small></div>';
      for (var s = 0; s < 3; s++) {
        var ids = secs[s][1]; if (!ids.length) continue;
        h += '<div class="sec">' + secs[s][0] + '</div><div class="rows">';
        for (var j = 0; j < ids.length; j++) { var x = list[ids[j]]; h += '<button class="row rep' + (x.imp >= 3 ? ' top' : (s === 0 ? ' imp' : '')) + '" type="button" data-a="j" data-v="' + ids[j] + '"><span class="mk">' + (x.imp >= 3 ? '★' : (s === 0 ? '●' : '·')) + '</span><span class="mid">' + x.t + '</span>' + (x.c !== undefined ? '<span class="go">▸</span>' : '') + '</button>'; }
        h += '</div>';
      }
      return h + '</div><div class="dlg-f"><div class="pv">이제 <b>' + G.factions[G.player].name + '군</b>의 차례입니다</div><button class="btn pri" type="button" data-a="close">확인</button></div>';
    },
    on: { j: function (el) { var e = list[+el.getAttribute('data-v')]; if (e && e.c !== undefined) jumpFromDialog('지난 열흘의 일', function () { clearSel(); jumpTo(e.c, e.r, Math.max(cam.z, 0.8)); flashHex(e.c, e.r, '#b5332a'); }); } }
  });
}
function nextUnit() {
  var us = pendingUnits();
  if (!us.length) us = facUnits(G.player).filter(function (u) { return !u.done; });
  if (!us.length) { toast('움직일 부대가 없습니다'); return; }
  var cur = UI.sel && UI.sel.kind === 'unit' ? UI.sel.id : -1, i = 0;
  for (var j = 0; j < us.length; j++) if (us[j].id === cur) i = (j + 1) % us.length;
  gotoUnit(us[i]);
}
function showGameOver() {
  dropSave();
  var win = G.over === 'win';
  playBgm(win ? 'victory' : 'defeat', true);
  showDialog({
    render: function () {
      return '<div class="dlg-h"><h2>' + (win ? '천하통일' : '패망') + '</h2></div><div class="dlg-b"><p>' + (win ? dateStr() + ', ' + josa(G.factions[G.player].name, '이가') + ' 천하를 하나로 만들었습니다.' : dateStr() + ', ' + G.factions[G.player].name + ' 세력은 역사 속으로 사라졌습니다.') + '</p></div>' +
        '<div class="dlg-f"><div class="pv">' + fmt(G.turn * 10) + '일째</div><button class="btn pri" type="button" data-a="t">처음으로</button></div>';
    },
    lock: true,                                                    // 바깥을 눌러도 닫히지 않는다(닫히면 끝난 판에 갇힌다)
    on: { t: function () { closeDialog(); G = null; UI.ret = null; hideSheet(); showTitle(); playBgm('title'); } }
  });
}

/* ---------- 시작 ---------- */
function showTitle() {
  $('title').classList.remove('off');
  $('tCont').disabled = !hasSave();
  $('tVer').textContent = GAME_VERSION + ' · 194년 군웅할거';
}
function startGame() {
  $('title').classList.add('off');
  resize();
  var L = off(G.factions[G.player].lord), b = L.unit !== null ? UMAP[L.unit] : G.bases[L.loc];
  var p = hexCenter(b.c, b.r);
  cam.x = p[0]; cam.y = p[1] + 4; cam.z = 0.9; clampCam();
  UI.battleTurn = undefined; UI.sel = null; UI.rc = null; UI.atk = null; UI.target = null; UI.march = null; UI.ret = null; UI.via = false; UI.sret = null; MSTACK.length = 0; paintRet();
  refreshHud(); showHome(); requestDraw(); playBgm(bgmForState());
}
function showFactionSelect() {
  var st = { f: -1 };
  var info = SCENARIO.factions.map(function (sf, i) {
    var os = SCENARIO.officers.filter(function (o) { return o.f === i; }), lord = null;
    os.forEach(function (o) { if (o.n === sf.n) lord = o; });
    return { i: i, n: sf.n, color: sf.color, cities: sf.cities, cnt: os.length, lord: lord };
  });
  showDialog({
    render: function () {
      var h = dlgHead('194년 군웅할거 — 군주를 고르세요') + '<div class="dlg-b"><div class="rows">';
      for (var i = 0; i < info.length; i++) {
        var x = info[i];
        h += '<button class="row' + (st.f === x.i ? ' sel' : '') + '" type="button" data-a="f" data-v="' + x.i + '">' + porTag(x.lord) + '<span class="mid"><span class="nm">' + x.n + ' <span class="chip" style="background:' + x.color + '">' + x.cities.join('·') + '</span></span><span class="ds" style="white-space:normal">' + FACTION_DESC[x.n] + '</span></span><span class="rt">무장<br><b>' + x.cnt + '</b></span></button>';
      }
      return h + '</div></div><div class="dlg-f"><div class="pv">' + (st.f >= 0 ? '<b>' + info[st.f].n + '</b> · 도시 ' + info[st.f].cities.length + ' · 무장 ' + info[st.f].cnt + '명' : '세력을 누르면 선택됩니다') + '</div><button class="btn pri" type="button" data-a="go"' + (st.f < 0 ? ' disabled' : '') + '>시작</button></div>';
    },
    on: {
      f: function (el) { st.f = +el.getAttribute('data-v'); refreshDialog(); },
      go: function () { if (st.f < 0) return; closeDialog(); newGame(st.f); startGame(); sfx('gong'); showIntro(); }
    }
  });
}
function showIntro() {
  var F = G.factions[G.player], L = off(F.lord);
  showDialog({
    render: function () {
      return dlgHead(dateStr() + ' — ' + F.name) + '<div class="dlg-b"><div class="card">' + sceneTag(L) + '<div><p>' + FACTION_DESC[F.name] + '</p></div></div><div class="help"><ul>' +
        '<li><b>도시</b>를 누르면 내정·군사·인재 명령이 열립니다. 도시 둘레 <b>밝은 칸</b>에 시설을 짓습니다.</li>' +
        '<li>무장을 고를 때 <b>자동</b>을 누르면 그 일을 가장 잘하는 무장을 골라 줍니다.</li>' +
        '<li>화면 아래 <b>STATUS 창</b>의 <b>지금 할 일</b>을 위에서부터 누르면 됩니다.</li>' +
        '<li><b>군사 → 출진</b>으로 부대를 성 앞에 내보낸 뒤, <b>파란 칸</b>을 눌러 움직이고 <b>적</b>을 눌러 공격합니다. 이웃 성까지는 적어도 30일이 걸립니다.</li>' +
        '<li>명령은 <b>행동력</b>을 씁니다. 할 일을 마치면 <b>턴 종료</b> — 열흘 동안 일어난 일을 차례로 보여 줍니다.</li>' +
        '<li>자세한 규칙은 메뉴 → 도움말에 있습니다.</li></ul></div></div><div class="dlg-f"><div class="pv">도시 42곳을 모두 차지하면 천하통일</div><button class="btn pri" type="button" data-a="close">시작</button></div>';
    }, on: {}
  });
}
function boot(data) {
  loadOpts();
  try { init3d(); } catch (e) { document.body.innerHTML = '<p style="padding:24px;color:#1b1a18;font:16px sans-serif">이 기기에서는 3D 지도를 그릴 수 없습니다(WebGL을 쓸 수 없음).<br>' + e.message + '</p>'; return; }
  loadAssets(); initInput(); resize();
  delegate($('sheet'), function () { return SHEET; }, function () { backSheet(); });
  delegate($('modal'), function () { return MODAL; }, function () { backDialog(); });
  $('btnEnd').addEventListener('click', function () { audioInit(); doEndTurn(); });
  $('hud').addEventListener('click', function () { if (!G || G.over || UI.busy || UI.play || MODAL) return; audioInit(); sfx('ui'); HOME.open = true; saveOpts(); clearSel(); });
  $('play').addEventListener('click', function () { playNudge(); });
  $('plSkip').addEventListener('click', function (e) { e.stopPropagation(); sfx('ui'); playSkip(); });
  $('plSpeed').addEventListener('click', function (e) { e.stopPropagation(); sfx('ui'); UI.pspeed = UI.pspeed % 3 + 1; saveOpts(); $('plSpeed').textContent = '속도: ' + SPEEDS[UI.pspeed][0]; });
  $('btnNext').addEventListener('click', function () { audioInit(); sfx('ui'); nextUnit(); });
  $('btnList').addEventListener('click', function () { audioInit(); sfx('ui'); if (G) showLists(); });
  $('btnLog').addEventListener('click', function () { audioInit(); sfx('ui'); if (G) showLog(G.log, '기록'); });
  $('btnMenu').addEventListener('click', function () { audioInit(); sfx('ui'); if (G) showMenu(); });
  $('ret').addEventListener('click', function () { if (!G || G.over || UI.busy || UI.play || MODAL) return; audioInit(); sfx('ui'); goRet(); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (MODAL) { backDialog(); return; }
    if (G && !G.over && !UI.busy && !UI.play && SHEET && !SHEET.home) backSheet();
  });
  $('tNew').addEventListener('click', function () { audioInit(); playBgm('title'); sfx('ui'); showFactionSelect(); });
  $('tCont').addEventListener('click', function () { audioInit(); if (loadGame()) { startGame(); toast(dateStr() + ' — 이어서 합니다'); } else toast('저장된 게임이 없습니다'); });
  $('tHelp').addEventListener('click', function () { audioInit(); playBgm('title'); showHelp(); });
  document.addEventListener('visibilitychange', function () { if (document.hidden) saveGame(); });
  if (data && data.save && deserialize(data.save)) startGame(); else { showTitle(); BGM.want = 'title'; }
  requestAnimationFrame(tick);
}
(function () {
  var hot = window.claude && window.claude.hot;
  if (hot && hot.snapshot) hot.snapshot(function () { return { save: (G && !G.over) ? (UI.play ? UI.play.save0 : serialize()) : null }; });
  // three.js는 허용된 CDN에서 불러온다. 첫 주소가 막히면 같은 파일을 다른 곳에서 차례로 받는다.
  var ALT = ['https://cdn.jsdelivr.net/npm/three@0.149.0/build/three.min.js', 'https://unpkg.com/three@0.149.0/build/three.min.js'];
  function start() { if (hot && hot.ready) hot.ready(boot); else boot((hot && hot.data) || {}); }
  function need() {
    if (window.THREE) { start(); return; }
    var u = ALT.shift();
    if (!u) { document.body.innerHTML = '<p style="padding:24px;color:#1b1a18;font:16px/1.6 sans-serif">3D 지도 라이브러리(three.js)를 불러오지 못했습니다.<br>네트워크 연결을 확인하고 다시 열어 주세요.</p>'; return; }
    var s = document.createElement('script'); s.src = u; s.onload = need; s.onerror = need; document.head.appendChild(s);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', need); else need();
})();
