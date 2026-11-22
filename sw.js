/* 삼국지 천하도 — 서비스 워커: 한 번 연 뒤에는 인터넷이 없어도 열린다.
   · 화면(index.html): 저장해 둔 것을 바로 연다. 인터넷이 되면 먼저 서버의 것이 바뀌었는지만 짧게 묻고(HEAD, 2.5초까지),
     바뀌었으면 새 화면을 받아 저장한 뒤 그것을 연다. 그래서 새 판을 올리면 다음에 열 때 바로 바뀐다.
   · 아이콘·manifest: 저장해 둔 것을 쓴다. 바꾸면 SHELL 의 번호를 올린다(v0.18: 아이콘의 낙관이 天下圖 로 바뀌어 2).
   · 음악(bgm/*.mp3): 화면이 뜬 뒤에 차례로 받아 둔다(페이지가 'warm' 을 보낸다). 받아 둔 곡은 구간 요청(Range)에도 잘라서 답한다.
     곡을 바꾸면 BGM 의 번호를 올린다.
   · 영상(video/*.mp4 — v0.19): 음악과 같이 받아 두고 구간 요청에도 답한다(영상이 먼저, 그다음 음악). 영상을 바꾸면 VID 의 번호를 올린다.
   · 글꼴(Google Fonts): 받은 것을 저장해 두고 쓴다. */
var SHELL = 'chunhado-shell-2', BGM = 'chunhado-bgm-1', FONT = 'chunhado-font-1', VID = 'chunhado-video-1';
var HOME = new URL('./', self.registration.scope).href;
var SHELL_FILES = [HOME, 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/icon-maskable-512.png', 'icons/apple-touch-icon.png', 'icons/favicon-48.png'];
var BGM_FILES = ['title', 'field1', 'field2', 'tense', 'battle1', 'battle2', 'victory', 'defeat'].map(function (n) { return new URL('bgm/' + n + '.mp3', self.registration.scope).href; });
var VIDEO_FILES = ['title', 'opening', 'win', 'lose'].map(function (n) { return new URL('video/' + n + '.mp4', self.registration.scope).href; });

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(SHELL).then(function (c) { return c.addAll(SHELL_FILES); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.filter(function (k) { return k.indexOf('chunhado-') === 0 && k !== SHELL && k !== BGM && k !== FONT && k !== VID; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('message', function (e) {
  if (e.data === 'warm') e.waitUntil(warm(VID, VIDEO_FILES).then(function () { return warm(BGM, BGM_FILES); }));
});

/* 음악을 미리 받아 둔다. 이미 있는 곡은 건너뛰고, 한 곡씩 차례로. 실패해도 괜찮다 — 틀 때 인터넷에서 받는다 */
function warm(name, files) {
  return caches.open(name).then(function (c) {
    return files.reduce(function (p, u) {
      return p.then(function () {
        return c.match(u).then(function (hit) {
          if (hit) return;
          return fetch(u).then(function (r) { if (r && r.status === 200) return c.put(u, r); });
        });
      }).catch(function () { /* */ });
    }, Promise.resolve());
  });
}
function tag(r) { return r ? (r.headers.get('etag') || r.headers.get('last-modified') || '').replace(/^W\//, '') : ''; }
function within(p, ms) { return new Promise(function (ok, no) { var t = setTimeout(function () { no(new Error('timeout')); }, ms); p.then(function (v) { clearTimeout(t); ok(v); }, function (x) { clearTimeout(t); no(x); }); }); }
function fetchPage(c) {
  return fetch(HOME, { cache: 'no-store' }).then(function (r) {
    if (r && r.ok) return c.put(HOME, r.clone()).then(function () { return r; }, function () { return r; });
    return r;
  });
}
function page() {
  return caches.open(SHELL).then(function (c) {
    return c.match(HOME).then(function (hit) {
      if (!hit) return fetchPage(c);
      return within(fetch(HOME, { method: 'HEAD', cache: 'no-store' }), 2500).then(function (h) {
        if (h && h.ok && tag(h) && tag(h) !== tag(hit)) return fetchPage(c).then(function (r) { return r && r.ok ? r : hit; }, function () { return hit; });
        return hit;
      }, function () { return hit; });                       // 인터넷이 없거나 느리다 → 저장해 둔 화면
    });
  });
}
function media(req, name, type) {
  var url = req.url.split('?')[0];
  return caches.open(name).then(function (c) {
    return c.match(url).then(function (hit) {
      if (!hit) return fetch(req);                           // 아직 받아 두지 못한 곡
      var range = req.headers.get('range');
      if (!range) return hit;
      return hit.arrayBuffer().then(function (buf) {
        var m = /bytes=(\d*)-(\d*)/.exec(range), n = buf.byteLength, a, b;
        if (!m || (m[1] === '' && m[2] === '')) return new Response(buf, { status: 200, headers: { 'Content-Type': type, 'Content-Length': String(n) } });
        if (m[1] === '') { a = Math.max(0, n - (+m[2])); b = n - 1; } else { a = +m[1]; b = m[2] === '' ? n - 1 : Math.min(+m[2], n - 1); }
        if (a > b || a >= n) return new Response(null, { status: 416, headers: { 'Content-Range': 'bytes */' + n } });
        return new Response(buf.slice(a, b + 1), { status: 206, statusText: 'Partial Content',
          headers: { 'Content-Type': type, 'Content-Range': 'bytes ' + a + '-' + b + '/' + n, 'Content-Length': String(b - a + 1), 'Accept-Ranges': 'bytes' } });
      });
    });
  });
}
function shellFile(req) {
  return caches.open(SHELL).then(function (c) {
    return c.match(req, { ignoreSearch: true }).then(function (hit) {
      return hit || fetch(req).then(function (r) { if (r && r.ok && r.status === 200) c.put(req, r.clone()); return r; });
    });
  });
}
function font(e, req, keep) {
  return caches.open(FONT).then(function (c) {
    return c.match(req).then(function (hit) {
      if (hit && keep) return hit;                           // 글꼴 파일은 바뀌지 않는다
      var net = fetch(req).then(function (r) { if (r && r.ok) c.put(req, r.clone()); return r; });
      if (hit) { e.waitUntil(net.then(function () { /* */ }, function () { /* */ })); return hit; }   // 글꼴 목록(css)은 저장한 것을 쓰고 뒤에서 새로 받는다
      return net;
    });
  });
}
self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin === self.location.origin) {
    if (url.href.indexOf(self.registration.scope) !== 0) return;
    if (req.mode === 'navigate') {                          // 게임 화면만 맡는다. 다른 문서(옛 판 등)는 그대로 인터넷에서
      if (url.href.split('?')[0].split('#')[0] === HOME || url.pathname === new URL('index.html', self.registration.scope).pathname) e.respondWith(page());
      return;
    }
    if (/\/bgm\/[^/]+\.mp3$/.test(url.pathname)) { e.respondWith(media(req, BGM, 'audio/mpeg')); return; }
    if (/\/video\/[^/]+\.(mp4|webm)$/.test(url.pathname)) { e.respondWith(media(req, VID, /\.webm$/.test(url.pathname) ? 'video/webm' : 'video/mp4')); return; }
    e.respondWith(shellFile(req));
    return;
  }
  if (url.hostname === 'fonts.gstatic.com') e.respondWith(font(e, req, true));
  else if (url.hostname === 'fonts.googleapis.com') e.respondWith(font(e, req, false));
});
