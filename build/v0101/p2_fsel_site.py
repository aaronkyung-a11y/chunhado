# v0.10.1 (2/…): 고른 시설을 지도에 표시 · 부지 번호를 시설에도 · 짓는 중인 시설은 공사장 그림  (ui_panels.js · ui3d.js · style.css)
#  요청: "이 화면일 때 똑같은 시장이 많아서 뭐가 지금 내가 선택한 시장인지 모르겠어 표시해줘" · "만들고 있는 건축물는 그래픽이 달라야할듯"
#  - 시설 창(흡수합병 · 철거)이 떠 있는 동안: 지도는 건설 자리를 볼 때처럼 어두워지고 그 시설만 환하게, 붉은 테두리가 둘리고 이름표가 붉은 딱지가 된다.
#    창은 '무엇을 지을까요' 창처럼 지도를 가리지 않는다(아래 창 · 버튼 줄은 숨는다). 지도에서 같은 거점의 다른 시설을 누르면 그 시설로,
#    빈 부지를 누르면 '무엇을 지을까요'로 바뀌고, 그 밖을 누르면 닫힌다. ('무엇을 지을까요' 창에서 시설을 눌러도 그 시설의 창으로 간다)
#    건설 자리를 보는 동안에는 성의 그림에 가린 부지(성 바로 뒤의 칸)를 눌러도 성이 아니라 그 부지가 집힌다(전에는 성이 집혔다).
#  - 부지 번호(성을 가운데 두고 북쪽에서 시계 방향 — v0.9.3)가 지은 시설에도 붙는다: 지도의 이름 앞 작은 딱지, 시설 탭의 줄 앞, 시설 창의 제목.
#    시설 탭의 '지은 시설'은 번호 차례로 늘어선다.
#  - 짓는 중인 시설: 전에는 완성된 그림을 반투명하게 보였다. 이제 '밑그림 + 비계'다 — 그 시설의 그림을 먹빛만 옅게 남기고 대나무 비계 · 통나무 더미 · 붉은 깃발을
#    덧그린다(그림 파일을 새로 넣은 것이 아니라 화면에서 만든다). 공사가 3분의 1씩 나아갈 때마다 밑그림이 짙어진다. 시설 탭의 줄과 시설 창의 작은 그림도 같다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- ui_panels.js
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()

# 1) 작은 그림: 짓는 중이면 공사장
s = rep(s, "function thumb(key, cls) { return '<img class=\"th' + (cls ? ' ' + cls : '') + '\" alt=\"\" src=\"' + SPRITES[key].u + '\">'; }",
           "function thumb(key, cls) { return '<img class=\"th' + (cls ? ' ' + cls : '') + '\" alt=\"\" src=\"' + SPRITES[key].u + '\">'; }\n"
           "function facThumb(fc, cls) { var u = (!fc.done && typeof siteUrl === 'function') ? siteUrl(fc.t) : ''; return u ? '<img class=\"th' + (cls ? ' ' + cls : '') + '\" alt=\"\" src=\"' + u + '\">' : thumb(fc.t, cls); }      // 짓는 중인 시설은 공사장 그림\n"
           "function lotChip(b, pi) { return '<i class=\"lno\">' + lotNo(b, pi) + '</i>'; }                                   // 부지 번호 딱지(지도의 번호와 같다)")

# 2) 시설 창도 지도를 보여 주는 창
s = rep(s, "m.classList.toggle('see', !!MODAL.see); $('app').classList.toggle('seeing', !!devOf());",
           "m.classList.toggle('see', !!MODAL.see); $('app').classList.toggle('seeing', !!(devOf() || fselOf()));")
s = rep(s, "function devOf() { if (MODAL && MODAL.dev) return MODAL.dev; for (var i = MSTACK.length - 1; i >= 0; i--) if (MSTACK[i].d.dev) return MSTACK[i].d.dev; return null; }",
           "function devOf() { if (MODAL && MODAL.dev) return MODAL.dev; for (var i = MSTACK.length - 1; i >= 0; i--) if (MSTACK[i].d.dev) return MSTACK[i].d.dev; return null; }\n"
           "/* 시설 창(흡수합병 · 철거)이 떠 있으면 그 시설 { b, pi } — 지도에서 그 시설을 표시한다(v0.10.1) */\n"
           "function fselOf() { if (MODAL && MODAL.fsel) return MODAL.fsel; for (var i = MSTACK.length - 1; i >= 0; i--) if (MSTACK[i].d.fsel) return MSTACK[i].d.fsel; return null; }")

# 3) buildView: 고른 시설(fi) · 시설의 번호
s = rep(s, "  var d = devOf(), b = d ? G.bases[d.b] : (SHEET && SHEET.fac ? SHEET.fac() : null);\n"
           "  if (!b || b.owner !== G.player || b.kind !== 'city') return null;\n"
           "  var why = buildWhy(b), pi = d ? d.pi : -1, sig = b.id + '/' + pi + '/' + why + '/', lots = [], facs = [];\n",
           "  var d = devOf(), fs = d ? null : fselOf(), b = d ? G.bases[d.b] : (fs ? G.bases[fs.b] : (SHEET && SHEET.fac ? SHEET.fac() : null));\n"
           "  if (!b || b.owner !== G.player || b.kind !== 'city') return null;\n"
           "  var why = buildWhy(b), pi = d ? d.pi : -1, fi = (fs && b.plots[fs.pi] && b.plots[fs.pi].fac) ? fs.pi : -1, sig = b.id + '/' + pi + '/' + fi + '/' + why + '/', lots = [], facs = [];\n")
s = rep(s, "    if (p.fac) { facs.push({ c: p.c, r: p.r, n: FAC[p.fac.t].name, done: p.fac.done }); sig += 'f' + i + p.fac.t + (p.fac.done ? '' : 'c') + ','; }",
           "    if (p.fac) { var left = p.fac.done ? '' : days(Math.max(1, Math.ceil((p.fac.need - p.fac.prog) / Math.max(1, p.fac.rate)))); facs.push({ i: i, no: lotNo(b, i), c: p.c, r: p.r, n: FAC[p.fac.t].name, done: p.fac.done, left: left }); sig += 'f' + i + p.fac.t + (p.fac.done ? '' : 'c' + left) + ','; }")
s = rep(s, "  if (!lots.length) return null;                               // 빈 부지가 없으면 비출 것이 없다\n"
           "  lots.sort(function (x, y) { return x.n - y.n; });\n"
           "  return { b: b, pi: pi, why: why, lots: lots, facs: facs, sig: sig };",
           "  if (!lots.length && fi < 0) return null;                     // 빈 부지도, 고른 시설도 없으면 비출 것이 없다\n"
           "  lots.sort(function (x, y) { return x.n - y.n; });\n"
           "  return { b: b, pi: pi, fi: fi, why: why, lots: lots, facs: facs, sig: sig };")

# 4) 지도를 눌렀을 때
s = rep(s, "/* '무엇을 지을까요' 창이 떠 있는 동안 지도를 눌렀다: 다른 빈 부지면 자리를 바꾸고, 그 밖이면 창을 닫는다 */\n"
           "function devTap(c, r) {\n"
           "  var d = MODAL.dev, b = G.bases[d.b], pl = plotAt(c, r);\n",
           "/* '무엇을 지을까요' 창이 떠 있는 동안 지도를 눌렀다: 다른 빈 부지면 자리를 바꾸고, 이 거점의 시설이면 그 시설의 창으로, 그 밖이면 창을 닫는다 */\n"
           "function devTap(c, r) {\n"
           "  var d = MODAL.dev, b = G.bases[d.b], pl = plotAt(c, r);\n"
           "  if (pl && pl.base === b && pl.plot.fac) { sfx('ui'); flowFacility(b, pl.i); return; }\n")
s = rep(s, "  if (MODAL) { if (MODAL.dev) devTap(c, r); return; }",
           "  if (MODAL) { if (MODAL.dev) devTap(c, r); else if (MODAL.fsel) fselTap(c, r); return; }")
s = rep(s, "/* 이 자리에 지으면 늘어나는 수입(금/월, 병량/분기)",
           "/* 시설 창이 떠 있는 동안 지도를 눌렀다: 같은 거점의 다른 시설이면 그 시설로, 빈 부지면 '무엇을 지을까요'로, 그 밖이면 창을 닫는다(v0.10.1) */\n"
           "function fselTap(c, r) {\n"
           "  var f = MODAL.fsel, b = G.bases[f.b], pl = plotAt(c, r);\n"
           "  if (pl && pl.base === b) {\n"
           "    if (pl.plot.fac) { if (pl.i !== f.pi) { sfx('ui'); flowFacility(b, pl.i); } return; }\n"
           "    flowDevelop(b, pl.i); return;                              // 지을 수 없으면 까닭을 알리고 이 창은 그대로 둔다\n"
           "  }\n"
           "  backDialog();\n"
           "}\n"
           "/* 이 자리에 지으면 늘어나는 수입(금/월, 병량/분기)")

# 5) 시설 탭: 지은 시설을 번호 차례로, 번호 딱지와 함께
s = rep(s, "        for (i = 0; i < b.plots.length; i++) {\n"
           "          var fc = b.plots[i].fac;\n"
           "          if (!fc) continue;\n"
           "          h += '<button class=\"row\" type=\"button\" data-a=\"plot\" data-v=\"' + i + '\">' + thumb(fc.t) + '<span class=\"mid\"><span class=\"nm\">' + FAC[fc.t].name + ' Lv' + fc.lv + '</span>",
           "        var built = []; for (i = 0; i < b.plots.length; i++) if (b.plots[i].fac) built.push(i);\n"
           "        built.sort(function (x, y) { return lotNo(b, x) - lotNo(b, y); });                                     // 번호 차례(지도의 딱지와 같다)\n"
           "        for (var bi = 0; bi < built.length; bi++) {\n"
           "          i = built[bi];\n"
           "          var fc = b.plots[i].fac;\n"
           "          h += '<button class=\"row\" type=\"button\" data-a=\"plot\" data-v=\"' + i + '\">' + facThumb(fc) + '<span class=\"mid\"><span class=\"nm\">' + lotChip(b, i) + FAC[fc.t].name + ' Lv' + fc.lv + '</span>")

# 6) 시설 창: 지도를 보여 주고(see) 고른 시설을 알린다(fsel). 제목에 번호
s = rep(s, "  var F = FAC[fc.t];\n"
           "  showDialog({\n"
           "    render: function () {\n"
           "      var cands = mergeCandidates(b, pi);\n"
           "      var h = dlgHead(b.n + ' ' + F.name + ' Lv' + fc.lv) + '<div class=\"dlg-b\"><div class=\"card\">' + thumb(fc.t, 'lg') + '<p>' + F.desc + '</p></div>'",
           "  var F = FAC[fc.t];\n"
           "  showDialog({\n"
           "    fsel: { b: b.id, pi: pi }, see: true,                          // 지도에서 이 시설이 표시된다 — 다른 시설을 누르면 그 시설로 바뀐다(fselTap)\n"
           "    render: function () {\n"
           "      var cands = mergeCandidates(b, pi);\n"
           "      var h = dlgHead(b.n + ' ' + lotMark(lotNo(b, pi)) + ' ' + F.name + ' Lv' + fc.lv) + '<div class=\"dlg-b\"><div class=\"card\">' + facThumb(fc, 'lg') + '<p>' + F.desc + '</p></div>'")

# 7) 도움말
s = rep(s, "같은 시설이 붙어 있으면 흡수합병으로 레벨을 올립니다(최대 3).",
           "<b>지은 시설</b>에도 같은 번호가 붙어 있고, 줄이나 지도에서 누르면 그 시설만 환해지고 <b>붉은 테두리와 붉은 이름표</b>가 붙습니다. 짓는 중인 시설은 비계를 두른 공사장으로 보입니다. 같은 시설이 붙어 있으면 흡수합병으로 레벨을 올립니다(최대 3).")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui3d.js
p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()

# 1) 시설 그림의 원본을 남겨 둔다(공사장 그림을 만들 때 쓴다)
s = rep(s, "    img(SPRITES[key].u, function (im) {\n"
           "      var t = new THREE.Texture(im); t.needsUpdate = true; TEX[key] = t;",
           "    img(SPRITES[key].u, function (im) {\n"
           "      SITE_IMG[key] = im;\n"
           "      var t = new THREE.Texture(im); t.needsUpdate = true; TEX[key] = t;")

# 2) 공사장 그림
s = rep(s, "/* ---------- 물체 ---------- */\n",
r"""/* ---------- 공사장(v0.10.1) ----------
   짓는 중인 시설은 완성된 그림 대신 '밑그림 + 비계'로 보인다: 그 시설의 그림을 먹빛만 옅게 남기고(밑그림), 그 위에 대나무 비계 · 통나무 더미 · 붉은 깃발을 덧그린다.
   공사가 나아갈수록(셋으로 나눈 단계 0·1·2) 밑그림이 짙어진다. 처음 쓸 때 만들어 TEX['시설@단계'] 에 넣어 둔다(SPRITES 에도 같은 크기로 올린다 — setSprite 가 그대로 쓴다). */
var SITE_IMG = {}, SITE_URL = {}, SITE_INK = [0.42, 0.54, 0.68], SITE_A = [0.84, 0.90, 0.95];
function siteStage(fc) { return clamp(Math.floor(3 * (fc.prog || 0) / Math.max(1, fc.need || 1)), 0, 2); }
function siteCanvas(key, st) {
  var im = SITE_IMG[key], S = SPRITES[key]; if (!im || !S) return null;
  var w = S.w, h = S.h, c = document.createElement('canvas'), i; c.width = w; c.height = h;
  var x = c.getContext('2d'); x.drawImage(im, 0, 0, w, h);
  var d, x0 = w, x1 = 0, y0 = h, y1 = 0, k = SITE_INK[st], al = SITE_A[st];
  try { d = x.getImageData(0, 0, w, h); } catch (e) { return null; }
  var p = d.data;
  for (i = 0; i < p.length; i += 4) {
    var a = p[i + 3];
    if (a > 60) { var px = (i >> 2) % w, py = ((i >> 2) / w) | 0; if (px < x0) x0 = px; if (px > x1) x1 = px; if (py < y0) y0 = py; if (py > y1) y1 = py; }
    var g = 255 - (255 - (p[i] * 0.3 + p[i + 1] * 0.59 + p[i + 2] * 0.11)) * k;
    p[i] = g; p[i + 1] = g * 0.985; p[i + 2] = g * 0.95; p[i + 3] = a * al;
  }
  x.putImageData(d, 0, 0);
  if (x1 - x0 < 40 || y1 - y0 < 40) return c;
  var seed = 7; for (i = 0; i < key.length; i++) seed = (Math.imul(seed, 31) + key.charCodeAt(i)) | 0;
  function rnd() { seed = (seed + 0x6D2B79F5) | 0; var t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }
  // 비계: 바닥의 마름모(왼쪽 L · 앞 F · 오른쪽 R · 뒤 B) 위에 세운 틀. 앞의 두 면은 또렷하게, 뒤는 옅게
  var cx = (x0 + x1) / 2, A = (x1 - x0) * 0.385, B = A * 0.5, base = y1 - B - (y1 - y0) * 0.11, H = Math.min(Math.max((base - B) - (y0 + 16), 34), A * 1.05);
  var L = [cx - A, base], F = [cx, base + B], R = [cx + A, base], K = [cx, base - B], POLE = '#9c6c34', EDGE = 'rgba(58,40,24,0.94)', BACK = 'rgba(150,112,64,0.5)';
  function up(P, hh) { return [P[0], P[1] - hh]; }
  function mid(P, Q) { return [(P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2]; }
  function line(P, Q, wd, col, edge) {                               // 손으로 그은 듯 조금 흔들리는 선(먹 테두리 + 대나무 빛)
    var n = 6, pts = [], j;
    for (j = 0; j <= n; j++) { var t = j / n, in_ = (j > 0 && j < n) ? 1.2 : 0; pts.push([P[0] + (Q[0] - P[0]) * t + (rnd() - 0.5) * in_, P[1] + (Q[1] - P[1]) * t + (rnd() - 0.5) * in_]); }
    function path() { x.beginPath(); x.moveTo(pts[0][0], pts[0][1]); for (j = 1; j <= n; j++) x.lineTo(pts[j][0], pts[j][1]); }
    x.lineCap = 'round'; x.lineJoin = 'round';
    if (edge) { path(); x.strokeStyle = EDGE; x.lineWidth = wd + 1.3; x.stroke(); }
    path(); x.strokeStyle = col; x.lineWidth = wd; x.stroke();
  }
  line(K, up(K, H), 1.4, BACK); line(up(L, H), up(K, H), 1.4, BACK); line(up(K, H), up(R, H), 1.4, BACK);
  [0.36, 0.70].forEach(function (q) { line(up(L, H * q), up(K, H * q), 1.1, BACK); line(up(K, H * q), up(R, H * q), 1.1, BACK); });
  [L, mid(L, F), F, mid(F, R), R].forEach(function (P) { line([P[0], P[1] + 2], up(P, H + 5), 2.2, POLE, true); });
  [0.36, 0.70, 1].forEach(function (q) { line(up(L, H * q), up(F, H * q), 1.8, POLE, true); line(up(F, H * q), up(R, H * q), 1.8, POLE, true); });
  line(L, up(mid(L, F), H * 0.36), 1.3, POLE, true); line(up(mid(L, F), H * 0.36), up(F, H * 0.70), 1.3, POLE, true);
  line(R, up(mid(F, R), H * 0.36), 1.3, POLE, true); line(up(mid(F, R), H * 0.36), up(F, H * 0.70), 1.3, POLE, true);
  var ft = up(R, H + 22);                                             // 붉은 깃발: 오른쪽 기둥 꼭대기
  line(up(R, H + 5), ft, 1.0, EDGE);
  x.beginPath(); x.moveTo(ft[0], ft[1]); x.lineTo(ft[0] - 14, ft[1] + 4.5); x.lineTo(ft[0], ft[1] + 9); x.closePath(); x.fillStyle = '#ba342a'; x.fill();
  var lx = cx - A * 0.72, ly = base + B * 0.78;                       // 통나무 더미: 왼쪽 앞 바닥
  for (i = 0; i < 3; i++) line([lx + i * 3.2 - 10, ly + i * 2.4 - 3], [lx + i * 3.2 + 10, ly + i * 2.4 - 13], 2.6, '#b0844e', true);
  return c;
}
/* 짓는 중인 시설에 쓸 그림의 키('market@1'). 만들 수 없으면(그림이 아직 없다) '' — 그때는 전처럼 완성된 그림을 옅게 쓴다 */
function siteTexKey(t, st) {
  var k = t + '@' + st;
  if (TEX[k]) return k;
  if (TEX[k] === null) return '';
  var c = siteCanvas(t, st);
  if (!c) { if (SITE_IMG[t]) TEX[k] = null; return ''; }
  var tx = new THREE.CanvasTexture(c); TEX[k] = tx; SPRITES[k] = { w: SPRITES[t].w, h: SPRITES[t].h, ay: SPRITES[t].ay };
  return k;
}
/* 목록과 창의 작은 그림에 쓸 주소(가운데 단계). 없으면 '' */
function siteUrl(t) {
  if (SITE_URL[t] === undefined) {
    var c = siteCanvas(t, 1); if (!c) return SITE_IMG[t] ? (SITE_URL[t] = '') : '';
    try { SITE_URL[t] = URL.createObjectURL(b64blob(c.toDataURL('image/png').split(',')[1], 'image/png')); } catch (e) { SITE_URL[t] = ''; }
  }
  return SITE_URL[t];
}

/* ---------- 물체 ---------- */
""")

# 3) 지도의 시설: 짓는 중이면 공사장 그림
s = rep(s, "      var fs = fc.t + fc.lv + (fc.done ? 'd' : 'c');\n"
           "      if (!fo) { p = hexPos(pl.c, pl.r); fo = R3.facs[fk] = { sp: spriteObj(fc.t, FAC_W, 2), sig: '' }; fo.sp.position.set(p[0], p[1], p[2]); R3.objs.add(fo.sp); }\n"
           "      if (fo.sig !== fs) { fo.sig = fs; setSprite(fo.sp, fc.t, FAC_W * (0.94 + 0.10 * (fc.lv - 1))); fo.sp.material.opacity = fc.done ? 1 : 0.5; }",
           "      var sk = fc.done ? '' : siteTexKey(fc.t, siteStage(fc)), fs = fc.t + fc.lv + (fc.done ? 'd' : 'c' + sk);      // 짓는 중: 공사장 그림(단계가 오르면 바뀐다)\n"
           "      if (!fo) { p = hexPos(pl.c, pl.r); fo = R3.facs[fk] = { sp: spriteObj(fc.t, FAC_W, 2), sig: '' }; fo.sp.position.set(p[0], p[1], p[2]); R3.objs.add(fo.sp); }\n"
           "      if (fo.sig !== fs) { fo.sig = fs; setSprite(fo.sp, sk || fc.t, FAC_W * (0.94 + 0.10 * (fc.lv - 1))); fo.sp.material.opacity = (fc.done || sk) ? 1 : 0.5; }")

# 4) 건설 자리 그림: 고른 시설을 환하게 + 붉은 테두리 + 붉은 이름표, 시설의 이름 앞에 번호 딱지
s = rep(s, "  for (i = 0; i < v.lots.length; i++) rings.push(hexRing(v.lots[i].c, v.lots[i].r, 1));\n"
           "  x.globalCompositeOperation = 'destination-out'; x.fillStyle = '#000';\n"
           "  for (i = 0; i < v.lots.length; i++) if (rings[i] && v.lots[i].ok) { ringPath(x, rings[i]); x.fill(); }      // 지을 수 있는 칸만 뚫는다\n",
           "  for (i = 0; i < v.lots.length; i++) rings.push(hexRing(v.lots[i].c, v.lots[i].r, 1));\n"
           "  var selF = null, selR = null, selQ = null, selU = 0;                                // 고른 시설(시설 창이 떠 있을 때)\n"
           "  if (v.fi >= 0) for (i = 0; i < v.facs.length; i++) if (v.facs[i].i === v.fi) {\n"
           "    var sp0 = hexPos(v.facs[i].c, v.facs[i].r), sq0 = w2s(sp0[0], sp0[1], sp0[2]);\n"
           "    if (sq0) { selF = v.facs[i]; selR = hexRing(selF.c, selF.r, 1); selQ = sq0; selU = pxPerUnit(sq0[2]); }\n"
           "  }\n"
           "  x.globalCompositeOperation = 'destination-out'; x.fillStyle = '#000';\n"
           "  for (i = 0; i < v.lots.length; i++) if (rings[i] && v.lots[i].ok) { ringPath(x, rings[i]); x.fill(); }      // 지을 수 있는 칸만 뚫는다\n"
           "  if (selF) {                                                                          // 고른 시설은 건물 전체가 환하게(칸보다 조금 넓게, 가장자리는 번지게)\n"
           "    var gy = selQ[1] - selU * 0.22, gr = selU * 1.34, gg = x.createRadialGradient(selQ[0], gy, gr * 0.5, selQ[0], gy, gr);\n"
           "    gg.addColorStop(0, 'rgba(0,0,0,1)'); gg.addColorStop(0.7, 'rgba(0,0,0,0.92)'); gg.addColorStop(1, 'rgba(0,0,0,0)');\n"
           "    x.fillStyle = gg; x.beginPath(); x.arc(selQ[0], gy, gr, 0, 6.2832); x.fill(); x.fillStyle = '#000';\n"
           "  }\n")
s = rep(s, "  for (i = 0; i < v.facs.length; i++) {                        // 이미 지은 시설: 어둠 속에서도 옆에 무엇이 있는지 이름으로\n",
           "  var facLabels = function () { for (i = 0; i < v.facs.length; i++) {      // 이미 지은 시설: 어둠 속에서도 옆에 무엇이 있는지 번호와 이름으로(빈 부지의 테두리보다 나중에 그린다 — 아래에서 부른다)\n")
s = rep(s, "    var fpx = clamp(Math.round(fpu * 0.40), 10, 13);\n"
           "    x.font = '700 ' + fpx + 'px ' + FONT_B; x.lineWidth = 3; x.strokeStyle = 'rgba(20,18,16,0.72)';\n"
           "    x.fillStyle = v.facs[i].done ? 'rgba(244,239,227,0.94)' : 'rgba(244,239,227,0.7)';\n"
           "    x.strokeText(v.facs[i].n, fq[0], fq[1] + fpu * 0.16); x.fillText(v.facs[i].n, fq[0], fq[1] + fpu * 0.16);\n"
           "    if (!v.facs[i].done) { x.font = '600 ' + (fpx - 1) + 'px ' + FONT_B; x.strokeText('짓는 중', fq[0], fq[1] + fpu * 0.16 + fpx + 1); x.fillText('짓는 중', fq[0], fq[1] + fpu * 0.16 + fpx + 1); }\n"
           "  }\n",
           "    var fpx = clamp(Math.round(fpu * 0.40), 10, 13), fa = v.facs[i], fon = fa === selF, fly = fq[1] + fpu * 0.16;\n"
           "    x.font = '700 ' + fpx + 'px ' + FONT_B;\n"
           "    var ftw = x.measureText(fa.n).width, fbr = clamp(fpx * 0.6, 6, 7.8), ftx = fq[0] + fbr + 1.5, fbx = ftx - ftw / 2 - fbr - 2.5;      // 번호 딱지 + 이름: 둘을 합친 것이 칸의 가운데에 오게\n"
           "    if (fon) { rr(x, fbx - fbr - 4, fly - fpx / 2 - 4.5, ftx + ftw / 2 + 6 - (fbx - fbr - 4), fpx + 9, 3); x.fillStyle = SEAL; x.fill(); x.lineWidth = 1.4; x.strokeStyle = PAPER; x.stroke(); }      // 고른 시설: 이름표가 붉은 딱지가 된다\n"
           "    x.lineWidth = 3; x.strokeStyle = 'rgba(20,18,16,0.78)';\n"
           "    x.fillStyle = fon ? '#fff' : (fa.done ? 'rgba(244,239,227,0.96)' : 'rgba(244,239,227,0.8)');\n"
           "    if (!fon) x.strokeText(fa.n, ftx, fly);\n"
           "    x.fillText(fa.n, ftx, fly);\n"
           "    if (!fa.done) { var fly2 = fly + fpx + (fon ? 6 : 1); x.font = '600 ' + (fpx - 1) + 'px ' + FONT_B; x.fillStyle = '#f0d58a'; x.strokeText(fa.left + ' 남음', fq[0], fly2); x.fillText(fa.left + ' 남음', fq[0], fly2); }      // 짓는 중: 남은 날수\n"
           "    x.beginPath(); x.arc(fbx, fly, fbr, 0, 6.2832); x.fillStyle = fon ? PAPER : 'rgba(244,239,227,0.95)'; x.fill(); x.lineWidth = 1; x.strokeStyle = fon ? PAPER : INK; x.stroke();      // 번호 딱지(빈 부지의 번호와 같은 차례 — 시설 탭의 줄 앞에도 같은 번호가 있다)\n"
           "    x.fillStyle = fon ? SEAL : INK; x.font = '900 ' + Math.round(fbr * (fa.no > 9 ? 1.12 : 1.36)) + 'px ' + FONT_D; x.fillText(String(fa.no), fbx, fly + fbr * 0.08);\n"
           "  } };\n")
s = rep(s, "      x.fillStyle = '#fff'; x.fillText('여기', q[0], by + 11.5);\n"
           "    }\n"
           "  }\n",
           "      x.fillStyle = '#fff'; x.fillText('여기', q[0], by + 11.5);\n"
           "    }\n"
           "  }\n"
           "  if (selF && selR) { ringPath(x, selR); x.lineWidth = 6.4; x.strokeStyle = PAPER; x.stroke(); x.lineWidth = 3.8; x.strokeStyle = SEAL; x.stroke(); }      // 고른 시설: 붉은 테두리(이름표는 facLabels 가 붉은 딱지로 그린다 — 위의 칸을 가리는 '여기' 표는 달지 않는다)\n"
           "  x.textAlign = 'center'; x.textBaseline = 'middle'; facLabels();\n")
# 5) 건설 자리를 보는 중: 성의 그림에 가린 부지(성 바로 뒤의 칸)를 눌러도 성이 아니라 그 부지가 집힌다
s = rep(s, "  var best = null, bd = 1e9;\n  function test(c, r, sp, pri) {",
           "  if (gh && SPOT.on && SPOT.v) { var gp = plotAt(gh[0], gh[1]); if (gp && gp.base === SPOT.v.b) return gh; }      // 건설 자리를 보는 중(v0.10.1): 그 거점의 부지는 성의 그림에 가려 있어도 부지로 집는다\n"
           "  var best = null, bd = 1e9;\n  function test(c, r, sp, pri) {")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- style.css
p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += ("\n/* ---------- v0.10.1: 부지 번호 딱지(시설 탭의 줄 앞) ---------- */\n"
      ".lno { display: inline-flex; align-items: center; justify-content: center; min-width: 19px; height: 19px; margin-right: 6px; padding: 0 0 1px; border: 1.2px solid var(--ink); border-radius: 10px; background: var(--paper); font: 900 11.5px var(--font-display); font-style: normal; vertical-align: 1px; font-variant-numeric: tabular-nums; }\n")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
