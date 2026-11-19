# v0.7 소리 큐: 전투 연출의 순간마다 맞는 소리
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:80])
    return s.replace(a, b)
p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "if (e && e.name === 'NotAllowedError') BGM.name = ''; else if (!e || e.name !== 'AbortError') next(); });",
           "if (e && e.name === 'NotAllowedError') { BGM.name = ''; BGM.idx[name] = i; } else if (!e || e.name !== 'AbortError') next(); });")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/fx.js'; s = io.open(p, encoding='utf-8').read()
# 계략: 두루마리 펴는 소리로 시작
s = rep(s, """    fxMark(tracks, 0, 520, 'enso', FX_INDIGO, pa, 0.8, 2.6, Math.random() * 6.28, { dy: 0.35, fade: 1.1, spin: 1.2 });
    hit = 300;""", """    fxMark(tracks, 0, 520, 'enso', FX_INDIGO, pa, 0.8, 2.6, Math.random() * 6.28, { dy: 0.35, fade: 1.1, spin: 1.2 });
    tracks.push({ a: 0, b: 0, on: function () { sfx('page'); } });
    hit = 300;""")
# 전법: 기합
s = rep(s, """      if (A) tracks.push({ a: 0, b: 240, step: function (u) { var s = 1 + 0.16 * Math.sin(Math.PI * u); A.sp.scale.set(A.sp.userData.w * s, A.sp.userData.h * s, 1); } });
      pre = 230;""", """      if (A) tracks.push({ a: 0, b: 240, step: function (u) { var s = 1 + 0.16 * Math.sin(Math.PI * u); A.sp.scale.set(A.sp.userData.w * s, A.sp.userData.h * s, 1); } });
      tracks.push({ a: 0, b: 0, on: function () { sfx('shout'); } });
      pre = 230;""")
# 쏘는 공격: 시위 소리, 여러 발이면 화살 무리
s = rep(s, """      var n = tac === '난사' ? 14 : (tac === '관시' ? 1 : (big ? 9 : 6)), colA = tac === '화시' && !res.fail ? FX_FIRE : FX_INK;""",
"""      var n = tac === '난사' ? 14 : (tac === '관시' ? 1 : (big ? 9 : 6)), colA = tac === '화시' && !res.fail ? FX_FIRE : FX_INK;
      tracks.push({ a: pre + 50, b: pre + 50, on: function () { sfx('bow'); if (n > 1) sfx('arrows'); } });""")
# 기병 전법: 말발굽
s = rep(s, "      tracks.push({ a: pre, b: pre + 210, on: function () { sfx('step'); fxDust(pa[0], pa[1], pa[2], 1.3); },",
           "      tracks.push({ a: pre, b: pre + 210, on: function () { sfx('charge'); fxDust(pa[0], pa[1], pa[2], 1.3); },")
# 반격
s = rep(s, """      fxHurt(tracks, c0 + (T && !ranged ? 170 : 330), A, ah, 0.11);
      end = Math.max(end, c0 + 620);""", """      fxHurt(tracks, c0 + (T && !ranged ? 170 : 330), A, ah, 0.11);
      (function (melee) { tracks.push({ a: c0 + (melee ? 150 : 0), b: c0 + (melee ? 150 : 0), on: function () { sfx(melee ? 'counter' : 'bow'); } }); })(!!(T && !ranged));
      end = Math.max(end, c0 + 620);""")
# 일기토
s = rep(s, "      tracks.push({ a: d0 + 110, b: d0 + 110, on: function () { fxShake(5, 260); } });",
           "      tracks.push({ a: d0, b: d0, on: function () { sfx('duel'); } });\n      tracks.push({ a: d0 + 110, b: d0 + 110, on: function () { fxShake(5, 260); } });")
# 궤멸
s = rep(s, "  if (res.killed && T) { fxVanish(tracks, end - 120, T, pt1); tracks.push({ a: end - 60, b: end - 60, on: function () { fxStamp(",
           "  if (res.killed && T) { fxVanish(tracks, end - 120, T, pt1); tracks.push({ a: end - 60, b: end - 60, on: function () { sfx('rout'); fxStamp(")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
