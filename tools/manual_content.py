# -*- coding: utf-8 -*-
# 매뉴얼 본문. (종류, 내용) 튜플의 리스트.
#   h1 대제목 / h2 중제목 / p 본문 / code 코드블록 / bullet 목록 / note 참고상자 / warn 주의상자
#   kv 표 (제목, [[열1,열2],...]) / pagebreak

DOC = [
 ("title", ("서울 클라이밍장 웹 — 수정·배포 매뉴얼",
            "직접 코드를 고치고 배포하기 위한 안내서 · 2026-09-24 기준")),

 ("h1", "0. 5분 요약"),
 ("p", "고치고 배포하는 전체 흐름은 이렇습니다. 자세한 설명은 뒤에 있습니다."),
 ("code", ["cd ~/Developer/SeoulClimb",
           "python3 -m http.server 5173 --directory web   # 1. 로컬 서버 켜기",
           "#    브라우저에서 http://localhost:5173 열기",
           "#    web/ 안의 파일을 고치고 브라우저 새로고침 (Cmd+Shift+R)",
           "",
           "git add -A && git commit -m \"무엇을 고쳤는지\" && git push   # 2. 배포"]),
 ("p", "push하면 GitHub이 자동으로 배포합니다. 1~2분 뒤 아래 주소에 반영됩니다."),
 ("url", "https://jaejui45.github.io/seoul-climbing/"),

 ("h1", "1. 파일 구조"),
 ("p", "수정할 것은 web/ 폴더 안의 파일 3개가 거의 전부입니다."),
 ("kv", ("", [
   ["web/index.html", "화면 뼈대. 제목, 검색창, 필터 버튼이 여기 있다"],
   ["web/style.css", "색과 디자인. 맨 위 :root 에 색상 변수가 모여 있다"],
   ["web/app.js", "동작 전부. 영업시간 계산, 필터, 목록·지도 그리기"],
   ["web/gyms.json", "암장 데이터 51곳. 직접 고치지 말 것 (3장 참고)"],
   ["web/*.png, icon.svg", "아이콘. make_icon.py 로 생성된 파일"],
   ["web/manifest.webmanifest", "홈 화면에 추가했을 때의 앱 이름·아이콘 설정"],
 ])),
 ("p", "web/ 바깥의 파일은 iOS 앱과 데이터 관리용입니다. 웹만 고칠 때는 건드리지 않아도 됩니다."),
 ("kv", ("", [
   ["gyms.json (루트)", "데이터 원본. web/ 과 iOS 앱이 이 파일을 복사해서 쓴다"],
   ["curate.py", "원천 데이터를 정리해 gyms.json 을 만드는 스크립트"],
   ["sync-data.sh", "curate.py 실행 후 web/ 과 iOS 앱에 복사"],
   ["SeoulClimb/", "iOS 앱 소스"],
   [".github/workflows/pages.yml", "push 하면 자동 배포하는 설정"],
 ])),

 ("h1", "2. 로컬에서 고치기"),
 ("h2", "서버 켜기"),
 ("p", "웹 파일은 그냥 열어도 되지만, gyms.json 을 불러오려면 서버가 필요합니다. 터미널에서:"),
 ("code", ["cd ~/Developer/SeoulClimb",
           "python3 -m http.server 5173 --directory web"]),
 ("p", "브라우저에서 http://localhost:5173 을 엽니다. 끌 때는 터미널에서 Ctrl+C 를 누릅니다."),
 ("note", "파일을 고쳐도 화면이 그대로면 브라우저가 옛 파일을 캐시한 것입니다. "
          "Cmd+Shift+R 로 강력 새로고침하세요."),

 ("h2", "아이폰에서 미리 보기"),
 ("p", "맥과 아이폰이 같은 Wi-Fi에 있으면, 배포 전에도 아이폰에서 확인할 수 있습니다. "
       "먼저 맥의 IP 주소를 확인합니다."),
 ("code", ["ipconfig getifaddr en0"]),
 ("p", "나온 주소(예: 192.168.0.76)를 아이폰 사파리에 http://192.168.0.76:5173 형태로 입력합니다."),
 ("warn", "이때 위치 기능(가까운 순)은 동작하지 않습니다. 브라우저는 HTTPS 또는 localhost 에서만 "
          "위치를 허용합니다. 위치까지 확인하려면 배포된 주소로 보셔야 합니다."),

 ("h2", "문법 오류 확인"),
 ("p", "JavaScript 를 고친 뒤 화면이 백지가 되면 문법 오류일 가능성이 큽니다. 두 가지로 확인합니다."),
 ("code", ["node --check web/app.js     # 문법만 빠르게 검사"]),
 ("p", "그리고 브라우저에서 우클릭 → 검사 → Console 탭을 보면 빨간 오류 메시지가 나옵니다. "
       "오류 줄 번호가 함께 표시되니 그 줄을 보면 됩니다."),

 ("pagebreak", None),

 ("h1", "3. 자주 하는 수정"),

 ("h2", "3-1. 색 바꾸기"),
 ("p", "web/style.css 맨 위의 :root 블록에 색이 모여 있습니다. 여기만 고치면 전체에 반영됩니다."),
 ("code", [":root {",
           "  --accent: #f26b21;   /* 주황. 선택된 버튼, 강조 */",
           "  --open:   #17803d;   /* 영업중 초록 */",
           "  --shut:   #b3261e;   /* 영업 종료 빨강 */",
           "  --soon:   #b45309;   /* 영업 전 주황 */",
           "  ...",
           "}"]),
 ("p", "아래쪽 @media (prefers-color-scheme: dark) 블록은 다크 모드용입니다. "
       "다크 모드 색도 같이 고쳐야 양쪽이 어울립니다."),
 ("note", "--open 과 --open-bg 는 한 쌍입니다. 글자색(--open)과 배지 배경색(--open-bg)이라 "
          "배경은 훨씬 연한 색을 씁니다."),

 ("h2", "3-2. 제목·문구 바꾸기"),
 ("p", "화면 맨 위 제목과 검색창 안내 문구는 web/index.html 에 있습니다."),
 ("code", ["<h1>서울 클라이밍장</h1>",
           "<input type=\"search\" id=\"q\" placeholder=\"이름, 구, 주소 검색\">"]),
 ("p", "브라우저 탭 이름과 홈 화면에 추가했을 때의 이름은 따로입니다."),
 ("code", ["<title>서울 클라이밍장</title>                     <!-- 탭 이름 -->",
           "<meta name=\"apple-mobile-web-app-title\" content=\"서울클라이밍\">  <!-- 홈 화면 -->"]),
 ("p", "홈 화면 이름은 web/manifest.webmanifest 의 short_name 도 함께 고쳐야 합니다."),

 ("h2", "3-3. 필터 버튼 추가하기"),
 ("p", "예를 들어 '24시간' 필터를 추가한다고 하면, 두 파일을 고칩니다."),
 ("p", "① web/index.html 의 버튼 목록에 한 줄 추가:"),
 ("code", ["<button class=\"chip\" data-f=\"allday\" aria-pressed=\"false\">24시간</button>"]),
 ("p", "② web/app.js 의 visible() 함수 안, 다른 필터 옆에 조건 한 줄 추가:"),
 ("code", ["function visible(now) {",
           "  ...",
           "  if (state.filter === 'open'   && status(g, now).kind !== 'open') return false;",
           "  if (state.filter === 'allday' && !g.hours?.every(h => h && h[1] === '24:00')) return false;",
           "  ...",
           "}"]),
 ("note", "data-f 값과 app.js 의 state.filter 비교 문자열이 같아야 합니다. "
          "여기서는 둘 다 'allday' 입니다."),

 ("h2", "3-4. 목록 카드에 항목 추가하기"),
 ("p", "카드 한 장을 그리는 곳은 app.js 의 card() 함수입니다. HTML을 문자열로 만들어 돌려줍니다. "
       "예를 들어 평점을 보여주려면 .meta 줄에 끼워 넣습니다."),
 ("code", ["<div class=\"meta\">${esc(gym.district)} · ${...} · 오늘 ${hoursText(gym, now.day)}",
           "  ${gym.rating ? ` · ★ ${gym.rating}` : ''}",
           "</div>"]),
 ("warn", "사용자에게 보여줄 문자열은 반드시 esc() 로 감싸세요. "
          "데이터에 <, > 같은 문자가 있으면 화면이 깨지거나 보안 문제가 생깁니다. "
          "숫자(좌표, 평점)는 감쌀 필요 없습니다."),

 ("h2", "3-5. 지도 바꾸기"),
 ("p", "지도는 Leaflet + OpenStreetMap 입니다. app.js 의 renderMap() 안에 있습니다."),
 ("code", ["map = L.map(el, { zoomControl: false, scrollWheelZoom: false })",
           "      .setView([37.54, 126.99], 11);   // 초기 중심 좌표와 확대 수준"]),
 ("p", "핀 색은 바로 아래 color 객체에서 정합니다. 영업 상태별로 다릅니다."),
 ("code", ["const color = { open: '#17803d', soon: '#d97706',",
           "                shut: '#b3261e', unknown: '#6c6c73' };"]),
 ("warn", "OpenStreetMap 기본 타일은 개인용 수준의 트래픽만 허용합니다. "
          "사람이 많이 쓰게 되면 MapTiler 같은 서비스의 무료 키를 받아 타일 주소를 바꾸세요."),

 ("pagebreak", None),

 ("h1", "4. 암장 데이터 고치기"),
 ("warn", "web/gyms.json 을 직접 고치지 마세요. sync-data.sh 를 실행하면 덮어써집니다. "
          "진짜 원본은 프로젝트 루트의 gyms.json 이고, 그것도 curate.py 가 만듭니다."),
 ("h2", "데이터 한 건의 생김새"),
 ("code", ["{",
           " \"name\": \"더클라임 강남점\",",
           " \"category\": \"실내 클라이밍장\",     // 또는 \"야외 인공암벽\"",
           " \"district\": \"강남구\",",
           " \"address\": \"서울특별시 강남구 테헤란로8길 21 ...\",",
           " \"latitude\": 37.497516,",
           " \"longitude\": 127.031979,",
           " \"phone\": \"02-566-8821\",          // 없으면 null",
           " \"hours\": [ [\"08:00\",\"24:00\"], ... ],  // 월~일 7개",
           " \"rating\": 4.4, \"ratingCount\": 36,",
           " \"source\": \"더클라임 공식 홈페이지\"",
           "}"]),
 ("p", "hours 는 월요일부터 일요일까지 7개입니다. 값의 의미는 이렇습니다."),
 ("kv", ("", [
   ["[\"10:00\", \"23:00\"]", "그 요일 영업시간"],
   ["null", "그 요일 휴무"],
   ["[\"00:00\", \"24:00\"]", "24시간"],
   ["hours 자체가 null", "영업시간 정보 없음 (회색 배지)"],
 ])),
 ("note", "자정을 넘겨 새벽까지 여는 곳은 종료 시각을 24 시 이후로 적습니다. "
          "예를 들어 새벽 2시까지면 [\"18:00\", \"26:00\"] 입니다. 앱이 알아서 처리합니다."),

 ("h2", "고치는 방법"),
 ("p", "curate.py 안에 수정용 표가 들어 있습니다. 상황에 맞는 곳을 고칩니다."),
 ("kv", ("", [
   ["THECLIMB", "더클라임 지점의 주소·전화·영업시간을 공식 정보로 덮어쓰는 표"],
   ["EXCLUDE", "이름에 이 단어가 들어가면 목록에서 빼는 설정"],
   ["RENAME", "지저분한 상호명을 깔끔하게 바꾸는 규칙"],
   ["ADDR_FIX", "주소가 깨진 곳을 바로잡는 표"],
 ])),
 ("p", "고친 뒤에는 반드시 아래를 실행해야 web/ 과 iOS 앱에 반영됩니다."),
 ("code", ["cd ~/Developer/SeoulClimb",
           "./sync-data.sh"]),
 ("p", "실행하면 \"gyms.json 동기화 완료 (51곳)\" 처럼 출력됩니다. "
       "기준일을 바꾸려면 루트 gyms.json 의 updated 값을 직접 고치면 됩니다."),

 ("pagebreak", None),

 ("h1", "5. 배포하기"),
 ("h2", "기본 흐름"),
 ("p", "GitHub에 push 하면 자동으로 배포됩니다. 별도 명령이 없습니다."),
 ("code", ["cd ~/Developer/SeoulClimb",
           "git add -A",
           "git commit -m \"영업시간 갱신\"",
           "git push"]),
 ("p", "push 후 1~2분이면 아래 주소에 반영됩니다."),
 ("url", "https://jaejui45.github.io/seoul-climbing/"),

 ("h2", "배포 상태 확인"),
 ("p", "배포가 잘 됐는지 터미널에서 볼 수 있습니다."),
 ("code", ["gh run list --limit 3      # 최근 배포 3건의 성공/실패",
           "gh run watch              # 진행 중인 배포를 실시간으로 보기"]),
 ("p", "completed success 로 나오면 성공입니다. failure 면 아래 명령으로 원인을 봅니다."),
 ("code", ["gh run view --log-failed"]),
 ("p", "웹 브라우저로는 저장소의 Actions 탭에서 같은 내용을 볼 수 있습니다."),
 ("url", "https://github.com/jaejui45/seoul-climbing/actions"),

 ("h2", "배포했는데 화면이 그대로일 때"),
 ("bullet", [
   "브라우저 캐시입니다. Cmd+Shift+R (아이폰은 사파리 설정에서 기록 지우기)",
   "gh run list 로 배포가 실제로 성공했는지 확인",
   "git status 로 커밋을 빠뜨린 파일이 없는지 확인",
   "홈 화면에 추가한 아이콘으로 열었다면, 지우고 다시 추가해야 반영될 때가 있습니다",
 ]),

 ("h2", "되돌리기"),
 ("p", "잘못 배포했을 때 직전 상태로 돌아가는 방법입니다."),
 ("code", ["git log --oneline -5           # 돌아갈 지점 확인",
           "git revert HEAD               # 마지막 커밋을 취소하는 새 커밋 생성",
           "git push"]),
 ("note", "git reset 대신 git revert 를 쓰세요. 이미 push 한 내용을 reset 으로 지우면 "
          "기록이 어긋나 다음 push 가 막힙니다."),

 ("h1", "6. 막혔을 때"),
 ("kv", ("", [
   ["화면이 백지", "node --check web/app.js 로 문법 확인, 브라우저 Console 확인"],
   ["데이터가 안 보임", "서버 없이 파일을 직접 열었는지 확인. http.server 로 열어야 함"],
   ["위치가 안 잡힘", "HTTPS 에서만 동작. localhost 나 배포 주소로 확인"],
   ["지도가 회색", "인터넷 연결 확인. 타일은 외부에서 받아옴"],
   ["git push 거부됨", "git pull --rebase 후 다시 push"],
   ["배포 실패", "gh run view --log-failed 로 로그 확인"],
 ])),
 ("h2", "원래대로 되돌리고 싶을 때"),
 ("p", "고치다 꼬였는데 아직 커밋 전이라면, 마지막 커밋 상태로 전부 되돌립니다."),
 ("code", ["git checkout -- web/        # web/ 폴더의 수정 전부 취소",
           "git status                 # 지금 뭐가 바뀌었는지 확인"]),

 ("h1", "7. 참고"),
 ("kv", ("", [
   ["배포 주소", "https://jaejui45.github.io/seoul-climbing/"],
   ["저장소", "https://github.com/jaejui45/seoul-climbing"],
   ["로컬 폴더", "~/Developer/SeoulClimb"],
   ["데이터 기준일", "2026-09-19 (암장 51곳)"],
 ])),
 ("p", "영업시간 판정 규칙은 웹(app.js)과 iOS 앱(SeoulClimb/Models/Gym.swift)이 동일합니다. "
       "한쪽 규칙을 고치면 다른 쪽도 같이 고쳐야 두 앱이 같은 결과를 냅니다."),
 ("p", "Leaflet 사용법은 leafletjs.com 문서에, GitHub Actions 배포 설정은 "
       ".github/workflows/pages.yml 에 있습니다."),
]
