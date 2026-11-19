#!/usr/bin/env python3
"""v0.4: ui3d.js 를 수묵 지도로. build/ui3d.v03.js → src/ui3d.js (여러 번 돌려도 같은 결과)"""
import os
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
s = open(os.path.join(root, 'build', 'ui3d.v03.js'), encoding='utf8').read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new)

# ---- 색: 종이·먹 ----
rep("Z_MIN = 0.14, Z_MAX = 2.3, FOGC = 0xaab2ac;", "Z_MIN = 0.14, Z_MAX = 2.3, FOGC = 0xefe9db;\nvar INK = '#1b1a18', PAPER = '#f4efe3', SEAL = '#b5332a', NEUTRAL = '#8d877b';")
rep("new THREE.MeshBasicMaterial({ color: 0x4a4a44 })", "new THREE.MeshBasicMaterial({ color: 0xefe9db })")
rep("var pos = [], idx = [], n = 0, w = 0.105;", "var pos = [], idx = [], n = 0, w = 0.062;")
rep("new THREE.MeshBasicMaterial({ color: 0xdcc48e, transparent: true, opacity: 0.78,", "new THREE.MeshBasicMaterial({ color: 0x2b2722, transparent: true, opacity: 0.46,")
# 나무: 짙은 먹점
rep("cols[i * 3] = 0.16 + 0.30 * t; cols[i * 3 + 1] = 0.30 + 0.34 * t; cols[i * 3 + 2] = 0.14 + 0.20 * t;", "cols[i * 3] = 0.12 + 0.20 * t; cols[i * 3 + 1] = 0.15 + 0.23 * t; cols[i * 3 + 2] = 0.13 + 0.19 * t;")
rep("col.setRGB(0.80 + 0.35 * e[4], 0.88 + 0.22 * hash2(j, i), 0.75 + 0.3 * e[4]);", "var tg = 0.72 + 0.5 * e[4]; col.setRGB(tg, tg * (0.98 + 0.08 * hash2(j, i)), tg);")
# 불: 밝은 종이 위에서도 보이게(더하기 섞기 → 보통 섞기), 주홍 먹빛
rep("g.addColorStop(0, 'rgba(255,244,190,1)'); g.addColorStop(0.35, 'rgba(255,170,50,0.9)'); g.addColorStop(0.75, 'rgba(220,70,20,0.45)'); g.addColorStop(1, 'rgba(160,30,10,0)');",
    "g.addColorStop(0, 'rgba(255,226,150,0.98)'); g.addColorStop(0.32, 'rgba(236,120,44,0.95)'); g.addColorStop(0.72, 'rgba(190,52,36,0.78)'); g.addColorStop(1, 'rgba(120,24,18,0)');")
rep("depthTest: false, depthWrite: false, blending: THREE.AdditiveBlending }));", "depthTest: false, depthWrite: false }));")

# ---- 지형 셰이더: 먹 격자, 담채 겹침 ----
rep("  '  col *= 0.90 + 0.20 * dn + nearK * 0.20 * (dn2 - 0.5);',", "  '  col *= 0.955 + 0.09 * dn + nearK * 0.10 * (dn2 - 0.5);',")
rep("  '  col = mix(col, col * 0.55, line * gk * 0.5);',", "  '  col = mix(col, vec3(0.105, 0.10, 0.094), line * gk * 0.21);',")
rep("""  '  if (ov.a > 0.004) {',
  '    float edge = 1.0 - smoothstep(0.03, 0.05 + aa * 2.0, e);',
  '    col = mix(col, ov.rgb, ov.a * (0.50 + 0.50 * edge));',
  '    col += ov.rgb * edge * ov.a * 0.30;',
  '  }',""",
"""  '  if (ov.a > 0.004) {',
  '    if (ov.a < 0.30) {',                                      // 담채: 세력권·성역. 칸 테두리 없이 번지듯
  '      col = mix(col, col * mix(vec3(1.0), ov.rgb, 0.85), ov.a * 2.6);',
  '    } else {',                                                // 이동·공격 범위: 칸 가장자리를 짙게
  '      float edge = 1.0 - smoothstep(0.03, 0.06 + aa * 2.0, e);',
  '      col = mix(col, ov.rgb, ov.a * (0.34 + 0.66 * edge));',
  '    }',
  '  }',""")

# ---- 이름표 ----
rep("""  var bw = w - (badge ? 22 : 0);
  rr(x, 2, 2, bw - 4, h - 4, 7); x.fillStyle = bg; x.fill(); x.lineWidth = 2.5; x.strokeStyle = border; x.stroke();
  var y = 5;
  x.textAlign = 'center'; x.textBaseline = 'top';
  for (i = 0; i < lines.length; i++) {
    var ln = lines[i]; x.font = (ln.bold || 700) + ' ' + ln.px * S + 'px ' + (ln.font || FONT_B);
    x.fillStyle = 'rgba(0,0,0,0.55)'; x.fillText(ln.t, bw / 2 + 1.5, y + 2);
    x.fillStyle = ln.color || '#fff'; x.fillText(ln.t, bw / 2, y); y += ln.px * S * 1.18;
  }
  if (badge) { x.beginPath(); x.arc(w - 17, 17, 15, 0, 6.3); x.fillStyle = '#c0392b'; x.fill(); x.lineWidth = 2; x.strokeStyle = '#fff'; x.stroke(); x.fillStyle = '#fff'; x.font = '700 20px ' + FONT_B; x.textBaseline = 'middle'; x.fillText(badge, w - 17, 18); }""",
"""  var bw = w - (badge ? 22 : 0), sel = border === SEAL;
  // 석채(石彩) 빛 판에 종이 빛 글씨, 가는 먹선. 고른 것은 인주색 겹테
  rr(x, 3, 3, bw - 6, h - 6, 3); x.fillStyle = bg; x.fill();
  x.lineWidth = sel ? 4 : 1.6; x.strokeStyle = sel ? SEAL : border; x.stroke();
  if (sel) { rr(x, 6.5, 6.5, bw - 13, h - 13, 1.5); x.lineWidth = 1.2; x.strokeStyle = 'rgba(251,246,234,0.75)'; x.stroke(); }
  var y = 5;
  x.textAlign = 'center'; x.textBaseline = 'top';
  for (i = 0; i < lines.length; i++) {
    var ln = lines[i]; x.font = (ln.bold || 700) + ' ' + ln.px * S + 'px ' + (ln.font || FONT_B);
    x.fillStyle = 'rgba(20,18,16,0.38)'; x.fillText(ln.t, bw / 2 + 1, y + 1.5);
    x.fillStyle = ln.color || '#fbf6ea'; x.fillText(ln.t, bw / 2, y); y += ln.px * S * 1.18;
  }
  if (badge) { rr(x, w - 31, 3, 28, 28, 4); x.fillStyle = SEAL; x.fill(); x.lineWidth = 1.5; x.strokeStyle = '#fbf6ea'; x.stroke(); x.fillStyle = '#fbf6ea'; x.font = '800 19px ' + FONT_B; x.textBaseline = 'middle'; x.fillText(badge, w - 17, 18); }""")
# 얼굴 딱지: 종이 원 위에 먹 초상을 겹쳐 그린다
rep("""  var g = x.createRadialGradient(S / 2, S * 0.38, 2, S / 2, S / 2, S * 0.62); g.addColorStop(0, '#7f9ab1'); g.addColorStop(1, '#1f3347');
  x.save(); x.beginPath(); x.arc(S / 2, S / 2, S / 2 - 4, 0, 6.3); x.clip(); x.fillStyle = g; x.fillRect(0, 0, S, S);
  try { var iw = img.naturalWidth, ih = img.naturalHeight; x.drawImage(img, iw * 0.21, ih * 0.02, iw * 0.58, ih * 0.58, 3, 3, S - 6, S - 6); } catch (e) { /* 바탕만 */ }
  x.restore();
  x.beginPath(); x.arc(S / 2, S / 2, S / 2 - 4, 0, 6.3); x.lineWidth = 5; x.strokeStyle = ring; x.stroke();
  x.beginPath(); x.arc(S / 2, S / 2, S / 2 - 1.3, 0, 6.3); x.lineWidth = 1.6; x.strokeStyle = 'rgba(12,16,22,0.92)'; x.stroke();""",
"""  x.save(); x.beginPath(); x.arc(S / 2, S / 2, S / 2 - 4, 0, 6.3); x.clip(); x.fillStyle = '#f6f1e6'; x.fillRect(0, 0, S, S);
  x.globalCompositeOperation = 'multiply';
  try { var iw = img.naturalWidth, ih = img.naturalHeight; x.drawImage(img, iw * 0.20, ih * 0.03, iw * 0.60, ih * 0.60, 3, 3, S - 6, S - 6); } catch (e) { /* 바탕만 */ }
  x.restore();
  x.beginPath(); x.arc(S / 2, S / 2, S / 2 - 4, 0, 6.3); x.lineWidth = 5; x.strokeStyle = ring; x.stroke();
  x.beginPath(); x.arc(S / 2, S / 2, S / 2 - 1.3, 0, 6.3); x.lineWidth = 1.4; x.strokeStyle = 'rgba(27,26,24,0.9)'; x.stroke();""")

# ---- 거점: 석채 판 + 성역 붓 고리 ----
rep("""    var mineB = b.owner === G.player, col = b.owner >= 0 ? G.factions[b.owner].color : '#7d766a';""",
"""    var mineB = b.owner === G.player, col = b.owner >= 0 ? G.factions[b.owner].color : NEUTRAL;
    if (b.kind === 'city' && !o.zone) {                                 // 성역(성 둘레 ZONE_R 칸)을 붓으로 두른 고리
      var zr = (ZONE_R + 0.5) * SQ3 * 0.94;
      o.zone = new THREE.Mesh(R3.zoneGeo || (R3.zoneGeo = new THREE.PlaneGeometry(2, 2).rotateX(-Math.PI / 2)), new THREE.MeshBasicMaterial({ map: R3.zoneTex || (R3.zoneTex = ensoTexture()), transparent: true, opacity: 0.6, depthTest: false, depthWrite: false }));
      o.zone.scale.set(zr, 1, zr * 0.93); o.zone.rotation.y = hash2(i, 77) * 6.283; o.zone.position.set(o.g.position.x, o.g.position.y + 0.06, o.g.position.z); o.zone.renderOrder = 0.5; R3.objs.add(o.zone);
    }
    if (o.zone && o.zcol !== col) { o.zcol = col; o.zone.material.color.set(shade(col, 0.82)); }""")
rep("""      if (b.owner >= 0) ls.push({ t: fmt(b.troops), px: 10.5, color: '#f3e7c8' });
      drawLabel(o.lab, ls, shade(col, 0.72), (UI.sel && UI.sel.kind === 'base' && UI.sel.id === b.id) ? '#ffe9a6' : '#d9bb72', mineB && idleN[b.id] ? idleN[b.id] : 0);""",
"""      if (b.owner >= 0) ls.push({ t: fmt(b.troops), px: 10.5, color: '#f6efdf' });
      drawLabel(o.lab, ls, shade(col, 0.86), (UI.sel && UI.sel.kind === 'base' && UI.sel.id === b.id) ? SEAL : INK, mineB && idleN[b.id] ? idleN[b.id] : 0);""")
# 부대
rep("new THREE.MeshBasicMaterial({ color: fcol, transparent: true, opacity: 0.62, depthTest: false, depthWrite: false }));", "new THREE.MeshBasicMaterial({ color: fcol, map: R3.dotTex || (R3.dotTex = inkDotTexture()), transparent: true, opacity: 0.78, depthTest: false, depthWrite: false }));")
rep("""      o.sp.material.color.setHex(dim ? 0x8d8d8d : 0xffffff); o.ring.material.color.set(fcol); o.ring.material.opacity = dim ? 0.38 : 0.62;""",
"""      o.sp.material.color.setHex(0xffffff); o.sp.material.opacity = dim ? 0.52 : 1; o.ring.material.color.set(fcol); o.ring.material.opacity = dim ? 0.4 : 0.78;""")
rep("""lns = [{ t: mark + fmt(u.troops), px: 12, bold: 800, color: u.status ? '#e4c6ff' : '#fff3c9' }];
      if (showName) lns.unshift({ t: L.n, px: 10.5, color: '#fff' });
      drawLabel(o.lab, lns, shade(fcol, dim ? 0.42 : 0.66), isSel ? '#fff' : 'rgba(20,14,8,0.9)');""",
"""lns = [{ t: mark + fmt(u.troops), px: 12, bold: 800, color: '#fbf6ea' }];
      if (showName) lns.unshift({ t: L.n, px: 10.5, font: FONT_D, bold: 900, color: '#fbf6ea' });
      drawLabel(o.lab, lns, dim ? mixHex(fcol, '#8d877b', 0.6) : shade(fcol, 0.84), isSel ? SEAL : INK);""")
rep("if (fim) { drawFace(o.fc, fim, isSel ? '#ffffff' : fcol);", "if (fim) { drawFace(o.fc, fim, isSel ? SEAL : fcol);")
rep("function shade(hex, k) {", """function mixHex(a, b, t) { var x = rgbOf(a), y = rgbOf(b); return 'rgb(' + Math.round(x[0] + (y[0] - x[0]) * t) + ',' + Math.round(x[1] + (y[1] - x[1]) * t) + ',' + Math.round(x[2] + (y[2] - x[2]) * t) + ')'; }
/* 붓으로 한 번에 두른 고리(성역 표시): 굵기가 변하고 한쪽이 트여 있다 */
function ensoTexture() {
  var n = 256, c = document.createElement('canvas'); c.width = c.height = n;
  var x = c.getContext('2d'), i, s = 91;
  function rnd() { s = (s * 1664525 + 1013904223) | 0; return ((s >>> 8) & 0xffff) / 65535; }
  x.translate(n / 2, n / 2);
  for (var pass = 0; pass < 3; pass++) {
    var a0 = 0.5 + rnd() * 0.3, a1 = a0 + 5.45 + rnd() * 0.4, steps = 220;
    for (i = 0; i < steps; i++) {
      var t = i / (steps - 1), a = a0 + (a1 - a0) * t, r = 112 + Math.sin(a * 3.1 + pass) * 1.6 + (rnd() - 0.5) * 1.4;
      var wd = (2.2 + 4.6 * Math.sin(Math.PI * Math.pow(t, 0.8))) * (pass ? 0.55 : 1), al = (0.34 + 0.4 * Math.sin(Math.PI * t)) * (pass ? 0.5 : 1) * (0.6 + 0.4 * rnd());
      x.fillStyle = 'rgba(255,255,255,' + al.toFixed(3) + ')';
      x.beginPath(); x.arc(Math.cos(a) * (r - pass * 3.5), Math.sin(a) * (r - pass * 3.5), wd, 0, 6.3); x.fill();
    }
  }
  var t2 = new THREE.CanvasTexture(c); t2.minFilter = THREE.LinearMipmapLinearFilter; return t2;
}
/* 부대 발밑의 먹점: 가운데가 짙고 가장자리가 번진 점 */
function inkDotTexture() {
  var n = 96, c = document.createElement('canvas'); c.width = c.height = n;
  var x = c.getContext('2d'), g = x.createRadialGradient(n / 2, n / 2, 4, n / 2, n / 2, n / 2);
  g.addColorStop(0, 'rgba(255,255,255,0.95)'); g.addColorStop(0.62, 'rgba(255,255,255,0.86)'); g.addColorStop(0.84, 'rgba(255,255,255,0.42)'); g.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = g; x.fillRect(0, 0, n, n);
  return new THREE.CanvasTexture(c);
}
function shade(hex, k) {""")

# ---- 덧칠: 세력권은 성역과 같은 넓이의 담채, 범위는 쪽빛·주홍 ----
rep("var col = rgbOf(G.factions[b.owner].color), rad = b.kind === 'gate' ? 1 : 3;", "var col = rgbOf(G.factions[b.owner].color), rad = b.kind === 'gate' ? 1 : ZONE_R;")
rep("if (t !== 120 && t !== 115 && t !== 109) ovPut(k, col, 52);", "if (t !== 120 && t !== 115 && t !== 109) ovPut(k, col, 44);")
rep("ovPut(K(b.plots[j].c, b.plots[j].r), [255, 240, 196], 96);", "ovPut(K(b.plots[j].c, b.plots[j].r), [176, 124, 34], 88);")
rep("ovPut(UI.march.path[i], [255, 236, 170], 120);", "ovPut(UI.march.path[i], [47, 79, 111], 96);")
rep("if (BAT[k] !== undefined) ovPut(k, [255, 215, 106], 150); else ovPut(k, [72, 150, 255], 104);", "if (BAT[k] !== undefined) ovPut(k, [176, 124, 34], 170); else ovPut(k, ZONE[k] !== ZONE[K(su.c, su.r)] ? [96, 118, 140] : [47, 79, 111], 122);")
rep("ovPut(K(ats[i].c, ats[i].r), [236, 62, 46], 150);", "ovPut(K(ats[i].c, ats[i].r), [181, 51, 42], 172);")
rep("ovPut(K(UMAP[UI.sel.id].c, UMAP[UI.sel.id].r), [255, 255, 255], 120);", "ovPut(K(UMAP[UI.sel.id].c, UMAP[UI.sel.id].r), [27, 26, 24], 96);")
rep("if (UI.sel && UI.sel.kind === 'base') ovPut(K(G.bases[UI.sel.id].c, G.bases[UI.sel.id].r), [255, 215, 106], 150);", "if (UI.sel && UI.sel.kind === 'base') ovPut(K(G.bases[UI.sel.id].c, G.bases[UI.sel.id].r), [176, 124, 34], 150);")
rep("if (UI.target) ovPut(K(UI.target.c, UI.target.r), [255, 215, 106], 215);", "if (UI.target) ovPut(K(UI.target.c, UI.target.r), [181, 51, 42], 225);")
# 철 따라 종이 빛만 살짝
rep("if (m >= 3 && m <= 5) tn.set(1.0, 1.02, 0.98); else if (m >= 6 && m <= 8) tn.set(0.97, 1.03, 0.94); else if (m >= 9 && m <= 11) tn.set(1.07, 0.99, 0.86); else tn.set(1.02, 1.03, 1.08);",
    "if (m >= 3 && m <= 5) tn.set(0.995, 1.0, 0.985); else if (m >= 6 && m <= 8) tn.set(0.985, 1.0, 0.975); else if (m >= 9 && m <= 11) tn.set(1.0, 0.985, 0.95); else tn.set(0.99, 0.995, 1.01);")

# ---- 뜨는 글씨·고리 ----
rep("el.style.color = color || '#fff'; el.style.opacity = 0;\n  $('fx').appendChild(el);\n  UI.floats.push({ p: hexPos(c, r), el: el, t0: performance.now() + (delay || 0), dur: 1200 });",
    "el.style.color = color || INK; el.style.opacity = 0;\n  $('fx').appendChild(el);\n  UI.floats.push({ p: hexPos(c, r), el: el, t0: performance.now() + (delay || 0), dur: 1350 });")
rep("el.className = 'ring'; el.style.borderColor = color || '#fff'; el.style.opacity = 0;", "el.className = 'ring'; el.style.borderColor = color || INK; el.style.opacity = 0;")

# ---- 이동 연출: 걸음마다 들썩이고 먼지(담묵)가 인다 ----
rep("""  var dur = Math.min(900, 85 * path.length + 80) * (slow || 1), last = -1;
  anim(dur, function (t) {
    var f = t * (pts.length - 1), i2 = Math.min(pts.length - 2, Math.floor(f)), w = f - i2, a = pts[i2], b = pts[i2 + 1];
    var x = a[0] + (b[0] - a[0]) * w, z = a[2] + (b[2] - a[2]) * w, y = groundY(x, z);
    o.g.position.set(x, y, z); o.ring.position.set(x, y + 0.04, z);
    if (i2 !== last) { last = i2; sfx('step');""",
"""  var dur = Math.min(1500, 150 * path.length + 120) * (slow || 1), last = -1, hop = vis.type === 'cav' ? 0.16 : (vis.type === 'ram' || vis.type === 'trans' ? 0.04 : 0.10);
  if (!vis.type) { var uu = UMAP[vis.id]; if (uu) hop = uu.type === 'cav' ? 0.16 : (uu.type === 'ram' || uu.type === 'trans' ? 0.04 : 0.10); }
  anim(dur, function (t) {
    var f = t * (pts.length - 1), i2 = Math.min(pts.length - 2, Math.floor(f)), w = f - i2, a = pts[i2], b = pts[i2 + 1];
    var x = a[0] + (b[0] - a[0]) * w, z = a[2] + (b[2] - a[2]) * w, y = groundY(x, z);
    o.g.position.set(x, y + Math.abs(Math.sin(w * Math.PI * 2)) * hop, z); o.ring.position.set(x, y + 0.04, z);
    if (i2 !== last) { last = i2; sfx('step'); if (typeof fxDust === 'function') fxDust(a[0], a[1], a[2], 0.8);""")

# ---- 미니맵 ----
rep("else { x.fillStyle = '#56624a'; x.fillRect(0, 0, w, h); }", "else { x.fillStyle = '#efe9db'; x.fillRect(0, 0, w, h); }")
rep("x.fillStyle = b.owner >= 0 ? G.factions[b.owner].color : '#d8d2c2'; x.fillRect(p[0] * sx - s / 2, p[1] * sz - s / 2, s, s);\n    x.strokeStyle = b.owner === G.player ? '#fff' : 'rgba(0,0,0,0.7)'; x.lineWidth = 1;",
    "x.fillStyle = b.owner >= 0 ? G.factions[b.owner].color : '#a8a295'; x.fillRect(p[0] * sx - s / 2, p[1] * sz - s / 2, s, s);\n    x.strokeStyle = b.owner === G.player ? SEAL : 'rgba(27,26,24,0.8)'; x.lineWidth = b.owner === G.player ? 1.6 : 1;")
rep("x.closePath(); x.lineWidth = 2; x.strokeStyle = '#fff'; x.stroke();", "x.closePath(); x.lineWidth = 1.6; x.strokeStyle = SEAL; x.stroke();")

# ---- 낙관(찍히는 글씨) ----
rep("      else { f.el.style.opacity = ft < 0.7 ? 1 : (1 - ft) / 0.3; f.el.style.transform = 'translate(-50%,-100%) translate(' + sp[0] + 'px,' + (sp[1] - ft * 38) + 'px)'; }",
    "      else if (f.stamp) { var ss = ft < 0.12 ? 2.5 - 1.5 * (ft / 0.12) : 1; f.el.style.opacity = ft < 0.05 ? ft / 0.05 : (ft < 0.78 ? 1 : (1 - ft) / 0.22); f.el.style.transform = 'translate(-50%,-50%) translate(' + sp[0] + 'px,' + (sp[1] - 22) + 'px) rotate(-5deg) scale(' + ss.toFixed(3) + ')'; }\n      else { var pop = ft < 0.1 ? 0.6 + 4 * ft : 1; f.el.style.opacity = ft < 0.72 ? 1 : (1 - ft) / 0.28; f.el.style.transform = 'translate(-50%,-100%) translate(' + sp[0] + 'px,' + (sp[1] - ft * 34 + (f.dy || 0)) + 'px) scale(' + pop.toFixed(3) + ')'; }")
# ---- 부대: 그림은 크게, 이름표는 조금 작게 ----
rep("FAC_W = 1.62, UNIT_W = 1.55;", "FAC_W = 1.62, UNIT_W = 2.0;")
rep("new THREE.CircleGeometry(0.80, 20).rotateX(-Math.PI / 2)", "new THREE.CircleGeometry(1.0, 24).rotateX(-Math.PI / 2)")
rep("labelSize(uo.lab, lk * 0.92); uo.lab.sp.visible = showU;", "labelSize(uo.lab, lk * 0.82); uo.lab.sp.visible = showU;")
rep("o.fc.sp.position.set(-0.56, o.sp.userData.top * 0.78, 0);", "o.fc.sp.position.set(-0.74, o.sp.userData.top * 0.80, 0);")
# ---- 뜨는 글씨: 겹치지 않게 위아래 자리(dy)를 줄 수 있다 ----
rep("function floatText(c, r, text, color, delay, big) {", "function floatText(c, r, text, color, delay, big, dy) {")
rep("UI.floats.push({ p: hexPos(c, r), el: el, t0: performance.now() + (delay || 0), dur: 1350 });", "UI.floats.push({ p: hexPos(c, r), el: el, t0: performance.now() + (delay || 0), dur: 1350, dy: dy || 0 });")
# 한지 결(패널 바탕)을 CSS 변수로
rep("  $('title').style.backgroundImage = 'url(' + TITLE_IMG + ')';", "  $('title').style.backgroundImage = 'url(' + TITLE_IMG + ')';\n  if (typeof HANJI_IMG === 'string') document.documentElement.style.setProperty('--hanji', 'url(' + HANJI_IMG + ')');")
open(os.path.join(root, 'src', 'ui3d.js'), 'w', encoding='utf8').write(s)
print('ui3d.js', len(s))
