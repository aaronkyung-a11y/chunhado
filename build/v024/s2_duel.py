# -*- coding: utf-8 -*-
"""v0.24: (요청 11-25 19:00) "일기토가 시작될 때 일기토 패 라는 글씨가 나오던데.. 버그 같네? 일기토는 시작도 안 했는데."
까닭: 지난 열흘을 보여 줄 때, 내 부대가 얽힌 일기토는 처음부터 다시 그려 보인다(v0.13). 그런데 그 화면이 열리기 전에
  (1) 공격 연출의 끝에 결과 글씨('일기토 패 -N' — resultFx)가 먼저 뜨고  (2) 위쪽의 말(caption)에도 '… — 아무개 승' 이 먼저 적혔다.
고침: 다시 그려 보일 일기토면 두 가지 모두 일기토 화면이 닫힌 뒤에 보인다. 그 전에는 말에 '일기토!'(신청이면 '응함')까지만 적는다.
   python3 build/v024/s2_duel.py   (apply.sh 가 s1_rules.py 다음에 부른다)"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s)


def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:70], s.count(a))
    return s.replace(a, b)


u = rd('src/ui_panels.js')
# ───────── 결과의 말: 일기토의 승패를 아직 적지 않는 꼴 ─────────
u = rep(u, "function resultMsg(name, res) {",
        "function resultMsg(name, res, hideDuel) {                          // hideDuel(v0.24): 곧 일기토를 화면으로 보여 줄 것이면 승패는 아직 적지 않는다")
u = rep(u, "(res.accepted ? (res.duel ? ' — ' + (res.duel.draw ?", "(res.accepted ? (res.duel && !hideDuel ? ' — ' + (res.duel.draw ?")
u = rep(u, "  if (res.duel) msg += duelTxt(res.duel);\n", "  if (res.duel) msg += hideDuel ? ' · 일기토!' : duelTxt(res.duel);\n")
# ───────── 결과의 글씨: '일기토 패 -N' 을 따로 떼어, 뒤로 미룰 수 있게 ─────────
u = rep(u, "function resultFx(res) {", "function resultFx(res, noDuel) {                                   // noDuel(v0.24): '일기토 패' 글씨는 나중에(duelLossFx) — 일기토 화면이 닫힌 뒤에")
u = rep(u, "  if (res.duel && !res.duel.draw) floatText(res.duel.win ? tc : ac, res.duel.win ? tr : ar, '일기토 패 -' + fmt(res.duel.loss), C_INK, 1150, true, -8);",
        "  if (!noDuel) duelLossFx(res, 1150);")
u = rep(u, "function duelTxt(d) {",
        "/* 일기토에서 진 부대 위에 잃은 병력을 적는다. 일기토를 화면으로 다시 보여 줄 때는 그 화면이 닫힌 뒤에 부른다(v0.24 — 시작도 하기 전에 '일기토 패' 가 뜨던 것) */\n"
        "function duelLossFx(res, delay) {\n"
        "  if (!res || !res.duel || res.duel.draw) return;\n"
        "  var tc = res.tc1 !== undefined ? res.tc1 : (res.tc !== undefined ? res.tc : res.c), tr = res.tr1 !== undefined ? res.tr1 : (res.tr !== undefined ? res.tr : res.r);\n"
        "  var ac = res.ac1 !== undefined ? res.ac1 : res.ac, ar = res.ar1 !== undefined ? res.ar1 : res.ar;\n"
        "  floatText(res.duel.win ? tc : ac, res.duel.win ? tr : ar, '일기토 패 -' + fmt(res.duel.loss), '#1b1a18', delay || 0, true, -8);\n"
        "}\n"
        "function duelTxt(d) {")
# ───────── 지난 열흘: AI 가 건 일기토(신청) ─────────
u = rep(u, "      var r = e.res;\n      setCaption(e.f, resultMsg(e.name, r), e.tf === G.player ? 'hit' : '');\n",
        "      var r = e.res, rp = !!(r.accepted && r.duelRec && r.duel && !P.skip && mineD);      // v0.24: 다시 그려 보일 것이면 승패는 그 화면이 닫힌 뒤에\n"
        "      setCaption(e.f, resultMsg(e.name, r, rp), e.tf === G.player ? 'hit' : '');\n")
u = rep(u, "      if (r.duelRec && r.duel && !P.skip && mineD) {", "      if (rp) {")
u = rep(u, "out: duelOutHtml(null, r.duel, e.name, r.tname || '') }, pg(function () { pwait(300 * k, cb); }));",
        "out: duelOutHtml(null, r.duel, e.name, r.tname || '') }, pg(function () {\n"
        "          setCaption(e.f, resultMsg(e.name, r), e.tf === G.player ? 'hit' : '');\n"
        "          if (!r.duel.draw) floatText(r.duel.win ? r.c : r.ac, r.duel.win ? r.r : r.ar, '일기토 패 -' + fmt(r.duel.loss), '#b5332a', 0, true, 22); else floatText(r.c, r.r, '비김', '#6a645a', 0, false, 22);\n"
        "          pwait(1100 * k, cb);\n"
        "        }));")
# ───────── 지난 열흘: 공격에서 벌어진 일기토 ─────────
u = rep(u, "      setCaption(e.f, (e.res.fell && restFall(e.res.tbase)) ? '<b>' + e.name + '</b> — ' + e.res.tname + ' 공격' : resultMsg(e.name, e.res), e.tf === G.player ? 'hit' : '');",
        "      var rec = e.res.duelRec, replay = !!(rec && e.res.duel && !P.skip && (e.f === G.player || e.tf === G.player));      // v0.24: 일기토를 다시 그려 보일 것이면 승패(말 · '일기토 패' 글씨)는 그 화면이 닫힌 뒤에\n"
        "      var capCls = e.tf === G.player ? 'hit' : '';\n"
        "      setCaption(e.f, (e.res.fell && restFall(e.res.tbase)) ? '<b>' + e.name + '</b> — ' + e.res.tname + ' 공격' : resultMsg(e.name, e.res, replay), capCls);")
u = rep(u, "        var rec = e.res.duelRec;\n        if (rec && e.res.duel && !P.skip && (e.f === G.player || e.tf === G.player)) {", "        if (replay && !P.skip) {")
u = rep(u, "out: duelOutHtml(null, e.res.duel, e.name, e.res.tname || '') }, pg(function () { pwait(300 * k, cb); }));\n          return;\n        }\n",
        "out: duelOutHtml(null, e.res.duel, e.name, e.res.tname || '') }, pg(function () {\n"
        "            setCaption(e.f, resultMsg(e.name, e.res), capCls); duelLossFx(e.res, 0);\n"
        "            pwait(1100 * k, cb);\n"
        "          }));\n          return;\n        }\n"
        "        if (replay) { setCaption(e.f, resultMsg(e.name, e.res), capCls); duelLossFx(e.res, 0); }      // 연출 사이에 건너뛰기를 눌렀다 — 화면 없이 결과만\n")
u = rep(u, "      }), function () { resultFx(e.res); });", "      }), function () { resultFx(e.res, replay); });")
wr('src/ui_panels.js', u)
print('s2_duel ok')
