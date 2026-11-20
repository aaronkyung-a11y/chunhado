# v0.8 성역 멈춤 없애기 — 화면 쪽
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "if (t.kind === 'base' && zoneFresh(su, t.b) && hdist(su.c, su.r, c, r) <= uRange(su)) toast('성역에 막 들어선 부대는 이번 턴에 성을 칠 수 없습니다 — 다음 턴에 공격하세요', 2800);",
           "if (t.kind === 'base' && justOut(su) && hdist(su.c, su.r, c, r) <= uRange(su)) toast('출진한 턴에는 거점을 칠 수 없습니다 — 다음 턴에 공격하세요', 2800);")
s = rep(s, "      if (res.halted) zoneToast(res.from, c, r);\n", "")
i0 = s.index("/* 성역의 경계를 넘었을 때의 안내 */"); i1 = s.index("function estBase(u, b) {")
s = s[:i0] + s[i1:]
s = rep(s, "var e = estBase(u, t.b), fresh = zoneFresh(u, t.b);", "var e = estBase(u, t.b), fresh = justOut(u);")
s = rep(s, "sub: fresh ? '성역에 막 들어섬 — 다음 턴부터' : ", "sub: fresh ? '출진한 턴 — 다음 턴부터' : ")
a0 = s.index("            (x.zin >= 0 && G.bases[x.zin].owner >= 0"); a1 = s.index("\n", a0) + 1
s = s[:a0] + s[a1:]
h0 = s.index("  '<h3>성역과 행군 일수</h3>"); h1 = s.index("\n", h0) + 1
s = s[:h0] + """  '<h3>성역과 행군</h3><p>성 둘레 ' + ZONE_R + '칸(붓으로 두른 고리 안)은 그 성의 <b>성역</b>입니다. 성역을 드나들 때 멈추지 않습니다 — 이동력이 남아 있으면 그대로 나아가고, 닿으면 바로 칠 수 있습니다. 다만 <b>출진한 그 턴에는 거점을 칠 수 없습니다</b>(부대끼리는 싸울 수 있습니다). 성에서 나와 다른 성을 치기까지 가까운 성끼리는 20일(2턴), 대개는 30일 넘게 걸립니다.</p>' +
""" + s[h1:]
s = rep(s, "이웃 성까지는 적어도 30일, 보통 40~60일이 걸립니다. 군량이 떨어지면 병사가 흩어집니다.</p>", "이웃 거점까지는 가까우면 20일, 보통 30~50일이 걸립니다. 군량이 떨어지면 병사가 흩어집니다.</p>")
s = rep(s, "<b>적</b>을 눌러 공격합니다. 이웃 성까지는 적어도 30일이 걸립니다.</li>", "<b>적</b>을 눌러 공격합니다. 이웃 거점까지는 가까우면 20일, 보통 30~50일이 걸립니다.</li>")
assert 'zoneFresh' not in s and 'zoneToast' not in s and '.zin' not in s and 'halted' not in s
io.open(p, 'w', encoding='utf-8').write(s)
p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "else ovPut(k, (UI.rc.halt ? UI.rc.halt[k] : ZONE[k] !== ZONE[K(su.c, su.r)]) ? [96, 118, 140] : [47, 79, 111], 122); }", "else ovPut(k, [47, 79, 111], 122); }")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
