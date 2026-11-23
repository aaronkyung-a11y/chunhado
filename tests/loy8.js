// v0.8 충성과 인연 규칙 확인:  node tests/loy8.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '..', process.env.SRC || 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of 'mapdata.js,roster.js,data.js,core.js,ai.js'.split(',')) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
vm.runInContext(`
var FAILS = [], N = 0;
function chk(name, cond, info) { N++; console.log((cond ? '  ok   ' : '  FAIL ') + name + (info !== undefined ? '  [' + info + ']' : '')); if (!cond) FAILS.push(name); }
function by(n) { for (var i = 0; i < G.officers.length; i++) if (G.officers[i].n === n) return G.officers[i]; return null; }
function quarter() { var m0 = G.month; do { endTurn(); } while (!(G.xun === 0 && (G.month === 1 || G.month === 4 || G.month === 7 || G.month === 10) && G.month !== m0)); }
// 1) 표의 이름이 모두 명부에 있는가
var names = {}, lords = {}; SCENARIO.officers.forEach(function (o) { names[o.n] = 1; }); SCENARIO.factions.forEach(function (f) { lords[f.n] = 1; });
var bad = []; Object.keys(BONDS).forEach(function (l) { if (!lords[l]) bad.push(l); Object.keys(BONDS[l]).forEach(function (n) { if (!names[n]) bad.push(l + ':' + n); }); });
chk('인연 표의 이름이 모두 명부에 있다', !bad.length, bad.join(' '));
newGame(2, 11); G.aiOnly = true;                       // 유비로 시작(AI 가 대신 둔다)
// 2) 시작 충성
var os = G.officers.filter(function (o) { return o.f >= 0 && o.st !== 'hidden' && !isLord(o); }), bonded = os.filter(bondOf), rest = os.filter(function (o) { return !bondOf(o); });
chk('인연이 있는 무장은 모두 충성 100 (' + bonded.length + '명)', bonded.every(function (o) { return o.loy === 100; }));
chk('그 밖의 무장은 80~98 (' + rest.length + '명)', rest.every(function (o) { return o.loy >= 80 && o.loy <= 98 && o.loy === loyNat(o); }), Math.min.apply(null, rest.map(function (o) { return o.loy; })) + '~' + Math.max.apply(null, rest.map(function (o) { return o.loy; })));
chk('관우·장비는 유비의 의형제', bondOf(by('관우')) === '의형제' && bondOf(by('장비')) === '의형제' && by('관우').loy === 100);
chk('군주에게는 인연을 매기지 않는다', bondOf(by('유비')) === null && by('유비').loy === 100);
chk('조운은 공손찬 밑에서는 인연이 없다', bondOf(by('조운')) === null && bondWith(by('조운'), by('유비').f) === '심복');
var avg = os.reduce(function (s, o) { return s + o.loy; }, 0) / os.length;
chk('평균 충성 90 이상', avg >= 90, avg.toFixed(1));
// 군주 매력이 높을수록 자리 잡는 값이 높다: 같은 사람을 두 세력에 놓아 본다
var t = rest[0], f0 = t.f, hi = -1, lo = -1; G.factions.forEach(function (F, i) { var c = off(F.lord).cha; if (hi < 0 || c > off(G.factions[hi].lord).cha) hi = i; if (lo < 0 || c < off(G.factions[lo].lord).cha) lo = i; });
t.f = hi; var nh = loyNat(t); t.f = lo; var nl = loyNat(t); t.f = f0;
chk('군주 매력이 높으면 자리 잡는 값도 높다', nh > nl, facName(hi) + ' ' + nh + ' > ' + facName(lo) + ' ' + nl);
// 3) 흐름: 포상으로 올린 몫은 빠지고, 낮은 값은 오른다. 인연은 그대로.  (AI 가 3년을 두는 동안 사로잡히거나 세력이 바뀐 무장은 빼고 센다)
var ups = rest.filter(function (o, i) { return i % 3 === 0 && loyNat(o) <= 92; }), downs = rest.filter(function (o, i) { return i % 3 === 1; }), g = by('관우');
ups.forEach(function (o) { o._f = o.f; o._n = loyNat(o); o.loy = o._n + 6; o._l = o.loy; });
downs.forEach(function (o) { o._f = o.f; o._n = loyNat(o); o.loy = o._n - 10; o._l = o.loy; });
g.loy = 60;
if (typeof aiPoach === 'function') aiPoach = function () {};      // v0.9: 다른 세력 무장 등용(거절하면 충성 +3, 떠나면 남은 무장 +2)은 여기서 보는 '분기마다의 흐름'과 별개라 꺼 둔다 — 그쪽은 tests/adv9.js
// v0.9.1: 사로잡혔다가 남의 세력에 등용되고, 다시 사로잡혀 제 세력으로 돌아온 무장은 '그대로 있던 무장'이 아니다(등용되면 충성이 70~85 로 새로 매겨진다).
//         0.9.1 의 판에서 손관이 도겸 → 손책(196년 2월) → 도겸(196년 10월)으로 돌아와 끝날 때 세력은 같고 충성은 자리 잡는 값 아래였다 — 등용된 적이 있는 무장은 뺀다
var _cr8 = cmdRecruit; cmdRecruit = function (b, id, tid) { var t = off(tid), r = _cr8.apply(this, arguments); if (r && r.ok && r.joined && t) t._moved = true; return r; };
function stay(o) { return o.f === o._f && o.st === 'active' && !o._moved; }
quarter();
chk('인연 무장은 분기가 바뀌면 100 으로 돌아온다', by('관우').loy === 100 || by('관우').f !== by('유비').f, by('관우').loy);
var d1 = downs.filter(stay);
var rew = d1.filter(function (o) { return o.loy > o._l + 2; });         // AI 는 충성 72 미만인 무장을 포상한다(+8~12) — 그 무장들은 2 넘게 오른다
chk('낮은 충성은 분기마다 2씩 오른다 (' + d1.length + '명, 그중 AI 가 포상한 ' + rew.length + '명은 더 오름)', d1.length >= 20 && d1.every(function (o) { return o.loy === o._l + 2 || (o._l < 72 && o.loy >= o._l + 2 + 8); }), d1.filter(function (o) { return o.loy !== o._l + 2; }).slice(0, 4).map(function (o) { return o._l + '→' + o.loy; }).join(' '));
var u1 = ups.filter(stay);
chk('높은 충성은 한 분기에 많아야 1 내린다 (' + u1.length + '명)', u1.length >= 15 && u1.every(function (o) { return o.loy === o._l || o.loy === o._l - 1; }) && u1.some(function (o) { return o.loy === o._l - 1; }), u1.filter(function (o) { return o.loy < o._l; }).length + '명이 내림');
for (var q = 0; q < 11; q++) quarter();
var d3 = downs.filter(stay), u3 = ups.filter(stay);
chk('3년 뒤: 낮았던 무장은 자리 잡는 값에 닿아 멈췄다 (' + d3.length + '명)', d3.length >= 10 && d3.every(function (o) { return o.loy === loyNat(o); }), d3.slice(0, 3).map(function (o) { return o._l + '→' + o.loy + '/' + loyNat(o); }).join(' '));
var drop = u3.reduce(function (s2, o) { return s2 + (o._l - o.loy); }, 0) / Math.max(1, u3.length);
chk('3년 뒤: 포상으로 올린 몫은 줄되 자리 잡는 값 아래로는 안 내려간다 (' + u3.length + '명, 평균 -' + drop.toFixed(1) + ')', u3.length >= 8 && u3.every(function (o) { return o.loy <= o._l && o.loy >= loyNat(o); }) && drop >= 2 && drop <= 6, u3.slice(0, 3).map(function (o) { return o._l + '→' + o.loy + '/' + loyNat(o); }).join(' '));
var low = G.officers.filter(function (o) { return o.f >= 0 && o.st === 'active' && !isLord(o) && o.loy < 70; });
chk('3년 뒤: 충성 70 아래인 무장이 없다', !low.length, low.slice(0, 5).map(function (o) { return o.n + o.loy; }).join(' '));
var bl = G.officers.filter(function (o) { return o.f >= 0 && o.st === 'active' && bondOf(o) && o.loy !== 100; });
chk('3년 뒤: 인연 무장은 모두 100', !bl.length, bl.slice(0, 5).map(function (o) { return o.n + o.loy; }).join(' '));
// 4) 등용
newGame(2, 5);
var L = by('유비'), home = G.bases[L.loc], rec = L, zy = by('조운'), fr = G.officers.filter(function (o) { return o.st === 'free'; })[0] || null;
// 재야로 만든 조운(유비와 심복 사이)과 보통 재야 무장을 견준다
zy.f = -1; zy.st = 'free'; zy.loc = home.id; zy.unit = null;
var other = by('장료'); var of0 = other.f; other.f = -1; other.st = 'free'; other.loc = home.id;
var pz = recruitChance(home, rec, zy), po = recruitChance(home, rec, other);
chk('내 군주와 인연이 있는 재야 무장은 등용 확률 +30', pz === Math.min(RECRUIT.max, po + 30), po + ' → ' + pz);      // v0.21: 위 끝이 95 → RECRUIT.max(88)
G.factions[home.owner].ap = 999; var joined = false;
for (var k = 0; k < 60 && !joined; k++) { rec.acted = false; var r = cmdRecruit(home, rec.id, zy.id); G.factions[home.owner].ap = 999; joined = r.ok && r.joined; G.turn++; }      // v0.9: 한 무장에게는 한 턴에 한 번만 권할 수 있고 결과가 턴마다 정해져 있으므로, 턴을 넘겨 가며 권한다
chk('인연이 있는 무장은 등용되면 바로 충성 100', joined && zy.loy === 100, zy.loy);
for (k = 0, joined = false; k < 200 && !joined; k++) { rec.acted = false; r = cmdRecruit(home, rec.id, other.id); G.factions[home.owner].ap = 999; joined = r.ok && r.joined; G.turn++; }
chk('보통 무장은 등용되면 70~85 에서 시작', joined && other.loy >= 70 && other.loy <= 85, other.loy);
// 포로: 주군과 인연이 있으면 5% 까지
var xh = by('하후돈'), cc = by('조조');
xh.st = 'captive'; xh.capF = home.owner; xh.loc = home.id; xh.unit = null; home.captives.push(xh.id);
var xu = by('우금'); xu.st = 'captive'; xu.capF = home.owner; xu.loc = home.id; xu.unit = null; home.captives.push(xu.id);
var ph = recruitChance(home, rec, xh), pu = recruitChance(home, rec, xu);
chk('주군과 인연이 있는 포로는 5% 까지(하후돈)', ph <= 5, ph); chk('인연이 없는 포로는 그보다 높다(우금)', pu > ph, pu);
G.factions[cc.f].alive = false; var ph2 = recruitChance(home, rec, xh); G.factions[cc.f].alive = true;
chk('주군의 세력이 사라지면 그 제한이 풀린다', ph2 > 5, ph2);
// 5) 저장: 옛 저장(인연 무장의 충성이 낮게 적힌)을 열면 100 이 된다. 부지도 채워진다
newGame(0, 3);
var gz = by('하후돈'); gz.loy = 81; var nb = G.bases.filter(function (x) { return x.kind === 'city'; })[0], full = nb.plots.length; nb.plots.length = full - 4;
var sv = serialize(); var okL = deserialize(sv);
chk('저장을 다시 열면 인연 무장은 100', okL && by('하후돈').loy === 100, by('하후돈').loy);
var nb2 = G.bases[nb.id];
chk('옛 저장의 모자란 부지가 채워진다', nb2.plots.length === full && nb2.plots[full - 1].fac === null && PAT[K(nb2.plots[full - 1].c, nb2.plots[full - 1].r)].i === full - 1, nb2.plots.length + ' / ' + full);
console.log('\\n' + N + '항목, 어긋난 것 ' + FAILS.length + '건');
`, ctx);
process.exit(ctx.FAILS.length ? 1 : 0);
