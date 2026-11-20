# v0.8 충성과 인연: "충성심이 이상하리만큼 낮아. 관계가 있는 무장은 충성심이 잘 안 떨어진다던가, 충성도가 굉장히 높아야할 것 같은데"
#  v0.7: 시작 충성 = 78 + 이름 값 % 20 (78~97, 군주와의 사이를 보지 않음 — 관우도 낮게 나올 수 있었다). 분기마다 30% 확률로 -1(60 까지). 등용된 무장 70~85.
#  고침: ① 인연(BONDS: 의형제·혈연·부부·인척·심복)이 있는 무장은 충성 100, 내려가지 않는다. 포로가 되어도 주군의 세력이 살아 있으면 등용에 거의 응하지 않는다(5% 까지)
#        ② 그 밖의 무장은 '자리 잡는 값'(86~93 + 군주 매력에 따른 -2~+6 → 80~98)으로 시작하고, 포상으로 올린 몫은 분기마다 30% 확률로 1씩 빠지며, 그보다 낮으면 분기마다 2씩 오른다
#        ③ 새로 온 무장(등용·포로 등용)은 70~85 에서 시작해 자리 잡는 값까지 오른다. 군주와 인연이 있는 무장을 등용하면 바로 100, 등용 확률 +30
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "/* 특기 */\nvar SKILLS = {", """/* 인연: 군주와 깊은 사이인 무장(군주 이름 → { 무장 이름: 사이 }). 그 군주를 모시는 동안 충성이 100 에서 내려가지 않는다.
   사이: 의형제 · 혈연(부자·형제·친족, 양자 포함) · 부부 · 인척(처가) · 심복(끝까지 따른 사람) */
var BONDS = {
  '조조': { '하후돈': '혈연', '하후연': '혈연', '조인': '혈연', '조홍': '혈연', '조순': '혈연', '조비': '혈연', '조창': '혈연', '전위': '심복', '허저': '심복' },
  '여포': { '초선': '부부', '여령기': '혈연', '고순': '심복', '진궁': '심복' },
  '유비': { '관우': '의형제', '장비': '의형제', '간옹': '심복', '진도': '심복', '조운': '심복', '미축': '인척', '손건': '심복', '제갈량': '심복', '유봉': '혈연', '관평': '심복', '관흥': '심복', '장포': '심복' },
  '원소': { '원담': '혈연', '원희': '혈연', '원상': '혈연', '고간': '혈연', '안량': '심복', '문추': '심복', '심배': '심복' },
  '공손찬': { '공손속': '혈연' },
  '공손도': { '공손강': '혈연', '공손공': '혈연' },
  '원술': { '원윤': '혈연', '기령': '심복' },
  '손책': { '손권': '혈연', '손정': '혈연', '손분': '혈연', '오경': '혈연', '주유': '의형제', '대교': '부부', '정보': '심복', '황개': '심복', '한당': '심복', '주치': '심복' },
  '엄백호': { '엄여': '혈연' },
  '유표': { '채모': '인척', '유반': '혈연', '황조': '심복' },
  '마등': { '마초': '혈연', '마철': '혈연', '마휴': '혈연', '마대': '혈연', '방덕': '심복', '한수': '의형제' },
  '장로': { '장위': '혈연' },
  '유장': { '황권': '심복', '장임': '심복', '엄안': '심복', '왕루': '심복' }
};

/* 특기 */
var SKILLS = {""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
# 도우미
s = rep(s, "function uLeader(u) { return off(u.off[0]); }", """/* 충성과 인연 */
function bondWith(o, f) {                 // 무장 o 와 세력 f 의 군주 사이(없으면 null)
  if (!o || f === undefined || f < 0 || !G.factions[f] || G.factions[f].lord === o.id) return null;
  var L = off(G.factions[f].lord), m = L && BONDS[L.n];
  return (m && m[o.n]) || null;
}
function bondOf(o) { return o ? bondWith(o, o.f) : null; }       // 지금 모시는 군주와의 사이
function loyNat(o) {                      // 충성이 자리 잡는 값: 인연이 있으면 100, 아니면 사람됨(이름에서 뽑은 86~93)과 군주의 매력(-2~+6)에 따라 80~98
  if (bondOf(o)) return 100;
  var L = (o.f >= 0 && G.factions[o.f]) ? off(G.factions[o.f].lord) : null;
  var h = (o.n.charCodeAt(0) * 7 + o.n.charCodeAt(o.n.length - 1) * 13) % 8;
  return clamp(Math.round(86 + h + ((L ? L.cha : 70) - 70) / 5), 80, 98);
}
function uLeader(u) { return off(u.off[0]); }""")
# 시작 충성
s = rep(s, "      else { o.loy = 78 + ((o.n.charCodeAt(0) + o.n.charCodeAt(o.n.length - 1)) % 20); o.merit = Math.max(0, (o.ldr + o.war - 120) * 20); }",
           "      else { o.merit = Math.max(0, (o.ldr + o.war - 120) * 20); }")
s = rep(s, """    G.officers.push(o);
  }
  reindex();
  REPORT = []; EVQ = [];
  phaseStart(G.player);""", """    G.officers.push(o);
  }
  for (i = 0; i < G.officers.length; i++) { var lo = G.officers[i]; if (lo.f >= 0 && G.factions[lo.f].lord !== lo.id) lo.loy = loyNat(lo); }   // 군주가 정해진 뒤에 매긴다
  reindex();
  REPORT = []; EVQ = [];
  phaseStart(G.player);""")
# 분기
s = rep(s, "      if (o.loy > 60 && chance(30)) o.loy--;\n", """      var nat = loyNat(o);
      if (nat >= 100) o.loy = 100;                                       // 인연: 내려가지 않는다
      else if (o.loy > nat) { if (chance(30)) o.loy--; }                 // 포상으로 올린 몫은 천천히 빠진다
      else if (o.loy < nat) o.loy = Math.min(nat, o.loy + 2);            // 새로 온 무장은 분기마다 2씩 자리를 잡는다
""")
# 해가 바뀌어 가담하는 무장
s = rep(s, "h.st = 'active'; h.f = lf; h.loc = lb.id; h.loy = 95; h.j = null;", "h.st = 'active'; h.f = lf; h.loc = lb.id; h.loy = 95; h.j = null; if (bondOf(h)) h.loy = 100;")
# 등용
s = rep(s, "  if (t.st === 'captive') { p -= 15; if (t.f >= 0 && G.factions[t.f].alive) p -= (t.loy - 60) * 0.8; }\n  return clamp(Math.round(p), 3, 95);",
           """  if (bondWith(t, b.owner)) p += 30;                                    // 내 군주와 인연이 있는 사람
  if (t.st === 'captive') { p -= 15; if (t.f >= 0 && G.factions[t.f].alive) p -= (t.loy - 60) * 0.8; }
  p = clamp(Math.round(p), 3, 95);
  if (t.st === 'captive' && t.f >= 0 && G.factions[t.f].alive && bondOf(t)) p = Math.min(p, 5);   // 주군과 인연이 있는 포로는 주군의 세력이 살아 있는 한 거의 응하지 않는다
  return p;""")
s = rep(s, "t.st = 'active'; t.f = b.owner; t.capF = -1; t.unit = null; t.acted = true; t.loy = 70 + ri(0, 15); t.merit = Math.round(t.merit * 0.5);",
           "t.st = 'active'; t.f = b.owner; t.capF = -1; t.unit = null; t.acted = true; t.loy = 70 + ri(0, 15); t.merit = Math.round(t.merit * 0.5); if (bondOf(t)) t.loy = 100;")
# 옛 저장: 인연 무장은 바로 100
s = rep(s, "  G = g; reindex(); REPORT = []; EVQ = [];\n  return true;\n}", """  G = g; reindex(); REPORT = []; EVQ = [];
  for (var oi = 0; oi < G.officers.length; oi++) { var go = G.officers[oi]; if (go.f >= 0 && go.st !== 'hidden' && bondOf(go)) go.loy = 100; }   // v0.8: 인연이 있는 무장
  return true;
}""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "(o.f >= 0 ? '<div><span>충성</span><b>' + o.loy + '</b></div>", "(o.f >= 0 ? '<div><span>충성</span><b>' + (isLord(o) ? '군주' : o.loy + (bondOf(o) ? ' <em class=\"bond\">' + bondOf(o) + '</em>' : '')) + '</b></div>")
s = rep(s, "'<h3>인재</h3><p>탐색으로 재야의 인재를 찾아 등용합니다. 사로잡은 적장도 등용할 수 있습니다. 충성이 낮은 무장은 떠날 수 있으니 포상하세요. 해가 바뀌면 새 인물이 세상에 나옵니다.</p>' +",
           "'<h3>인재</h3><p>탐색으로 재야의 인재를 찾아 등용합니다. 사로잡은 적장도 등용할 수 있습니다. 해가 바뀌면 새 인물이 세상에 나옵니다.</p>' +\n  '<h3>충성과 인연</h3><p>군주와 <b>인연</b>(의형제·혈연·부부·인척·심복)이 있는 무장은 충성이 100이고 내려가지 않습니다 — 무장 창의 충성 옆에 그 사이가 적혀 있습니다. 포로가 되어도 주군의 세력이 남아 있는 한 등용에 거의 응하지 않습니다. 그 밖의 무장은 군주의 매력에 따라 80~98 사이에 자리를 잡습니다. 새로 등용한 무장은 70~85에서 시작해 분기마다 2씩 오르고, 포상으로 올린 충성은 천천히 제자리로 돌아옵니다.</p>' +")
io.open(p, 'w', encoding='utf-8').write(s)
p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
if '.bond' not in s:
    s += "\n.bond { font-style: normal; font-size: 11.5px; font-weight: 800; color: var(--seal); border: 1px solid var(--seal); border-radius: 2px; padding: 0 4px; margin-left: 3px; vertical-align: 1px; }\n"
    io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
