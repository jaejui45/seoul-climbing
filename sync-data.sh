#!/bin/bash
# gyms.json 단일 원본: 데이터를 다시 만들고 iOS 앱과 웹에 함께 반영한다.
set -e
cd "$(dirname "$0")"
python3 curate.py > /dev/null
cp gyms.json SeoulClimb/Resources/gyms.json
cp gyms.json web/gyms.json
echo "gyms.json 동기화 완료 ($(python3 -c "import json;print(len(json.load(open('gyms.json'))['gyms']))")곳)"
