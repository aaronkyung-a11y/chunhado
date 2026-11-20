# v0.8 수송대: 이동력 14 → 18, 우리 땅(내 성역·들판) 안에서는 성역의 경계에서 멈추지 않는다
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:90])
    return s.replace(a, b)
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "trans:   { name: '수송대', g: '수', cls: 'trans', mp: 14,", "trans:   { name: '수송대', g: '수', cls: 'trans', mp: 18,")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """/* 이번 턴 이동 가능 범위. 반환: { cost:{key:cost}, prev:{key:key}, stop:{key:true} } */
function unitReach(u) {
  var cost = {}, prev = {}, stop = {}, start = K(u.c, u.r), h = new Heap();
  var ignoreZoc = uHas(u, '비장'), z0 = ZONE[start];""", """/* 성역의 경계를 넘는 걸음이 그 턴의 이동을 끝내는가.
   보통은 끝낸다(성과 성 사이 행군이 적어도 30일이 되게 하는 규칙). 수송대만 예외: 내 성역과 주인 없는 들판 사이를 오갈 때는 멈추지 않는다
   — 물자를 나르는 길이 싸우러 가는 길만큼 더딜 까닭이 없다. 남의 성역(빈 성 포함)을 드나들 때는 수송대도 멈춘다. */
function zoneHalts(u, zFrom, zTo) {
  if (zFrom === zTo) return false;
  if (u.type !== 'trans') return true;
  return !((zFrom < 0 || G.bases[zFrom].owner === u.f) && (zTo < 0 || G.bases[zTo].owner === u.f));
}
/* 이번 턴 이동 가능 범위. 반환: { cost:{key:cost}, prev:{key:key}, stop:{key:true}, halt:{key:true — 거기 서면 이번 턴 이동 끝} } */
function unitReach(u) {
  var cost = {}, prev = {}, stop = {}, halt = {}, start = K(u.c, u.r), h = new Heap();
  var ignoreZoc = uHas(u, '비장');""")
s = rep(s, """      if (ZONE[k] !== z0) continue;                                    // 성역의 경계를 넘었으면 이동 끝""",
           """      if (halt[k]) continue;                                           // 성역의 경계를 넘었으면 이동 끝""")
s = rep(s, """        cost[nk] = nd; prev[nk] = k;
        if (!ou) stop[nk] = true;
        h.push(nd, nk);
      }
    }
  }
  delete stop[start];
  return { cost: cost, prev: prev, stop: stop };""", """        cost[nk] = nd; prev[nk] = k;
        if (zoneHalts(u, ZONE[k], ZONE[nk])) halt[nk] = true; else delete halt[nk];
        if (!ou) stop[nk] = true;
        h.push(nd, nk);
      }
    }
  }
  delete stop[start];
  return { cost: cost, prev: prev, stop: stop, halt: halt };""")
s = rep(s, """      if (ZONE[nk] !== ZONE[k]) mc += ZONE_PEN;""", """      if (ZONE[nk] !== ZONE[k] && zoneHalts(u, ZONE[k], ZONE[nk])) mc += ZONE_PEN;""")
s = rep(s, """  if (ZONE[k] !== ZONE[K(from[0], from[1])]) { u.mp = 0; u.zin = ZONE[k]; }   // 성역의 경계를 넘었으면 이번 턴 이동은 여기까지. 막 들어선 성역의 성은 이번 턴에 칠 수 없다(zin)""",
           """  var halted = rc.halt ? !!rc.halt[k] : ZONE[k] !== ZONE[K(from[0], from[1])];
  if (halted) { u.mp = 0; u.zin = ZONE[k]; }                // 성역의 경계를 넘었으면 이번 턴 이동은 여기까지. 막 들어선 성역의 성은 이번 턴에 칠 수 없다(zin)""")
s = rep(s, """    if (ZONE[path[i]] !== z) { z = ZONE[path[i]]; halt = true; }       // 성역의 경계를 넘으면 그 턴은 거기까지""",
           """    if (ZONE[path[i]] !== z) { if (zoneHalts(u, z, ZONE[path[i]])) halt = true; z = ZONE[path[i]]; }   // 성역의 경계를 넘으면 그 턴은 거기까지(수송대는 우리 땅 안에서 예외)""")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
