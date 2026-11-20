# v0.8 돈과 병량: "보통 돈이 없어서 뭘 할 수가 없는 것 같다. 비용이 전반적으로 너무 크다" / "병량도 너무 적게 늘어난다. 분기별인데"
#  재 본 것(v0.7, 조조 시작): 금 수입 389/월(130/턴) 대 징병·생산 300·시설 200~400, 행동력 92/턴(4~6번) → 금은 0.4번 치. 수확 2,188/분기 대 주둔군 16,000명 소모 2,403/분기.
#  고침: 수입 약 2배(성 기본 금 ×2.3~2.4, 시장 ×1.2, 성 기본 병량 ×2.7~2.9, 농장 ×1.2 — 부지가 1.6배로 늘어 시설 수가 늘므로 한 곳당 수입은 조금만), 비용 약 2/3. 비용은 COST 표 한 곳에서.
import io, re
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
i0 = s.index("/* 시설 */"); i1 = s.index("var MAX_DUR")
s = s[:i0] + """/* 수입과 비용 — v0.8: 수입은 약 2배, 비용은 약 2/3 로. 부지가 1.6배로 늘었으므로(6·8·10 → 10·13·16) 올린 몫은 주로 성의 기본 수입에 두었다(시장·농장 한 곳의 수입은 1.2배).
   (v0.7: 성 기본 금 L300 M220 S150 · 시장 150/250/370 · 성 기본 병량 L1500 M1000 S700 · 농장 1500/2500/3600 ·
          징병 300 · 순찰 100 · 생산 300 · 충차 600(발명 300) · 포상 100 · 합병 150×레벨 · 시설 200~400) */
var MARKET_INC = [0, 180, 300, 440];
var FARM_INC = [0, 1800, 3000, 4400];
var LV_MUL = [0, 1.0, 1.3, 1.6];
var BASE_GOLD = { L: 700, M: 520, S: 360 };
var BASE_FOOD = { L: 4000, M: 2900, S: 2000 };
var COST = { draft: 200, patrol: 60, produce: 200, ram: 400, ramInv: 200, reward: 60, merge: 100 };   // merge 는 레벨마다
/* 시설 */
var FAC = {
  market:   { name: '시장',   g: '시', color: '#c9972b', cost: 140, build: 300, desc: '매월 금 수입 +' + MARKET_INC[1] + ' (Lv2 ' + MARKET_INC[2] + ', Lv3 ' + MARKET_INC[3] + ')' },
  farm:     { name: '농장',   g: '농', color: '#6a9a3b', cost: 140, build: 300, desc: '분기마다 병량 +' + FARM_INC[1] + ' (Lv2 ' + FARM_INC[2] + ', Lv3 ' + FARM_INC[3] + ')' },
  barracks: { name: '병영',   g: '병', color: '#a04a3a', cost: 200, build: 400, desc: '징병 가능. 레벨이 오르면 징병량 증가' },
  smithy:   { name: '대장간', g: '야', color: '#5d6d7e', cost: 200, build: 400, desc: '창·극·노 생산. 레벨이 오르면 생산량 증가' },
  stable:   { name: '마구간', g: '마', color: '#8e6b3e', cost: 200, build: 400, desc: '군마 생산' },
  workshop: { name: '공방',   g: '공', color: '#6c5b7b', cost: 270, build: 500, desc: '충차 생산' },
  mint:     { name: '조폐',   g: '폐', color: '#d4b04a', cost: 200, build: 400, desc: '인접한 시장의 수입 +50%' },
  granary:  { name: '곡창',   g: '곡', color: '#9bb04a', cost: 200, build: 400, desc: '인접한 농장의 수입 +50%' }
};
var FAC_ORDER = ['market', 'farm', 'barracks', 'smithy', 'stable', 'workshop', 'mint', 'granary'];
""" + s[i1:]
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "  var f = b.plots[pi].fac, cost = 150 * f.lv;", "  var f = b.plots[pi].fac, cost = COST.merge * f.lv;")
s = rep(s, "  if (b.gold < 300) return ERR('금이 부족합니다 (300 필요)');", "  if (b.gold < COST.draft) return ERR('금이 부족합니다 (' + COST.draft + ' 필요)');")
s = rep(s, "  b.gold -= 300; useAP(b.owner, AP.draft);", "  b.gold -= COST.draft; useAP(b.owner, AP.draft);")
s = rep(s, "  if (b.gold < 100) return ERR('금이 부족합니다 (100 필요)');\n  if (!needAP(b.owner, AP.patrol))", "  if (b.gold < COST.patrol) return ERR('금이 부족합니다 (' + COST.patrol + ' 필요)');\n  if (!needAP(b.owner, AP.patrol))")
s = rep(s, "  b.gold -= 100; useAP(b.owner, AP.patrol);", "  b.gold -= COST.patrol; useAP(b.owner, AP.patrol);")
s = rep(s, "  var cost = kind === 'ram' ? (anyHas(os, '발명') ? 300 : 600) : 300;", "  var cost = kind === 'ram' ? (anyHas(os, '발명') ? COST.ramInv : COST.ram) : COST.produce;")
s = rep(s, "  if (b.gold < 100) return ERR('금이 부족합니다 (100 필요)');\n  if (!needAP(b.owner, AP.reward))", "  if (b.gold < COST.reward) return ERR('금이 부족합니다 (' + COST.reward + ' 필요)');\n  if (!needAP(b.owner, AP.reward))")
s = rep(s, "  b.gold -= 100; useAP(b.owner, AP.reward);", "  b.gold -= COST.reward; useAP(b.owner, AP.reward);")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "if (os[i].loy < 72 && !isLord(os[i]) && b.gold >= 250 && F.ap >= AP.reward)", "if (os[i].loy < 72 && !isLord(os[i]) && b.gold >= COST.reward + 110 && F.ap >= AP.reward)")
s = rep(s, "if (b.order < 60 && b.gold >= 150 && F.ap >= AP.patrol)", "if (b.order < 60 && b.gold >= COST.patrol + 40 && F.ap >= AP.patrol)")
s = rep(s, "if (pi < 0 || b.gold < FAC[type].cost + 100) break;", "if (pi < 0 || b.gold < FAC[type].cost + 70) break;")
s = rep(s, "if (F.ap >= AP.merge + 10 && b.gold >= 600 && !b.plots.some(", "if (F.ap >= AP.merge + 10 && b.gold >= COST.merge * 2 + 200 && !b.plots.some(")
s = rep(s, "if (hasFac(b, 'barracks') && b.gold >= 420 && b.order >= 55", "if (hasFac(b, 'barracks') && b.gold >= COST.draft + 80 && b.order >= 55")
s = rep(s, "    if (b.gold >= 380 && F.ap >= AP.produce) {", "    if (b.gold >= COST.produce + 50 && F.ap >= AP.produce) {")
s = rep(s, "else if (hasFac(b, 'workshop') && b.w.ram < 1 && b.gold >= 900) cmdProduce(b, 'ram', [os[0].id]);", "else if (hasFac(b, 'workshop') && b.w.ram < 1 && b.gold >= COST.ram + 200) cmdProduce(b, 'ram', [os[0].id]);")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "cmd('draft', '징병', '금 300 · 행 ' + AP.draft, false, !hasFac(b, 'barracks')) + cmd('patrol', '순찰', '금 100 · 행 ' + AP.patrol)", "cmd('draft', '징병', '금 ' + COST.draft + ' · 행 ' + AP.draft, false, !hasFac(b, 'barracks')) + cmd('patrol', '순찰', '금 ' + COST.patrol + ' · 행 ' + AP.patrol)")
s = rep(s, "cmd('produce', '생산', '금 300~ · 행 ' + AP.produce,", "cmd('produce', '생산', '금 ' + COST.produce + '~ · 행 ' + AP.produce,")
s = rep(s, " + ' · 금 300'; } },\n", " + ' · 금 ' + COST.draft; } },\n")
s = rep(s, "return '치안 <b>+' + Math.min(v, 100 - b.order) + '</b> · 금 100'; } },", "return '치안 <b>+' + Math.min(v, 100 - b.order) + '</b> · 금 ' + COST.patrol; } },")
s = rep(s, "<p class=\"note\">창·극·노·군마는 금 300, 충차는 금 600. 지력이 높은 무장일수록 많이 만듭니다.</p>", "<p class=\"note\">창·극·노·군마는 금 ' + COST.produce + ', 충차는 금 ' + COST.ram + '. 지력이 높은 무장일수록 많이 만듭니다.</p>")
s = rep(s, "return k[0] === 'ram' ? '충차 1대 · 금 ' + (anyHas(os, '발명') ? 300 : 600) : '예상 <b>+' + fmt(produceAmount(b, k[0], os)) + '</b> · 금 300'; } },", "return k[0] === 'ram' ? '충차 1대 · 금 ' + (anyHas(os, '발명') ? COST.ramInv : COST.ram) : '예상 <b>+' + fmt(produceAmount(b, k[0], os)) + '</b> · 금 ' + COST.produce; } },")
s = rep(s, "dlgHead('포상 — 금 100 · 행동력 ' + AP.reward)", "dlgHead('포상 — 금 ' + COST.reward + ' · 행동력 ' + AP.reward)")
s = rep(s, "'금 ' + 150 * fc.lv + ' · 행 ' + AP.merge", "'금 ' + COST.merge * fc.lv + ' · 행 ' + AP.merge")
s = rep(s, "if (hasFac(b, 'barracks') && b.gold >= 300 && b.order >= 60) tips.push(['징병', 'home']);", "if (hasFac(b, 'barracks') && b.gold >= COST.draft && b.order >= 60) tips.push(['징병', 'home']);")
s = rep(s, "cmd('reward', '포상', '금 100 · 행 ' + AP.reward)", "cmd('reward', '포상', '금 ' + COST.reward + ' · 행 ' + AP.reward)")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
