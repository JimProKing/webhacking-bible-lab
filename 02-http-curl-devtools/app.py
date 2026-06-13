"""
02-http-curl-devtools: HTTP 기초 정복 - 브라우저 개발자도구 + curl 직접 보내기/받기
크리핵티브 웹 해킹 바이블 Ch02 기초

목표:
- Burp 없이도 HTTP 요청/응답을 "직접" 만들고 관찰하는 근육을 만든다.
- 브라우저 DevTools (Network 탭)으로 실제 트래픽을 보고 → "Copy as cURL" → 터미널에서 편집/재전송 연습.
- curl (Windows: curl.exe)의 기본부터 쿠키, 헤더 조작까지 단계별로 체득.
- 나중에 Burp를 만나면 "이게 왜 편한지"를 제대로 이해하게 함.

실행:
    cd 02-http-curl-devtools
    python app.py
    브라우저: http://127.0.0.1:5003
"""

from flask import Flask, request, render_template_string, make_response, redirect, url_for, jsonify
import sqlite3
import json

app = Flask(__name__)
app.secret_key = "curl-devtools-study-only"

def get_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            phone TEXT,
            email TEXT,
            is_admin INTEGER DEFAULT 0
        )
    """)
    c.executemany("""
        INSERT INTO users (username, name, phone, email, is_admin) VALUES (?, ?, ?, ?, ?)
    """, [
        ("chulsu", "철수", "010-1234-5678", "chulsu@example.com", 0),
        ("sumi", "수미", "010-9876-5432", "sumi@example.com", 0),
        ("admin", "관리자", "010-0000-0000", "admin@secret.local", 1),
    ])
    return conn

DB = get_db()

INDEX_HTML = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>02-http-curl-devtools | HTTP 기초 + curl + DevTools</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    .code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; background:#f8f9fa; padding:8px 12px; border-radius:6px; }
    .mission { background:#fff3cd; border-left:5px solid #ffc107; }
    pre { background:#212529; color:#d4d4d4; padding:12px; border-radius:6px; overflow-x:auto; }
    .step { counter-increment: step; }
    .step:before { content: counter(step); background:#0d6efd; color:white; width:24px; height:24px; display:inline-flex; align-items:center; justify-content:center; border-radius:50%; margin-right:8px; font-size:13px; }
  </style>
</head>
<body class="bg-light">
<div class="container py-4" style="max-width: 980px;">

  <!-- 로그인 상태 표시 헤더 (로그인/로그아웃 경험 개선) -->
  {% if current_user %}
  <div class="d-flex justify-content-between align-items-center mb-3 p-3 bg-success bg-opacity-10 border border-success rounded">
    <div>
      <strong>✅ 로그인 상태:</strong> 
      <span class="fw-bold">{{ current_user.name }}</span> 
      ({{ current_user.username }})
      {% if current_user.is_admin %}
        <span class="badge bg-danger ms-1">관리자</span>
      {% endif %}
    </div>
    <div>
      <a href="/myinfo" class="btn btn-sm btn-success">내 정보 보기</a>
      <a href="/logout" class="btn btn-sm btn-outline-danger">로그아웃</a>
    </div>
  </div>
  {% else %}
  <div class="d-flex justify-content-between align-items-center mb-3 p-2 bg-light border rounded small">
    <div><strong>로그인되지 않음</strong></div>
    <div><a href="#login-form" class="btn btn-sm btn-outline-primary">로그인 폼으로 이동</a></div>
  </div>
  {% endif %}

  <div class="text-center mb-3">
    <h1 class="fw-bold">02-http-curl-devtools</h1>
    <p class="text-muted mb-1">브라우저 개발자도구 + <strong>curl로 직접 HTTP 주고받기</strong> 연습</p>
    <p class="small text-danger fw-semibold">Burp Suite는 잠시 내려놓고, 먼저 "직접 손으로" HTTP를 느끼자!</p>
  </div>

  <div class="alert alert-info">
    <strong>이 섹션의 핵심 목표</strong><br>
    1. 브라우저 DevTools Network 탭으로 실제 요청/응답 구조를 눈으로 확인<br>
    2. "Copy as cURL" 기능을 100번 반복해서 손에 익히기<br>
    3. 터미널(PowerShell)에서 curl.exe 로 요청을 <strong>직접 작성하고</strong> 수정해서 보내기<br>
    4. 쿠키/헤더/바디를 수동으로 조작하는 감각 기르기<br>
    <strong>5. 개발자도구 Console에서 fetch()로 로그인/요청 보내기 (이번에 집중!)</strong>
  </div>

  <!-- 사전 준비 -->
  <div class="card mb-3">
    <div class="card-header bg-dark text-white">0. Windows에서 curl 준비 확인 (5초 컷)</div>
    <div class="card-body small">
      <p class="mb-1">PowerShell을 열고 아래를 입력해보세요:</p>
      <pre>curl.exe --version</pre>
      <p class="mb-1 mt-2">curl.exe 가 없으면 Windows 10/11 최신 버전이면 이미 들어있습니다. (빌드 17063 이상)</p>
      <p class="text-muted small mb-0">참고: PowerShell에서 그냥 <code>curl</code> 이라고 치면 <strong>Invoke-WebRequest</strong>의 별칭(alias)이 실행됩니다. 
      진짜 curl을 쓰고 싶으면 <strong>curl.exe</strong> 라고 명시하세요.</p>
    </div>
  </div>

  <div class="row g-3">
    <!-- GET + 파라미터 -->
    <div class="col-md-6">
      <div class="card h-100">
        <div class="card-header">1. GET 요청 + 쿼리 파라미터 조작</div>
        <div class="card-body">
          <p><strong>의도:</strong> ?user 값을 바꿔서 다른 사람 정보 보기 (권한 체크 없음)</p>
          
          <form action="/profile" method="GET" class="mb-3">
            <div class="input-group">
              <span class="input-group-text">user</span>
              <input type="text" name="user" class="form-control" value="chulsu">
              <button class="btn btn-primary">브라우저로 보기</button>
            </div>
          </form>

          <div class="mission p-2 rounded mb-2 small">
            <strong>DevTools + curl 미션</strong><br>
            1. 브라우저에서 위 폼 제출 (chulsu)<br>
            2. F12 → Network 탭 열기 → "profile" 요청 찾기 → 우클릭 → <strong>Copy → Copy as cURL (cmd)</strong><br>
            3. PowerShell에 붙여넣기 후 실행<br>
            4. 명령어 끝에 <code>?user=sumi</code> 로 바꿔서 다시 실행해보기
          </div>

          <div class="small text-muted">
            추천 curl 명령어 (복사해서 사용):
          </div>
          <pre class="small">curl.exe "http://127.0.0.1:5003/profile?user=sumi" -v</pre>
          <pre class="small">curl.exe "http://127.0.0.1:5003/profile?user=admin" -i</pre>
        </div>
      </div>
    </div>

    <!-- POST -->
    <div class="col-md-6" id="login-form">
      <div class="card h-100">
        <div class="card-header">2. POST 요청 + Body (form data)</div>
        <div class="card-body">
          <form action="/login" method="POST" class="mb-3">
            <div class="mb-2">
              <input type="text" name="username" class="form-control" value="chulsu">
            </div>
            <div class="mb-2">
              <input type="password" name="password" class="form-control" value="test123">
            </div>
            <button class="btn btn-success w-100">로그인 (브라우저)</button>
          </form>

          <div class="mission p-2 rounded mb-2 small">
            <strong>curl 미션</strong><br>
            로그인 폼을 브라우저로 한 번 전송 → Network에서 POST /login 찾기 → Copy as cURL<br>
            그 다음 PowerShell에서 직접 아래처럼 작성해보기:
          </div>

          <pre class="small">curl.exe "http://127.0.0.1:5003/login" `
  -X POST `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=chulsu&password=test123" `
  -i</pre>
        </div>
      </div>
    </div>
  </div>

  <!-- 쿠키 / 세션 -->
  <div class="card mt-3">
    <div class="card-header">3. 쿠키 다루기 (가장 중요!)</div>
    <div class="card-body">
      <p>로그인 후 발급되는 <code>session_user</code> 쿠키를 curl로 직접 주고받는 연습.</p>
      
      <a href="/myinfo" class="btn btn-outline-dark btn-sm" target="_blank">브라우저로 /myinfo 보기 (쿠키 필요)</a>

      <div class="mt-3">
        <div class="small fw-bold">curl로 쿠키를 다루는 기본 패턴 (반드시 외우기):</div>
        <pre class="small"># 1. 로그인하면서 쿠키 파일로 저장
curl.exe "http://127.0.0.1:5003/login" -X POST -d "username=chulsu&password=test123" -c cookies.txt -i

# 2. 저장된 쿠키를 사용해서 요청 보내기
curl.exe "http://127.0.0.1:5003/myinfo" -b cookies.txt -i

# 3. 쿠키 값을 직접 조작해서 보내기 (수동 세션 하이재킹)
curl.exe "http://127.0.0.1:5003/myinfo" -b "session_user=admin" -i</pre>
      </div>

      <div class="alert alert-warning small mt-2 mb-0">
        <strong>실전 미션</strong>: 위 명령어로 chulsu로 로그인한 후, <code>session_user=admin</code> 으로 직접 바꿔서 관리자 정보가 나오는지 확인하세요.
      </div>
    </div>
  </div>

  <!-- Debug / Echo -->
  <div class="card mt-3 border-success">
    <div class="card-header bg-success text-white">4. 최고의 연습 도구: /debug/echo (요청을 그대로 돌려줌)</div>
    <div class="card-body">
      <p class="small">이 엔드포인트는 받은 요청의 <strong>method, headers, cookies, query, body 전부</strong>를 JSON으로 돌려줍니다. curl 실험할 때 최고의 친구.</p>
      
      <div class="row">
        <div class="col-md-6">
          <div class="small">기본 사용법:</div>
          <pre class="small">curl.exe "http://127.0.0.1:5003/debug/echo" -v</pre>
          <pre class="small">curl.exe "http://127.0.0.1:5003/debug/echo?foo=bar&test=123"</pre>
        </div>
        <div class="col-md-6">
          <div class="small">헤더 + 바디 실험:</div>
          <pre class="small">curl.exe "http://127.0.0.1:5003/debug/echo" `
  -H "X-My-Header: hello" `
  -H "User-Agent: MyCustomAgent/1.0" `
  -d "name=grok&role=hacker"</pre>
        </div>
      </div>
      <div class="small text-muted">PowerShell에서 줄바꿈은 백틱(`) 사용. 한 줄로 이어서 써도 됩니다.</div>
    </div>
  </div>

  <!-- ========== 5. 브라우저 콘솔(fetch) 실습 섹션 (사용자 요청) ========== -->
  <div class="card mt-3 border-primary">
    <div class="card-header bg-primary text-white">
      5. 개발자도구 Console에서 fetch()로 로그인 성공시키기 ★
    </div>
    <div class="card-body">
      <p class="small mb-2"><strong>목표:</strong> F12 → Console 탭에서 JavaScript fetch로 POST 로그인 요청을 직접 보내고, 브라우저 쿠키에 세션을 심어서 /myinfo가 로그인 상태로 보이게 만들기.</p>

      <div class="alert alert-warning small py-2">
        <strong>가장 중요한 포인트</strong><br>
        <code>credentials: 'include'</code> 를 꼭 넣어야 쿠키가 요청에 포함되고, 응답의 Set-Cookie가 브라우저에 저장됩니다.<br>
        (curl에서는 -b/-c로 직접 관리했지만, 브라우저 fetch는 이 옵션으로 자동 처리)
      </div>

      <h6 class="mt-3">실습 1: chulsu로 로그인 (Console에 붙여넣기)</h6>
      <pre class="small">fetch("http://127.0.0.1:5003/login", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({ username: "chulsu", password: "test123" }),
  credentials: "include"
})
.then(r => { console.log("상태코드:", r.status); return r.text(); })
.then(html => console.log("응답 일부:", html.slice(0, 300)));</pre>

      <h6 class="mt-3">실습 2: 로그인 후 /myinfo 확인 (쿠키가 제대로 심겼는지)</h6>
      <pre class="small">fetch("http://127.0.0.1:5003/myinfo", { credentials: "include" })
.then(r => r.text())
.then(t => console.log(t));</pre>

      <div class="small text-muted mt-1">위 두 개를 순서대로 Console에 붙여넣고 실행해보세요. 그 후 브라우저에서 직접 http://127.0.0.1:5003/myinfo 새로고침 해보면 로그인 상태가 유지되어 있을 겁니다.</div>

      <h6 class="mt-3">실습 3: admin으로 로그인 + 내 정보 확인 (한 번에)</h6>
      <pre class="small">// 한 번에 admin 로그인하고 바로 확인
fetch("http://127.0.0.1:5003/login", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: "username=admin&password=test123",
  credentials: "include"
})
.then(r => r.text())
.then(() => fetch("http://127.0.0.1:5003/myinfo", {credentials:"include"}))
.then(r => r.text())
.then(console.log);</pre>

      <h6 class="mt-3">실습 4: /debug/echo 로 요청이 어떻게 왔는지 Console에서 보기 (JSON 편하게)</h6>
      <pre class="small">fetch("http://127.0.0.1:5003/debug/echo?format=json", { credentials: "include" })
  .then(r => r.json())
  .then(console.log);</pre>

      <h6 class="mt-3">실습 5: 로그아웃 (새로 추가된 기능)</h6>
      <pre class="small">// Console에서 로그아웃
fetch("/logout", { method: "POST", credentials: "include" })
  .then(r => { console.log("로그아웃 상태:", r.status); location.reload(); });

// 또는 단순 GET
// location.href = "/logout";</pre>
      <div class="small text-muted">로그아웃 후 브라우저 새로고침하거나 <code>/myinfo</code> 를 다시 fetch 해보면 쿠키가 사라진 걸 확인할 수 있습니다.</div>

      <h6 class="mt-3">팁: async/await로 편하게 여러 번 쓰기</h6>
      <pre class="small">// Console에 한 번 붙여넣고, 그 뒤로 login() 또는 check() 라고만 치면 됨
async function loginAs(user, pw) {
  const res = await fetch("/login", {
    method: "POST",
    headers: {"Content-Type": "application/x-www-form-urlencoded"},
    body: new URLSearchParams({username: user, password: pw}),
    credentials: "include"
  });
  console.log("로그인 응답 상태:", res.status);
  return res.text();
}
async function checkMyInfo() {
  const r = await fetch("/myinfo", {credentials:"include"});
  console.log(await r.text());
}
async function whoAmI() {
  const r = await fetch("/debug/echo?format=json", {credentials:"include"});
  console.log(await r.json());
}

// 사용 예
// loginAs("chulsu", "test123").then(checkMyInfo)
// whoAmI()</pre>

      <div class="mt-2 p-2 bg-light border rounded small">
        <strong>Network 탭 관찰 방법:</strong><br>
        Console에서 fetch를 실행하는 동안 <strong>Network 탭을 열어두세요</strong>. 
        "login", "myinfo" 요청이 보이고, Headers / Payload / Cookies 탭에서 상세 내용을 볼 수 있습니다.<br>
        이게 바로 "Burp 없이도 DevTools로 충분히 분석/실험 가능"하다는 걸 보여줍니다.
      </div>
    </div>
  </div>
  <!-- ========== Console 실습 섹션 끝 ========== -->

  <!-- ========== 6. 요청 가로채기(Intercept) + 세션 하이재킹 맛보기 ========== -->
  <div class="card mt-3 border-danger">
    <div class="card-header bg-danger text-white">
      6. 요청 가로채기 &amp; 하이재킹 (DevTools로 직접 해보기) ★
    </div>
    <div class="card-body">
      <p class="small"><strong>너가 지금까지 한 건 "직접 작성해서 보내기"</strong>였다.<br>
      이제부터는 <strong>"브라우저가 원래 보내려던 요청을 가로채서" 수정하고 재전송</strong>하는 걸 배운다.</p>

      <div class="alert alert-primary small py-2">
        이게 바로 Burp Suite가 하는 일의 기초다. 지금은 DevTools만으로 어느 정도까지 가능한지 먼저 체험하자.
      </div>

      <h6 class="mt-2">방법 1: DevTools Network 탭으로 요청 "가로채기" (Edit and Resend가 안 보일 때 대처법 포함)</h6>
      
      <div class="alert alert-danger small py-1">
        <strong>회원 정보 보기 클릭해도 Fetch/XHR에 아무것도 안 뜨는 이유</strong><br>
        현재 페이지의 "회원 정보 보기"와 로그인 폼은 <strong>일반 form submit</strong>이라 브라우저가 <u>전체 페이지를 새로 불러</u>옵니다 (document navigation).<br>
        Fetch/XHR 필터는 <strong>자바스크립트 fetch()나 XMLHttpRequest</strong> 요청만 보여줍니다.
      </div>

      <div class="alert alert-info small py-1">
        <strong>해결: 아래 버튼을 사용하세요</strong> (이 버튼들은 fetch()로 요청을 보내서 Fetch/XHR에 제대로 잡힙니다)
      </div>

      <div class="row g-2 mb-3">
        <!-- GET Profile fetch button -->
        <div class="col-md-6">
          <div class="card card-body p-2">
            <div class="input-group input-group-sm mb-1">
              <span class="input-group-text">user=</span>
              <input id="int-user" type="text" class="form-control" value="chulsu">
              <button class="btn btn-primary btn-sm" onclick="interceptDemoProfile()">회원정보 fetch 요청 보내기</button>
            </div>
            <small class="text-muted">이 버튼 클릭 → Network 탭에서 <strong>Fetch/XHR</strong> 필터 켜기 → profile 요청이 나타남</small>
          </div>
        </div>

        <!-- POST Login fetch button -->
        <div class="col-md-6">
          <div class="card card-body p-2">
            <button class="btn btn-success btn-sm w-100 mb-1" onclick="interceptDemoLogin()">로그인 fetch 요청 (chulsu / test123)</button>
            <small class="text-muted">로그인도 fetch로 보냅니다. Network에 POST 요청이 잡혀요.</small>
          </div>
        </div>
      </div>

      <div id="intercept-result" class="small border p-2 bg-light mb-2" style="display:none; white-space:pre-wrap; font-family:monospace; max-height: 140px; overflow:auto;"></div>

      <strong>가로채기 연습 방법 (이제 제대로 보일 거예요)</strong>
      <ol class="small">
        <li>위 버튼 중 하나를 클릭하세요.</li>
        <li><strong>F12 → Network</strong> 탭 열기</li>
        <li>상단 <strong>"Fetch/XHR"</strong> 필터를 클릭해서 켜세요.</li>
        <li>요청 목록에 <code>/profile</code> 또는 <code>/login</code> 이 나타날 거예요.</li>
        <li>그 요청을 <strong>우클릭 → Copy → Copy as fetch</strong></li>
        <li>Console에 붙여넣은 뒤, <code>user=xxx</code> 나 body 데이터를 고쳐서 다시 실행해보세요.</li>
      </ol>
      <div class="small text-success fw-bold">이제부터는 이 버튼들로 연습하면 Fetch/XHR에 항상 잘 보입니다.</div>

      <h6 class="mt-3">방법 2: 로그인 요청 가로채서 쿠키 값 훔쳐보기 (Set-Cookie 관찰)</h6>
      <ol class="small">
        <li>로그인 폼으로 chulsu / test123 전송 (브라우저 폼 직접 사용)</li>
        <li>Network 탭에서 <code>login</code> POST 요청 찾기</li>
        <li>요청을 클릭 → 오른쪽에 <strong>Response Headers</strong> 탭 열기</li>
        <li><code>Set-Cookie: session_user=chulsu; HttpOnly</code> 라인을 찾음</li>
        <li>이 값을 복사 → 이게 바로 "세션 토큰"이다.</li>
      </ol>
      <p class="small text-muted">HttpOnly 때문에 JavaScript로 <code>document.cookie</code>로는 읽을 수 없지만, 프록시나 이 방법으로 값을 알게 되면 공격자가 사용할 수 있다.</p>

      <h6 class="mt-3">하이재킹 (Session Hijacking) 실습 — 가능하다!</h6>
      <p class="small"><strong>예:</strong> 철수가 로그인한 상태에서, 공격자가 철수의 쿠키 값을 알아낸 상황을 재현해보자.</p>

      <div class="border p-2 rounded mb-2 small bg-light">
        <strong>단계:</strong><br>
        1. 정상적으로 로그인 (폼 클릭)<br>
        2. Network에서 login 응답의 <code>Set-Cookie</code> 값 확인 → <code>session_user=chulsu</code> 복사<br>
        3. 새 탭이나 시크릿 모드에서 이 사이트 다시 열기 (로그인 안 된 상태)<br>
        4. Console에 아래 붙여넣기 (쿠키를 강제로 넣어서 요청):
        <pre class="small mt-1 mb-1">fetch("/myinfo", {
  credentials: "include",
  headers: {
    "Cookie": "session_user=chulsu"   // ← 훔친 값으로 강제 설정
  }
}).then(r => r.text()).then(console.log);</pre>
        5. 또는 curl로:
        <pre class="small">curl.exe "http://127.0.0.1:5003/myinfo" -H "Cookie: session_user=chulsu" -i</pre>
        <strong>결과:</strong> 철수의 정보가 그대로 나온다! → 이것이 세션 하이재킹.
      </div>

      <div class="alert alert-warning small">
        <strong>왜 이게 가능한가?</strong><br>
        이 랩의 쿠키는 서명(signature)도 없고, 예측 가능하며, HttpOnly지만 값만 알면 누구나 사용할 수 있다.<br>
        실제 서비스에서는 Secure, HttpOnly + SameSite + 서명(session signing) + 짧은 만료시간 등을 써서 방어한다.
      </div>

      <h6 class="mt-3">방법 3: 진짜 제대로 가로채고 싶다면? → Proxy (Burp 소개)</h6>
      <p class="small">DevTools의 "Edit and Resend"는 <strong>한 번에 한 요청만</strong> 수정할 수 있다.<br>
      모든 트래픽을 실시간으로 가로채서, 자동으로 수정하고, Repeater로 반복 보내고 싶다면 <strong>프록시 도구</strong>가 필요하다.</p>
      <ul class="small">
        <li>Burp Suite Community (무료) 설치</li>
        <li>FoxyProxy로 브라우저 트래픽을 127.0.0.1:8080 으로 돌림</li>
        <li>이제 페이지에서 아무거나 클릭/전송하면 <strong>Burp의 Proxy Intercept</strong>에 걸림</li>
        <li>Headers, Body 마음대로 고치고 Forward</li>
        <li>한 번 보낸 요청은 Repeater에 저장해서 계속 변조 가능</li>
      </ul>
      <p class="small text-muted">지금 너가 curl과 Console fetch로 배운 모든 게 Burp 안에서는 훨씬 편하게, 자동으로, 히스토리까지 보면서 할 수 있게 된다.</p>

      <div class="small mt-2">
        <strong>다음 단계 추천:</strong> 이 섹션의 실습을 모두 해봤으면, "Burp로 넘어가자"고 말해. 그 때부터 진짜 강력한 가로채기 도구를 배운다.
      </div>
    </div>
  </div>
  <!-- ========== 가로채기 & 하이재킹 섹션 끝 ========== -->

  <div class="mt-4 p-3 bg-white border rounded">
    <h6 class="mb-2">추가 추천 연습 (직접 해보기)</h6>
    <ul class="small mb-0">
      <li><code>curl.exe ... -v</code> : verbose 모드. 요청 헤더 + 응답 헤더 + TLS handshake 전부 보기 (강추)</li>
      <li><code>curl.exe ... -i</code> : response headers 포함해서 출력</li>
      <li><code>curl.exe ... -o response.html</code> : 응답을 파일로 저장</li>
      <li><code>curl.exe ... -H "Cookie: session_user=admin"</code> : -b 대신 직접 헤더로 쿠키 넣기</li>
      <li>로그인 후 받은 <strong>Set-Cookie</strong> 값을 직접 복사해서 다음 curl에 넣어보기</li>
      <li>여러 개의 -H 옵션으로 커스텀 헤더 여러 개 동시에 보내기</li>
      <li><strong>Console fetch</strong>로도 동일한 공격(파라미터 변조, 쿠키 위장)을 해보기</li>
      <li><strong>로그아웃</strong>: <code>fetch("/logout", {method:"POST", credentials:"include"})</code> 또는 <code>curl ... /logout</code></li>
    </ul>
  </div>

  <div class="text-center mt-4">
    <a href="/debug/echo" class="btn btn-sm btn-outline-success" target="_blank">/debug/echo 바로가기 (브라우저)</a>
    <span class="ms-2 text-muted small">Console에서 <code>fetch("/debug/echo?format=json", {credentials:"include"}).then(r=>r.json()).then(console.log)</code> 해보세요!</span>
  </div>
</div>

<script>
// DevTools 가로채기 연습용 fetch 버튼들 (Fetch/XHR에 제대로 나타나게 함)
async function interceptDemoProfile() {
  const user = document.getElementById('int-user').value || 'chulsu';
  const resultBox = document.getElementById('intercept-result');
  resultBox.style.display = 'block';
  resultBox.innerHTML = '요청 보내는 중... (Network 탭 확인!)';

  try {
    const res = await fetch(`/profile?user=${encodeURIComponent(user)}`, {
      credentials: 'include'
    });
    const html = await res.text();
    resultBox.innerHTML = `<strong>응답 (처음 400자):</strong><br>` + html.replace(/</g, '&lt;').slice(0, 400);
    console.log('%c[DevTools 실습] profile 요청 완료. Network 탭에서 Fetch/XHR 필터를 켜고 "profile" 요청을 우클릭 → Copy as fetch 해보세요!', 'color:#0d6efd');
  } catch(e) {
    resultBox.innerHTML = '에러: ' + e;
  }
}

async function interceptDemoLogin() {
  const resultBox = document.getElementById('intercept-result');
  resultBox.style.display = 'block';
  resultBox.innerHTML = '로그인 요청 보내는 중... (Network 탭 확인!)';

  try {
    const res = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'username=chulsu&password=test123',
      credentials: 'include'
    });
    const html = await res.text();
    resultBox.innerHTML = `<strong>로그인 응답 (일부):</strong><br>` + html.replace(/</g, '&lt;').slice(0, 300);
    console.log('%c[DevTools 실습] login POST 완료. Network에서 "login" 요청을 우클릭해서 Copy as fetch 하세요. Set-Cookie도 Response Headers에서 확인!', 'color:#198754');
    
    // 로그인 성공 후 상태 바를 업데이트하려면 페이지 새로고침 권장
    setTimeout(() => {
      resultBox.innerHTML += '<br><span style="color:#dc3545">※ 상단 로그인 상태 바를 업데이트하려면 페이지 새로고침 하세요.</span>';
    }, 800);
  } catch(e) {
    resultBox.innerHTML = '에러: ' + e;
  }
}

// 편의를 위해 원래 있던 loginAs 함수도 유지 (이미 이전에 안내함)
console.log('%c[안내] interceptDemoProfile() 과 interceptDemoLogin() 함수가 추가되었습니다. Network에서 Fetch/XHR 필터를 켜고 위 버튼들을 눌러보세요.', 'color:gray');
</script>
</body>
</html>
"""

PROFILE_HTML = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <title>회원 정보 | curl-devtools</title>
</head>
<body class="bg-light">
<div class="container py-4" style="max-width: 620px;">
  <h2>회원 정보 조회 결과</h2>
  {% if user %}
  <div class="card">
    <div class="card-body">
      <table class="table table-sm mb-0">
        <tr><th>아이디</th><td>{{ user.username }}</td></tr>
        <tr><th>이름</th><td>{{ user.name }}</td></tr>
        <tr><th>전화번호</th><td>{{ user.phone }}</td></tr>
        <tr><th>이메일</th><td>{{ user.email }}</td></tr>
        <tr><th>관리자?</th><td>{{ '예' if user.is_admin else '아니오' }}</td></tr>
      </table>
    </div>
  </div>
  <div class="alert alert-danger mt-3 small">
    이 결과는 <strong>curl로 ?user= 값을 직접 바꿔서</strong>도 똑같이 얻을 수 있습니다.<br>
    DevTools에서 Copy as cURL 한 뒤 파라미터만 수정해서 다시 보내세요.
  </div>
  {% else %}
  <div class="alert alert-secondary">사용자를 찾을 수 없습니다.</div>
  {% endif %}
  <a href="/" class="btn btn-secondary btn-sm mt-2">← 메인으로</a>
</div>
</body>
</html>
"""

LOGIN_HTML = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <title>로그인 결과 | curl-devtools</title>
</head>
<body class="bg-light">
<div class="container py-4" style="max-width: 520px;">

  <div class="d-flex justify-content-between mb-2">
    <a href="/" class="btn btn-sm btn-outline-secondary">← 홈으로</a>
    <a href="/logout" class="btn btn-sm btn-outline-danger">로그아웃</a>
  </div>

  <h2>로그인 결과</h2>
  <div class="alert {% if success %}alert-success{% else %}alert-danger{% endif %}">
    {{ message }}
  </div>
  {% if success %}
    <a href="/myinfo" class="btn btn-primary">내 정보 보기 (/myinfo)</a>
    <a href="/logout" class="btn btn-outline-danger ms-2">로그아웃 테스트</a>
    <div class="small text-muted mt-2">로그인 성공 후 curl이나 Console fetch로 쿠키를 조작해보세요.</div>
  {% else %}
    <a href="/" class="btn btn-secondary btn-sm mt-2">다시 로그인하기</a>
  {% endif %}
</div>
</body>
</html>
"""

MYINFO_HTML = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <title>내 정보 | curl-devtools</title>
</head>
<body class="bg-light">
<div class="container py-4" style="max-width: 620px;">

  <!-- 간단한 상단 상태 -->
  {% if user %}
  <div class="d-flex justify-content-between align-items-center mb-3 p-2 bg-success bg-opacity-10 border border-success rounded">
    <div><strong>현재 로그인:</strong> {{ user.name }} ({{ user.username }})</div>
    <div>
      <a href="/" class="btn btn-sm btn-outline-secondary">홈</a>
      <a href="/logout" class="btn btn-sm btn-outline-danger">로그아웃</a>
    </div>
  </div>
  {% endif %}

  <h2>내 정보 (쿠키 기반)</h2>
  {% if user %}
  <div class="card">
    <div class="card-body">
      <p>안녕하세요, <strong>{{ user.name }}</strong>님!</p>
      <p>전화번호: {{ user.phone }}</p>
      <p>이메일: {{ user.email }}</p>
      {% if user.is_admin %}
        <div class="alert alert-danger py-1 small">🎉 관리자 권한! (curl/fetch로 session_user=admin 쿠키를 직접 넣어서 도달했습니다)</div>
      {% endif %}
    </div>
  </div>

  <div class="mt-3">
    <a href="/logout" class="btn btn-danger">로그아웃 하기 (쿠키 삭제)</a>
    <a href="/" class="btn btn-secondary ms-2">← 메인으로</a>
  </div>
  {% else %}
  <div class="alert alert-danger">로그인이 필요합니다. (쿠키 없음)</div>
  <a href="/" class="btn btn-secondary btn-sm mt-2">← 메인으로 (로그인 폼)</a>
  {% endif %}

  <div class="mt-3 p-3 bg-white border rounded small">
    <strong>연습 포인트 (curl / Console fetch)</strong><br>
    • 로그인 후 쿠키를 <code>-b "session_user=admin"</code> 로 바꿔서 admin 정보 보기<br>
    • Console에서 <code>fetch('/logout', {method:'POST', credentials:'include'})</code> 로 로그아웃 테스트<br>
    • 로그아웃 후 다시 /myinfo 가면 "로그인 필요" 가 나와야 정상
  </div>
</div>
</body>
</html>
"""

@app.route("/")
def index():
    # 로그인 상태를 템플릿에 전달 (콘솔/fetch/curl 연습에 유용)
    session_user = request.cookies.get("session_user")
    current_user = None
    if session_user:
        c = DB.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (session_user,))
        row = c.fetchone()
        if row:
            current_user = dict(row)
    return render_template_string(INDEX_HTML, current_user=current_user)

@app.route("/profile")
def profile():
    username = request.args.get("user", "chulsu")
    c = DB.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    user = dict(row) if row else None
    return render_template_string(PROFILE_HTML, user=user)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect(url_for("index"))
    
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    
    success = False
    message = "로그인 실패"
    
    if username == "chulsu" and password == "test123":
        success = True
        message = "철수 로그인 성공! (curl로도 똑같이 해보세요)"
        resp = make_response(render_template_string(LOGIN_HTML, message=message, success=success))
        resp.set_cookie("session_user", "chulsu", httponly=True)
        return resp
    elif username == "admin" and password == "test123":
        success = True
        message = "관리자 로그인 성공!"
        resp = make_response(render_template_string(LOGIN_HTML, message=message, success=success))
        resp.set_cookie("session_user", "admin", httponly=True)
        return resp
    else:
        return render_template_string(LOGIN_HTML, message="아이디 또는 비밀번호가 틀렸습니다.", success=False)

@app.route("/myinfo")
def myinfo():
    session_user = request.cookies.get("session_user")
    if not session_user:
        return render_template_string(MYINFO_HTML, user=None)
    
    c = DB.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (session_user,))
    row = c.fetchone()
    user = dict(row) if row else None
    return render_template_string(MYINFO_HTML, user=user)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """
    로그아웃: session_user 쿠키를 삭제 (만료 처리).
    GET으로도 동작하게 해서 <a href="/logout"> 링크로 쉽게 테스트 가능.
    실제로는 POST가 더 안전하지만, 학습용으로는 둘 다 지원.
    curl / fetch 콘솔 연습에도 좋음:
      fetch('/logout', {method:'POST', credentials:'include'})
      curl.exe "http://127.0.0.1:5003/logout" -b cookies.txt -c cookies.txt
    """
    resp = make_response(redirect(url_for("index")))
    # 쿠키 즉시 만료 (HttpOnly 유지)
    resp.set_cookie("session_user", "", expires=0, httponly=True)
    # 더 확실하게 하려면 아래처럼도 가능:
    # resp.delete_cookie("session_user")
    return resp

@app.route("/debug/echo")
def debug_echo():
    """curl 연습 최고의 친구. 받은 요청을 최대한 자세히 돌려줌."""
    info = {
        "method": request.method,
        "url": request.url,
        "path": request.path,
        "query_string": request.query_string.decode("utf-8", errors="replace"),
        "args": dict(request.args),
        "form": dict(request.form),
        "data": request.get_data(as_text=True)[:500] if request.get_data() else None,
        "headers": dict(request.headers),
        "cookies": dict(request.cookies),
        "remote_addr": request.remote_addr,
        "content_type": request.content_type,
        "content_length": request.content_length,
    }
    # Console(fetch), curl, 또는 ?format=json 요청이면 깔끔한 JSON 반환 (Console 실습에 최적화)
    wants_json = (
        request.args.get("format") == "json" or
        request.headers.get("Accept", "").startswith("application/json") or
        "curl" in request.headers.get("User-Agent", "").lower() or
        "fetch" in request.headers.get("User-Agent", "").lower() or
        bool(request.headers.get("Sec-Fetch-Mode"))
    )
    if wants_json:
        return jsonify(info)
    return f"<pre>{json.dumps(info, indent=2, ensure_ascii=False)}</pre>"

@app.route("/debug/headers")
def debug_headers():
    return "<pre>" + json.dumps(dict(request.headers), indent=2, ensure_ascii=False) + "</pre>"

if __name__ == "__main__":
    print("=" * 65)
    print("02-http-curl-devtools 시작")
    print("접속: http://127.0.0.1:5003")
    print("이 실습은 Burp 없이 DevTools + curl.exe 로 진행합니다.")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5003, debug=True)
