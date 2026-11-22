# v0.20 (8) 싸움의 그림 — 화살이 날아가는 모습 · 불길을 또렷하고 정교하게
#   "화살 쏘는 모습(화살이 날아가는 모습), 불길 등의 애니메이션이 없어진거 같은데 잘 봐주고 좀 더 애니메이션이 정교하면 좋겠다"
#   살펴본 결과: 없어지지는 않았다 — 화살은 가는 선 여섯 줄이 0.3초쯤 스쳐 지나갔고(화면에서 2픽셀 굵기), 0.17 부터 부대마다 붙은 얼굴 · 병력 딱지에 가려 거의 보이지 않았다.
#   · 화살: 굵은 살대 · 살촉 · 깃을 그린 그림으로(1.5배), 날아가는 시간을 늘리고(0.25초 + 거리 → 0.4초 + 거리), 뒤에 잔상이 따라온다. 시위를 놓는 순간의 붓 자국,
#           꽂힌 화살이 잠깐 남았다가 사라진다. 딱지 위로 그려진다(가려지지 않게).
#   · 불(화계 · 화전): 불길이 여럿 차례로 솟고(크게), 불티가 튀어 오르고, 연기가 피어오른다. 불화살은 붉은 잔상을 끈다.
#   · 칸에 붙은 불(불길): 불꽃 다섯(전에는 셋)이 크게 일렁이고 그 위로 연기가 오른다.
#   · 칼 · 창: 맞은 자리에 먹이 튄다. 큰 타격(전법 성공 · 치명)은 엇갈린 두 획.
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

s = rd('src/fx.js')
# 화살 그림: 살대 · 살촉 · 깃
s = rep(s, """    c = fxCanvas(128, 24); x = c.getContext('2d');
    g = x.createLinearGradient(0, 0, 128, 0); g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.35, 'rgba(255,255,255,0.55)'); g.addColorStop(1, 'rgba(255,255,255,1)');
    x.strokeStyle = g; x.lineWidth = 2.4; x.lineCap = 'round'; x.beginPath(); x.moveTo(4, 12); x.lineTo(118, 12); x.stroke();
    x.fillStyle = '#fff'; x.beginPath(); x.moveTo(126, 12); x.lineTo(108, 6); x.lineTo(112, 12); x.lineTo(108, 18); x.closePath(); x.fill();""",
"""    c = fxCanvas(192, 40); x = c.getContext('2d');                 // v0.20: 굵은 살대 · 살촉 · 깃(전에는 가는 선 한 줄이었다)
    g = x.createLinearGradient(0, 0, 192, 0); g.addColorStop(0, 'rgba(255,255,255,0.55)'); g.addColorStop(0.3, 'rgba(255,255,255,0.9)'); g.addColorStop(1, 'rgba(255,255,255,1)');
    x.strokeStyle = g; x.lineWidth = 4.2; x.lineCap = 'round'; x.beginPath(); x.moveTo(20, 20); x.lineTo(168, 20); x.stroke();
    x.fillStyle = '#fff'; x.beginPath(); x.moveTo(190, 20); x.lineTo(158, 9); x.lineTo(165, 20); x.lineTo(158, 31); x.closePath(); x.fill();
    x.globalAlpha = 0.85; for (i = 0; i < 3; i++) { x.beginPath(); x.moveTo(8 + i * 9, 20); x.lineTo(2 + i * 9, 8); x.lineTo(14 + i * 9, 8); x.lineTo(22 + i * 9, 20); x.lineTo(14 + i * 9, 32); x.lineTo(2 + i * 9, 32); x.closePath(); x.fill(); }
    x.globalAlpha = 1;
  } else if (name === 'trail') {                             // 날아가는 것 뒤에 끌리는 잔상: 앞이 짙고 뒤로 흩어진다
    c = fxCanvas(192, 24); x = c.getContext('2d');
    for (i = 0; i < 9; i++) { var ty = 4 + R() * 16, tx0 = R() * 90; g = x.createLinearGradient(tx0, 0, 192, 0); g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(1, 'rgba(255,255,255,' + (0.35 + 0.5 * R()).toFixed(2) + ')'); x.strokeStyle = g; x.lineWidth = 1 + R() * 2.2; x.beginPath(); x.moveTo(tx0, ty); x.lineTo(190, 12 + (ty - 12) * 0.25); x.stroke(); }
  } else if (name === 'ember') {                             // 불티: 작은 점 몇
    c = fxCanvas(64, 64); x = c.getContext('2d');
    for (i = 0; i < 9; i++) { var ex = 8 + R() * 48, ey = 8 + R() * 48, er = 1.6 + R() * 3.2; g = x.createRadialGradient(ex, ey, 0, ex, ey, er * 2); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.5, 'rgba(255,255,255,0.7)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(ex - er * 2, ey - er * 2, er * 4, er * 4); }""")
# 화살 무리
s = rep(s, """function fxVolley(tracks, a, from, to, n, color, spread) {
  var dist = Math.sqrt((to[0] - from[0]) * (to[0] - from[0]) + (to[2] - from[2]) * (to[2] - from[2])), h = 0.7 + 0.16 * dist, fly = 250 + 22 * dist;
  for (var i = 0; i < n; i++) (function (i) {
    var sp = null, ox = (Math.random() - 0.5) * (spread || 0.5), oz = (Math.random() - 0.5) * (spread || 0.5), sx = (Math.random() - 0.5) * 0.4, st = a + i * (170 / n);
    function at(t) { var x = from[0] + sx + (to[0] + ox - from[0] - sx) * t, z = from[2] + (to[2] + oz - from[2]) * t; return [x, groundY(x, z) + 0.6 + Math.sin(Math.PI * t) * h, z]; }
    tracks.push({ a: st, b: st + fly,
      on: function () { sp = fxSprite('arrow', color === undefined ? FX_INK : color, 9); sp.scale.set(1.25, 0.24, 1); },
      step: function (u) { var p = at(u), q = at(Math.min(1, u + 0.05)); sp.position.set(p[0], p[1], p[2]); sp.material.rotation = u < 0.96 ? fxAngle(p, q) : sp.material.rotation; sp.material.opacity = u < 0.1 ? u * 10 : 1; },
      off: function () { if (sp) fxKill(sp); } });
  })(i);
  return a + 170 + fly;
}""", """var VOLLEY = { fly0: 400, flyK: 30, gap: 260, w: 1.9, h: 0.40, stick: 620 };      // v0.20: 날아가는 시간(ms) = fly0 + flyK × 거리 · 쏘는 간격 · 화살 크기 · 꽂힌 화살이 남는 시간
function fxVolley(tracks, a, from, to, n, color, spread) {
  var dist = Math.sqrt((to[0] - from[0]) * (to[0] - from[0]) + (to[2] - from[2]) * (to[2] - from[2])), h = 0.9 + 0.2 * dist, fly = VOLLEY.fly0 + VOLLEY.flyK * dist;
  var col = color === undefined ? FX_INK : color, hot = col === FX_FIRE;
  for (var i = 0; i < n; i++) (function (i) {
    var sp = null, tr = null, ox = (Math.random() - 0.5) * (spread || 0.5), oz = (Math.random() - 0.5) * (spread || 0.5), sx = (Math.random() - 0.5) * 0.5, st = a + i * (VOLLEY.gap / n) + Math.random() * 30, hk = h * (0.85 + 0.3 * Math.random());
    function at(t) { var x = from[0] + sx + (to[0] + ox - from[0] - sx) * t, z = from[2] + (to[2] + oz - from[2]) * t; return [x, groundY(x, z) + 0.7 + Math.sin(Math.PI * t) * hk, z]; }
    tracks.push({ a: st, b: st + fly,
      on: function () { sp = fxSprite('arrow', col, 9.6); sp.scale.set(VOLLEY.w, VOLLEY.h, 1); tr = fxSprite('trail', hot ? 0xf2a03c : col, 9.5); tr.center.set(1, 0.5); },
      step: function (u) {
        var p = at(u), q = at(Math.min(1, u + 0.05)), ang = u < 0.96 ? fxAngle(p, q) : sp.material.rotation;
        sp.position.set(p[0], p[1], p[2]); sp.material.rotation = ang; sp.material.opacity = u < 0.08 ? u * 12.5 : 1;
        tr.position.set(p[0], p[1], p[2]); tr.material.rotation = ang; tr.scale.set(VOLLEY.w * (1.1 + 1.3 * Math.sin(Math.PI * Math.min(1, u * 1.15))), VOLLEY.h * (hot ? 1.5 : 1.05), 1); tr.material.opacity = (hot ? 0.8 : 0.5) * Math.sin(Math.PI * Math.min(1, u * 1.08));
      },
      off: function () { if (tr) fxKill(tr); if (!sp) return; var s0 = sp, p1 = at(1); s0.position.set(p1[0], p1[1] - 0.22, p1[2]); s0.scale.set(VOLLEY.w * 0.72, VOLLEY.h, 1);      // 꽂힌 채 잠깐 남는다
        anim(VOLLEY.stick, function (t) { s0.material.opacity = t < 0.5 ? 0.9 : 0.9 * (1 - (t - 0.5) / 0.5); }, function () { fxKill(s0); }); } });
    if (i % 2 === 0) fxMark(tracks, st + fly - 20, 300, 'puff', FX_WASH, [to[0] + ox, to[1], to[2] + oz], 0.35, 0.9, 0, { dy: 0.2, rise: 0.25, alpha: 0.7, order: 2.6 });      // 떨어진 자리의 먼지
  })(i);
  fxMark(tracks, a - 10, 300, 'arc', col, from, 0.9, 1.5, fxAngle(from, to) + 1.57, { dy: 0.8, fade: 1.5, alpha: 0.85 });      // 시위를 놓는 붓 자국
  return a + VOLLEY.gap + fly;
}
/* v0.20 불: 불길이 차례로 솟고, 불티가 튀고, 연기가 오른다. k = 크기 */
function fxBlaze(tracks, a, p, k, n) {
  var i; k = k || 1; n = n || 6;
  for (i = 0; i < n; i++) fxMark(tracks, a + i * 75, 760, 'flame', 0xffffff, [p[0] + (Math.random() - 0.5) * 1.1 * k, p[1], p[2] + (Math.random() - 0.5) * 0.6 * k], 0.45 * k, (1.05 + Math.random() * 0.5) * k, 0, { dy: 0.5, aspect: 1.7, rise: 0.55, fade: 1, order: 9.2 });
  for (i = 0; i < 4; i++) fxMark(tracks, a + 90 + i * 120, 820, 'ember', i % 2 ? 0xffd27a : FX_FIRE, [p[0] + (Math.random() - 0.5) * 0.9 * k, p[1], p[2]], 0.5 * k, 1.5 * k, Math.random() * 6.28, { dy: 0.9, rise: 1.5 + Math.random() * 0.8, fade: 1.2, spin: 1.2, order: 9.4 });
  for (i = 0; i < 3; i++) fxMark(tracks, a + 320 + i * 170, 1150, 'puff', 0x4a4640, [p[0] + (i - 1) * 0.35 * k, p[1], p[2] - 0.1], 0.9 * k, 2.3 * k, 0, { dy: 1.2, rise: 1.5, alpha: 0.55, fade: 1.1, order: 9.1 });
  fxMark(tracks, a, 460, 'spark', FX_FIRE, p, 0.8 * k, 2.4 * k, 0, { order: 9.3 });
  return a + n * 75 + 760;
}""")
s = rep(s, """        for (i = 0; i < 5; i++) fxMark(tracks, hit + i * 70, 620, 'flame', 0xffffff, [pt[0] + (Math.random() - 0.5) * 0.9, pt[1], pt[2] + (Math.random() - 0.5) * 0.5], 0.5, 1.5, 0, { dy: 0.5, aspect: 1.5, rise: 0.5, fade: 1 });
        fxMark(tracks, hit, 420, 'spark', FX_FIRE, pt, 0.8, 2.2, 0, {});
        fxHurt(tracks, hit + 60, T, pt, 0.14);""", """        fxMark(tracks, 160, hit - 100, 'trail', 0xf2a03c, fxLerp(pa, pt, 0.5), 2.2, 3.4, ang, { dy: 0.9, aspect: 0.16, fade: 1.2, alpha: 0.8 });      // v0.20: 불씨가 날아간다
        var blazeEnd = fxBlaze(tracks, hit, pt, 1.15, 7);
        tracks.push({ a: hit, b: hit, on: function () { sfx('fire'); } });
        fxHurt(tracks, hit + 60, T, pt, 0.14);""")
s = rep(s, """    tracks.push({ a: hit, b: hit, on: impact });
    end = hit + 720;
  } else {""", """    tracks.push({ a: hit, b: hit, on: impact });
    end = Math.max(hit + 720, typeof blazeEnd === 'number' ? blazeEnd - 260 : 0);
  } else {""")
s = rep(s, """      if (tac === 'hwasi' && !res.fail) for (i = 0; i < 3; i++) fxMark(tracks, hit + i * 80, 560, 'flame', 0xffffff, [pt[0] + (i - 1) * 0.4, pt[1], pt[2]], 0.5, 1.3, 0, { dy: 0.5, aspect: 1.5, rise: 0.4 });""",
        """      if (tac === 'hwasi' && !res.fail) fxBlaze(tracks, hit, pt, 0.95, 5);                       // v0.20: 불화살이 꽂힌 자리에 불이 인다""")
s = rep(s, """  function slashAt(a, p, col, size, rot) { fxMark(tracks, a, 380, 'arc', col, p, size * 0.7, size * 1.25, rot === undefined ? ang - 1.2 + Math.random() * 0.5 : rot, { fade: 1.6 });""",
        """  function slashAt(a, p, col, size, rot) {
    if (size >= 2.2) fxMark(tracks, a + 70, 360, 'arc', FX_INK, p, size * 0.6, size * 1.1, (rot === undefined ? ang : rot) + 1.9, { fade: 1.7, alpha: 0.8 });      // v0.20: 큰 타격은 엇갈린 두 획
    fxMark(tracks, a + 30, 520, 'splat', FX_INK, [p[0] + (Math.random() - 0.5) * 0.5, p[1], p[2] + 0.1], size * 0.22, size * 0.52, Math.random() * 6.28, { dy: 0.5, alpha: 0.5, fade: 1.2, order: 2.7 });      // 먹이 튄다
    fxMark(tracks, a, 380, 'arc', col, p, size * 0.7, size * 1.25, rot === undefined ? ang - 1.2 + Math.random() * 0.5 : rot, { fade: 1.6 });""")
wr('src/fx.js', s)

s = rd('src/ui3d.js')
# 칸에 붙은 불: 불꽃 다섯 + 연기
s = rep(s, """    for (j = 0; j < 3; j++) { var fsprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: R3.flame, transparent: true, depthTest: false, depthWrite: false })); fsprite.center.set(0.5, 0.08); fsprite.position.set((j - 1) * 0.42, 0, (j % 2) * 0.2); fsprite.renderOrder = 4; fg.add(fsprite); }""",
        """    for (j = 0; j < 5; j++) { var fsprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: R3.flame, transparent: true, depthTest: false, depthWrite: false })); fsprite.center.set(0.5, 0.08); fsprite.position.set((j - 2) * 0.33, 0, (j % 2) * 0.24 - 0.1); fsprite.renderOrder = 4; fsprite.userData.k = j === 2 ? 1.25 : (j % 2 ? 1 : 0.8); fg.add(fsprite); }      // v0.20: 불꽃 다섯(가운데가 크다)
    for (j = 0; j < 2; j++) { var smoke = new THREE.Sprite(new THREE.SpriteMaterial({ map: fxTex('puff'), color: 0x4a4640, transparent: true, opacity: 0, depthTest: false, depthWrite: false })); smoke.renderOrder = 3.9; smoke.userData.smoke = j + 1; fg.add(smoke); }      // 연기 둘이 번갈아 오른다""")
s = rep(s, """for (i = 0; i < fg.children.length; i++) { var s = 0.9 + 0.22 * Math.sin(now / 90 + i * 2.1 + (+fk)); fg.children[i].scale.set(0.8 * s, 1.25 * s + 0.15 * Math.sin(now / 57 + i), 1); } }""",
        """for (i = 0; i < fg.children.length; i++) {
        var fch = fg.children[i];
        if (fch.userData.smoke) { var su = ((now / 1700) + fch.userData.smoke * 0.5 + (+fk) * 0.37) % 1; fch.position.set(0.25 * Math.sin(su * 5 + fch.userData.smoke), 1.5 + 1.9 * su, -0.05); fch.scale.set(1.1 + 1.5 * su, 0.9 + 1.2 * su, 1); fch.material.opacity = 0.42 * Math.sin(Math.PI * su); continue; }
        var s = (0.9 + 0.22 * Math.sin(now / 90 + i * 2.1 + (+fk))) * (fch.userData.k || 1); fch.scale.set(1.0 * s, 1.6 * s + 0.2 * Math.sin(now / 57 + i), 1);
      } }""")
wr('src/ui3d.js', s)
print('s8 ok')
