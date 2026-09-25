# 서울 클라이밍장

서울시 클라이밍장의 위치와 영업시간을 보여주는 iOS 앱 + 모바일 웹.

## 구성

| 경로 | 내용 |
|---|---|
| `SeoulClimb/` | iOS 앱 (SwiftUI + MapKit, iOS 17+) |
| `web/` | 모바일 웹 / PWA (Leaflet + OpenStreetMap, 빌드 도구 없음) |
| `gyms.json` | **데이터 원본.** 두 앱이 같은 파일을 복사해 쓴다 |
| `collect.py` | 카카오맵에서 데이터를 수집하는 스크립트 |
| `sync-data.sh` | iOS·웹 양쪽에 복사 (`--collect` 로 재수집) |

## iOS 앱 실행

```bash
open SeoulClimb.xcodeproj      # Xcode에서 ⌘R
```

프로젝트 파일은 [XcodeGen](https://github.com/yonaskolb/XcodeGen)으로 생성한다.
파일을 추가·삭제했으면 `xcodegen generate`를 다시 실행한다.

## 웹 실행

정적 파일이라 서버만 있으면 된다.

```bash
python3 -m http.server 5173 --directory web
```

휴대폰에서 같은 Wi-Fi로 `http://<맥의 IP>:5173` 접속. 공유 버튼 →
"홈 화면에 추가"를 누르면 앱처럼 전체 화면으로 실행된다.

### 배포

`web/` 폴더를 그대로 올리면 된다 (빌드 단계 없음).

- **GitHub Pages**: 저장소 Settings → Pages → 브랜치의 `/web` 폴더 지정
- **Vercel / Netlify**: 배포할 디렉터리를 `web`으로 지정

위치 기능(`navigator.geolocation`)은 HTTPS 또는 localhost에서만 동작한다.
위 서비스는 모두 HTTPS를 기본 제공한다.

## 데이터

서울 클라이밍장 **104곳** (실내 93 · 야외 인공암벽 11). 영업시간이 등록된 곳은 67곳.

출처는 셋이며, 정확한 순서대로 적용한다.

1. **체인 공식 홈페이지** — 더클라임 10개 지점
2. **카카오맵** — 업주가 직접 등록·관리하는 정보. 요일별 + 공휴일 영업시간
3. **Google 지도** ([Climblife](https://climblife.co.kr) 수집) — 카카오에 시간이 없는 곳 보충

각 암장의 `source` 와 `checked` 필드에 어느 출처에서 언제 갱신된 값인지 남긴다.
서울 외 지역, 용품점·협회 등 등반 시설이 아닌 곳, 60m 이내 중복은 제외한다.

```bash
./sync-data.sh --collect   # 카카오맵에서 새로 수집 후 앱·웹에 반영
```

영업시간 판정은 iOS(`Gym.swift`)와 웹(`app.js`)이 같은 규칙을 쓴다.
기기 시간대와 상관없이 **항상 한국 시간(Asia/Seoul)** 기준이고,
자정 넘는 영업과 요일별 휴무를 함께 처리한다.

데이터를 고칠 때는 `curate.py`를 수정하고 `./sync-data.sh`를 실행한다.
