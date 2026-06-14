#!/usr/bin/env python3
"""
VulnBoard - 크리핵티브 웹 해킹 바이블 실습용 취약 웹사이트
주요 초점: SQL Injection (Ch04) + 책의 후반 공격 기법들

이 앱은 의도적으로 여러 취약점을 포함하고 있습니다.
실제 서비스에 절대 사용하지 마세요. 학습 전용입니다.

실행:
    python app.py

접속: http://127.0.0.1:5002

특징:
- Flask + SQLite (가벼움, Windows 바로 실행)
- 여러 SQLi 진입점 (error, union, boolean blind, time-based, login, search, IDOR-style)
- Stored XSS (댓글)
- Broken Access Control / IDOR
- 간단한 파일 업로드 (나중에 확장)
- 관리자 페이지 (취약한 권한 체크)
- 모든 주요 요청은 Burp로 관찰/공격할 것!

코드에 # VULNERABLE: 주석으로 취약한 부분 명시.
"""

import os
import sqlite3
import time
import random
from datetime import datetime
from flask import (
    Flask, request, render_template, redirect, url_for,
    session, flash, send_from_directory, make_response, jsonify
)
from lab_problems import PROBLEMS, get_problem, get_all_parts, get_progress_stats
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "vulnboard-insecure-for-study-only-2026"
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DB_PATH = os.path.join(os.path.dirname(__file__), 'vulnboard.db')

# ============================================================
# Database initialization (rich data for SQLi practice)
# ============================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Users table - classic target for SQLi
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            nickname TEXT,
            email TEXT,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')

    # Posts (board)
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            content TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Comments (stored XSS + SQLi practice)
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            user_id INTEGER,
            content TEXT,
            created_at TEXT,
            FOREIGN KEY(post_id) REFERENCES posts(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Secrets table - for UNION / blind dumping practice
    c.execute('''
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY,
            owner TEXT,
            secret TEXT,
            flag TEXT
        )
    ''')

    # Files (for upload vuln later)
    c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            original_name TEXT,
            uploaded_at TEXT
        )
    ''')

    # Seed data (only if empty)
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        now = datetime.now().isoformat()
        users = [
            ("admin", "admin123!@#", "관리자", "admin@vulnboard.local", 1, now),
            ("chulsu", "test123", "철수", "chulsu@example.com", 0, now),
            ("sumi", "sumi2025", "수미", "sumi@secret.local", 0, now),
            ("guest", "guest", "손님", "guest@vulnboard.local", 0, now),
        ]
        c.executemany(
            "INSERT INTO users (username, password, nickname, email, is_admin, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            users
        )

        # Posts
        posts = [
            (1, "공지사항: VulnBoard 오픈", "여러분 환영합니다. 이 사이트는 웹해킹 연습용으로 만들어졌습니다. 여러 취약점이 숨어있어요. 찾아보세요!", now),
            (2, "오늘 점심 뭐 먹지", "김치찌개 먹을까? 아니면 제육볶음? 추천 좀...", now),
            (3, "비밀 프로젝트 진행 중", "다음 주에 중요한 발표가 있습니다. 절대 외부에 유출 금지.", now),
            (1, "SQL Injection 연습용 게시글", "이 게시판의 여러 기능에서 SQL Injection이 가능합니다. 직접 찾아보세요. flag는 secrets 테이블에 있습니다.", now),
        ]
        c.executemany(
            "INSERT INTO posts (user_id, title, content, created_at) VALUES (?, ?, ?, ?)",
            posts
        )

        # Comments (one with XSS payload example)
        comments = [
            (1, 1, "정말 유용한 사이트네요!", now),
            (2, 2, "저는 김치찌개 추천!", now),
            (3, 1, "<script>alert('XSS 테스트')</script> 댓글에 스크립트 넣으면 어떻게 될까?", now),
            (1, 4, "이 글의 content를 잘 보면 힌트가 있을지도?", now),
        ]
        c.executemany(
            "INSERT INTO comments (post_id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
            comments
        )

        # Secrets - the real treasure for advanced SQLi
        secrets = [
            (1, "admin", "root password hint: p@ssw0rd_is_not_this", "FLAG{SQLi_UNION_is_classic}"),
            (2, "sumi", "내가 좋아하는 사람은 철수야... 절대 들키지마", "FLAG{BLIND_SQLi_IS_POWERFUL}"),
            (3, "admin", "VulnBoard DB backup password: vulnboard2025!backup", "FLAG{TIME_BASED_SQLi_MASTER}"),
            (4, "chulsu", "수미한테 고백할 용기 없어...", "FLAG{SECOND_ORDER_SQLi}"),
        ]
        c.executemany(
            "INSERT INTO secrets (id, owner, secret, flag) VALUES (?, ?, ?, ?)",
            secrets
        )

        # Sample file record
        c.execute(
            "INSERT INTO files (user_id, filename, original_name, uploaded_at) VALUES (?, ?, ?, ?)",
            (1, "notice.txt", "공지사항.txt", now)
        )

        # Create a real file in uploads
        with open(os.path.join(app.config['UPLOAD_FOLDER'], "notice.txt"), "w", encoding="utf-8") as f:
            f.write("VulnBoard 관리자 공지\n관리자 비밀번호는 절대 바꾸지 마세요: admin123!@#\n")

    conn.commit()
    conn.close()
    print("[+] Database initialized with seed data.")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# Helper: very vulnerable query executor (for teaching)
# ============================================================
def execute_vulnerable_query(query):
    """
    WARNING: This is intentionally vulnerable.
    We use this for demonstrating raw SQL concatenation.
    """
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute(query)
        rows = c.fetchall()
        return rows, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


# ============================================================
# Routes
# ============================================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/guide')
def guide():
    """기존 가이드 (레거시). 새로 만든 문제집 /lab 을 추천."""
    return render_template('guide.html')


# ============================================================
# 새로운 한국식 문제집 (문제 객체화 + 풀이)
# "이 문제집 하나만 끝까지 따라하면 책을 온전히 마스터할 수 있다"
# ============================================================

@app.route('/lab')
def lab():
    """크리핵티브 웹 해킹 바이블 정복 문제집 - 메인 진입점"""
    parts = get_all_parts()
    return render_template('lab.html', problems=PROBLEMS, parts=parts)

@app.route('/problem/<int:pid>')
def problem_detail(pid):
    prob = get_problem(pid)
    if not prob:
        flash("해당 문제가 없습니다.")
        return redirect(url_for('lab'))
    return render_template('problem_detail.html', prob=prob)

@app.route('/lab/progress', methods=['POST'])
def lab_progress():
    """클라이언트(localStorage)에서 보낸 solved_ids를 받아 통계 반환 (선택 사용)"""
    data = request.get_json(silent=True) or {}
    solved = data.get('solved', [])
    stats = get_progress_stats(solved)
    return jsonify(stats)


@app.route('/board')
def board():
    """게시판 목록 - 검색 기능 포함 (강력한 SQLi 포인트)"""
    keyword = request.args.get('q', '')
    conn = get_db()
    c = conn.cursor()

    if keyword:
        # VULNERABLE: Classic search SQLi (LIKE with concatenation)
        # Try: ' OR '1'='1' --
        # Try: ' UNION SELECT 1,username,password,4 FROM users --
        query = f"SELECT p.id, p.title, p.content, u.nickname, p.created_at FROM posts p JOIN users u ON p.user_id = u.id WHERE p.title LIKE '%{keyword}%' OR p.content LIKE '%{keyword}%' ORDER BY p.id DESC"
        rows, error = execute_vulnerable_query(query)
        posts = rows if rows else []
    else:
        c.execute("""
            SELECT p.id, p.title, p.content, u.nickname, p.created_at 
            FROM posts p 
            JOIN users u ON p.user_id = u.id 
            ORDER BY p.id DESC
        """)
        posts = c.fetchall()
        error = None

    conn.close()
    return render_template('board.html', posts=posts, keyword=keyword, error=error)


@app.route('/post/<int:post_id>')
def view_post(post_id):
    """개별 글 보기 - ID 기반 SQLi (가장 흔한 패턴)"""
    conn = get_db()
    c = conn.cursor()

    # VULNERABLE: Direct ID injection point
    # Normal: /post/1
    # Attack: /post/1' OR '1'='1   or   /post/99999 UNION ...
    # Also good for error-based and union-based
    query = f"SELECT p.id, p.title, p.content, u.nickname, u.id as author_id, p.created_at FROM posts p JOIN users u ON p.user_id = u.id WHERE p.id = {post_id}"
    rows, error = execute_vulnerable_query(query)

    post = rows[0] if rows else None
    comments = []

    if post:
        # VULNERABLE comment loading (also injectable via other means)
        c.execute("SELECT c.id, c.content, u.nickname, c.created_at FROM comments c JOIN users u ON c.user_id = u.id WHERE c.post_id = ?", (post['id'],))
        comments = c.fetchall()

    conn.close()
    return render_template('post.html', post=post, comments=comments, error=error, post_id=post_id)


@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    """댓글 작성 - Stored XSS + SQLi 가능"""
    if 'user_id' not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for('login'))

    content = request.form.get('content', '')

    conn = get_db()
    c = conn.cursor()
    now = datetime.now().isoformat()

    # VULNERABLE: content is stored as-is (no escaping) → stored XSS
    # Also later can be used in other queries for second-order SQLi
    c.execute(
        "INSERT INTO comments (post_id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
        (post_id, session['user_id'], content, now)
    )
    conn.commit()
    conn.close()

    flash("댓글이 등록되었습니다. (Stored XSS 테스트 가능)")
    return redirect(url_for('view_post', post_id=post_id))


@app.route('/write', methods=['GET', 'POST'])
def write_post():
    if 'user_id' not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content', '')

        conn = get_db()
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute(
            "INSERT INTO posts (user_id, title, content, created_at) VALUES (?, ?, ?, ?)",
            (session['user_id'], title, content, now)
        )
        conn.commit()
        new_id = c.lastrowid
        conn.close()

        flash("게시글이 등록되었습니다.")
        return redirect(url_for('view_post', post_id=new_id))

    return render_template('write.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 - 가장 고전적이고 강력한 SQLi 진입점"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        conn = get_db()
        c = conn.cursor()

        # VULNERABLE: Classic authentication bypass
        # Payload: admin' -- 
        # Payload: ' OR '1'='1' --
        # Payload: admin' OR '1'='1' LIMIT 1 --
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        rows, err = execute_vulnerable_query(query)

        if rows and len(rows) > 0:
            user = rows[0]
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])
            flash(f"환영합니다, {user['nickname']}님!")
            conn.close()
            return redirect(url_for('board'))
        else:
            error = "로그인 실패. SQLi로 우회해보세요!"
            conn.close()

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    flash("로그아웃 되었습니다.")
    return redirect(url_for('index'))


@app.route('/profile')
@app.route('/profile/<username>')
def profile(username=None):
    """프로필 조회 - IDOR / Parameter Tampering 연습"""
    if username is None:
        if 'username' not in session:
            return redirect(url_for('login'))
        username = session['username']

    conn = get_db()
    c = conn.cursor()

    # VULNERABLE: 직접 username으로 조회 (아무런 권한 체크 없음)
    # /profile/admin 또는 /profile/sumi 로 바로 이동 가능
    # 나중에 /profile?user= 로 바꿔서 param tamper 연습도 가능하게 확장
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()

    # 사용자의 posts
    if user:
        c.execute("SELECT id, title, created_at FROM posts WHERE user_id = ? ORDER BY id DESC", (user['id'],))
        user_posts = c.fetchall()
    else:
        user_posts = []

    conn.close()
    return render_template('profile.html', user=user, user_posts=user_posts, viewed_username=username)


@app.route('/search')
def search():
    """별도 검색 페이지 (book의 다양한 기법 연습용)"""
    q = request.args.get('q', '')
    results = []
    error = None

    if q:
        # VULNERABLE: Another search point, different from board
        query = f"SELECT id, title, content FROM posts WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'"
        rows, err = execute_vulnerable_query(query)
        if err:
            error = f"에러 발생 (이걸로 에러 기반 SQLi 연습하세요): {err}"
        else:
            results = rows or []

    return render_template('search.html', results=results, q=q, error=error)


@app.route('/admin')
def admin_panel():
    """관리자 페이지 - Broken Access Control 연습의 정석"""
    # VULNERABLE: 세션의 is_admin만 체크. URL로 직접 접근 가능.
    # Bypass 방법:
    # 1. SQLi로 로그인하면서 is_admin=1 세션 강제
    # 2. Burp로 쿠키/세션 변조
    # 3. /admin?admin=1 같은 param 추가 (의도적으로 체크 안 함)
    if not session.get('is_admin'):
        # Weak check - easy to bypass with SQLi or direct access after tampering
        flash("관리자만 접근 가능합니다. (힌트: SQLi나 세션 변조로 우회하세요)")
        return redirect(url_for('board'))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    all_users = c.fetchall()
    c.execute("SELECT * FROM secrets")
    all_secrets = c.fetchall()
    conn.close()

    return render_template('admin.html', users=all_users, secrets=all_secrets)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
def admin_delete_user(user_id):
    """관리자 기능 - 추가 broken access + IDOR"""
    if not session.get('is_admin'):
        return "권한 없음", 403

    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash(f"사용자 {user_id} 삭제 시도됨 (실제로는 cascade 안 되어있음)")
    return redirect(url_for('admin_panel'))


# ============================================================
# File upload (basic, for Ch09 file upload chapter)
# ============================================================
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        flash("로그인 후 이용하세요.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash("파일이 없습니다.")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("선택된 파일이 없습니다.")
            return redirect(request.url)

        if file:
            # VULNERABLE: filename sanitization weak (for later path traversal / upload bypass)
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            conn = get_db()
            c = conn.cursor()
            c.execute(
                "INSERT INTO files (user_id, filename, original_name, uploaded_at) VALUES (?, ?, ?, ?)",
                (session['user_id'], filename, file.filename, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()

            flash(f"파일 업로드 성공: {filename} (웹쉘 업로드 연습 가능 지점)")
            return redirect(url_for('upload_file'))

    # List uploaded files (also vulnerable listing)
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT f.*, u.username FROM files f JOIN users u ON f.user_id = u.id ORDER BY f.id DESC")
    files = c.fetchall()
    conn.close()

    return render_template('upload.html', files=files)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # VULNERABLE: Direct file serving without proper access control or type check
    # Later chapters: path traversal like /uploads/../../app.py or webshell
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ============================================================
# Command injection simulation point (Ch05)
# ============================================================
@app.route('/tools/ping', methods=['GET', 'POST'])
def ping_tool():
    """의도적으로 취약한 ping 도구 (OS Command Injection 연습)"""
    result = None
    cmd = None
    if request.method == 'POST':
        host = request.form.get('host', '127.0.0.1')
        # VULNERABLE: 직접 셸 명령어에 삽입
        # Windows: 127.0.0.1 & whoami
        # 또는 127.0.0.1 | dir
        cmd = f"ping -n 1 {host}"   # Windows ping
        # 실제 실행 (위험하지만 학습용)
        try:
            import subprocess
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
            result = output.decode('utf-8', errors='ignore')
        except Exception as e:
            result = f"실행 결과 (에러 포함): {str(e)}"

    return render_template('ping.html', result=result, cmd=cmd)


# ============================================================
# Additional vulnerable endpoints for book chapter coverage
# ============================================================

@app.route('/download')
def download_file():
    """Ch08 파일 다운로드 취약점 연습용 (Path Traversal 가능)"""
    filename = request.args.get('file', 'notice.txt')
    # VULNERABLE: 사용자 입력을 그대로 파일 경로로 사용 (../ 트래버설 가능)
    # 예: ?file=../../../app.py 또는 ?file=../../vulnboard.db
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        return f"파일 다운로드 실패 (에러 기반 정보 수집 가능): {str(e)}", 400


@app.route('/settings', methods=['GET', 'POST'])
def user_settings():
    """Ch07 CSRF 취약점 데모 (토큰 없음 + 중요한 액션)"""
    if 'user_id' not in session:
        flash("로그인 후 이용하세요.")
        return redirect(url_for('login'))

    message = None
    if request.method == 'POST':
        # VULNERABLE: CSRF 토큰 전혀 없음. 다른 사이트의 폼으로 이 요청을 보낼 수 있음.
        new_email = request.form.get('email', '')
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, session['user_id']))
        conn.commit()
        conn.close()
        message = f"이메일이 '{new_email}'(으)로 변경되었습니다. (CSRF 공격 가능 상태)"

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT email FROM users WHERE id = ?", (session['user_id'],))
    current = c.fetchone()
    conn.close()

    return render_template('settings.html', current_email=current['email'] if current else '', message=message)


# ============================================================
# Debug / Utility for learning
# ============================================================
@app.route('/debug/db')
def debug_db():
    """학습용: 현재 DB 상태를 볼 수 있게 (실제로는 숨겨야 함)"""
    conn = get_db()
    c = conn.cursor()
    tables = {}
    for table in ['users', 'posts', 'comments', 'secrets', 'files']:
        c.execute(f"SELECT * FROM {table}")
        tables[table] = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template('debug_db.html', tables=tables)


@app.route('/reset')
def reset_db():
    """편의 기능: DB 초기화 (연습 중 망가뜨렸을 때)"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    session.clear()
    flash("데이터베이스가 초기화되었습니다. 다시 로그인하세요. (admin / admin123!@#)")
    return redirect(url_for('index'))


# ============================================================
# Templates are in templates/ folder (we will create them)
# ============================================================

if __name__ == '__main__':
    init_db()
    print("=" * 60)
    print("VulnBoard (취약 게시판) 시작")
    print("접속 주소: http://127.0.0.1:5002")
    print("Burp Suite를 켜고 모든 공격을 연습하세요!")
    print("DB 초기화: /reset")
    print("힌트/챌린지: vulnboard/HACKING_CHALLENGES.md 참고")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5002, debug=True)
