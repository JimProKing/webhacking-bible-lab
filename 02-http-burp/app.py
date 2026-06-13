"""
02-http-burp: HTTP와 Burp Suite 마스터하기
크리핵티브의 한 권으로 끝내는 웹 해킹 바이블 - Ch02 매핑

이 앱의 목적:
- HTTP 요청/응답의 모든 요소(메서드, 헤더, 파라미터, 쿠키, 바디)를 직접 눈으로 확인
- Burp Suite로 "모든 트래픽을 가로채서 보는" 경험을 처음부터 하기
- 책에서 강조하는 "사용자 입력값이 어떻게 서버로 전달되는지"를 체감

실행:
    python app.py
    브라우저: http://127.0.0.1:5001
"""

from flask import Flask, request, render_template_string, make_response, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "for-study-only-not-real-secret"

# 간단한 인메모리 DB (실습용)
def get_db():
    # check_same_thread=False is needed because Flask dev server (debug=True)
    # handles requests in different threads, but this is a simple in-memory demo DB.
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
    # 책 초반에 나오는 "철수/수미" 예시를 위한 데이터
    c.executemany("""
        INSERT INTO users (username, name, phone, email, is_admin) VALUES (?, ?, ?, ?, ?)
    """, [
        ("chulsu", "철수", "010-1234-5678", "chulsu@example.com", 0),
        ("sumi", "수미", "010-9876-5432", "sumi@example.com", 0),
        ("admin", "관리자", "010-0000-0000", "admin@secret.local", 1),
    ])
    return conn

DB = get_db()

# HTML 템플릿 (간단하게 인라인)
INDEX_HTML = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>02-http-burp | 크리핵티브 웹 해킹 바이블 Ch02 실습</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-4" style="max-width: 860px;">
  <div class="text-center mb-3">
    <h1 class="fw-bold">02-http-burp: HTTP + Burp Suite 완전 정복</h1>
    <p class="text-muted">크리핵티브의 한 권으로 끝내는 웹 해킹 바이블 — Chapter 02 매핑</p>
  </div>

  <div class="alert alert-primary">
    <strong>이 앱의 목표:</strong> Burp로 모든 트래픽을 가로채고 조작하는 경험.<br>
    <strong>추천</strong>: 먼저 <code>02-http-curl-devtools</code> 에서 curl + DevTools로 직접 HTTP를 주고받는 연습을 끝낸 후 오는 걸 강력 추천합니다.
  </div>

  <div class="row g-3">
    <!-- GET -->
    <div class="col-md-6">
      <div class="card h-100">
        <div class="card-header">1. GET 요청 + 파라미터 변조 (Ch01~Ch02 연결)</div>
        <div class="card-body">
          <p class="small">책 초반 "철수 → 수미" 예시를 그대로 재현.</p>
          <form action="/profile" method="GET" class="mb-2">
            <div class="input-group">
              <span class="input-group-text">user</span>
              <input type="text" name="user" class="form-control" value="chulsu">
              <button class="btn btn-primary">회원 정보 보기</button>
            </div>
          </form>
          <div class="small text-muted">Burp에서 요청을 가로채서 <code>user=sumi</code> 또는 <code>user=admin</code>으로 바꿔보세요.</div>
        </div>
      </div>
    </div>

    <!-- POST -->
    <div class="col-md-6">
      <div class="card h-100">
        <div class="card-header">2. POST 요청 + 바디 확인</div>
        <div class="card-body">
          <form action="/login" method="POST">
            <div class="mb-2">
              <input type="text" name="username" class="form-control" value="chulsu" placeholder="아이디">
            </div>
            <div class="mb-2">
              <input type="password" name="password" class="form-control" value="test123" placeholder="비밀번호">
            </div>
            <button class="btn btn-success w-100">로그인</button>
          </form>
          <div class="small text-muted mt-1">Burp에서 요청 바디(username=...&password=...)를 반드시 확인하세요.</div>
        </div>
      </div>
    </div>
  </div>

  <div class="card mt-3">
    <div class="card-header">3. 쿠키 / 세션 실습 (나중에 세션 하이재킹으로 발전)</div>
    <div class="card-body">
      <a href="/myinfo" class="btn btn-outline-dark">내 정보 보기 (쿠키 필요)</a>
      <div class="small mt-2 text-muted">로그인 성공 후 발급되는 <code>session_user</code> 쿠키를 Burp로 확인 → 값을 admin으로 바꿔서 Repeater 전송 연습.</div>
    </div>
  </div>

  <div class="card mt-3 border-warning">
    <div class="card-header bg-warning">Burp Suite 실습 체크리스트 (curl 기초를 먼저 추천)</div>
    <div class="card-body small">
      <p class="mb-1 small text-muted">이전 단계(02-http-curl-devtools)에서 직접 curl로 연습했다면, Burp가 얼마나 편한 도구인지 실감할 수 있습니다.</p>
      <ol class="mb-1">
        <li>Burp 실행 → Proxy → Intercept is on</li>
        <li>브라우저 프록시 127.0.0.1:8080 (FoxyProxy 강력 추천)</li>
        <li>위 모든 폼을 전송하면서 Burp에서 요청을 가로채서 Headers / Params / Body 관찰</li>
        <li>Repeater로 보내서 파라미터/쿠키를 마음대로 바꿔가며 Forward</li>
        <li>HTTP History에서 과거 요청을 다시 열어 분석하는 습관 들이기</li>
      </ol>
      <strong>지금 당장:</strong> /profile?user=chulsu 를 Repeater로 보내서 user 값을 sumi로 바꿔보세요.
    </div>
  </div>

  <div class="mt-3 text-center">
    <a href="/debug/request" class="btn btn-sm btn-info">디버그 페이지 (Burp 없이 대략 구조 보기)</a>
    <span class="text-muted small ms-2">curl + DevTools로 먼저 연습하면 Burp의 가치가 더 잘 보입니다.</span>
  </div>
</div>
</body>
</html>
"""

PROFILE_HTML = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <title>회원 정보 | 02-http-burp</title>
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
    ⚠️ 여기서는 <code>?user</code> 파라미터를 아무런 권한 검증 없이 그대로 사용하고 있습니다.<br>
    이것이 파라미터 변조(IDOR)의 가장 기본 형태입니다. Burp Repeater로 user 값을 자유롭게 바꿔보세요.
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
  <title>로그인 결과 | 02-http-burp</title>
</head>
<body class="bg-light">
<div class="container py-4" style="max-width: 520px;">
  <h2>로그인 결과</h2>
  <div class="alert {% if success %}alert-success{% else %}alert-danger{% endif %}">
    {{ message }}
  </div>
  {% if success %}
    <a href="/myinfo" class="btn btn-primary">내 정보 페이지로 이동 (쿠키 확인 필수!)</a>
  {% endif %}
  <a href="/" class="btn btn-secondary btn-sm mt-2 d-block w-fit">← 메인으로</a>
  <div class="small text-muted mt-3">Burp History에서 방금 보낸 POST 요청의 바디를 꼭 열어보세요.</div>
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
  <title>내 정보 | 02-http-burp</title>
</head>
<body class="bg-light">
<div class="container py-4" style="max-width: 620px;">
  <h2>내 정보 (세션/쿠키 기반)</h2>
  {% if user %}
  <div class="card">
    <div class="card-body">
      <p>안녕하세요, <strong>{{ user.name }}</strong>님!</p>
      <p>전화번호: {{ user.phone }}</p>
      <p>이메일: {{ user.email }}</p>
      {% if user.is_admin %}
        <div class="alert alert-danger py-1 small">🎉 관리자 권한 확인됨 (나중에 세션 변조 / SQLi로 admin 권한 얻는 실습에 사용)</div>
      {% endif %}
    </div>
  </div>
  {% else %}
  <div class="alert alert-danger">로그인이 필요합니다. 메인에서 로그인하세요.</div>
  {% endif %}
  <a href="/" class="btn btn-secondary btn-sm mt-2">← 메인으로</a>

  <div class="mt-3 p-3 bg-white border rounded small">
    <strong>Burp 실습 포인트:</strong><br>
    로그인 후 발급된 <code>Cookie: session_user=xxx</code> 를 Burp Repeater에서 직접 수정해서 다른 사용자로 위장해보세요.
  </div>
</div>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(INDEX_HTML)


@app.route("/profile")
def profile():
    """
    [취약점 포인트 - 책 Ch01 예시와 동일]
    ?user= 값을 받아서 아무런 검증/권한 체크 없이 바로 DB 조회.
    이것이 파라미터 변조 + 나중에 IDOR로 발전하는 기초.
    """
    username = request.args.get("user", "chulsu")
    
    # ★★★ 여기서 취약! (의도적으로)
    # 실제로는 현재 로그인한 사용자가 이 user를 볼 권한이 있는지 확인해야 함.
    c = DB.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))  # ← 그래도 ? placeholder는 썼지만, 로직 자체가 문제
    row = c.fetchone()
    
    if row:
        user = dict(row)
    else:
        user = None
    
    return render_template_string(PROFILE_HTML, user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect(url_for("index"))
    
    # POST 데이터 받기 (Burp에서 body를 꼭 확인할 것)
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    
    # 실습용: 비밀번호는 거의 무시 (chulsu / test123 만 통과시킴)
    # 나중에 SQLi 챕터에서 진짜 취약한 로그인으로 업그레이드 예정
    success = False
    message = "로그인 실패"
    
    if username == "chulsu" and password == "test123":
        success = True
        message = "철수 로그인 성공! 세션이 발급되었습니다."
        resp = make_response(render_template_string(LOGIN_HTML, message=message, success=success))
        resp.set_cookie("session_user", "chulsu", httponly=True)  # httponly지만 아직 secure하지 않음
        return resp
    elif username == "admin" and password == "test123":  # admin도 동일 pw로 편의
        success = True
        message = "관리자 로그인 성공!"
        resp = make_response(render_template_string(LOGIN_HTML, message=message, success=success))
        resp.set_cookie("session_user", "admin", httponly=True)
        return resp
    else:
        return render_template_string(LOGIN_HTML, message="아이디 또는 비밀번호가 틀렸습니다.", success=False)


@app.route("/myinfo")
def myinfo():
    """
    쿠키(세션) 기반 인증 예시.
    Burp로 쿠키를 가로채서 다른 사용자로 위장하는 연습을 하게 될 것.
    """
    session_user = request.cookies.get("session_user")
    if not session_user:
        return render_template_string(MYINFO_HTML, user=None)
    
    c = DB.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (session_user,))
    row = c.fetchone()
    user = dict(row) if row else None
    return render_template_string(MYINFO_HTML, user=user)


@app.route("/debug/request")
def debug_request():
    """
    Burp 없이도 현재 요청의 모든 정보를 볼 수 있게 만든 디버그 페이지.
    (학습용) 실제 공격할 때는 Burp History + Repeater를 쓰는 게 정석.
    """
    info = {
        "method": request.method,
        "path": request.path,
        "args": dict(request.args),
        "form": dict(request.form),
        "headers": dict(request.headers),
        "cookies": dict(request.cookies),
        "remote_addr": request.remote_addr,
    }
    return f"<pre>{info}</pre>"


if __name__ == "__main__":
    print("=" * 60)
    print("02-http-burp 실습 앱 시작")
    print("접속: http://127.0.0.1:5001")
    print("Burp Proxy를 127.0.0.1:8080 으로 설정하고 사용하세요!")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5001, debug=True)
