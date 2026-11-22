#!/usr/bin/env python3
"""194년 군웅할거 로스터 생성.
기존 群雄割據 삼국지(index.html)의 GEN_DEFS에서 능력치(무력/통솔/지력/정치)를 가져오고,
매력·병과 적성 5종·특기·소속을 붙여 src/roster.js 를 만든다.
usage: make_roster.py <threekingdoms/index.html> <out roster.js>
"""
import sys, re, json

SRC, OUT = sys.argv[1], sys.argv[2]
src = open(SRC, encoding='utf-8').read()
i = src.index('const GEN_DEFS=['); j = src.index('];', i)
BASE = {}
for m in re.finditer(r"\['([^']+)',\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)(?:,\s*(-?\d+),\s*(-?\d+),\s*(-?\d+))?\]", src[i:j]):
    n = m.group(1)
    if n in BASE: continue
    BASE[n] = dict(war=int(m.group(2)), ldr=int(m.group(3)), int=int(m.group(4)), pol=int(m.group(5)),
                   apt3=[int(m.group(8) or 2), int(m.group(9) or 2), int(m.group(10) or 2)])

# 기존 로스터에 없는 인물 (무력, 통솔, 지력, 정치) — 자체 산정
NEW = {
 '유장': (28, 44, 56, 66), '학맹': (76, 68, 40, 35), '진규': (18, 40, 80, 82), '허유': (30, 52, 88, 70),
 '공손속': (70, 62, 48, 40), '단경': (68, 66, 50, 46), '추단': (70, 64, 42, 38), '유의': (72, 70, 56, 50),
 '공손공': (48, 52, 54, 60), '공손모': (70, 66, 48, 42), '설홍': (58, 60, 62, 60), '휴고': (74, 66, 40, 34),
 '종보': (70, 60, 36, 30), '염상': (22, 50, 80, 82), '원윤': (40, 48, 52, 56), '양강': (70, 64, 40, 36),
 '손분': (76, 74, 58, 56), '번능': (68, 62, 40, 36), '설례': (64, 60, 44, 42), '허소': (10, 30, 78, 80),
 '엄여': (78, 64, 36, 28), '허공': (44, 54, 60, 62), '추타': (66, 58, 38, 34), '전동': (64, 56, 36, 32),
 '주흔': (66, 68, 58, 60), '하제': (82, 84, 70, 62), '동습': (84, 76, 50, 44), '소비': (70, 68, 58, 54),
 '진취': (68, 62, 40, 36), '단외': (72, 74, 60, 62), '호거아': (82, 60, 30, 24), '마휴': (72, 66, 44, 40),
 '성공영': (58, 70, 82, 72), '염행': (90, 80, 60, 48), '장위': (74, 70, 50, 46), '양백': (64, 60, 44, 40),
 '유괴': (72, 74, 58, 54), '왕루': (20, 44, 74, 72), '정도': (18, 48, 84, 70), '동화': (24, 56, 74, 86),
 '등현': (70, 68, 48, 44), '양회': (72, 70, 52, 46), '조위': (70, 74, 62, 58), '방희': (62, 68, 64, 66),
 '장굉': (16, 40, 86, 90), '고옹': (20, 52, 82, 90), '옹개': (70, 66, 50, 46), '김선': (52, 56, 58, 62),
 '유도': (30, 48, 60, 66),
}

# 매력 — 자체 산정 (없으면 공식)
CHA = {'조조': 96, '유비': 99, '손권': 95, '손책': 92, '원소': 92, '원술': 70, '유표': 85, '유장': 72, '공손찬': 75, '마등': 82,
 '장로': 86, '도겸': 78, '공융': 80, '여포': 40, '이각': 30, '곽사': 28, '유요': 70, '엄백호': 35, '왕랑': 68, '공손도': 66,
 '장양': 70, '관우': 93, '장비': 45, '조운': 88, '제갈량': 92, '주유': 93, '육손': 90, '사마의': 79, '순욱': 91, '곽가': 78,
 '가후': 58, '노숙': 89, '여몽': 80, '마초': 82, '황충': 75, '장료': 78, '하후돈': 81, '하후연': 76, '조인': 74, '서황': 70,
 '장합': 72, '전위': 58, '허저': 60, '태사자': 79, '감녕': 55, '주태': 60, '황개': 72, '정보': 76, '한당': 62, '진궁': 70,
 '고순': 68, '안량': 55, '문추': 52, '전풍': 66, '저수': 72, '심배': 62, '봉기': 50, '곽도': 55, '순유': 80, '정욱': 60,
 '방통': 69, '서서': 82, '법정': 55, '위연': 45, '방덕': 70, '한수': 68, '장임': 72, '엄안': 76, '문빙': 70, '채모': 58,
 '괴월': 65, '괴량': 70, '황조': 40, '기령': 55, '장소': 80, '장굉': 78, '미축': 82, '진등': 74, '손건': 70, '간옹': 72,
 '초선': 92, '국의': 45, '악진': 62, '우금': 60, '이전': 70, '조홍': 55, '장수': 66, '양봉': 50, '장제': 55, '번조': 40,
 '마대': 68, '황보숭': 80, '주준': 74, '허소': 76, '화흠': 72, '고옹': 80, '사마휘': 84, '정현': 86, '황권': 74, '장송': 40}

# 병과 적성 — 창/극/노/기/병기 (없으면 공식)
APT = {'여포': 'SSASC', '관우': 'SSAAC', '장비': 'SACAC', '조운': 'SAASC', '마초': 'SBBSC', '황충': 'AASAC', '장료': 'SABSC',
 '하후돈': 'ASBAC', '하후연': 'BASSC', '서황': 'ASBAC', '장합': 'ASAAB', '감녕': 'ASABC', '태사자': 'ASSAC', '손책': 'SABSC',
 '주유': 'ABABB', '전위': 'BSCBC', '허저': 'ASCBC', '안량': 'SABAC', '문추': 'AABSC', '고순': 'SABBB', '조인': 'ASBAB',
 '방덕': 'ASBSC', '위연': 'SSBAC', '공손찬': 'BBASC', '마등': 'ABBSC', '조조': 'AAASA', '유비': 'AABBC', '제갈량': 'ABSBS',
 '사마의': 'ASABA', '육손': 'AAABB', '여몽': 'SABBB', '황개': 'BAABC', '주태': 'ASBBC', '손권': 'BABBC', '원소': 'BABAC',
 '국의': 'BASBC', '염행': 'SABSC', '한수': 'BBBAC', '장임': 'AASBC', '엄안': 'AASBC', '문빙': 'ASABC', '악진': 'SABBC',
 '우금': 'ASBBC', '정보': 'SABBC', '한당': 'BASAC', '기령': 'ASBBC', '장수': 'SABAC', '황보숭': 'AAAAB', '주준': 'AABBB',
 '유엽': 'CCBCS', '곽가': 'CCBCB', '순욱': 'CCCCB', '가후': 'BCBCB', '진궁': 'BBBCB', '방통': 'CBBCB', '서서': 'ABBCB',
 '하제': 'ASBBC', '동습': 'ASBCC', '마대': 'ABBSC', '장패': 'ASBAC', '이엄': 'AABBB', '손견': 'SABAC'}

# 특기 — 자체 설계
SKILL = {'조조': '허실', '유비': '인덕', '손권': '지도', '손책': '용장', '원소': '명성', '원술': '부호', '공손찬': '기장', '마등': '기장',
 '유표': '미도', '유장': '미도', '장로': '미도', '도겸': '인덕', '공융': '논객', '이각': '공성', '왕랑': '논객', '공손도': '위압',
 '여포': '비장', '관우': '신장', '장비': '투신', '조운': '통찰', '마초': '기신', '황충': '궁신', '장료': '위풍', '하후돈': '기장',
 '하후연': '급습', '허저': '금강', '전위': '철벽', '서황': '명경', '장합': '극장', '감녕': '위풍', '태사자': '극장', '주태': '불굴',
 '황개': '화공', '정보': '창장', '한당': '궁장', '여몽': '공심', '주유': '화신', '제갈량': '신산', '사마의': '심모', '육손': '화공',
 '방통': '연환', '가후': '반계', '곽가': '귀모', '순욱': '왕좌', '순유': '간파', '정욱': '간파', '진궁': '간파', '전풍': '명경',
 '저수': '간파', '서서': '명경', '법정': '심모', '노숙': '부호', '장소': '논객', '미축': '부호', '진등': '미도', '순심': '논객',
 '심배': '철벽', '고순': '공성', '안량': '용장', '문추': '기장', '국의': '궁장', '기령': '극장', '엄안': '궁장', '장임': '궁장',
 '문빙': '철벽', '위연': '연전', '방덕': '용장', '한수': '강행', '마대': '기장', '조인': '철벽', '우금': '명경', '악진': '강행',
 '이전': '축성', '조홍': '부호', '만총': '축성', '유엽': '발명', '한호': '둔전', '장수': '창장', '초선': '논객', '허소': '안력',
 '황보숭': '화공', '주준': '위압', '염행': '용장', '장세평': '번식', '화흠': '부호', '고옹': '미도', '장굉': '논객', '동소': '논객',
 '사마휘': '안력', '정현': '안력', '장연': '답파', '하제': '답파', '동습': '극장', '조위': '둔전', '괴량': '간파', '괴월': '허실',
 '황권': '간파', '장송': '안력', '허유': '허실', '성공영': '간파', '손건': '논객', '간옹': '논객', '맹획': '답파', '축융': '화공',
 '진규': '간파', '염상': '명경', '동화': '능리', '장패': '강행', '양봉': '포박', '엄백호': '포박', '전예': '축성', '태사자_': ''}

# 세력 (id 순서 = 행동 순서). (군주, 색, {도시: [무장...]})
FACTIONS = [
 ('조조', '#2b6cb0', {'진류': ['조조', '하후돈', '하후연', '조인', '조홍', '악진', '이전', '전위', '순욱', '정욱', '우금', '모개', '사환', '조순']}),
 ('여포', '#7b2d8e', {'복양': ['여포', '장료', '고순', '진궁', '송헌', '위속', '후성', '성렴', '초선', '장막', '학맹', '조성']}),
 ('유비', '#2e8b57', {'소패': ['유비', '관우', '장비', '간옹', '진도']}),
 ('도겸', '#718096', {'하비': ['도겸', '미축', '미방', '진등', '손건', '조표', '장패', '손관', '궐선', '조굉', '조욱', '착융', '진규']}),
 ('원소', '#b7950b', {'업': ['원소', '전풍', '저수', '심배', '봉기', '곽도', '순심', '신평', '진림', '허유', '안량', '문추', '장합', '고람', '국의', '순우경'],
                    '남피': ['원담', '장의거', '한맹', '여광', '여상'], '평원': ['고간', '마연', '장개', '원희', '견초', '신비']}),
 ('공손찬', '#4299e1', {'북평': ['공손찬', '조운', '전예', '엄강', '공손속', '단경'], '계': ['전해', '관정', '추단']}),
 ('공손도', '#34495e', {'양평': ['공손도', '공손강', '유의', '공손공', '공손모']}),
 ('장양', '#7d6608', {'진양': ['장양', '동소', '설홍', '휴고']}),
 ('공융', '#805ad5', {'북해': ['공융', '무안국', '왕수', '손소', '종보']}),
 ('원술', '#b83280', {'수춘': ['원술', '기령', '장훈', '양홍', '한윤', '염상', '원윤', '악취', '양강', '진기', '양대장'], '여남': ['교유', '뇌박', '진란', '유벽', '공도', '하만']}),
 ('손책', '#c53030', {'여강': ['손책', '정보', '황개', '한당', '주치', '여범', '손정', '오경', '손분']}),
 ('유요', '#3f51b5', {'건업': ['유요', '태사자', '장영', '번능', '우미', '설례', '허소', '시의']}),
 ('엄백호', '#8d6e63', {'오': ['엄백호', '엄여', '허공', '추타', '전동']}),
 ('왕랑', '#5f9ea0', {'회계': ['왕랑', '우번', '주흔', '하제', '동습']}),
 ('유표', '#00897b', {'양양': ['유표', '괴량', '괴월', '채모', '장윤', '문빙', '왕위', '이적', '한숭', '부손', '왕찬', '채중', '채화'],
                    '강릉': ['이엄', '곽준'], '강하': ['황조', '감녕', '소비', '진취', '등룡'], '장사': ['황충', '유반', '한현']}),
 ('이각', '#7b241c', {'장안': ['이각', '곽사', '장제', '번조', '가후', '장수', '이몽', '왕방', '양봉', '한섬', '서황', '이별', '호봉', '이감', '호진', '동승', '단외', '종요', '호거아']}),
 ('마등', '#c05621', {'무위': ['마등', '마초', '방덕', '마대', '마철', '마휴'], '천수': ['한수', '성공영', '염행', '양추', '후선', '성의', '정은']}),
 ('장로', '#16a085', {'한중': ['장로', '장위', '양임', '양앙', '염포', '양송', '양백']}),
 ('유장', '#6b8e23', {'성도': ['유장', '황권', '장송', '오의', '유괴', '왕루', '정도', '동화'], '자동': ['장임', '냉포', '등현', '고패', '양회', '뇌동', '오란'],
                    '강주': ['엄안', '조위', '방희', '비시']}),
]
GATE_OWNER = {'함곡관': '이각', '동관': '이각', '무관': '이각', '양평관': '장로', '검각': '유장', '호관': '장양', '호로관': None}

# 재야/미등장 (이름, 등장 연도, 도시, [합류할 군주])
FUTURE = [
 ('허저', 194, '여남'), ('장연', 194, '진양'), ('장소', 194, '건업'), ('장굉', 194, '건업'), ('능조', 194, '오'), ('화흠', 194, '시상'),
 ('좌자', 194, '여강'), ('화타', 194, '소패'), ('사마휘', 194, '양양'), ('정현', 194, '북해'), ('황보숭', 194, '장안'), ('주준', 194, '낙양'),
 ('전주', 194, '북평'), ('선우보', 194, '계'), ('관녕', 194, '양평'), ('병원', 194, '양평'), ('왕렬', 194, '양평'), ('장세평', 194, '계'),
 ('답돈', 194, '북평'), ('주유', 195, '여강'), ('주태', 195, '수춘'), ('장흠', 195, '수춘'), ('진무', 195, '여강'), ('우길', 195, '오'),
 ('순유', 196, '허창'), ('곽가', 196, '허창'), ('가규', 196, '진양'), ('고옹', 196, '오'), ('미형', 196, '허창'), ('만총', 196, '진류'),
 ('한호', 196, '낙양'), ('유엽', 197, '수춘'), ('법정', 197, '성도'), ('맹달', 197, '자동'), ('여몽', 198, '여강'), ('노숙', 198, '수춘'),
 ('진군', 198, '허창'), ('여령기', 198, '복양', '여포'), ('대교', 199, '여강'), ('제갈근', 200, '건업'), ('감택', 200, '회계'), ('서성', 200, '오'),
 ('반장', 200, '복양'), ('위연', 200, '장사'), ('옹개', 200, '건녕'), ('형도영', 200, '영릉'), ('조범', 200, '계양'), ('김선', 200, '무릉'),
 ('유도', 200, '영릉'), ('손권', 200, '여강', '손책'), ('관평', 200, '소패', '유비'), ('원상', 200, '업', '원소'), ('사마의', 201, '낙양'),
 ('서서', 201, '신야'), ('요화', 201, '양양'), ('육손', 203, '오'), ('능통', 204, '오'), ('방통', 205, '양양'), ('이회', 205, '건녕'),
 ('유파', 205, '영릉'), ('팽양', 205, '성도'), ('맹획', 205, '운남'), ('축융', 205, '운남'), ('조비', 205, '진류', '조조'), ('제갈량', 207, '양양'),
 ('장완', 208, '영릉'), ('등지', 208, '신야'), ('조창', 208, '진류', '조조'), ('마량', 209, '양양'), ('유봉', 209, '소패', '유비'),
 ('학소', 210, '진양'), ('곽회', 211, '진양'), ('비의', 212, '강하'), ('마속', 213, '양양'), ('장익', 213, '성도'), ('마충', 214, '자동'),
 ('관흥', 214, '소패', '유비'), ('장포', 214, '소패', '유비'), ('왕평', 215, '한중'), ('양수', 215, '장안'), ('등애', 218, '여남'), ('강유', 222, '천수'),
]

PORTRAIT = {'안량': 'anliang', '감녕': 'ganning', '관우': 'guanyu', '황충': 'huangzhong', '황조': 'huangzu', '여포': 'lubu', '사마의': 'simayi',
 '손책': 'sunce', '태사자': 'taishici', '문추': 'wenchou', '하후돈': 'xiahoudun', '하후연': 'xiahouyuan', '허저': 'xuchu', '장비': 'zhangfei',
 '장료': 'zhangliao', '조운': 'zhaoyun', '조조': 'caocao', '유비': 'liubei', '원소': 'yuanshao', '원술': 'yuanshu', '공손찬': 'gongsunzan',
 '유표': 'liubiao', '유장': 'liuzhang', '마등': 'mateng', '장로': 'zhanglu', '도겸': 'taoqian', '공융': 'kongrong', '이각': 'lijue', '유요': 'liuyao',
 '엄백호': 'yanbaihu', '왕랑': 'wanglang', '공손도': 'gongsundu', '장양': 'zhangyang', '제갈량': 'zhugeliang', '주유': 'zhouyu', '육손': 'luxun',
 '손권': 'sunquan', '마초': 'machao', '순욱': 'xunyu', '곽가': 'guojia', '가후': 'jiaxu', '전위': 'dianwei', '진궁': 'chengong', '고순': 'gaoshun',
 '장합': 'zhanghe', '전풍': 'tianfeng', '저수': 'jushou', '서황': 'xuhuang', '조인': 'caoren', '정욱': 'chengyu', '순유': 'xunyou', '노숙': 'lusu',
 '여몽': 'lumeng', '황개': 'huanggai', '정보': 'chengpu', '주태': 'zhoutai', '방통': 'pangtong', '서서': 'xushu', '법정': 'fazheng', '위연': 'weiyan',
 '방덕': 'pangde', '장임': 'zhangren', '엄안': 'yanyan', '문빙': 'wenping', '한수': 'hansui', '기령': 'jiling', '국의': 'quyi', '초선': 'diaochan',
 '악진': 'yuejin', '우금': 'yujin', '괴월': 'kuaiyue', '심배': 'shenpei', '장소': 'zhangzhao', '진등': 'chendeng', '이전': 'lidian', '조홍': 'caohong',
 '장수': 'zhangxiu'}
FEMALE = {'초선', '대교', '여령기', '축융'}
# v0.3: 새로 그린 초상(주요 무장 79명) — art/por2_jobs.tsv 의 (키, 이름)
import os
_tsv = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art', 'por2_jobs.tsv')
for _ln in open(_tsv, encoding='utf-8'):
    _p = _ln.rstrip('\n').split('\t')
    if len(_p) >= 2 and _p[0]:
        assert _p[1] not in PORTRAIT, _p[1]
        PORTRAIT[_p[1]] = _p[0]

import roster17 as R17                              # v0.17: 더한 무장(맨 뒤에 붙인다 — 기존 번호가 바뀌지 않게)
CHA.update(R17.CHA17); SKILL.update(R17.SKILL17); FEMALE |= set(R17.WOMEN)
for _n, _w in R17.WOMEN.items():
    assert _n not in CHA and _n not in APT and _n not in SKILL and _n not in PORTRAIT and _w[7] not in PORTRAIT.values(), _n
    CHA[_n] = _w[4]; APT[_n] = _w[5]; SKILL[_n] = _w[6]
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art', 'raw17', _w[7] + '.png')): PORTRAIT[_n] = _w[7]
if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art', 'raw17', 'daqiao.png')): PORTRAIT['대교'] = 'daqiao'      # 그동안 공용 그림(gf1)을 썼다
import roster18 as R18                              # v0.18: 공용 초상을 쓰던 이름난 무장 60명에게 제 초상(그림이 있는 것만)
for _n, _k in R18.PORTRAIT18.items():
    assert _n not in PORTRAIT and _k not in PORTRAIT.values(), (_n, _k)
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art', 'raw18', _k + '.png')): PORTRAIT[_n] = _k

L = 'CBAS'
def jit(name, mod):
    return sum(ord(ch) for ch in name) % mod
def stats(name):
    if name in R17.WOMEN:
        w, l, i_, p = R17.WOMEN[name][:4]
        return w, l, i_, p, [1, 1, 1]
    if name in BASE: b = BASE[name]; return b['war'], b['ldr'], b['int'], b['pol'], b['apt3']
    if name in NEW:
        w, l, i_, p = NEW[name]
        a = 3 if w >= 82 else (2 if w >= 68 else 1)
        return w, l, i_, p, [a, a, 2 if (w >= 68 or i_ >= 85) else 1]
    raise KeyError(name)
def cha(name, w, l, i_, p):
    if name in CHA: return CHA[name]
    v = round((p * 0.45 + l * 0.35 + i_ * 0.2) * 0.85 + 6 + jit(name, 11))
    return max(15, min(88, v))
def apt(name, w, i_, a3):
    if name in APT: return APT[name]
    cav, inf, arc = a3
    sp = inf; hb = max(1, inf - (jit(name, 3) == 0))
    if jit(name, 5) == 1 and inf >= 2: sp, hb = max(1, inf - 1), inf
    sg = 3 if i_ >= 92 else (2 if i_ >= 80 else 1)
    return L[sp - 1] + L[hb - 1] + L[arc - 1] + L[cav - 1] + L[sg - 1]
def skill(name, w, l, i_, p, c, ap):
    if name in SKILL: return SKILL[name]
    h = jit(name, 997)
    if w >= 88:
        best = max(range(4), key=lambda k: ('CBAS'.index(ap[k]), -k))
        return ['창장', '극장', '궁장', '기장'][best]
    if i_ >= 88: return '간파'
    if w >= 78: return ['강행', '답파', '포박', '공성', '불굴', '급습'][h % 6]
    if i_ >= 78: return ['명경', '논객', '안력', '화공'][h % 4]
    if p >= 70: return ['능리', '번식', '축성', '부호', '미도', '둔전'][h % 6]
    if c >= 80: return '명성'
    if l >= 80: return '강행'
    return ''

officers = []
seen = set()
def add(name, fac, city, year=0, join=None, status='active'):
    assert name not in seen, name
    seen.add(name)
    w, l, i_, p, a3 = stats(name)
    c = cha(name, w, l, i_, p)
    ap = apt(name, w, i_, a3)
    sk = skill(name, w, l, i_, p, c, ap)
    por = PORTRAIT.get(name)
    if not por:
        if name in FEMALE: por = 'gf1' if name == '대교' else 'gf2'
        else: por = ('gm' if w >= i_ else 'gc') + str(1 + jit(name, 5))
    o = dict(n=name, ldr=l, war=w, int=i_, pol=p, cha=c, apt=ap, sk=sk, f=fac, c=city, por=por)
    if year: o['y'] = year
    if join: o['j'] = join
    if status != 'active': o['st'] = status
    officers.append(o)

facs = []
for fi, (lord, color, cities) in enumerate(FACTIONS):
    facs.append(dict(n=lord, color=color, cities=list(cities.keys())))
    for city, names in cities.items():
        for n in names: add(n, fi, city)
for f in FUTURE:
    add(f[0], -1, f[2], year=f[1], join=(f[3] if len(f) > 3 else None), status='hidden')
N_OLD = len(officers)
_lord = {f['n']: i for i, f in enumerate(facs)}
_city = set(c for f in facs for c in f['cities'])
for lord, cities in R17.ACTIVE17.items():
    for city, names in cities.items():
        assert city in facs[_lord[lord]]['cities'], (lord, city)
        for n in names: add(n, _lord[lord], city)
for f in R17.FUTURE17:
    assert len(f) < 4 or f[3] in _lord, f
    add(f[0], -1, f[2], year=f[1], join=(f[3] if len(f) > 3 else None), status='hidden')
assert all(n in seen for n in R17.WOMEN), [n for n in R17.WOMEN if n not in seen]

lord_idx = {f['n']: i for i, f in enumerate(facs)}
out = dict(factions=facs, officers=officers, women=sorted(n for n in seen if n in FEMALE), gates={k: (lord_idx[v] if v else -1) for k, v in GATE_OWNER.items()})
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('var SCENARIO=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('factions', len(facs), 'officers', len(officers), 'active', sum(1 for o in officers if o['f'] >= 0), 'old', N_OLD, 'new', len(officers) - N_OLD, 'women', sum(1 for o in officers if o['n'] in FEMALE))
_names = set(o['n'] for o in officers)
_bad = [n for n in PORTRAIT if n not in _names]
if _bad: print('로스터에 없는 초상 이름:', _bad)
from collections import Counter
print('skills', Counter(o['sk'] for o in officers).most_common())
print('portraits unique', len(set(o['por'] for o in officers if not o['por'].startswith('g'))), 'generic', sum(1 for o in officers if o['por'].startswith('g')))
missing = [n for n in PORTRAIT if n not in seen]
print('portrait names not in roster:', missing)
