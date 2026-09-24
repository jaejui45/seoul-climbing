#!/bin/bash
# 연결된 아이폰에 빌드해서 설치한다.
#   사전 준비: Xcode에 Apple ID 추가 + Local.xcconfig 의 DEVELOPMENT_TEAM 설정
#             아이폰에서 설정 → 개인정보 보호 및 보안 → 개발자 모드 켜기
set -euo pipefail
cd "$(dirname "$0")"

TEAM=$(grep -E '^DEVELOPMENT_TEAM' Local.xcconfig | sed 's/.*= *//')
if [ -z "$TEAM" ]; then
  echo "❌ Local.xcconfig 의 DEVELOPMENT_TEAM 이 비어 있습니다. 파일 안 설명을 참고하세요." >&2
  exit 1
fi

DEVICE=$(xcrun devicectl list devices 2>/dev/null | awk '$NF=="physical" && /connected/ {print $(NF-4); exit}')
if [ -z "${DEVICE:-}" ]; then
  echo "❌ 연결된 아이폰을 찾지 못했습니다. 케이블로 연결하고 '이 컴퓨터를 신뢰' 를 눌러주세요." >&2
  exit 1
fi

DD=build/device
echo "▶︎ 빌드 중…"
xcodebuild -project SeoulClimb.xcodeproj -scheme SeoulClimb \
  -configuration Debug -destination "id=$DEVICE" \
  -derivedDataPath "$DD" -allowProvisioningUpdates build

APP=$(find "$DD/Build/Products" -name 'SeoulClimb.app' -maxdepth 3 | head -1)
echo "▶︎ 설치 중: $APP"
xcrun devicectl device install app --device "$DEVICE" "$APP"
echo "✅ 완료. 아이폰 홈 화면에서 '서울클라이밍' 을 실행하세요."
echo "   처음 실행 시 설정 → 일반 → VPN 및 기기 관리 에서 개발자 앱을 신뢰해야 합니다."
