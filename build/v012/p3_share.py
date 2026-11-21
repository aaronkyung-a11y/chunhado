# v0.12 (3/…): 세이브 파일을 골라 보내기 · 받은 파일 가져오기  (ui_panels.js · style.css)
#  요청 "공유 할 때 세이브 파일을 골라서 보내주는 옵션."
#   - [공유] 창에 [세이브 파일 보내기]: 저장 칸(지금 판 = 자동 저장 · 직전 · 1~6번)을 고르면 그 판을 글 파일(.txt)로 만든다.
#       보내기(휴대폰의 공유 창에 파일로) · 파일로 저장 · 글자로 복사 — 되는 것만 보인다(공유 창이 파일을 받는지는 navigator.canShare 로 묻는다).
#       파일은 머리말 두 줄(누구의 언제 판인지 · 여는 법) + 저장본 그대로. 확장자가 .txt 인 까닭: 공유 창이 받는 파일 종류가 정해져 있다.
#   - [공유]는 이제 늘 창을 먼저 연다(v0.11 은 휴대폰에서 곧바로 주소만 보냈다 — 고를 자리가 없었다).
#   - 불러오기 창에 [파일에서 가져오기] · [붙여넣기로 가져오기]: 빈 번호 칸에 넣는다(빈 칸이 없으면 덮어쓸 칸을 고른다). 제목 화면의 [불러오기]는 저장이 없어도 열린다.
#   - 남이 보낸 파일이므로 받을 때 본다: 이 게임의 저장 꼴인가 · 글자에 < > " 가 없는가(저장본에는 들어갈 일이 없다 — 화면에 그대로 찍히는 글이다) ·
#       세력 색이 #rrggbb 꼴인가 · 실제로 열리는가(열어 본 뒤 하던 판은 그대로 되돌린다). 하나라도 어긋나면 받지 않는다.
#   - 고침: 깨진 저장을 불러오다 실패하면 하던 판이 망가질 수 있었다(deserialize 가 G 를 바꾼 뒤 멈추는 경우) → 실패하면 하던 판으로 되돌린다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
# 공유 창: 세이브 파일 보내기
s = rep(s, "        '<p class=\"note\">저장한 판은 함께 가지 않습니다 — 받는 사람은 새 게임으로 시작합니다.</p></div>';",
           "        '<h3 class=\"shh\">하던 판 보내기</h3><p>주소만 보내면 받는 사람은 새 게임으로 시작합니다. 하던 판을 이어서 하게 하려면 세이브 파일을 함께 보내세요.</p>' +\n"
           "        '<div class=\"cmds c1\"><button class=\"cmd\" type=\"button\" data-a=\"savesend\"><b>세이브 파일 보내기</b><small>보낼 판 고르기</small></button></div></div>';")
s = rep(s, "      send: function () { shareSend(url, true); }\n    }\n  }, true);\n}",
           "      send: function () { shareSend(url, true); },\n      savesend: function () { showSaveSend(); }\n    }\n  }, true);\n}")
s = rep(s, "function shareGame() {\n  var url = shareUrl();\n  if (!(navigator.share && shareSend(url, false))) showShare();\n}",
           "function shareGame() { showShare(); }                          // v0.12: 늘 창을 먼저 연다(주소 · 세이브 파일 가운데 고른다)\n"
           "/* ---------- 세이브 파일 보내기 · 가져오기(v0.12) ---------- */\n"
           "function saveFileName(m) { return '천하도_' + m.f + '_' + String(m.d).replace(/\\s+/g, '') + '.txt'; }\n"
           "/* 칸의 저장본 → 보낼 글(머리말 두 줄 + 저장본). 비었거나 열 수 없는 칸이면 null */\n"
           "function saveFileText(id) {\n"
           "  var sv = lsGet(slotKey(id)), m = slotInfo(id); if (!sv || !m || m.bad) return null;\n"
           "  return { name: saveFileName(m), meta: m, text: '삼국지 천하도 세이브 — ' + m.f + ' · ' + m.d + ' · ' + m.n + '성 · ' + fmt(m.tr) + '명 (' + GAME_VERSION + ')\\n여는 법: ' + SHARE_URL + ' → 불러오기 → 파일에서 가져오기\\n' + sv + '\\n' };\n"
           "}\n"
           "function saveFileObj(p) { try { return new File([p.text], p.name, { type: 'text/plain' }); } catch (e) { return null; } }\n"
           "function canShareFile(f) { try { return !!(f && navigator.share && navigator.canShare && navigator.canShare({ files: [f] })); } catch (e) { return false; } }\n"
           "function saveDownload(p) {\n"
           "  try {\n"
           "    var url = URL.createObjectURL(new Blob([p.text], { type: 'text/plain' })), a = document.createElement('a');\n"
           "    a.href = url; a.download = p.name; a.style.display = 'none'; document.body.appendChild(a); a.click();\n"
           "    setTimeout(function () { if (a.parentNode) a.parentNode.removeChild(a); URL.revokeObjectURL(url); }, 1500);\n"
           "    return true;\n"
           "  } catch (e) { return false; }\n"
           "}\n"
           "function copyLong(txt, okMsg) {                                 // 긴 글 복사: 새 방식 → 옛 방식(숨긴 칸을 골라 execCommand)\n"
           "  function old() {\n"
           "    var ok = false, ta = document.createElement('textarea');\n"
           "    try { ta.value = txt; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;opacity:0'; document.body.appendChild(ta); ta.focus(); ta.select(); ta.setSelectionRange(0, txt.length); ok = document.execCommand('copy'); } catch (e) { ok = false; }\n"
           "    if (ta.parentNode) ta.parentNode.removeChild(ta);\n"
           "    toast(ok ? okMsg : '복사가 막혀 있습니다 — [파일로 저장]을 써 보세요', ok ? 2000 : 3200);\n"
           "  }\n"
           "  try { if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(txt).then(function () { toast(okMsg); }, old); return; } } catch (e) { /* */ }\n"
           "  old();\n"
           "}\n"
           "function saveRowHtml(id, m, btn) {\n"
           "  return '<div class=\"row\" data-slot=\"' + id + '\"><i class=\"svn' + (id.charAt(0) === 's' ? '' : ' au') + '\">' + slotName(id) + '</i><span class=\"mid\"><span class=\"nm\"><span class=\"chip\" style=\"background:' + m.c + '\">' + m.f + '</span> ' + m.d + '</span>' +\n"
           "    '<span class=\"ds\">' + m.n + '성 · ' + fmt(m.tr) + '명' + (m.t ? ' · ' + saveWhen(m.t) : '') + '</span></span>' + (btn || '') + '</div>';\n"
           "}\n"
           "function showSaveSend() {\n"
           "  if (inGame() && !UI.play) saveGame();                          // 지금 모습을 자동 저장에 먼저 적는다 — '자동' 칸이 곧 지금 하는 판이다\n"
           "  var st = { id: '' }, game = inGame();\n"
           "  showDialog({\n"
           "    render: function () {\n"
           "      var h = dlgHead('세이브 파일 보내기') + '<div class=\"dlg-b shr\">', p = st.id ? saveFileText(st.id) : null;\n"
           "      if (!p) {\n"
           "        var ids = slotIds(), n = 0, rows = '';\n"
           "        for (var i = 0; i < ids.length; i++) { var m = slotInfo(ids[i]); if (!m || m.bad) continue; n++; rows += saveRowHtml(ids[i], m, '<button class=\"btn\" type=\"button\" data-a=\"spick\" data-v=\"' + ids[i] + '\">고르기</button>'); }\n"
           "        h += n ? '<p>보낼 판을 고르세요.' + (game ? ' <b>자동</b> = 지금 하는 판.' : '') + '</p><div class=\"rows svl\">' + rows + '</div>' : '<p class=\"note\">저장된 판이 없습니다 — 게임을 시작하면 턴마다 자동으로 저장됩니다.</p>';\n"
           "      } else {\n"
           "        var kb = Math.max(1, Math.round(p.text.length / 1024)), can = canShareFile(saveFileObj(p));\n"
           "        h += '<div class=\"rows svl\">' + saveRowHtml(st.id, p.meta, '<button class=\"btn\" type=\"button\" data-a=\"sback\">다른 판</button>') + '</div>' +\n"
           "          '<div class=\"cmds c1\">' + (can ? '<button class=\"cmd pri\" type=\"button\" data-a=\"sshare\"><b>보내기</b><small>앱 고르기 · 파일로 갑니다</small></button>' : '') +\n"
           "          '<button class=\"cmd' + (can ? '' : ' pri') + '\" type=\"button\" data-a=\"sdown\"><b>파일로 저장</b><small>' + p.name + ' · 약 ' + kb + 'KB</small></button>' +\n"
           "          '<button class=\"cmd\" type=\"button\" data-a=\"scopy\"><b>글자로 복사</b><small>붙여 넣어 보낼 때 · 글이 깁니다</small></button></div>' +\n"
           "          '<p class=\"note\">받는 사람: 게임을 열고 <b>불러오기 → 파일에서 가져오기</b>(복사해 보냈으면 <b>붙여넣기로 가져오기</b>).' + (can ? '' : ' 이 화면에서는 공유 창에 파일을 실을 수 없어 저장 · 복사만 됩니다.') + '</p>';\n"
           "      }\n"
           "      return h + '</div>';\n"
           "    },\n"
           "    on: {\n"
           "      spick: function (el) { st.id = el.getAttribute('data-v'); refreshDialog(); },\n"
           "      sback: function () { st.id = ''; refreshDialog(); },\n"
           "      sshare: function () {\n"
           "        var p = saveFileText(st.id), f = p ? saveFileObj(p) : null; if (!canShareFile(f)) { toast('이 화면에서는 파일을 공유 창에 실을 수 없습니다 — [파일로 저장]을 쓰세요', 3200); return; }\n"
           "        try { navigator.share({ files: [f], title: '삼국지 천하도 세이브', text: '삼국지 천하도 세이브(' + p.meta.f + ' · ' + p.meta.d + ') — ' + SHARE_URL + ' 에서 불러오기 → 파일에서 가져오기' }).then(function () { /* 보냈다 */ }, function (e) { if (!(e && e.name === 'AbortError')) toast('공유 창을 열지 못했습니다 — [파일로 저장]을 쓰세요', 3200); }); }\n"
           "        catch (e) { toast('공유 창을 열지 못했습니다 — [파일로 저장]을 쓰세요', 3200); }\n"
           "      },\n"
           "      sdown: function () { var p = saveFileText(st.id); if (p && saveDownload(p)) toast('파일로 내보냈습니다 — 내려받은 파일을 보내면 됩니다', 2800); else toast('이 화면에서는 파일을 내보낼 수 없습니다 — [글자로 복사]를 쓰세요', 3200); },\n"
           "      scopy: function () { var p = saveFileText(st.id); if (p) copyLong(p.text, '세이브를 복사했습니다'); }\n"
           "    }\n"
           "  }, true);\n"
           "}\n"
           "/* 저장본의 뼈대가 이 판의 지도 · 세력 · 병과와 맞는가(deserialize 는 너그러워서 뼈대가 어긋난 글도 받아들인다 — 그런 판은 열고 나서 멈춘다) */\n"
           "function saveShapeOk(g) {\n"
           "  function num(v) { return typeof v === 'number' && isFinite(v); }\n"
           "  var i, j, nf = g.factions.length, no = g.officers.length;\n"
           "  if (!num(g.year) || !num(g.month) || !(g.xun === 0 || g.xun === 1 || g.xun === 2) || g.turn < 0 || g.player < 0 || g.player >= nf) return false;\n"
           "  if (g.bases.length !== MAPDATA.bases.length || nf !== SCENARIO.factions.length || no < 1) return false;\n"
           "  for (i = 0; i < nf; i++) { var f = g.factions[i]; if (!f || typeof f.name !== 'string' || !f.name) return false; }\n"
           "  for (i = 0; i < no; i++) { var o = g.officers[i]; if (!o || typeof o.n !== 'string' || !num(o.f) || o.f < -1 || o.f >= nf || !num(o.ldr) || !num(o.war) || !num(o.int) || !num(o.pol) || !num(o.cha)) return false; }\n"
           "  for (i = 0; i < g.bases.length; i++) {\n"
           "    var b = g.bases[i]; if (!b || b.n !== MAPDATA.bases[i].n || !num(b.owner) || b.owner < -1 || b.owner >= nf || !num(b.troops) || b.troops < 0 || !num(b.gold) || !num(b.food) || !num(b.dur) || !b.w || typeof b.w !== 'object') return false;\n"
           "    if (b.plots !== undefined && !Array.isArray(b.plots)) return false;\n"
           "    for (j = 0; b.plots && j < b.plots.length; j++) { var p = b.plots[j]; if (!p || !num(p.c) || !num(p.r) || (p.fac && !FAC[p.fac.t])) return false; }\n"
           "  }\n"
           "  for (i = 0; i < g.units.length; i++) {\n"
           "    var u = g.units[i]; if (!u || !num(u.f) || u.f < 0 || u.f >= nf || !num(u.c) || !num(u.r) || !inMap(u.c, u.r) || !UNIT_TYPES[u.type] || !num(u.troops) || !Array.isArray(u.off) || !u.off.length) return false;\n"
           "    for (j = 0; j < u.off.length; j++) if (!num(u.off[j]) || u.off[j] < 0 || u.off[j] >= no) return false;\n"
           "  }\n"
           "  return true;\n"
           "}\n"
           "/* 열어 본다(하던 판은 그대로 둔다). 열린 뒤 화면이 처음에 쓰는 것들도 한 번 불러 본다 */\n"
           "function saveProbe(sv) {\n"
           "  var g0 = G, r0 = REPORT, e0 = EVQ, j0 = JOT, ok = false;\n"
           "  try { ok = deserialize(sv); if (ok) { facBases(G.player); G.units.forEach(function (u) { uLeader(u); uName(u); }); saveMetaOf(G, sv.length); serialize(); } } catch (e) { ok = false; }\n"
           "  G = g0; REPORT = r0; EVQ = e0; JOT = j0; if (g0) reindex();\n"
           "  return ok;\n"
           "}\n"
           "/* 받은 글 → { ok, s: 저장본, meta } 또는 { ok: false, why }. 남이 보낸 파일이므로 꼼꼼히 본다(머리말은 이 파일의 p3 에) */\n"
           "function saveParse(txt) {\n"
           "  function bad(w) { return { ok: false, why: w }; }\n"
           "  if (typeof txt !== 'string' || !txt.replace(/\\s+/g, '')) return bad('내용이 비어 있습니다');\n"
           "  if (txt.length > 6e6) return bad('파일이 너무 큽니다');\n"
           "  var a = txt.indexOf('{\"'), z = txt.lastIndexOf('}'), g = null;\n"
           "  if (a < 0 || z < a) return bad('천하도의 세이브 파일이 아닙니다');\n"
           "  try { g = JSON.parse(txt.slice(a, z + 1)); } catch (e) { return bad('세이브가 중간에 끊겼거나 깨졌습니다'); }\n"
           "  if (!g || g.ver !== 2 || !Array.isArray(g.factions) || !Array.isArray(g.officers) || !Array.isArray(g.bases) || !Array.isArray(g.units) || !Array.isArray(g.log) || typeof g.player !== 'number' || typeof g.turn !== 'number' || !g.factions[g.player]) return bad('천하도의 세이브 파일이 아닙니다');\n"
           "  var clean = true, n = 0, i;\n"
           "  (function walk(o, d) {\n"
           "    if (!clean) return;\n"
           "    if (typeof o === 'string') { if (o.length > 600 || /[<>\"]/.test(o)) clean = false; return; }\n"
           "    if (o && typeof o === 'object') { if (d > 14 || ++n > 400000) { clean = false; return; } for (var k in o) { if (/[<>\"]/.test(k)) { clean = false; return; } walk(o[k], d + 1); } }\n"
           "  })(g, 0);\n"
           "  for (i = 0; clean && i < g.factions.length; i++) if (!g.factions[i] || !/^#[0-9a-fA-F]{3,8}$/.test(String(g.factions[i].color))) clean = false;\n"
           "  if (!clean) return bad('알 수 없는 내용이 들어 있어 받지 않았습니다');\n"
           "  if (!saveShapeOk(g)) return bad('이 판에서는 열 수 없는 세이브입니다');\n"
           "  var sv = JSON.stringify(g);\n"
           "  if (!saveProbe(sv)) return bad('이 판에서는 열 수 없는 세이브입니다');\n"
           "  var m = saveMetaOf(g, sv.length); m.t = Date.now();\n"
           "  return { ok: true, s: sv, meta: m };\n"
           "}\n"
           "function firstEmptySlot() { for (var i = 1; i <= SAVE_SLOTS; i++) if (!lsGet(slotKey('s' + i))) return 's' + i; return ''; }\n"
           "function saveImportTo(id, res) {\n"
           "  var ok = slotWrite(id, res.s, res.meta);\n"
           "  toast(ok ? slotLabel(id) + '에 넣었습니다 — ' + res.meta.f + ' · ' + res.meta.d : (canStore() ? '넣지 못했습니다 — 저장 공간이 모자랍니다(안 쓰는 칸을 지워 주세요)' : '이 환경에서는 저장할 수 없습니다'), ok ? 2600 : 3400);\n"
           "  titleBtns(); return ok;\n"
           "}\n"
           "/* 받은 글을 저장 칸에 넣는다: 빈 번호 칸이 있으면 거기, 없으면 덮어쓸 칸을 고르게 한다. done = 넣은 뒤 할 일 */\n"
           "function flowImport(txt, done) {\n"
           "  var res = saveParse(txt);\n"
           "  if (!res.ok) { toast(res.why, 3600); return; }\n"
           "  var id = firstEmptySlot();\n"
           "  if (id) { saveImportTo(id, res); if (done) done(); return; }\n"
           "  var arm = '';\n"
           "  showDialog({\n"
           "    render: function () {\n"
           "      var h = dlgHead('넣을 칸 고르기') + '<div class=\"dlg-b\"><p>빈 칸이 없습니다. 받은 판(<b>' + res.meta.f + ' · ' + res.meta.d + '</b>)으로 덮어쓸 칸을 고르세요.</p><div class=\"rows svl\">';\n"
           "      for (var i = 1; i <= SAVE_SLOTS; i++) { var sid = 's' + i, m = slotInfo(sid); if (!m) continue; h += m.bad ? '<div class=\"row\" data-slot=\"' + sid + '\"><i class=\"svn\">' + i + '</i><span class=\"mid\"><span class=\"nm\">열 수 없는 저장</span></span><button class=\"btn\" type=\"button\" data-a=\"over\" data-v=\"' + sid + '\">덮어쓰기</button></div>' : saveRowHtml(sid, m, '<button class=\"btn' + (arm === sid ? ' pri' : '') + '\" type=\"button\" data-a=\"over\" data-v=\"' + sid + '\">' + (arm === sid ? '정말 덮어쓰기' : '덮어쓰기') + '</button>'); }\n"
           "      return h + '</div></div>';\n"
           "    },\n"
           "    on: { over: function (el) { var sid = el.getAttribute('data-v'); if (arm !== sid) { arm = sid; refreshDialog(); return; } var ok = saveImportTo(sid, res); backDialog(); if (ok && done) done(); } }\n"
           "  }, true);\n"
           "}\n"
           "function pickSaveFile(cb) {\n"
           "  var old = $('svPick'); if (old && old.parentNode) old.parentNode.removeChild(old);\n"
           "  var inp = document.createElement('input'); inp.type = 'file'; inp.id = 'svPick'; inp.accept = '.txt,.json,text/plain,application/json'; inp.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;opacity:0';\n"
           "  inp.addEventListener('change', function () {\n"
           "    var f = inp.files && inp.files[0]; if (inp.parentNode) inp.parentNode.removeChild(inp);\n"
           "    if (!f) return;\n"
           "    if (f.size > 6e6) { toast('파일이 너무 큽니다'); return; }\n"
           "    var rd = new FileReader(); rd.onload = function () { cb(String(rd.result || '')); }; rd.onerror = function () { toast('파일을 읽지 못했습니다'); }; rd.readAsText(f);\n"
           "  });\n"
           "  document.body.appendChild(inp); inp.click();\n"
           "}\n"
           "function showSavePaste(done) {\n"
           "  showDialog({\n"
           "    render: function () {\n"
           "      return dlgHead('붙여넣기로 가져오기') + '<div class=\"dlg-b shr\"><p>받은 세이브 글 전체를 아래 칸에 붙여 넣으세요.</p><textarea class=\"svta\" id=\"svTa\" spellcheck=\"false\" placeholder=\"삼국지 천하도 세이브 — …\"></textarea>' +\n"
           "        '<div class=\"cmds c2\"><button class=\"cmd\" type=\"button\" data-a=\"clip\"><b>붙여넣기</b><small>복사해 둔 글</small></button><button class=\"cmd pri\" type=\"button\" data-a=\"take\"><b>가져오기</b></button></div></div>';\n"
           "    },\n"
           "    on: {\n"
           "      clip: function () {\n"
           "        var no = function () { toast('붙여넣기가 막혀 있습니다 — 칸을 길게 눌러 붙여 넣으세요', 3200); };\n"
           "        try { if (navigator.clipboard && navigator.clipboard.readText) navigator.clipboard.readText().then(function (t) { var ta = $('svTa'); if (ta) ta.value = t; }, no); else no(); } catch (e) { no(); }\n"
           "      },\n"
           "      take: function () { var ta = $('svTa'), t = ta ? ta.value : ''; if (!t.replace(/\\s+/g, '')) { toast('붙여 넣은 글이 없습니다'); return; } backDialog(); flowImport(t, done); }\n"
           "    }\n"
           "  }, true);\n"
           "}")
# 불러오기 창: 가져오기 단추
s = rep(s, "      if (st.mode === 'load' && !anySave()) h += '<p class=\"note\">저장된 판이 없습니다.</p>';\n"
           "      return h + '</div><p class=\"note\">'",
           "      if (st.mode === 'load' && !anySave()) h += '<p class=\"note\">저장된 판이 없습니다.</p>';\n"
           "      if (st.mode === 'load') h += '</div><div class=\"cmds c2 svimp\"><button class=\"cmd\" type=\"button\" data-a=\"simport\"><b>파일에서 가져오기</b><small>받은 세이브 파일</small></button><button class=\"cmd\" type=\"button\" data-a=\"spaste\"><b>붙여넣기로 가져오기</b><small>복사해 받은 글</small></button>';\n"
           "      return h + '</div><p class=\"note\">'")
s = rep(s, "      sdel: function (el) {\n        var id = el.getAttribute('data-v');\n        if (st.arm !== 'd' + id) { st.arm = 'd' + id; refreshDialog(); return; }\n        slotDrop(id); st.arm = ''; refreshDialog(); titleBtns();\n      }\n",
           "      sdel: function (el) {\n        var id = el.getAttribute('data-v');\n        if (st.arm !== 'd' + id) { st.arm = 'd' + id; refreshDialog(); return; }\n        slotDrop(id); st.arm = ''; refreshDialog(); titleBtns();\n      },\n"
           "      simport: function () { pickSaveFile(function (t) { flowImport(t, function () { st.arm = ''; refreshDialog(); }); }); },\n"
           "      spaste: function () { showSavePaste(function () { st.arm = ''; refreshDialog(); }); }\n")
# 제목 화면의 [불러오기]: 저장이 없어도 열린다(파일을 받아 올 수 있으므로)
s = rep(s, "function titleBtns() { $('tCont').disabled = !hasSave(); $('tLoad').disabled = !anySave(); }",
           "function titleBtns() { $('tCont').disabled = !hasSave(); $('tLoad').disabled = false; }      // v0.12: [불러오기]는 늘 열린다 — 받은 세이브 파일을 가져올 수 있다")
# 불러오다 실패하면 하던 판으로 되돌린다
s = rep(s, "  var keep = (inGame() && !UI.play) ? serialize() : lsGet(SAVE_KEY), ok = false;\n  try { ok = deserialize(s); } catch (e) { ok = false; }\n  if (!ok) return false;",
           "  var keep = (inGame() && !UI.play) ? serialize() : lsGet(SAVE_KEY), ok = false, g0 = G, r0 = REPORT, e0 = EVQ, j0 = JOT;\n  try { ok = deserialize(s); } catch (e) { ok = false; }\n"
           "  if (!ok) { G = g0; REPORT = r0; EVQ = e0; JOT = j0; if (g0) reindex(); return false; }      // v0.12: 열지 못했으면 하던 판을 그대로 되돌린다")
# 도움말
s = rep(s, "<h3>공유</h3><p>제목 화면과 메뉴의 <b>공유</b>를 누르면 휴대폰의 공유 창이 열립니다(안 열리는 곳에서는 주소와 QR이 적힌 창). 보내는 것은 게임의 주소뿐이고, 저장한 판은 함께 가지 않습니다.</p>",
           "<h3>공유</h3><p>제목 화면과 메뉴의 <b>공유</b>를 누르면 주소와 QR이 적힌 창이 열립니다(<b>보내기</b>로 휴대폰의 공유 창). 주소만 보내면 받는 사람은 새 게임으로 시작합니다.</p>" +
           "<p><b>하던 판을 보내려면</b> 같은 창의 <b>세이브 파일 보내기</b>에서 판을 고르세요 — 공유 창에 파일로 싣거나, 파일로 저장하거나, 글자로 복사할 수 있습니다. 받는 사람은 <b>불러오기 → 파일에서 가져오기</b>(복사해 받았으면 <b>붙여넣기로 가져오기</b>)로 빈 저장 칸에 넣고 불러옵니다.</p>")
# 메뉴의 알림 글
s = rep(s, "턴마다 자동 저장 · 저장 칸 ' + SAVE_SLOTS + '개 · 이 기기에만 남습니다</p>", "턴마다 자동 저장 · 저장 칸 ' + SAVE_SLOTS + '개 · 이 기기에만 남습니다(다른 기기로는 공유 → 세이브 파일 보내기)</p>")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s = rep(s, ".qrw small { color: var(--dim); font-size: 12px; }",
           ".qrw small { color: var(--dim); font-size: 12px; }\n"
           "/* 세이브 파일 보내기 · 가져오기(v0.12) */\n"
           ".shr .shh { font: 900 15px var(--font-display); letter-spacing: .06em; margin: 16px 0 4px; padding-top: 12px; border-top: 1px solid var(--line-2); }\n"
           ".shr .svta { width: 100%; height: 132px; border: 1px solid var(--ink); border-radius: 2px; background: var(--paper); color: var(--ink); font: 500 12px/1.4 var(--font-body); padding: 8px 10px; margin: 2px 0 9px; box-sizing: border-box; resize: none; }\n"
           ".cmds.svimp { margin-top: 10px; }\n"
           ".shr .rows.svl { margin-bottom: 10px; }")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
