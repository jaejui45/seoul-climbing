# 서울 클라이밍장

서울시 클라이밍장의 위치와 영업시간을 보여주는 iOS 앱 + 모바일 웹.

## 구성

| 경로 | 내용 |
|---|---|
| `SeoulClimb/` | iOS 앱 (SwiftUI + MapKit, iOS 17+) |
| `web/` | 모바일 웹 / PWA (Leaflet + OpenStreetMap, 빌드 도구 없음) |
| `gyms.json` | **데이터 원본.** 두 앱이 같은 파일을 복사해 쓴다 |
| `curate.py` | 원천 데이터 정리 스크립트 |
| `sync-data.sh` | `curate.py` 실행 후 iOS·웹 양쪽에 복사 |

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

- 좌표와 요일별 영업시간: [Climblife](https://climblife.co.kr) 암장 DB (Google 지도 기준)
- 더클라임 서울 10개 지점: [공식 홈페이지](http://theclimb.co.kr/?portfolio=branch) 기준으로 덮어씀
- 폐점 지점(홍대·서울대·신사), 중복 항목, 클라이밍장이 아닌 시설은 제외

영업시간 판정은 iOS(`Gym.swift`)와 웹(`app.js`)이 같은 규칙을 쓴다.
기기 시간대와 상관없이 **항상 한국 시간(Asia/Seoul)** 기준이고,
자정 넘는 영업과 요일별 휴무를 함께 처리한다.

데이터를 고칠 때는 `curate.py`를 수정하고 `./sync-data.sh`를 실행한다.
