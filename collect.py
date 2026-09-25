# -*- coding: utf-8 -*-
"""서울 클라이밍장 데이터 수집.

카카오맵을 단일 출처로 쓴다. 업주가 직접 관리하는 정보라 요일별 영업시간과
공휴일 영업시간까지 가장 정확하다.

  1단계  m.map.kakao.com 검색으로 25개 구를 훑어 장소 ID를 모은다
  2단계  place.map.kakao.com API 로 각 장소의 상세 정보를 받는다
  3단계  서울 외 지역, 클라이밍장이 아닌 곳, 중복을 걸러낸다
  4단계  체인 공식 홈페이지 정보로 덮어쓴다 (브랜드가 직접 고지한 값 우선)

결과는 gyms.json 으로 저장된다. 실행 후 ./sync-data.sh 로 앱과 웹에 반영한다.
"""
import json, re, os, time, math, difflib, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
UA_MOBILE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15'
UA_DESKTOP = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
GU = ['종로구','중구','용산구','성동구','광진구','동대문구','중랑구','성북구','강북구','도봉구',
      '노원구','은평구','서대문구','마포구','양천구','강서구','구로구','금천구','영등포구','동작구',
      '관악구','서초구','강남구','송파구','강동구']
DAYS = ['월','화','수','목','금','토','일']

def get(url, ua=UA_DESKTOP, referer=None, as_json=False):
    h = {'User-Agent': ua, 'Accept': 'application/json' if as_json else '*/*'}
    if referer:
        h['Referer'] = referer
    req = urllib.request.Request(url, headers=h)
    raw = urllib.request.urlopen(req, timeout=25).read()
    return json.loads(raw) if as_json else raw.decode('utf-8', 'replace')

# ── 1단계: 장소 ID 수집 ────────────────────────────────────────────────
ITEM = re.compile(r'<li class="search_item[^"]*"([^>]*)>')
ATTR = re.compile(r'data-([a-z]+)="([^"]*)"')

def collect_ids():
    found = {}
    for gu in GU:
        for term in ('클라이밍', '암벽'):
            for page in (1, 2, 3):
                url = ('https://m.map.kakao.com/actions/searchView?q='
                       + urllib.parse.quote(f'서울 {gu} {term}') + f'&page={page}')
                try:
                    html = get(url, ua=UA_MOBILE)
                except Exception as e:
                    print(f'  검색 실패 {gu} {term} {page}: {e}')
                    continue
                items = [dict(ATTR.findall(m.group(1))) for m in ITEM.finditer(html)]
                items = [a for a in items if a.get('type') == 'place' and a.get('id')]
                if not items:
                    break
                for a in items:
                    found.setdefault(a['id'], a.get('title', ''))
                time.sleep(0.3)
        print(f'  {gu} 누적 {len(found)}')
    return list(found)

# ── 2단계: 상세 정보 ───────────────────────────────────────────────────
def fetch_detail(pid):
    j = get(f'https://place.map.kakao.com/places/panel3/{pid}',
            referer=f'https://place.map.kakao.com/{pid}', as_json=True)
    s = j.get('summary') or {}
    oh = j.get('open_hours') or {}
    periods = (oh.get('all') or {}).get('periods') or []
    base = next((p for p in periods if '기본' in (p.get('period_title') or '')), None)
    if base is None and periods:
        base = periods[0]
    holiday = next((p for p in periods if '공휴일' in (p.get('period_title') or '')), None)

    def times(day):
        t = (day.get('on_days') or {}).get('start_end_time_desc')
        if not t:
            return None
        m = re.match(r'(\d{1,2}:\d{2})\s*~\s*(\d{1,2}:\d{2})', t)
        if not m:
            return None
        o, c = m.group(1), m.group(2)
        # 자정을 넘겨 새벽까지 여는 경우 종료 시각을 24시 이후로 표현한다
        if _min(c) <= _min(o):
            c = '%02d:%s' % (int(c[:2]) + 24, c[3:])
        return [o, c]

    hours = None
    if base:
        byday = {d.get('day_of_the_week'): times(d) for d in (base.get('days') or [])}
        if any(byday.values()):
            hours = [byday.get(d) for d in DAYS]

    hol = None
    if holiday and (holiday.get('days') or []):
        hol = times(holiday['days'][0])

    return {
        'kakaoId': str(pid),
        'name': s.get('name'),
        'kakaoCategory': (s.get('category') or {}).get('name'),
        'latitude': (s.get('point') or {}).get('lat'),
        'longitude': (s.get('point') or {}).get('lon'),
        'address': (s.get('address') or {}).get('road') or (s.get('address') or {}).get('disp'),
        'regions': [r.get('name') for r in (s.get('regions') or [])],
        'phone': next((p.get('tel') for p in (s.get('phone_numbers') or [])), None),
        'link': next(iter(s.get('homepages') or []), None),
        'hours': hours,
        'holidayHours': hol,
        'kakaoUpdated': (s.get('meta') or {}).get('updated_at', '')[:10] or None,
        'status': s.get('status'),
    }

def _min(hhmm):
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)

# ── 3단계: 걸러내기 ────────────────────────────────────────────────────
CATEGORY_OK = {'클라이밍'}
# 카테고리가 클라이밍이 아니어도 실제 등반 시설인 곳
NAME_KEEP = ('인공암벽', '암벽장', '실내암벽', '암벽공원')
# 이름만 클라이밍이고 등반 시설이 아닌 곳
NAME_DROP = ('협회', '공장', '용품', '아크테릭스', '블랙다이아몬드', '그리벨',
             '라이튼클라이밍', '화장실', '음수대', '주차장', '학교', '대학교')

def is_gym(p):
    name = p['name'] or ''
    if any(k in name for k in NAME_DROP):
        return False
    if p['kakaoCategory'] in CATEGORY_OK:
        return True
    return any(k in name for k in NAME_KEEP)

def haversine(a, b):
    R, rad = 6371000, math.pi / 180
    dlat, dlon = (b[0] - a[0]) * rad, (b[1] - a[1]) * rad
    s = (math.sin(dlat / 2) ** 2
         + math.cos(a[0] * rad) * math.cos(b[0] * rad) * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(s))

def score(p):
    """중복일 때 어느 쪽을 남길지: 영업시간 > 주소 > 전화 > 최신순"""
    return (p['hours'] is not None, bool(p['address']), bool(p['phone']),
            p.get('kakaoUpdated') or '')

def dedupe(places):
    kept = []
    for p in sorted(places, key=score, reverse=True):
        dup = next((q for q in kept
                    if haversine((p['latitude'], p['longitude']),
                                 (q['latitude'], q['longitude'])) < 60), None)
        if dup:
            # 같은 건물의 같은 시설 — 빠진 정보만 보충한다
            for k in ('phone', 'link', 'hours', 'holidayHours', 'address'):
                if not dup.get(k) and p.get(k):
                    dup[k] = p[k]
            dup.setdefault('aliases', []).append(p['name'])
            continue
        kept.append(p)
    return kept

# ── 4단계: 체인 공식 정보 덮어쓰기 ────────────────────────────────────
def wk(o, c, wo, wc):
    return [[o, c]] * 5 + [[wo, wc]] * 2

# theclimb.co.kr/?portfolio=branch (2026-09-24 확인)
THECLIMB = {
    '마곡': ('02-2668-5014', wk('09:30', '23:30', '08:00', '22:00')),
    '양재': ('02-576-8821',  wk('08:00', '24:00', '08:00', '22:00')),
    '신림': ('02-877-8821',  wk('07:00', '24:00', '08:00', '22:00')),
    '연남': ('02-2088-5071', wk('07:00', '24:00', '08:00', '22:00')),
    '강남': ('02-566-8821',  wk('08:00', '24:00', '08:00', '22:00')),
    '사당': ('02-585-8821',  wk('08:00', '24:00', '08:00', '22:00')),
    '논현': ('02-545-5014',  wk('08:00', '24:00', '08:00', '22:00')),
    '문래': ('02-3667-5014', wk('07:00', '24:00', '08:00', '22:00')),
    '이수': ('02-588-5014',  wk('08:00', '24:00', '08:00', '22:00')),
    '성수': ('02-499-5014',  wk('08:00', '24:00', '08:00', '22:00')),
}

def apply_official(p):
    m = re.match(r'더클라임\s*(\S+?)점', p['name'] or '')
    if m and m.group(1) in THECLIMB:
        phone, hours = THECLIMB[m.group(1)]
        p['phone'], p['hours'] = phone, hours
        p['source'] = '더클라임 공식 홈페이지'
        p['name'] = f'더클라임 {m.group(1)}점'
    elif not p.get('source'):
        # 보조 출처에서 이미 표시한 경우에는 덮어쓰지 않는다
        p['source'] = '카카오맵 (업체 등록 정보)'
    return p

# ── 5단계: 보조 출처로 영업시간 보충 ─────────────────────────────────
# 카카오에 영업시간을 등록하지 않은 곳은 Climblife(구글 지도 기반)에서 가져온다.
# 출처가 다르므로 source 에 구분해 남긴다.
FALLBACK_URL = 'https://climblife.co.kr/api/gyms?limit=5000'
AMPM = re.compile(r'(오전|오후)\s*(\d{1,2}):(\d{2})')

def _norm(name):
    """비교용 이름: 공백/영문/괄호/흔한 접미어를 떼어낸다."""
    n = re.sub(r'[A-Za-z()\[\],.\-_/]', '', name or '')
    n = re.sub(r'\s+', '', n)
    for w in ('클라이밍짐', '클라이밍센터', '클라이밍', '볼더링', '암벽장', '인공암벽', '짐', '센터'):
        n = n.replace(w, '')
    return n

def _same_place(a, b):
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return False
    if na in nb or nb in na:
        return True
    return difflib.SequenceMatcher(None, na, nb).ratio() >= 0.6

def _parse_fallback_hours(text):
    """'월요일: 오전 11:00 ~ 오후 11:00' 7줄 → hours 배열"""
    res = {}
    for line in (text or '').split('\n'):
        m = re.match(r'^(.)요일:\s*(.*)$', line.strip())
        if not m:
            continue
        day, v = m.group(1), m.group(2)
        if '휴무' in v:
            res[day] = None
            continue
        if '24시간' in v:
            res[day] = ['00:00', '24:00']
            continue
        parts = AMPM.findall(v)
        if len(parts) < 2:
            # 종료 시각에 오전/오후가 빠진 경우
            nums = re.findall(r'(\d{1,2}):(\d{2})', v)
            if len(parts) == 1 and len(nums) == 2:
                a1, h1, m1 = parts[0]
                oh = int(h1) % 12 + (12 if a1 == '오후' else 0)
                ch, cm = int(nums[1][0]), nums[1][1]
                if ch <= oh and ch < 12:
                    ch += 12
                res[day] = ['%02d:%s' % (oh, m1), '%02d:%s' % (ch, cm)]
            continue
        (a1, h1, m1), (a2, h2, m2) = parts[0], parts[1]
        oh = int(h1) % 12 + (12 if a1 == '오전' and False else (12 if a1 == '오후' else 0))
        ch = int(h2) % 12 + (12 if a2 == '오후' else 0)
        if ch == 0 and m2 == '00':
            ch = 24
        res[day] = ['%02d:%s' % (oh, m1), '%02d:%s' % (ch, m2)]
    return [res[d] for d in DAYS] if len(res) == 7 else None

def fill_missing_hours(places):
    try:
        items = get(FALLBACK_URL, as_json=True)['items']
    except Exception as e:
        print(f'  보조 출처를 불러오지 못했습니다: {e}')
        return 0
    cands = [x for x in items
             if (x.get('address') or '').startswith('서울') and x.get('opening_hours')]
    filled = 0
    for p in places:
        if p['hours']:
            continue
        for c in cands:
            d = haversine((p['latitude'], p['longitude']),
                          (float(c['latitude']), float(c['longitude'])))
            if d > 150 or not _same_place(p['name'], c['name']):
                continue
            hours = _parse_fallback_hours(c['opening_hours'])
            if hours:
                p['hours'] = hours
                p['source'] = 'Google 지도 (Climblife 수집)'
                filled += 1
            break
    return filled

# ── 실행 ───────────────────────────────────────────────────────────────
def main():
    cache = os.path.join(HERE, 'kakao_cache.json')
    if os.path.exists(cache):
        details = json.load(open(cache))
        print(f'캐시 사용: {len(details)}건 (다시 수집하려면 {os.path.basename(cache)} 삭제)')
    else:
        print('1단계 · 장소 ID 수집')
        ids = collect_ids()
        print(f'2단계 · 상세 정보 {len(ids)}건')
        details = []
        for i, pid in enumerate(ids, 1):
            try:
                details.append(fetch_detail(pid))
            except Exception as e:
                print(f'  실패 {pid}: {e}')
            if i % 20 == 0:
                print(f'  {i}/{len(ids)}')
            time.sleep(0.25)
        json.dump(details, open(cache, 'w'), ensure_ascii=False, indent=1)

    print('3단계 · 걸러내기')
    seoul = [p for p in details
             if p.get('latitude') and p.get('status') == 'Y'
             and (p.get('regions') or [''])[0] == '서울' and is_gym(p)]
    print(f'  서울 클라이밍 시설 {len(seoul)}건')
    seoul = dedupe(seoul)
    print(f'  중복 제거 후 {len(seoul)}건')

    print('5단계 · 보조 출처로 영업시간 보충')
    print(f'  {fill_missing_hours(seoul)}곳 보충')

    print('4단계 · 공식 정보 반영')
    gyms = []
    for p in map(apply_official, seoul):
        outdoor = any(k in (p['name'] or '') for k in NAME_KEEP)
        gyms.append({
            'name': p['name'],
            'category': '야외 인공암벽' if outdoor else '실내 클라이밍장',
            'district': (p['regions'] or ['', ''])[1] if len(p['regions']) > 1 else '',
            'address': p['address'],
            'latitude': round(p['latitude'], 6),
            'longitude': round(p['longitude'], 6),
            'phone': p['phone'],
            'hours': p['hours'],
            'holidayHours': p['holidayHours'],
            'link': p['link'],
            'kakaoId': p['kakaoId'],
            'source': p['source'],
            'checked': p.get('kakaoUpdated'),
        })

    gyms.sort(key=lambda g: (g['category'] != '실내 클라이밍장', g['district'], g['name']))
    for i, g in enumerate(gyms, 1):
        g['id'] = i

    out = os.path.join(HERE, 'gyms.json')
    updated = time.strftime('%Y-%m-%d')
    json.dump({'updated': updated, 'source': '카카오맵', 'gyms': gyms},
              open(out, 'w'), ensure_ascii=False, indent=1)

    with_hours = sum(1 for g in gyms if g['hours'])
    print(f'\n완료: {len(gyms)}곳 (영업시간 있음 {with_hours}곳, 없음 {len(gyms) - with_hours}곳)')
    print(f'  실내 {sum(1 for g in gyms if g["category"] == "실내 클라이밍장")}곳 · '
          f'야외 {sum(1 for g in gyms if g["category"] == "야외 인공암벽")}곳')
    print(f'→ {out}')

if __name__ == '__main__':
    main()
