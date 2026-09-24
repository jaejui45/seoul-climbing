import json, re, os, urllib.request

# 원천 데이터: Climblife 암장 DB. 캐시가 없으면 내려받는다.
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gyms_raw.json')
if not os.path.exists(RAW):
    with urllib.request.urlopen('https://climblife.co.kr/api/gyms?limit=5000', timeout=30) as r:
        open(RAW, 'wb').write(r.read())
d = json.load(open(RAW))
S = [g for g in d['items'] if g['region']=='서울' or (g.get('address') or '').startswith('서울')]

DAYS = ['월','화','수','목','금','토','일']

def to24(ampm, h, m):
    h = int(h) % 12
    if ampm == '오후': h += 12
    return h, int(m)

def parse(hstr):
    """-> list of 7: None(휴무) | [open, close] 'HH:MM' | 'unknown'"""
    if not hstr or '준비중' in hstr: return None
    res = {}
    for line in hstr.split('\n'):
        m = re.match(r'^(.)요일:\s*(.*)$', line.strip())
        if not m: continue
        day, v = m.group(1), m.group(2)
        if '휴무' in v: res[day] = None; continue
        if '24시간' in v: res[day] = ['00:00','24:00']; continue
        parts = re.findall(r'(오전|오후)?\s*(\d{1,2}):(\d{2})', v)
        if len(parts) < 2: continue
        (a1,h1,m1),(a2,h2,m2) = parts[0], parts[1]
        oh, om = to24(a1 or '오전', h1, m1)
        if a2: ch, cm = to24(a2, h2, m2)
        else:
            # 오후/오전 생략된 종료시각 → 시작 기준으로 보정
            ch, cm = int(h2), int(m2)
            if ch <= oh and ch < 12: ch += 12
        if ch == 0 and cm == 0: ch = 24
        if ch < oh: ch += 24 if ch + 24 - oh <= 20 else 0
        res[day] = ['%02d:%02d' % (oh, om), '%02d:%02d' % (ch if ch <= 24 else ch-24, cm)]
    if len(res) < 7: return None
    return [res[x] for x in DAYS]

def wk(o, c, wo, wc):
    return [[o,c]]*5 + [[wo,wc]]*2

# 더클라임 공식 홈페이지(theclimb.co.kr/?portfolio=branch) 기준 덮어쓰기
THECLIMB = {
    '마곡': ('서울특별시 강서구 마곡동로 62 마곡사이언스타워 7층', '02-2668-5014', wk('09:30','23:30','08:00','22:00')),
    '양재': ('서울특별시 강남구 남부순환로 2615 지하1층', '02-576-8821', wk('08:00','24:00','08:00','22:00')),
    '신림': ('서울특별시 관악구 신원로 35 삼모더프라임타워 5층', '02-877-8821', wk('07:00','24:00','08:00','22:00')),
    '연남': ('서울특별시 마포구 양화로 186 LC타워 3층', '02-2088-5071', wk('07:00','24:00','08:00','22:00')),
    '강남': ('서울특별시 강남구 테헤란로8길 21 화인강남빌딩 지하1층', '02-566-8821', wk('08:00','24:00','08:00','22:00')),
    '사당': ('서울특별시 관악구 과천대로 939 지하2층', '02-585-8821', wk('08:00','24:00','08:00','22:00')),
    '논현': ('서울특별시 서초구 강남대로 519 지하1층', '02-545-5014', wk('08:00','24:00','08:00','22:00')),
    '문래': ('서울특별시 영등포구 당산로 63', '02-3667-5014', wk('07:00','24:00','08:00','22:00')),
    '이수': ('서울특별시 동작구 동작대로 59 지하1층', '02-588-5014', wk('08:00','24:00','08:00','22:00')),
    '성수': ('서울특별시 성동구 아차산로17길 49 지하1층', '02-499-5014', wk('08:00','24:00','08:00','22:00')),
}

EXCLUDE = ['배드민턴장', '주차장', '상상팡팡', '몽키즈', '파쿠르']
RENAME = [  # (패턴, 정리된 이름)
    (r'^더클라임.*?(마곡|양재|신림|연남|강남|사당|논현|문래|이수|성수)', lambda m: '더클라임 '+m.group(1)+'점'),
    (r'^PEAKERS 클라이밍 (\S+)', lambda m: '피커스 클라이밍 '+m.group(1)+'점'),
    (r'^피커스 클라이밍$', lambda m: '피커스 클라이밍 종로점'),
    (r'^알레클라이밍 강동점.*', lambda m: '알레클라이밍 강동점'),
    (r'^알레클라이밍\(ALLEZ.*', lambda m: '알레클라이밍 영등포점'),
    (r'^서울볼더스 클라이밍 컴퍼니.*|^서울볼더스 선유', lambda m: '서울볼더스 선유점'),
    (r'^서울볼더스 (클라이밍 )?목동점', lambda m: '서울볼더스 목동점'),
    (r'^산타클라이밍짐.*', lambda m: '산타클라이밍짐'),
    (r'^을지로 담장 클라이밍.*', lambda m: '을지로 담장 클라이밍'),
    (r'^은평\s*인공암벽장', lambda m: '은평 인공암벽장'),
    (r'^강서\s*(한강공원\s*)?인공암벽장?', lambda m: '강서한강공원 인공암벽장'),
    (r'^뚝섬한강공원\s*인공암벽장?', lambda m: '뚝섬한강공원 인공암벽장'),
    (r'^당고개(공원)?\s*인공암벽장', lambda m: '당고개공원 인공암벽장'),
    (r'^보라매공원(인공암벽등반장| 인공암벽장)?$', lambda m: '보라매공원 인공암벽장'),
    (r'^(용마폭포공원.*|중랑 스포츠 클라이밍 경기장|용마폭포공원 인공암벽장)$', lambda m: '중랑 스포츠클라이밍 경기장 (용마폭포공원)'),
    (r'^응봉산 암벽등반공원$', lambda m: '응봉산 암벽등반공원'),
]
ADDR_FIX = {
    '알레클라이밍 혜화점': '서울특별시 종로구 창경궁로34길 18-5 토가빌딩 지하2층',
    '알레클라이밍 영등포점': '서울특별시 영등포구 영등포로33길 14 스위트빌 B01호',
    '클라임웍스 클라이밍': '서울특별시 영등포구 버드나루로 85',
    '알레클라이밍 강동점': '서울특별시 강동구 천호대로177길 39 지하2층',
}
OUTDOOR_NAMES = ['인공암벽', '암벽등반공원', '경기장']

def district(addr):
    m = re.search(r'서울특별시\s+(\S+구)', addr) or re.search(r'(\S+구)\s', addr)
    return m.group(1) if m else ''

out = {}
for g in S:
    name = g['name'].strip()
    if any(x in name for x in EXCLUDE): continue
    for pat, fn in RENAME:
        m = re.match(pat, name)
        if m: name = fn(m); break
    addr = ADDR_FIX.get(name, g['address'])
    hours = parse(g.get('opening_hours'))
    phone = None; src = 'Google 지도 영업시간 (Climblife 수집)'
    tc = re.match(r'더클라임 (\S+)점', name)
    if tc and tc.group(1) in THECLIMB:
        addr, phone, hours = THECLIMB[tc.group(1)]; src = '더클라임 공식 홈페이지'
    outdoor = any(x in name for x in OUTDOOR_NAMES) and '클라이밍장' not in name
    rec = dict(name=name, category='야외 인공암벽' if outdoor else '실내 클라이밍장',
               district=district(addr), address=addr,
               latitude=round(float(g['latitude']),6), longitude=round(float(g['longitude']),6),
               phone=phone, hours=hours, rating=float(g['external_rating']) if g.get('external_rating') else None,
               ratingCount=g.get('external_rating_count') or 0, source=src)
    prev = out.get(name)
    if prev is None or (rec['ratingCount'] > prev['ratingCount']) or (prev['hours'] is None and rec['hours']):
        out[name] = rec

gyms = sorted(out.values(), key=lambda r: (r['category']!='실내 클라이밍장', r['district'], r['name']))
for i, g in enumerate(gyms, 1): g['id'] = i
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gyms.json')
updated = json.load(open(OUT))['updated'] if os.path.exists(OUT) else '2026-09-19'
json.dump({'updated': updated, 'gyms': gyms}, open(OUT, 'w'), ensure_ascii=False, indent=1)
print(len(gyms))
for g in gyms:
    h = g['hours']
    hs = '정보없음' if h is None else ' '.join(('휴' if x is None else x[0]+'-'+x[1]) for x in (h[0], h[5], h[6]))
    print(f"{g['id']:>2} {g['category'][:2]} {g['district']:<5} {g['name']:<28} {hs}")
