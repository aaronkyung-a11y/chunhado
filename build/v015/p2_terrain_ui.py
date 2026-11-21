#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.15 — 지형을 화면에 적는다(ui_panels.js · style.css).
   · 부대 창: 선 칸의 지형과 높이, 그 효과 한 줄
   · 대상 창: 이 싸움에 걸리는 지형의 값 — 내 공격과 상대의 반격에 무엇이 얼마나 곱해지는가
   · 빈 땅을 눌렀을 때의 알림에 높이
   · 도움말"""
import os, io
ROOT = os.environ.get('CH_ROOT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
def rd(n): return io.open(os.path.join(ROOT, 'src', n), encoding='utf-8').read()
def wr(n, s): io.open(os.path.join(ROOT, 'src', n), 'w', encoding='utf-8').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:70])
    return s.replace(a, b)

s = rd('ui_panels.js')
UI = r'''/* ---------- 지형 풀이(v0.15) ---------- */
function pctTxt(m) { var p = Math.round((m - 1) * 100); return (p > 0 ? '+' : '−') + Math.abs(p) + '%'; }
var TERRAIN_SHORT = { p: '', f: '받는 피해 −15%', h: '받는 피해 −15%', d: '', w: '공격 −30% · 받는 피해 +20%' };
/* 부대가 선 칸: 지형 · 높이 · 그 칸의 효과 */
function terrLine(u) {
  var t = terr(u.c, u.r), cav = UNIT_TYPES[u.type].cls === 'horse', tx = TERRAIN_SHORT[t] || '';
  if (cav && (t === 'f' || t === 'h')) tx += (tx ? ' · ' : '') + '기병 공격 −15%'; else if (cav && t === 'p') tx = '기병 · 평지의 적에게 +10%';
  return '<div class="terrl"><i class="tmk">地</i><b>' + (isRoad(u.c, u.r) && t !== 'w' ? TERRAIN_NAME[t] + '(길)' : TERRAIN_NAME[t]) + '</b> · 높이 <b>' + elevOf(u.c, u.r) + '</b>' + (tx ? '<span>' + tx + '</span>' : '') + '</div>';
}
/* 이 싸움에 걸리는 지형의 값: a 가 d 를 칠 때(둘 다 부대) */
function terrNote(a, d) {
  var far = hdist(a.c, a.r, d.c, d.r) > 1, ms = terrMods(a, d, far), cs = far ? [] : terrMods(d, a, false), x = 1, y = 1, i;
  if (!ms.length && !cs.length) return '';
  for (i = 0; i < ms.length; i++) x *= ms[i].m;
  for (i = 0; i < cs.length; i++) y *= cs[i].m;
  var h = '<p class="note tnote"><b>지형</b> ';
  if (ms.length) h += ms.map(function (m) { return m.k + ' <em class="' + (m.m >= 1 ? 'good' : 'bad') + '">' + pctTxt(m.m) + '</em>'; }).join(' · ') + (ms.length > 1 ? ' → 내 피해 <em class="' + (x >= 1 ? 'good' : 'bad') + '">' + pctTxt(x) + '</em>' : '');
  else h += '내 피해는 그대로';
  if (cs.length) h += '<br>반격 ' + cs.map(function (m) { return m.k + ' <em class="' + (m.m <= 1 ? 'good' : 'bad') + '">' + pctTxt(m.m) + '</em>'; }).join(' · ') + (cs.length > 1 ? ' → <em class="' + (y <= 1 ? 'good' : 'bad') + '">' + pctTxt(y) + '</em>' : '');
  return h + '</p>';
}
function targetActions(u, t) {'''
s = rep(s, "function targetActions(u, t) {", UI)
# 부대 창
s = rep(s, "(x.type === 'trans' && mine ? cargoLine(x) : '') + statusBanner(x);", "(x.type === 'trans' && mine ? cargoLine(x) : '') + terrLine(x) + statusBanner(x);")
# 대상 창
s = rep(s, "          if (t.kind === 'unit' && t.u.status) h += '<p class=\"note stn\">'", "          if (t.kind === 'unit') h += terrNote(x, t.u);                                    // v0.15: 이 싸움에 걸리는 지형\n          if (t.kind === 'unit' && t.u.status) h += '<p class=\"note stn\">'")
# 빈 땅
s = rep(s, "  toast(TERRAIN_NAME[tt] + (isRoad(c, r) && tt !== 'w' ? ' (길)' : (isRoad(c, r) ? ' (나루)' : '')) + ' — ' + TERRAIN_DESC[tt], 1800);",
           "  toast(TERRAIN_NAME[tt] + (isRoad(c, r) && tt !== 'w' ? ' (길)' : (isRoad(c, r) ? ' (나루)' : '')) + (tt === 'm' || tt === 's' || tt === 'x' ? '' : ' · 높이 ' + elevOf(c, r)) + ' — ' + TERRAIN_DESC[tt], 2600);")
# 도움말
s = rep(s, "  '<h3>지도</h3>", "  '<h3>지형</h3><p>먹으로 짙게 그린 <b>산</b>과 바다 · 변경은 지나갈 수 없고, 그런 칸에는 <b>칸 줄이 없습니다</b>. 칸 줄이 보이는 곳은 모두 갈 수 있는 땅입니다. 빈 땅을 누르면 지형과 높이가 뜹니다.</p><ul>' +\n"
           "  '<li><b>높낮이</b> — 칸마다 높이가 있습니다. 치는 칸이 맞는 칸보다 한 단 높을 때마다 주는 피해 <b>+' + Math.round(ELEV_K.step * 100) + '%</b>, 낮을 때마다 −' + Math.round(ELEV_K.step * 100) + '% (' + ELEV_K.max + '단까지). 반격에도 같습니다 — 높은 곳을 차지하면 덜 맞고 더 세게 받아칩니다.</li>' +\n"
           "  '<li><b>숲 · 구릉</b> — 이동이 느립니다. 그 위의 부대는 받는 피해 −15%. 숲 속의 부대를 화살로 쏘면 −15% 더. 숲에서는 기병 전법을 쓸 수 없고 불이 번집니다.</li>' +\n"
           "  '<li><b>기병</b> — 평지에서 평지의 적을 치면 +10%. 숲 · 구릉에서 치거나 숲 · 구릉의 적을 치면 −15%.</li>' +\n"
           "  '<li><b>강</b> — 건너는 데 이동력이 많이 듭니다(나루는 덜). 물 위에서는 공격 −30%, 받는 피해 +20%.</li>' +\n"
           "  '<li>부대 창에 선 칸의 지형과 높이가, 적 부대를 고르면 대상 창에 <b>그 싸움에 걸리는 지형의 값</b>이 적힙니다. 예상 피해에는 이미 들어 있습니다.</li></ul>' +\n"
           "  '<h3>지도</h3>")
wr('ui_panels.js', s)

s = rd('style.css')
s += '''
/* ---------- 지형 풀이(v0.15) ---------- */
.terrl { display: flex; align-items: center; gap: 5px; margin: 6px 0 2px; font-size: 13px; color: var(--ink-2); }
.terrl b { color: var(--ink); } .terrl .tmk { font: 900 11.5px var(--font-display); font-style: normal; color: var(--ink-2); border: 1px solid #1b1a1855; padding: 0 3px; line-height: 1.35; }
.terrl span { margin-left: auto; font-size: 12px; color: var(--ink-2); }
.note.tnote { margin: 6px 0; padding: 5px 8px; border-left: 3px solid #6a645a; background: #1b1a180a; line-height: 1.5; }
.note.tnote em { font-style: normal; font-weight: 700; } .note.tnote em.good { color: #2f6f4f; } .note.tnote em.bad { color: var(--seal); }
'''
wr('style.css', s)
print('p2_terrain_ui ok')
