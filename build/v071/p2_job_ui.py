# v0.7.1/v0.8 화면: 건설 담당 무장 표시, 건설 안내, 시설 창의 담당·공사 중단
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:90])
    return s.replace(a, b)
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()

s = rep(s, """function offStatus(o) {
  if (o.st === 'travel') return '이동 중 (' + days(o.eta) + ')';
  if (o.unit !== null) return '출진 중';
  return o.acted ? '행동 완료' : '대기';
}""", """function offStatus(o) {
  if (o.st === 'travel') return '이동 중 (' + days(o.eta) + ')';
  if (o.unit !== null) return '출진 중';
  var j = jobOf(o);
  if (j) return '<b class="job">' + FAC[j.fac.t].name + ' 건설 중</b> (' + days(j.left) + ')';      // 완공될 때까지 다른 일을 못 한다
  return o.acted ? '행동 완료' : '대기';
}""")

# 건설: 담당을 고를 때와 착공했을 때 "완공까지 묶인다"를 알린다
s = rep(s, """        preview: function (os) { var rate = 60 + Math.round((bestOf(os, 'pol') + sumOthers(os, 'pol') * 0.5) * 0.6); if (anyHas(os, '축성')) rate *= 2; return '완공까지 <b>' + days(Math.ceil(F.build / rate)) + '</b> · 금 ' + F.cost; } },
        function (os) { var r = cmdDevelop(b, pi, t, ids(os)); return done(r, r.ok ? F.name + ' 착공 — ' + days(r.turns) + ' 뒤 완공' : '', 'hammer'); });""",
"""        preview: function (os) { var rate = 60 + Math.round((bestOf(os, 'pol') + sumOthers(os, 'pol') * 0.5) * 0.6); if (anyHas(os, '축성')) rate *= 2; return '완공까지 <b>' + days(Math.ceil(F.build / rate)) + '</b> · 금 ' + F.cost + '<br><span class="warn">담당 무장은 완공될 때까지 다른 일을 못 합니다</span>'; } },
        function (os) { var r = cmdDevelop(b, pi, t, ids(os)); return done(r, r.ok ? F.name + ' 착공 — ' + days(r.turns) + ' 뒤 완공. ' + os.map(function (o) { return o.n; }).join('·') + '은(는) 그때까지 공사에 매입니다' : '', 'hammer'); });""")

# 시설 창: 짓는 중이면 담당과 남은 날, 철거 대신 '공사 중단'
s = rep(s, """(fc.done ? '' : '<p class="note">건설 중 — ' + days(Math.max(1, Math.ceil((fc.need - fc.prog) / fc.rate))) + ' 남음</p>') +""",
"""(fc.done ? '' : '<p class="note">건설 중 — ' + days(Math.max(1, Math.ceil((fc.need - fc.prog) / fc.rate))) + ' 남음' + (builders(fc).length ? ' · 담당 <b>' + builders(fc).map(function (o) { return o.n; }).join('·') + '</b> (완공될 때까지 다른 일을 못 합니다)' : '') + '</p>') +""")
s = rep(s, """        '<button class="cmd" type="button" data-a="demo"><b>철거</b><small>부지를 비웁니다</small></button></div>' +""",
"""        '<button class="cmd" type="button" data-a="demo"><b>' + (fc.done ? '철거' : '공사 중단') + '</b><small>' + (fc.done ? '부지를 비웁니다' : (builders(fc).length ? '부지를 비우고 담당 무장을 풉니다' : '부지를 비웁니다')) + '</small></button></div>' +""")
s = rep(s, """      demo: function (el) { if (el.getAttribute('data-c')) { cmdDemolish(b, pi); closeDialog(); sfx('miss'); toast(F.name + ' 철거'); refreshSheet(); afterAction(); } else { el.setAttribute('data-c', '1'); el.querySelector('b').textContent = '정말 철거?'; } }""",
"""      demo: function (el) {
        if (el.getAttribute('data-c')) {
          var was = fc.done, rd = cmdDemolish(b, pi), names = (rd.freed || []).map(function (id) { return off(id).n; });
          closeDialog(); sfx('miss');
          toast(was ? F.name + ' 철거' : F.name + ' 공사 중단' + (names.length ? ' — ' + names.join('·') + (off(rd.freed[0]).acted ? ' 풀려남(이번 턴은 쉼)' : ' 풀려남') : ''));
          refreshSheet(); afterAction();
        } else { el.setAttribute('data-c', '1'); el.querySelector('b').textContent = fc.done ? '정말 철거?' : '정말 중단?'; }
      }""")

# 도움말
s = rep(s, """'<h3>이번 판에 아직 없는 것</h3>""", """'<h3>무장이 묶이는 일</h3><p>대부분의 명령은 그 턴에 끝나서, 맡은 무장은 다음 턴에 다시 쓸 수 있습니다. <b>시설 건설</b>만은 여러 턴이 걸리고, 맡은 무장은 <b>완공될 때까지</b> 다른 명령도 출진도 이동도 못 합니다(무장 목록에 "○○ 건설 중"). 급하면 그 시설을 눌러 <b>공사 중단</b>을 하면 풀려납니다 — 들인 금은 돌아오지 않습니다. 성이 함락되면 짓다 만 시설은 버려집니다.</p>' +
  '<h3>이번 판에 아직 없는 것</h3>""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """
/* v0.8 — 공사에 매인 무장, 안내 글 */
.job { color: var(--seal); font-weight: 800; }
.warn { color: var(--seal); font-size: 12px; }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
