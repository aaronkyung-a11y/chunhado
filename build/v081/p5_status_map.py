# v0.8.1 상태 이상 표시 — 지도
#  ① 머리 위 상태 딱지: 혼란(쪽빛)·위보(황토)·불길(인주). 남은 턴 수를 함께 적는다(혼란 2). 이름표와 같은 크기 규칙(화면에서 늘 같은 크기), 멀리 물러나면 이름표와 함께 숨는다
#  ② 혼란·위보에 걸린 부대 머리 위에 소용돌이(먹 붓 자국, 걸리는 순간에만 보이던 것)가 계속 돈다. 부대 그림은 물이 빠진 빛이 되고, 혼란이면 좌우로 비틀거린다
#  ③ 병력 숫자 앞에 붙던 '혼란 '/'위보 ' 글자는 뗀다(딱지가 대신한다)
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "/* 부대 왼쪽 위에 붙는 주장 얼굴 딱지(둥근 초상). 테두리는 세력 색 */",
"""/* 상태 딱지(부대 머리 위): segs = [{t, bg}] 를 옆으로 나란히. 종이 빛 테두리를 둘러 어떤 땅 위에서도 읽힌다 */
var ST_COL = { confuse: '#2f4f6f', rumor: '#8a5a12', fire: '#b5332a' }, ST_TINT = { confuse: 0xaebdd2, rumor: 0xdccda4 };
function drawChips(L, segs) {
  var x = L.cv.getContext('2d'), S = 2, px = 12.5 * S, pad = 6.5 * S, gap = 2.5 * S, bh = Math.ceil(px * 1.5), w = 6, i, tail = 9;
  x.font = '800 ' + px + 'px ' + FONT_B;
  for (i = 0; i < segs.length; i++) { segs[i].w = Math.ceil(x.measureText(segs[i].t).width + pad * 2); w += segs[i].w + (i ? gap : 0); }
  L.cv.width = w; L.cv.height = bh + 6 + tail; L.w = w; L.h = bh + 6 + tail;
  x = L.cv.getContext('2d'); x.font = '800 ' + px + 'px ' + FONT_B; x.textAlign = 'center'; x.textBaseline = 'middle'; x.lineJoin = 'round';
  // 꼬리(가운데 아래 세모) — 어느 부대의 딱지인지 가리킨다
  x.beginPath(); x.moveTo(w / 2 - 9, bh + 1); x.lineTo(w / 2, bh + 3 + tail); x.lineTo(w / 2 + 9, bh + 1); x.closePath(); x.fillStyle = segs[0].bg; x.fill(); x.lineWidth = 2.4; x.strokeStyle = '#fbf6ea'; x.stroke();
  var X = 3;
  for (i = 0; i < segs.length; i++) {
    rr(x, X, 3, segs[i].w, bh, 6); x.fillStyle = segs[i].bg; x.fill(); x.lineWidth = 2.4; x.strokeStyle = '#fbf6ea'; x.stroke();
    x.fillStyle = 'rgba(20,18,16,0.4)'; x.fillText(segs[i].t, X + segs[i].w / 2 + 1, 3 + bh / 2 + 2.5);
    x.fillStyle = '#fbf6ea'; x.fillText(segs[i].t, X + segs[i].w / 2, 3 + bh / 2 + 1);
    X += segs[i].w + gap;
  }
  x.beginPath(); x.moveTo(w / 2 - 7.5, bh + 1.5); x.lineTo(w / 2, bh + tail); x.lineTo(w / 2 + 7.5, bh + 1.5); x.closePath(); x.fillStyle = segs[0].bg; x.fill();   // 테두리 선을 덮어 판과 꼬리를 잇는다
  L.tex.dispose(); L.tex.needsUpdate = true;
}
/* 부대의 상태 딱지에 적을 것 */
function statusSegs(u) {
  var segs = [], n = statusLeft(u);
  if (u.status) segs.push({ t: statusName(u.status) + (n > 0 ? ' ' + n : ''), bg: ST_COL[u.status] || ST_COL.confuse });
  if (unitOnFire(u)) segs.push({ t: '불길', bg: ST_COL.fire });
  return segs;
}
/* 부대 왼쪽 위에 붙는 주장 얼굴 딱지(둥근 초상). 테두리는 세력 색 */""")
s = rep(s, """      o.fc = mkLabel(); o.fc.sp.center.set(0.5, 0.5); o.fc.sp.renderOrder = 7; o.fc.sp.visible = false; o.fcOn = false; o.g.add(o.fc.sp);""",
"""      o.fc = mkLabel(); o.fc.sp.center.set(0.5, 0.5); o.fc.sp.renderOrder = 7; o.fc.sp.visible = false; o.fcOn = false; o.g.add(o.fc.sp);
      o.st = mkLabel(); o.st.sp.renderOrder = 8; o.st.sp.visible = false; o.stOn = false; o.stK = ''; o.ph = (u.id * 1.7) % 6.283; o.g.add(o.st.sp);      // 상태 딱지
      o.sw = new THREE.Sprite(new THREE.SpriteMaterial({ map: fxTex('swirl'), color: 0x2f4f6f, transparent: true, opacity: 0.9, depthTest: false, depthWrite: false }));   // 머리 위 소용돌이
      o.sw.renderOrder = 5; o.sw.visible = false; o.g.add(o.sw);""")
s = rep(s, "sig = u.f + '|' + u.type + '|' + Math.round(u.troops / 10) + '|' + (u.f === G.player && u.done) + '|' + (u.status || '') + '|' + isSel",
           "var segs = statusSegs(u);\n    sig = u.f + '|' + u.type + '|' + Math.round(u.troops / 10) + '|' + (u.f === G.player && u.done) + '|' + segs.map(function (g) { return g.t; }).join('+') + '|' + isSel")
s = rep(s, """      o.sp.material.color.setHex(0xffffff); o.sp.material.opacity = dim ? 0.52 : 1; o.ring.material.color.set(fcol); o.ring.material.opacity = dim ? 0.4 : 0.78;""",
"""      o.sp.material.color.setHex(u.status ? (ST_TINT[u.status] || 0xffffff) : 0xffffff); o.sp.material.opacity = dim ? 0.52 : 1; o.ring.material.color.set(fcol); o.ring.material.opacity = dim ? 0.4 : 0.78;
      // 상태: 머리 위 딱지 + 소용돌이. 혼란이면 tick 에서 좌우로 비틀거리게 한다
      o.stOn = segs.length > 0; o.stK = u.status || '';
      if (!o.stK) o.sp.material.rotation = 0;
      if (o.stOn) { drawChips(o.st, segs); o.stY = o.sp.userData.top * 0.97; o.st.sp.position.set(0.06, o.stY, 0); }
      o.sw.visible = !!o.stK;
      if (o.stK) { o.sw.material.color.set(ST_COL[o.stK] || ST_COL.confuse); o.sw.scale.set(1.18, 1.18, 1); o.sw.position.set(0.02, o.sp.userData.top * 0.72, 0); }""")
s = rep(s, "      var mark = u.status ? (u.status === 'confuse' ? '혼란 ' : '위보 ') : (u.dest >= 0 ? '▸ ' : ''), lns = [{ t: mark + fmt(u.troops), px: 12, bold: 800, color: '#fbf6ea' }];",
           "      var mark = (!u.status && u.dest >= 0) ? '▸ ' : '', lns = [{ t: mark + fmt(u.troops), px: 12, bold: 800, color: '#fbf6ea' }];      // 상태는 머리 위 딱지가 알린다(0.8까지는 여기에 '혼란 ' 글자를 붙였다)")
s = rep(s, "o = R3.units[id]; R3.objs.remove(o.g); R3.objs.remove(o.ring); o.sp.material.dispose(); o.lab.tex.dispose(); o.lab.sp.material.dispose(); o.fc.tex.dispose(); o.fc.sp.material.dispose(); o.ring.material.dispose(); delete R3.units[id];",
           "o = R3.units[id]; R3.objs.remove(o.g); R3.objs.remove(o.ring); o.sp.material.dispose(); o.lab.tex.dispose(); o.lab.sp.material.dispose(); o.fc.tex.dispose(); o.fc.sp.material.dispose(); o.st.tex.dispose(); o.st.sp.material.dispose(); o.sw.material.dispose(); o.ring.material.dispose(); delete R3.units[id];")
# 매 프레임: 소용돌이·비틀거림·딱지의 오르내림 (불과 같은 박자로 초당 20번만 다시 그린다)
s = rep(s, """    if (hot || UI.floats.length || (nf && now - (R3.fireT || 0) > 50)) { UI.render = true; R3.fireT = now; }   // 불은 초당 20번만 다시 그린다""",
"""    var nst = 0;
    for (var sid in R3.units) {
      var so = R3.units[sid]; if (!so.stK) continue;
      nst++;
      so.sw.material.rotation = -now / 380 + so.ph;                                                    // 소용돌이가 돈다
      if (so.stK === 'confuse') so.sp.material.rotation = 0.075 * Math.sin(now / 250 + so.ph);          // 혼란: 비틀거린다
      so.st.sp.position.y = so.stY + 0.05 * Math.sin(now / 320 + so.ph);                               // 딱지가 살짝 오르내린다
    }
    if (hot || UI.floats.length || ((nf || nst) && now - (R3.fireT || 0) > 50)) { UI.render = true; R3.fireT = now; }   // 불·상태 표시는 초당 20번만 다시 그린다""")
s = rep(s, "labelSize(uo.fc, lk * 0.92); uo.fc.sp.visible = showU && uo.fcOn; }",
           "labelSize(uo.fc, lk * 0.92); uo.fc.sp.visible = showU && uo.fcOn; labelSize(uo.st, lk * 0.84); uo.st.sp.visible = showU && uo.stOn; }")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
