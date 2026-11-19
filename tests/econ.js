const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
ctx.newGame(0, +(process.argv[3] || 3)); ctx.G.aiOnly = true;
const turns = +(process.argv[2] || 108);
for (let t = 0; t < turns; t++) ctx.endTurn();
vm.runInContext(`
console.log(dateStr());
G.bases.filter(function(b){return b.kind==='city' && b.owner>=0}).slice(0,60).forEach(function(b){
  var n = aiCountFac(b), fs = Object.keys(n).filter(function(k){return n[k]}).map(function(k){return FAC[k].g + n[k]}).join('');
  console.log((b.n+'    ').slice(0,3), (facName(b.owner)+'    ').slice(0,4), 'gold', b.gold, 'inc', goldIncome(b), 'food', b.food, 'finc', foodIncome(b), 'troops', b.troops, 'mor', b.morale, 'ord', b.order, 'w', b.w.spear, b.w.halberd, b.w.bow, b.w.horse, b.w.ram, 'fac', fs, 'off', baseOfficers(b).length, 'ap', G.factions[b.owner].ap);
});
console.log('units', G.units.map(function(u){return facName(u.f)+':'+uName(u)+':'+UNIT_TYPES[u.type].g+u.troops+(u.ai?'/'+u.ai.mode+(u.ai.target!==undefined?'>'+G.bases[u.ai.target].n:''):'')}).join(' '));
`, ctx);
