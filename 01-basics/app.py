"""
01-basics: 웹 해킹이란 무엇인가? (책 Chapter 01 매핑)

이 앱의 목적:
- "왜 웹이 해커들의 공격 맛집인가?" 를 코드와 함께 체감
- 사용자 입력값 검증 미흡이 모든 취약점의 시작점임을 보여줌
- 책 Ch01에서 나온 "철수 → 수미 정보 탈취" 예시를 최소 코드로 재현

이론은 책을 읽되, 여기서는 "직접 만져보는 것"에 집중.
"""

from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

def get_db():
    # check_same_thread=False is needed because Flask dev server (debug=True)
    # handles requests in different threads, but this is a simple in-memory demo DB.
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        CREATE TABLE memos (
            id INTEGER PRIMARY KEY,
            owner TEXT,
            content TEXT,
            is_secret INTEGER DEFAULT 0
        )
    """)
    c.executemany("INSERT INTO memos (owner, content, is_secret) VALUES (?, ?, ?)", [
        ("chulsu", "오늘 점심은 김치찌개", 0),
        ("sumi", "철수한테 고백할까 말까 고민중...", 1),   # 비밀 메모
        ("admin", "플래그{webhacking_is_fun_with_input_validation}", 1),
    ])
    return conn

DB = get_db()

INDEX = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>01-basics | 크리핵티브 웹 해킹 바이블 Ch01 실습</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-5">
  <div class="text-center mb-4">
    <h1 class="display-6 fw-bold">01-basics: 왜 웹이 공격 맛집인가?</h1>
    <p class="lead text-muted">크리핵티브의 한 권으로 끝내는 웹 해킹 바이블 — Chapter 01 실습</p>
  </div>

  <div class="row">
    <div class="col-lg-7">
      <div class="card mb-4">
        <div class="card-header bg-primary text-white">
          <strong>📖 책 Ch01에서 배우는 핵심</strong>
        </div>
        <div class="card-body small">
          <ul class="mb-0">
            <li>웹 서비스가 해커들의 공격 1순위인 진짜 이유 (80/443 포트 항상 열림, 사용자 입력 필수)</li>
            <li>대부분의 취약점은 <strong>"사용자 입력값에 대한 검증 미흡"</strong>에서 시작</li>
            <li>공격 기법만 외우지 말고, <strong>프로그램이 어떻게 동작하는지</strong> 이해해야 구조적 취약점을 찾을 수 있음</li>
            <li>책에 나오는 "철수 → 수미 정보 탈취" 예시를 가장 단순하게 재현</li>
          </ul>
        </div>
      </div>

      <div class="card mb-4 border-danger">
        <div class="card-header bg-danger text-white">
          <strong>🎯 실습 목표 (5분 컷)</strong>
        </div>
        <div class="card-body">
          <h6>1. 정상 동작 관찰</h6>
          <p class="small">아래 폼으로 <code>chulsu</code>의 메모를 먼저 확인해보세요.</p>

          <form action="/memo" method="GET" class="row g-2 mb-3">
            <div class="col-auto">
              <input type="text" name="owner" class="form-control" value="chulsu" style="width:200px">
            </div>
            <div class="col-auto">
              <button class="btn btn-primary">메모 보기</button>
            </div>
          </form>

          <h6>2. 공격 실습 (파라미터 조작)</h6>
          <p class="small mb-1">아래 링크를 클릭하거나, owner 값을 직접 바꿔서 요청을 보내세요:</p>
          <div class="d-flex gap-2 flex-wrap">
            <a href="/memo?owner=sumi" class="btn btn-outline-danger btn-sm">?owner=sumi (수미의 비밀 메모)</a>
            <a href="/memo?owner=admin" class="btn btn-outline-danger btn-sm">?owner=admin (관리자 플래그)</a>
            <a href="/memo?owner=chulsu" class="btn btn-outline-secondary btn-sm">원래대로</a>
          </div>

          <div class="alert alert-warning mt-3 small mb-0">
            <strong>성공 기준:</strong> 수미의 비밀 고민이나 <code>플래그{webhacking_is_fun_with_input_validation}</code> 가 화면에 보이면 1단계 정복!
          </div>
        </div>
      </div>
    </div>

    <div class="col-lg-5">
      <div class="card mb-3">
        <div class="card-header">💡 왜 이게 취약할까? (책의 핵심 메시지)</div>
        <div class="card-body small">
          서버 코드는 대략 이렇게 되어 있습니다:<br>
          <code class="d-block mt-1">owner = request.args.get("owner")</code>
          <code class="d-block">SELECT * FROM memos WHERE owner = owner</code><br>
          <strong>문제:</strong> "지금 이 요청을 보낸 사람이, 이 owner의 메모를 볼 <u>권한이 있는가?</u>" 에 대한 검사가 전혀 없습니다.<br><br>
          이것이 "입력값 검증 미흡"의 가장 단순하고 강력한 예시입니다.
        </div>
      </div>

      <div class="card border-success">
        <div class="card-header bg-success text-white">자가 점검 (Ch01 끝낸 후)</div>
        <div class="card-body small">
          □ "입력값 검증 미흡"을 한 문장으로 설명할 수 있는가?<br>
          □ 왜 웹은 사용자 입력을 반드시 받을 수밖에 없는가?<br>
          □ 이 예제에서 owner 대신 숫자 id를 썼다면 어떤 차이가 있을까? (Ch10 IDOR 예고)
        </div>
      </div>
    </div>
  </div>

  <div class="text-center mt-4">
    <p class="text-muted small">이 실습이 끝나면 → <strong>02-http-curl-devtools</strong> 로 넘어가서 DevTools + curl로 HTTP 직접 주고받는 연습을 하세요.</p>
    <a href="http://127.0.0.1:5003" class="btn btn-outline-primary btn-sm" target="_blank">02-http-curl-devtools 열기 (별도 실행 필요)</a>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

MEMO = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>메모 조회 결과 | 01-basics</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-5" style="max-width: 720px;">
  <h2 class="mb-4">메모 조회 결과</h2>

  {% if memo %}
  <div class="card mb-3">
    <div class="card-body">
      <p><strong>작성자:</strong> {{ memo.owner }}</p>
      <p><strong>내용:</strong><br> {{ memo.content }}</p>
      {% if memo.is_secret %}
        <div class="alert alert-danger py-1 px-2 small mb-0">⚠️ 비밀 메모 — 원래는 볼 수 없어야 하는 정보입니다.</div>
      {% endif %}
    </div>
  </div>
  {% else %}
  <div class="alert alert-secondary">메모가 없습니다.</div>
  {% endif %}

  <a href="/" class="btn btn-secondary">← 다시 시도 (다른 owner로)</a>

  <div class="mt-4 small text-muted">
    이 결과가 나왔다면 이미 "파라미터 변조"에 성공한 것입니다.<br>
    책 Ch01의 "철수 → 수미 탈취" 예시를 직접 재현한 상태입니다.
  </div>
</div>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(INDEX)


@app.route("/memo")
def view_memo():
    """
    [의도적 취약점]
    owner 파라미터를 받아서 아무런 권한 검사 없이 그대로 조회.
    이것이 "입력값 검증 미흡"의 가장 단순한 형태.
    """
    owner = request.args.get("owner", "chulsu")
    
    # ★ 취약한 코드의 핵심
    c = DB.cursor()
    c.execute("SELECT * FROM memos WHERE owner = ?", (owner,))
    row = c.fetchone()
    
    if row:
        return render_template_string(MEMO, memo=dict(row))
    return render_template_string(MEMO, memo=None)


if __name__ == "__main__":
    print("01-basics 앱 시작: http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
