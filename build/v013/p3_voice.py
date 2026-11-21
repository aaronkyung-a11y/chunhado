#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.13 — 중국어 음성을 게임에 붙인다. 소리와 엔진은 새 파일(src/voicedata.js · src/voice.js)에 있고, 여기는 부르는 곳만 고친다.
   · core.js   actEv: 싸움 결과에 두 부대의 대장 번호를 적어 둔다(res.alead · res.tlead) — 화면의 음성이 누구 목소리인지 알아야 한다. 규칙은 그대로.
   · fx.js     animAct: 시작할 때 치는 쪽의 한마디. 음성이 나가면 전법의 기합 효과음(shout)은 내지 않는다(겹치지 않게)
   · ui_panels sayLine/talk: 대화창의 말에 갈래가 맞는 음성 · resultFx: 결과에 따른 한마디 · 메뉴에 [음성] 켜고 끄기 · 도움말
   · style.css 칸 위에 뜨는 뜻풀이(.flt.vsay) · 대결 화면의 뜻풀이(.du-float.vsay) — 이름이 .say(군사의 말 줄)와 겹치지 않게"""
import os, io
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
def rd(n): return io.open(os.path.join(ROOT, 'src', n), encoding='utf-8').read()
def wr(n, s): io.open(os.path.join(ROOT, 'src', n), 'w', encoding='utf-8').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:70])
    return s.replace(a, b)

# ---------- core.js ----------
s = rd('core.js')
s = rep(s, "res.aid = u.id; res.atype = u.type; res.af = f; res.ac0 = ac; res.ar0 = ar;",
           "res.aid = u.id; res.atype = u.type; res.af = f; res.ac0 = ac; res.ar0 = ar;\n    res.alead = u.off[0]; res.tlead = t && t.u ? t.u.off[0] : -1;      // v0.13: 두 부대의 대장(화면의 음성이 쓴다)")
wr('core.js', s)

# ---------- fx.js ----------
s = rd('fx.js')
s = rep(s, "  var touched = [];\n  function hold(o, p) {",
           "  var touched = [];\n  var voiced = typeof voiceAct === 'function' ? voiceAct(res, 0) : false;      // v0.13: 치는 쪽의 한마디(중국어 음성)\n  function hold(o, p) {")
s = rep(s, "tracks.push({ a: 0, b: 0, on: function () { sfx('shout'); } });",
           "tracks.push({ a: 0, b: 0, on: function () { if (!voiced) sfx('shout'); } });      // 음성이 나가면 기합 효과음은 겹치지 않게 뺀다")
wr('fx.js', s)

# ---------- ui_panels.js ----------
s = rd('ui_panels.js')
s = rep(s, "function talk(o, say, sub, ms) {\n",
           "function talk(o, say, sub, ms) {\n  voiceTalk(o);                                             // v0.13: 방금 고른 말이면 갈래에 맞는 음성을 붙인다(대화창을 꺼 두어도)\n")
s = rep(s, "function sayLine(o, key, x) {\n",
           "function sayLine(o, key, x) {\n  SAYV = { o: o.id, key: key, t: performance.now() };\n")
s = rep(s, "  if (res.fell) { sfx('fall'); if (res.af === G.player) sfx('cheerlate'); }\n}",
           "  if (res.fell) { sfx('fall'); if (res.af === G.player) sfx('cheerlate'); }\n  voiceAct(res, 1);                                         // v0.13: 결과에 따른 한마디\n}")
s = rep(s, "<button class=\"cmd\" type=\"button\" data-a=\"snd\"><b>효과음 ' + (UI.sound ? '켜짐' : '꺼짐') + '</b></button>",
           "<button class=\"cmd\" type=\"button\" data-a=\"snd\"><b>효과음 ' + (UI.sound ? '켜짐' : '꺼짐') + '</b></button><button class=\"cmd\" type=\"button\" data-a=\"voi\"><b>음성 ' + (UI.voice === false ? '꺼짐' : '켜짐') + '</b><small>' + (UI.sound ? '중국어' : '효과음이 꺼져 있음') + '</small></button>")
s = rep(s, "      snd: function () { UI.sound = !UI.sound; if (UI.sound) audioInit(); saveOpts(); refreshDialog(); },",
           "      snd: function () { UI.sound = !UI.sound; if (UI.sound) audioInit(); else voiceStop(true); saveOpts(); refreshDialog(); },\n"
           "      voi: function () { UI.voice = UI.voice === false; if (UI.voice === false) voiceStop(true); saveOpts(); toast(UI.voice ? '음성 켬 — 무장이 중국어로 한마디 합니다' : '음성 끔', 2000); refreshDialog(); },")
s = rep(s, "home: HOME.open, talk: UI.talk !== false }));", "home: HOME.open, talk: UI.talk !== false, voice: UI.voice !== false }));")
s = rep(s, "    if (o.talk === false) UI.talk = false;\n", "    if (o.talk === false) UI.talk = false;\n    if (o.voice === false) UI.voice = false;\n")
s = rep(s, "<h3>소리</h3><p>효과음과 음악은 메뉴에서 따로 끌 수 있습니다.",
           "<h3>소리</h3><p><b>음성</b> — 무장이 중국어로 한마디 합니다(출진 · 공격 · 전법 · 대성공 · 실패 · 적 부대 궤멸 · 함락 · 퇴각 · 일기토 · 계략 · 명령 · 등용). 목소리는 다섯 갈래입니다: 맹장(무력 88 이상 · 지력 72 미만) · 군주 · 지장(무력 70 미만) · 무장 · 여장. 싸움에서는 내가 낀 싸움에만 나오고, 칸 위에 뜻이 잠깐 뜹니다. 메뉴의 [음성]으로 끌 수 있고, 효과음을 끄면 함께 꺼집니다.</p><p>효과음과 음악은 메뉴에서 따로 끌 수 있습니다.")
wr('ui_panels.js', s)

# ---------- style.css ----------
s = rd('style.css')
s = rep(s, ".flt.big { font-size: 25px; letter-spacing: .04em; }",
           ".flt.big { font-size: 25px; letter-spacing: .04em; }\n.flt.vsay { font: 700 14px var(--font-body); color: #2a2620; letter-spacing: 0; }      /* 음성의 뜻풀이(v0.13) */")
s = rep(s, ".du-float.big { font-size: 36px; } .du-float.heal { color: #2f4f6f; }",
           ".du-float.big { font-size: 36px; } .du-float.heal { color: #2f4f6f; }\n/* 대결 화면에 뜨는 음성의 뜻풀이: 초상 위쪽의 말풍선. 길면 줄을 바꾸고, 화면 밖으로 나가지 않게 제 쪽 가장자리에 붙인다 */\n.du-float.vsay { left: 2px; right: auto; top: 3%; width: max-content; max-width: min(47vw, 200px); white-space: normal; text-align: left; font: 700 13.5px/1.35 var(--font-body); color: var(--ink); text-shadow: none; padding: 5px 8px; background: var(--paper); border: 1px solid #1b1a1855; box-shadow: 2px 3px 0 #1b1a1820; animation: duSay 2s ease-out forwards; }\n.du-f.d .du-float.vsay { left: auto; right: 2px; }\n@keyframes duSay { 0% { opacity: 0; transform: translateY(6px); } 10% { opacity: 1; transform: none; } 82% { opacity: 1; } 100% { opacity: 0; } }")
wr('style.css', s)
print('p3_voice ok')
