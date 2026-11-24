# v0.22 (2) 친 다음에 바뀐다 — 요청 10
#   "공격해서 함락하거나 특기 공격을 하면 결과자리에 먼저 부대가 가 있거나 성 색이 먼저 바뀌거나, 궤멸이 먼저 되어서 사라진 다음에 공격하는데 공격 이후에 효과가 적용되어야하지"
#   까닭: 규칙 쪽 상태는 명령을 내린 순간 끝까지 가 있다(함락 · 궤멸 · 밀려남 · 줄어든 병력). 내 공격은 그 뒤 0.3초 동안 싸움터를 당겨 보이고 나서야 연출을 시작하는데,
#        그 사이에 지도가 새 상태로 다시 그려졌다 — 궤멸한 부대는 지워지고, 성에 들어간 내 부대도 지워지고, 성은 새 주인의 빛깔이 되고, 밀려난 부대는 벌써 밀려나 있었다.
#        (AI 의 차례를 보여 줄 때는 부대만 붙잡아 두었고, 성의 빛깔 · 이름표의 병력 · 불은 붙잡지 않았다.)
#   고친 것: 연출에 얽힌 그림을 연출이 끝날 때까지 지금 모습 그대로 붙잡아 둔다.
#     부대: o.keep (자리 · 이름표 · 빛깔을 고치지 않고, 규칙 쪽에서 사라져도 지우지 않는다) — 친 부대 · 맞은 부대 · 함께 맞은 부대
#     거점: R3.bhold[거점] = 그때의 주인 (이름표 · 성역의 붓 고리 · 시설 · 세력권 · 미니맵을 고치지 않는다) — 맞은 거점 · 시설이 맞은 거점 · 걸어 들어가 차지한 빈 거점
#     불:   R3.fhold[칸] (불길은 불화살 · 화계가 닿은 뒤에 인다)
#   푸는 곳: 공격 연출이 끝날 때(animAct) · 함락 장면(fxFall) · 한 묶음의 장면이 끝날 때(clearAnimFlags) · 아무 연출도 없는데 남아 있으면 곧바로(syncScene 의 안전망)
#   함께: 전법에 함께 맞은 부대(횡소 · 일소 · 관통 …)가 궤멸하면 이제 그 자리에서 흩어지는 모습이 나온다(전에는 연출 전에 지워졌다) — 규칙 쪽 결과에 그 부대의 번호와 생사를 적는다(res.extra[].id · dead).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

# ---------------- core.js: 함께 맞은 부대의 번호 · 생사 ----------------
s = rd('src/core.js')
s = rep(s, """    var ex = { c: o2.c, r: o2.r, dmg: od };
    res.extra.push(ex);
    var dead2 = hurtUnit(o2, od, u.f, u); afterHit(u, o2, od);""", """    var ex = { c: o2.c, r: o2.r, dmg: od, id: o2.id };       // v0.22: id · dead — 화면이 그 부대의 그림을 붙잡아 두었다가 맞는 모습 · 흩어지는 모습을 보인다
    res.extra.push(ex);
    var dead2 = hurtUnit(o2, od, u.f, u); afterHit(u, o2, od);
    if (dead2) ex.dead = true;""")
wr('src/core.js', s)

# ---------------- ui3d.js ----------------
s = rd('src/ui3d.js')
s = rep(s, "bases: [], units: {}, facs: {}, fires: {}, ", "bases: [], units: {}, facs: {}, fires: {}, bhold: {}, fhold: {}, ")
s = rep(s, "function syncScene() {\n  if (!G || !R3.ready) return;\n", """/* ---------- 붙잡아 두기(v0.22) ----------
   규칙 쪽 상태는 명령을 내린 순간 끝까지 가 있다. 그 결과(함락 · 궤멸 · 밀려남 · 줄어든 병력)를 그림에 곧바로 옮기면 치기도 전에 성의 빛깔이 바뀌고 부대가 사라진다.
   그래서 연출에 얽힌 부대 · 거점 · 불은 연출이 끝날 때까지 지금 모습 그대로 둔다.
     부대 o.keep        자리 · 이름표 · 빛깔을 고치지 않는다(o.anim 과 함께 선다 — anim 이 풀리면 keep 도 풀린다). 규칙 쪽에서 사라져도 지우지 않는다
     거점 R3.bhold[id]  = 그때의 주인. 이름표 · 성역의 붓 고리 · 시설 · 세력권 · 미니맵을 고치지 않는다
     불   R3.fhold[칸]  그 칸의 불길을 아직 세우지 않는다
   푸는 곳: animAct 의 끝 · fxFall · clearAnimFlags · (아무 연출도 없는데 남았으면) syncScene */
function keepUnit(id) { var o = (R3 && R3.units) ? R3.units[id] : null; if (o) { o.anim = true; o.keep = true; } return o; }
function keepBase(id, owner) { if (R3 && R3.bhold && id >= 0 && R3.bhold[id] === undefined) R3.bhold[id] = owner; }
function freeBase(id) { if (!R3 || !R3.bhold || R3.bhold[id] === undefined) return; delete R3.bhold[id]; if (R3.bases[id]) R3.bases[id].sig = ''; requestDraw(); }
function ownerShown(b) { var h = (R3 && R3.bhold) ? R3.bhold[b.id] : undefined; return h === undefined ? b.owner : h; }      // 지도에 보이는 주인(붙잡아 둔 동안은 옛 주인)
function keepAct(res, all) {                                 // 행동 하나(공격 · 전법 · 계략)에 얽힌 그림을 붙잡는다. all = 이 행동으로 사라진 부대는 모두(내가 직접 내린 명령 — 함락으로 멸망한 세력의 부대까지)
  if (!R3 || !R3.ready || !res || res.aid === undefined || res.kind === 'challenge') return;
  if (all) for (var gid in R3.units) if (!UMAP[gid]) keepUnit(gid);
  keepUnit(res.aid); if (res.tid >= 0) keepUnit(res.tid);
  if (res.extra) for (var i = 0; i < res.extra.length; i++) if (res.extra[i].id !== undefined) keepUnit(res.extra[i].id);
  if (res.tbase >= 0 && (res.tk === 'base' || res.tk === 'fac')) keepBase(res.tbase, res.tf);
  if (res.c !== undefined && (res.fire || (res.kind === 'ploy' && res.success && res.ploy === '화계'))) R3.fhold[K(res.c, res.r)] = 1;
}
function freeAct(res) {                                      // 그 행동의 연출이 끝났다(함락한 거점은 함락 장면이 푼다)
  if (!R3 || !res) return;
  if (res.tbase >= 0 && !res.fell) freeBase(res.tbase);
  if (res.c !== undefined && R3.fhold[K(res.c, res.r)]) { delete R3.fhold[K(res.c, res.r)]; requestDraw(); }
}
function holdsFree() {                                       // 남은 것을 모두 푼다
  if (!R3) return;
  var k, n = 0;
  for (k in R3.bhold) { delete R3.bhold[k]; if (R3.bases[k]) R3.bases[k].sig = ''; n++; }
  for (k in R3.fhold) { delete R3.fhold[k]; n++; }
  for (k in R3.units) { var o = R3.units[k]; if (o.keep) { o.keep = false; if (o.anim) { o.anim = false; o.c = -1; o.sig = ''; } n++; } }
  if (n) requestDraw();
}
function holdsAny() { var k; if (!R3) return false; for (k in R3.bhold) return true; for (k in R3.fhold) return true; for (k in R3.units) if (R3.units[k].keep) return true; return false; }
function syncScene() {
  if (!G || !R3.ready) return;
  if (!UI.busy && !UI.play && holdsAny()) holdsFree();           // v0.22: 아무 연출도 없는데 붙잡아 둔 것이 남아 있으면(놓친 것) 푼다
""")
# 거점: 붙잡아 둔 동안은 건드리지 않는다
s = rep(s, "    var mineB = b.owner === G.player, col = b.owner >= 0", "    if (R3.bhold[i] !== undefined) continue;                              // v0.22: 연출이 끝날 때까지 지금 모습 그대로(이름표 · 붓 고리 · 시설)\n    var mineB = b.owner === G.player, col = b.owner >= 0")
# 부대
s = rep(s, "    if (!o.anim && (o.c !== u.c || o.r !== u.r)) {", "    if (o.keep) { if (o.anim) continue; o.keep = false; }                 // v0.22: 붙잡아 둔 부대 — 자리 · 이름표 · 빛깔을 고치지 않는다\n    if (!o.anim && (o.c !== u.c || o.r !== u.r)) {")
# 불
s = rep(s, "    if (R3.fires[fk2]) continue;", "    if (R3.fires[fk2] || R3.fhold[fk2]) continue;                           // v0.22: 불화살 · 화계가 닿기 전에는 불길을 세우지 않는다")
# 세력권
s = rep(s, """    var b = G.bases[i]; if (b.owner < 0) continue;
    var col = rgbOf(G.factions[b.owner].color), rad = b.kind === 'gate' ? 1 : ZONE_R;""", """    var b = G.bases[i], ow = ownerShown(b); if (ow < 0) continue;      // v0.22: 붙잡아 둔 거점은 옛 주인의 빛깔로
    var col = rgbOf(G.factions[ow].color), rad = b.kind === 'gate' ? 1 : ZONE_R;""")
s = rep(s, "    if (b.owner === G.player && b.kind === 'city') for (j = 0; j < b.plots.length; j++) if (!b.plots[j].fac) ovPut(", "    if (ow === G.player && b.owner === G.player && b.kind === 'city') for (j = 0; j < b.plots.length; j++) if (!b.plots[j].fac) ovPut(")
# 미니맵
s = rep(s, """    var b = G.bases[i], p = hexCenter(b.c, b.r), s = b.kind === 'gate' ? 3 : 5;
    x.fillStyle = b.owner >= 0 ? G.factions[b.owner].color : '#a8a295'; x.fillRect(p[0] * sx - s / 2, p[1] * sz - s / 2, s, s);
    x.strokeStyle = b.owner === G.player ? SEAL : 'rgba(27,26,24,0.8)'; x.lineWidth = b.owner === G.player ? 1.6 : 1; x.strokeRect(""", """    var b = G.bases[i], p = hexCenter(b.c, b.r), s = b.kind === 'gate' ? 3 : 5, bow = ownerShown(b);
    x.fillStyle = bow >= 0 ? G.factions[bow].color : '#a8a295'; x.fillRect(p[0] * sx - s / 2, p[1] * sz - s / 2, s, s);
    x.strokeStyle = bow === G.player ? SEAL : 'rgba(27,26,24,0.8)'; x.lineWidth = bow === G.player ? 1.6 : 1; x.strokeRect(""")
wr('src/ui3d.js', s)

# ---------------- fx.js ----------------
s = rd('src/fx.js')
# 함께 맞은 부대: 번호로 찾는다(궤멸해 칸에서 사라졌어도 그림은 붙잡혀 있다) — 맞는 모습 · 흩어지는 모습
s = rep(s, """      var p = hexPos(xh.c, xh.r), ou = UAT[K(xh.c, xh.r)], oo = ou ? R3.units[ou.id] : null;
      fxMark(tracks, hit + 60 + i * 70, 340, 'arc', FX_INK, p, 1.2, 2.0, Math.random() * 6.28, { fade: 1.6 });
      if (oo && !oo.anim) fxHurt(tracks, hit + 80 + i * 70, oo, p, 0.11);
      end = Math.max(end, hit + 460 + i * 70);""", """      var p = hexPos(xh.c, xh.r), ou = UAT[K(xh.c, xh.r)], oo = xh.id !== undefined ? (R3.units[xh.id] || null) : (ou ? R3.units[ou.id] : null);
      fxMark(tracks, hit + 60 + i * 70, 340, 'arc', FX_INK, p, 1.2, 2.0, Math.random() * 6.28, { fade: 1.6 });
      if (oo && oo !== A && oo !== T && (oo.keep || !oo.anim)) {            // v0.22: 붙잡아 둔 그림을 그 자리에서 흔들고, 궤멸했으면 흩어 보낸다
        if (touched.indexOf(oo) < 0) { oo.anim = true; touched.push(oo); }
        fxHurt(tracks, hit + 80 + i * 70, oo, p, 0.11);
        if (xh.dead) { fxVanish(tracks, hit + 300 + i * 70, oo, p); end = Math.max(end, hit + 900 + i * 70); }
      }
      end = Math.max(end, hit + 460 + i * 70);""")
s = rep(s, """    for (var q = 0; q < touched.length; q++) { var o = touched[q]; o.anim = false; o.c = -1; o.sig = ''; if (o.sp && !o.gone) {""", """    if (typeof freeAct === 'function') freeAct(res);                  // v0.22: 붙잡아 둔 거점 · 불을 푼다(함락한 거점은 함락 장면이 푼다)
    for (var q = 0; q < touched.length; q++) { var o = touched[q]; o.anim = false; o.keep = false; o.c = -1; o.sig = ''; if (o.sp && !o.gone) {""")
s = rep(s, """function fxFall(b, text) {
  if (!R3 || !R3.ready) return 0;
""", """function fxFall(b, text) {
  if (!R3 || !R3.ready) return 0;
  if (typeof freeBase === 'function') freeBase(b.id);                 // v0.22: 이제 새 주인의 빛깔로(붙잡아 두었다면 여기서 푼다)
""")
wr('src/fx.js', s)

# ---------------- ui_panels.js ----------------
s = rd('src/ui_panels.js')
# 내 공격: 규칙이 끝난 바로 그때 붙잡는다(싸움터를 당겨 보이는 0.3초 동안 지도가 새 상태로 그려지지 않게)
s = rep(s, """  var miss = pa ? advAfter(pa, !!res.success) : '';
  UI.battleTurn = G.turn; playBgm('battle');
  var msg = resultMsg(name, res), fellB = res.fell && t.kind === 'base' ? t.b : null;""", """  var miss = pa ? advAfter(pa, !!res.success) : '';
  keepAct(res, true);                                              // v0.22: 연출이 끝날 때까지 얽힌 부대 · 거점의 그림을 지금 모습 그대로 둔다
  UI.battleTurn = G.turn; playBgm('battle');
  var msg = resultMsg(name, res), fellB = res.fell && t.kind === 'base' ? t.b : null;""")
s = rep(s, """    animAct(res, function () {
      duelThen(function () {
        UI.busy = false;""", """    animAct(res, function () {
      clearAnimFlags();                                            // v0.22: 붙잡아 둔 것을 모두 푼다 — 이제 지도가 새 상태로 바뀐다(함락이면 아래의 함락 장면과 함께)
      duelThen(function () {
        UI.busy = false;""")
# 걸어 들어가 차지한 빈 거점: 닿을 때까지 옛 빛깔
s = rep(s, """  var vis = unitVis(u), name = uName(u), res = aimApproach(u);
  if (!res) { marchDone(u, null, say); return true; }""", """  var vis = unitVis(u), name = uName(u), res = aimApproach(u);
  if (!res) { marchDone(u, null, say); return true; }
  if (res.captured !== undefined) keepBase(res.captured, -1);""")
s = rep(s, """  var vis = unitVis(u), name = uName(u), res = unitMarch(u);
  if (!res || !res.ok) { if (cb) cb(res); return; }""", """  var vis = unitVis(u), name = uName(u), res = unitMarch(u);
  if (!res || !res.ok) { if (cb) cb(res); return; }
  if (animate && res.captured !== undefined) keepBase(res.captured, -1);      // v0.22: 부대가 닿을 때까지 성은 옛 빛깔""")
s = rep(s, """  var res = unitMove(u, c, r, rc);
  if (!res.ok) { toast(res.msg); return; }""", """  var res = unitMove(u, c, r, rc);
  if (!res.ok) { toast(res.msg); return; }
  if (res.captured !== undefined) keepBase(res.captured, -1);          // v0.22: 부대가 닿을 때까지 성은 옛 빛깔(함락 장면 fxFall 이 푼다)""")
s = rep(s, """      marchLog(u, name, res);
      if (P.skip || !o) continue;
      o.anim = true;                                     // 연출이 시작될 때까지 제자리에 둔다""", """      marchLog(u, name, res);
      if (P.skip || !o) continue;
      o.anim = true;                                     // 연출이 시작될 때까지 제자리에 둔다
      if (res.captured !== undefined) keepBase(res.captured, -1);""")
# 붙잡아 둔 것을 한꺼번에 푸는 곳
s = rep(s, "function clearAnimFlags() { if (!R3) return; for (var id in R3.units) { var o = R3.units[id]; o.held = false; if (o.anim) { o.anim = false; o.c = -1; o.sig = ''; } } }",
        "function clearAnimFlags() { if (!R3) return; for (var id in R3.units) { var o = R3.units[id]; o.held = false; o.keep = false; if (o.anim) { o.anim = false; o.c = -1; o.sig = ''; } } holdsFree(); }      // v0.22: 붙잡아 둔 거점 · 불도 푼다")
# AI 의 차례: 보여 줄 사건에 얽힌 것만 붙잡는다 — 부대(이름표까지) · 맞은 거점 · 함락할 거점
s = rep(s, """  if (e.t === 'move') { o = R3.units[e.id]; if (o) o.anim = true; }
  else if (e.t === 'act' && e.res) { o = R3.units[e.res.aid]; if (o) o.anim = true; if (e.res.tid >= 0) { o = R3.units[e.res.tid]; if (o) o.anim = true; } }
}""", """  if (e.t === 'move') { o = R3.units[e.id]; if (o) o.anim = true; }
  else if (e.t === 'act' && e.res) { o = R3.units[e.res.aid]; if (o) o.anim = true; if (e.res.tid >= 0) { o = R3.units[e.res.tid]; if (o) o.anim = true; } keepAct(e.res); }      // v0.22: 이름표 · 함께 맞은 부대 · 맞은 거점까지
  else if (e.t === 'fall') {                                     // v0.22: 함락 장면이 나올 때까지 옛 주인의 빛깔. 그 함락으로 사라진 옛 주인의 부대(멸망)도 그때까지 남긴다
    keepBase(e.b, e.old);
    if (e.old >= 0) for (var gid in R3.units) { var og = R3.units[gid]; if (!UMAP[gid] && og.sig && +og.sig.split('|')[1] === e.old) keepUnit(gid); }
  }
}
/* 남은 장면에 얽힌 그림을 다시 붙잡는다 — 앞 장면이 끝나며 풀린 것(같은 부대가 움직이고 나서 친다) */
function holdRest() { var P = UI.play; if (!P || !P.rest) return; for (var i = 0; i < P.rest.length; i++) holdEv(P.rest[i]); }
function restFall(bid) { var P = UI.play; if (!P || !P.rest) return false; for (var i = 0; i < P.rest.length; i++) if (P.rest[i].t === 'fall' && P.rest[i].b === bid) return true; return false; }""")
s = rep(s, """      for (i = 0; i < evs.length; i++) holdEv(evs[i]);          // 보여 줄 때까지 그림을 지금 모습 그대로 둔다
      for (i = 0; i < evs.length; i++) {
        e = evs[i];
        if (e.cls === 2 || (e.cls === 1 && (big || P.minor < 16))) { show.push(e); if (e.cls === 1 && !big) P.minor++; }
      }""", """      for (i = 0; i < evs.length; i++) {
        e = evs[i];
        if (e.cls === 2 || (e.cls === 1 && (big || P.minor < 16))) { show.push(e); if (e.cls === 1 && !big) P.minor++; }
      }
      for (i = 0; i < show.length; i++) holdEv(show[i]);         // 보여 줄 때까지 그림을 지금 모습 그대로 둔다(v0.22: 보여 주지 않을 것은 붙잡지 않는다 — 풀어 줄 장면이 없다)""")
s = rep(s, """  var one = pg(function () {
    if (P.skip || i >= evs.length) { clearAnimFlags(); requestDraw(); done(); return; }
    P.shown++;
    presentEvent(evs[i++], one);
  });""", """  var one = pg(function () {
    if (P.skip || i >= evs.length) { P.rest = null; clearAnimFlags(); requestDraw(); done(); return; }
    P.shown++;
    var e1 = evs[i++]; P.rest = evs.slice(i);                    // v0.22: 아직 보여 주지 않은 장면들(holdRest 가 다시 붙잡는다)
    presentEvent(e1, one);
  });""")
s = rep(s, """      animMove({ id: e.id }, e.from, e.path, pg(function () { P.ans = []; requestDraw(); pwait(140, cb); }), 0.8 * spdK());""", """      animMove({ id: e.id }, e.from, e.path, pg(function () { P.ans = []; holdRest(); requestDraw(); pwait(140, cb); }), 0.8 * spdK());""")
s = rep(s, """      animAct(e.res, pg(function () {
        P.ans = []; requestDraw();
        var rec = e.res.duelRec;""", """      animAct(e.res, pg(function () {
        P.ans = [];
        if (e.res.fell && e.res.tbase >= 0 && !restFall(e.res.tbase)) freeBase(e.res.tbase);      // v0.22: 뒤따르는 함락 장면이 없으면 여기서 새 빛깔로
        holdRest(); requestDraw();
        var rec = e.res.duelRec;""")
# 함락 장면은 그 함락을 부른 장면(공격 · 걸어 들어감) 뒤에: 규칙 쪽에서는 함락이 먼저 적힌다(captureBase 가 사건을 남긴 뒤에야 공격 · 이동의 사건이 남는다).
#   0.21 까지 AI 의 차례를 보여 줄 때는 '○○ 함락!' 장면이 먼저 나오고 나서 그 성을 치는 모습이 나왔다.
s = rep(s, "    var s = P.next(), evs = EVQ.splice(0, EVQ.length), show = [], i, e, big = false, onlyMoves = false;", "    var s = P.next(), evs = orderEvs(EVQ.splice(0, EVQ.length)), show = [], i, e, big = false, onlyMoves = false;")
s = rep(s, "function pump() {\n", """/* v0.22: 함락 사건을 그 함락을 부른 장면(그 거점을 무너뜨린 공격 · 그 거점에 걸어 들어간 이동) 바로 뒤로 보낸다 — 치고 나서 함락 장면이 나오게.
   규칙 쪽에서는 함락이 먼저 적힌다(captureBase 가 사건을 남기고, 그 뒤에 공격 · 이동의 사건이 남는다) */
function orderEvs(evs) {
  for (var i = 0; i < evs.length; i++) {
    var e = evs[i]; if (e.t !== 'fall') continue;
    for (var j = i + 1; j < evs.length; j++) {
      var c = evs[j];
      if (c.t === 'fall' && c.b === e.b) break;
      if ((c.t === 'act' && c.res && c.res.fell && c.res.tbase === e.b) || (c.t === 'move' && c.into === e.b)) { evs.splice(i, 1); evs.splice(j, 0, e); i--; break; }      // 빼면 c 가 j - 1 로 당겨진다 → j 에 넣으면 c 바로 뒤
    }
  }
  return evs;
}
function pump() {
""")
# 함락으로 끝나는 공격: 치는 장면의 자막은 '○○대 — △△ 공격'(함락이라는 말은 뒤따르는 함락 장면이 한다 — 전에는 치기도 전에 '△△ 함락!'이 떴다)
s = rep(s, "      setCaption(e.f, resultMsg(e.name, e.res), e.tf === G.player ? 'hit' : '');", "      setCaption(e.f, (e.res.fell && restFall(e.res.tbase)) ? '<b>' + e.name + '</b> — ' + e.res.tname + ' 공격' : resultMsg(e.name, e.res), e.tf === G.player ? 'hit' : '');      // v0.22")
wr('src/ui_panels.js', s)
print('s2 ok')
