# v0.18.1 — ① 수송을 마친 무장: 머물지 · 돌아올지를 고른다   ② '지금 할 일'의 군사 예측 표시(○ · ×)가 둥근 숫자 배지처럼 크게 그려지던 것
#   ① 그동안: 수송대가 아군 거점에 들어가면 호송 무장은 그 거점에 머물렀다(돌려보내려면 다음 턴에 [이동]으로 따로 명령).
#      이제: 수송 창에서 '짐을 내린 뒤 — 그곳에 머문다 | 돌아온다'를 고른다(u.back). 가는 길에도 부대 창에서 바꿀 수 있다.
#        · 돌아온다 + 아군 거점에 들어감 → 실은 것은 그 거점에 합쳐지고, 무장은 떠나온 거점으로 걸어서 돌아간다(이동 명령과 같은 날수, 행동력은 들지 않는다).
#        · 돌아온다 + 부대에 [보급]      → 그 수송대는 떠나온 거점으로 행군한다(u.dest). 더 나눠 줄 것이 있으면 [행군 취소].
#        · 떠나온 거점을 잃었으면, 또는 들어간 곳이 떠나온 거점이면 머문다. 빈 거점을 차지한 때도 머문다.
#        · [귀환]: 수송대를 지금 떠나온 거점으로 행군시키는 단추(떠나온 거점의 바로 옆에서는 내지 않는다).
#      AI와 군단은 쓰지 않는다(전과 같다). 저장 형식은 그대로(부대에 back 이 붙을 뿐).
#   ② .todo .n(왼쪽의 둥근 숫자 배지)이 풀이 글 속의 <i class="adv n">×</i> 에도 걸렸다 → .todo > .n 으로. 표시는 기호 대신 말로(응할 듯 · 오늘은 불응 …).
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

# ───────────────────────── data.js ─────────────────────────
s = rd('src/data.js')
s = rep(s, "var GAME_VERSION = 'v0.18';", "var GAME_VERSION = 'v0.18.1';")
wr('src/data.js', s)

# ───────────────────────── core.js ─────────────────────────
s = rd('src/core.js')
s = rep(s, """function enterBase(u, b) {
  var nt = b.troops + u.troops;""", """/* v0.18.1: 짐을 내리면 돌아가기로 한 수송대(u.back)가 돌아갈 거점 — 떠나온 거점(u.home)이 아직 제 것이고, 지금 들어가는 곳(b)이 아닐 때. 아니면 null(머문다) */
function transHome(u, b) { if (!u || u.type !== 'trans' || !u.back) return null; var hb = G.bases[u.home]; return (hb && hb.owner === u.f && (!b || hb.id !== b.id)) ? hb : null; }
function transSetBack(u, on) { if (!u || u.type !== 'trans') return false; if (on) u.back = true; else delete u.back; return true; }
/* viaMove = 걸어서 아군 거점에 들어간 것(unitMove). 그때만 돌아가는 수송대의 무장이 길을 떠난다 → { to: 거점, turns } (빈 거점을 차지한 때는 머문다) */
function enterBase(u, b, viaMove) {
  var nt = b.troops + u.troops;""")
s = rep(s, """  for (var i = 0; i < u.off.length; i++) { var o = off(u.off[i]); o.unit = null; o.loc = b.id; o.acted = true; }
  removeUnit(u);
}""", """  var hb = viaMove ? transHome(u, b) : null, bt = hb ? travelTurns(b, hb) : 0;
  for (var i = 0; i < u.off.length; i++) { var o = off(u.off[i]); o.unit = null; o.loc = b.id; o.acted = true; if (hb) { o.st = 'travel'; o.dest = hb.id; o.eta = bt; } }
  removeUnit(u);
  return hb ? { to: hb.id, turns: bt } : null;
}""")
s = rep(s, """    if (b.owner === u.f) { enterBase(u, b); return { ok: true, path: path, from: from, entered: b.id }; }""",
        """    if (b.owner === u.f) { var bk = enterBase(u, b, true), er = { ok: true, path: path, from: from, entered: b.id }; if (bk) er.back = bk; return er; }""")
s = rep(s, """  for (var i = 0; i < os.length; i++) { os[i].unit = u.id; os[i].acted = true; }
  u.mp = uMaxMp(u);""", """  for (var i = 0; i < os.length; i++) { os[i].unit = u.id; os[i].acted = true; }
  if (spec.type === 'trans' && spec.back) u.back = true;       // v0.18.1: 짐을 내리면 돌아온다
  u.mp = uMaxMp(u);""")
s = rep(s, """  t.done = true; t.ox = -1;
  return { ok: true, food: food, troops: troops };
}""", """  t.done = true; t.ox = -1;
  var sr = { ok: true, food: food, troops: troops }, hb = transHome(t, null);
  if (hb) { t.dest = K(hb.c, hb.r); if (t.aim) delete t.aim; sr.home = hb.id; }      // v0.18.1: 돌아가기로 한 수송대는 보급을 마치면 떠나온 거점으로 행군한다
  return sr;
}""")
wr('src/core.js', s)

# ───────────────────────── ui_panels.js ─────────────────────────
s = rd('src/ui_panels.js')
# ② 풀이 글의 표시를 말로
s = rep(s, """tip = t.n + ' 등용 <i class="adv y">○</i>'; say = L === 2 ? b.n + '의 ' + kindN""", """tip = t.n + ' 등용 <i class="adv y">응할 듯</i>'; say = L === 2 ? b.n + '의 ' + kindN""")
s = rep(s, """tip = kindN + ' ' + x.ts.length + '명 <i class="adv n">×</i>';""", """tip = kindN + ' ' + x.ts.length + '명 <i class="adv n">오늘은 불응</i>';""")
s = rep(s, """tip = L === 0 ? '이웃 무장 등용' : t.n + ' 등용 <i class="adv y">○</i>';""", """tip = L === 0 ? '이웃 무장 등용' : t.n + ' 등용 <i class="adv y">응할 듯</i>';""")
s = rep(s, """tip = '탐색 <i class="adv y">○</i>';""", """tip = '탐색 <i class="adv y">만날 듯</i>';""")
s = rep(s, """tip = '숨은 인재 <i class="adv n">×</i>';""", """tip = '숨은 인재 <i class="adv n">오늘은 못 만남</i>';""")

# ① 들어갔을 때의 말
s = rep(s, """function marchDone(x, res, say) {                            // 행군의 한 구간이 끝난 뒤(명령을 내린 직후)
  if (res && res.ok && res.entered !== undefined) { toast(G.bases[res.entered].n + ' 입성'); selectBase(G.bases[res.entered]); }""",
        """/* v0.18.1: 거점에 들어갔을 때의 한마디 — 돌아가기로 한 수송대면 무장이 어디로 며칠 걸려 돌아가는지 */
function backSay(res) { return res && res.back ? ' · 무장은 ' + euro(G.bases[res.back.to].n) + ' 돌아갑니다(' + days(res.back.turns) + ')' : ''; }
function enterToast(res) { var bn = G.bases[res.entered].n; if (res.back) toast(bn + '에 짐을 내림' + backSay(res), 3400); else toast(bn + ' 입성'); }
function transHomeOf(x) { var hb = x && x.type === 'trans' ? G.bases[x.home] : null; return hb && hb.owner === x.f ? hb : null; }
function tbackBtn(x) { var hb = transHomeOf(x), on = !!(x.back && hb); return '<button class="act tbk' + (on ? ' on' : '') + '" type="button" data-a="tback"><b>짐 내린 뒤</b><small>' + (on ? euro(hb.n) + ' 돌아옴' : '그곳에 머묾') + '</small></button>'; }
function gohomeBtn(x) { var hb = transHomeOf(x); return hb && x.dest !== K(hb.c, hb.r) && hdist(x.c, x.r, hb.c, hb.r) > 1 ? '<button class="act" type="button" data-a="gohome"><b>귀환</b><small>' + euro(hb.n) + ' 행군</small></button>' : ''; }
function marchDone(x, res, say) {                            // 행군의 한 구간이 끝난 뒤(명령을 내린 직후)
  if (res && res.ok && res.entered !== undefined) { enterToast(res); selectBase(G.bases[res.entered]); }""")
s = rep(s, """    if (res.entered !== undefined) { toast(G.bases[res.entered].n + ' 입성'); selectBase(G.bases[res.entered]); }
    else if (res.captured !== undefined) { sfx('fall'); sfx('cheerlate'); fxFall(G.bases[res.captured], '점령'); toast(G.bases[res.captured].n + ' 점령!'); selectBase(G.bases[res.captured]); }
    else if (res.dead) { toast('불길 속에서 부대가 흩어졌습니다'); clearSel(); }""",
        """    if (res.entered !== undefined) { enterToast(res); selectBase(G.bases[res.entered]); }
    else if (res.captured !== undefined) { sfx('fall'); sfx('cheerlate'); fxFall(G.bases[res.captured], '점령'); toast(G.bases[res.captured].n + ' 점령!'); selectBase(G.bases[res.captured]); }
    else if (res.dead) { toast('불길 속에서 부대가 흩어졌습니다'); clearSel(); }""")
s = rep(s, """  if (res.entered !== undefined) { b = G.bases[res.entered]; logMsg(name + ' ' + b.n + ' 입성', b.c, b.r, G.player, 1); }""",
        """  if (res.entered !== undefined) { b = G.bases[res.entered]; logMsg(name + ' ' + b.n + ' 입성' + backSay(res).replace('돌아갑니다', '돌아간다'), b.c, b.r, G.player, 1); }""")
s = rep(s, """    var tail = res.entered !== undefined ? ' — <b>' + G.bases[res.entered].n + '</b> 입성' : (""",
        """    var tail = res.entered !== undefined ? ' — <b>' + G.bases[res.entered].n + '</b> 입성' + backSay(res) : (""")

# ① 부대 창: [짐 내린 뒤] · [귀환]
s = rep(s, """옆의 수송대에서</small></button>' : '')) +
            ((x.dest >= 0 || x.aim) ?""", """옆의 수송대에서</small></button>' : '')) +
            (x.type === 'trans' ? tbackBtn(x) + gohomeBtn(x) : '') +
            ((x.dest >= 0 || x.aim) ?""")
s = rep(s, """(x.type !== 'trans' && supplyPairs(x).length ? '<div class="acts"><button class="act pri" type="button" data-a="supply"><b>보급 받기</b><small>옆의 수송대에서</small></button></div>' : '');""",
        """(x.type !== 'trans' && supplyPairs(x).length ? '<div class="acts"><button class="act pri" type="button" data-a="supply"><b>보급 받기</b><small>옆의 수송대에서</small></button></div>' : '') + (x.type === 'trans' && !x.status ? '<div class="acts">' + tbackBtn(x) + '</div>' : '');""")
s = rep(s, """      supply: function () { var x = UMAP[u.id]; if (x) pickSupply(x); },""",
        """      supply: function () { var x = UMAP[u.id]; if (x) pickSupply(x); },
      tback: function () {                                       // v0.18.1: 짐을 내린 뒤 머물지 · 돌아올지(가는 길에도 바꾼다)
        var x = UMAP[u.id]; if (!x || x.type !== 'trans' || x.f !== G.player) return;
        var hb = transHomeOf(x);
        if (!hb && !x.back) return toast('떠나온 거점이 남의 손에 있어 돌아갈 곳이 없습니다', 2600);
        transSetBack(x, !x.back);
        toast(x.back ? '짐을 내리면 ' + josa(uLeader(x).n, '은는') + ' ' + euro(hb.n) + ' 돌아옵니다' : '짐을 내린 곳에 머뭅니다', 2600); refreshSheet();
      },
      gohome: function () { var x = UMAP[u.id], hb = transHomeOf(x); if (x && hb && !x.done && x.f === G.player) orderMarch(x, hb.c, hb.r); },""")

# ① 보급을 마친 뒤
s = rep(s, """(r.troops ? '병력 ' + fmt(r.troops) + '명' : ''), 3000);""", """(r.troops ? '병력 ' + fmt(r.troops) + '명' : '') + (r.home !== undefined ? ' · 다음 턴부터 ' + euro(G.bases[r.home].n) + ' 돌아갑니다' : ''), r.home !== undefined ? 3800 : 3000);""")

# ① 수송 창
s = rep(s, """bow: 0, horse: 0, ram: 0, at: null }, RO = ringOn(st);""", """bow: 0, horse: 0, ram: 0, at: null, back: !!UI.tback }, RO = ringOn(st);""")
s = rep(s, """cargo: { spear: st.spear, halberd: st.halberd, bow: st.bow, horse: st.horse, ram: st.ram }, at: st.at || undefined });
      if (!r.ok) return toast(r.msg);
      closeDialog(); sfx('drum'); talk(uLeader(r.unit), sayLine(uLeader(r.unit), 'trans'), '수송대 출발 — 거점에 들이거나, 아군 부대 옆에서 [보급]', 3200);""",
        """cargo: { spear: st.spear, halberd: st.halberd, bow: st.bow, horse: st.horse, ram: st.ram }, at: st.at || undefined, back: st.back });
      if (!r.ok) return toast(r.msg);
      closeDialog(); sfx('drum'); talk(uLeader(r.unit), sayLine(uLeader(r.unit), 'trans'), st.back ? '수송대 출발 — 짐을 내리면 ' + euro(b.n) + ' 돌아옵니다' : '수송대 출발 — 거점에 들이거나, 아군 부대 옆에서 [보급]', 3200);""")
s = rep(s, """  on.at = RO.at; on.atauto = RO.atauto;
  showDialog({
    render: function () {
      var h = dlgHead('수송 — ' + b.n)""", """  on.at = RO.at; on.atauto = RO.atauto;
  on.tback = function (el) { st.back = el.getAttribute('data-v') === '1'; UI.tback = st.back; saveOpts(); refreshDialog(); };      // v0.18.1: 고른 것은 다음 수송 창에도 그대로
  showDialog({
    render: function () {
      var h = dlgHead('수송 — ' + b.n)""")
s = rep(s, """      h += deployRing(b, st);
      return h + '<p class="note">군량 80일분은 자동으로 실립니다 · 아군 거점에 들이면 합쳐지고, <b>아군 부대 옆</b>에서는 [보급]으로 병량과 병력을 넘깁니다</p></div>""",
        """      h += '<div class="sec">짐을 내린 뒤 <small>호송 무장은</small></div><div class="seg tbk"><button type="button" data-a="tback" data-v="0"' + (st.back ? '' : ' class="on"') + '>그곳에 머문다</button><button type="button" data-a="tback" data-v="1"' + (st.back ? ' class="on"' : '') + '>' + euro(b.n) + ' 돌아온다</button></div>';
      h += deployRing(b, st);
      return h + '<p class="note">군량 80일분은 자동으로 실립니다 · 아군 거점에 들이면 합쳐지고, <b>아군 부대 옆</b>에서는 [보급]으로 병량과 병력을 넘깁니다' + (st.back ? ' · <b>돌아온다</b>: 거점에 짐을 내린 무장은 걸어서, 부대에 보급한 수송대는 행군으로 돌아옵니다' : '') + '</p></div>""")

# 고른 것을 기억한다
s = rep(s, """voice: UI.voice !== false, pct: !!UI.pct }));""", """voice: UI.voice !== false, pct: !!UI.pct, tback: !!UI.tback }));""")
s = rep(s, """    if (o.pct === true) UI.pct = true;                         // v0.18: 확률을 숫자로(기본은 말)""",
        """    if (o.pct === true) UI.pct = true;                         // v0.18: 확률을 숫자로(기본은 말)
    if (o.tback === true) UI.tback = true;                     // v0.18.1: 수송 창의 '짐을 내린 뒤 돌아온다'""")

# 도움말
s = rep(s, """보급한 수송대는 그 턴의 행동을 마칩니다.</p>' +""", """보급한 수송대는 그 턴의 행동을 마칩니다.</p>' +
  '<p><b>짐을 내린 뒤</b> — 수송 창에서 호송 무장이 <b>그곳에 머물지 · 돌아올지</b>를 고릅니다(가는 길에도 부대 창의 <b>짐 내린 뒤</b>로 바꿉니다). <b>돌아온다</b>면, 아군 거점에 짐을 내린 무장은 떠나온 거점으로 걸어서 돌아오고(무장 [이동]과 같은 날수 · 행동력은 들지 않습니다), 부대에 보급한 수송대는 떠나온 거점으로 행군합니다(더 나눠 줄 것이 있으면 <b>행군 취소</b>). 떠나온 거점을 잃었으면 머뭅니다. 부대 창의 <b>귀환</b>은 수송대를 지금 떠나온 거점으로 행군시킵니다.</p>' +""")
wr('src/ui_panels.js', s)

# ───────────────────────── style.css ─────────────────────────
s = rd('src/style.css')
for a in ('.todo .n {', '.todo .n.num {', '.todo.warn .n { background', '.todo.cool .n {', '.todo.end .n {', '.todo.peace .n {', '.todo.warn .n { font-family', '.todo.advh .n {'):
    s = rep(s, a, a.replace(' .n', ' > .n'))
assert s.count('.todo .n') == 0 and s.count('.todo.warn .n') == 0, 'todo .n left'
s += """
/* v0.18.1 — '지금 할 일'의 풀이 글 속 군사 표시(응할 듯 · 오늘은 불응): 글과 같은 줄, 같은 크기. (왼쪽의 둥근 숫자 배지는 .todo > .n 으로만 잡는다 — 예전에는 .adv.n 도 걸려 크고 둥글게 그려졌다) */
.todo small .adv { margin: 0 0 0 2px; font-weight: 800; }
/* 수송 창: 짐을 내린 뒤 머문다 | 돌아온다 */
.seg.tbk { margin: 2px 0 10px; }
.seg.tbk button { height: 38px; font: 800 13.5px var(--font-body); letter-spacing: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 6px; }
.act.tbk.on small { color: var(--seal); font-weight: 700; }
"""
wr('src/style.css', s)
print('ok')
