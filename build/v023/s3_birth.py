# -*- coding: utf-8 -*-
"""v0.23 (3) 아이 탄생 · 수명 켬/끔.   python3 build/v023/s3_birth.py   (s1 · s2 다음에)
   · 명부의 아이(아버지가 적힌 사람): 태어난 해에 알린다. 등장 연도에 아버지가 섬기는 세력으로 온다(s1).
   · 이 판에서 태어나는 아이(가상): 해가 바뀔 때 벼슬하는 남자 무장(BIRTH.min ~ max 세)에게서 BIRTH.p %(군주는 lord %)로. 성은 아버지의 성, 이름은 한 글자. 능력은 아버지를 닮는다.
     BIRTH.grow 년 뒤에 장성해 아버지가 섬기는 세력(없으면 그 집안)으로 온다. 지금은 아들만(여성 공용 초상이 아직 없다).
   · 수명은 판마다 켜고 끈다(G.life): 새 판을 시작할 때 고르고, 메뉴에서도 바꾼다. 끄면 늙어 죽지 않고 가상의 아이도 태어나지 않는다."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s)


def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:70], s.count(a))
    return s.replace(a, b)


# ───────── data.js ─────────
d = rd('src/data.js')
d = rep(d, "var HEIR = {", """/* v0.23 아이: p · lord = 한 해에 아이가 태어날 확률(%, 무장 · 군주) · min ~ max = 아버지의 나이(세는나이) · kids = 한 사람의 자식 수(명부의 자식도 센다) · grow = 장성하는 나이
   inh = 아버지를 닮는 몫(나머지는 60 으로 끌린다) · vr = 능력의 들쭉날쭉(±) · life = 수명(세) · skP = 아버지의 특기를 물려받을 확률(%) · skR = 그렇지 않을 때 다른 특기를 얻을 확률(%) */
var BIRTH = { p: 1.5, lord: 4.5, min: 20, max: 50, kids: 3, grow: 15, inh: 0.7, vr: 12, life: [55, 75], skP: 35, skR: 15,
  sk: ['창장', '극장', '궁장', '기장', '불굴', '금강', '간파', '능리', '논객', '둔전', '부호', '안력'], skip: ['올돌골', '가비능', '금환결', '망아장', '동도나', '아회남', '철리길'] };
var SURN2 = ['제갈', '사마', '하후', '공손', '황보', '태사', '순우', '선우', '관구', '영호', '남궁'];      // 두 글자 성
var KID_NAMES = ('충 안 평 흥 녕 익 광 성 현 무 준 원 기 승 찬 연 수 통 정 화 휘 윤 훈 강 담 소 진 범 표 굉 홍 함 림 집 염 빈 건 규 술 융 택 서 임 철 웅 창 봉 운 백 개 경 근 단 랑 렴 륜 목 민 보 상 석 섭 순 식 악 양 엄 영 예 온 완 요 우 위 은 응 일 재 전 종 주 지 직 참 초 총 추 치 침 탐 태 필 하 한 합 항 해 혁 형 호 환 황 회 효 후 흠 희').split(' ');
var HEIR = {""")
wr('src/data.js', d)

# ───────── bios.js ─────────
b = rd('src/bios.js')
b = rep(b, "function bioOf(o) { return (o && BIOS[o.n]) || ''; }",
        "function kidBio(o) { return o.dad + '의 ' + (o.sex === 'f' ? '딸' : '아들') + '. ' + o.by + '년에 이 판에서 태어났다(사서에 없는 가상의 인물).'; }      // v0.23: 이 판에서 태어난 아이\nfunction bioOf(o) { return (o && BIOS[o.n]) || (o && o.kid ? kidBio(o) : ''); }")
wr('src/bios.js', b)

# ───────── core.js ─────────
c = rd('src/core.js')
c = rep(c, "function newGame(playerFaction, seed, scen) {      // v0.23: scen = 시대(없으면 194년 군웅할거)", "function newGame(playerFaction, seed, scen, life) {      // v0.23: scen = 시대(없으면 194년 군웅할거) · life = false 면 수명을 끈 판")
c = rep(c, "    ver: 2, scen: SCENARIO.id, life: 1,", "    ver: 2, scen: SCENARIO.id, life: (life === false || life === 0) ? 0 : 1,")
c = rep(c, "  if (newMonth) lifeTick();                                              // v0.23: 수명", "  if (newYear) birthTick();                                              // v0.23: 아이\n  if (newMonth) lifeTick();                                              // v0.23: 수명")
c = rep(c, "function serialize() { return JSON.stringify(G); }", r"""/* 수명을 켜고 끈다(이 판). 켤 때 이미 수명이 지나 있는 사람은 한꺼번에 떠나지 않도록 1 ~ LIFE.old 년에 걸쳐 흩는다 */
function lifeSet(on) {
  if (on) {
    G.officers.forEach(function (o) { if (o.dy && o.st !== 'dead' && o.st !== 'hidden' && lifeDue(o)) { o.dy = G.year + 1 + (strHash(o.n) >>> 0) % LIFE.old; o.late = 1; } });
    G.life = 1;
  } else { G.life = 0; G.officers.forEach(function (o) { if (o.sick) delete o.sick; }); }
  return G.life === 1;
}
/* ================= 아이(v0.23) =================
   해가 바뀔 때(roundEnd) birthTick: ① 명부의 아이가 태어나는 해면 알린다 ② 벼슬하는 남자 무장에게서 가상의 아이가 태어난다(BIRTH). 판의 난수(rnd)는 쓰지 않는다(omenRoll · strHash). */
function surnameOf(n) { return (n.length >= 3 && SURN2.indexOf(n.slice(0, 2)) >= 0) ? n.slice(0, 2) : n.charAt(0); }
function kidsOf(o) { return G.officers.filter(function (k) { return k.dad === o.n; }); }
function kidName(o, used) {
  var sur = surnameOf(o.n), N = KID_NAMES.length, h = strHash('kid|' + o.id + '|' + G.year + '|' + (G.seed0 | 0)) >>> 0, i, nm;
  for (i = 0; i < N; i++) { nm = sur + KID_NAMES[(h + i) % N]; if (!used[nm]) return nm; }
  for (i = 0; i < N * 4; i++) { nm = sur + KID_NAMES[(h + i) % N] + KID_NAMES[((h >>> 9) + i * 3) % N]; if (!used[nm]) return nm; }
  return null;
}
function makeKid(o, used) {
  var key = 'kid|' + o.id + '|' + G.year, nm = kidName(o, used); if (!nm) return null;
  function roll(k) { return omenRoll(key + '|' + k) / 100; }
  function stat(k) { return clamp(Math.round(o[k] * BIRTH.inh + 60 * (1 - BIRTH.inh) + (roll(k) * 2 - 1) * BIRTH.vr), 20, 97); }
  var L = 'CBAS', apt = '', i, r, x;
  for (i = 0; i < 5; i++) { x = L.indexOf(o.apt.charAt(i)); r = roll('a' + i); if (r < 0.25) x = Math.max(0, x - 1); else if (r > 0.9) x = Math.min(3, x + 1); apt += L.charAt(x); }
  var k = { id: G.officers.length, n: nm, ldr: stat('ldr'), war: stat('war'), int: stat('int'), pol: stat('pol'), cha: stat('cha'), apt: apt, sk: '', por: '', f: -1, st: 'hidden', loc: cityOf(o.loc), unit: null, loy: 100, merit: 0, acted: false,
    y: G.year + BIRTH.grow, j: facHouse(o.f), capF: -1, dest: -1, eta: 0, pf: -1, by: G.year, dy: 0, dm: 1 + Math.floor(roll('dm') * 12), dad: o.n, kid: 1 };
  r = roll('sk') * 100;
  if (o.sk && r < BIRTH.skP) k.sk = o.sk; else if (r >= 100 - BIRTH.skR) k.sk = BIRTH.sk[Math.floor(roll('sk2') * BIRTH.sk.length)];
  k.por = (k.war >= k.int ? 'gm' : 'gc') + (1 + Math.floor(roll('por') * 5));
  k.dy = k.by + BIRTH.life[0] + Math.floor(roll('life') * (BIRTH.life[1] - BIRTH.life[0] + 1));
  return k;
}
function birthNote(fa, k) {
  var p = offAt(fa), mine = fa.f === G.player, w = isWoman(k) ? '딸' : '아들';
  logMsg(fa.n + '에게 ' + w + ' ' + josa(k.n, '이가') + ' 태어났다', p.c, p.r, fa.f, mine ? 1 : 0);
  if (mine && !G.aiOnly) ev({ t: 'news', f: fa.f, c: p.c, r: p.r, text: '<b>' + fa.n + '에게 ' + w + ' ' + josa(k.n, '이가') + ' 태어났습니다</b> — ' + k.y + '년에 장성합니다' });
}
function birthTick() {
  var n0 = G.officers.length, used = null, i, made = 0;
  for (i = 0; i < n0; i++) {
    var o = G.officers[i];
    if (o.st === 'hidden' && o.dad && !o.kid && o.by === G.year) { var fa = offByName(o.dad); if (fa && fa.st !== 'dead' && fa.f >= 0) birthNote(fa, o); continue; }      // ① 명부의 아이
    if (G.life !== 1 || o.f < 0 || !(o.st === 'active' || o.st === 'travel') || !o.by || o.sick || o.n.length > 3 || isWoman(o) || BIRTH.skip.indexOf(o.n) >= 0) continue;      // ② 가상의 아이: 수명을 켠 판에서만
    var age = ageOf(o); if (age < BIRTH.min || age > BIRTH.max) continue;
    if (omenRoll('birth|' + o.id + '|' + G.year) >= (isLord(o) ? BIRTH.lord : BIRTH.p)) continue;
    if (kidsOf(o).length >= BIRTH.kids) continue;
    if (!used) { used = {}; for (var j = 0; j < G.officers.length; j++) used[G.officers[j].n] = 1; }
    var k = makeKid(o, used); if (!k) continue;
    used[k.n] = 1; G.officers.push(k); birthNote(o, k); made++;
  }
  return made;
}
function serialize() { return JSON.stringify(G); }""")
c = rep(c, "  if (grownB) for (var gbi = G.bases.length - grownB;", "  if (lifeNew) { var lcap = facCities(G.player)[0] || facBases(G.player)[0]; logMsg('수명이 생겼습니다(v0.23) — 무장이 제 수명에 세상을 떠나고 아이가 태어납니다. 메뉴에서 끌 수 있습니다', lcap ? lcap.c : undefined, lcap ? lcap.r : undefined, G.player, 1); }\n  if (grownB) for (var gbi = G.bases.length - grownB;")
wr('src/core.js', c)

# ───────── ui_panels.js ─────────
u = rd('src/ui_panels.js')
u = rep(u, "  var st = { f: -1, scen: UI.scenPick || '194' }, S = null, info = [];", "  var st = { f: -1, scen: UI.scenPick || '194', life: UI.lifePick !== false }, S = null, info = [];")
u = rep(u, "      h += '</div><p class=\"scsub\"><b>' + S.han + '</b> ' + S.sub + '</p><div class=\"rows\">';",
        "      h += '</div><p class=\"scsub\"><b>' + S.han + '</b> ' + S.sub + '</p><button type=\"button\" class=\"lifeb' + (st.life ? ' on' : '') + '\" data-a=\"life\" aria-pressed=\"' + (st.life ? 'true' : 'false') + '\"><b>수명 ' + (st.life ? '켬' : '끔') + '</b><span>' + (st.life ? '무장이 제 수명에 세상을 떠나고, 아이가 태어납니다' : '무장이 늙어 죽지 않습니다 · 아이도 태어나지 않습니다') + '</span></button><div class=\"rows\">';")
u = rep(u, "      f: function (el) { st.f = +el.getAttribute('data-v'); refreshDialog(); },\n      go: function () { if (st.f < 0) return; closeDialog(); keepPrev(); newGame(st.f, undefined, st.scen);",
        "      life: function () { st.life = !st.life; UI.lifePick = st.life; sfx('ui'); refreshDialog(); },\n      f: function (el) { st.f = +el.getAttribute('data-v'); refreshDialog(); },\n      go: function () { if (st.f < 0) return; closeDialog(); keepPrev(); newGame(st.f, undefined, st.scen, st.life);")
u = rep(u, "        '<button class=\"cmd\" type=\"button\" data-a=\"title\"><b>처음으로</b></button></div>", "        '<button class=\"cmd\" type=\"button\" data-a=\"life\"><b>수명 ' + (G.life === 1 ? '켜짐' : '꺼짐') + '</b><small>이 판</small></button>' +\n        '<button class=\"cmd\" type=\"button\" data-a=\"title\"><b>처음으로</b></button></div>")
u = rep(u, "      help: function () { showHelp(); },\n      share:", "      life: function () { var on = lifeSet(G.life !== 1); saveGame(); toast(on ? '수명 켬 — 무장이 제 수명에 세상을 떠나고 아이가 태어납니다' : '수명 끔 — 무장이 늙어 죽지 않습니다(아이도 태어나지 않습니다)', 2600); refreshDialog(); },\n      help: function () { showHelp(); },\n      share:")
u = rep(u, "    heirNote(o) +\n", "    famNote(o) + heirNote(o) +\n")
u = rep(u, "function heirTag(o) {", r"""function famNote(o) {                      // v0.23: 아버지 · 자식(태어난 아이만)
  if (!G) return '';
  var kids = G.officers.filter(function (k) { return k.dad === o.n && k.by <= G.year; }), s = [];
  if (o.dad) s.push('아버지 <b>' + o.dad + '</b>');
  if (kids.length) s.push('자식 ' + kids.map(function (k) { return '<b>' + k.n + '</b>' + (k.st === 'dead' ? '(졸)' : (k.st === 'hidden' ? '(' + ageOf(k) + '세)' : '')); }).join(' · '));
  return s.length ? '<p class="note fam">' + s.join(' — ') + '</p>' : '';
}
function heirTag(o) {""")
u = rep(u, "  '<h3>후계</h3><p>군주가 세상을 떠나면",
        "  '<p><b>수명 켬 · 끔</b> — 새 판을 시작할 때 <b>수명</b> 단추로 고르고, 판을 하는 중에도 <b>메뉴</b>에서 바꿉니다. 끄면 무장이 늙어 죽지 않고(가상의 아이도 태어나지 않습니다), 다시 켜면 이미 수명이 지난 사람은 ' + LIFE.old + '년에 걸쳐 차례로 떠납니다. 예전 저장은 켜진 채로 열립니다.</p>' +\n" +
        "  '<h3>아이</h3><p>사서에 아버지가 적힌 사람(유선 · 조예 · 손등 …)은 <b>태어난 해에 알림</b>이 오고, 등장 연도가 되면 <b>아버지가 섬기는 세력</b>으로 옵니다(아버지가 벼슬하지 않으면 그 집안으로). 수명을 켠 판에서는 해가 바뀔 때 벼슬하는 무장(' + BIRTH.min + ' ~ ' + BIRTH.max + '세)에게서 <b>가상의 아이</b>도 태어납니다 — 한 해에 ' + BIRTH.p + '%(군주는 ' + BIRTH.lord + '%), 한 사람에게 ' + BIRTH.kids + '명까지. 성은 아버지의 성을 따르고, 능력 · 적성 · 특기는 아버지를 닮되 들쭉날쭉합니다. ' + BIRTH.grow + '년 뒤에 장성해 찾아오고, 초상은 공용입니다. 무장 창에 아버지와 자식이 적힙니다. 지금은 아들만 태어납니다.</p>' +\n" +
        "  '<h3>후계</h3><p>군주가 세상을 떠나면")
wr('src/ui_panels.js', u)

s = rd('src/style.css')
s += """.lifeb { display: flex; align-items: center; gap: 9px; width: 100%; margin: 0 0 6px; padding: 5px 9px; min-height: 36px; border: 1px solid var(--line-2); border-radius: 2px; background: var(--paper-2); text-align: left; font-family: var(--font-body); color: var(--ink-2); }
.lifeb b { flex: 0 0 auto; font-size: 13px; color: var(--dim); }
.lifeb.on b { color: var(--jade); }
.lifeb span { font-size: 11.5px; line-height: 1.3; }
.note.fam { margin: -2px 0 6px; color: var(--ink-2); line-height: 1.45; }
"""
wr('src/style.css', s)
print('s3_birth ok')
