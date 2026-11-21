# v0.11 (2/…): 등용과 옛 관계  (data.js · core.js · ai.js · ui_panels.js · style.css)
#  요청: "멸망한 세력 출신의 포로들은 좀 더 등용 가능성이 높아져야하고 과거 관계를 고려해서 등용에 응할 가능성이 달라져야한다.
#         즉, 과거에 군주였던 사람이 설득하면 좀 더 가능성이 높은 등"
#  - 무장마다 섬겼던 세력을 적는다: o.pf = 마지막으로 섬긴 세력, o.past = 그 앞의 세력들. 세력의 군주는 바뀌지 않으므로 '누가 누구의 옛 주군인가'를 알 수 있다.
#    세력이 바뀌는 곳이 여럿이라(등용 · 장성 · 멸망 · 이탈) 턴이 넘어갈 때와 등용 직후에 훑어서 적는다(pastSweep). 옛 저장은 시나리오의 세력으로 미루어 채운다.
#  - 멸망한 세력 출신: 포로는 '포로라서 −15'가 없어지고 +10(전보다 +25), 재야는 +10. 옛 군주 자신은 전과 같다.
#  - 보내는 무장과 대상의 사이(가장 큰 것 하나): 직접 인연(의형제·혈연·부부·인척·심복) +50 · 옛 주군 +30 · 같은 주군과 인연으로 묶인 사이 +30 · 옛 신하 +20 · 옛 동료 +12
#  - 대상이 예전에 이 세력을 섬겼으면 +15. 이 세력이 대상의 옛 주군을 참수했으면 −20(그 주군과 인연이 있었으면 3% 이하).
#  - 다른 세력의 무장에게 권할 때는 위의 값에 0.6 을 곱해 더한다(참수의 원한은 그대로). 직접 인연이 있는 사람이 가면 '충성 95 이상이면 응하지 않는다'는 벽을 넘는다.
#  - 화면: 대상 줄에 출신(옛 ○○군 · 멸망)과 가장 잘 권할 무장의 사이, 보낼 무장을 고르는 표에 사이, 아래 미리보기에 더해진 까닭. 무장 창에 옛 세력.
#  - AI(와 군단): 재야·포로에게 매력이 가장 높은 무장을 보내던 것을 성공률이 가장 높은 무장으로.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- data.js
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var POACH_AI = {",
"""/* 등용과 옛 관계(v0.11): 보내는 무장과 대상의 사이(가장 큰 것 하나) — bond 직접 인연 · lord 옛 주군 · kin 같은 주군과 인연으로 묶인 사이 · vassal 옛 신하 · mate 옛 동료.
   home = 대상이 예전에 이 세력을 섬겼다 · fallen = 멸망한 세력 출신 · grudge = 이 세력이 옛 주군을 참수했다(그 주군과 인연이 있었으면 grudgeCap % 이하).
   poach = 다른 세력의 무장에게 권할 때 위의 값에 곱하는 몫 */
var TIES = { bond: 50, lord: 30, kin: 30, vassal: 20, mate: 12, home: 15, fallen: 10, grudge: -20, grudgeCap: 3, poach: 0.6 };
var POACH_AI = {""")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- core.js
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "capF: -1, dest: -1, eta: 0 };\n    if (o.f >= 0) {", "capF: -1, dest: -1, eta: 0, pf: so.f };\n    if (o.f >= 0) {")

s = rep(s, """function recruitChance(b, o, t) {
  var L = off(G.factions[b.owner].lord);
  if (t.st === 'active') {                                              // 다른 세력의 무장(v0.9)
    var mine = bondWith(t, b.owner);
    if (bondOf(t)) return 0;                                            //   제 주군과 인연이 있으면 응하지 않는다
    if (t.loy >= POACH.wall && !mine) return 0;                         //   충성이 아주 높아도 응하지 않는다
    var q = POACH.base + (o.cha - 50) * POACH.cha + (o.pol - 50) * POACH.pol + (L.cha - off(G.factions[t.f].lord).cha) * POACH.lord - (t.loy - POACH.loy0) * POACH.loyK;
    if (o.sk === '논객') q += POACH.talker;
    if (mine) q += POACH.bond;
    return clamp(Math.round(q), 0, POACH.max);
  }
  var p = 35 + (o.cha - 50) * 0.7 + (o.pol - 50) * 0.2;
  p += (L.cha - 70) * 0.4;
  if (o.sk === '논객') p += 20;
  if (bondWith(t, b.owner)) p += 30;                                    // 내 군주와 인연이 있는 사람
  if (t.st === 'captive') { p -= 15; if (t.f >= 0 && G.factions[t.f].alive) p -= (t.loy - 60) * 0.8; }
  p = clamp(Math.round(p), 3, 95);
  if (t.st === 'captive' && t.f >= 0 && G.factions[t.f].alive && bondOf(t)) p = Math.min(p, 5);   // 주군과 인연이 있는 포로는 주군의 세력이 살아 있는 한 거의 응하지 않는다
  return p;
}
""",
"""/* ---------- 옛 관계(v0.11) ----------
   o.pf = 마지막으로 섬긴 세력(지금 섬기고 있으면 그 세력, 섬긴 적이 없으면 -1), o.past = 그 앞에 섬겼던 세력들(없으면 필드가 없다).
   세력이 바뀌는 곳이 여럿이라(등용 · 장성 · 멸망 · 이탈 …) 그때마다 적지 않고 pastSweep() 이 훑어서 적는다 — 턴이 넘어갈 때와 등용 직후.
   세력의 군주(G.factions[f].lord)는 바뀌지 않으므로 '누가 누구의 옛 주군인가'는 이것만으로 알 수 있다. */
function homeF(o) { var so = SCENARIO.officers[o.id]; return (so && so.f >= 0) ? so.f : -1; }             // 시나리오가 시작될 때 섬기던 세력
function pastInit(o) {                                                  // 옛 저장(v0.10.1 까지)에는 없다: 시나리오의 세력에서 지금 세력으로 한 번 옮긴 것으로 본다
  var h = homeF(o);
  o.pf = o.f >= 0 ? o.f : h;
  if (h >= 0 && h !== o.pf) o.past = [h];
}
function pastNote(o) {
  if (o.pf === undefined) { pastInit(o); return; }
  if (o.f < 0 || o.f === o.pf) return;                                  // 재야 · 주인 잃은 포로: 마지막 세력을 그대로 둔다
  if (o.pf >= 0) { if (!o.past) o.past = []; var k = o.past.indexOf(o.pf); if (k >= 0) o.past.splice(k, 1); o.past.push(o.pf); }
  o.pf = o.f;
  if (o.past) { var k2 = o.past.indexOf(o.f); if (k2 >= 0) o.past.splice(k2, 1); }      // 예전에 섬기던 세력으로 돌아왔다: 옛 세력 목록에서는 뺀다
}
function pastSweep() { for (var i = 0; i < G.officers.length; i++) pastNote(G.officers[i]); }
function lastF(o) { return o.pf === undefined ? (o.f >= 0 ? o.f : homeF(o)) : o.pf; }
function servedF(o) {                                                   // 섬겼던 세력들 — 지금 섬기는 세력은 뺀다(재야 · 주인 잃은 포로라면 마지막 세력도 든다)
  var pf = lastF(o), out = o.past ? o.past.slice() : [], k;
  if (o.pf === undefined) { var h = homeF(o); if (h >= 0 && out.indexOf(h) < 0) out.push(h); }
  if (pf >= 0 && out.indexOf(pf) < 0) out.push(pf);
  if (o.f >= 0) { k = out.indexOf(o.f); if (k >= 0) out.splice(k, 1); }
  return out;
}
function fallenOf(t) { var lf = lastF(t); return t.f < 0 && lf >= 0 && !!G.factions[lf] && !G.factions[lf].alive && G.factions[lf].lord !== t.id; }   // 멸망한 세력 출신(그 군주 자신은 아니다)
function lordOfAny(o, fs) { for (var i = 0; i < fs.length; i++) if (G.factions[fs[i]] && G.factions[fs[i]].lord === o.id) return true; return false; }
function bondDirect(a, b) { var m = BONDS[a.n], n = BONDS[b.n]; return (m && m[b.n]) || (n && n[a.n]) || null; }
function bondShared(a, b) { for (var L in BONDS) if (BONDS[L][a.n] && BONDS[L][b.n]) return L; return null; }
/* 보내는 무장 o 와 대상 t 의 옛 사이(가장 큰 것 하나) → { k, v, label, short } 또는 null. f = 권하는 세력(o 가 지금 섬기는 세력)
   같은 주군과의 인연(kin)은 그 주군이 권하는 세력의 군주가 아닐 때만 센다 — 그때는 '우리 군주와 인연'으로 이미 세었다 */
function tieOf(o, t, f) {
  if (f === undefined) f = o.f;
  var FL = (f >= 0 && G.factions[f]) ? off(G.factions[f].lord) : null;
  var d = bondDirect(o, t); if (d) return { k: 'bond', v: TIES.bond, label: (FL && FL.id === o.id ? '군주가 직접 설득' : '보내는 무장과 ' + d), short: d };
  var st = servedF(t), so = servedF(o), i;
  if (lordOfAny(o, st)) return { k: 'lord', v: TIES.lord, label: '옛 주군의 설득', short: '옛 주군' };
  var sh = bondShared(o, t); if (sh && !(FL && FL.n === sh)) return { k: 'kin', v: TIES.kin, label: josa(sh, '과와') + ' 맺은 인연', short: '인연' };
  if (lordOfAny(t, so)) return { k: 'vassal', v: TIES.vassal, label: '옛 신하의 설득', short: '옛 신하' };
  for (i = 0; i < so.length; i++) if (st.indexOf(so[i]) >= 0) return { k: 'mate', v: TIES.mate, label: '옛 동료의 설득', short: '옛 동료' };
  return null;
}
/* 세력 f 가 t 의 주군(지금 · 예전)을 참수했는가 → { lord, bond } 또는 null */
function grudgeOf(f, t) {
  var fs = servedF(t); if (t.f >= 0) fs.push(t.f);
  for (var i = 0; i < fs.length; i++) { var F = G.factions[fs[i]], L = F ? off(F.lord) : null; if (L && L.id !== t.id && L.st === 'dead' && L.exBy === f) return { lord: L, bond: (BONDS[L.n] && BONDS[L.n][t.n]) || null }; }
  return null;
}
/* 등용 성공률과 그 까닭 { p, why: [[글, 값]…], tie, no: 응하지 않는 까닭 } — recruitChance 는 p 만 돌려준다 */
function recruitTerms(b, o, t) {
  var L = off(G.factions[b.owner].lord), why = [], tie = tieOf(o, t, b.owner), home = servedF(t).indexOf(b.owner) >= 0, gr = grudgeOf(b.owner, t), mine = bondWith(t, b.owner), k;
  if (t.st === 'active') {                                              // 다른 세력의 무장(v0.9)
    if (bondOf(t)) return { p: 0, why: why, tie: tie, no: '주군과 ' + bondOf(t) };                       //   제 주군과 인연이 있으면 응하지 않는다
    if (t.loy >= POACH.wall && !mine && !(tie && tie.k === 'bond')) return { p: 0, why: why, tie: tie, no: '충성 ' + POACH.wall + ' 이상' };   //   충성이 아주 높아도 응하지 않는다(인연이 있는 사람이 가면 다르다)
    var q = POACH.base + (o.cha - 50) * POACH.cha + (o.pol - 50) * POACH.pol + (L.cha - off(G.factions[t.f].lord).cha) * POACH.lord - (t.loy - POACH.loy0) * POACH.loyK;
    if (o.sk === '논객') { q += POACH.talker; why.push(['논객', POACH.talker]); }
    if (mine) { q += POACH.bond; why.push(['우리 군주와 ' + mine, POACH.bond]); }
    if (tie) { k = Math.round(tie.v * TIES.poach); q += k; why.push([tie.label, k]); }
    if (home) { k = Math.round(TIES.home * TIES.poach); q += k; why.push(['예전에 섬긴 세력', k]); }
    if (gr) { q += TIES.grudge; why.push([gr.lord.n + ' 참수의 원한', TIES.grudge]); }
    q = clamp(Math.round(q), 0, POACH.max);
    if (gr && gr.bond) q = Math.min(q, TIES.grudgeCap);
    return { p: q, why: why, tie: tie };
  }
  var p = 35 + (o.cha - 50) * 0.7 + (o.pol - 50) * 0.2;
  p += (L.cha - 70) * 0.4;
  if (o.sk === '논객') { p += 20; why.push(['논객', 20]); }
  if (mine) { p += 30; why.push(['우리 군주와 ' + mine, 30]); }           // 내 군주와 인연이 있는 사람
  var dead = fallenOf(t);
  if (t.st === 'captive') {
    if (dead) why.push(['멸망한 세력 출신', 15 + TIES.fallen]);            //   돌아갈 곳이 없다: 포로라서 깎이던 15 가 없고, 거기에 더한다
    else { p -= 15; if (t.f >= 0 && G.factions[t.f].alive) p -= (t.loy - 60) * 0.8; }
  } else if (dead) why.push(['멸망한 세력 출신', TIES.fallen]);
  if (dead) p += TIES.fallen;
  if (tie) { p += tie.v; why.push([tie.label, tie.v]); }
  if (home) { p += TIES.home; why.push(['예전에 섬긴 세력', TIES.home]); }
  if (gr) { p += TIES.grudge; why.push([gr.lord.n + ' 참수의 원한', TIES.grudge]); }
  p = clamp(Math.round(p), 3, 95);
  if (t.st === 'captive' && t.f >= 0 && G.factions[t.f].alive && bondOf(t)) p = Math.min(p, 5);   // 주군과 인연이 있는 포로는 주군의 세력이 살아 있는 한 거의 응하지 않는다
  if (gr && gr.bond) p = Math.min(p, TIES.grudgeCap);                    // 인연이 있던 주군을 벤 세력에는 거의 응하지 않는다
  return { p: p, why: why, tie: tie };
}
function recruitChance(b, o, t) { return recruitTerms(b, o, t).p; }
""")
s = rep(s, "t.loy = 70 + ri(0, 15); t.merit = Math.round(t.merit * 0.5); if (bondOf(t)) t.loy = 100;\n",
           "t.loy = 70 + ri(0, 15); t.merit = Math.round(t.merit * 0.5); if (bondOf(t)) t.loy = 100;\n    pastNote(t);                                                        // 섬겼던 세력을 적어 둔다(v0.11)\n")
s = rep(s, "t.st = 'dead'; t.f = -1; t.capF = -1; return { ok: true }; }", "t.st = 'dead'; t.f = -1; t.capF = -1; t.exBy = b.owner; return { ok: true }; }      // exBy: 누가 베었는가(v0.11 — 그 신하였던 무장들이 원한을 품는다)")
# 이웃 세력이 데려갈 위험: 충성의 벽은 recruitTerms 가 본다(직접 인연이 있는 사람이 오면 벽을 넘는다)
s = rep(s, "if (!o || o.st !== 'active' || o.unit !== null || o.f < 0 || isLord(o) || bondOf(o) || o.loy >= POACH.wall) return null;",
           "if (!o || o.st !== 'active' || o.unit !== null || o.f < 0 || isLord(o) || bondOf(o)) return null;")
# 턴이 넘어갈 때 훑는다
s = rep(s, "  // 날짜\n  G.turn++; G.xun++;\n", "  pastSweep();                                                        // 섬겼던 세력을 적어 둔다(v0.11)\n  // 날짜\n  G.turn++; G.xun++;\n")
# 불러올 때: 옛 저장에는 없다
s = rep(s, "  G = g; reindex(); REPORT = []; EVQ = []; JOT = null;\n  corpsFix();\n",
           "  G = g; reindex(); REPORT = []; EVQ = []; JOT = null;\n  corpsFix();\n  pastSweep();                                                           // v0.11: 섬겼던 세력(옛 저장에는 없다 — 시나리오의 세력으로 미루어 채운다)\n")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ai.js: 성공률이 가장 높은 무장을 보낸다
p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "        os.sort(function (a, c2) { return c2.cha - a.cha; });\n        var rr = cmdRecruit(b, os[0].id, cp.id);",
           "        os.sort(function (a, c2) { return recruitChance(b, c2, cp) - recruitChance(b, a, cp) || c2.cha - a.cha || a.id - c2.id; });      // v0.11: 옛 주군 · 옛 동료가 있으면 그 사람이 간다\n        var rr = cmdRecruit(b, os[0].id, cp.id);")
s = rep(s, "os.sort(function (a, c2) { return c2.cha - a.cha; }); cmdRecruit(b, os[0].id, fr[i].id); }",
           "var frT = fr[i]; os.sort(function (a, c2) { return recruitChance(b, c2, frT) - recruitChance(b, a, frT) || c2.cha - a.cha || a.id - c2.id; }); cmdRecruit(b, os[0].id, frT.id); }")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui_panels.js
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "/* 군사가 \"응할 것\"이라고 보는 이웃 무장(가장 잘하는 무장을 보냈을 때) */\n",
"""/* 옛 관계(v0.11)를 글로 */
function originTxt(t) {                                    // 어디 출신인가: 지금 섬기는 세력(포로) 또는 마지막으로 섬긴 세력
  var f = t.f >= 0 ? t.f : lastF(t); if (f < 0 || !G.factions[f]) return '';
  return (t.f >= 0 ? '' : '옛 ') + G.factions[f].name + '군' + (G.factions[f].alive ? '' : ' · 멸망');
}
function whyTxt(x) { return x.why.map(function (w) { return w[0] + ' <b' + (w[1] < 0 ? ' class="bad"' : '') + '>' + (w[1] >= 0 ? '+' : '−') + Math.abs(w[1]) + '</b>'; }).join(' · '); }
function servedTxt(o) { return servedF(o).map(function (f) { return G.factions[f].name + '군' + (G.factions[f].alive ? '' : '(멸망)'); }).join(' · '); }
/* 군사가 "응할 것"이라고 보는 이웃 무장(가장 잘하는 무장을 보냈을 때) */
""")
# 대상 줄: 출신과 가장 잘 권할 무장의 사이
s = rep(s, "  function bestP(t) { return bestRecruiter(b, t).p; }\n  function bestM(t) { return advMark(bestRecruiter(b, t).adv); }\n",
"""  function bestP(t) { return bestRecruiter(b, t).p; }
  function bestM(t) { return advMark(bestRecruiter(b, t).adv); }
  function tieSub(t, org) {                                    // 줄 오른쪽의 작은 글: 가장 잘 권할 무장과 대상의 사이(있으면), 없으면 출신
    var x = bestRecruiter(b, t), tie = x.o ? tieOf(x.o, t, b.owner) : null, og = org ? originTxt(t) : '';
    return tie ? '<br><small class="tie">' + x.o.n + ' · ' + tie.short + '</small>' : (og ? '<br><small>' + og + '</small>' : '');
  }
""")
s = rep(s, "rt: w ? '<span class=\"bad\">' + w + '</span>' : (idle ? bestM(t) + '최고 <b>' + bestP(t) + '%</b>' : '') }); }\n        h += '</div>';\n      }\n      if (far.length) {",
           "rt: (w ? '<span class=\"bad\">' + w + '</span>' : (idle ? bestM(t) + '최고 <b>' + bestP(t) + '%</b>' : '')) + (w || !idle ? (originTxt(t) ? '<br><small>' + originTxt(t) + '</small>' : '') : tieSub(t, true)) }); }\n        h += '</div>';\n      }\n      if (far.length) {")
s = rep(s, "(w ? '<span class=\"bad\">' + w + '</span>' : (idle ? (L[i].p ? bestM(t) : '') + '최고 <b>' + L[i].p + '%</b>' : '')) }); }",
           "(w ? '<span class=\"bad\">' + w + '</span>' : (idle ? (L[i].p ? bestM(t) : '') + '최고 <b>' + L[i].p + '%</b>' + (L[i].p ? tieSub(t, false) : '') : '')) }); }")
# 권할 수 없는 까닭: 벽을 넘는 사람이 있는지는 recruitTerms 가 안다
s = rep(s, "    if (t.st === 'active' && t.loy >= POACH.wall && !bondWith(t, b.owner)) return '충성 ' + POACH.wall + ' 이상';\n",
           "    if (t.st === 'active' && t.loy >= POACH.wall && !bondWith(t, b.owner) && !idleOfficers(b).some(function (o) { var ti = tieOf(o, t, b.owner); return ti && ti.k === 'bond'; })) return '충성 ' + POACH.wall + ' 이상';\n")
# 보낼 무장을 고르는 표: 사이를 적고, 아래에 더해진 까닭
s = rep(s, "        rt: function (o) { return advMark(recruitAdvice(b, o, t)) + '<b>' + recruitChance(b, o, t) + '%</b>'; }, rtHead: '성공률',",
           "        rt: function (o) { var x = recruitTerms(b, o, t); return advMark(recruitAdvice(b, o, t)) + '<b>' + x.p + '%</b>' + (x.tie ? '<small class=\"tie\">' + x.tie.short + '</small>' : ''); }, rtHead: '성공률',")
s = rep(s, "        preview: function (os) { return '성공률 <b>' + recruitChance(b, os[0], t) + '%</b>' + (farT ? ' · 충성 ' + t.loy : ''); },",
           "        preview: function (os) { var x = recruitTerms(b, os[0], t); return '성공률 <b>' + x.p + '%</b>' + (farT ? ' · 충성 ' + t.loy : '') + (x.no ? ' · <span class=\"bad\">' + x.no + '</span>' : '') + (x.why.length ? '<br><small>' + whyTxt(x) + '</small>' : ''); },")
# 포로 창: 출신과 적성, 참수의 뒷일
s = rep(s, "h = dlgHead('포로 ' + cs.length + '명') + '<div class=\"dlg-b\"><p class=\"note\">등용은 인재 → 등용에서</p>';",
           "h = dlgHead('포로 ' + cs.length + '명') + '<div class=\"dlg-b\"><p class=\"note\">등용은 인재 → 등용에서 · <b>옛 군주를 참수하면</b> 그 신하였던 무장들이 우리의 등용에 잘 응하지 않습니다(' + TIES.grudge + ', 인연이 있던 무장은 거의 불가)</p>';")
s = rep(s, "h += '<div class=\"row\">' + porTag(cs[i]) + '<span class=\"mid\"><span class=\"nm\">' + cs[i].n + skTag(cs[i])", "h += '<div class=\"row cpv\">' + porTag(cs[i]) + '<span class=\"mid\"><span class=\"nm\">' + cs[i].n + skTag(cs[i])")
s = rep(s, "'<span class=\"mid\"><span class=\"nm\">' + cs[i].n + skTag(cs[i]) + '</span><span class=\"ds\">' + st5(cs[i]) + '</span></span><button class=\"btn\" type=\"button\" data-a=\"rel\"",
           "'<span class=\"mid\"><span class=\"nm\">' + cs[i].n + skTag(cs[i]) + (originTxt(cs[i]) ? ' <small class=\"org\">' + originTxt(cs[i]) + '</small>' : '') + '</span><span class=\"ds\">' + st5(cs[i]) + '</span>' + apt5(cs[i]) + '</span><button class=\"btn\" type=\"button\" data-a=\"rel\"")
io.open(p, 'w', encoding='utf-8').write(s)

# 무장 창: 옛 세력
s = io.open(p, encoding='utf-8').read()
s = rep(s, "'</b></div><div><span>공적</span><b>' + fmt(o.merit) + '</b></div>' : '') + '</div></div>' +\n",
           "'</b></div><div><span>공적</span><b>' + fmt(o.merit) + '</b></div>' : '') + '</div>' + (servedF(o).length ? '<p class=\"note\">섬겼던 세력 — ' + servedTxt(o) + '</p>' : '') + '</div>' +\n")
# 도움말
s = rep(s, "  '<h3>인재</h3><p>탐색으로 재야의 인재를 찾아 등용합니다. 사로잡은 적장도 등용할 수 있습니다. 해가 바뀌면 새 인물이 세상에 나옵니다.</p>' +\n",
           "  '<h3>인재</h3><p>탐색으로 재야의 인재를 찾아 등용합니다. 사로잡은 적장도 등용할 수 있습니다. 해가 바뀌면 새 인물이 세상에 나옵니다.</p>' +\n"
           "  '<p><b>옛 관계</b> — 등용은 누구를 보내느냐에 따라 달라집니다. 보내는 무장이 대상과 <b>직접 인연</b>(의형제·혈연·부부·인척·심복)이면 +' + TIES.bond + ', 대상의 <b>옛 주군</b>이면 +' + TIES.lord + ', 같은 주군과 인연으로 묶인 사이면 +' + TIES.kin + ', 옛 신하면 +' + TIES.vassal + ', <b>옛 동료</b>(같은 세력에 있던 적이 있다)면 +' + TIES.mate + '입니다(가장 큰 것 하나). 대상이 예전에 우리 세력을 섬겼다면 +' + TIES.home + '.</p>' +\n"
           "  '<p><b>멸망한 세력 출신</b>은 돌아갈 곳이 없어 더 잘 응합니다 — 포로는 전보다 +' + (15 + TIES.fallen) + '(포로라서 깎이던 15가 없어지고 +' + TIES.fallen + '), 재야는 +' + TIES.fallen + '. 그 세력의 군주였던 사람은 그대로입니다. 반대로 <b>옛 군주를 참수하면</b> 그 신하였던 무장들은 우리에게 ' + TIES.grudge + ', 그 군주와 인연이 있던 무장은 ' + TIES.grudgeCap + '% 아래입니다. 등용 창의 대상 줄에 출신과 가장 잘 권할 무장이, 무장을 고르는 표에 그 사이가, 아래에 더해진 까닭이 적혀 있습니다.</p>' +\n")
s = rep(s, "제 주군과 인연이 있거나 충성이 ' + POACH.wall + ' 이상이면 응하지 않고, 군주와 출진 중인 무장에게는 권할 수 없습니다.",
           "제 주군과 인연이 있거나 충성이 ' + POACH.wall + ' 이상이면 응하지 않고(대상과 직접 인연이 있는 무장을 보내면 충성이 높아도 권할 수 있습니다), 군주와 출진 중인 무장에게는 권할 수 없습니다.")
s = rep(s, "성공률은 보내는 무장의 매력·정치, 두 군주의 매력 차이, 그리고 <b>대상의 충성</b>으로 정해집니다.",
           "성공률은 보내는 무장의 매력·정치, 두 군주의 매력 차이, 그리고 <b>대상의 충성</b>으로 정해집니다(옛 관계는 ' + Math.round(TIES.poach * 100) + '%만 셉니다).")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- style.css
p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """/* 등용: 옛 관계 */
.row .rt small { font-size: 11px; color: var(--dim); }
.row .rt small.tie, .c-x small.tie { color: var(--seal); font-weight: 700; }
.c-x small.tie { display: block; font-size: 10.5px; line-height: 1.15; }
.row .nm small.org { font: 500 11px var(--font-body); color: var(--dim); margin-left: 4px; }
.row.cpv { gap: 7px; }
.row.cpv .btn { flex: none; padding: 0 10px; }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('p2 ok')
