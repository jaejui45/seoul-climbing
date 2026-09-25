#!/bin/bash
# gyms.json 단일 원본: 수집 결과를 iOS 앱과 웹에 함께 반영한다.
#   --collect 를 붙이면 카카오맵에서 데이터를 새로 수집한다 (수 분 소요).
#   붙이지 않으면 기존 gyms.json 을 그대로 복사만 한다.
set -e
cd "$(dirname "$0")"

if [ "${1:-}" = "--collect" ]; then
  rm -f kakao_cache.json
  python3 collect.py
fi

cp gyms.json SeoulClimb/Resources/gyms.json
cp gyms.json web/gyms.json
python3 - <<'PY'
import json
d = json.load(open('gyms.json'))
g = d['gyms']
hours = sum(1 for x in g if x['hours'])
print(f"동기화 완료 · {len(g)}곳 (영업시간 {hours}곳) · 기준일 {d['updated']}")
PY
