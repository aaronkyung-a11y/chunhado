# v0.21 (1) 관문이 길목이 된다
#   "함곡관, 호로관 같은 관문을 아래로 통과할 수 있으면 관문이 왜 필요하지?"
#   0.20 까지: 거점 칸은 지나갈 수 없어서 부대는 늘 관문 '옆'으로 돌아 다녔고, 일곱 관문 모두 그렇게 돌아도 길이 0 ~ 1걸음밖에 늘지 않았다.
#   · 관문 양옆으로 능선(넘을 수 없는 칸과 칸 사이의 변 — MAPDATA.walls, tools/gates21.py)이 선다. 땅(칸)은 그대로다.
#     능선 너머의 이웃 칸은 이웃이 아니다: 걸어갈 수 없고, 맞붙어 칠 수 없고(활은 두 칸 거리에서 넘겨 쏜다), 불도 번지지 않는다.
#   · 내 관문은 그냥 지나간다(관문 칸에 서지는 않는다 — 서면 입성). 남의 관문은 빼앗아야 지난다.
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

s = rd('src/core.js')
s = rep(s, """  var d = (r & 1) ? NB_ODD : NB_EVEN, out = [];
  for (var i = 0; i < 6; i++) { var cc = c + d[i][0], rr = r + d[i][1]; if (inMap(cc, rr)) out.push([cc, rr]); }
  return out;
}""", """  var d = (r & 1) ? NB_ODD : NB_EVEN, out = [], k6 = (r * W + c) * 6;
  for (var i = 0; i < 6; i++) { var cc = c + d[i][0], rr = r + d[i][1]; if (inMap(cc, rr) && !WALLB[k6 + i]) out.push([cc, rr]); }      // v0.21: 능선 너머는 이웃이 아니다
  return out;
}""")
s = rep(s, "var NHEX = W * H, NBR = new Int32Array(NHEX * 6), TCH", "var NHEX = W * H, NBR = new Int32Array(NHEX * 6), WALLB = new Uint8Array(NHEX * 6), WALLS = {}, TCH")
s = rep(s, """    for (var ci = 0; ci < 3; ci++) MC[ci][k] = (t === 'm' || t === 's' || t === 'x') ? 99 : (t === 'w' ? (rd ? 4 : 8) : (rd ? ROAD_COST[ci] : MOVE_COST[t][ci]));
  }
})();""", """    for (var ci = 0; ci < 3; ci++) MC[ci][k] = (t === 'm' || t === 's' || t === 'x') ? 99 : (t === 'w' ? (rd ? 4 : 8) : (rd ? ROAD_COST[ci] : MOVE_COST[t][ci]));
  }
  /* v0.21 능선: [c1, r1, c2, r2, 관문] — 두 칸 사이의 변을 막는다(양쪽 다) */
  (MAPDATA.walls || []).forEach(function (w) {
    var a = w[1] * W + w[0], b = w[3] * W + w[2];
    [[a, b], [b, a]].forEach(function (p) {
      for (var i = 0; i < 6; i++) if (NBR[p[0] * 6 + i] === p[1]) { NBR[p[0] * 6 + i] = -1; WALLB[p[0] * 6 + i] = 1; }
      WALLS[p[0] * 65536 + p[1]] = 1;
    });
  });
})();
function walled(k1, k2) { return WALLS[k1 * 65536 + k2] === 1; }                 // 두 칸 사이에 능선이 있는가
/* 지나갈 수 있는 관문인가 — 제 세력의 관문만(v0.21) */
function gateOpen(f, k) { var bi = BAT[k]; if (bi === undefined) return false; var b = G.bases[bi]; return b.kind === 'gate' && b.owner === f; }""")
s = rep(s, """    if (k !== start) {
      if (BAT[k] !== undefined) continue;                              // 거점에 들어가면 이동 끝
      if (!ignoreZoc && enemyAdjacent(u.f, c, r)) continue;            // ZOC: 멈춤
    }""", """    if (k !== start) {
      if (BAT[k] !== undefined) { if (!gateOpen(u.f, k)) continue; }   // 거점에 들어가면 이동 끝 — v0.21: 내 관문은 지나간다
      else if (!ignoreZoc && enemyAdjacent(u.f, c, r)) continue;       // ZOC: 멈춤
    }""")
s = rep(s, "    if (k !== start && BAT[k] !== undefined) continue;\n    for (var i = 0; i < 6; i++) {\n      var nk = NBR[k * 6 + i];",
           "    if (k !== start && BAT[k] !== undefined && !gateOpen(u.f, k)) continue;      // v0.21: 내 관문은 지나간다\n    for (var i = 0; i < 6; i++) {\n      var nk = NBR[k * 6 + i];")
# 길 위에서 멈출 칸: 지나가는 관문 칸에는 서지 않는다(서면 입성해 버린다)
s = rep(s, "  for (var i = 0; i < path.length; i++) if (rc.stop[path[i]]) best = path[i];\n  if (best >= 0) { var c = best % W, r = (best - c) / W; unitMove(u, c, r, rc); }",
           "  for (var i = 0; i < path.length; i++) if (rc.stop[path[i]] && (BAT[path[i]] === undefined || i === path.length - 1)) best = path[i];\n  if (best >= 0) { var c = best % W, r = (best - c) / W; unitMove(u, c, r, rc); }")
s = rep(s, "  for (var i = 0; i < path.length; i++) if (rc.stop[path[i]] && (!G.fires[path[i]] || BAT[path[i]] !== undefined)) best = path[i];",
           "  for (var i = 0; i < path.length; i++) if (rc.stop[path[i]] && (BAT[path[i]] === undefined ? !G.fires[path[i]] : i === path.length - 1)) best = path[i];")
s = rep(s, """    var k = K(c, r), ou = UAT[k];
    if (ou && ou.f !== u.f) { if (!pactOn(u.f, ou.f)) out.push({ kind: 'unit', u: ou, c: c, r: r, d: d }); continue; }""", """    var k = K(c, r), ou = UAT[k];
    if (d === 1 && walled(K(u.c, u.r), k)) continue;                   // v0.21: 능선 너머 바로 옆 칸은 칠 수 없다(계략은 넘어간다)
    if (ou && ou.f !== u.f) { if (!pactOn(u.f, ou.f)) out.push({ kind: 'unit', u: ou, c: c, r: r, d: d }); continue; }""")
s = rep(s, "  if (hdist(t.c, t.r, u.c, u.r) !== 1) return ERR('옆 칸의 부대에만 보급할 수 있습니다');",
           "  if (hdist(t.c, t.r, u.c, u.r) !== 1 || walled(K(t.c, t.r), K(u.c, u.r))) return ERR('옆 칸의 부대에만 보급할 수 있습니다');")
wr('src/core.js', s)

s = rd('src/ai.js')
s = rep(s, "  for (i = 0; i < path.length; i++) { k = path[i]; if (rc.stop[k] && (!G.fires[k] || BAT[k] !== undefined)) dest = k; }",
           "  for (i = 0; i < path.length; i++) { k = path[i]; if (rc.stop[k] && (BAT[k] === undefined ? !G.fires[k] : i === path.length - 1)) dest = k; }      // v0.21: 지나가는 관문 칸에는 서지 않는다")
wr('src/ai.js', s)

# 지도: 능선이 선 변마다 짙은 먹선 + 빗금(어느 변이 막혔는지 가까이서도 또렷하게). 바탕 그림의 산줄기(tools/terrain21.py) 위에 얹힌다
s = rd('src/ui3d.js')
s = rep(s, "  buildTerrain(); buildRoads(); buildTrees();", "  buildTerrain(); buildRoads(); buildTrees(); buildWalls();")
s = rep(s, "function hash2(a, b) {", """function buildWalls() {                                          // v0.21 관문의 능선(MAPDATA.walls): 막힌 변을 따라 먹선 한 줄, 가운데에 짧은 빗금
  var ws = MAPDATA.walls || []; if (!ws.length) return;
  var pos = [], idx = [], n = 0, w = 0.075;
  function quad(ax, az, bx, bz, hw) {
    var tx = bx - ax, tz = bz - az, L = Math.sqrt(tx * tx + tz * tz) || 1, px = -tz / L * hw, pz = tx / L * hw;
    var ya = Math.max(groundY(ax, az), groundY(ax + px, az + pz), groundY(ax - px, az - pz)) + 0.05, yb = Math.max(groundY(bx, bz), groundY(bx + px, bz + pz), groundY(bx - px, bz - pz)) + 0.05;
    pos.push(ax + px, ya, az + pz, ax - px, ya, az - pz, bx + px, yb, bz + pz, bx - px, yb, bz - pz);
    idx.push(n, n + 1, n + 2, n + 1, n + 3, n + 2); n += 4;
  }
  ws.forEach(function (e, i) {
    var a = hexCenter(e[0], e[1]), b = hexCenter(e[2], e[3]), mx = (a[0] + b[0]) / 2, mz = (a[1] + b[1]) / 2, dx = b[0] - a[0], dz = b[1] - a[1], L = Math.sqrt(dx * dx + dz * dz) || 1;
    var ux = dx / L, uz = dz / L, px = -uz, pz = ux, j = (hash2(e[0] * 7 + e[2], e[1] * 5 + e[3]) - 0.5) * 0.10;
    var cx = mx + ux * j, cz = mz + uz * j;                         // 가운데를 조금 흔들어 꺾인 선으로
    quad(mx + px * 0.5, mz + pz * 0.5, cx, cz, w); quad(cx, cz, mx - px * 0.5, mz - pz * 0.5, w);
    var sgn = (i % 2) ? 1 : -1; quad(cx, cz, cx + ux * 0.24 * sgn + px * 0.10, cz + uz * 0.24 * sgn + pz * 0.10, w * 0.62);      // 빗금
  });
  var g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3)); g.setIndex(new THREE.BufferAttribute(new Uint16Array(idx), 1));
  var mat = new THREE.MeshBasicMaterial({ color: 0x1b1a18, transparent: true, opacity: 0.74, depthWrite: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 });
  var mesh = new THREE.Mesh(g, mat); mesh.frustumCulled = false; mesh.renderOrder = 0; R3.scene.add(mesh);
}
function hash2(a, b) {""")
wr('src/ui3d.js', s)
print('s1 ok')
