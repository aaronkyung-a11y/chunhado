# v0.10 (1/…): 군단 — 규칙(core.js · data.js)
#  요청: "위임 가능하도록, 군단을 만들어서 위임해서 임무의 방향성을 주도록 하자."
#  - 플레이어가 제 거점을 묶어 군단을 만들고 군단장에게 맡긴다. 맡긴 거점과 거기서 나간 부대는 군단장(AI)이 방침대로 움직인다(ai.js 의 corpsStepper).
#  - 방침: 내정(dev) · 군비(arm) · 공격(atk — 칠 거점) · 지원(sup — 병력·물자를 보낼 내 거점). 언제든 바꿀 수 있고, 거점도 부대도 언제든 직할로 되돌릴 수 있다.
#  - 군단은 제 행동력을 따로 가진다: 턴마다 20 + 도시 × 8 + 군단장 매력 ÷ 5 (120 까지), 255 까지 쌓인다. 직할의 행동력은 직할 도시만 센다.
#  - 군단은 내가 [턴 종료]를 누른 직후, 다른 세력보다 먼저 움직인다(turnStepper 의 첫 단계).
#  - 군단의 부대가 차지한 거점은 그 군단에 든다. 거점을 모두 잃으면 군단은 해산된다. 군단장이 자리를 비우면 다음 사람이 맡는다.
#  - 군단이 한 일은 JOT 에 적어 두었다가 턴 보고에 한 줄로 낸다.
#  AI 세력의 규칙은 건드리지 않는다(군단이 없는 판 · AI 대전은 0.9.3 과 같은 길로 흘러간다).
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- data.js
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var GAME_VERSION = 'v0.9.3';", "var GAME_VERSION = 'v0.10';")
s = rep(s, "var ADVISE = { k: 0.5, min: 50 };", """var ADVISE = { k: 0.5, min: 50 };
/* 군단(v0.10): 방침 넷, 군단 수의 한도, 군단의 행동력(턴마다 base + 도시 × city + 군단장 매력 ÷ 5, max 까지) */
var CORPS_MAX = 6;
var CORPS_DIR = { dev: '내정', arm: '군비', atk: '공격', sup: '지원' };
var CORPS_AP = { base: 20, city: 8, max: 120, cap: 255 };
var CORPS_ATK = { mul: 2.0, add: 3000, grow: 1500 };      // 공격에 나서는 문턱: (수비 + grow × 가는 턴 수) × mul × (지키는 장수의 몫) + add""")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- core.js
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()

# 1) 군단의 자료와 규칙 — 내정 명령 앞에 둔다
CORPS = r"""/* ---------- 군단(v0.10) ----------
   플레이어가 제 거점을 묶어 군단장에게 맡긴다. 맡긴 거점과 거기서 나간 부대는 군단장이 방침대로 움직인다(ai.js 의 corpsStepper).
     G.corps = [{ id, n(번호: 제n군단), lead(군단장 무장 id, 비면 -1), dir, target(거점 id, 없으면 -1), ap, t0(만든 턴), note(지난 차례의 보고) }]
     거점 b.corps · 부대 u.corps = 군단 id (직할이면 0 이거나 없다)
   방침 dir: 'dev' 내정 · 'arm' 군비 · 'atk' 공격(target = 칠 거점) · 'sup' 지원(target = 병력·물자를 보낼 내 거점)
   군단은 제 행동력(ap)을 따로 가진다. 직할의 행동력은 직할 도시만 센다(apRegen). AI 세력에는 군단이 없다. */
function corpsAll() { return G.corps || (G.corps = []); }
function corpsById(id) { var cs = G.corps || [], i; if (!id) return null; for (i = 0; i < cs.length; i++) if (cs[i].id === id) return cs[i]; return null; }
function corpsName(cp) { return '제' + cp.n + '군단'; }
function corpsBases(cp) { return G.bases.filter(function (b) { return b.owner === G.player && b.corps === cp.id; }); }
function corpsCities(cp) { return G.bases.filter(function (b) { return b.owner === G.player && b.corps === cp.id && b.kind === 'city'; }); }
function corpsUnits(cp) { return G.units.filter(function (u) { return u.f === G.player && u.corps === cp.id; }); }
function baseCorps(b) { return (b && b.owner === G.player && b.corps) ? corpsById(b.corps) : null; }       // 그 거점을 맡은 군단(직할이면 null)
function unitCorps(u) { return (u && u.f === G.player && u.corps) ? corpsById(u.corps) : null; }
function directBases(f) { return G.bases.filter(function (b) { return b.owner === f && !(f === G.player && b.corps && corpsById(b.corps)); }); }
function directUnits(f) { return G.units.filter(function (u) { return u.f === f && !(f === G.player && u.corps && corpsById(u.corps)); }); }
function corpsTroops(cp) { var t = 0; corpsBases(cp).forEach(function (b) { t += b.troops; }); corpsUnits(cp).forEach(function (u) { t += u.troops; }); return t; }
function corpsOfficers(cp) {
  return G.officers.filter(function (o) {
    if (o.f !== G.player) return false;
    if (o.unit !== null && o.unit !== undefined) { var u = UMAP[o.unit]; return !!u && u.corps === cp.id; }
    return o.st === 'active' && !!G.bases[o.loc] && G.bases[o.loc].owner === G.player && G.bases[o.loc].corps === cp.id;
  });
}
/* 군단장이 될 수 있는가: 군주가 아니고, 그 군단의 거점에 있거나 그 군단의 부대에 있다 */
function corpsLeadOk(cp, o) {
  if (!o || o.f !== G.player || isLord(o)) return false;
  if (o.unit !== null && o.unit !== undefined) { var u = UMAP[o.unit]; return !!u && u.corps === cp.id; }
  return o.st === 'active' && !!G.bases[o.loc] && G.bases[o.loc].owner === G.player && G.bases[o.loc].corps === cp.id;
}
function corpsLead(cp) { var o = (cp.lead !== undefined && cp.lead >= 0) ? off(cp.lead) : null; return corpsLeadOk(cp, o) ? o : null; }
function corpsLeadScore(o) { return o.ldr + o.int * 0.6 + o.cha * 0.6 + o.war * 0.3; }
function corpsLeadCands(cp) { return G.officers.filter(function (o) { return corpsLeadOk(cp, o); }).sort(function (a, b) { return corpsLeadScore(b) - corpsLeadScore(a) || a.id - b.id; }); }
function corpsRegen(cp) { var L = corpsLead(cp); return Math.min(CORPS_AP.max, CORPS_AP.base + CORPS_AP.city * corpsCities(cp).length + (L ? Math.floor(L.cha / 5) : 0)); }
/* 방침을 말로: "공격 → 여남" */
function corpsDirText(cp) {
  var T = (cp.target !== undefined && cp.target >= 0) ? G.bases[cp.target] : null;
  return CORPS_DIR[cp.dir] + ((cp.dir === 'atk' || cp.dir === 'sup') && T ? ' → ' + T.n : '');
}
function corpsDirOk(cp, dir, target) {
  if (!CORPS_DIR[dir]) return '없는 방침';
  if (dir === 'atk') { var T = G.bases[target]; if (!T || T.owner === G.player) return '칠 거점을 고르세요'; }
  if (dir === 'sup') { var D = G.bases[target]; if (!D || D.owner !== G.player) return '보낼 거점을 고르세요'; if (D.corps === cp.id) return '같은 군단의 거점에는 보낼 수 없습니다'; }
  return '';
}
function corpsSetDir(cp, dir, target) {
  var why = corpsDirOk(cp, dir, target); if (why) return ERR(why);
  cp.dir = dir; cp.target = (dir === 'atk' || dir === 'sup') ? target : -1;
  corpsUnits(cp).forEach(function (u) {                              // 이미 나가 있는 부대도 새 방침을 따른다(수송대는 가던 길을 간다)
    if (u.type === 'trans') return;
    if (dir === 'atk') u.ai = { mode: 'attack', target: cp.target, home: u.home };
    else if (u.ai && u.ai.mode === 'attack') u.ai = { mode: 'return', home: u.home };
  });
  return { ok: true };
}
function corpsSetLead(cp, id) {
  var o = off(id); if (!corpsLeadOk(cp, o)) return ERR('그 군단의 거점이나 부대에 있는 무장만 군단장이 될 수 있습니다(군주 제외)');
  cp.lead = o.id; return { ok: true };
}
/* 새 군단: 직할 거점들을 묶는다. 군단장을 주지 않으면 가장 알맞은 사람이 맡는다. 방침을 주지 않으면 군비 */
function corpsCreate(baseIds, leadId, dir, target) {
  if (G.aiOnly) return ERR('AI 대전에는 군단이 없습니다');
  var cs = corpsAll(), i, bs = [];
  if (cs.length >= CORPS_MAX) return ERR('군단은 ' + CORPS_MAX + '개까지 둘 수 있습니다');
  if (!baseIds || !baseIds.length) return ERR('맡길 거점을 고르세요');
  for (i = 0; i < baseIds.length; i++) { var b = G.bases[baseIds[i]]; if (!b || b.owner !== G.player) return ERR('내 거점만 맡길 수 있습니다'); if (baseCorps(b)) return ERR(b.n + '은(는) 이미 군단에 맡겼습니다'); bs.push(b); }
  var n = 1, used = {}; cs.forEach(function (c) { used[c.n] = 1; }); while (used[n]) n++;
  G.nextCorps = (G.nextCorps || 1);
  var cp = { id: G.nextCorps++, n: n, lead: -1, dir: 'arm', target: -1, ap: 0, t0: G.turn, note: null };
  cs.push(cp); cs.sort(function (x, y) { return x.n - y.n; });
  bs.forEach(function (b2) { b2.corps = cp.id; });
  var c2 = corpsLeadCands(cp);
  if (!c2.length) { corpsDisband(cp); return ERR('군단장을 맡을 무장이 없습니다 — 군주 말고 무장이 있는 거점을 넣으세요'); }
  cp.lead = (leadId !== undefined && leadId >= 0 && corpsLeadOk(cp, off(leadId))) ? leadId : c2[0].id;
  if (dir && dir !== 'arm') { var r = corpsSetDir(cp, dir, target); if (!r.ok) { corpsDisband(cp); return r; } }
  return { ok: true, corps: cp };
}
/* 거점을 군단에 넣는다(직할이든 다른 군단의 것이든) */
function corpsAssign(cp, baseId) {
  var b = G.bases[baseId];
  if (!b || b.owner !== G.player) return ERR('내 거점만 맡길 수 있습니다');
  if (b.corps === cp.id) return ERR('이미 이 군단의 거점입니다');
  var old = baseCorps(b);
  b.corps = cp.id;
  if (cp.dir === 'sup' && cp.target === b.id) { cp.dir = 'arm'; cp.target = -1; }      // 보내던 곳이 제 거점이 되었다
  if (old) corpsFix();
  return { ok: true };
}
/* 거점을 직할로 되돌린다. 거점이 남지 않은 군단은 해산된다 */
function corpsRelease(baseId) {
  var b = G.bases[baseId], cp = baseCorps(b);
  if (!cp) return ERR('직할 거점입니다');
  b.corps = 0;
  corpsFix();
  return { ok: true, gone: !corpsById(cp.id) };
}
function corpsTakeUnit(u) { if (!unitCorps(u)) return ERR('직할 부대입니다'); u.corps = 0; u.ai = null; return { ok: true }; }      // 부대를 직할로
function corpsDisband(cp) {
  G.bases.forEach(function (b) { if (b.corps === cp.id) b.corps = 0; });
  G.units.forEach(function (u) { if (u.corps === cp.id) { u.corps = 0; if (u.f === G.player) u.ai = null; } });
  var cs = corpsAll(), i = cs.indexOf(cp); if (i >= 0) cs.splice(i, 1);
  return { ok: true };
}
/* 뒤처리: 잃은 거점의 표시 지우기 · 거점이 없는 군단 해산 · 빈 군단장 자리 채우기 · 이룬(또는 어긋난) 방침 돌리기. 바뀐 것은 기록에 남긴다 */
function corpsFix() {
  if (!G.corps || !G.corps.length) return;
  var i, cs = G.corps.slice();
  G.bases.forEach(function (b) { if (b.corps && (b.owner !== G.player || !corpsById(b.corps))) b.corps = 0; });
  for (i = 0; i < cs.length; i++) {
    var cp = cs[i], bs = corpsBases(cp), nm = corpsName(cp), cap = bs[0];
    if (!bs.length) {
      var us = corpsUnits(cp);
      corpsDisband(cp);
      logMsg(nm + ' 해산 — 맡은 거점이 없습니다' + (us.length ? ' (부대 ' + us.length + '개는 직할로)' : ''), us.length ? us[0].c : undefined, us.length ? us[0].r : undefined, G.player, 2);
      continue;
    }
    if (!corpsLead(cp)) {
      var had = cp.lead !== undefined && cp.lead >= 0 ? off(cp.lead) : null, c2 = corpsLeadCands(cp);
      cp.lead = c2.length ? c2[0].id : -1;
      if (c2.length) logMsg(nm + ' — ' + (had ? josa(had.n, '이가') + ' 자리를 비워 ' : '') + josa(c2[0].n, '이가') + ' 군단장을 맡았다', cap.c, cap.r, G.player, 1);
      else if (had) logMsg(nm + ' — 군단장 자리가 비었습니다(맡을 무장이 없습니다)', cap.c, cap.r, G.player, 2);
    }
    var T = (cp.target !== undefined && cp.target >= 0) ? G.bases[cp.target] : null;
    if (cp.dir === 'atk' && (!T || T.owner === G.player)) {
      if (T) { logMsg(nm + ' — ' + josa(T.n, '을를') + ' 손에 넣어 방침을 군비로 돌렸다', T.c, T.r, G.player, 2); ev({ t: 'news', f: G.player, c: T.c, r: T.r, text: '<b>' + nm + '</b> — ' + josa(T.n, '을를') + ' 손에 넣었습니다. 방침을 <b>군비</b>로 돌립니다' }); }
      corpsSetDir(cp, 'arm', -1);
    } else if (cp.dir === 'sup' && (!T || T.owner !== G.player || T.corps === cp.id)) {
      logMsg(nm + ' — 보낼 거점이 없어져 방침을 군비로 돌렸다', cap.c, cap.r, G.player, 2);
      corpsSetDir(cp, 'arm', -1);
    }
  }
  G.units.forEach(function (u) { if (u.corps && (u.f !== G.player || !corpsById(u.corps))) { u.corps = 0; if (u.f === G.player) u.ai = null; } });
}
/* 군단의 차례: 시작(행동력을 채우고 한 일을 적을 준비) → ai.js 의 corpsStepper → 끝(한 일을 한 줄로 기록) */
var JOT = null;                                                   // 군단의 차례를 돌리는 동안만 배열: 그 군단이 한 일
function jot(k, b, n, x) { if (JOT) JOT.push({ k: k, b: b ? b.id : -1, n: n || 0, x: x }); }
function corpsStart(cp) {
  corpsFix();
  if (!corpsById(cp.id)) return false;
  cp.ap = Math.min(CORPS_AP.cap, (cp.ap || 0) + corpsRegen(cp));
  JOT = [];
  return true;
}
function corpsNoteText(J) {
  var d = { draft: 0, patrol: 0, train: 0, search: 0, reward: 0, trade: 0, fights: 0, sieges: 0 }, prod = {}, built = [], merged = [], joined = [], out = [], sent = 0, sentN = 0, sup = 0, supN = 0, moved = 0, i;
  for (i = 0; i < J.length; i++) {
    var e = J[i];
    if (e.k === 'draft') d.draft += e.n;
    else if (e.k === 'patrol') d.patrol++;
    else if (e.k === 'train') d.train++;
    else if (e.k === 'produce') prod[e.x] = (prod[e.x] || 0) + e.n;
    else if (e.k === 'develop') built.push(FAC[e.x].name);
    else if (e.k === 'merge') merged.push(FAC[e.x].name + ' Lv' + e.n);
    else if (e.k === 'search') d.search++;
    else if (e.k === 'recruit') { if (e.n) joined.push(off(e.x).n); }
    else if (e.k === 'reward') d.reward++;
    else if (e.k === 'trade') d.trade++;
    else if (e.k === 'move') moved += e.n;
    else if (e.k === 'deploy') { if (e.x === 'trans') { sup++; supN += e.n; } else { sent++; sentN += e.n; } }
    else if (e.k === 'act') d.fights++;
    else if (e.k === 'siege') d.sieges++;
  }
  if (sent) out.push(sent + '부대 출진(' + nf(sentN) + '명)');
  if (d.sieges) out.push('성 공격 ' + d.sieges + '회');
  if (d.fights) out.push('싸움 ' + d.fights + '회');
  if (sup) out.push('수송 ' + sup + '대(' + nf(supN) + '명)');
  if (d.draft) out.push('징병 +' + nf(d.draft));
  for (var k in prod) out.push(WEAPON_NAMES[k] + ' +' + nf(prod[k]));
  if (built.length) out.push(built.join('·') + ' 착공');
  if (merged.length) out.push(merged.join('·') + ' 합병');
  if (joined.length) out.push(joined.join('·') + ' 등용');
  if (d.train) out.push('훈련' + (d.train > 1 ? ' ' + d.train : ''));
  if (d.patrol) out.push('순찰' + (d.patrol > 1 ? ' ' + d.patrol : ''));
  if (d.search) out.push('탐색' + (d.search > 1 ? ' ' + d.search : ''));
  if (d.reward) out.push('포상 ' + d.reward);
  if (d.trade) out.push('거래' + (d.trade > 1 ? ' ' + d.trade : ''));
  if (moved) out.push('무장 ' + moved + '명 이동');
  return out.join(' · ');
}
function corpsEnd(cp) {
  var J = JOT || []; JOT = null;
  if (!corpsById(cp.id)) return;
  corpsFix();
  if (!corpsById(cp.id)) return;
  var txt = corpsNoteText(J), L = corpsLead(cp), cap = corpsBases(cp)[0];
  cp.note = { t: G.turn, s: txt, n: J.length };
  var e = { d: dateStr(), t: corpsName(cp) + ' (' + (L ? L.n + ' · ' : '') + corpsDirText(cp) + ') — ' + (txt || '한 일 없음 (행동력 ' + cp.ap + ')'), c: cap ? cap.c : undefined, r: cap ? cap.r : undefined, f: G.player, imp: 1, corps: cp.id };
  G.log.push(e); if (G.log.length > 150) G.log.shift(); REPORT.push(e);
}

"""
s = rep(s, "/* ---------- 내정 명령 ---------- */\nfunction ERR(m) { return { ok: false, msg: m }; }", CORPS + "/* ---------- 내정 명령 ---------- */\nfunction ERR(m) { return { ok: false, msg: m }; }")

# 2) 직할의 행동력은 직할 도시만 센다(AI 세력은 그대로)
s = rep(s, "  var L = off(G.factions[f].lord), v = 50 + 8 * facCities(f).length + Math.floor(L.cha / 5);",
           "  var nc = facCities(f).length;\n  if (f === G.player && !G.aiOnly && G.corps && G.corps.length) nc = directBases(f).filter(function (b) { return b.kind === 'city'; }).length;      // 군단에 맡긴 도시는 군단의 행동력으로 센다\n  var L = off(G.factions[f].lord), v = 50 + 8 * nc + Math.floor(L.cha / 5);")

# 3) 내 차례가 시작될 때 군단의 뒤처리
s = rep(s, "  var F = G.factions[f], i;\n  if (!F.alive) return;\n  if (!facAdv(f)) {", "  var F = G.factions[f], i;\n  if (!F.alive) return;\n  if (f === G.player && !G.aiOnly) corpsFix();\n  if (!facAdv(f)) {")

# 4) 턴 진행: 다른 세력보다 먼저 군단이 움직인다
s = rep(s, """function turnStepper() {
  var f = -1, st = null, stage = 0;
  return function () {
    if (G.over) return null;
    if (stage === 0) {""", """function turnStepper() {
  var f = -1, st = null, stage = 0;
  var cps = (!G.aiOnly && G.corps && G.corps.length) ? G.corps.slice() : [], ci = 0, cur = null;      // 군단(v0.10): 내 차례의 끝에, 다른 세력보다 먼저
  if (cps.length) stage = -1;
  return function () {
    if (G.over) { JOT = null; return null; }
    if (stage === -1) {
      if (st) { if (st()) return { kind: 'step', f: G.player, corps: cur.id }; st = null; corpsEnd(cur); if (G.over) return null; }
      while (ci < cps.length) {
        cur = cps[ci++];
        if (!corpsStart(cur)) continue;
        st = corpsStepper(cur);
        return { kind: 'corps', f: G.player, corps: cur.id };
      }
      stage = 0;
    }
    if (stage === 0) {""")

# 5) 거점의 주인이 바뀔 때: 군단의 부대가 차지하면 그 군단에, 아니면 표시를 지운다
s = rep(s, "  b.owner = u.f; b.troops = 0;\n  b.dur = Math.max(b.dur, Math.round(b.maxDur * 0.3));\n  if (b.kind === 'city') b.order = Math.max(20, b.order - 25);",
           "  b.owner = u.f; b.troops = 0;\n  if (b.corps || u.corps) b.corps = (u.f === G.player && !G.aiOnly && u.corps && corpsById(u.corps)) ? u.corps : 0;      // 군단의 부대가 차지한 거점은 그 군단에 든다\n  b.dur = Math.max(b.dur, Math.round(b.maxDur * 0.3));\n  if (b.kind === 'city') b.order = Math.max(20, b.order - 25);")
s = rep(s, "        b.owner = -1; b.troops = 0; b.dur = Math.max(b.dur, Math.round(b.maxDur * 0.3));", "        b.owner = -1; b.troops = 0; if (b.corps) b.corps = 0; b.dur = Math.max(b.dur, Math.round(b.maxDur * 0.3));")

# 6) 초반 보호: 사람이 두는 판에서 내 군단의 부대는 명을 받아 치는 것이므로 막지 않는다(보호가 풀리는 것은 actEv 가 전과 같이 처리한다)
s = rep(s, "  if (f === G.player) return G.turn > PEACE_ALL;                   // 플레이어 자리를 AI 가 대신 둘 때(시험·AI 대전): 다른 AI 와 같다",
           "  if (f === G.player) return !G.aiOnly || G.turn > PEACE_ALL;      // AI 대전에서 플레이어 자리를 AI 가 둘 때는 다른 AI 와 같다. 사람이 두는 판에서 이 물음이 오는 것은 내 군단의 부대뿐 — 명을 받아 치는 것이다")

# 7) 한 일 적기(JOT 가 켜져 있을 때만)
s = rep(s, "  p.fac = { t: type, lv: 1, done: false, prog: 0, need: F.build, rate: rate, hp: 300, by: os.map(function (o) { return o.id; }), t0: G.turn };",
           "  p.fac = { t: type, lv: 1, done: false, prog: 0, need: F.build, rate: rate, hp: 300, by: os.map(function (o) { return o.id; }), t0: G.turn };\n  jot('develop', b, 0, type);")
s = rep(s, "  f.lv++; b.plots[pj].fac = null;\n  markActed(os, 30);", "  f.lv++; b.plots[pj].fac = null;\n  markActed(os, 30); jot('merge', b, f.lv, f.t);")
s = rep(s, "  var n = draftAmount(b, os);\n  b.gold -= COST.draft; useAP(b.owner, AP.draft);", "  var n = draftAmount(b, os);\n  b.gold -= COST.draft; useAP(b.owner, AP.draft); jot('draft', b, n);")
s = rep(s, "  b.gold -= COST.patrol; useAP(b.owner, AP.patrol);", "  b.gold -= COST.patrol; useAP(b.owner, AP.patrol); jot('patrol', b, v);")
s = rep(s, "  useAP(b.owner, AP.train);\n  var before = b.morale; b.morale = Math.min(100, b.morale + v);", "  useAP(b.owner, AP.train); jot('train', b, v);\n  var before = b.morale; b.morale = Math.min(100, b.morale + v);")
s = rep(s, "  var n = kind === 'ram' ? 1 : produceAmount(b, kind, os);\n  b.w[kind] += n;", "  var n = kind === 'ram' ? 1 : produceAmount(b, kind, os);\n  b.w[kind] += n; jot('produce', b, n, kind);")
s = rep(s, "  if (dir === 'buy') { if (b.gold < gold) return ERR('금이 부족합니다'); b.gold -= gold; b.food += gold * 4; useAP(b.owner, AP.trade); return { ok: true, n: gold * 4 }; }",
           "  if (dir === 'buy') { if (b.gold < gold) return ERR('금이 부족합니다'); b.gold -= gold; b.food += gold * 4; useAP(b.owner, AP.trade); jot('trade', b, gold, dir); return { ok: true, n: gold * 4 }; }")
s = rep(s, "  b.food -= gold * 6; b.gold += gold; useAP(b.owner, AP.trade);\n  return { ok: true, n: gold };", "  b.food -= gold * 6; b.gold += gold; useAP(b.owner, AP.trade); jot('trade', b, gold, dir);\n  return { ok: true, n: gold };")
s = rep(s, "  if (!needAP(b.owner, AP.search)) return ERR('행동력이 부족합니다');\n  useAP(b.owner, AP.search);", "  if (!needAP(b.owner, AP.search)) return ERR('행동력이 부족합니다');\n  useAP(b.owner, AP.search); jot('search', b);")
s = rep(s, "  b.gold -= COST.reward; useAP(b.owner, AP.reward);", "  b.gold -= COST.reward; useAP(b.owner, AP.reward); jot('reward', b, 1, t.id);")
s = rep(s, "  useAP(b.owner, AP.move);\n  var t = travelTurns(b, d);", "  useAP(b.owner, AP.move); jot('move', b, os.length, destId);\n  var t = travelTurns(b, d);")
s = rep(s, "  addUnit(u);\n  ev({ t: 'deploy', id: u.id, f: u.f, n: uName(u), base: b.id, c: u.c, r: u.r });", "  addUnit(u); jot('deploy', b, troops, spec.type);\n  ev({ t: 'deploy', id: u.id, f: u.f, n: uName(u), base: b.id, c: u.c, r: u.r });")
s = rep(s, "    return { ok: true, joined: true, p: p, far: far, from: from };", "    jot('recruit', b, 1, t.id);\n    return { ok: true, joined: true, p: p, far: far, from: from };")
s = rep(s, "  return { ok: true, joined: false, p: p, far: far };", "  jot('recruit', b, 0, t.id);\n  return { ok: true, joined: false, p: p, far: far };")

# 8) 새 판 · 불러오기
s = rep(s, "units: [], fires: {}, nextUnit: 1, log: [], over: null, aiOnly: false", "units: [], fires: {}, nextUnit: 1, log: [], over: null, aiOnly: false, corps: [], nextCorps: 1")
s = rep(s, "  G = g; reindex(); REPORT = []; EVQ = [];", "  if (!g.corps) { g.corps = []; g.nextCorps = 1; }                         // v0.10: 군단(옛 저장에는 없다)\n  G = g; reindex(); REPORT = []; EVQ = []; JOT = null;\n  corpsFix();")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
