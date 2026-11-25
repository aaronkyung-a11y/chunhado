# -*- coding: utf-8 -*-
"""v0.23 명부 만들기: 예전 명부(build/roster.v0221.js) + tools/hist23.py → src/roster.js (+ build/v023/roster23_dump.tsv, build/v023/bios_new.json)
   python3 tools/roster23.py            만들고 요약을 찍는다
   · 194년 판은 예전 명부의 425명을 글자 하나 바꾸지 않는다(순서 · 능력 · 세력 · 도시 · 등장 연도). 새 무장은 그 뒤에 붙는다.
   · 다른 시대는 hist23 의 내력(누구를 언제부터 섬겼나)과 판도(SCEN)로 자리를 정한다.
   · 수명: 병사 · 자연사는 역사의 해, 처형 · 전사는 max(역사의 해 + LIFE_ADD, 태어난 해 + LIFE_MIN)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import hist23 as H

LIFE_ADD, LIFE_MIN = 15, 60
LINEAGE = {'손책': ['손견'], '손권': ['손견', '손책'], '조비': ['조조'], '조예': ['조조', '조비'], '유선': ['유비'], '유장': ['유언'], '이각': ['동탁'], '원상': ['원소'],
           '공손강': ['공손도'], '공손공': ['공손도', '공손강'], '공손연': ['공손도', '공손강', '공손공']}
GATES = ['함곡관', '동관', '무관', '양평관', '검각', '호관', '호로관']


def hsh(s, salt=0):
    h = (2166136261 ^ salt) & 0xffffffff
    for ch in s:
        h = ((h ^ ord(ch)) * 16777619) & 0xffffffff
    return h


def num(tok):
    if tok == '?': return None, True
    if tok.endswith('?'): return int(tok[:-1]), True
    return int(tok), False


def house(n): return H.HOUSE_OF.get(n, n)


def main():
    warn = []
    src = open(os.path.join(ROOT, 'build', 'roster.v0221.js'), encoding='utf-8').read()
    old = json.loads(src[src.index('{'):src.rindex('}') + 1])
    OF, OO = old['factions'], old['officers']

    def tokens(parts, rec):
        for t in parts:
            if t.startswith('fa='): rec['fa'] = t[3:]
            elif t == 'j': rec['jf'] = True
            elif t == 'x': rec['car'].append((None, 'x'))
            else:
                y, h = t.split(':'); rec['car'].append((int(y), h))

    T = {}
    for ln in H.OLD.strip().split('\n'):
        p = ln.split()
        if not p: continue
        rec = dict(by=num(p[1]), hd=num(p[2]), k=p[3], car=[], fa=None, jf=False)
        assert p[3] in ('n', 'k'), ln
        tokens(p[4:], rec)
        if p[0] in T: warn.append('겹침 ' + p[0])
        T[p[0]] = rec
    names_old = [o['n'] for o in OO]
    for n in T:
        if n not in names_old: warn.append('명부에 없는 이름 ' + n)
    miss = [n for n in names_old if n not in T]

    M = []
    for i, so in enumerate(OO):
        rec = T.get(so['n']) or dict(by=(None, True), hd=(None, True), k='n', car=[], fa=None, jf=False)
        m = dict(n=so['n'], ldr=so['ldr'], war=so['war'], int=so['int'], pol=so['pol'], cha=so['cha'], apt=so['apt'], sk=so.get('sk', ''), por=so['por'], new=False,
                 f194=so['f'], home=so['c'], st194=so.get('st'), y194=so.get('y'), j194=so.get('j'), rec=rec, has_sk=('sk' in so))
        M.append(m)
    bios = {}
    for ln in H.NEW.strip().split('\n'):
        p = ln.split('|')
        assert len(p) == 9, ln
        st = [int(x) for x in p[1].split()]; life = p[5].split(); car = p[7].split()
        rec = dict(by=num(life[0]), hd=num(life[1]), k=life[2], car=[], fa=None, jf=False)
        tokens(car, rec)
        assert p[0] not in names_old and all(p[0] != x['n'] for x in M), '이름 겹침 ' + p[0]
        assert len(p[2]) == 5 and p[3] in ('',) + tuple(SKILLS), ln
        M.append(dict(n=p[0], ldr=st[0], war=st[1], int=st[2], pol=st[3], cha=st[4], apt=p[2], sk=p[3], por=p[4], new=True, f194=None, home=p[6], st194=None, y194=None, j194=None, rec=rec, has_sk=True))
        bios[p[0]] = p[8]
    IDX = {m['n']: i for i, m in enumerate(M)}

    # ── 생몰년 ──
    for m in M:
        r = m['rec']; n = m['n']; h1, h2, h3 = hsh(n, 11), hsh(n, 23), hsh(n, 37)
        car = [c for c in r['car']]
        hidden = (m['st194'] == 'hidden')
        (by, be), (hd, he) = r['by'], r['hd']
        # 내력의 첫 해(태어난 해를 어림하는 데 쓴다)
        first = None
        ys = [c[0] for c in car if c[0] is not None]
        if ys: first = min(ys)
        if not m['new']:
            first = min(first, m['y194']) if (first and hidden) else (first or (m['y194'] if hidden else 194))
            if not hidden: first = min(first, 194)
        if by is None:
            by = (m['y194'] - 16 - h1 % 5) if hidden else (158 + h1 % 13)
            if r['fa'] and r['fa'] in T and T[r['fa']]['by'][0]: by = max(by, T[r['fa']]['by'][0] + 18 + h1 % 8)
            by = min(by, first - 15)
            if hd is not None: by = min(by, hd - 25)
        if hd is None:
            hd = by + 58 + h2 % 14
            last = max(ys) if ys else first
            hd = max(hd, last + 5, (first or 0) + 8)
        m['by'], m['hd'], m['e'] = by, hd, (1 if be else 0) | (2 if he else 0)
        m['k'] = 1 if r['k'] == 'k' else 0
        m['dy'] = max(hd + LIFE_ADD, by + LIFE_MIN) if m['k'] else hd
        m['dm'] = 1 + h3 % 12
        m['fa'] = r['fa']; m['jf'] = r['jf']
        if m['fa'] and m['fa'] not in IDX: warn.append('아버지가 명부에 없다 ' + n + ' ← ' + m['fa'])
        if not m['new'] and not hidden and hd < 194: warn.append('194년에 있는데 그 전에 죽었다 ' + n + ' ' + str(hd))
        if hidden and hd < m['y194']: warn.append('등장하기 전에 죽는다 ' + n + ' %d < %d' % (hd, m['y194']))
        if hd - by < 16: warn.append('너무 일찍 죽는다 ' + n + ' %d~%d' % (by, hd))
        # 내력
        if not car or car == [(None, 'x')]:
            x = bool(car)
            if m['new']: raise SystemExit('새 무장의 내력이 없다 ' + n)
            if hidden: car = [(m['y194'], 'x' if (x or not m['j194']) else house(m['j194']))]
            elif x: car = [(by + 16, 'x')]
            else:
                hh = house(OF[m['f194']]['n']); car = [(min(194, max(by + 16, H.HSTART.get(hh, 184))), hh)]
        car = [(c[0] if c[0] is not None else (m['y194'] if hidden else by + 16), c[1]) for c in car]
        car.sort(key=lambda c: c[0])
        m['car'] = car
        for c in car:
            if c[1] not in ('x', '-') and c[1] not in H.HSTART: warn.append('모르는 집안 ' + n + ' ' + c[1])

    # ── 시대 ──
    def factions_of(S):
        if S['id'] == '194':
            return [dict(n=f['n'], color=f['color'], cities=list(f['cities']), house=house(f['n'])) for f in OF]
        out = []
        for (n, col, cities, start, mul, desc) in S['factions']:
            d = dict(n=n, color=col, cities=list(cities), house=house(n), desc=desc)
            if start: d['start'] = start
            if mul: d['mul'] = mul
            out.append(d)
        return out

    def status(m, S, FS, own, forced):
        """→ (f, city, st, y, j, why)  st: 0 있음 · 1 숨음 · 2 재야 · 3 죽음"""
        n = m['n']; Y = S['year']
        m = dict(m, home=S.get('home', {}).get(n, m['home']))
        for k, f in enumerate(FS):
            if f['n'] == n: return (k, f['cities'][0], 0, 0, None, 'lord')
        if n in S.get('dead', ()) or m['hd'] < Y: return (-1, m['home'], 3, 0, None, 'dead')
        car = m['car']
        pc = S.get('place', {}).get(n)
        ya = min(m['y194'], car[0][0]) if (not m['new'] and m['st194'] == 'hidden') else car[0][0]      # 세상에 나오는 해(예전 명부의 등장 연도)
        if Y < ya or Y < car[0][0]:
            if pc and pc in own and m['by'] + 14 <= Y: return (own[pc], pc, 0, 0, None, 'place')
            if Y < ya:                                          # 아직 어리다: 그 해가 되면 나온다(따라갈 집안이 있으면 스스로 찾아간다)
                hs = [c[1] for c in car if c[1] not in ('x', '-')]
                auto = bool(m['j194']) or bool(m['fa']) or m['jf']
                j = (house(m['j194']) if m['j194'] else (hs[0] if hs else None)) if auto else None
                return (-1, m['home'], 1, ya, j, 'young')
            return (-1, m['home'], 1, ya, None, 'wait')         # 세상에 나왔으나 아직 누구도 섬기지 않는다: 그 도시에서 탐색으로 찾는다
        cur = [c for c in car if c[0] <= Y][-1]
        h, y0 = cur[1], cur[0]
        while h in H.ABSORB and H.ABSORB[h][0] <= Y and H.ABSORB[h][0] >= y0:
            y0, h = H.ABSORB[h][0], H.ABSORB[h][1]
        if pc and pc in own: return (own[pc], pc, 0, 0, None, 'place')
        if pc: forced.append(n + '→' + pc + '(주인 없음)')
        if h == 'x': return (-1, m['home'], 1, ya, None, 'x')
        fk = -1
        for k, f in enumerate(FS):
            if f['house'] == h: fk = k
        if h == '-' or fk < 0: return (-1, m['home'], 2, 0, None, 'free')
        return (fk, None, 0, 0, None, 'serve')

    scens = []; summary = []
    for S in H.SCEN:
        FS = factions_of(S); Y = S['year']
        own = {}
        for k, f in enumerate(FS):
            f['anc'] = LINEAGE.get(f['n'], [])
            for c in f['cities']:
                assert c not in own, S['id'] + ' 도시 겹침 ' + c
                own[c] = k
        forced = []; pl = []
        for i, m in enumerate(M):
            if S['id'] == '194' and not m['new']:
                pl.append([m['f194'], m['home'], 1 if m['st194'] == 'hidden' else 0, m['y194'] or 0, m['j194'], 'old']); continue
            pl.append(list(status(m, S, FS, own, forced)))
        # 도시를 정하지 않은 사람: 제 고장이 우리 땅이면 거기, 아니면 본거지에 무게를 두고 흩는다
        for i, m in enumerate(M):
            p = pl[i]
            if p[2] == 0 and p[1] is None:
                f = FS[p[0]]
                if m['home'] in f['cities']: p[1] = m['home']; p[5] = 'home'
                else:
                    w = [f['cities'][0]] * 3 + f['cities'][1:]
                    p[1] = w[hsh(m['n'], 51) % len(w)]; p[5] = 'spread'
        if S['id'] != '194':
            for k, f in enumerate(FS):                          # 빈 성이 없도록 사람이 많은 성에서 하나씩 옮긴다
                for c in f['cities']:
                    here = lambda cc: [i for i, p in enumerate(pl) if p[2] == 0 and p[0] == k and p[1] == cc]
                    if here(c): continue
                    best = None
                    for cc in f['cities']:
                        mv = [i for i in here(cc) if pl[i][5] in ('spread', 'home')]
                        if len(here(cc)) >= 2 and mv and (best is None or len(here(cc)) > best[0]): best = (len(here(cc)), sorted(mv, key=lambda i: (pl[i][5] != 'spread', hsh(M[i]['n'], 77)))[0])
                    if best: pl[best[1]][1] = c; pl[best[1]][5] = 'fill'
        # 확인
        for k, f in enumerate(FS):
            assert f['n'] in IDX, '군주가 명부에 없다 ' + f['n']
            if M[IDX[f['n']]]['hd'] < Y: warn.append(S['id'] + ' 군주가 이미 죽었다 ' + f['n'])
        for n in S.get('place', {}):
            if n not in IDX: warn.append(S['id'] + ' place: 모르는 이름 ' + n)
            elif pl[IDX[n]][5] != 'place' and pl[IDX[n]][5] != 'lord': warn.append(S['id'] + ' place 가 먹지 않았다 ' + n + '(' + pl[IDX[n]][5] + ')')
        for x in forced: warn.append(S['id'] + ' ' + x)
        gates = {}
        for g in GATES:
            who = S.get('gates', {}).get(g) if S['id'] != '194' else None
            gates[g] = old['gates'][g] if S['id'] == '194' else ([k for k, f in enumerate(FS) if f['n'] == who][0] if who else -1)
        cnt = [sum(1 for p in pl if p[2] == 0 and p[0] == k) for k in range(len(FS))]
        empt = [c for k, f in enumerate(FS) for c in f['cities'] if not any(p[2] == 0 and p[0] == k and p[1] == c for p in pl)]
        summary.append('%s %s: 세력 %d · 있음 %d · 숨음 %d · 재야 %d · 죽음 %d%s\n   %s' % (S['id'], S['name'], len(FS), sum(1 for p in pl if p[2] == 0), sum(1 for p in pl if p[2] == 1),
                       sum(1 for p in pl if p[2] == 2), sum(1 for p in pl if p[2] == 3), (' · 빈 성 ' + ','.join(empt)) if empt else '', ' '.join('%s%d/%d' % (f['n'], len(f['cities']), cnt[k]) for k, f in enumerate(FS))))
        scens.append(dict(S=S, FS=FS, pl=pl, gates=gates))

    # 194년 판의 내력과 예전 명부가 어긋나는 곳(자료 점검용)
    S194 = [s for s in scens if s['S']['id'] == '194'][0]
    own194 = {c: k for k, f in enumerate(S194['FS']) for c in f['cities']}
    mism = []
    for i, m in enumerate(M):
        if m['new'] or not T.get(m['n']) or not T[m['n']]['car']: continue
        st = status(m, dict(id='x194', year=194), S194['FS'], own194, [])
        if m['st194'] == 'hidden':
            if m['car'][0][0] < m['y194'] and m['car'][0][1] not in ('x', '-'): mism.append('%s 등장 %d 인데 내력은 %d:%s' % (m['n'], m['y194'], m['car'][0][0], m['car'][0][1]))
        elif st[0] != m['f194'] or st[2] != 0: mism.append('%s 명부 %s 내력 %s/%s' % (m['n'], OF[m['f194']]['n'], S194['FS'][st[0]]['n'] if st[0] >= 0 else '-', st[5]))

    # ── 쓰기 ──
    cities = []
    for s in scens:
        for p in s['pl']:
            if p[1] not in cities: cities.append(p[1])
    J = lambda x: json.dumps(x, ensure_ascii=False, separators=(',', ':'))
    out = ['/* 명부 (v0.23) — tools/roster23.py 가 tools/hist23.py 와 예전 명부로 만든다. 손으로 고치지 않는다.\n'
           '   ROSTER: 무장(능력 · 생몰년). by 태어난 해 · hd 역사에서 죽은 해 · k 1 = 처형 · 전사(더 오래 산다) · dy 판에서 수명이 다하는 해 · dm 그 달 · e 1 = 태어난 해가 추정, 2 = 죽은 해가 추정 · fa 아버지\n'
           '   SCENS: 시대. pl[i] = [세력, 도시(RCITY), 0 있음 · 1 숨음 · 2 재야 · 3 죽음, 등장 연도, 따라갈 집안]   scenarioMake(id) 가 예전의 SCENARIO 꼴로 펼친다 */']
    rows = []
    for m in M:
        d = dict(n=m['n'], ldr=m['ldr'], war=m['war'], int=m['int'], pol=m['pol'], cha=m['cha'], apt=m['apt'])
        if m['has_sk']: d['sk'] = m['sk']
        d['por'] = m['por']; d['by'] = m['by']; d['hd'] = m['hd']; d['dy'] = m['dy']; d['dm'] = m['dm']
        if m['k']: d['k'] = 1
        if m['e']: d['e'] = m['e']
        if m['fa']: d['fa'] = m['fa']
        rows.append(J(d))
    out.append('var ROSTER=[\n' + ',\n'.join(rows) + '];')
    out.append('var RCITY=' + J(cities) + ';')
    out.append('var HOUSES=' + J(H.HOUSE_OF) + ';')
    out.append('var WOMEN=' + J(old['women']) + ';')
    ss = []
    for s in scens:
        S = s['S']
        pl = []
        for p in s['pl']:
            e = [p[0], cities.index(p[1])]
            if p[2] or p[3] or p[4]: e.append(p[2])
            if p[3] or p[4]: e.append(p[3])
            if p[4]: e.append(p[4])
            pl.append(e)
        ss.append('{"id":%s,"year":%d,"month":%d,"name":%s,"han":%s,"sub":%s,\n"factions":%s,\n"gates":%s,\n"pl":%s}' % (J(S['id']), S['year'], S['month'], J(S['name']), J(S['han']), J(S['sub']), J(s['FS']), J(s['gates']), J(pl)))
    out.append('var SCENS=[\n' + ',\n'.join(ss) + '];')
    out.append(SCEN_JS)
    open(os.path.join(ROOT, 'src', 'roster.js'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    os.makedirs(os.path.join(ROOT, 'build', 'v023'), exist_ok=True)
    json.dump(bios, open(os.path.join(ROOT, 'build', 'v023', 'bios_new.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    with open(os.path.join(ROOT, 'build', 'v023', 'roster23_dump.tsv'), 'w', encoding='utf-8') as f:
        f.write('n\tby\thd\tk\tdy\te\tfa\tcar\t' + '\t'.join(s['S']['id'] for s in scens) + '\n')
        for i, m in enumerate(M):
            cell = []
            for s in scens:
                p = s['pl'][i]
                cell.append({0: (s['FS'][p[0]]['n'] + '/' + p[1]) if p[0] >= 0 else '?', 1: 'h%d%s@%s' % (p[3], ('>' + p[4]) if p[4] else '', p[1]), 2: 'free@' + p[1], 3: '†'}[p[2]])
            f.write('\t'.join([m['n'], str(m['by']), str(m['hd']), 'k' if m['k'] else 'n', str(m['dy']), str(m['e']), m['fa'] or '', ' '.join('%d:%s' % c for c in m['car'])] + cell) + '\n')
    print('무장 %d명(예전 %d + 새 %d) · 추정: 태어난 해 %d명, 죽은 해 %d명 · 자료가 없는 사람 %d명' % (len(M), len(OO), len(M) - len(OO), sum(1 for m in M if m['e'] & 1), sum(1 for m in M if m['e'] & 2), len(miss)))
    if miss: print('  hist23 에 없는 이름: ' + ' '.join(miss))
    for s in summary: print(s)
    short = [n for n, b in bios.items() if len(b) < 20 or len(b) > 110 or not b.endswith('.')]
    if short: print('열전 길이: ' + ' '.join(short))
    print('어긋남 %d: ' % len(mism) + ' | '.join(mism[:70]))
    print('경고 %d: ' % len(warn) + ' | '.join(warn[:60]))
    print('roster.js %d bytes' % os.path.getsize(os.path.join(ROOT, 'src', 'roster.js')))


SKILLS = '비장 신장 투신 용장 창장 극장 궁장 기장 기신 궁신 위풍 연전 금강 철벽 불굴 급습 공심 강행 답파 포박 공성 신산 허실 귀모 통찰 명경 간파 반계 연환 심모 화신 화공 부호 미도 명성 능리 번식 발명 축성 둔전 인덕 위압 안력 논객 지도 왕좌'.split()

SCEN_JS = r'''var SCEN_CACHE={};
function houseName(n){return HOUSES[n]||n;}
function scenarioMake(id){
  if(SCEN_CACHE[id])return SCEN_CACHE[id];
  var S=null,i,k;
  for(i=0;i<SCENS.length;i++)if(SCENS[i].id===id)S=SCENS[i];
  if(!S)return scenarioMake('194');
  var out={id:S.id,year:S.year,month:S.month,name:S.name,han:S.han,sub:S.sub,factions:[],officers:[],women:WOMEN,gates:S.gates};
  for(i=0;i<S.factions.length;i++){var f=S.factions[i],g={};for(k in f)g[k]=f[k];g.cities=f.cities.slice();out.factions.push(g);}
  for(i=0;i<ROSTER.length;i++){
    var r=ROSTER[i],p=S.pl[i],o={n:r.n,ldr:r.ldr,war:r.war,int:r.int,pol:r.pol,cha:r.cha,apt:r.apt};
    if(r.sk!==undefined)o.sk=r.sk;
    o.f=p[0];o.c=RCITY[p[1]];o.por=r.por;
    if(p[2]===1){o.st='hidden';o.y=p[3];if(p[4])o.j=p[4];}
    else if(p[2]===2)o.st='free';
    else if(p[2]===3)o.st='dead';
    o.by=r.by;o.hd=r.hd;o.dy=r.dy;o.dm=(r.dy===S.year&&r.dm<7)?r.dm+6:r.dm;
    if(r.k)o.k=1;if(r.e)o.e=r.e;if(r.fa)o.fa=r.fa;
    out.officers.push(o);
  }
  SCEN_CACHE[id]=out;return out;
}
var SCENARIO=scenarioMake('194');'''

if __name__ == '__main__':
    main()
