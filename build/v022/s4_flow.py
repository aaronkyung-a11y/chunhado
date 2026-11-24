# v0.22 (4) 출진 · 수송의 흐름 — 요청 6 · 9 · 11
#   ⑥ "수송 시 장수를 선택하고 다음 버튼을 누르면 수송 물자를 선택하게 하면 더 좋을 것 같아. '짐' 말고 '물자' 로 표현 변경"
#      수송 창이 두 걸음(① 호송 무장 · 짐 ② 어디로)에서 세 걸음이 된다: ① 호송 무장 → [다음] → ② 물자 → [다음] → ③ 어디로.
#      말: 짐 → 물자(걸음 이름 · 되돌아가는 단추 · '실을 물자' · 보급 완료 창의 '남은 물자' · 도움말).
#   ⑨ "병량이 모자라면 병량이 모자라서 안된다고 해."
#      0.21 까지: 출진할 때 도시 병량이 고른 군량에 못 미치면 작은 붉은 글씨 한 줄('모자랍니다 — N일분만 실립니다')만 띄우고 말없이 덜 실었다(0 이어도 그대로 나갔다).
#               수송대의 군량 80일분도 모자라면 말없이 있는 만큼만 실었고, 병량이 500 에 못 미치면 병량 칸이 아예 나오지 않았다.
#      이제: 모자라면 모자란다고 말하고, 말없이 덜 싣지 않는다.
#        출진 — 댈 수 없는 군량 칸은 흐리게(누르면 "도시 병량이 모자랍니다 — 180일분에 9,000 필요 · 보유 4,000").
#               ②로 넘어올 때 고른 날수를 댈 수 없으면 댈 수 있는 가장 긴 것을 고르고 그렇게 했다고 적는다. 하나도 못 대면 아무것도 고르지 않은 채로 두고
#               [있는 만큼 싣기 · N일분] 단추를 낸다(열흘분 이상일 때). [출진]은 흐려지고, 누르면 까닭을 말한다. 열흘분도 없으면 출진할 수 없다.
#        수송 — 물자 걸음에 붉게: "도시 병량이 모자랍니다 — 호송 병력의 군량 80일분에 … 필요 · 보유 … N일분만 싣고 떠납니다". 열흘분도 없으면 떠날 수 없다(까닭을 말한다).
#               병량이 실을 만큼(500) 없으면 그렇다고 적는다.
#      AI 와 규칙(cmdDeploy)은 그대로다 — 화면에서 내가 내리는 명령만 달라진다.
#   ⑪ "출진 무장 고를 때, 적성을 고르면 그 적성이 높은 순대로 보여주면 좋겠네"
#      병과를 고르면 무장 목록이 그 병과의 적성이 높은 차례(S → A → B → C, 같으면 전처럼 싸움 솜씨 순)로 다시 선다. 검병은 적성이 없어 전과 같다.
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)
def cut(s, a, b, new):
    i = s.index(a); j = s.index(b, i); assert s.count(a) == 1, a[:50]
    return s[:i] + new + s[j:]

s = rd('src/ui_panels.js')

# ================= ⑪ 출진: 적성 순 =================
s = rep(s, """        h += '</div><div class="sec">무장 <small>첫 번째가 주장 · 3명까지</small><button class="btn auto" type="button" data-a="auto">자동 편성</button></div><div class="rows">';
        var ai = APT_IDX[st.type];
        for (i = 0; i < list.length; i++) {
          var o = list[i], si = st.ids.indexOf(o.id);""", """        var ai = APT_IDX[st.type], L1 = list;
        if (ai !== undefined) L1 = list.slice().sort(function (x, y) { return APT_RANK[y.apt.charAt(ai)] - APT_RANK[x.apt.charAt(ai)] || aiMilScore(y) - aiMilScore(x); });      // v0.22: 고른 병과의 적성이 높은 차례(같으면 싸움 솜씨 순 — 검병은 적성이 없어 전과 같다)
        h += '</div><div class="sec">무장 <small>첫 번째가 주장 · 3명까지' + (ai !== undefined ? ' · <b class="aptby">' + UNIT_TYPES[st.type].name + ' 적성 순</b>' : '') + '</small><button class="btn auto" type="button" data-a="auto">자동 편성</button></div><div class="rows">';
        for (i = 0; i < L1.length; i++) {
          var o = L1[i], si = st.ids.indexOf(o.id);""")

# ================= ⑨ 출진: 군량 =================
s = rep(s, """  function food() { return Math.min(b.food, Math.ceil(st.troops / 20) * st.turns); }
  function foodNote() {                                        // 도시 병량이 모자라면 실제로 실리는 날수를 적는다
    var per = Math.max(1, Math.ceil(st.troops / 20)), need = per * st.turns;
    return '도시 병량 ' + fmt(b.food) + (need > b.food ? ' · <b class="bad">모자랍니다 — ' + days(Math.floor(b.food / per)) + '분만 실립니다</b>' : ' · 이웃 거점까지 20~50일');
  }""", """  /* v0.22 군량: 도시 병량이 모자라면 모자란다고 말한다 — 말없이 덜 싣지 않는다.
     st.turns = 고른 날수(턴) · 0 = 고르지 못함(어느 것도 댈 수 없다) · -1 = '있는 만큼'. st.low = 낮춰 골랐을 때 처음 바란 날수(말로 알린다) */
  function per() { return Math.max(1, Math.ceil(st.troops / 20)); }                 // 열흘에 먹는 병량
  function needOf(n) { return per() * n; }
  function canT() { return Math.floor(b.food / per()); }                            // 지금 병력으로 도시 병량이 대는 턴 수
  function okT(n) { return needOf(n) <= b.food; }
  function foodBad() {                                                              // 지금 고른 군량으로는 못 나간다 → 그 까닭. 나갈 수 있으면 ''
    var none = '병량이 모자라 출진할 수 없습니다 — 병력 ' + fmt(st.troops) + '명의 열흘분(' + fmt(per()) + ')도 없습니다 · 도시 병량 ' + fmt(b.food);
    if (st.turns === -1) return canT() >= 1 ? '' : none;
    if (st.turns > 0 && okT(st.turns)) return '';
    if (canT() < 1) return none;
    return '병량이 모자랍니다 — ' + (st.turns > 0 ? days(st.turns) + '분에 ' + fmt(needOf(st.turns)) + ' 필요 · ' : '') + '도시 병량 ' + fmt(b.food) + '. 군량을 더 짧게 고르거나 [있는 만큼 싣기], 아니면 병력을 줄이세요';
  }
  function food() { return st.turns === -1 ? per() * canT() : (st.turns > 0 && okT(st.turns) ? needOf(st.turns) : 0); }
  function foodNote() {
    var h0 = '도시 병량 ' + fmt(b.food);
    if (st.turns === -1 && canT() >= 1) return h0 + ' · <b class="bad">있는 만큼 싣습니다 — ' + days(canT()) + '분(' + fmt(per() * canT()) + ')</b>';
    if (st.turns > 0 && okT(st.turns)) return h0 + (st.low ? ' · <b class="bad">병량이 모자라 ' + st.low + '분 대신 ' + days(st.turns) + '분을 골랐습니다</b>' : ' · 이웃 거점까지 20~50일');
    if (canT() < 1) return h0 + ' · <b class="bad">병량이 모자라 출진할 수 없습니다</b> — 병력 ' + fmt(st.troops) + '명의 열흘분(' + fmt(per()) + ')도 없습니다. 병력을 줄이거나 병량을 채우세요(시장의 거래 · 수송)';
    return h0 + ' · <b class="bad">병량이 모자랍니다</b> — ' + (st.turns > 0 ? days(st.turns) + '분에 ' + fmt(needOf(st.turns)) + ' 필요' : days(DEPLOY_FOOD[0]) + '분(' + fmt(needOf(DEPLOY_FOOD[0])) + ')도 댈 수 없습니다') +
      ' <button class="btn auto" type="button" data-a="fmax">있는 만큼 싣기 · ' + days(canT()) + '분</button>';
  }
  function foodPick() {                                                             // ②로 넘어올 때: 고른 날수를 댈 수 없으면 댈 수 있는 가장 긴 것으로(그렇게 했다고 적는다). 하나도 못 대면 0
    st.low = '';
    if (st.turns === -1) { if (canT() >= 1) return; st.turns = DEPLOY_FOOD[1]; }
    if (st.turns > 0 && okT(st.turns)) return;
    var want = st.turns > 0 ? st.turns : DEPLOY_FOOD[1], best = 0;
    DEPLOY_FOOD.forEach(function (n) { if (n <= want && okT(n)) best = n; });
    if (best) st.low = days(want);
    st.turns = best;
  }""")
s = rep(s, """      DEPLOY_FOOD.forEach(function (n) { h += '<button class="opt' + (st.turns === n ? ' on' : '') + '" type="button" data-a="turns" data-v="' + n + '"><b>' + days(n) + '분</b><small>' + fmt(Math.ceil(st.troops / 20) * n) + '</small></button>'; });""",
        """      DEPLOY_FOOD.forEach(function (n) { h += '<button class="opt' + (st.turns === n ? ' on' : '') + (okT(n) ? '' : ' off') + '" type="button" data-a="turns" data-v="' + n + '"><b>' + days(n) + '분</b><small>' + fmt(needOf(n)) + '</small></button>'; });      // v0.22: 댈 수 없는 칸은 흐리게""")
s = rep(s, """<button class="btn pri" type="button" data-a="ok"' + (st.ids.length && st.troops >= 100 ? '' : ' disabled') + '>출진</button></div>';""",
        """<button class="btn pri' + (foodBad() ? ' off' : '') + '" type="button" data-a="ok"' + (st.ids.length && st.troops >= 100 ? '' : ' disabled') + '>출진</button></div>';""")
s = rep(s, """      turns: function (el) { st.turns = +el.getAttribute('data-v'); refreshDialog(); },""",
        """      turns: function (el) {
        var n = +el.getAttribute('data-v');
        if (!okT(n)) return toast('도시 병량이 모자랍니다 — ' + days(n) + '분에 ' + fmt(needOf(n)) + ' 필요 · 보유 ' + fmt(b.food), 2800);      // v0.22: 모자라면 모자란다고 말한다
        st.turns = n; st.low = ''; refreshDialog();
      },
      fmax: function () { if (canT() < 1) return toast(foodBad(), 3400); st.turns = -1; st.low = ''; refreshDialog(); },""")
s = rep(s, """      next: function () { if (!st.ids.length) return toast('주장을 고르세요'); fix(); if (st.troops < 100) return toast('데리고 나갈 병력이 없습니다'); st.step = 2; EX.open(); },""",
        """      next: function () { if (!st.ids.length) return toast('주장을 고르세요'); fix(); if (st.troops < 100) return toast('데리고 나갈 병력이 없습니다'); foodPick(); st.step = 2; EX.open(); },""")
s = rep(s, """        for (var k = 0; k < bs.length; k++) bs[k].querySelector('small').textContent = fmt(Math.ceil(st.troops / 20) * +bs[k].getAttribute('data-v'));
        if ($('dpN')) $('dpN').innerHTML = foodNote();
        var ok = document.querySelector('#modal [data-a="ok"]'); if (ok) ok.disabled = !(st.troops >= 100);""",
        """        for (var k = 0; k < bs.length; k++) { var nk = +bs[k].getAttribute('data-v'); bs[k].querySelector('small').textContent = fmt(needOf(nk)); bs[k].classList.toggle('off', !okT(nk)); }
        if (st.low && !(st.turns > 0 && okT(st.turns))) st.low = '';
        if ($('dpN')) $('dpN').innerHTML = foodNote();
        var ok = document.querySelector('#modal [data-a="ok"]'); if (ok) { ok.disabled = !(st.troops >= 100); ok.classList.toggle('off', !!foodBad()); }""")
s = rep(s, """        if (st.step !== 2) return;
        var r = cmdDeploy(b, { type: st.type, ids: st.ids, troops: st.troops, food: food(), at: st.at || undefined });""",
        """        if (st.step !== 2) return;
        var fb = foodBad(); if (fb) return toast(fb, 3600);                // v0.22: 병량이 모자라면 모자라서 안 된다고 말한다
        var r = cmdDeploy(b, { type: st.type, ids: st.ids, troops: st.troops, food: food(), at: st.at || undefined });""")

# ================= ⑥ · ⑨ 수송: 세 걸음 · 물자 =================
NEW_TRANS = r"""function flowTransport(b) {
  var cp0 = baseCorps(b);                                       // v0.18: 군단에 맡긴 거점에서도 보낸다(군단장은 자리를 지킨다 · 행동력은 직할의 것 · 나간 수송대는 직할)
  var list = idleOfficers(b).filter(function (o) { return !(cp0 && cp0.lead === o.id); }).sort(function (x, y) { return aiMilScore(x) - aiMilScore(y); });
  if (!list.length) return toast('행동할 수 있는 무장이 없습니다');
  if (b.troops < 100) return toast('호위할 병력이 없습니다');
  var st = { step: 1, id: list[0].id, troops: Math.min(1000, Math.floor(b.troops / 100) * 100), gold: 0, food: 0, spear: 0, halberd: 0, bow: 0, horse: 0, ram: 0, to: null }, D, DP;
  var fs = [['troops', '병력', b.troops, 100], ['gold', '금', b.gold, 50], ['food', '병량', b.food, 500], ['spear', '창', b.w.spear, 100], ['halberd', '극', b.w.halberd, 100], ['bow', '노', b.w.bow, 100], ['horse', '군마', b.w.horse, 100], ['ram', '충차', b.w.ram, 1]];
  function load() { var a = []; fs.forEach(function (f) { if (st[f[0]] > 0) a.push(f[1] + ' ' + fmt(st[f[0]])); }); return a.join(' · '); }
  /* v0.22 군량: 호송 병력이 80일 동안 먹을 병량은 고르지 않아도 싣는다. 도시 병량이 그에 못 미치면 그렇다고 말하고, 열흘분도 없으면 떠나지 못한다 */
  function per() { return Math.max(1, Math.ceil(st.troops / 20)); }
  function need() { return per() * 8; }
  function foodOut() { return Math.max(st.food, Math.min(b.food, need())); }
  function cant() { return Math.floor(b.food / per()) < 1 ? '병량이 모자라 수송대를 낼 수 없습니다 — 호송 병력 ' + fmt(st.troops) + '명의 열흘분(' + fmt(per()) + ')도 없습니다 · 도시 병량 ' + fmt(b.food) : ''; }
  function foodNote() {
    if (b.food >= need()) return '호송 병력의 군량 <b>80일분(' + fmt(need()) + ')</b>은 고르지 않아도 실립니다';
    var d = Math.floor(b.food / per());
    return '<b class="bad">도시 병량이 모자랍니다</b> — 호송 병력의 군량 80일분에 ' + fmt(need()) + ' 필요 · 보유 ' + fmt(b.food) + '. ' +
      (d >= 1 ? '<b class="bad">' + days(d) + '분만 싣고 떠납니다</b>(가는 길이 그보다 멀면 굶습니다)' : '<b class="bad">열흘분도 없어 떠날 수 없습니다</b>') + ' · 병력을 줄이면 덜 듭니다';
  }
  var on = {
    pick: function (el) { st.id = +el.getAttribute('data-v'); refreshDialog(); },
    auto: function () { var t = autoTeam(b, 'trans', 0); if (t.length) st.id = t[0]; toast('자동 선택', 1500); refreshDialog(); },
    next: function () {
      if (st.step === 1) { st.step = 2; paintDialog(0); return; }             // ① 무장 → ② 물자
      var c = cant(); if (c) return toast(c, 3600);                           // v0.22: 병량이 모자라면 모자라서 안 된다고 말한다
      st.step = 3; DP.open();                                                // ② 물자 → ③ 어디로
    },
    prev: function () { if (st.step === 3) { st.step = 2; DP.close(); paintDialog(0); } else { st.step = 1; paintDialog(0); } },
    to: function (el) { var t = DP.find(el.getAttribute('data-v')); if (t) DP.pickT(t); },
    ok: function () {
      if (st.step !== 3) return;
      if (!st.to) return toast('갈 곳을 고르세요 — 지도의 우리 성이나 아래 목록', 2000);
      var c = cant(); if (c) return toast(c, 3600);
      var free = st.to.k === 'x', p = free ? null : (DP.plan(st.to, true) || DP.plan(st.to)); if (!free && !p) return toast('그곳으로 가는 길이 없습니다');
      var tn = st.to.n;
      var r = cmdDeploy(b, { type: 'trans', ids: [st.id], troops: st.troops, food: foodOut(), gold: st.gold, cargo: { spear: st.spear, halberd: st.halberd, bow: st.bow, horse: st.horse, ram: st.ram }, at: p ? p.spot : undefined });
      if (!r.ok) return toast(r.msg);
      closeDialog(); sfx('drum'); talk(uLeader(r.unit), sayLine(uLeader(r.unit), 'trans'), free ? '수송대 출발 — 부대를 눌러 갈 곳을 정하세요' : '수송대 출발 — ' + tn + (p.turns ? ' · 약 ' + days(p.turns) : ''), 3200); syncScene(); selectUnit(r.unit); UI.sret = backToBase(b.id);
      if (free || K(r.unit.c, r.unit.r) === p.goal) { afterAction(); return; }
      orderMarch(r.unit, p.goal % W, (p.goal - p.goal % W) / W);          // 나오자마자 그곳으로 행군(이번 턴에 갈 수 있는 만큼)
    }
  };
  fs.forEach(function (f) { on[f[0]] = function (el) {
    st[f[0]] = +el.value; $('tv_' + f[0]).textContent = fmt(st[f[0]]);
    if ($('trN')) $('trN').innerHTML = foodNote();
    var nx = document.querySelector('#modal [data-a="next"]'); if (nx) nx.classList.toggle('off', !!cant());
  }; });
  D = {
    render: function () {
      var h, i;
      if (st.step === 1) {                                         // ① 호송 무장
        h = dlgHead('수송 — ' + b.n + stepTag(1, 3, '호송 무장')) + '<div class="dlg-b"><div class="sec">호송 무장<button class="btn auto" type="button" data-a="auto">자동</button></div><div class="rows">';
        for (i = 0; i < list.length; i++) h += offRow(list[i], { a: 'pick', sel: list[i].id === st.id });
        return h + '</div></div><div class="dlg-f"><div class="pv">호송 <b>' + off(st.id).n + '</b> · 행동력 ' + AP.deploy + '</div><button class="btn pri" type="button" data-a="next">다음 ›</button></div>';
      }
      if (st.step === 2) {                                         // ② 물자(v0.22 — 전에는 ①에 함께 있었다)
        h = dlgHead('수송 — ' + b.n + stepTag(2, 3, '물자')) + '<div class="dlg-b"><p class="note team">호송 <b>' + off(st.id).n + '</b></p><div class="sec">실을 물자</div>';
        for (i = 0; i < fs.length; i++) {
          var f = fs[i], m = Math.floor(f[2] / f[3]) * f[3];
          if (m <= 0 && f[0] === 'food') { h += '<p class="note lack"><b class="bad">병량 — 실을 만큼 없습니다</b> (보유 ' + fmt(f[2]) + ' · ' + fmt(f[3]) + '부터 싣습니다)</p>'; continue; }      // v0.22: 말없이 빼지 않는다
          if (m <= 0 && f[0] !== 'troops') continue;
          h += '<div class="fld"><label><span>' + f[1] + ' (보유 ' + fmt(f[2]) + ')</span><b id="tv_' + f[0] + '">' + fmt(st[f[0]]) + '</b></label><input type="range" id="tr_' + f[0] + '" min="' + (f[0] === 'troops' ? 100 : 0) + '" max="' + m + '" step="' + f[3] + '" value="' + st[f[0]] + '" data-i="' + f[0] + '"></div>';
        }
        return h + '<p class="note" id="trN">' + foodNote() + '</p></div><div class="dlg-f"><button class="btn" type="button" data-a="prev">‹ 무장</button><div class="pv">행동력 ' + AP.deploy + '</div><button class="btn pri' + (cant() ? ' off' : '') + '" type="button" data-a="next">다음 ›</button></div>';
      }
      // ③ 어디로(지도에서)
      var free = !!st.to && st.to.k === 'x', p = st.to && !free ? DP.plan(st.to) : null;
      h = dlgHead('수송 — ' + b.n + stepTag(3, 3, '어디로')) + '<div class="dlg-b"><p class="note team">호송 <b>' + off(st.id).n + '</b> · ' + load() + '</p>';
      h += '<p class="note">지도에서 <b>우리 성 · 우리 부대</b>를 누르거나 아래에서 고르세요 — 나오자마자 그곳으로 갑니다. 머물지 · 돌아올지는 <b>수송을 마쳤을 때</b> 묻습니다.</p><div class="rows">' + DP.rows() + '</div></div>';
      return h + '<div class="dlg-f"><button class="btn" type="button" data-a="prev">‹ 물자</button><div class="pv">' + (free ? '<b>성 앞</b> — 직접 움직입니다' : (st.to ? '<b>' + st.to.n + '</b> — ' + (p ? DP.eta(p) : '길 없음') : '갈 곳을 고르세요')) + '</div><button class="btn pri' + (free || (st.to && p) ? '' : ' off') + '" type="button" data-a="ok">출발</button></div>';
    },
    on: on
  };
  DP = destPick(b, st, D);
  showDialog(D);
}

"""
s = cut(s, "function flowTransport(b) {", "/* ---------- 목록·기록·메뉴 ---------- */", NEW_TRANS)

# 말: 짐 → 물자
s = rep(s, "<small>남은 짐 — 병량 ' + fmt(t.food)", "<small>남은 물자 — 병량 ' + fmt(t.food)")
s = rep(s, "data-a=\"tback\"><b>짐 내린 뒤</b>", "data-a=\"tback\"><b>물자 내린 뒤</b>")
s = rep(s, "toast(x.back ? '짐을 내리면 ' + josa(uLeader(x).n, '은는') + ' ' + euro(hb.n) + ' 돌아옵니다' : '짐을 내린 곳에 머뭅니다', 2600);", "toast(x.back ? '물자를 내리면 ' + josa(uLeader(x).n, '은는') + ' ' + euro(hb.n) + ' 돌아옵니다' : '물자를 내린 곳에 머뭅니다', 2600);")
s = rep(s, "수송대를 냅니다 — ① 호송 무장과 짐 ② <b>어디로</b>:", "수송대를 냅니다 — ① 호송 무장 ② <b>물자</b>(실을 것 — 호송 병력의 군량 80일분은 고르지 않아도 실립니다) ③ <b>어디로</b>:")
wr('src/ui_panels.js', s)
print('s4 ok')
