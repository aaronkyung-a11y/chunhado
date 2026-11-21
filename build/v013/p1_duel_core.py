# v0.13 (1/…): 대결의 규칙 — 일기토 · 설전  (data.js · core.js · ai.js)
#  요청(2026-11-21 15:54) "애니메이션이 들어간 일기토, 설전 모드 넣어주고, 외교 모드도 추가하면 좋을 듯"   (외교는 다음 판)
#   v0.12 까지의 일기토: 붙어 싸울 때 7% 로 저절로 벌어지고, 무력 차로 한 번에 승패가 났다(고를 것이 없었다).
#   - 대결 = 합마다 두 사람이 수를 하나씩 낸다. 세 가지 수가 가위바위보처럼 물리고, 피해는 능력의 비의 2.5제곱(일기토 = 무력, 설전 = 지력)으로 정해진다.
#       일기토: 맹공(필살을 이긴다) · 방어(맹공을 받아친다 — 피해는 0.7배) · 필살(방어를 부순다 — 1.6배, 맹공에 지면 1.3배로 맞는다)
#               같은 수: 맹공끼리 = 서로 0.6배씩 · 방어끼리 = 숨을 고른다(+6) · 필살끼리 = 무력으로 겨뤄 이긴 쪽이 1.2배
#       설전:   도리 > 이해 > 시세 > 도리(같은 수는 서로 0.5배씩)
#       기세: 합을 이기면 +1(셋까지, 하나에 피해 +12%), 지면 0.   다섯 합 안에 쓰러뜨리지 못하면 남은 힘의 비율로 판정(6%p 안이면 비김).
#       기색: 사람이 두는 쪽에는 상대가 낼 수의 낌새를 보여 준다 — 맞을 확률 = 55 + (내 읽는 능력 − 상대의 것) × 0.5 (35~85%). 읽는 능력: 일기토 = 지력, 설전 = 매력.
#   - 싸움터의 일기토: 저절로 벌어지는 것(7%)은 그대로 두되 승패를 이 규칙으로 가린다. 사람이 직접 친 공격에서 벌어지면 화면에서 수를 고른다(DUEL_DEFER).
#   - 새 명령 '일기토 신청'(unitChallenge): 옆의 적 부대에 건다. 기력 10, 행동을 쓴다. 상대가 응할지는 미리 정해 둔 주사위(턴마다) — 응할 확률 = 50 + (상대 무력 − 내 무력) × 4 (+20: 무력 85 이상 · 지력 70 미만의 맹장), 5~95%.
#       응하지 않으면 상대 부대의 기력 −5.
#   - 결과(전과 같은 크기): 진 부대 기력 −25 · 병력 −8%, 이긴 부대 기력 +10 · 주장 공적 +100. 쓰러졌으면(KO) 기력 −35 · 병력 −12% · 혼란 10일. 비기면 두 주장 공적 +30.
#   - 설전으로 등용(cmdRecruit 의 넷째 인수): 주사위 대신 설전의 승패로 정한다. 등용 확률이 10% 이상일 때만. 대상의 버티는 힘 = 100 × (1 + (60 − 확률) ÷ 100).
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- data.js
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var GAME_VERSION = 'v0.12.1';", "var GAME_VERSION = 'v0.13';")
s = rep(s, "/* 계략 */",
           "/* 대결(v0.13): 일기토 · 설전의 숫자\n"
           "   hp 버티는 힘 · rounds 합의 수 · base 한 번의 피해(능력이 같을 때) · pow 능력 비의 지수 · mom 기세 하나의 피해 덧셈 · drawGap 판정에서 비김으로 보는 차(%p)\n"
           "   read* 기색을 맞게 읽을 확률 = readBase + (내 읽는 능력 − 상대) × readK, readLo~readHi\n"
           "   싸움터: rate 저절로 벌어질 확률(%) · minWar 그때 두 주장의 무력 하한 · loss/koLoss 진 부대의 병력 손실 · morLose/koMor 기력 손실 · morWin 이긴 쪽 기력 · merit 공적 · koTurns 쓰러졌을 때 혼란(턴)\n"
           "   신청: ask 드는 기력 · refuse 응하지 않은 부대의 기력 손실 · accBase/accK/accBold 응할 확률 = accBase + (상대 무력 − 내 무력) × accK (+accBold: 맹장)\n"
           "   설전 등용: talkMin 이 확률(%)부터 걸 수 있다 · talkHp 대상의 버티는 힘 = hp × (1 + (talkHp − 확률) ÷ 100) */\n"
           "var DUEL_K = { hp: 100, rounds: 5, base: 24, pow: 2.5, mom: 0.12, momMax: 3, drawGap: 6, readBase: 55, readK: 0.5, readLo: 35, readHi: 85,\n"
           "  rate: 7, minWar: 75, loss: 0.08, koLoss: 0.12, morLose: 25, koMor: 35, morWin: 10, merit: 100, drawMerit: 30, koTurns: 1,\n"
           "  ask: 10, refuse: 5, accBase: 50, accK: 4, accBold: 20, talkMin: 10, talkHp: 60 };\n"
           "/* 수: beats = 이기는 상대 수 · mult = 이겼을 때의 피해 배수 · lose = 졌을 때 맞는 배수(없으면 1) · tie = 같은 수가 만났을 때 [방식, 값]\n"
           "   방식: both = 서로 값(배수)만큼 친다 · rest = 둘 다 값만큼 회복한다 · clash = 능력으로 겨뤄 이긴 쪽이 값(배수)으로 친다 */\n"
           "var DUEL_KIND = {\n"
           "  duel: { name: '일기토', stat: 'war', statName: '무력', read: 'int', unit: '합', order: ['atk', 'def', 'sp'],\n"
           "    moves: { atk: { name: '맹공', han: '攻', beats: 'sp', mult: 1.0, tie: ['both', 0.6], desc: '필살을 이긴다' },\n"
           "             def: { name: '방어', han: '守', beats: 'atk', mult: 0.7, tie: ['rest', 6], desc: '맹공을 받아친다' },\n"
           "             sp:  { name: '필살', han: '必', beats: 'def', mult: 1.6, lose: 1.3, tie: ['clash', 1.2], desc: '방어를 부순다 · 맹공에 약하다' } } },\n"
           "  talk: { name: '설전', stat: 'int', statName: '지력', read: 'cha', unit: '논', order: ['ri', 'gain', 'tide'],\n"
           "    moves: { ri:   { name: '도리', han: '理', beats: 'gain', mult: 1.0, tie: ['both', 0.5], desc: '이해를 이긴다' },\n"
           "             gain: { name: '이해', han: '利', beats: 'tide', mult: 1.0, tie: ['both', 0.5], desc: '시세를 이긴다' },\n"
           "             tide: { name: '시세', han: '勢', beats: 'ri', mult: 1.0, tie: ['both', 0.5], desc: '도리를 이긴다' } } }\n"
           "};\n"
           "/* 계략 */")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- core.js
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
old = s[s.index("function tryDuel(a, d, res) {"):s.index("/* 공격 가능한 대상 (현재 위치 기준) */")]
assert "win = chance(100 / (1 + Math.exp(-(la.war - ld.war) / 6)))" in old
new = r'''/* ====================== 대결(v0.13): 일기토 · 설전 ======================
   판 S = { kind, a, d(두 사람: id · n · st 능력 · rd 읽는 능력 · hp · max · mom 기세 · last 지난 수), round, max, over, win('a' | 'd' | 'draw'), ko, log[합의 기록], plan, hint }
   규칙은 여기서 끝난다 — 화면(src/duel.js)은 수를 고르게 하고 결과를 그려 보일 뿐이다. 숫자는 data.js 의 DUEL_K · DUEL_KIND */
var DUEL_DEFER = false;                                            // 켜져 있으면 싸움터의 일기토를 여기서 끝내지 않고 판만 만들어 돌려준다(res.duelS) — 사람이 수를 고른다
function duelSide(o, K, hp) { return { id: o.id, n: o.n, st: Math.max(1, o[K.stat]), rd: o[K.read], hp: hp, max: hp, mom: 0, last: null }; }
function duelNew(kind, A, D, opt) {
  var K = DUEL_KIND[kind], o = opt || {};
  return { kind: kind, a: duelSide(A, K, o.hpA || DUEL_K.hp), d: duelSide(D, K, o.hpD || DUEL_K.hp), round: 0, max: o.rounds || DUEL_K.rounds, over: false, win: null, ko: false, log: [], plan: null, hint: null };
}
function duelOther(side) { return side === 'a' ? 'd' : 'a'; }
/* AI 가 수를 고를 때의 무게. 일기토는 성미(무력이 지력보다 높을수록 거칠다)와 형세, 설전은 고르게 — 둘 다 상대가 지난 합에 낸 수를 이기는 수에 조금 더 건다 */
function duelWeights(S, side) {
  var K = DUEL_KIND[S.kind], me = S[side], op = S[duelOther(side)], o = off(me.id), w = {}, i, ids = K.order;
  if (S.kind === 'duel') {
    var bold = clamp((o.war - o.int) / 40, -1, 1);
    w.atk = 40 + 10 * bold; w.sp = 30 + 10 * bold; w.def = 30 - 20 * bold;
    if (me.hp < me.max * 0.35) w.sp += 20;                           // 몰리면 크게 건다
    if (me.mom >= 2) w.atk += 10;                                   // 기세를 탔으면 몰아친다
  } else for (i = 0; i < ids.length; i++) w[ids[i]] = 34;
  for (i = 0; i < ids.length; i++) {
    if (op.last && K.moves[ids[i]].beats === op.last) w[ids[i]] += 15;
    if (me.last === ids[i]) w[ids[i]] -= 8;                          // 같은 수를 거듭 내지는 않으려 한다
    if (w[ids[i]] < 5) w[ids[i]] = 5;
  }
  return w;
}
function duelPick(S, side) {
  var w = duelWeights(S, side), ids = DUEL_KIND[S.kind].order, tot = 0, i;
  for (i = 0; i < ids.length; i++) tot += w[ids[i]];
  var x = rnd() * tot;
  for (i = 0; i < ids.length; i++) { x -= w[ids[i]]; if (x < 0) return ids[i]; }
  return ids[ids.length - 1];
}
/* side 가 상대의 기색을 맞게 읽을 확률(%) */
function duelRead(S, side) { var me = S[side], op = S[duelOther(side)]; return Math.round(clamp(DUEL_K.readBase + (me.rd - op.rd) * DUEL_K.readK, DUEL_K.readLo, DUEL_K.readHi)); }
/* 다음 합을 준비한다: 사람이 두지 않는 쪽의 수를 미리 정하고(S.plan), 사람(human = 'a' | 'd' | null)에게 보일 기색(S.hint = { move, p })을 만든다 */
function duelPlan(S, human) {
  if (S.over) return null;
  S.plan = { a: human === 'a' ? null : duelPick(S, 'a'), d: human === 'd' ? null : duelPick(S, 'd') };
  S.hint = null;
  if (human) {
    var real = S.plan[duelOther(human)], p = duelRead(S, human), show = real;
    if (!(rnd() * 100 < p)) { var others = DUEL_KIND[S.kind].order.filter(function (m) { return m !== real; }); show = others[Math.floor(rnd() * others.length)]; }
    S.hint = { move: show, p: p };
  }
  return S.plan;
}
function duelDmg(from, to, mult) { return Math.max(1, Math.round(DUEL_K.base * Math.pow(from.st / to.st, DUEL_K.pow) * mult * (1 + DUEL_K.mom * from.mom) * (0.88 + rnd() * 0.24))); }
/* 한 합을 치른다. ma · md = 두 사람의 수. 돌려주는 값 = 그 합의 기록 { n, ma, md, win('a' | 'd' | null), how, toA, toD(받은 피해), heal, hpA, hpD } */
function duelStep(S, ma, md) {
  if (S.over) return null;
  var K = DUEL_KIND[S.kind], A = S.a, D = S.d, MA = K.moves[ma], MD = K.moves[md];
  if (!MA || !MD) return null;
  var R = { n: S.round + 1, ma: ma, md: md, win: null, how: '', toA: 0, toD: 0, heal: 0 };
  if (ma === md) {
    var T = MA.tie; R.how = T[0];
    if (T[0] === 'both') { R.toD = duelDmg(A, D, T[1]); R.toA = duelDmg(D, A, T[1]); }
    else if (T[0] === 'rest') { R.heal = T[1]; A.hp = Math.min(A.max, A.hp + T[1]); D.hp = Math.min(D.max, D.hp + T[1]); }
    else { var pa = Math.pow(A.st, 3) / (Math.pow(A.st, 3) + Math.pow(D.st, 3)); if (rnd() < pa) { R.win = 'a'; R.toD = duelDmg(A, D, T[1]); } else { R.win = 'd'; R.toA = duelDmg(D, A, T[1]); } }
  } else if (MA.beats === md) { R.win = 'a'; R.how = 'beat'; R.toD = duelDmg(A, D, MA.mult * (MD.lose || 1)); }
  else { R.win = 'd'; R.how = 'beat'; R.toA = duelDmg(D, A, MD.mult * (MA.lose || 1)); }
  A.hp -= R.toA; D.hp -= R.toD;
  if (R.win === 'a') { A.mom = Math.min(DUEL_K.momMax, A.mom + 1); D.mom = 0; } else if (R.win === 'd') { D.mom = Math.min(DUEL_K.momMax, D.mom + 1); A.mom = 0; }
  A.last = ma; D.last = md; S.round++; S.plan = null; S.hint = null;
  if (A.hp <= 0 || D.hp <= 0) {                                      // 쓰러졌다. 둘 다 쓰러지면 덜 깎인 쪽이 이긴다
    S.over = true; S.ko = true;
    S.win = A.hp <= 0 && D.hp <= 0 ? (A.hp === D.hp ? 'draw' : (A.hp > D.hp ? 'a' : 'd')) : (A.hp <= 0 ? 'd' : 'a');
    if (S.win === 'draw') S.ko = false;
    if (A.hp < 0) A.hp = 0; if (D.hp < 0) D.hp = 0;
  } else if (S.round >= S.max) {                                     // 판정: 남은 힘의 비율
    var ra = A.hp / A.max * 100, rd = D.hp / D.max * 100;
    S.over = true; S.win = Math.abs(ra - rd) < DUEL_K.drawGap ? 'draw' : (ra > rd ? 'a' : 'd');
  }
  R.hpA = A.hp; R.hpD = D.hp; S.log.push(R);
  return R;
}
function duelAuto(S) { var n = 0; while (!S.over && n++ < 99) { var p = duelPlan(S, null); duelStep(S, p.a, p.d); } return S; }

/* ---------- 싸움터의 일기토 ---------- */
function duelBattleOk(a, d) { return alive(a) && alive(d) && hdist(a.c, a.r, d.c, d.r) === 1 && a.f !== d.f; }
function tryDuel(a, d, res) {
  if (!duelBattleOk(a, d)) return;
  var la = uLeader(a), ld = uLeader(d);
  if (la.war < DUEL_K.minWar || ld.war < DUEL_K.minWar || !chance(DUEL_K.rate)) return;
  duelBattle(a, d, res);
}
/* 두 부대의 주장이 일기토를 벌인다. DUEL_DEFER 가 켜져 있으면 판만 만들어 res.duelS 로 돌려준다(끝나면 화면이 duelFinish 를 부른다) */
function duelBattle(a, d, res) {
  var S = duelNew('duel', uLeader(a), uLeader(d));
  S.ua = a.id; S.ud = d.id;
  if (DUEL_DEFER) { res.duelS = S; return S; }
  duelAuto(S); duelFinish(S, res);
  res.duelRec = duelRecOf(S);                                        // 화면이 처음부터 다시 그려 보일 수 있게(저장되지 않는다)
  return S;
}
function duelRecOf(S) { return { kind: S.kind, a: { id: S.a.id, st: S.a.st, max: S.a.max }, d: { id: S.d.id, st: S.d.st, max: S.d.max }, log: S.log, win: S.win, ko: S.ko, max: S.max }; }
/* 끝난 일기토의 결과를 부대에 입힌다(한 번만). res 가 있으면 res.duel 에 요약을 붙이고, 부대가 무너졌으면 res.killed · res.selfDead 도 */
function duelFinish(S, res) {
  if (!S || !S.over || S.done || S.kind !== 'duel') return null;
  S.done = true;
  var a = UMAP[S.ua], d = UMAP[S.ud], la = off(S.a.id), ld = off(S.d.id), out = { a: la.n, d: ld.n, win: S.win === 'a', draw: S.win === 'draw', ko: S.ko, rounds: S.round, loss: 0 };
  if (res) res.duel = out;
  if (!a || !d) return out;                                          // 그사이 부대가 사라졌다(일어나지 않아야 하지만 멈추지는 않는다)
  if (S.win === 'draw') {
    la.merit += DUEL_K.drawMerit; ld.merit += DUEL_K.drawMerit;
    logMsg('일기토! ' + la.n + ' 대 ' + ld.n + ' — ' + S.round + '합을 겨루고 비김', d.c, d.r, -1, (a.f === G.player || d.f === G.player) ? 2 : 0);
    return out;
  }
  var Wn = S.win === 'a' ? a : d, Ls = S.win === 'a' ? d : a, wl = S.win === 'a' ? la : ld;
  out.loss = Math.round(Ls.troops * (S.ko ? DUEL_K.koLoss : DUEL_K.loss));
  Ls.morale = Math.max(0, Ls.morale - (S.ko ? DUEL_K.koMor : DUEL_K.morLose)); Wn.morale = Math.min(100, Wn.morale + DUEL_K.morWin);
  wl.merit += DUEL_K.merit;
  logMsg('일기토! ' + la.n + ' 대 ' + ld.n + ' — ' + wl.n + (S.ko ? ' 승(' + S.round + '합 만에 쓰러뜨림)' : ' 승'), d.c, d.r, -1, (a.f === G.player || d.f === G.player) ? 2 : 0);
  var dead = hurtUnit(Ls, out.loss, Wn.f, Wn);
  if (dead) { if (res) { if (Ls === a) res.selfDead = true; else res.killed = true; } }
  else if (S.ko && !uHas(Ls, '통찰') && !uHas(Ls, '명경')) { setStatus(Ls, 'confuse', DUEL_K.koTurns); out.confused = true; }
  return out;
}
/* ---------- 일기토 신청(v0.13) ---------- */
function challengeTargets(u) {
  var out = [], ns = nbrs(u.c, u.r);
  for (var i = 0; i < ns.length; i++) { var o = UAT[K(ns[i][0], ns[i][1])]; if (o && o.f !== u.f && !o.status) out.push({ kind: 'unit', u: o, c: o.c, r: o.r }); }
  return out;
}
function challengeChance(u, d) {                                    // 상대가 응할 확률(%)
  var la = uLeader(u), ld = uLeader(d), bold = ld.war >= 85 && ld.int < 70;
  return Math.round(clamp(DUEL_K.accBase + (ld.war - la.war) * DUEL_K.accK + (bold ? DUEL_K.accBold : 0), 5, 95));
}
function challengeRoll(u, d) { return omenRoll('duel|' + u.id + '|' + d.id); }      // 미리 정해 둔 결과(턴마다): 같은 턴에 다시 물어도 같다
function unitChallenge0(u, t) {
  if (u.done) return ERR('이미 행동을 마쳤습니다');
  if (u.status) return ERR('명령을 내릴 수 없는 부대입니다');
  var d = t && t.u;
  if (!d || !duelBattleOk(u, d)) return ERR('옆에 붙은 적 부대에만 걸 수 있습니다');
  if (d.status) return ERR('어지러운 부대는 응할 수 없습니다');
  if (u.morale < DUEL_K.ask) return ERR('기력이 부족합니다 (' + DUEL_K.ask + ' 필요)');
  var p = challengeChance(u, d), yes = challengeRoll(u, d) < p;
  u.morale -= DUEL_K.ask; u.done = true; u.ox = -1;
  var res = { ok: true, kind: 'challenge', c: d.c, r: d.r, ac: u.c, ar: u.r, tname: uName(d), p: p, accepted: yes };
  if (!yes) { d.morale = Math.max(0, d.morale - DUEL_K.refuse); res.mor = DUEL_K.refuse; logMsg(uLeader(u).n + '의 일기토 신청을 ' + josa(uLeader(d).n, '이가') + ' 받지 않음', d.c, d.r, -1, 0); return res; }
  duelBattle(u, d, res);
  return res;
}
function unitChallenge(u, t) { var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t); return actEv(u, t, unitChallenge0(u, t), f, n, ac, ar, tf, -1); }
/* ---------- 설전으로 등용(v0.13) ---------- */
function talkRecruitOk(b, o, t) { var p = recruitChance(b, o, t); return p >= DUEL_K.talkMin && p < 100; }
function talkRecruitNew(b, o, t) {
  var p = recruitChance(b, o, t), S = duelNew('talk', o, t, { hpD: Math.round(DUEL_K.hp * (1 + (DUEL_K.talkHp - p) / 100)) });
  S.rb = b.id; S.ro = o.id; S.rt = t.id; S.rp = p;
  return S;
}

'''
s = s.replace(old, new)
# 등용: 넷째 인수 S(끝난 설전)가 있으면 주사위 대신 그 승패로
s = rep(s, "function cmdRecruit(b, id, tid) {", "function cmdRecruit(b, id, tid, S) {")
s = rep(s, "  if (!needAP(b.owner, AP.recruit)) return ERR('행동력이 부족합니다');\n  useAP(b.owner, AP.recruit);\n  var o = os[0]; markActed(os, 15);\n"
           "  var p = recruitChance(b, o, t), okR = recruitRoll(t) < p;             // 미리 정해 둔 결과(군사가 미리 말해 줄 수 있다)\n",
           "  if (S && (S.kind !== 'talk' || !S.over || S.used || S.rb !== b.id || S.ro !== id || S.rt !== tid)) return ERR('설전의 결과가 맞지 않습니다');\n"
           "  if (!needAP(b.owner, AP.recruit)) return ERR('행동력이 부족합니다');\n  useAP(b.owner, AP.recruit);\n  var o = os[0]; markActed(os, 15);\n"
           "  var p = recruitChance(b, o, t), okR = S ? S.win === 'a' : recruitRoll(t) < p;      // 미리 정해 둔 결과(군사가 미리 말해 줄 수 있다). 설전을 벌였으면 그 승패(v0.13)\n"
           "  if (S) S.used = true;\n")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ai.js
p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "if (res.duel) txt += ' · 일기토 ' + (res.duel.win ? res.duel.a : res.duel.d) + ' 승';",
           "if (res.duel) txt += ' · 일기토 ' + (res.duel.draw ? '비김' : (res.duel.win ? res.duel.a : res.duel.d) + ' 승');")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
