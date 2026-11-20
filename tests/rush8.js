// 초반 압박 재기: 한 세력을 '플레이어 자리'에 두고(조작은 AI) 그 세력의 거점·시설이 처음 공격받는 턴, 처음 성을 잃는 턴, 망하는 턴을 센다.
//   node tests/rush8.js [턴=72] [씨앗 수=5]      SRC=<폴더> 로 다른 판과 견줌.   FACS=2,6,7 로 세력을 고름(기본: 시작 병력이 1만 미만인 일곱 세력)
//   PASSIVE=1 이면 그 세력은 아무것도 하지 않는다(처음 하는 사람이 손을 놓고 있는 경우에 가깝다)
//   v0.8.1부터: 초반 보호(G.peace)가 지켜지는지도 센다 — '보호 중인데, 내가 먼저 치지 않은 세력이 내 거점·시설을 친 횟수'(어김)가 0 이어야 한다. 어김이 있으면 종료 코드 1
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const turns = +(process.argv[2] || 72), nseed = +(process.argv[3] || 5), PASSIVE = !!process.env.PASSIVE;
function run(fac, seed) {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
  ctx.ME = fac; ctx.PASSIVE = PASSIVE;
  vm.runInContext(`
    var R = { firstMarch: 0, firstHit: 0, firstLoss: 0, dead: 0, by: '', hitTroops: 0, myTroops0: 0, viol: 0, until: 0, atEnd: 0, hits: 0 }, ROUND = 0;
    var _ua = unitAttack0; unitAttack0 = function (u, t) {
      var mine = (t.kind === 'base' || t.kind === 'fac') && t.b && t.b.owner === ME, uf = u.f;
      var prot = mine && G.peace && G.turn < G.peace.until && !G.peace.broken[uf];
      var r = _ua(u, t);
      if (r && r.ok && mine) {
        R.hits++;
        if (prot) R.viol++;
        if (!R.firstHit) { R.firstHit = ROUND + 1; R.by = facName(uf); R.myTroopsAtHit = t.b.troops; }
      }
      return r;
    };
    var _cb = captureBase; captureBase = function (b, u) { var own = b.owner, prot = own === ME && G.peace && G.turn < G.peace.until && u && !G.peace.broken[u.f]; var r = _cb(b, u); if (own === ME) { if (prot) R.viol++; if (!R.firstLoss) R.firstLoss = ROUND + 1; } return r; };
    var _ad = aiDeploy; aiDeploy = function (b, leader, subs, troops, turns, ai, toward, forceType) { var u = _ad(b, leader, subs, troops, turns, ai, toward, forceType); if (u && !R.firstMarch && b.owner !== ME && ai && ai.mode === 'attack' && G.bases[ai.target] && G.bases[ai.target].owner === ME) R.firstMarch = ROUND + 1; return u; };
    if (PASSIVE) { var _ap = aiPhase; aiPhase = function (f) { if (f === ME) return; return _ap(f); }; var _st = typeof aiPhaseStepper === 'function' ? aiPhaseStepper : null; if (_st) aiPhaseStepper = function (f) { if (f === ME) return function () { return false; }; return _st(f); }; }
  `, ctx);
  ctx.newGame(fac, seed); ctx.G.aiOnly = true;
  ctx.R.myTroops0 = ctx.G.bases.filter(b => b.owner === fac).reduce((s, b) => s + b.troops, 0);
  ctx.R.until = ctx.G.peace ? ctx.G.peace.until : 1;
  for (let t = 0; t < turns; t++) {
    ctx.ROUND = t; ctx.endTurn();
    if (ctx.G.turn === ctx.R.until) ctx.R.atEnd = ctx.G.bases.filter(b => b.owner === fac).reduce((s, b) => s + b.troops, 0) + ctx.G.units.filter(u => u.f === fac).reduce((s, u) => s + u.troops, 0);
    if (!ctx.G.factions[fac].alive) { ctx.R.dead = t + 1; break; } if (ctx.G.over) break;
  }
  ctx.R.name = ctx.G.factions[fac].name;
  ctx.R.cities = ctx.G.bases.filter(b => b.owner === fac && b.kind === 'city').length;
  return ctx.R;
}
const list = (process.env.FACS || '2,6,7,8,10,12,13').split(',').map(Number);
console.log('src', path.basename(root), '| turns', turns, '| seeds', nseed, PASSIVE ? '| 그 세력은 손을 놓음' : '| 그 세력도 AI 가 둠');
console.log('세력      시작병력 보호끝  보호 끝날 때 병력           나를 향한 첫 출진(턴)   첫 피격(턴)            첫 함락(턴)            멸망(턴)          망한 판   끝날 때 성 수');
let tot = { hit: [], dead: 0, n: 0, loss: [], viol: 0, early: 0 };
for (const f of list) {
  const rs = []; for (let s = 1; s <= nseed; s++) rs.push(run(f, s * 101));
  const col = k => rs.map(r => r[k] || '-').join(',');
  const dead = rs.filter(r => r.dead).length;
  rs.forEach(r => { tot.n++; tot.viol += r.viol; if (r.firstHit) { tot.hit.push(r.firstHit); if (r.firstHit < r.until) tot.early++; } if (r.dead) tot.dead++; if (r.firstLoss) tot.loss.push(r.firstLoss); });
  console.log((rs[0].name + '        ').slice(0, 6), String(rs[0].myTroops0).padStart(7), String(rs[0].until).padStart(5), ' ', col('atEnd').padEnd(28), col('firstMarch').padEnd(22), col('firstHit').padEnd(22), col('firstLoss').padEnd(22), col('dead').padEnd(18), dead + '/' + nseed, '    ', rs.map(r => r.cities).join(','), ' 친 쪽:', [...new Set(rs.map(r => r.by).filter(Boolean))].join('·'));
}
const med = a => { if (!a.length) return '-'; const b = a.slice().sort((x, y) => x - y); return b[Math.floor((b.length - 1) / 2)]; };
console.log('합계: ' + tot.n + '판 가운데 공격받은 판 ' + tot.hit.length + ' (첫 피격 턴의 가운데값 ' + med(tot.hit) + ', 12턴 안 ' + tot.hit.filter(x => x <= 12).length + '판, 6턴 안 ' + tot.hit.filter(x => x <= 6).length + '판) · 거점(성·관문)을 잃은 판 ' + tot.loss.length + ' (가운데값 ' + med(tot.loss) + '턴) · 망한 판 ' + tot.dead);
console.log('보호가 끝나기 전에 맞은 판 ' + tot.early + ' (그 세력이 먼저 친 상대에게 맞은 것은 어김이 아니다) · 보호 어김 ' + tot.viol + '회');
if (tot.viol) { console.log('FAIL: 보호 중인 거점·시설이 공격받음'); process.exit(1); }
