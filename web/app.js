'use strict';

const DAYS = ['월', '화', '수', '목', '금', '토', '일'];
const state = { gyms: [], updated: '', q: '', filter: 'all', near: false, showMap: true, here: null };

/* ── 영업시간 계산 (iOS 앱 Gym.swift와 동일한 규칙) ───────────────── */

// 사용자의 기기 시간대와 무관하게 항상 한국 시간 기준으로 판단한다.
function seoulNow(date = new Date()) {
  const p = new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Seoul', weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false,
  }).formatToParts(date);
  const get = (t) => p.find((x) => x.type === t).value;
  const wd = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].indexOf(get('weekday'));
  return { day: wd, minutes: (+get('hour') % 24) * 60 + +get('minute') };
}

const toMin = (hhmm) => {
  const [h, m] = hhmm.split(':').map(Number);
  return h * 60 + m;
};

function status(gym, now) {
  if (!gym.hours) return { kind: 'unknown', text: '시간 정보 없음' };

  // 전날 영업이 자정을 넘긴 경우
  const y = gym.hours[(now.day + 6) % 7];
  if (y && toMin(y[1]) > 1440 && now.minutes < toMin(y[1]) - 1440) {
    return { kind: 'open', text: `영업중 · ${y[1]} 종료` };
  }

  const h = gym.hours[now.day];
  if (!h) return { kind: 'shut', text: '오늘 휴무' };
  const [open, close] = [toMin(h[0]), toMin(h[1])];
  if (now.minutes >= open && now.minutes < close) {
    return { kind: 'open', text: `영업중 · ${h[1] === '24:00' ? '자정' : h[1]} 종료` };
  }
  if (now.minutes < open) return { kind: 'soon', text: `영업 전 · ${h[0]} 오픈` };
  return { kind: 'shut', text: '영업 종료' };
}

const hoursText = (gym, i) => {
  if (!gym.hours) return '정보 없음';
  const h = gym.hours[i];
  if (!h) return '휴무';
  return h[0] === '00:00' && h[1] === '24:00' ? '24시간' : `${h[0]} – ${h[1]}`;
};

/* ── 거리 ─────────────────────────────────────────────────────── */

function distance(a, b) {
  const R = 6371e3, rad = Math.PI / 180;
  const dLat = (b.lat - a.lat) * rad, dLon = (b.lon - a.lon) * rad;
  const s = Math.sin(dLat / 2) ** 2 +
    Math.cos(a.lat * rad) * Math.cos(b.lat * rad) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(s));
}
const fmtDist = (m) => (m < 1000 ? `${Math.round(m)}m` : `${(m / 1000).toFixed(1)}km`);

/* ── 필터 ─────────────────────────────────────────────────────── */

function visible(now) {
  const q = state.q.trim().toLowerCase();
  let list = state.gyms.filter((g) => {
    if (state.filter === 'open' && status(g, now).kind !== 'open') return false;
    if (state.filter === 'indoor' && g.category !== '실내 클라이밍장') return false;
    if (state.filter === 'outdoor' && g.category !== '야외 인공암벽') return false;
    if (!q) return true;
    return (g.name + g.district + g.address).toLowerCase().includes(q);
  });
  if (state.near && state.here) {
    list = [...list].sort((a, b) =>
      distance(state.here, { lat: a.latitude, lon: a.longitude }) -
      distance(state.here, { lat: b.latitude, lon: b.longitude }));
  }
  return list;
}

/* ── 렌더링 ───────────────────────────────────────────────────── */

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function card(gym, now) {
  const st = status(gym, now);
  const dist = state.here
    ? `<span class="dist">${fmtDist(distance(state.here, { lat: gym.latitude, lon: gym.longitude }))}</span>` : '';
  const rows = gym.hours
    ? gym.hours.map((_, i) =>
        `<tr class="${i === now.day ? 'today' : ''}"><td>${DAYS[i]}요일</td>` +
        `<td class="${gym.hours[i] ? '' : 'off'}">${hoursText(gym, i)}</td></tr>`).join('')
    : '<tr><td colspan="2">등록된 영업시간 정보가 없습니다.</td></tr>';
  const nq = encodeURIComponent(gym.name);
  const phone = gym.phone
    ? `<a href="tel:${gym.phone.replace(/[^0-9]/g, '')}">전화</a>` : '';

  return `<details class="gym">
    <summary>
      <div class="row1"><span class="name">${esc(gym.name)}</span>${dist}</div>
      <div class="meta">${esc(gym.district)} · ${gym.category === '실내 클라이밍장' ? '실내' : '야외 인공암벽'} · 오늘 ${hoursText(gym, now.day)}</div>
      <span class="badge ${st.kind}">${st.text}</span>
    </summary>
    <div class="detail">
      <table>${rows}</table>
      <p class="addr">${esc(gym.address)}</p>
      <div class="actions">
        <a class="primary" href="https://map.naver.com/p/search/${nq}" target="_blank" rel="noopener">네이버 지도</a>
        <a href="https://map.kakao.com/?q=${nq}" target="_blank" rel="noopener">카카오맵</a>
        <a href="https://maps.apple.com/?daddr=${gym.latitude},${gym.longitude}&q=${nq}&dirflg=r">길찾기</a>
        ${phone}
      </div>
      <p class="src">출처: ${esc(gym.source)} · 공휴일·세팅일에는 달라질 수 있어요.</p>
    </div>
  </details>`;
}

let map, layer;

function renderMap(list, now) {
  const el = document.getElementById('map');
  el.classList.toggle('hidden', !state.showMap);
  if (!state.showMap) return;

  if (!map) {
    map = L.map(el, { zoomControl: false, scrollWheelZoom: false }).setView([37.54, 126.99], 11);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors', maxZoom: 19,
    }).addTo(map);
    L.control.zoom({ position: 'bottomright' }).addTo(map);
    layer = L.layerGroup().addTo(map);
  } else {
    map.invalidateSize();
  }

  layer.clearLayers();
  const color = { open: '#17803d', soon: '#d97706', shut: '#b3261e', unknown: '#6c6c73' };
  list.forEach((g) => {
    const st = status(g, now);
    L.circleMarker([g.latitude, g.longitude], {
      radius: 8, weight: 2, color: '#fff', fillColor: color[st.kind], fillOpacity: 1,
    }).addTo(layer).bindPopup(
      `<b>${esc(g.name)}</b><br>${esc(g.district)} · 오늘 ${hoursText(g, now.day)}<br>${st.text}`);
  });
  if (state.here) {
    L.circleMarker([state.here.lat, state.here.lon], {
      radius: 6, weight: 3, color: '#1a73e8', fillColor: '#fff', fillOpacity: 1,
    }).addTo(layer).bindPopup('내 위치');
  }
}

function render() {
  const now = seoulNow();
  const list = visible(now);
  document.getElementById('list').innerHTML =
    list.length ? list.map((g) => card(g, now)).join('')
                : '<p class="empty">조건에 맞는 클라이밍장이 없습니다.</p>';
  document.getElementById('count').textContent =
    `${list.length}곳${state.near && state.here ? ' · 가까운 순' : ''}`;
  document.getElementById('foot').textContent =
    `영업시간 기준일 ${state.updated} · 방문 전 확인하세요`;
  renderMap(list, now);
}

/* ── 이벤트 ───────────────────────────────────────────────────── */

document.getElementById('q').addEventListener('input', (e) => {
  state.q = e.target.value;
  render();
});

document.getElementById('chips').addEventListener('click', (e) => {
  const btn = e.target.closest('.chip');
  if (!btn) return;
  const f = btn.dataset.f;

  if (f === 'map') {
    state.showMap = !state.showMap;
    btn.setAttribute('aria-pressed', String(state.showMap));
  } else if (f === 'near') {
    state.near = !state.near;
    btn.setAttribute('aria-pressed', String(state.near));
    if (state.near && !state.here) locate();
  } else {
    state.filter = f;
    document.querySelectorAll('.chip[data-f]').forEach((c) => {
      if (!['map', 'near'].includes(c.dataset.f)) {
        c.setAttribute('aria-pressed', String(c.dataset.f === f));
      }
    });
  }
  render();
});

function locate() {
  if (!navigator.geolocation) return;
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      state.here = { lat: pos.coords.latitude, lon: pos.coords.longitude };
      render();
    },
    () => {
      state.near = false;
      document.querySelector('.chip[data-f=near]').setAttribute('aria-pressed', 'false');
      render();
    },
    { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 });
}

fetch('gyms.json')
  .then((r) => r.json())
  .then((d) => {
    state.gyms = d.gyms;
    state.updated = d.updated;
    render();
    setInterval(render, 60000); // 영업 상태를 1분마다 갱신
  })
  .catch(() => {
    document.getElementById('list').innerHTML = '<p class="empty">데이터를 불러오지 못했습니다.</p>';
  });
