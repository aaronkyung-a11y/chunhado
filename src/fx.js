/* ===== 천하도 — 먹 붓질 연출: 이동·공격·전법·계략·함락 =====
   그림은 모두 코드로 그린 흰 붓 자국(투명 바탕)이고, 쓸 때 먹빛·인주빛으로 물들인다.
   한 번의 행동은 하나의 anim 위에 올린 시간표(fxTimeline)로 돌아가므로, 재생 중 화면을 누르면 한꺼번에 끝까지 넘어간다. */
var FX = { tex: {}, live: [] };
var FXK = 1.32;                                          // 붓 자국의 크기(부대 그림 크기에 맞춤)
var FX_INK = 0x1b1a18, FX_SEAL = 0xb5332a, FX_WASH = 0x6f6a60, FX_INDIGO = 0x2f4f6f, FX_FIRE = 0xd8572a;

function fxRng(seed) { var s = seed | 0; return function () { s = (s * 1664525 + 1013904223) | 0; return ((s >>> 8) & 0xffff) / 65535; }; }
function fxCanvas(w, h) { var c = document.createElement('canvas'); c.width = w; c.height = h; cv2d(c); return c; }
function fxTexOf(c) { return cvTex(c, false); }      // v0.22: 화소를 지닌 텍스처(ui3d.js 의 cvTex)

/* 붓 자국 그림들 */
function fxTex(name) {
  if (FX.tex[name]) return FX.tex[name];
  var c, x, i, j, R = fxRng(name.length * 7919 + name.charCodeAt(0) * 131), g;
  if (name === 'stroke') {                                   // 곧게 그은 한 획: 갈라진 붓털, 시작은 짙고 끝은 마른 붓
    c = fxCanvas(512, 96); x = c.getContext('2d');
    for (i = 0; i < 46; i++) {
      var y = 10 + 76 * (i / 45) + (R() - 0.5) * 3, x0 = 6 + R() * 26, x1 = 512 - R() * (40 + 150 * Math.abs(i / 45 - 0.5));
      x.strokeStyle = 'rgba(255,255,255,' + (0.35 + 0.65 * R()).toFixed(2) + ')'; x.lineWidth = 1.2 + R() * 2.6;
      x.beginPath(); x.moveTo(x0, y); x.bezierCurveTo(170, y + (R() - 0.5) * 5, 340, y + (R() - 0.5) * 5, x1, y + (R() - 0.5) * 4); x.stroke();
    }
    x.globalCompositeOperation = 'destination-out';          // 마른 붓: 군데군데 비어 있다
    for (i = 0; i < 90; i++) { x.fillStyle = 'rgba(0,0,0,' + (0.3 + 0.6 * R()).toFixed(2) + ')'; var gx = 150 + R() * 360; x.fillRect(gx, R() * 96, 8 + R() * 46 * (gx / 512), 1 + R() * 2.2); }
    x.globalCompositeOperation = 'destination-in';           // 위아래로 볼록한 모양
    g = x.createRadialGradient(256, 48, 10, 256, 48, 262); g.addColorStop(0, 'rgba(0,0,0,1)'); g.addColorStop(0.9, 'rgba(0,0,0,1)'); g.addColorStop(1, 'rgba(0,0,0,0)');
    x.save(); x.translate(256, 48); x.scale(1, 0.19); x.translate(-256, -48); x.fillStyle = g; x.fillRect(-10, -400, 540, 900); x.restore();
  } else if (name === 'arc') {                               // 휘둘러 벤 초승달 획
    c = fxCanvas(256, 256); x = c.getContext('2d'); x.translate(128, 150);
    for (i = 0; i < 40; i++) {
      var rr2 = 78 + 34 * (i / 39) + (R() - 0.5) * 2, a0 = Math.PI * (1.12 + R() * 0.07), a1 = Math.PI * (1.9 - R() * 0.12 - 0.1 * Math.abs(i / 39 - 0.45));
      x.strokeStyle = 'rgba(255,255,255,' + (0.3 + 0.7 * R()).toFixed(2) + ')'; x.lineWidth = 1 + R() * 2.4;
      x.beginPath(); x.arc(0, 0, rr2, a0, a1); x.stroke();
    }
    x.globalCompositeOperation = 'destination-out';
    for (i = 0; i < 60; i++) { var aa = Math.PI * (1.45 + R() * 0.45), r3 = 78 + R() * 34; x.fillStyle = 'rgba(0,0,0,' + (0.4 + 0.5 * R()).toFixed(2) + ')'; x.beginPath(); x.arc(Math.cos(aa) * r3, Math.sin(aa) * r3, 0.8 + R() * 1.6, 0, 6.3); x.fill(); }
    x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'destination-in';
    g = x.createLinearGradient(20, 0, 236, 0); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.12, 'rgba(0,0,0,1)'); g.addColorStop(0.7, 'rgba(0,0,0,0.95)'); g.addColorStop(1, 'rgba(0,0,0,0)');
    x.fillStyle = g; x.fillRect(0, 0, 256, 256);
  } else if (name === 'splat') {                             // 튄 먹물
    c = fxCanvas(256, 256); x = c.getContext('2d'); x.fillStyle = '#fff';
    x.beginPath();
    for (i = 0; i <= 28; i++) { var a = i / 28 * 6.2832, rd = 46 + 26 * R() + (i % 4 === 0 ? 20 * R() : 0); if (i) x.lineTo(128 + Math.cos(a) * rd, 128 + Math.sin(a) * rd); else x.moveTo(128 + rd, 128); }
    x.closePath(); x.fill();
    for (i = 0; i < 26; i++) { var a2 = R() * 6.2832, d2 = 62 + R() * 58, s2 = 1.5 + R() * 7 * (1 - (d2 - 62) / 70); x.globalAlpha = 0.5 + 0.5 * R(); x.beginPath(); x.ellipse(128 + Math.cos(a2) * d2, 128 + Math.sin(a2) * d2, s2 * (1 + R()), s2, a2, 0, 6.3); x.fill(); }
    x.globalAlpha = 1; x.globalCompositeOperation = 'destination-out';
    g = x.createRadialGradient(118, 118, 2, 128, 128, 60); g.addColorStop(0, 'rgba(0,0,0,0.42)'); g.addColorStop(1, 'rgba(0,0,0,0)'); x.fillStyle = g; x.fillRect(0, 0, 256, 256);
  } else if (name === 'puff') {                              // 담묵 먼지
    c = fxCanvas(128, 128); x = c.getContext('2d');
    for (i = 0; i < 7; i++) { var px = 64 + (R() - 0.5) * 52, py = 66 + (R() - 0.5) * 40, pr = 20 + R() * 22; g = x.createRadialGradient(px, py, 1, px, py, pr); g.addColorStop(0, 'rgba(255,255,255,0.5)'); g.addColorStop(0.6, 'rgba(255,255,255,0.22)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(0, 0, 128, 128); }
  } else if (name === 'arrow') {                             // 날아가는 화살 한 줄기
    c = fxCanvas(192, 40); x = c.getContext('2d');                 // v0.20: 굵은 살대 · 살촉 · 깃(전에는 가는 선 한 줄이었다)
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
    for (i = 0; i < 9; i++) { var ex = 8 + R() * 48, ey = 8 + R() * 48, er = 1.6 + R() * 3.2; g = x.createRadialGradient(ex, ey, 0, ex, ey, er * 2); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.5, 'rgba(255,255,255,0.7)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(ex - er * 2, ey - er * 2, er * 4, er * 4); }
  } else if (name === 'spark') {                             // 부딪힌 자리의 짧은 획들
    c = fxCanvas(128, 128); x = c.getContext('2d'); x.translate(64, 64); x.strokeStyle = '#fff'; x.lineCap = 'round';
    for (i = 0; i < 11; i++) { var a3 = i / 11 * 6.2832 + R() * 0.4, r0 = 12 + R() * 10, r1 = 34 + R() * 26; x.lineWidth = 1.6 + R() * 3.4; x.globalAlpha = 0.55 + 0.45 * R(); x.beginPath(); x.moveTo(Math.cos(a3) * r0, Math.sin(a3) * r0); x.lineTo(Math.cos(a3) * r1, Math.sin(a3) * r1); x.stroke(); }
  } else if (name === 'swirl') {                             // 소용돌이(혼란·위보)
    c = fxCanvas(256, 256); x = c.getContext('2d'); x.translate(128, 128); x.fillStyle = '#fff';
    for (j = 0; j < 2; j++) for (i = 0; i < 240; i++) { var tt = i / 239, a4 = j * Math.PI + tt * 7.6, r4 = 14 + tt * 100; x.globalAlpha = (0.25 + 0.6 * (1 - tt)) * (0.6 + 0.4 * R()); x.beginPath(); x.arc(Math.cos(a4) * r4, Math.sin(a4) * r4, 1.6 + 5.2 * Math.sin(Math.PI * tt), 0, 6.3); x.fill(); }
  } else return null;
  return (FX.tex[name] = fxTexOf(c));
}

/* 지도 위에 띄우는 붓 자국 하나 */
function fxSprite(name, color, order) {
  var tex = name === 'enso' ? (R3.zoneTex || (R3.zoneTex = ensoTexture())) : (name === 'flame' ? R3.flame : fxTex(name));
  var sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, color: color === undefined ? FX_INK : color, transparent: true, opacity: 0, depthTest: false, depthWrite: false }));
  sp.renderOrder = order || 9; R3.objs.add(sp); FX.live.push(sp);
  return sp;
}
function fxKill(sp) { var i = FX.live.indexOf(sp); if (i >= 0) FX.live.splice(i, 1); R3.objs.remove(sp); sp.material.dispose(); }
function fxClear() { while (FX.live.length) fxKill(FX.live[0]); }
function easeOut(t) { return 1 - (1 - t) * (1 - t); }
function easeIO(t) { return t < 0.5 ? 2 * t * t : 1 - 2 * (1 - t) * (1 - t); }
/* 화면에서 본 두 점 사이의 각도(스프라이트 회전에 쓴다) */
function fxAngle(p, q) {
  var a = w2s(p[0], p[1], p[2]), b = w2s(q[0], q[1], q[2]);
  if (!a || !b) return 0;
  return Math.atan2(-(b[1] - a[1]), b[0] - a[0]);
}

/* 시간표: tracks = [{a, b, on, step(0..1), off}] (밀리초). 하나의 anim 으로 돌린다 */
function fxTimeline(total, tracks, done) {
  var i;
  for (i = 0; i < tracks.length; i++) tracks[i].st = 0;
  anim(Math.max(30, total), function (t) {
    var ms = t * total;
    for (var k = 0; k < tracks.length; k++) {
      var tr = tracks[k];
      if (tr.st === 2 || (ms < tr.a && t < 1)) continue;
      if (tr.st === 0) { tr.st = 1; if (tr.on) tr.on(); }
      var u = (t >= 1 || tr.b <= tr.a) ? 1 : clamp((ms - tr.a) / (tr.b - tr.a), 0, 1);
      if (tr.step) tr.step(u);
      if (u >= 1) { tr.st = 2; if (tr.off) tr.off(); }
    }
  }, done);
  return total;
}
/* 붓 자국 하나를 나타냈다 지우는 길: 크기 s0→s1, 진하기는 금세 올랐다가 서서히 빠진다 */
function fxMark(tracks, a, dur, name, color, p, s0, s1, rot, opt) {
  var sp = null; opt = opt || {};
  tracks.push({ a: a, b: a + dur,
    on: function () { sp = fxSprite(name, color, opt.order); sp.position.set(p[0], p[1] + (opt.dy === undefined ? 0.7 : opt.dy), p[2]); sp.material.rotation = rot || 0; },
    step: function (u) {
      var s = (s0 + (s1 - s0) * easeOut(u)) * FXK, k = opt.aspect || 1;
      sp.scale.set(s, s * k, 1);
      sp.material.opacity = (opt.alpha || 1) * (u < 0.15 ? u / 0.15 : Math.pow(1 - (u - 0.15) / 0.85, opt.fade || 1.3));
      if (opt.spin) sp.material.rotation = (rot || 0) + opt.spin * u;
      if (opt.rise) sp.position.y = p[1] + (opt.dy === undefined ? 0.7 : opt.dy) + opt.rise * u;
    },
    off: function () { if (sp) fxKill(sp); } });
}
/* 걸음마다 이는 먼지 */
function fxDust(x, y, z, k) {
  if (!R3 || !R3.ready || cam.z < 0.34) return;
  var sp = fxSprite('puff', FX_WASH, 2.5), ox = (Math.random() - 0.5) * 0.3;
  sp.position.set(x + ox, y + 0.12, z + 0.1);
  anim(520, function (t) { var s = (0.5 + 0.9 * t) * (k || 1); sp.scale.set(s, s * 0.7, 1); sp.material.opacity = 0.55 * (1 - t); sp.position.y = y + 0.12 + 0.25 * t; }, function () { fxKill(sp); });
}
/* 화면 흔들기(큰 타격) */
function fxShake(px, ms) {
  if (!cv) return;
  anim(ms || 220, function (t) { var k = (1 - t) * px; cv.style.transform = t >= 1 ? '' : 'translate(' + (Math.sin(t * 40) * k).toFixed(1) + 'px,' + (Math.cos(t * 33) * k * 0.7).toFixed(1) + 'px)'; });
}
/* 낙관처럼 찍히는 글씨 */
function fxStamp(c, r, text, delay) {
  var el = document.createElement('div'); el.className = 'stamp'; el.textContent = text; el.style.opacity = 0;
  $('fx').appendChild(el);
  UI.floats.push({ p: hexPos(c, r), el: el, t0: performance.now() + (delay || 0), dur: 1700, stamp: true }); UI.render = true;
}

/* 부대·거점 그림을 다루는 작은 도우미 */
function fxPut(o, p) { o.g.position.set(p[0], p[1], p[2]); if (o.ring) o.ring.position.set(p[0], p[1] + 0.04, p[2]); }
function fxFace(o, fromP, toP) {
  if (!o.sp || Math.abs(toP[0] - fromP[0]) < 0.2) return;
  var f = toP[0] < fromP[0] ? -1 : 1;
  if (f !== o.face) { o.face = f; setSprite(o.sp, o.sp.userData.key, UNIT_W, f < 0); }
}
function fxLerp(p, q, t) { var x = p[0] + (q[0] - p[0]) * t, z = p[2] + (q[2] - p[2]) * t; return [x, groundY(x, z), z]; }
/* 맞아서 떨리고 붉게 물드는 길 */
function fxHurt(tracks, a, o, home, amp) {
  if (!o) return;
  tracks.push({ a: a, b: a + 330,
    step: function (u) {
      var k = 1 - u, dx = Math.sin(u * 20) * k * (amp || 0.13);
      o.g.position.set(home[0] + dx, home[1], home[2]);
      if (o.sp) o.sp.material.color.setRGB(1, 1 - 0.55 * k, 1 - 0.62 * k);
    },
    off: function () { o.g.position.set(home[0], home[1], home[2]); if (o.sp) o.sp.material.color.setRGB(1, 1, 1); } });
}
/* 흩어지며 사라지는 길(궤멸) */
function fxVanish(tracks, a, o, p) {
  if (!o) return;
  fxMark(tracks, a, 900, 'splat', FX_INK, p, 0.7, 2.3, Math.random() * 6.28, { dy: 0.3, alpha: 0.8, fade: 1.0, order: 2.6 });
  tracks.push({ a: a, b: a + 560,
    step: function (u) {
      var k = 1 - u;
      o.sp.material.opacity = k; o.lab.sp.material.opacity = k; if (o.fc) o.fc.sp.material.opacity = k; if (o.ring) o.ring.material.opacity = 0.6 * k;
      o.g.position.y = p[1] - 0.25 * u;
    },
    off: function () { o.g.visible = false; if (o.ring) o.ring.visible = false; o.gone = true; } });
}
/* 화살 무리: n 발이 포물선으로 날아간다 */
var VOLLEY = { fly0: 400, flyK: 30, gap: 260, w: 1.9, h: 0.40, stick: 620 };      // v0.20: 날아가는 시간(ms) = fly0 + flyK × 거리 · 쏘는 간격 · 화살 크기 · 꽂힌 화살이 남는 시간
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
}

/* ---------- 공격·전법·계략 한 번을 그려 보인다 ----------
   res 는 규칙 쪽 결과(actEv 가 붙인 aid·tid·처음 자리·나중 자리 포함). onImpact 는 타격 순간에 한 번(숫자 띄우기·소리).
   돌려주는 값은 걸리는 시간(밀리초). */
function animAct(res, done, onImpact) {
  var fin = function () { if (done) done(); };
  if (!R3 || !R3.ready || !res || res.ac0 === undefined) { if (onImpact) onImpact(); fin(); return 0; }
  var A = R3.units[res.aid] || null, T = res.tid >= 0 ? (R3.units[res.tid] || null) : null, B = res.tbase >= 0 ? R3.bases[res.tbase] : null;
  var pa = hexPos(res.ac0, res.ar0), pt = hexPos(res.c, res.r);
  var pa1 = res.aAlive ? hexPos(res.ac1, res.ar1) : pa, pt1 = (T && res.tAlive && res.tc1 !== undefined) ? hexPos(res.tc1, res.tr1) : pt;
  var ranged = hdist(res.ac0, res.ar0, res.c, res.r) > 1, tracks = [], hit = 170, end = 0, i;
  var ang = fxAngle(pa, pt), big = res.kind === 'tactic' && !res.fail, crit = !!res.crit;
  var touched = [];
  var voiced = typeof voiceAct === 'function' ? voiceAct(res, 0) : false;      // v0.13: 치는 쪽의 한마디(중국어 음성)
  function hold(o, p) { if (!o) return; o.anim = true; o.gone = false; fxPut(o, p); o.g.visible = true; if (o.ring) o.ring.visible = true; touched.push(o); }
  hold(A, pa); hold(T, pt);
  if (A) fxFace(A, pa, pt);
  if (T && res.kind !== 'ploy') fxFace(T, pt, pa);
  var fired = false;
  function impact() { if (fired) return; fired = true; if (onImpact) onImpact(); }
  function lunge(o, from, to, a, k, back) {                 // 다가갔다가 제자리로
    if (!o) return;
    tracks.push({ a: a, b: a + 170, on: function () { sfx('step'); }, step: function (u) { fxPut(o, fxLerp(from, to, k * easeOut(u))); } });
    if (back !== false) tracks.push({ a: a + 190, b: a + 430, step: function (u) { fxPut(o, fxLerp(from, to, k * (1 - easeIO(u)))); } });
  }
  function slashAt(a, p, col, size, rot) {
    if (size >= 2.2) fxMark(tracks, a + 70, 360, 'arc', FX_INK, p, size * 0.6, size * 1.1, (rot === undefined ? ang : rot) + 1.9, { fade: 1.7, alpha: 0.8 });      // v0.20: 큰 타격은 엇갈린 두 획
    fxMark(tracks, a + 30, 520, 'splat', FX_INK, [p[0] + (Math.random() - 0.5) * 0.5, p[1], p[2] + 0.1], size * 0.22, size * 0.52, Math.random() * 6.28, { dy: 0.5, alpha: 0.5, fade: 1.2, order: 2.7 });      // 먹이 튄다
    fxMark(tracks, a, 380, 'arc', col, p, size * 0.7, size * 1.25, rot === undefined ? ang - 1.2 + Math.random() * 0.5 : rot, { fade: 1.6 }); fxMark(tracks, a, 300, 'spark', FX_SEAL, p, size * 0.4, size * 0.95, Math.random() * 6.28, { fade: 1.2 }); }
  function tgtHome() { return T ? pt : (B ? [B.g.position.x, B.g.position.y, B.g.position.z] : pt); }
  var TH = tgtHome(), TO = T || B;

  if (res.kind === 'ploy') {
    // 계략: 붓 고리가 퍼지고, 대상에 효과
    fxMark(tracks, 0, 520, 'enso', FX_INDIGO, pa, 0.8, 2.6, Math.random() * 6.28, { dy: 0.35, fade: 1.1, spin: 1.2 });
    tracks.push({ a: 0, b: 0, on: function () { sfx('page'); } });
    hit = 300;
    if (res.ploy === '소화') { fxMark(tracks, 120, 700, 'puff', FX_INDIGO, pa, 1.2, 4.2, 0, { dy: 0.3, alpha: 0.9 }); }
    else if (res.success) {
      if (res.ploy === '화계') {
        fxMark(tracks, 160, hit - 100, 'trail', 0xf2a03c, fxLerp(pa, pt, 0.5), 2.2, 3.4, ang, { dy: 0.9, aspect: 0.16, fade: 1.2, alpha: 0.8 });      // v0.20: 불씨가 날아간다
        var blazeEnd = fxBlaze(tracks, hit, pt, 1.15, 7);
        tracks.push({ a: hit, b: hit, on: function () { sfx('fire'); } });
        fxHurt(tracks, hit + 60, T, pt, 0.14);
      } else {
        fxMark(tracks, hit - 60, 900, 'swirl', FX_INDIGO, pt, 2.6, 1.1, 0, { dy: 0.8, spin: -5, fade: 0.8 });
        fxHurt(tracks, hit + 200, T, pt, 0.08);
      }
    } else {
      fxMark(tracks, hit, 520, 'puff', FX_WASH, pt, 0.8, 1.7, 0, { dy: 0.7, rise: 0.4 });
      if (res.reflected) { fxMark(tracks, hit + 260, 800, res.ploy === '화계' ? 'flame' : 'swirl', res.ploy === '화계' ? 0xffffff : FX_INDIGO, pa, 1.0, 1.9, 0, { dy: 0.7, spin: res.ploy === '화계' ? 0 : -4 }); fxHurt(tracks, hit + 300, A, pa, 0.12); }
    }
    tracks.push({ a: hit, b: hit, on: impact });
    end = Math.max(hit + 720, typeof blazeEnd === 'number' ? blazeEnd - 260 : 0);
  } else {
    var tac = tacIdOf(res), pre = 0;                         // v0.18: 전법은 id 로 가린다(이름은 바뀔 수 있다)
    if (res.kind === 'tactic') {                             // 전법: 먼저 기합(인주빛 고리)
      fxMark(tracks, 0, 420, 'enso', FX_SEAL, pa, 0.9, 2.3, Math.random() * 6.28, { dy: 0.35, spin: 1.6, fade: 1.2 });
      if (A) tracks.push({ a: 0, b: 240, step: function (u) { var s = 1 + 0.16 * Math.sin(Math.PI * u); A.sp.scale.set(A.sp.userData.w * s, A.sp.userData.h * s, 1); } });
      tracks.push({ a: 0, b: 0, on: function () { if (!voiced) sfx('shout'); } });      // 음성이 나가면 기합 효과음은 겹치지 않게 뺀다
      pre = 230;
    }
    var bowLike = ranged || tac === 'hwasi' || tac === 'gwansi' || tac === 'nansa';
    if (bowLike) {
      // 쏘는 공격: 몸을 젖혔다가 화살 무리
      if (A) tracks.push({ a: pre, b: pre + 260, step: function (u) { fxPut(A, fxLerp(pa, pt, -0.10 * Math.sin(Math.PI * u))); } });
      var n = tac === 'nansa' ? 14 : (tac === 'gwansi' ? 1 : (big ? 9 : 6)), colA = tac === 'hwasi' && !res.fail ? FX_FIRE : FX_INK;
      tracks.push({ a: pre + 50, b: pre + 50, on: function () { sfx('bow'); if (n > 1) sfx('arrows'); } });
      if (tac === 'gwansi' && !res.fail) {                     // 꿰뚫는 한 줄기
        var far = fxLerp(pa, pt, 1.9);
        fxMark(tracks, pre + 120, 420, 'stroke', FX_SEAL, fxLerp(pa, far, 0.55), 4.2, 5.6, ang, { aspect: 0.11, fade: 1.4 });
        hit = pre + 200;
      } else hit = fxVolley(tracks, pre + 60, pa, pt, n, colA, tac === 'nansa' ? 1.9 : 0.55) - 40;
      fxMark(tracks, hit, 320, 'spark', tac === 'hwasi' ? FX_FIRE : FX_INK, TH, 0.6, 1.5, Math.random() * 6.28, {});
      if (tac === 'hwasi' && !res.fail) fxBlaze(tracks, hit, pt, 0.95, 5);                       // v0.20: 불화살이 꽂힌 자리에 불이 인다
    } else if (tac === 'seonpung' && !res.fail) {             // 주위를 한 바퀴 휩쓴다
      fxMark(tracks, pre, 620, 'enso', FX_INK, pa, 1.4, 4.3, 0, { dy: 0.45, spin: 5.5, fade: 1.1 });
      fxMark(tracks, pre + 60, 560, 'enso', FX_SEAL, pa, 1.0, 3.6, 2, { dy: 0.5, spin: 6.5, fade: 1.3, alpha: 0.8 });
      hit = pre + 230;
    } else if ((tac === 'dolgyeok' || tac === 'doljin' || tac === 'dolpa') && !res.fail) {
      // 기병 돌격: 먼지를 일으키며 들이받는다. 밀려난 적과 따라 들어간 자리까지
      var dashTo = tac === 'dolpa' ? pa1 : fxLerp(pa, pt, 0.62);
      tracks.push({ a: pre, b: pre + 210, on: function () { sfx('charge'); fxDust(pa[0], pa[1], pa[2], 1.3); },
        step: function (u) { var p = fxLerp(pa, dashTo, easeIO(u)); if (A) fxPut(A, [p[0], p[1] + Math.abs(Math.sin(u * 9)) * 0.12, p[2]]); if (u > 0.3 && u < 0.36) fxDust(p[0], p[1], p[2], 1.2); } });
      fxMark(tracks, pre + 40, 460, 'stroke', FX_INK, fxLerp(pa, pt, 0.5), 2.6, 3.9, ang, { aspect: 0.2, fade: 1.5, dy: 0.35, alpha: 0.75 });
      hit = pre + 170;
      if (A && tac !== 'dolpa') tracks.push({ a: hit + 60, b: hit + 330, step: function (u) { fxPut(A, fxLerp(dashTo, pa1, easeIO(u))); } });
    } else {
      // 근접: 달려들어 벤다
      var k = (tac === 'dolchul' || tac === 'naseon' || tac === 'idan') && !res.fail ? 0.5 : 0.4;
      lunge(A, pa, TH, pre, k, (tac !== 'idan' || res.fail) && !res.pulled);      // 견인으로 끌 때는 제자리로 돌아오지 않고 그대로 뒤로 물러선다(아래)
      hit = pre + 150;
      if (tac === 'idan' && !res.fail && A) {                  // 두 번 찌른다
        tracks.push({ a: pre + 190, b: pre + 300, step: function (u) { fxPut(A, fxLerp(pa, TH, k * (1 - 0.6 * easeIO(u)))); } });
        tracks.push({ a: pre + 300, b: pre + 420, step: function (u) { fxPut(A, fxLerp(pa, TH, k * (0.4 + 0.75 * easeOut(u)))); } });
        tracks.push({ a: pre + 440, b: pre + 680, step: function (u) { fxPut(A, fxLerp(pa, TH, k * 1.15 * (1 - easeIO(u)))); } });
        fxMark(tracks, pre + 400, 360, 'stroke', FX_SEAL, fxLerp(pa, TH, 0.9), 2.2, 3.4, ang, { aspect: 0.14, fade: 1.5 });
      }
      if ((tac === 'dolchul' || tac === 'naseon' || tac === 'idan') && !res.fail) fxMark(tracks, hit - 20, 380, 'stroke', FX_INK, fxLerp(pa, TH, 0.85), 2.2, 3.6, ang, { aspect: 0.15, fade: 1.5 });
      if (tac === 'naseon' && !res.fail) fxMark(tracks, hit, 620, 'swirl', FX_SEAL, TH, 0.6, 2.2, 0, { spin: 7, fade: 1.2 });
      if (tac === 'hoengchi' && !res.fail) fxMark(tracks, hit - 30, 460, 'arc', FX_INK, TH, 2.6, 4.4, ang - 1.57, { fade: 1.4 });
      if (tac === 'galkwi' && !res.fail) fxMark(tracks, hit - 40, 440, 'arc', FX_SEAL, [TH[0], TH[1] - 0.15, TH[2]], 1.5, 2.9, ang + 1.57, { fade: 1.5 });   // 거는 갈고리 획
      if (res.pulled && A) {                                   // v0.18 견인: 건 채로 뒷걸음질 — 나는 뒤 칸으로, 적은 내가 섰던 자리로(적은 아래 '자리 옮김'이 끈다)
        var pull0 = fxLerp(pa, TH, k);
        fxMark(tracks, hit + 40, 420, 'stroke', FX_SEAL, fxLerp(pa, TH, 0.5), 1.6, 2.6, ang, { aspect: 0.13, fade: 1.4 });
        tracks.push({ a: hit + 60, b: hit + 400, on: function () { sfx('step'); fxDust(pa[0], pa[1], pa[2], 1.0); }, step: function (u) { fxPut(A, fxLerp(pull0, pa1, easeIO(u))); } });
      }
    }
    // 타격
    if (!bowLike && tac !== 'seonpung') slashAt(hit, TH, big || crit ? FX_SEAL : FX_INK, big ? 2.5 : (crit ? 2.3 : 1.8));
    if (TO) fxHurt(tracks, hit + 20, TO, TH, big || crit ? 0.2 : (B && !T ? 0.09 : 0.13));
    if (B && !T) for (i = 0; i < 3; i++) fxMark(tracks, hit + 40 + i * 70, 620, 'puff', FX_WASH, [TH[0] + (i - 1) * 0.9, TH[1], TH[2] + 0.2], 0.7, 1.8, 0, { dy: 0.25, rise: 0.5, alpha: 0.9, order: 2.6 });
    tracks.push({ a: hit, b: hit, on: function () { impact(); if (big || crit || res.fell) fxShake(big ? 5 : 3.5, 240); } });
    end = hit + 420;
    // 부가 대상(횡소·일소·관통·전우)
    if (res.extra) for (i = 0; i < res.extra.length; i++) (function (xh, i) {
      var p = hexPos(xh.c, xh.r), ou = UAT[K(xh.c, xh.r)], oo = xh.id !== undefined ? (R3.units[xh.id] || null) : (ou ? R3.units[ou.id] : null);
      fxMark(tracks, hit + 60 + i * 70, 340, 'arc', FX_INK, p, 1.2, 2.0, Math.random() * 6.28, { fade: 1.6 });
      if (oo && oo !== A && oo !== T && (oo.keep || !oo.anim)) {            // v0.22: 붙잡아 둔 그림을 그 자리에서 흔들고, 궤멸했으면 흩어 보낸다
        if (touched.indexOf(oo) < 0) { oo.anim = true; touched.push(oo); }
        fxHurt(tracks, hit + 80 + i * 70, oo, p, 0.11);
        if (xh.dead) { fxVanish(tracks, hit + 300 + i * 70, oo, p); end = Math.max(end, hit + 900 + i * 70); }
      }
      end = Math.max(end, hit + 460 + i * 70);
    })(res.extra[i], i);
    // 자리 옮김: 밀려남 · (v0.18) 끌려옴 — 끌려올 때는 조금 늦게, 끄는 쪽을 따라온다
    if (T && res.tAlive && (pt1[0] !== pt[0] || pt1[2] !== pt[2])) {
      var mv0 = hit + (res.pulled ? 130 : 40), mv1 = hit + (res.pulled ? 440 : 300);
      tracks.push({ a: mv0, b: mv1, on: function () { fxDust(pt[0], pt[1], pt[2], 1.1); }, step: function (u) { fxPut(T, fxLerp(pt, pt1, res.pulled ? easeIO(u) : easeOut(u))); } });
      end = Math.max(end, mv1 + 40);
    }
    if (res.slam) fxMark(tracks, hit + 120, 420, 'spark', FX_SEAL, pt1, 0.8, 1.9, 0.5, {});
    // 연전
    if (res.dmg2) { slashAt(hit + 300, pt1, FX_INK, 1.7, ang + 1.3); fxHurt(tracks, hit + 320, T, pt1, 0.12); end = Math.max(end, hit + 700); }
    // 혼란
    if (res.confused) { fxMark(tracks, hit + 260, 800, 'swirl', FX_INDIGO, pt1, 2.0, 1.0, 0, { dy: 1.0, spin: -5, fade: 0.9 }); end = Math.max(end, hit + 900); }
    // 반격
    if (res.counter && !res.killed) {
      var c0 = Math.max(end - 60, hit + 380), ah = bowLike ? pa : pa1;
      if (T && !ranged) { lunge(T, pt1, ah, c0, 0.3); slashAt(c0 + 150, ah, FX_WASH, 1.5, ang + Math.PI - 1.0); }
      else if (T) fxVolley(tracks, c0, pt1, ah, 4, FX_WASH, 0.5);
      else if (B) { fxVolley(tracks, c0, TH, ah, 6, FX_WASH, 0.6); }
      fxHurt(tracks, c0 + (T && !ranged ? 170 : 330), A, ah, 0.11);
      (function (melee) { tracks.push({ a: c0 + (melee ? 150 : 0), b: c0 + (melee ? 150 : 0), on: function () { sfx(melee ? 'counter' : 'bow'); } }); })(!!(T && !ranged));
      end = Math.max(end, c0 + 620);
    }
    // 일기토: 크게 엇갈린 두 획
    if (res.duel) {
      var mid = fxLerp(pa1, pt1, 0.5), d0 = end;
      fxMark(tracks, d0, 620, 'stroke', FX_SEAL, mid, 2.4, 4.4, 0.7, { aspect: 0.17, dy: 0.8, fade: 1.2 });
      fxMark(tracks, d0 + 110, 620, 'stroke', FX_INK, mid, 2.4, 4.4, 2.44, { aspect: 0.17, dy: 0.8, fade: 1.2 });
      tracks.push({ a: d0, b: d0, on: function () { sfx('duel'); } });
      tracks.push({ a: d0 + 110, b: d0 + 110, on: function () { fxShake(5, 260); } });
      end = d0 + 780;
    }
  }
  // 궤멸
  if (res.killed && T) { fxVanish(tracks, end - 120, T, pt1); tracks.push({ a: end - 60, b: end - 60, on: function () { sfx('rout'); fxStamp(res.tc1 !== undefined ? res.tc1 : res.c, res.tr1 !== undefined ? res.tr1 : res.r, '궤멸'); } }); end += 520; }
  if ((res.selfDead || !res.aAlive) && A) { fxVanish(tracks, end - 120, A, pa1); end += 480; }
  if (res.destroyed) { fxMark(tracks, hit + 80, 800, 'splat', FX_INK, pt, 0.8, 2.4, 1, { dy: 0.3, alpha: 0.75, order: 2.6 }); end = Math.max(end, hit + 700); }
  tracks.push({ a: end, b: end, on: impact });
  return fxTimeline(end + 30, tracks, function () {
    if (typeof freeAct === 'function') freeAct(res);                  // v0.22: 붙잡아 둔 거점 · 불을 푼다(함락한 거점은 함락 장면이 푼다)
    for (var q = 0; q < touched.length; q++) { var o = touched[q]; o.anim = false; o.keep = false; o.c = -1; o.sig = ''; if (o.sp && !o.gone) { o.sp.material.color.setRGB(1, 1, 1); o.sp.scale.set(o.sp.userData.w, o.sp.userData.h, 1); } }
    cv.style.transform = ''; requestDraw(); fin();
  });
}

/* 성이 넘어가는 장면: 성이 떨리고 먼지가 일며 낙관이 찍힌다 */
function fxFall(b, text) {
  if (!R3 || !R3.ready) return 0;
  if (typeof freeBase === 'function') freeBase(b.id);                 // v0.22: 이제 새 주인의 빛깔로(붙잡아 두었다면 여기서 푼다)
  var o = R3.bases[b.id], p = hexPos(b.c, b.r), tracks = [], i;
  if (o) fxHurt(tracks, 0, o, [o.g.position.x, o.g.position.y, o.g.position.z], 0.2);
  for (i = 0; i < 6; i++) fxMark(tracks, i * 60, 760, 'puff', FX_WASH, [p[0] + (Math.random() - 0.5) * 2.6, p[1], p[2] + (Math.random() - 0.5) * 1.2], 0.9, 2.4, 0, { dy: 0.3, rise: 0.7, alpha: 0.95, order: 2.6 });
  fxMark(tracks, 80, 900, 'enso', FX_SEAL, p, 1.6, 5.2, Math.random() * 6.28, { dy: 0.3, spin: 1.2, fade: 1.2, order: 2.7 });
  fxShake(5, 320); fxStamp(b.c, b.r, text || '함락', 180);
  return fxTimeline(900, tracks);
}
/* 출진: 성에서 걸어 나온다 */
function fxDeploy(u, b, done) {
  var o = R3 && R3.ready ? R3.units[u.id] : null;
  if (!o) { if (done) done(); return; }
  var p0 = hexPos(b.c, b.r), p1 = hexPos(u.c, u.r);
  o.anim = true; fxFace(o, p0, p1);
  var step = function (t) {
    var e = easeOut(t), p = fxLerp(p0, p1, e), s = 0.55 + 0.45 * e;
    fxPut(o, [p[0], p[1] + Math.sin(Math.PI * t) * 0.18, p[2]]);
    o.sp.scale.set(o.sp.userData.w * s, o.sp.userData.h * s, 1); o.sp.material.opacity = Math.min(1, 0.2 + t * 1.6);
  };
  step(0);                                                    // v0.22.1: 첫 모습(성 안 · 작고 옅게)을 바로 입힌다 — 나갈 칸에 선 모습이 한 장이라도 먼저 그려지지 않게
  anim(430, step, function () { o.sp.scale.set(o.sp.userData.w, o.sp.userData.h, 1); o.anim = false; o.c = -1; o.sig = ''; fxDust(p1[0], p1[1], p1[2], 1.2); requestDraw(); if (done) done(); });
}
