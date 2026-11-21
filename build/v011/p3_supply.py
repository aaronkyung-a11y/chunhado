# v0.11 (3/…): 수송대의 부대 보급  (core.js · ui_panels.js · style.css)
#  요청: "수송대가 군대에도 보급해줄 수 있으면 좋겠다."
#  - 수송대가 옆 칸의 아군 부대에 병량과 병력을 넘긴다(cmdSupply). 병력은 받는 주장의 지휘 한도까지, 창·극·노·기병은 수송대에 실은 그 무기만큼(무기도 함께 넘어간다).
#    수송대는 병력 100명을 남기고, 보급하면 그 턴의 행동을 마친다. 받는 부대의 행동은 쓰지 않는다. 행동력은 들지 않는다.
#  - 부대 창: 수송대에는 [보급](옆에 아군 부대가 없으면 흐리게 — 누르면 풀이), 수송대 옆의 부대에는 [보급 받기]. 수송대 창에 실은 것을 적는다.
#  - AI 와 군단은 쓰지 않는다(전과 같이 거점으로 실어 나른다).
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- core.js
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "function unitWait(u) { u.done = true; u.ox = -1; return { ok: true }; }\n",
"""function unitWait(u) { u.done = true; u.ox = -1; return { ok: true }; }
/* ---------- 보급(v0.11): 수송대가 옆 칸의 아군 부대에 병량과 병력을 넘긴다 ----------
   병력은 받는 주장의 지휘 한도까지, 수송대에는 100명을 남긴다. 창·극·노·기병에게는 수송대에 실은 그 무기만큼만(무기도 함께 넘어간다).
   보급한 수송대는 그 턴의 행동을 마친다. 받는 부대의 행동은 쓰지 않는다. */
function supplyTargets(t) {                                  // 수송대 t 가 보급할 수 있는 부대
  var out = []; if (!t || t.type !== 'trans') return out;
  nbrs(t.c, t.r).forEach(function (n) { var u = UAT[K(n[0], n[1])]; if (u && u.f === t.f && u.type !== 'trans') out.push(u); });
  return out;
}
function supplySources(u) {                                  // 부대 u 옆에서 보급해 줄 수 있는 수송대(아직 행동하지 않은)
  var out = []; if (!u || u.type === 'trans') return out;
  nbrs(u.c, u.r).forEach(function (n) { var t = UAT[K(n[0], n[1])]; if (t && t.f === u.f && t.type === 'trans' && !t.done && !t.status) out.push(t); });
  return out;
}
function supplyMax(t, u) {                                   // 넘길 수 있는 한도 { food, troops, why: 병력이 그만큼인 까닭 }
  var wp = UNIT_TYPES[u.type].weapon, room = Math.max(0, cmdCap(uLeader(u)) - u.troops), spare = Math.max(0, t.troops - 100), m = Math.min(room, spare);
  var why = room <= spare ? '지휘 한도 ' + nf(cmdCap(uLeader(u))) : '수송대에 100명은 남깁니다';
  if (wp && wp !== 'ram') { var have = (t.cargo && t.cargo[wp]) || 0; if (have < m) { m = have; why = '실은 ' + WEAPON_NAMES[wp] + ' ' + nf(have); } }
  return { food: Math.max(0, Math.floor(t.food)), troops: Math.floor(m / 100) * 100, why: why };
}
function cmdSupply(t, u, give) {
  if (!t || !u || t.type !== 'trans' || u.type === 'trans' || t.f !== u.f) return ERR('보급할 수 없는 대상입니다');
  if (t.done) return ERR('수송대가 이미 행동을 마쳤습니다');
  if (t.status) return ERR('수송대가 명령을 들을 수 없습니다');
  if (hdist(t.c, t.r, u.c, u.r) !== 1) return ERR('옆 칸의 부대에만 보급할 수 있습니다');
  var food = Math.max(0, Math.floor(give.food || 0)), troops = Math.max(0, Math.floor((give.troops || 0) / 100) * 100), mx = supplyMax(t, u);
  if (food > mx.food) return ERR('수송대의 병량이 모자랍니다');
  if (troops > mx.troops) return ERR('병력은 ' + nf(mx.troops) + '명까지 넘길 수 있습니다 (' + mx.why + ')');
  if (!food && !troops) return ERR('넘길 것을 정하세요');
  t.food -= food; u.food += food;
  if (troops) {
    var wp = UNIT_TYPES[u.type].weapon;
    if (wp && wp !== 'ram') t.cargo[wp] -= troops;                       // 무기도 함께 넘어간다
    u.morale = Math.round((u.troops * u.morale + troops * t.morale) / (u.troops + troops));
    u.troops += troops; t.troops -= troops; if (!(u.max >= u.troops)) u.max = u.troops;
  }
  t.done = true; t.ox = -1;
  return { ok: true, food: food, troops: troops };
}
""")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui_panels.js
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()

# 보급 창
s = rep(s, "/* ---------- 거점 패널 ---------- */\nfunction baseSheet(b0, tab0) {",
"""/* ---------- 보급(v0.11): 수송대 t → 옆의 아군 부대 u ---------- */
function foodDays(food, u, troops) { var per = Math.ceil(troops / (uHas(u, '둔전') ? 40 : 20)); return per > 0 ? Math.floor(food / per) : 0; }
function cargoLine(t) {                                    // 수송대에 실은 것
  var c = t.cargo || {}, h = '<div class="wp cgo"><span>' + ico('food') + '병량 <b>' + fmt(t.food) + '</b></span>' + (t.gold ? '<span>' + ico('gold') + '금 <b>' + fmt(t.gold) + '</b></span>' : '');
  [['spear', '창'], ['halberd', '극'], ['bow', '노'], ['horse', '군마']].forEach(function (w) { if (c[w[0]]) h += '<span>' + ico(w[0]) + w[1] + ' <b>' + fmt(c[w[0]]) + '</b></span>'; });
  if (c.ram) h += '<span>' + ico('ram') + '충차 <b>' + c.ram + '</b></span>';
  return h + '</div>';
}
function supplyPairs(x) {                                  // 이 부대가 낄 수 있는 보급: [수송대, 받는 부대] 들(군단의 부대는 빼고)
  var out = [];
  if (x.type === 'trans') { if (!x.done && !x.status && !unitCorps(x)) supplyTargets(x).forEach(function (u) { if (!unitCorps(u)) out.push([x, u]); }); }
  else if (!unitCorps(x)) supplySources(x).forEach(function (t) { if (!unitCorps(t)) out.push([t, x]); });
  return out;
}
function flowSupply(t, u) {
  if (!alive(t) || !alive(u)) return;
  var mx = supplyMax(t, u), own = Math.ceil(t.troops / 20) * 3;                 // 수송대가 30일 버틸 몫은 남기는 것을 처음 값으로
  var st = { food: Math.max(0, Math.floor((mx.food - own) / 100) * 100), troops: 0 };
  function pv() {
    var a = foodDays(u.food, u, u.troops), b2 = foodDays(u.food + st.food, u, u.troops + st.troops), left = t.food - st.food, ld = foodDays(left, t, t.troops - st.troops);
    return uName(u) + ' 군량 <b>' + days(a) + '분 → ' + days(b2) + '분</b>' + (st.troops ? ' · 병력 <b>' + fmt(u.troops) + ' → ' + fmt(u.troops + st.troops) + '</b>' : '') +
      '<br><small>수송대에 남는 병량 ' + fmt(left) + ' (' + days(ld) + '분)' + (ld < 3 ? ' — <b class="bad">돌아갈 길이 멀면 굶습니다</b>' : '') + '</small>';
  }
  showDialog({
    render: function () {
      var T = UNIT_TYPES[u.type], wp = T.weapon;
      var h = dlgHead('보급 — ' + uName(t) + ' → ' + uName(u)) + '<div class="dlg-b">' +
        '<div class="card supc">' + porTag(uLeader(u), 'md') + '<p><b>' + uName(u) + '</b> · ' + T.name + ' ' + fmt(u.troops) + '명<br><small>군량 ' + fmt(u.food) + ' (' + days(foodDays(u.food, u, u.troops)) + '분) · 지휘 한도 ' + fmt(cmdCap(uLeader(u))) + '</small></p></div>' +
        '<div class="fld"><label><span>병량 (수송대에 ' + fmt(mx.food) + ')</span><b id="spFv">' + fmt(st.food) + '</b></label><input type="range" min="0" max="' + Math.floor(mx.food / 100) * 100 + '" step="100" value="' + st.food + '" data-i="food"></div>';
      if (mx.troops >= 100) h += '<div class="fld"><label><span>병력 (' + fmt(mx.troops) + '명까지 — ' + mx.why + ')</span><b id="spTv">' + fmt(st.troops) + '</b></label><input type="range" min="0" max="' + mx.troops + '" step="100" value="' + st.troops + '" data-i="troops"></div>';
      else h += '<p class="note">병력은 넘길 수 없습니다 — ' + (t.troops <= 100 ? '수송대에 100명은 남깁니다' : mx.why) + (wp && wp !== 'ram' ? ' · ' + T.name + '에게는 ' + WEAPON_NAMES[wp] + '도 실어 와야 합니다' : '') + '</p>';
      h += '<p class="note">보급하면 수송대는 이번 턴의 행동을 마칩니다 · 행동력은 들지 않습니다</p></div>' +
        '<div class="dlg-f"><div class="pv" id="spP">' + pv() + '</div><button class="btn pri" type="button" data-a="ok">보급</button></div>';
      return h;
    },
    on: {
      food: function (el) { st.food = +el.value; $('spFv').textContent = fmt(st.food); $('spP').innerHTML = pv(); },
      troops: function (el) { st.troops = +el.value; $('spTv').textContent = fmt(st.troops); $('spP').innerHTML = pv(); },
      ok: function () {
        var r = cmdSupply(t, u, st);
        if (!r.ok) return toast(r.msg);
        closeDialog(); sfx('drum');
        talk(uLeader(t), sayLine(uLeader(t), 'trans'), uName(u) + '에 보급 — ' + (r.food ? '병량 ' + fmt(r.food) : '') + (r.food && r.troops ? ' · ' : '') + (r.troops ? '병력 ' + fmt(r.troops) + '명' : ''), 3000);
        if (R3 && R3.ready) syncScene();
        var su = selUnit(); if (su) { UI.rc = unitReach(su); UI.atk = allTargets(su); } else { UI.rc = null; UI.atk = null; }
        refreshSheet(); requestDraw(); afterAction();
      }
    }
  }, true);
}
/* [보급] · [보급 받기]: 짝이 하나면 바로, 여럿이면 고른다 */
function pickSupply(x) {
  var ps = supplyPairs(x);
  if (!ps.length) return toast(x.type === 'trans' ? '아군 부대의 옆 칸으로 가면 병량과 병력을 넘길 수 있습니다' : '옆에 보급해 줄 수송대가 없습니다', 2800);
  if (ps.length === 1) return flowSupply(ps[0][0], ps[0][1]);
  showDialog({
    render: function () {
      var h = dlgHead(x.type === 'trans' ? '보급 — 어느 부대에' : '보급 — 어느 수송대에서') + '<div class="dlg-b"><div class="rows">';
      ps.forEach(function (pr, i) { var o = pr[x.type === 'trans' ? 1 : 0]; h += '<button class="row" type="button" data-a="go" data-v="' + i + '">' + porTag(uLeader(o)) + '<span class="mid"><span class="nm">' + uName(o) + '</span><span class="ds">' + UNIT_TYPES[o.type].name + ' ' + fmt(o.troops) + '명 · 군량 ' + fmt(o.food) + ' (' + days(unitFoodTurns(o)) + '분)</span></span></button>'; });
      return h + '</div></div>';
    },
    on: { go: function (el) { var pr = ps[+el.getAttribute('data-v')]; if (pr) flowSupply(pr[0], pr[1]); } }
  });
}

/* ---------- 거점 패널 ---------- */
function baseSheet(b0, tab0) {""")

# 부대 창: 단추와 실은 것
s = rep(s, "      direct: function () { var x = UMAP[u.id]; if (!x) return; var r = corpsTakeUnit(x);",
           "      supply: function () { var x = UMAP[u.id]; if (x) pickSupply(x); },\n      direct: function () { var x = UMAP[u.id]; if (!x) return; var r = corpsTakeUnit(x);")
s = rep(s, "'>' + days(turns) + '분</b></div></div>' + statusBanner(x);\n",
           "'>' + days(turns) + '분</b></div></div>' + (x.type === 'trans' && mine ? cargoLine(x) : '') + statusBanner(x);\n")
s = rep(s, "            (canDouse ? '<button class=\"act\" type=\"button\" data-a=\"douse\"><b>소화</b><small>기력 10</small></button>' : '') +\n",
           "            (canDouse ? '<button class=\"act\" type=\"button\" data-a=\"douse\"><b>소화</b><small>기력 10</small></button>' : '') +\n"
           "            (x.type === 'trans' ? '<button class=\"act' + (supplyPairs(x).length ? ' pri' : ' off') + '\" type=\"button\" data-a=\"supply\"><b>보급</b><small>' + (supplyPairs(x).length ? '옆의 아군 부대에' : '아군 부대 옆에서') + '</small></button>' : (supplyPairs(x).length ? '<button class=\"act pri\" type=\"button\" data-a=\"supply\"><b>보급 받기</b><small>옆의 수송대에서</small></button>' : '')) +\n")
# 행동을 마친 부대도 옆에 수송대가 있으면 받을 수 있다
s = rep(s, "      else if (mine && x.done) h += '<p class=\"note\">이번 턴 행동 끝' + (x.dest >= 0 ? ' · ' + destName(x.dest) + ' 방면 행군 중' : '') + '</p>';\n",
           "      else if (mine && x.done) h += '<p class=\"note\">이번 턴 행동 끝' + (x.dest >= 0 ? ' · ' + destName(x.dest) + ' 방면 행군 중' : '') + '</p>' + (x.type !== 'trans' && supplyPairs(x).length ? '<div class=\"acts\"><button class=\"act pri\" type=\"button\" data-a=\"supply\"><b>보급 받기</b><small>옆의 수송대에서</small></button></div>' : '');\n")
# 수송 창의 풀이
s = rep(s, "<p class=\"note\">군량 80일분은 자동으로 실립니다</p>", "<p class=\"note\">군량 80일분은 자동으로 실립니다 · 아군 거점에 들이면 합쳐지고, <b>아군 부대 옆</b>에서는 [보급]으로 병량과 병력을 넘깁니다</p>")
s = rep(s, "'수송대 출발 — 아군 거점에 들이면 물자가 합쳐집니다'", "'수송대 출발 — 거점에 들이거나, 아군 부대 옆에서 [보급]'")
# 도움말
s = rep(s, "  '<h3>행군(선택)</h3>",
           "  '<h3>수송과 보급</h3><p>거점의 출진 탭 <b>수송</b>으로 병력·금·병량·무기를 실은 수송대를 냅니다. 아군 거점에 들이면 실은 것이 그 거점에 합쳐집니다. <b>아군 부대의 옆 칸</b>에 가면 부대 창의 <b>보급</b>으로 병량과 병력을 넘길 수 있습니다(받는 부대 쪽에서는 <b>보급 받기</b>). 병력은 받는 주장의 지휘 한도까지이고, 창병·극병·노병·기병에게는 그 무기도 실어 와야 합니다. 보급한 수송대는 그 턴의 행동을 마칩니다.</p>' +\n"
           "  '<h3>행군(선택)</h3>")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- style.css
p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """/* 보급 */
.wp.cgo { margin: -2px 0 8px; }
.card.supc { align-items: center; gap: 10px; }
.card.supc p { margin: 0; }
.card.supc small { color: var(--dim); font-size: 12px; }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('p3 ok')
