# v0.11 (1/…): 작은 것 다섯  (data.js · ui_panels.js · index.html · style.css)
#  요청 ① "시장 등 레벨업 된 시설은 그 시설 레벨에 따른 생산량을 먼저 표시해야지. 180으로 되어있고 뒤에 lv 에 따른 걸 써놓으니 헷갈린다."
#        - 지은 시설의 줄과 시설 창은 '지금 레벨의 값'을 먼저 적는다(금 +440/월 · 최고 레벨). 새로 지을 때의 카드(FAC.desc)는 Lv1 기준 그대로.
#        - 시설 창에는 이 시설이 '지금 실제로' 보태는 수입(옆 조폐·곡창, 치안, 특기가 든 값)과 그 까닭을 한 줄 더.
#          병영·대장간·마구간은 도시에서 가장 높은 한 곳만 센다는 것, 조폐·곡창·공방은 레벨이 영향이 없다는 것도 적는다.
#        - 고침: 흡수합병 미리보기의 금액이 '150 × 레벨'로 적혀 있었다(실제 드는 금은 100 × 레벨 = COST.merge). 미리보기에 합친 뒤의 수입 변화도 적는다.
#  요청 ② "무장을 볼 때 적성을 볼 수 있으면 좋겠다."
#        - 무장 줄(목록 · 거점 · 부대 · 출진 · 등용)마다 능력치 아래에 적성 한 줄(창 극 노 기 병기). 무장 창의 적성 칸에는 제목과 풀이.
#  요청 ③ "치안이 낮으면 무슨 효과지?"
#        - 거점 창의 치안 칸에 지금의 수입 몫(%)을 적고, 누르면 풀이 창. 순찰 미리보기에도 수입 몫의 변화.
#  요청 ④ "전투 시 좀 더 긴 기간의 병량을 들고 갈 수 있으면 좋겠다. 너무 짧아"
#        - 출진 군량: 60·120·180·240일분 → 90·180·270·360일분(처음 값 120 → 180일분). 병력을 바꾸면 칸의 수량도 바로 바뀌고, 도시 병량이 모자라면 실리는 날수를 적는다.
#  요청 ⑤ "게임을 공유하는 버튼이 있으면 좋겠다."
#        - 제목 화면과 메뉴에 [공유]: 휴대폰의 공유 창 → 안 되면 주소·QR이 적힌 창(주소 복사).
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- data.js
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var GAME_VERSION = 'v0.10.1';", "var GAME_VERSION = 'v0.11';")
s = rep(s, "var SAVE_SLOTS = 6;",
           "var SHARE_URL = 'https://aaronkyung-a11y.github.io/chunhado/';      // 공유(v0.11)로 보내는 주소 — 누구나 열 수 있는 곳\n"
           "/* SHARE_URL 의 QR(33×33, 줄마다 16진수 · 왼쪽이 높은 자리). 주소를 바꾸면 다시 만들어야 한다(segno 로 만들고 OpenCV 로 읽어 확인) */\n"
           "var SHARE_QR = ['1fdd8aa7f', '104419d41', '17476ce5d', '17489065d', '1752c425d', '105194141', '1fd55557f', 'd60d00', 'fe189731', '14199266d', '1162454d6', '23bf0a5f', '19d4e47ba', '91f38263', '144c618fe', '991dbfec', 'c5a2e5b9', '16282b66d', '463f9976', '69cc5bbd', '1dc96a5bb', '121beea4d', '13f1ddc06', '1389dfe8f', '10c4667f1', '1b8ab15', '1fda59b54', '1058c7f1e', '1754005f9', '175eb7391', '175044564', '1055d98dc', '1fc6c05ea'];\n"
           "var SAVE_SLOTS = 6;")
s = rep(s, "var COST = {", "var DEPLOY_FOOD = [9, 18, 27, 36];      // 출진할 때 고르는 군량(턴 수): 90 · 180 · 270 · 360일분(v0.11 — 전에는 60~240일분)\nvar COST = {")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui_panels.js
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()

# ===== ① 시설: 지금 레벨의 값을 먼저 =====
s = rep(s, "/* 카드 한 줄: 이 자리에 이 시설을 지으면 [글, 빛깔('' · ok · no · warn)] */\n",
"""/* ---------- 시설의 풀이(v0.11): 지금 레벨의 값을 먼저 적는다. FAC[t].desc 는 새로 지을 때(Lv1) 보는 카드용 ---------- */
function lvTail(lv, f) { return lv >= 3 ? ' · 최고 레벨' : ' · Lv' + (lv + 1) + ' ' + f(lv + 1); }
function mulTxt(n) { return '×' + LV_MUL[n].toFixed(1); }
function facDesc(fc) {
  var lv = fc.lv || 1, t = fc.t;
  if (t === 'market') return '금 +' + fmt(MARKET_INC[lv]) + '/월' + lvTail(lv, function (n) { return '+' + fmt(MARKET_INC[n]); });
  if (t === 'farm') return '병량 +' + fmt(FARM_INC[lv]) + '/분기' + lvTail(lv, function (n) { return '+' + fmt(FARM_INC[n]); });
  if (t === 'barracks') return (lv > 1 ? '징병량 ' + mulTxt(lv) : '징병 가능') + lvTail(lv, function (n) { return (lv > 1 ? '' : '징병량 ') + mulTxt(n); });
  if (t === 'smithy') return (lv > 1 ? '창·극·노 생산량 ' + mulTxt(lv) : '창·극·노 생산') + lvTail(lv, function (n) { return (lv > 1 ? '' : '생산량 ') + mulTxt(n); });
  if (t === 'stable') return (lv > 1 ? '군마 생산량 ' + mulTxt(lv) : '군마 생산') + lvTail(lv, function (n) { return (lv > 1 ? '' : '생산량 ') + mulTxt(n); });
  if (t === 'workshop') return '충차 생산 · 레벨은 영향 없음';
  if (t === 'mint') return '옆 시장의 수입 +50% · 레벨은 영향 없음';
  if (t === 'granary') return '옆 농장의 수입 +50% · 레벨은 영향 없음';
  return FAC[t].desc;
}
/* 이 시설이 실제로 보태는 수입 = 이 시설만 뺀 수입 셈과의 차이(옆의 조폐·곡창, 치안, 특기가 다 들어 있다). 짓는 중이면 다 지어졌다고 치고 센다 */
function facYield(b, pi) {
  var p = b.plots[pi], fc = p.fac, was = fc.done;
  fc.done = true; var g1 = goldIncome(b), f1 = foodIncome(b);
  p.fac = null; var g0 = goldIncome(b), f0 = foodIncome(b);
  p.fac = fc; fc.done = was;
  return { gold: g1 - g0, food: f1 - f0 };
}
/* 시설 창의 둘째 줄: 지금 이 자리에서 실제로 얼마를 보태는가, 왜 그 값인가 */
function facNow(b, pi) {
  var fc = b.plots[pi].fac, t = fc.t, lv = fc.lv, y = facYield(b, pi), pre = fc.done ? '지금 ' : '다 지으면 ', op = incPct(b.order), why = [], n, i;
  if (t === 'market' || t === 'farm') {
    var sup = t === 'market' ? 'mint' : 'granary', skl = t === 'market' ? '부호' : '미도';
    n = Math.min(2, adjFacCount(b, pi, sup));
    if (n) why.push('옆 ' + FAC[sup].name + ' ' + n + '곳 +' + n * 50 + '%');
    if (op < 100) why.push('치안 ' + b.order + ' → ' + op + '%');
    if (baseHasSkill(b, skl)) why.push(skl + ' +20%');
    return pre + (t === 'market' ? '금 <b>+' + fmt(y.gold) + '</b>/월' : '병량 <b>+' + fmt(y.food) + '</b>/분기') + (why.length ? ' <small>(' + why.join(' · ') + ')</small>' : '');
  }
  if (t === 'mint' || t === 'granary') {
    var v = t === 'mint' ? y.gold : y.food, pair = t === 'mint' ? '시장' : '농장';
    n = adjFacCount(b, pi, t === 'mint' ? 'market' : 'farm');
    if (!n) return '<span class="bad">옆에 다 지은 ' + pair + '이 없어 ' + (fc.done ? '지금은' : '다 지어도') + ' 보탬이 없습니다</span>';
    if (v <= 0) return '<span class="bad">옆 ' + pair + '에 이미 ' + FAC[t].name + ' 둘이 붙어 있어 보탬이 없습니다</span> <small>(한 곳에 둘까지)</small>';
    return pre + (t === 'mint' ? '금 <b>+' + fmt(v) + '</b>/월' : '병량 <b>+' + fmt(v) + '</b>/분기') + ' <small>(옆 ' + pair + ' ' + n + '곳)</small>';
  }
  if (t === 'barracks' || t === 'smithy' || t === 'stable') {
    var best = 0, what = t === 'barracks' ? '징병량' : '생산량';
    for (i = 0; i < b.plots.length; i++) { var g = b.plots[i].fac; if (i !== pi && g && g.done && g.t === t && g.lv > best) best = g.lv; }
    if (best > lv) return '<span class="bad">이 도시에 Lv' + best + ' ' + FAC[t].name + '이 있어 이곳은 보탬이 없습니다</span> <small>(가장 높은 한 곳만 셉니다)</small>';
    if (best === lv) return '같은 레벨의 ' + FAC[t].name + '이 또 있습니다 — <b>한 곳만</b> 셉니다';
    return (fc.done ? '이 도시의 ' : '다 지으면 이 도시의 ') + what + ' <b>' + mulTxt(lv) + '</b> <small>(가장 높은 한 곳만 셉니다)</small>';
  }
  return '';
}
/* 흡수합병을 하면 달라지는 수입(금/월, 병량/분기) — 한 곳이 레벨 +1, 합쳐진 곳은 빈 부지가 된다 */
function mergeGain(b, pi, pj) {
  var f = b.plots[pi].fac, g = b.plots[pj].fac, g0 = goldIncome(b), f0 = foodIncome(b);
  f.lv++; b.plots[pj].fac = null;
  var g1 = goldIncome(b), f1 = foodIncome(b);
  f.lv--; b.plots[pj].fac = g;
  return { gold: g1 - g0, food: f1 - f0 };
}
function mergeNote(b, pi, pj) {
  var fc = b.plots[pi].fac, t = fc.t, mg = mergeGain(b, pi, pj), free = lotMark(lotNo(b, pj)) + ' 부지가 빕니다';
  function sg(v) { return (v >= 0 ? '+' : '−') + fmt(Math.abs(v)); }
  if (t === 'market' || t === 'mint') return '금 수입 <b' + (mg.gold < 0 ? ' class="bad"' : '') + '>' + sg(mg.gold) + '</b>/월 · ' + free;
  if (t === 'farm' || t === 'granary') return '병량 수입 <b' + (mg.food < 0 ? ' class="bad"' : '') + '>' + sg(mg.food) + '</b>/분기 · ' + free;
  if (t === 'workshop') return '충차 생산은 그대로 · ' + free;
  var cur = bestFacLv(b, t), nx = Math.max(cur, fc.lv + 1);
  return (t === 'barracks' ? '징병량 ' : '생산량 ') + mulTxt(cur) + ' → <b>' + mulTxt(nx) + '</b> · ' + free;
}
/* 카드 한 줄: 이 자리에 이 시설을 지으면 [글, 빛깔('' · ok · no · warn)] */
""")
s = rep(s, "(fc.done ? FAC[fc.t].desc : '건설 중 — ' + days(Math.max(1, Math.ceil((fc.need - fc.prog) / fc.rate))) + ' 남음') + '</span></span>' + (mergeCandidates(b, i).length",
           "(fc.done ? facDesc(fc) : '건설 중 — ' + days(Math.max(1, Math.ceil((fc.need - fc.prog) / fc.rate))) + ' 남음') + '</span></span>' + (mergeCandidates(b, i).length")
s = rep(s, "'<div class=\"dlg-b\"><div class=\"card\">' + facThumb(fc, 'lg') + '<p>' + F.desc + '</p></div>' + (fc.done ? '' : '<p class=\"note\">건설 중 — '",
           "'<div class=\"dlg-b\"><div class=\"card fcd\">' + facThumb(fc, 'lg') + '<p><b class=\"fcv\">' + facDesc(fc) + '</b>' + (now ? '<span class=\"fcn\">' + now + '</span>' : '') + '</p></div>' + (fc.done ? '' : '<p class=\"note\">건설 중 — '")
s = rep(s, "      var cands = mergeCandidates(b, pi);\n      var h = dlgHead(b.n + ' ' + lotMark(lotNo(b, pi)) + ' ' + F.name + ' Lv' + fc.lv)",
           "      var cands = mergeCandidates(b, pi), now = facNow(b, pi);\n      var h = dlgHead(b.n + ' ' + lotMark(lotNo(b, pi)) + ' ' + F.name + ' Lv' + fc.lv)")
s = rep(s, "'<p class=\"note\">흡수합병 = 옆의 같은 시설을 합쳐 레벨 +1 (최대 3)</p></div>';",
           "'<p class=\"note\">흡수합병 = 옆의 같은 시설을 합쳐 레벨 +1 (최대 3)' + (cands.length ? ' — ' + mergeNote(b, pi, cands[0]) : '') + ({ mint: 1, granary: 1, workshop: 1 }[fc.t] ? '<br><b class=\"bad\">' + josa(F.name, '은는') + ' 레벨을 올려도 효과가 같습니다</b> — 합치면 한 곳이 줄 뿐입니다' : '') + '</p></div>';")
s = rep(s, "preview: function () { return F.name + ' Lv' + fc.lv + ' → <b>Lv' + (fc.lv + 1) + '</b> · 금 ' + 150 * fc.lv; } },",
           "preview: function () { return F.name + ' Lv' + fc.lv + ' → <b>Lv' + (fc.lv + 1) + '</b> · 금 ' + COST.merge * fc.lv + '<br><small>' + mergeNote(b, pi, cands[0]) + '</small>'; } },")

# ===== ② 무장 줄의 적성 =====
s = rep(s, "function skTag(o) { return o.sk ? '<em>' + o.sk + '</em>' : ''; }\n",
"""function skTag(o) { return o.sk ? '<em>' + o.sk + '</em>' : ''; }
/* 적성 한 줄(v0.11): 창 극 노 기 병기 — S 붉은빛 · A 황토빛 · C 흐리게. on = 지금 고른 병과(출진 창)의 칸에 밑줄 */
function apt5(o, on) {
  var ks = ['창', '극', '노', '기', '병기'], s = '<span class="ds ap5">';
  for (var i = 0; i < 5; i++) { var a = o.apt.charAt(i); s += '<span' + (on === i ? ' class="on"' : '') + '><i>' + ks[i] + '</i><b class="' + a + '">' + a + '</b></span>'; }
  return s + '</span>';
}
""")
s = rep(s, "'</span><span class=\"ds\">' + (opt.ds !== undefined ? opt.ds : st5(o, opt.hi)) + '</span></span>' +",
           "'</span><span class=\"ds\">' + (opt.ds !== undefined ? opt.ds : st5(o, opt.hi)) + '</span>' + (opt.noapt ? '' : apt5(o, opt.apt)) + '</span>' +")
s = rep(s, "h += offRow(o, { a: 'pick', sel: si >= 0, badge: si === 0 ? '주장' : (si > 0 ? '부장' : ''), rt:",
           "h += offRow(o, { a: 'pick', sel: si >= 0, apt: ai, badge: si === 0 ? '주장' : (si > 0 ? '부장' : ''), rt:")
s = rep(s, "        '<div class=\"apt\">' + a + '</div>' +\n",
           "        '<div class=\"sec\">병종 적성</div><div class=\"apt\">' + a + '</div>' +\n"
           "        '<p class=\"note aptn\">부대의 공격·방어에 곱해집니다 — C ×' + APT_MUL.C + ' · B ×' + APT_MUL.B + ' · A ×' + APT_MUL.A + ' · S ×' + APT_MUL.S + ' (주장·부장 가운데 가장 높은 적성). 전법은 C 하나 · B 둘 · A부터 셋을 쓰고, 높을수록 잘 통합니다.</p>' +\n")

# ===== ③ 치안: 칸에 수입 몫, 누르면 풀이 =====
s = rep(s, "function done(res, msg, snd, who, key, x) {\n",
"""/* 치안의 효과(v0.11) — 셈은 core.js 의 goldIncome · foodIncome · draftAmount 와 같다 */
function incPct(order) { return Math.round(50 + order / 2); }            // 금·병량 수입에 곱해지는 몫(%)
function draftPct(order) { return Math.round(40 + order * 0.6); }         // 징병량에 곱해지는 몫(%)
function showOrderInfo(b) {
  showDialog({
    render: function () {
      var o = b.order;
      return dlgHead(b.n + ' 치안 ' + o) + '<div class="dlg-b"><div class="stats ordst"><div><span>' + ico('gold') + '금·병량 수입</span><b' + (o < 50 ? ' class="bad"' : '') + '>' + incPct(o) + '%</b></div><div><span>' + ico('troops') + '징병량</span><b' + (o < 50 ? ' class="bad"' : '') + '>' + (o < 20 ? '징병 불가' : draftPct(o) + '%') + '</b></div></div>' +
        '<div class="help"><ul><li>수입은 치안 100일 때 100%, 0일 때 50%입니다. 징병량은 100일 때 100%, 0일 때 40%이고 <b>치안이 20 아래면 징병할 수 없습니다</b>.</li>' +
        '<li><b>내려갈 때</b> — 징병할 때마다 −10(인덕 −5) · 50을 넘으면 매월 −1 · 도시의 병량이 바닥나면 턴마다 −3 · 성이 함락되면 −25</li>' +
        '<li><b>올릴 때</b> — <b>순찰</b>(금 ' + COST.patrol + '). 무력이나 통솔이 높은 무장일수록, 여럿이 할수록 많이 오릅니다(위압은 두 배).</li>' +
        '<li>가만히 두면 50으로 내려가 수입이 75%에 머뭅니다. 치안이 낮다고 민란이 나거나 무장이 떠나지는 않습니다.</li></ul></div></div>';
    }, on: {}
  }, true);
}
function done(res, msg, snd, who, key, x) {
""")
s = rep(s, "(city ? '<div><span>' + ico('order') + '치안</span><b' + (b.order < 50 ? ' class=\"bad\"' : '') + '>' + b.order + '</b></div>' : '')",
           "(city ? '<div class=\"tap\" data-a=\"order\"><span>' + ico('order') + '치안</span><b' + (b.order < 50 ? ' class=\"bad\"' : '') + '>' + b.order + (b.owner >= 0 ? '<small>수입 ' + incPct(b.order) + '% ›</small>' : '') + '</b></div>' : '')")
s = rep(s, "    cnew: function () { showCorpsNew(B().id); }\n  };\n  function cmd(a, name, sub, pri, offc)",
           "    cnew: function () { showCorpsNew(B().id); },\n    order: function () { showOrderInfo(B()); }\n  };\n  function cmd(a, name, sub, pri, offc)")
s = rep(s, "return '치안 <b>+' + Math.min(v, 100 - b.order) + '</b> · 금 ' + COST.patrol; } },",
           "v = Math.min(v, 100 - b.order); return '치안 <b>+' + v + '</b> · 금 ' + COST.patrol + '<br><small>수입 ' + incPct(b.order) + '% → ' + incPct(b.order + v) + '%</small>'; } },")

# ===== ④ 출진 군량 =====
s = rep(s, "var st = { type: 'sword', ids: [], troops: 0, turns: 12, auto: true };",
           "var st = { type: 'sword', ids: [], troops: 0, turns: DEPLOY_FOOD[1], auto: true };")
s = rep(s, "  function food() { return Math.min(b.food, Math.ceil(st.troops / 20) * st.turns); }\n",
           "  function food() { return Math.min(b.food, Math.ceil(st.troops / 20) * st.turns); }\n"
           "  function foodNote() {                                        // 도시 병량이 모자라면 실제로 실리는 날수를 적는다\n"
           "    var per = Math.max(1, Math.ceil(st.troops / 20)), need = per * st.turns;\n"
           "    return '도시 병량 ' + fmt(b.food) + (need > b.food ? ' · <b class=\"bad\">모자랍니다 — ' + days(Math.floor(b.food / per)) + '분만 실립니다</b>' : ' · 이웃 거점까지 20~50일');\n"
           "  }\n")
s = rep(s, "        [6, 12, 18, 24].forEach(function (n) {", "        DEPLOY_FOOD.forEach(function (n) {")
s = rep(s, "        h += '</div><p class=\"note\">도시 병량 ' + fmt(b.food) + ' · 이웃 거점까지 20~50일</p>';\n      }\n      return h + '</div><div class=\"dlg-f\"><div class=\"pv\" id=\"dpP\">'",
           "        h += '</div><p class=\"note\" id=\"dpN\">' + foodNote() + '</p>';\n      }\n      return h + '</div><div class=\"dlg-f\"><div class=\"pv\" id=\"dpP\">'")
s = rep(s, "      troops: function (el) { st.troops = +el.value; st.auto = false; $('dpV').textContent = fmt(st.troops); $('dpP').innerHTML = pv(); },\n      ok: function () {\n        var r = cmdDeploy(",
           "      troops: function (el) {\n"
           "        st.troops = +el.value; st.auto = false; $('dpV').textContent = fmt(st.troops); $('dpP').innerHTML = pv();\n"
           "        var bs = document.querySelectorAll('#modal [data-a=\"turns\"]');                 // 군량 칸의 수량과 모자람 표시도 바로 고친다\n"
           "        for (var k = 0; k < bs.length; k++) bs[k].querySelector('small').textContent = fmt(Math.ceil(st.troops / 20) * +bs[k].getAttribute('data-v'));\n"
           "        if ($('dpN')) $('dpN').innerHTML = foodNote();\n"
           "      },\n      ok: function () {\n        var r = cmdDeploy(")

# ===== ⑤ 공유 =====
s = rep(s, "function showMenu() {\n",
"""/* ---------- 공유(v0.11) ----------
   보내는 주소: 앱(깃허브 페이지 등 manifest 가 있는 빌드)으로 열려 있으면 지금 그 주소, Claude 아티팩트 안처럼 남이 열 수 없는 곳이면 SHARE_URL.
   휴대폰의 공유 창(navigator.share)을 먼저 쓰고, 없거나 막혀 있으면 주소·QR이 적힌 창을 연다. */
function shareUrl() {
  try { if (document.querySelector('link[rel="manifest"]') && /^https?:$/.test(location.protocol) && !/^(localhost|127\\.|\\[::1\\])/.test(location.host)) return location.origin + location.pathname.replace(/index\\.html$/, ''); } catch (e) { /* */ }
  return SHARE_URL;
}
function qrSvg(rows) {
  var n = rows.length, q = 3, d = '';
  for (var y = 0; y < n; y++) { var v = parseInt(rows[y], 16); for (var x = 0; x < n; x++) if (Math.floor(v / Math.pow(2, n - 1 - x)) % 2) d += 'M' + (x + q) + ' ' + (y + q) + 'h1v1h-1z'; }
  return '<svg class="qr" viewBox="0 0 ' + (n + 2 * q) + ' ' + (n + 2 * q) + '" shape-rendering="crispEdges" role="img" aria-label="주소 QR"><rect width="100%" height="100%" fill="#fff"/><path d="' + d + '" fill="#111"/></svg>';
}
function copyText(txt, el) {                               // 복사: 새 방식 → 옛 방식(입력 칸을 골라 execCommand) → 안 되면 false
  var ok = false;
  try { if (el) { el.focus(); el.select(); el.setSelectionRange(0, txt.length); ok = document.execCommand('copy'); } } catch (e) { ok = false; }
  if (!ok) { try { if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(txt).then(function () { toast('주소를 복사했습니다'); }, function () { toast('복사가 막혀 있습니다 — 주소를 길게 눌러 복사하세요', 3200); }); return true; } } catch (e2) { /* */ } }
  return ok;
}
function showShare() {
  var url = shareUrl();
  showDialog({
    render: function () {
      return dlgHead('공유') + '<div class="dlg-b shr"><p>이 주소를 보내면 누구나 바로 할 수 있습니다 — 설치 없이 브라우저에서 열리고, 휴대폰이면 앱으로 설치할 수도 있습니다.</p>' +
        '<input class="shurl" id="shU" type="text" readonly value="' + url + '">' +
        '<div class="cmds ' + (navigator.share ? 'c2' : 'c1') + '"><button class="cmd pri" type="button" data-a="copy"><b>주소 복사</b></button>' + (navigator.share ? '<button class="cmd" type="button" data-a="send"><b>보내기</b><small>앱 고르기</small></button>' : '') + '</div>' +
        (url === SHARE_URL ? '<div class="qrw">' + qrSvg(SHARE_QR) + '<small>옆 사람은 카메라로 QR을 비추면 됩니다</small></div>' : '') +
        '<p class="note">저장한 판은 함께 가지 않습니다 — 받는 사람은 새 게임으로 시작합니다.</p></div>';
    },
    on: {
      copy: function () { if (copyText(url, $('shU'))) toast('주소를 복사했습니다'); else toast('복사가 막혀 있습니다 — 주소를 길게 눌러 복사하세요', 3200); },
      send: function () { shareSend(url, true); }
    }
  }, true);
}
function shareSend(url, quiet) {
  try {
    navigator.share({ title: '삼국지 천하도', text: '삼국지 천하도 — 수묵 지도 위의 삼국지 전략 게임', url: url }).then(function () { /* 보냈다 */ }, function (e) {
      if (e && e.name === 'AbortError') return;                    // 사용자가 공유 창을 닫았다
      if (quiet) toast('이 화면에서는 공유 창을 열 수 없습니다 — 주소를 복사해 보내세요', 3200); else showShare();
    });
    return true;
  } catch (e) { return false; }
}
function shareGame() {
  var url = shareUrl();
  if (!(navigator.share && shareSend(url, false))) showShare();
}
function showMenu() {
""")
s = rep(s, "<button class=\"cmd\" type=\"button\" data-a=\"help\"><b>도움말</b></button>' +\n",
           "<button class=\"cmd\" type=\"button\" data-a=\"help\"><b>도움말</b></button><button class=\"cmd\" type=\"button\" data-a=\"share\"><b>공유</b></button>' +\n")
s = rep(s, "      help: function () { showHelp(); },\n      title: function () { saveGame(); closeDialog();",
           "      help: function () { showHelp(); },\n      share: function () { shareGame(); },\n      title: function () { saveGame(); closeDialog();")
s = rep(s, "  $('tHelp').addEventListener('click', function () { audioInit(); playBgm('title'); showHelp(); });\n",
           "  $('tHelp').addEventListener('click', function () { audioInit(); playBgm('title'); showHelp(); });\n"
           "  $('tShare').addEventListener('click', function () { audioInit(); sfx('ui'); shareGame(); });\n")

# ===== 도움말 =====
s = rep(s, "같은 시설이 붙어 있으면 흡수합병으로 레벨을 올립니다(최대 3). 조폐는 옆의 시장, 곡창은 옆의 농장 수입을 50% 늘립니다. 금은 매월 초, 병량은 1·4·7·10월 초에 들어옵니다.</p>' +\n",
           "같은 시설이 붙어 있으면 흡수합병으로 레벨을 올립니다(최대 3). 조폐는 옆의 시장, 곡창은 옆의 농장 수입을 50% 늘립니다(한 곳에 둘까지). 금은 매월 초, 병량은 1·4·7·10월 초에 들어옵니다.</p>' +\n"
           "  '<p><b>시설의 레벨</b> — 지은 시설의 줄에는 <b>지금 레벨의 값</b>이 먼저 적혀 있습니다(시장 ' + MARKET_INC[1] + ' · ' + MARKET_INC[2] + ' · ' + MARKET_INC[3] + ', 농장 ' + fmt(FARM_INC[1]) + ' · ' + fmt(FARM_INC[2]) + ' · ' + fmt(FARM_INC[3]) + '). 시설을 누르면 옆 시설과 치안까지 넣은 <b>실제 수입</b>이 나옵니다. 병영·대장간·마구간은 레벨마다 징병량·생산량이 ×' + LV_MUL[1].toFixed(1) + ' · ×' + LV_MUL[2].toFixed(1) + ' · ×' + LV_MUL[3].toFixed(1) + '이고 <b>도시에서 가장 높은 한 곳만</b> 셉니다. 조폐·곡창·공방은 레벨을 올려도 효과가 같습니다. 합병하면 두 곳이 한 곳이 되므로 당장의 수입은 조금 줄고 <b>부지가 하나 빕니다</b>(합병 창에 얼마가 달라지는지 적혀 있습니다).</p>' +\n"
           "  '<p><b>치안</b> — 금·병량 수입에 (50 + 치안 ÷ 2)%, 징병량에 (40 + 치안 × 0.6)%가 곱해지고, 20 아래면 징병할 수 없습니다. 징병할 때마다 10씩, 50을 넘으면 매월 1씩 내려가고 <b>순찰</b>로 올립니다. 거점 창의 치안 칸을 누르면 지금의 값이 나옵니다. 민란은 없습니다.</p>' +\n")
s = rep(s, "전법은 기력을 쓰고, 병과 적성(C→S)이 높을수록 쓸 수 있는 전법이 늘고 잘 통합니다.</p>' +\n",
           "전법은 기력을 쓰고, 병과 적성(C→S)이 높을수록 쓸 수 있는 전법이 늘고 잘 통합니다. 적성은 부대의 공격·방어에도 곱해집니다(C ×' + APT_MUL.C + ' ~ S ×' + APT_MUL.S + ') — 주장과 부장 가운데 가장 높은 적성을 씁니다. 무장 줄마다 능력치 아래에 <b>창 · 극 · 노 · 기 · 병기</b> 적성이 적혀 있습니다.</p>' +\n")
s = rep(s, "거점의 출진 탭에서 병과, 무장(주장과 부장 둘), 병력, 군량을 정하면 부대가 성 앞에 나옵니다.",
           "거점의 출진 탭에서 병과, 무장(주장과 부장 둘), 병력, 군량(' + days(DEPLOY_FOOD[0]) + '~' + days(DEPLOY_FOOD[DEPLOY_FOOD.length - 1]) + '분)을 정하면 부대가 성 앞에 나옵니다.")
s = rep(s, "  '<h3>앱으로 설치</h3>",
           "  '<h3>공유</h3><p>제목 화면과 메뉴의 <b>공유</b>를 누르면 휴대폰의 공유 창이 열립니다(안 열리는 곳에서는 주소와 QR이 적힌 창). 보내는 것은 게임의 주소뿐이고, 저장한 판은 함께 가지 않습니다.</p>' +\n"
           "  '<h3>앱으로 설치</h3>")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- index.html
p = 'src/index.html'; s = io.open(p, encoding='utf-8').read()
s = rep(s, '      <button id="tHelp" type="button">도움말</button>\n',
           '      <div class="t-row"><button id="tHelp" type="button">도움말</button><button id="tShare" type="button">공유</button></div>\n')
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- style.css
p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """
/* ---------- v0.11 ---------- */
/* 무장 줄의 적성 */
.row .ap5 { display: flex; gap: 9px; font-size: 11.5px; margin-top: 1px; color: var(--dim); }
.ap5 span { display: inline-flex; align-items: baseline; gap: 2px; }
.ap5 i { font-style: normal; }
.ap5 b { font-weight: 700; color: var(--ink-2); }
.ap5 b.S { color: var(--seal); font-weight: 800; } .ap5 b.A { color: var(--ochre); } .ap5 b.C { color: var(--dim); font-weight: 400; }
.ap5 span.on { box-shadow: inset 0 -2px 0 var(--seal); }
.ap5 span.on i { color: var(--ink); font-weight: 700; }
.note.aptn { margin: 0 0 8px; }
/* 치안 칸(누르면 풀이) */
.stats .tap { cursor: pointer; }
.stats .tap small { color: var(--dim); }
.stats.ordst { grid-template-columns: 1fr 1fr; margin-bottom: 4px; }
.stats.ordst b { font: 900 19px var(--font-display); }
/* 시설 창: 지금 레벨의 값을 크게, 실제 수입을 그 아래에 */
.card.fcd p { margin: 0; }
.fcv { display: block; font: 900 15.5px var(--font-display); color: var(--ink); }
.fcn { display: block; margin-top: 4px; color: var(--ink-2); font-size: 13px; }
.fcn small { color: var(--dim); font-size: 11.5px; }
.dlg-f .pv small { color: var(--dim); font-size: 11.5px; font-weight: 400; }
/* 공유 */
.shr .shurl { width: 100%; height: 44px; border: 1px solid var(--ink); border-radius: 2px; background: var(--paper); color: var(--ink); font: 600 13.5px var(--font-body); padding: 0 10px; margin: 2px 0 9px; box-sizing: border-box; }
.cmds.c2 { grid-template-columns: 1fr 1fr; } .cmds.c1 { grid-template-columns: 1fr; }
.qrw { display: flex; flex-direction: column; align-items: center; gap: 6px; margin: 14px 0 2px; }
.qrw small { color: var(--dim); font-size: 12px; }
.qr { width: min(46vw, 190px); height: auto; border: 1px solid var(--line-2); border-radius: 2px; }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('p1 ok')
