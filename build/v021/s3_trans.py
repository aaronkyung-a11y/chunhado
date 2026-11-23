# v0.21 (3) 수송: 갈 곳을 바로 고르고, 수송이 끝났을 때 머물지 · 돌아갈지를 묻는다
#   "수송 시 짐 내린 뒤 라는 말이 이상해. 수송이 완료된 후 정도가 되겠지? 그리고 처음 나올 때 방향을 눌러서 정하기보다 어디로 이동할지를 바로 보여주면 될 것 같아.
#    또한, 수송이 끝난 뒤 남을지 돌아올지에 대해서는 수송을 시작할 때 물어보지말고 수송 완료 하자마자 물어봐야할 듯"
#   · ②단계가 '내린 뒤 · 나갈 자리'에서 '어디로'가 되었다: 지도에 우리 성(과 들판의 우리 부대)마다 이름과 걸리는 날수가 뜨고, 누르면 그곳으로 간다.
#     나갈 칸은 그 길에 가장 좋은 쪽으로 알아서 잡고, 출발하면 곧바로 행군한다(이번 턴에 갈 수 있는 만큼).
#   · 머물지 · 돌아갈지는 수송이 끝났을 때 묻는다: 수송대가 우리 거점에 들어가면(걸어서) 창이 뜬다 — 턴을 넘기는 사이에 닿았으면 내 차례가 돌아오자마자.
#     부대에 [보급]한 뒤에도 묻는다(남는다 / 떠나온 거점으로 행군).
#   · 말: '짐을 내린 뒤' → '수송을 마친 뒤 / 수송 완료'.
#   규칙 쪽: u.back(출발할 때 정해 둔 '돌아온다')은 남겨 둔다 — 옛 저장의 수송대는 전처럼 묻지 않고 돌아간다. 새로 내는 수송대에는 붙지 않는다.
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

# ---------- 규칙 ----------
s = rd('src/core.js')
s = rep(s, "/* viaMove = 걸어서 아군 거점에 들어간 것(unitMove).", """/* v0.21 수송을 마친 뒤 머물지 · 돌아갈지 — 출발할 때가 아니라 '수송이 끝났을 때' 묻는다.
   G.tdone = [{ k: 'trans', b(들어간 거점), home(떠나온 거점), offs(호송 무장들), turn }] — 내 수송대(직할)가 걸어서 우리 거점에 들어갔을 때 쌓인다(떠나온 거점이 다른 우리 거점일 때만).
   화면이 맨 앞의 것부터 묻고 cmdTransAsk(돌아가는가)로 답한다. 답하지 않은 채 두 턴이 지난 것은 버린다(머문 것으로 본다). */
function transAskPush(u, b) {
  if (G.aiOnly || u.f !== G.player || u.type !== 'trans' || u.corps || u.back) return false;
  var hb = G.bases[u.home]; if (!hb || hb.owner !== u.f || hb.id === b.id) return false;
  G.tdone = (G.tdone || []).filter(function (a) { return G.turn - a.turn < 2; });
  G.tdone.push({ k: 'trans', b: b.id, home: hb.id, offs: u.off.slice(), turn: G.turn });
  return true;
}
function transAskInfo(a) {                                   // 아직 물을 수 있는가 → { b, home, os(그 거점에 머물러 있는 호송 무장), turns } 또는 null
  if (!a || a.k !== 'trans') return null;
  var b = G.bases[a.b], hb = G.bases[a.home];
  if (!b || !hb || b.owner !== G.player || hb.owner !== G.player) return null;
  var os = a.offs.map(off).filter(function (o) { return o && o.f === G.player && o.st === 'active' && o.unit === null && o.loc === b.id; });
  return os.length ? { b: b, home: hb, os: os, turns: travelTurns(b, hb) } : null;
}
function cmdTransAsk(back) {
  var a = G.tdone && G.tdone.shift(), v = transAskInfo(a);
  if (!v) return ERR('물을 것이 없습니다');
  if (!back) return { ok: true, stay: v.b.id, n: v.os.length };
  v.os.forEach(function (o) { o.st = 'travel'; o.dest = v.home.id; o.eta = v.turns; o.acted = true; });
  return { ok: true, back: { to: v.home.id, turns: v.turns }, n: v.os.length };
}
/* 수송의 어림: 거점 b 에서 무장 offId 가 이끄는 수송대가 칸 gk 까지 → { spot: 나갈 칸, turns, goal } 또는 null(길이 없다).
   best = 나갈 수 있는 칸을 모두 견줘 가장 빨리 닿는 쪽(아니면 곧은 거리로 가까운 쪽 하나만 본다 — 목록에 날수를 적을 때) */
function transPlan(b, offId, gk, best) {
  var gc = gk % W, gr = (gk - gc) / W, sp = best ? deploySpots(b) : [deploySpot(b, { c: gc, r: gr })], out = null;
  for (var i = 0; i < sp.length; i++) {
    if (!sp[i]) continue;
    var fu = { c: sp[i][0], r: sp[i][1], f: b.owner, type: 'trans', off: [offId], done: false, mp: 0 }; fu.mp = uMaxMp(fu);
    var here = K(sp[i][0], sp[i][1]) === gk, path = here ? [] : marchPath(fu, gk);
    if (!path) continue;
    var t = here ? 0 : marchTurns(fu, path), sc = t * 1000 + path.length;
    if (!out || sc < out.sc) out = { spot: sp[i], turns: t, goal: gk, sc: sc };
  }
  return out;
}
/* viaMove = 걸어서 아군 거점에 들어간 것(unitMove).""")
s = rep(s, "    if (b.owner === u.f) { var bk = enterBase(u, b, true), er = { ok: true, path: path, from: from, entered: b.id }; if (bk) er.back = bk; return er; }",
           "    if (b.owner === u.f) { var ask = transAskPush(u, b), bk = enterBase(u, b, true), er = { ok: true, path: path, from: from, entered: b.id }; if (bk) er.back = bk; if (ask) er.ask = true; return er; }")
wr('src/core.js', s)

# ---------- 화면 ----------
s = rd('src/ui_panels.js')
s = rep(s, "function enterToast(res) { var bn = G.bases[res.entered].n; if (res.back) toast(bn + '에 짐을 내림' + backSay(res), 3400); else toast(bn + ' 입성'); }",
           """function enterToast(res) { var bn = G.bases[res.entered].n; if (res.back) toast(bn + ' — 수송 완료' + backSay(res), 3400); else toast(bn + (res.ask ? ' — 수송 완료' : ' 입성')); if (res.ask) setTimeout(function () { askNext(); }, 60); }
/* v0.21 수송을 마친 호송 무장: 머물지 · 돌아갈지(G.tdone 의 맨 앞부터). 닫을 수 없는 창 — 둘 가운데 하나를 고른다. then = 다 물은 뒤에 할 일 */
function askNext(then) {
  var v = null;
  while (G && G.tdone && G.tdone.length && !(v = transAskInfo(G.tdone[0]))) G.tdone.shift();
  if (!v || G.over) { if (then) then(); return; }
  if (MODAL) { setTimeout(function () { askNext(then); }, 500); return; }
  var L = v.os[0], who = L.n + (v.os.length > 1 ? ' 외 ' + (v.os.length - 1) + '명' : '');
  function fin() { closeDialog(); refreshSheet(); refreshHud(); requestDraw(); askNext(then); }
  showDialog({
    lock: true, ask: 'trans',
    render: function () {
      return '<div class="dlg-h"><h2>수송 완료 — ' + v.b.n + '</h2></div><div class="dlg-b"><div class="card supc">' + porTag(L, 'md') + '<p><b>' + who + '</b><br><small>실어 온 것을 ' + v.b.n + '에 모두 들였습니다. 이제 어떻게 할까요?</small></p></div></div>' +
        '<div class="dlg-f two"><button class="btn" type="button" data-a="tstay"><b>' + v.b.n + '에 머문다</b></button><button class="btn" type="button" data-a="tgo"><b>' + euro(v.home.n) + ' 돌아간다</b> <small>' + days(v.turns) + '</small></button></div>';
    },
    on: {
      tstay: function () { cmdTransAsk(false); toast(josa(L.n, '은는') + ' ' + v.b.n + '에 머뭅니다', 2200); fin(); },
      tgo: function () { var r = cmdTransAsk(true); if (r.ok && r.back) toast(josa(L.n, '은는') + ' ' + euro(v.home.n) + ' 돌아갑니다 — ' + days(r.back.turns), 2800); fin(); }
    }
  });
}
/* 부대에 보급을 마친 수송대: 남을지 · 떠나온 거점으로 돌아갈지 */
function askSupplyDone(t) {
  var hb = transHomeOf(t);
  if (!t || !alive(t) || !hb || t.f !== G.player || t.corps || t.back) return;
  var L = uLeader(t), path = marchPath(t, K(hb.c, hb.r)); if (!path) return;
  showDialog({
    lock: true, ask: 'supply',
    render: function () {
      return '<div class="dlg-h"><h2>보급 완료</h2></div><div class="dlg-b"><div class="card supc">' + porTag(L, 'md') + '<p><b>' + uName(t) + '</b><br><small>남은 짐 — 병량 ' + fmt(t.food) + ' · 병력 ' + fmt(t.troops) + '명. 이제 어떻게 할까요?</small></p></div></div>' +
        '<div class="dlg-f two"><button class="btn" type="button" data-a="tstay"><b>이곳에 남는다</b></button><button class="btn" type="button" data-a="tgo"><b>' + euro(hb.n) + ' 돌아간다</b> <small>' + days(marchTurns(t, path)) + '</small></button></div>';
    },
    on: {
      tstay: function () { closeDialog(); refreshSheet(); },
      tgo: function () { closeDialog(); if (alive(t)) { if (t.aim) delete t.aim; t.dest = K(hb.c, hb.r); toast(uName(t) + ' — 다음 턴부터 ' + euro(hb.n) + ' 돌아갑니다', 2800); } refreshSheet(); requestDraw(); }
    }
  });
}""")
# 부대 창: '짐 내린 뒤' 단추는 없앤다(끝났을 때 묻는다). 귀환은 그대로
s = rep(s, "(x.type === 'trans' ? tbackBtn(x) + gohomeBtn(x) : '') +", "(x.type === 'trans' ? gohomeBtn(x) : '') +")
# 보급을 마친 뒤
s = rep(s, """        var su = selUnit(); if (su) { UI.rc = unitReach(su); UI.atk = allTargets(su); } else { UI.rc = null; UI.atk = null; }
        refreshSheet(); requestDraw(); afterAction();
      }""", """        var su = selUnit(); if (su) { UI.rc = unitReach(su); UI.atk = allTargets(su); } else { UI.rc = null; UI.atk = null; }
        refreshSheet(); requestDraw(); afterAction();
        if (r.home === undefined) setTimeout(function () { if (!MODAL) askSupplyDone(t); }, 900);      // v0.21: 보급을 마쳤으니 묻는다
      }""")
# 턴을 넘기는 사이에 닿은 수송대: 내 차례가 돌아오자마자 묻고, 그 뒤에 보고
s = rep(s, "  playBgm(bgmForState());\n  showReport(REPORT);\n}", "  playBgm(bgmForState());\n  askNext(function () { showReport(REPORT); });      // v0.21: 수송을 마친 무장이 있으면 먼저 묻는다\n}")

# 수송 창
NEW = r"""function destPick(b, st, D) {
  var bs = facBases(b.owner).filter(function (x) { return x.id !== b.id; }).sort(function (x, y) { return hdist(b.c, b.r, x.c, x.r) - hdist(b.c, b.r, y.c, y.r); });
  var us = G.units.filter(function (u) { return u.f === b.owner && u.type !== 'trans'; }).sort(function (x, y) { return hdist(b.c, b.r, x.c, x.r) - hdist(b.c, b.r, y.c, y.r); });
  var memo = {};
  function all() { return bs.map(function (x) { return { k: 'b', id: x.id, c: x.c, r: x.r, n: x.n }; }).concat(us.filter(function (u) { return UMAP[u.id]; }).map(function (u) { return { k: 'u', id: u.id, c: u.c, r: u.r, n: uName(u) }; })); }
  function same(a, t) { return !!a && !!t && a.k === t.k && a.id === t.id; }
  function goal(t) {                                             // 가서 설 칸: 거점은 그 칸, 부대는 그 옆의 빈 칸 가운데 이 성에서 가까운 곳
    if (t.k === 'b') return K(t.c, t.r);
    var best = -1, bd = 1e9;
    nbrs(t.c, t.r).forEach(function (n) { var k = K(n[0], n[1]), tt = terr(n[0], n[1]); if (tt === 'm' || tt === 's' || tt === 'x' || UAT[k] || BAT[k] !== undefined) return; var d = hdist(n[0], n[1], b.c, b.r); if (d < bd) { bd = d; best = k; } });
    return best;
  }
  function plan(t, best) { var id = t.k + t.id + (best ? '!' : '') + ':' + st.id; if (memo[id] === undefined) { var g = goal(t); memo[id] = g < 0 ? null : transPlan(b, st.id, g, best); } return memo[id]; }
  function eta(p) { return p.turns ? days(p.turns) : '바로 옆'; }
  function marks() {
    var list = [{ c: b.c, r: b.r, cls: 'ex src', html: '<b>' + b.n + '</b><small>여기서</small>', dy: -30 }];
    all().forEach(function (t) { var p = plan(t); list.push({ c: t.c, r: t.r, cls: 'ex' + (same(st.to, t) ? ' on' : '') + (p ? '' : ' no'), html: '<b>' + t.n + '</b><small>' + (p ? eta(p) : '길 없음') + '</small>', dy: -30 }); });
    marksSet(list); requestDraw();
  }
  function pickT(t) {
    if (t.k !== 'x' && !plan(t)) return toast(t.n + ' — 그곳으로 가는 길이 없습니다', 2000);
    st.to = t; sfx('ui'); refreshDialog(); marks();
    var row = document.querySelector('#modal .row.sel'); if (row && row.scrollIntoView) row.scrollIntoView({ block: 'nearest' });
  }
  var P = {
    list: function () { return all().map(function (t) { return { c: t.c, r: t.r, on: same(st.to, t) }; }); },
    has: function (c, r) { return all().some(function (t) { return t.c === c && t.r === r; }); },
    show: marks,
    tap: function (c, r) {
      var t = all().filter(function (x) { return x.c === c && x.r === r; })[0];
      if (!t) return toast(c === b.c && r === b.r ? '떠나는 성입니다 — 다른 우리 성이나 우리 부대를 누르세요' : '우리 성이나 우리 부대를 누르세요(이름이 뜬 곳)', 1800);
      pickT(t);
    }
  };
  return {
    open: function () {
      D.see = true; D.pick = P; if (typeof talkHide === 'function') talkHide(); paintDialog(0);
      var dl = document.querySelector('#modal .dlg'), top = $('hud') ? $('hud').getBoundingClientRect().bottom : 90, bot = dl ? dl.getBoundingClientRect().top : CH * 0.5;
      frameHexes([[b.c, b.r]].concat(all().map(function (t) { return [t.c, t.r]; })), top + 64, bot - 34, 1.1);
    },
    close: function () { D.see = false; D.pick = null; },
    find: function (v) { return v === 'x0' ? { k: 'x', id: 0, n: '성 앞' } : all().filter(function (t) { return t.k + t.id === v; })[0]; },
    pickT: pickT, plan: plan, eta: eta,
    rows: function () {
      var h = '', L = all(), i;
      for (i = 0; i < L.length; i++) {
        var t = L[i], p = plan(t), ds;
        if (t.k === 'b') { var x = G.bases[t.id]; ds = (x.kind === 'city' ? SIZE_NAME[x.sz] : '관문') + ' · 병력 ' + fmt(x.troops) + ' · 병량 ' + fmt(x.food); }
        else { var u = UMAP[t.id]; ds = '들판의 부대 · ' + UNIT_TYPES[u.type].name + ' ' + fmt(u.troops) + '명 · 군량 ' + days(unitFoodTurns(u)) + '분'; }
        h += '<button class="row' + (same(st.to, t) ? ' sel' : '') + (p ? '' : ' dim') + '" type="button" data-a="to" data-v="' + t.k + t.id + '"><span class="mid"><span class="nm">' + t.n + '</span><span class="ds">' + ds + '</span></span><span class="rt"><b>' + (p ? eta(p) : '길 없음') + '</b></span></button>';
      }
      h += '<button class="row' + (st.to && st.to.k === 'x' ? ' sel' : '') + '" type="button" data-a="to" data-v="x0"><span class="mid"><span class="nm">성 앞에 나가 기다린다</span><span class="ds">갈 곳을 정하지 않고 나갑니다 — 부대를 눌러 직접 움직입니다</span></span><span class="rt"><b>—</b></span></button>';
      return h;
    }
  };
}
function flowTransport(b) {
  var cp0 = baseCorps(b);                                       // v0.18: 군단에 맡긴 거점에서도 보낸다(군단장은 자리를 지킨다 · 행동력은 직할의 것 · 나간 수송대는 직할)
  var list = idleOfficers(b).filter(function (o) { return !(cp0 && cp0.lead === o.id); }).sort(function (x, y) { return aiMilScore(x) - aiMilScore(y); });
  if (!list.length) return toast('행동할 수 있는 무장이 없습니다');
  if (b.troops < 100) return toast('호위할 병력이 없습니다');
  var st = { step: 1, id: list[0].id, troops: Math.min(1000, Math.floor(b.troops / 100) * 100), gold: 0, food: 0, spear: 0, halberd: 0, bow: 0, horse: 0, ram: 0, to: null }, D, DP;
  var fs = [['troops', '병력', b.troops, 100], ['gold', '금', b.gold, 50], ['food', '병량', b.food, 500], ['spear', '창', b.w.spear, 100], ['halberd', '극', b.w.halberd, 100], ['bow', '노', b.w.bow, 100], ['horse', '군마', b.w.horse, 100], ['ram', '충차', b.w.ram, 1]];
  function load() { var a = []; fs.forEach(function (f) { if (st[f[0]] > 0) a.push(f[1] + ' ' + fmt(st[f[0]])); }); return a.join(' · '); }
  var on = {
    pick: function (el) { st.id = +el.getAttribute('data-v'); refreshDialog(); },
    auto: function () { var t = autoTeam(b, 'trans', 0); if (t.length) st.id = t[0]; toast('자동 선택', 1500); refreshDialog(); },
    next: function () { st.step = 2; DP.open(); },
    prev: function () { st.step = 1; DP.close(); paintDialog(0); },
    to: function (el) { var t = DP.find(el.getAttribute('data-v')); if (t) DP.pickT(t); },
    ok: function () {
      if (st.step !== 2) return;
      if (!st.to) return toast('갈 곳을 고르세요 — 지도의 우리 성이나 아래 목록', 2000);
      var free = st.to.k === 'x', p = free ? null : (DP.plan(st.to, true) || DP.plan(st.to)); if (!free && !p) return toast('그곳으로 가는 길이 없습니다');
      var need = Math.ceil(st.troops / 20) * 8, tn = st.to.n;
      var r = cmdDeploy(b, { type: 'trans', ids: [st.id], troops: st.troops, food: Math.max(st.food, Math.min(b.food, need)), gold: st.gold, cargo: { spear: st.spear, halberd: st.halberd, bow: st.bow, horse: st.horse, ram: st.ram }, at: p ? p.spot : undefined });
      if (!r.ok) return toast(r.msg);
      closeDialog(); sfx('drum'); talk(uLeader(r.unit), sayLine(uLeader(r.unit), 'trans'), free ? '수송대 출발 — 부대를 눌러 갈 곳을 정하세요' : '수송대 출발 — ' + tn + (p.turns ? ' · 약 ' + days(p.turns) : ''), 3200); syncScene(); selectUnit(r.unit); UI.sret = backToBase(b.id);
      if (free || K(r.unit.c, r.unit.r) === p.goal) { afterAction(); return; }
      orderMarch(r.unit, p.goal % W, (p.goal - p.goal % W) / W);          // 나오자마자 그곳으로 행군(이번 턴에 갈 수 있는 만큼)
    }
  };
  fs.forEach(function (f) { on[f[0]] = function (el) { st[f[0]] = +el.value; $('tv_' + f[0]).textContent = fmt(st[f[0]]); }; });
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
      // ② 어디로(지도에서)
      var free = !!st.to && st.to.k === 'x', p = st.to && !free ? DP.plan(st.to) : null;
      h = dlgHead('수송 — ' + b.n + stepTag(2, 2, '어디로')) + '<div class="dlg-b"><p class="note team">호송 <b>' + off(st.id).n + '</b> · ' + load() + '</p>';
      h += '<p class="note">지도에서 <b>우리 성 · 우리 부대</b>를 누르거나 아래에서 고르세요 — 나오자마자 그곳으로 갑니다. 머물지 · 돌아올지는 <b>수송을 마쳤을 때</b> 묻습니다.</p><div class="rows">' + DP.rows() + '</div></div>';
      return h + '<div class="dlg-f"><button class="btn" type="button" data-a="prev">‹ 짐</button><div class="pv">' + (free ? '<b>성 앞</b> — 직접 움직입니다' : (st.to ? '<b>' + st.to.n + '</b> — ' + (p ? DP.eta(p) : '길 없음') : '갈 곳을 고르세요')) + '</div><button class="btn pri' + (free || (st.to && p) ? '' : ' off') + '" type="button" data-a="ok">출발</button></div>';
    },
    on: on
  };
  DP = destPick(b, st, D);
  showDialog(D);
}

"""
s = cut(s, "function flowTransport(b) {", "/* ---------- 목록·기록·메뉴 ---------- */", NEW)
# 도움말
i = s.index("  '<h3>수송과 보급</h3>"); j = s.index("  '<h3>행군과 공격 명령</h3>")
s = s[:i] + r"""  '<h3>수송과 보급</h3><p>거점의 출진 탭 <b>수송</b>으로 병력·금·병량·무기를 실은 수송대를 냅니다 — ① 호송 무장과 짐 ② <b>어디로</b>: 지도에 우리 성과 들판의 우리 부대마다 이름과 걸리는 날수가 뜹니다. 누르고 [출발]하면 수송대가 그쪽으로 나와 <b>곧바로 행군</b>합니다(턴을 마칠 때마다 한 구간씩 알아서 갑니다). 아군 거점에 들어가면 실은 것이 그 거점에 합쳐집니다. <b>아군 부대의 옆 칸</b>에 가면 부대 창의 <b>보급</b>으로 병량과 병력을 넘길 수 있습니다(받는 부대 쪽에서는 <b>보급 받기</b>). 병력은 받는 주장의 지휘 한도까지이고, 창병·극병·노병·기병에게는 그 무기도 실어 와야 합니다. 보급한 수송대는 그 턴의 행동을 마칩니다.</p>' +
  '<p><b>수송을 마친 뒤</b> — 머물지 · 돌아갈지는 떠날 때가 아니라 <b>수송이 끝났을 때</b> 묻습니다. 수송대가 우리 거점에 들어가면 창이 뜹니다(턴을 넘기는 사이에 닿았으면 내 차례가 돌아오자마자): <b>머문다</b>면 호송 무장은 그 거점에 남고, <b>돌아간다</b>면 떠나온 거점으로 걸어서 돌아갑니다(무장 [이동]과 같은 날수 · 행동력은 들지 않습니다). 부대에 보급한 뒤에도 묻습니다 — 남아서 더 나눠 주거나, 떠나온 거점으로 행군합니다. 떠나온 거점을 잃었으면 묻지 않습니다. 부대 창의 <b>귀환</b>은 수송대를 지금 떠나온 거점으로 행군시킵니다.</p>' +
""" + s[j:]
wr('src/ui_panels.js', s)

s = rd('src/style.css')
s = s.rstrip('\n') + """
/* v0.21 수송 완료 · 보급 완료: 둘 가운데 하나를 고르는 창 */
.dlg-f.two { gap: 10px; }
.dlg-f.two .btn { flex: 1 1 0; min-height: 46px; line-height: 1.25; white-space: normal; }
.dlg-f.two .btn small { display: block; font-size: 11.5px; font-weight: 400; color: var(--dim); }
.btn.pri.off { opacity: .55; }
"""
wr('src/style.css', s)
print('s3 ok')
