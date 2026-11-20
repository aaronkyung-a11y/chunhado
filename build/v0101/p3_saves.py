# v0.10.1 (3/…): 세이브 칸 여러 개  (data.js · ui_panels.js · index.html · style.css)
#  요청: "세이브 파일도 하나밖에 없는게 좀 그래 여러개 만들면 좋겠다"
#  - 칸: 자동(턴마다 · 화면을 떠날 때 — 전부터 쓰던 chunhado_save_v2 그대로라 하던 판이 이어진다) · 직전(새 게임이나 불러오기로 밀려난 판, 한 번만) · 1~6(직접 저장).
#  - 메뉴의 [저장] · [불러오기] 가 칸을 고르는 창을 연다. 빈 칸은 바로 저장, 찬 칸은 한 번 더 눌러 덮어쓴다. 직접 저장하면 자동 저장도 같은 모습으로 맞춘다.
#    불러오면 하던 판의 지금 모습이 '직전' 칸에 남는다(잘못 불러와도 되돌릴 수 있다). 지우기는 × → 한 번 더.
#  - 제목 화면: [이어하기](자동 저장) 옆에 [불러오기].
#  - 칸마다 요약(세력 · 날짜 · 거점 수 · 병력 · 저장한 때)을 chunhado_save_v2_meta 에 따로 적는다. 없거나 저장본과 어긋나면 저장본을 읽어 다시 만든다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- data.js
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var SAVE_KEY = 'chunhado_save_v2';\n",
           "var SAVE_KEY = 'chunhado_save_v2';\n"
           "var SAVE_SLOTS = 6;                      // 직접 저장하는 칸 수(v0.10.1). 자동 저장은 SAVE_KEY 그대로, 직전 판은 SAVE_KEY + '_prev', 칸은 SAVE_KEY + '_s1' …\n")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui_panels.js
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()

# 1) 메뉴: 저장 · 불러오기는 칸을 고르는 창으로
s = rep(s, "      save: function () { toast(saveGame() ? '저장했습니다' : '이 환경에서는 저장할 수 없습니다'); },\n"
           "      load: function () { if (loadGame()) { closeDialog(); clearSel(); startGame(); toast('불러왔습니다'); } else toast('저장된 게임이 없습니다'); },\n",
           "      save: function () { showSaves('save'); },\n"
           "      load: function () { showSaves('load'); },\n")
s = rep(s, "<p class=\"note\">턴마다 자동 저장 · 이 기기에만 남습니다</p>", "<p class=\"note\">턴마다 자동 저장 · 저장 칸 ' + SAVE_SLOTS + '개 · 이 기기에만 남습니다</p>")

# 2) 저장 함수
s = rep(s, "function saveGame() { if (!G || G.over || UI.play) return false; try { localStorage.setItem(SAVE_KEY, serialize()); return true; } catch (e) { return false; } }\n"
           "function hasSave() { try { return !!localStorage.getItem(SAVE_KEY); } catch (e) { return false; } }\n"
           "function loadGame() { try { var s = localStorage.getItem(SAVE_KEY); return s ? deserialize(s) : false; } catch (e) { return false; } }\n"
           "function dropSave() { try { localStorage.removeItem(SAVE_KEY); } catch (e) { /* */ } }\n",
r"""/* 저장 칸(v0.10.1): 'auto' = 자동 저장(턴마다 · 화면을 떠날 때. 전부터 쓰던 SAVE_KEY 그대로) · 'prev' = 직전 판(새 게임이나 불러오기로 밀려난 판) · 's1'~ = 직접 저장.
   칸마다 요약(세력 · 날짜 · 거점 · 병력 · 저장한 때)을 SAVE_KEY + '_meta' 에 따로 적어 둔다 — 없거나 저장본과 길이가 다르면 저장본을 읽어 다시 만든다. */
function slotKey(id) { return id === 'auto' ? SAVE_KEY : SAVE_KEY + '_' + id; }
function slotIds() { var a = ['auto', 'prev']; for (var i = 1; i <= SAVE_SLOTS; i++) a.push('s' + i); return a; }
function slotName(id) { return id === 'auto' ? '자동' : (id === 'prev' ? '직전' : id.slice(1)); }
function slotLabel(id) { return id === 'auto' ? '자동 저장' : (id === 'prev' ? '직전 판' : id.slice(1) + '번 칸'); }
function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function lsSet(k, v) { try { localStorage.setItem(k, v); return true; } catch (e) { return false; } }
function lsDel(k) { try { localStorage.removeItem(k); } catch (e) { /* */ } }
function canStore() { if (!lsSet(SAVE_KEY + '_probe', '1')) return false; lsDel(SAVE_KEY + '_probe'); return true; }      // 저장 자체가 되는 환경인가(안 되면 공간이 모자란 것과 구별한다)
function saveMetaOf(g, len) {
  var tr = 0, nb = 0, i;
  for (i = 0; i < g.bases.length; i++) if (g.bases[i].owner === g.player) { nb++; tr += g.bases[i].troops; }
  for (i = 0; i < g.units.length; i++) if (g.units[i].f === g.player) tr += g.units[i].troops;
  return { f: g.factions[g.player].name, c: g.factions[g.player].color, d: g.year + '년 ' + g.month + '월 ' + ['상순', '중순', '하순'][g.xun], turn: g.turn, n: nb, tr: tr, t: Date.now(), len: len };
}
function metaAll() { try { return JSON.parse(lsGet(SAVE_KEY + '_meta') || '{}') || {}; } catch (e) { return {}; } }
function metaPut(id, m) { var a = metaAll(); if (m) a[id] = m; else delete a[id]; lsSet(SAVE_KEY + '_meta', JSON.stringify(a)); }
/* 칸의 요약. 비었으면 null, 열 수 없는 저장이면 { bad: true } */
function slotInfo(id) {
  var s = lsGet(slotKey(id)); if (!s) return null;
  var m = metaAll()[id];
  if (m && m.len === s.length) return m;
  try { var g = JSON.parse(s); if (!g || g.ver !== 2) return { bad: true }; m = saveMetaOf(g, s.length); m.t = 0; metaPut(id, m); return m; } catch (e) { return { bad: true }; }
}
function slotWrite(id, s, m) { if (!lsSet(slotKey(id), s)) return false; metaPut(id, m); return true; }
function slotDrop(id) { lsDel(slotKey(id)); metaPut(id, null); }
function inGame() { return !!G && !G.over && $('title').classList.contains('off'); }
function saveGame() { if (!G || G.over || UI.play) return false; var s = serialize(); return slotWrite('auto', s, saveMetaOf(G, s.length)); }
/* 직접 저장: 그 칸에 적고, 자동 저장도 같은 모습으로 맞춘다([이어하기]가 늘 가장 나중의 모습이 되게) */
function saveTo(id) { if (!G || G.over || UI.play) return false; var s = serialize(), m = saveMetaOf(G, s.length); if (!slotWrite(id, s, m)) return false; slotWrite('auto', s, m); return true; }
function hasSave() { return !!lsGet(SAVE_KEY); }
function anySave() { var ids = slotIds(); for (var i = 0; i < ids.length; i++) if (lsGet(slotKey(ids[i]))) return true; return false; }
/* 자동 저장이 다른 판으로 바뀌기 전에 '직전' 칸에 남긴다(새 게임 · 불러오기). keep = 남길 저장본(없으면 지금의 자동 저장) */
function keepPrev(keep) {
  var s = keep || lsGet(SAVE_KEY); if (!s) return;
  var m = null; try { m = saveMetaOf(JSON.parse(s), s.length); } catch (e) { return; }
  var old = metaAll().auto; if (!keep && old && old.len === s.length) m.t = old.t;       // 자동 저장을 그대로 옮길 때는 저장한 때도 그대로
  slotWrite('prev', s, m);
}
/* 칸을 불러온다. 하던 판의 지금 모습(제목 화면에서는 자동 저장)은 '직전' 칸에 남고, 불러온 판이 자동 저장이 된다 */
function loadFrom(id) {
  var s = lsGet(slotKey(id)); if (!s) return false;
  var keep = (inGame() && !UI.play) ? serialize() : lsGet(SAVE_KEY), ok = false;
  try { ok = deserialize(s); } catch (e) { ok = false; }
  if (!ok) return false;
  if (keep && keep !== s) keepPrev(keep);
  if (id !== 'auto') { var m = metaAll()[id], m2 = saveMetaOf(G, s.length); if (m && m.len === s.length) { m2.n = m.n; m2.tr = m.tr; } slotWrite('auto', s, m2); }
  return true;
}
function loadGame() { return loadFrom('auto'); }
function dropSave() { slotDrop('auto'); }
function saveWhen(t) {
  if (!t) return '';
  var d = new Date(t), n = new Date(), p2 = function (v) { return (v < 10 ? '0' : '') + v; }, hm = p2(d.getHours()) + ':' + p2(d.getMinutes());
  return (d.toDateString() === n.toDateString() ? '오늘 ' : (d.getMonth() + 1) + '월 ' + d.getDate() + '일 ') + hm;
}
/* 저장 · 불러오기 창. mode 'save' | 'load'. 제목 화면에서는 불러오기만 */
function showSaves(mode) {
  var game = inGame(), st = { mode: game ? mode : 'load', arm: '' };
  showDialog({
    render: function () {
      var ids = slotIds(), h = dlgHead(game ? '저장 · 불러오기' : '불러오기') + '<div class="dlg-b">';
      if (game) h += '<div class="seg"><button type="button" data-a="smode" data-v="save"' + (st.mode === 'save' ? ' class="on"' : '') + '>저장</button><button type="button" data-a="smode" data-v="load"' + (st.mode === 'load' ? ' class="on"' : '') + '>불러오기</button></div>';
      h += '<div class="rows svl">';
      for (var i = 0; i < ids.length; i++) {
        var id = ids[i], m = slotInfo(id), manual = id.charAt(0) === 's', act = '', del = '';
        if (!manual && (!m || st.mode === 'save')) continue;       // 자동 · 직전: 있을 때만, 불러올 때만 보인다(저장은 번호 칸에만)
        if (st.mode === 'load' && !m) continue;                    // 불러올 때는 찬 칸만
        if (st.mode === 'save') act = '<button class="btn' + (st.arm === 'w' + id ? ' pri' : '') + '" type="button" data-a="ssave" data-v="' + id + '">' + (st.arm === 'w' + id ? '덮어쓰기' : '저장') + '</button>';
        else if (m && !m.bad) act = '<button class="btn" type="button" data-a="sload" data-v="' + id + '">불러오기</button>';
        if (m && id !== 'auto') del = '<button class="btn del' + (st.arm === 'd' + id ? ' pri' : '') + '" type="button" data-a="sdel" data-v="' + id + '" aria-label="' + slotLabel(id) + ' 지우기">' + (st.arm === 'd' + id ? '지움' : '×') + '</button>';
        h += '<div class="row' + (m ? '' : ' emp') + '" data-slot="' + id + '"><i class="svn' + (manual ? '' : ' au') + '">' + slotName(id) + '</i><span class="mid">' +
          (!m ? '<span class="ds">빈 칸</span>' : (m.bad ? '<span class="nm">열 수 없는 저장</span>' : '<span class="nm"><span class="chip" style="background:' + m.c + '">' + m.f + '</span> ' + m.d + '</span><span class="ds">' + m.n + '성 · ' + fmt(m.tr) + '명' + (m.t ? ' · ' + saveWhen(m.t) : '') + '</span>')) +
          '</span>' + act + del + '</div>';
      }
      if (st.mode === 'load' && !anySave()) h += '<p class="note">저장된 판이 없습니다.</p>';
      return h + '</div><p class="note">' + (st.mode === 'save' ? '자동 저장은 턴마다 따로 됩니다.' : '<b>자동</b> = 턴마다 저절로 · <b>직전</b> = 새 게임 · 불러오기 바로 앞의 판') + '</p></div>';
    },
    on: {
      smode: function (el) { st.mode = el.getAttribute('data-v'); st.arm = ''; refreshDialog(); },
      ssave: function (el) {
        var id = el.getAttribute('data-v');
        if (slotInfo(id) && st.arm !== 'w' + id) { st.arm = 'w' + id; refreshDialog(); return; }      // 찬 칸: 한 번 더 눌러야 덮어쓴다
        var ok = saveTo(id); st.arm = '';
        toast(ok ? slotLabel(id) + '에 저장했습니다' : (canStore() ? '저장하지 못했습니다 — 저장 공간이 모자랍니다(안 쓰는 칸을 지워 주세요)' : '이 환경에서는 저장할 수 없습니다'), ok ? 1800 : 3200);
        refreshDialog();
      },
      sload: function (el) {
        var id = el.getAttribute('data-v');
        if (!loadFrom(id)) { toast('불러오지 못했습니다'); return; }
        closeDialog(); if (game) clearSel(); startGame(); toast(dateStr() + ' — ' + slotLabel(id) + '을 불러왔습니다', 2200);
      },
      sdel: function (el) {
        var id = el.getAttribute('data-v');
        if (st.arm !== 'd' + id) { st.arm = 'd' + id; refreshDialog(); return; }
        slotDrop(id); st.arm = ''; refreshDialog(); titleBtns();
      }
    }
  }, true);
}
function titleBtns() { $('tCont').disabled = !hasSave(); $('tLoad').disabled = !anySave(); }
""")

# 3) 제목 화면
s = rep(s, "  $('tCont').disabled = !hasSave();\n", "  titleBtns(); talkHide();                                    // 제목 화면에는 대화창을 남기지 않는다\n")
s = rep(s, "    if (!G || G.over || UI.play || G.turn !== turn || UI.briefT === turn) return;      // 한 턴에 한 번\n",
           "    if (!G || G.over || UI.play || G.turn !== turn || UI.briefT === turn || !inGame()) return;      // 한 턴에 한 번(제목 화면으로 나갔으면 말하지 않는다)\n")
s = rep(s, "  $('tCont').addEventListener('click', function () { audioInit(); if (loadGame()) { startGame(); toast(dateStr() + ' — 이어서 합니다'); } else toast('저장된 게임이 없습니다'); });\n",
           "  $('tCont').addEventListener('click', function () { audioInit(); if (loadGame()) { startGame(); toast(dateStr() + ' — 이어서 합니다'); } else toast('저장된 게임이 없습니다'); });\n"
           "  $('tLoad').addEventListener('click', function () { audioInit(); playBgm('title'); sfx('ui'); showSaves('load'); });\n")

# 4) 새 게임: 하던 판(자동 저장)을 '직전' 칸에 남기고, 새 판을 바로 자동 저장에 적는다
s = rep(s, "      go: function () { if (st.f < 0) return; closeDialog(); newGame(st.f); startGame(); sfx('gong'); showIntro(); }",
           "      go: function () { if (st.f < 0) return; closeDialog(); keepPrev(); newGame(st.f); saveGame(); startGame(); sfx('gong'); showIntro(); }")

# 5) 도움말
s = rep(s, "  '<h3>앱으로 설치</h3>",
           "  '<h3>저장</h3><p>턴이 끝날 때와 화면을 떠날 때 저절로 저장됩니다(<b>자동</b>) — 제목 화면의 <b>이어하기</b>가 이것을 엽니다. 메뉴의 <b>저장</b>에서 번호 칸 ' + SAVE_SLOTS + '개에 따로 남길 수 있고(찬 칸은 한 번 더 눌러 덮어씁니다), <b>불러오기</b>에서 골라 엽니다. 새 게임을 시작하거나 다른 칸을 불러오면 하던 판은 <b>직전</b> 칸에 한 번 남습니다. 저장은 이 기기의 이 주소에만 남습니다.</p>' +\n"
           "  '<h3>앱으로 설치</h3>")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- index.html
p = 'src/index.html'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "      <button id=\"tCont\" type=\"button\">이어하기</button>\n",
           "      <div class=\"t-row\"><button id=\"tCont\" type=\"button\">이어하기</button><button id=\"tLoad\" type=\"button\">불러오기</button></div>\n")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- style.css
p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += ("\n/* ---------- v0.10.1: 저장 칸 ---------- */\n"
      ".t-row { display: flex; gap: 10px; }\n"
      ".t-row button { flex: 1; min-width: 0; letter-spacing: .12em; }\n"
      ".seg { display: flex; border: 1px solid var(--ink); border-radius: 2px; margin: 2px 0 6px; overflow: hidden; }\n"
      ".seg button { flex: 1; height: 38px; font: 900 15px var(--font-display); color: var(--dim); letter-spacing: .08em; }\n"
      ".seg button.on { background: var(--ink); color: var(--paper); }\n"
      ".rows.svl .row { min-height: 60px; gap: 9px; cursor: default; }\n"
      ".rows.svl .row:active { background: none; }\n"
      ".rows.svl .row .nm .chip { margin-left: 0; margin-right: 3px; font-size: 11.5px; }\n"
      ".svn { flex: none; width: 34px; height: 34px; border-radius: 50%; border: 1.4px solid var(--ink); display: flex; align-items: center; justify-content: center; font: 900 16px var(--font-display); font-style: normal; background: var(--paper); }\n"
      ".svn.au { border-radius: 3px; font: 800 11.5px var(--font-body); background: var(--paper-2); }\n"
      ".rows.svl .row.emp .svn { border-style: dashed; border-color: var(--dim); color: var(--dim); }\n"
      ".rows.svl .btn { flex: none; height: 40px; padding: 0 12px; min-width: 62px; }\n"
      ".rows.svl .btn.del { min-width: 38px; padding: 0 8px; color: var(--dim); border-color: var(--line-2); font-size: 16px; }\n"
      ".rows.svl .btn.del.pri { color: var(--seal-ink); border-color: var(--seal-2); min-width: 52px; font-size: 14px; }\n")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
