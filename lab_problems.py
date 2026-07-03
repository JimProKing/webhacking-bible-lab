"""
크리핵티브의 한 권으로 끝내는 웹 해킹 바이블
정복용 한국식 문제집 (문제 객체화)

이 파일 하나가 "이 문제집을 전부 풀면 책을 마스터한다"의 진원지입니다.
모든 문제는 순서대로 설계되어 있으며, VulnBoard + 보조 랩을 통해 실습합니다.

사용법:
- from lab_problems import PROBLEMS, get_problem
- /lab 라우트에서 이 데이터를 렌더링
"""

PROBLEMS = [
    # ==================== PART 01 ====================
    {
        "id": 1,
        "num": "01",
        "part": "PART 01",
        "chapter": "Ch01",
        "title": "파라미터 변조로 다른 사람 비밀 메모 탈취",
        "difficulty": "★☆☆☆☆",
        "category": "기초 / 입력값 검증 미흡",
        "objective": "문제 01 전용 앱에서 owner 파라미터를 조작해, 로그인 없이 수미와 관리자의 비밀 정보를 확인한다.",
        "entry_points": [
            {"label": "문제 01 앱 실행", "url": "http://127.0.0.1:5000/", "note": "cd problems/01-파라미터-변조-기초 && python app.py"},
            {"label": "수미 메모 공격", "url": "http://127.0.0.1:5000/memo?owner=sumi"},
            {"label": "admin 플래그 공격", "url": "http://127.0.0.1:5000/memo?owner=admin"},
        ],
        "missions": [
            "chulsu의 정상 메모를 먼저 조회한다",
            "?owner=sumi 로 수미의 비밀 고민(고백 관련)을 확인한다",
            "?owner=admin 으로 관리자 플래그{webhacking_is_fun_with_input_validation}를 획득한다"
        ],
        "success_criteria": "admin의 플래그 문자열이 화면에 보인다.",
        "payload_examples": ["?owner=sumi", "?owner=admin"],
        "hints": [
            "브라우저 주소창에서 ?owner= 값을 직접 바꿔보세요.",
            "아무런 로그인/권한 체크가 없다는 점을 주목하세요.",
            "curl이나 DevTools로도 동일하게 시도 가능합니다."
        ],
        "solution": "서버가 owner 파라미터를 받아 'WHERE owner = ?' 쿼리에 그대로 사용하면서, '이 요청을 보낸 사용자가 해당 owner의 데이터를 볼 권한이 있는가?'에 대한 검사를 전혀 하지 않는다. 이것이 책 Ch01이 강조하는 '사용자 입력값 검증 미흡'의 가장 단순하고 강력한 예시다.",
        "secure_snippet": "# 취약: owner = request.args.get('owner')\n# c.execute(\"SELECT * FROM memos WHERE owner = ?\", (owner,))\n\n# 방어: 현재 사용자 권한 + 소유자 검증 추가\nif current_user.username != owner and not current_user.is_admin:\n    abort(403)",
        "book_refs": "Ch01. 웹 해킹에 대한 이해 - 1.2 해커들의 공격 맛집, 웹",
        "lab_target": "problems/01-파라미터-변조-기초",
        "flags": []
    },
    {
        "id": 2,
        "num": "02",
        "part": "PART 01",
        "chapter": "Ch02",
        "title": "HTTP 요청을 손으로 직접 만들고 조작하기 (curl + DevTools)",
        "difficulty": "★☆☆☆☆",
        "category": "HTTP 기초 / Burp 이전 근력",
        "objective": "문제 02 전용 앱에서 curl.exe와 브라우저 Console fetch로 GET/POST/쿠키를 직접 작성·조작한다. Burp 없이도 HTTP를 '손으로' 느끼는 것이 목표.",
        "entry_points": [
            {"label": "문제 02 앱 실행", "url": "http://127.0.0.1:5003/", "note": "cd problems/02-HTTP-직접-조작-curl-devtools && python app.py"},
        ],
        "missions": [
            "Network 탭에서 /profile 요청을 'Copy as cURL' 한 후 PowerShell에서 실행",
            "curl로 ?user=sumi, ?user=admin 직접 조작해 다른 사람 정보 확인",
            "로그인 후 session_user 쿠키 값을 admin으로 바꿔 /myinfo 세션 하이재킹",
            "Console에서 fetch()로 로그인 + 쿠키 포함 요청 보내기 (credentials: 'include' 필수)"
        ],
        "success_criteria": "admin으로 쿠키를 위장해 myinfo 페이지에서 관리자 권한 내용을 확인한다.",
        "payload_examples": [
            'curl.exe "http://127.0.0.1:5003/profile?user=admin"',
            'curl.exe ... -b "session_user=admin"',
            'fetch("/login", {method:"POST", body:..., credentials:"include"})'
        ],
        "hints": [
            "curl.exe (아니면 curl 아님!) 사용. PowerShell에서 Invoke-WebRequest 별칭 주의.",
            "로그인 성공 시 Set-Cookie를 관찰하세요.",
            "Console fetch 실습 섹션의 async loginAs 함수를 적극 활용."
        ],
        "solution": "HTTP는 단순한 텍스트 프로토콜이다. 메서드, 헤더, 바디, 쿠키를 직접 쓸 수 있다는 사실을 몸으로 깨닫는 것이 중요. 나중에 Burp가 '이걸 자동으로 편하게 해주는 도구'라는 걸 제대로 이해하게 된다.",
        "secure_snippet": "이 단계는 아직 보안 코드가 아니라 'HTTP를 직접 다루는 근육'을 기르는 단계. 쿠키에 서명 + HttpOnly + Secure + 짧은 만료시간 등을 나중에 적용.",
        "book_refs": "Ch02. 2.2 HTTP 핵심, 2.8~2.10 웹 프록시 & Burp",
        "lab_target": "problems/02-HTTP-직접-조작-curl-devtools",
        "flags": []
    },
    {
        "id": 3,
        "num": "03",
        "part": "PART 01",
        "chapter": "Ch02",
        "title": "Burp Suite로 모든 트래픽을 가로채고 Repeater로 무한 반복 공격하기",
        "difficulty": "★★☆☆☆",
        "category": "도구 마스터 / Burp 근력",
        "objective": "VulnBoard에서 Burp Proxy를 켜고, 모든 요청을 Intercept → Repeater로 보내 파라미터/쿠키/바디를 자유자재로 변조하는 습관을 들인다.",
        "entry_points": [
            {"label": "VulnBoard (메인)", "url": "http://127.0.0.1:5002/", "note": "python app.py"},
            {"label": "문제 03 보조 앱", "url": "http://127.0.0.1:5001/", "note": "cd problems/03-Burp-Repeater-마스터 && python app.py"},
        ],
        "missions": [
            "Burp Intercept ON 상태에서 로그인 폼 전송 → body 확인",
            "Repeater로 /profile?user=chulsu 요청을 여러 번 복제 후 user=sumi, admin으로 변경",
            "로그인 후 발급된 session 쿠키를 Repeater에서 admin으로 변경해서 재전송",
            "History에서 과거 요청을 찾아 다시 Repeater로 불러와 변조"
        ],
        "success_criteria": "Burp Repeater 없이 웹 해킹을 상상할 수 없는 상태가 된다. (자신감 있게 말할 수 있어야 함)",
        "payload_examples": ["Repeater에서 user 파라미터, Cookie 헤더 직접 편집"],
        "hints": [
            "FoxyProxy로 브라우저 트래픽을 127.0.0.1:8080으로 강제하세요.",
            "브라우저 주소창으로 하는 모든 행위는 '진짜 해킹'이 아닙니다. Repeater가 진짜입니다.",
            "성공한 공격은 Repeater 탭 이름을 'admin-login-sqli' 처럼 저장하는 습관."
        ],
        "solution": "Burp는 '중간에서 모든 걸 가로채서 편집하고 반복해서 보내는' 기계를 제공한다. 이 근육이 없으면 이후 SQLi, XSS 등에서 10배 이상 고생한다. 책이 'Burp 없이 웹 해킹은 상상도 할 수 없다'고 한 이유.",
        "secure_snippet": "도구 단계라 별도 secure 코드 없음. 다만 실제 서비스에서는 HSTS, CSP, Secure 쿠키 등을 통해 공격자가 쉽게 가로채기 어렵게 만든다.",
        "book_refs": "Ch02. 2.9 Burp Suite의 주요 기능, 2.10 기본 사용법",
        "lab_target": "VulnBoard",
        "flags": []
    },
    # ==================== PART 02 - SQLi 핵심 ====================
    {
        "id": 4,
        "num": "04",
        "part": "PART 02",
        "chapter": "Ch04",
        "title": "Level 1 - 로그인 SQL Injection (가장 고전적이고 강력한 우회)",
        "difficulty": "★★☆☆☆",
        "category": "SQL Injection / 인증 우회",
        "objective": "VulnBoard /login 에서 admin' --  또는 ' OR '1'='1' -- 로 비밀번호를 모른 채 admin 계정으로 로그인한다.",
        "entry_points": [
            {"label": "로그인 페이지", "url": "http://127.0.0.1:5002/login"},
        ],
        "missions": [
            "chulsu/test123 로 정상 로그인 관찰 (Burp Repeater로 저장)",
            "username=admin' --  + password=아무거나 로 로그인 시도",
            "' OR '1'='1' --  로도 시도",
            "성공 후 /admin 접근 가능한지 확인 (is_admin 세션)"
        ],
        "success_criteria": "admin 계정으로 로그인 성공 + 상단에 관리자 메뉴 또는 /admin 접근 가능",
        "payload_examples": [
            "admin' -- ",
            "admin' OR '1'='1' -- ",
            "' OR '1'='1' LIMIT 1 -- "
        ],
        "hints": [
            "쿼리가 대략 'SELECT * FROM users WHERE username='xxx' AND password='yyy'' 일 것이라고 상상하라.",
            "-- 뒤의 모든 것을 주석 처리하는 게 핵심.",
            "Burp Repeater에서만 20번 이상 반복하세요. 브라우저 폼으로는 절대 익숙해지지 않습니다."
        ],
        "solution": "사용자 입력이 문자열 따옴표로 감싸진 상태로 SQL에 직접 들어가기 때문에, ' 로 쿼리를 닫고 -- 로 나머지를 무효화할 수 있다. 인증 로직 자체가 '입력 = 쿼리 문자열'로 되어 있어서 발생하는 전형적인 1차 SQLi.",
        "secure_snippet": "# 절대 이렇게 하지 마라\nquery = f\"SELECT * FROM users WHERE username='{u}' AND password='{p}'\"\n\n# 올바른 방법\nc.execute(\"SELECT * FROM users WHERE username = ? AND password = ?\", (u, p))",
        "book_refs": "Ch04. 4.1~4.4 SQL Injection의 이해와 공격 방법론 (로그인 우회 파트)",
        "lab_target": "VulnBoard",
        "flags": ["admin 로그인 성공"]
    },
    {
        "id": 5,
        "num": "05",
        "part": "PART 02",
        "chapter": "Ch04",
        "title": "Level 2 - 검색 SQLi + UNION으로 secrets 테이블 전체 덤프",
        "difficulty": "★★★☆☆",
        "category": "SQL Injection / UNION 기반",
        "objective": "/board 또는 /search 에서 에러 기반으로 컬럼 수를 맞춘 후, UNION SELECT로 users와 secrets 테이블의 데이터를 화면에 뽑아낸다. 특히 FLAG들을 모두 획득.",
        "entry_points": [
            {"label": "게시판 검색", "url": "http://127.0.0.1:5002/board"},
            {"label": "고급 검색", "url": "http://127.0.0.1:5002/search"},
        ],
        "missions": [
            "' ORDER BY 1-- 부터 10까지 올려가며 컬럼 수 확인 (에러 나는 직전 숫자)",
            "' UNION SELECT 1,2,3,4,5,6 -- 로 컬럼 타입 맞추기",
            "users 테이블 username, password, is_admin 추출",
            "secrets 테이블 id,owner,secret,flag 모두 추출 (최소 3개 이상 FLAG 확인)"
        ],
        "success_criteria": "화면에 FLAG{SQLi_UNION_is_classic}, FLAG{BLIND_SQLi_IS_POWERFUL} 등 2개 이상 노출",
        "payload_examples": [
            "' ORDER BY 6--",
            "' UNION SELECT 1,username,password,4,5,6 FROM users --",
            "' UNION SELECT id,owner,secret,flag,5,6 FROM secrets --"
        ],
        "hints": [
            "에러 메시지가 컬럼 수를 친절하게 알려줍니다. 무시하지 마세요.",
            "UNION SELECT 뒤의 개수와 타입(문자열/숫자)을 정확히 맞춰야 합니다.",
            "secrets 테이블은 이 앱의 '진짜 보물'입니다. 이걸 못 찾으면 Ch04를 반만 한 겁니다."
        ],
        "solution": "LIKE 검색이 문자열 결합으로 되어 있어 ' 로 쿼리를 깨고 UNION을 주입할 수 있다. 컬럼 수/타입을 맞추는 과정 자체가 SQLi 공격의 핵심 근육이다. secrets 테이블을 만든 이유가 바로 이 실습 때문.",
        "secure_snippet": "f-string이나 % 포매팅으로 쿼리 만들지 말고, 반드시 placeholder + execute(params) 사용. 또는 ORM (SQLAlchemy) 사용.",
        "book_refs": "Ch04. 4.4 SQL 인젝션 공격 종류와 공격 방법론 - UNION 기반",
        "lab_target": "VulnBoard",
        "flags": ["FLAG{SQLi_UNION_is_classic}", "FLAG{BLIND_SQLi_IS_POWERFUL}"]
    },
    {
        "id": 6,
        "num": "06",
        "part": "PART 02",
        "chapter": "Ch04",
        "title": "Level 3 - 게시글 ID 기반 SQLi (현실에서 가장 흔한 패턴)",
        "difficulty": "★★★☆☆",
        "category": "SQL Injection / ID 기반",
        "objective": "/post/1 과 같은 형태의 URL에서 post_id를 조작해 '1' OR '1'='1 또는 UNION을 주입, 다른 게시글/비밀 데이터를 가져온다.",
        "entry_points": [
            {"label": "게시판에서 글 클릭 후 주소 수정", "url": "http://127.0.0.1:5002/post/1"},
            {"label": "직접 공격 예시", "url": "http://127.0.0.1:5002/post/1'"},
        ],
        "missions": [
            "/post/1' 로 에러 유발해서 쿼리 구조 파악",
            "UNION 또는 1 AND 1=2 UNION ... 형태로 secrets flag 추출",
            "여러 post id를 순회하면서 데이터 덤핑 연습"
        ],
        "success_criteria": "post ID를 통해 secrets 테이블의 FLAG 최소 1개 이상 획득",
        "payload_examples": [
            "/post/1'",
            "/post/1 AND 1=2 UNION SELECT 1,owner,secret,flag FROM secrets --"
        ],
        "hints": [
            "URL의 숫자 부분이 바로 취약점 진입점입니다. 숫자 뒤에 ' 를 붙여보세요.",
            "쿼리가 f\"... WHERE p.id = {post_id}\" 형태로 되어 있음.",
            "AND 1=2 를 앞에 붙이면 UNION의 첫 번째 결과셋을 강제로 비울 수 있습니다."
        ],
        "solution": "정수형 ID를 직접 문자열 연결로 쓰는 전형적인 'IDOR + SQLi' 복합 진입점. 실제 웹사이트에서 /view?id=123 같은 패턴이 아직도 매우 많다.",
        "secure_snippet": "post_id = int(post_id) 로 강제 캐스팅 + prepared statement. 또는 UUID 사용.",
        "book_refs": "Ch04. 4.3 취약점 분석 방법, 4.4 공격 종류 (에러/UNION)",
        "lab_target": "VulnBoard",
        "flags": []
    },
    {
        "id": 7,
        "num": "07",
        "part": "PART 02",
        "chapter": "Ch04",
        "title": "Level 4 - Boolean Blind SQLi (한 글자씩 참/거짓으로 추출)",
        "difficulty": "★★★★☆",
        "category": "SQL Injection / Blind",
        "objective": "에러가 안 나는 환경에서 SUBSTR + AND 조건으로 admin 비밀번호나 secrets flag를 한 글자씩 알아낸다. 응답의 '결과 있음/없음' 차이를 이용.",
        "entry_points": [
            {"label": "고급 검색 (추천)", "url": "http://127.0.0.1:5002/search"},
            {"label": "게시판 검색", "url": "http://127.0.0.1:5002/board"},
        ],
        "missions": [
            "1' AND 1=1 --  vs  1' AND 1=2 --  로 응답 차이 관찰",
            "1' AND SUBSTR((SELECT password FROM users WHERE username='admin'),1,1)='a' -- 로 한 글자 테스트",
            "Burp Intruder 또는 간단한 Python 스크립트로 자동화 (선택)",
            "최소 admin 비밀번호 앞 3~4글자 또는 flag 일부 추출 성공"
        ],
        "success_criteria": "Blind 기법으로 'admin' 계정의 password 또는 secrets의 flag 문자열 일부를 성공적으로 유추",
        "payload_examples": [
            "1' AND SUBSTR((SELECT flag FROM secrets LIMIT 1),1,1)='F' --",
            "1' AND LENGTH((SELECT password FROM users WHERE username='admin'))>5 --"
        ],
        "hints": [
            "참이면 결과가 나오고, 거짓이면 결과가 적거나 에러/빈 페이지가 되는 구조를 이용.",
            "SUBSTR(컬럼, 위치, 길이) 또는 SUBSTRING 사용.",
            "한 글자씩 26번(영문) 또는 10번(숫자) 테스트하는 게 지루하지만 이게 Blind의 본질."
        ],
        "solution": "에러가 안 나오는 환경(또는 에러 메시지를 숨긴 환경)에서도 데이터를 추출할 수 있는 강력한 기법. 실제 침투에서 가장 많이 쓰이는 형태 중 하나. '한 글자씩'이라는 개념을 몸으로 이해하는 게 핵심.",
        "secure_snippet": "동일. Prepared statement가 Blind를 막는 게 아니라, '쿼리 구조 자체를 사용자가 제어하지 못하게' 하는 것이다.",
        "book_refs": "Ch04. 4.4 SQL 인젝션 공격 종류 - Boolean Blind, Time-based Blind",
        "lab_target": "VulnBoard",
        "flags": ["FLAG{BLIND_SQLi_IS_POWERFUL} (직접 추출)"]
    },
    {
        "id": 8,
        "num": "08",
        "part": "PART 02",
        "chapter": "Ch04",
        "title": "Level 5 - Time-based Blind SQLi (지연으로 한 글자씩 추출)",
        "difficulty": "★★★★☆",
        "category": "SQL Injection / Blind",
        "objective": "응답 시간 차이를 이용해 데이터를 추출. 앱 내부에 의도적으로 time.sleep 조건 분기를 넣어두었음. 실제 DB SLEEP(pg_sleep, SLEEP()) 연습도 함께.",
        "entry_points": [
            {"label": "고급 검색", "url": "http://127.0.0.1:5002/search?q=1'"},
        ],
        "missions": [
            "특정 조건이 참일 때만 sleep(3) 정도가 걸리도록 페이로드 작성",
            "FLAG{TIME_BASED_SQLi_MASTER} 를 시간 차이로 추출",
            "실제 MySQL/PostgreSQL 환경이라면 SLEEP(3), pg_sleep(3) 사용법도 기록"
        ],
        "success_criteria": "FLAG{TIME_BASED_SQLi_MASTER} 획득 (시간 차이로 확인)",
        "payload_examples": [
            "1' AND (SELECT CASE WHEN SUBSTR((SELECT flag FROM secrets WHERE id=3),1,1)='F' THEN sleep(3) ELSE 0 END) -- (앱 내부 지원)"
        ],
        "hints": [
            "이 앱은 실제 DB SLEEP이 제한적이어서 Python time.sleep으로 시뮬레이션함.",
            "Burp Intruder로 '타이밍' 자동화를 연습하면 좋습니다.",
            "실무에서는 네트워크 지연이 섞이므로 여러 번 측정 + 중앙값 사용."
        ],
        "solution": "Boolean blind가 불가능하거나 (응답 차이가 명확하지 않을 때) 마지막 보루가 되는 기법. 방어자 입장에서는 '에러도 주지 말고, 성공/실패 응답도 동일하게 주고, 시간도 동일하게 주라'는 교훈.",
        "secure_snippet": "동일. Time-based도 결국 입력이 쿼리에 직접 들어가기 때문에 가능한 공격.",
        "book_refs": "Ch04. 4.4 Time-based Blind SQLi",
        "lab_target": "VulnBoard",
        "flags": ["FLAG{TIME_BASED_SQLi_MASTER}"]
    },
    # ==================== PART 02 - 기타 공격 ====================
    {
        "id": 9,
        "num": "09",
        "part": "PART 02",
        "chapter": "Ch05",
        "title": "OS Command Injection - ping 도구를 이용한 서버 명령 실행",
        "difficulty": "★★☆☆☆",
        "category": "Command Injection",
        "objective": "/tools/ping 에서 host 값을 127.0.0.1 & whoami 또는 127.0.0.1 | dir 로 조작해 서버에서 임의 명령을 실행한다.",
        "entry_points": [
            {"label": "Ping 도구", "url": "http://127.0.0.1:5002/tools/ping"},
        ],
        "missions": [
            "127.0.0.1 & whoami 로 현재 사용자 확인",
            "127.0.0.1 & type vulnboard.db 로 DB 파일 내용 읽기 시도",
            "Windows 환경에 맞는 구분자 (&, &&, |, ||) 모두 테스트"
        ],
        "success_criteria": "whoami 결과 또는 DB 파일 내용이 화면에 출력된다.",
        "payload_examples": ["127.0.0.1 & whoami", "127.0.0.1 | dir C:\\", "127.0.0.1 & type vulnboard.db"],
        "hints": [
            "Windows는 ; 대신 & 또는 | 를 사용.",
            "명령어가 shell=True로 실행되기 때문에 OS 쉘 메타문자가 그대로 해석된다.",
            "성공한 명령 결과가 화면에 보이지 않더라도 에러 메시지나 다른 부수 효과로 확인 가능."
        ],
        "solution": "사용자 입력을 쉘 명령어 문자열에 직접 넣고 subprocess(..., shell=True)로 실행하면, 입력에 ; & | $() 등이 들어가는 순간 공격자가 명령어를 추가할 수 있다.",
        "secure_snippet": "subprocess.check_output(['ping', '-n', '1', host], shell=False)  # 리스트 형태 + shell=False\n# 또는 shlex.split + 화이트리스트 검증",
        "book_refs": "Ch05. OS 커맨드 인젝션 취약점",
        "lab_target": "VulnBoard",
        "flags": []
    },
    {
        "id": 10,
        "num": "10",
        "part": "PART 02",
        "chapter": "Ch06",
        "title": "Stored XSS - 댓글에 스크립트 삽입으로 세션 쿠키 탈취 시뮬레이션",
        "difficulty": "★★☆☆☆",
        "category": "XSS / Stored",
        "objective": "아무 게시글에 댓글을 작성할 때 <script>alert(document.cookie)</script> 또는 더 나아가 쿠키를 외부로 보내는 페이로드를 저장한다. Stored XSS의 위험성을 몸으로 느낀다.",
        "entry_points": [
            {"label": "게시글 상세 + 댓글", "url": "http://127.0.0.1:5002/post/1"},
        ],
        "missions": [
            "댓글에 <script>alert('XSS')</script> 작성 후 게시글 다시 보기",
            "document.cookie 를 alert 또는 console.log 로 출력",
            "(고급) img onerror 나 fetch로 외부 서버로 쿠키 전송 페이로드 작성 (이 랩에는 외부 서버가 없으니 console로 확인)"
        ],
        "success_criteria": "댓글을 단 후 페이지를 보는 모든 사용자(관리자 포함)의 브라우저에서 스크립트가 실행된다.",
        "payload_examples": [
            "<script>alert(document.cookie)</script>",
            "<img src=x onerror=\"console.log(document.cookie)\">"
        ],
        "hints": [
            "댓글 content가 | safe 없이 그대로 출력되거나, Jinja autoescape가 우회되는 지점.",
            "Stored XSS는 한 번 넣으면 영구적으로 발동 → 관리자 쿠키 탈취 가능.",
            "HttpOnly 쿠키는 document.cookie로 읽을 수 없지만, 여전히 많은 공격 포인트가 남아있다."
        ],
        "solution": "저장된 콘텐츠를 출력할 때 아무런 escaping/sanitizing을 하지 않으면, 다음에 보는 모든 사용자의 브라우저 컨텍스트에서 공격자 스크립트가 실행된다. 세션 탈취, 키로거, defacement 등으로 이어짐.",
        "secure_snippet": "Jinja2는 기본 autoescape가 켜져 있습니다. content를 {{ content }} 로 출력하면 안전. | safe 필터를 절대 함부로 쓰지 마라. 또는 bleach 등으로 HTML sanitizing.",
        "book_refs": "Ch06. XSS 취약점 + 세션 하이재킹",
        "lab_target": "VulnBoard",
        "flags": []
    },
    {
        "id": 11,
        "num": "11",
        "part": "PART 02",
        "chapter": "Ch07",
        "title": "CSRF - 토큰 없는 중요한 액션 (이메일 변경, 사용자 삭제 등)",
        "difficulty": "★★☆☆☆",
        "category": "CSRF",
        "objective": "/settings 에서 CSRF 토큰 없이 이메일을 변경할 수 있음을 확인. 실제 공격 시나리오를 상상하고, 나중에 다른 사이트의 폼으로 요청을 보내는 공격을 이해한다.",
        "entry_points": [
            {"label": "설정 페이지 (로그인 필요)", "url": "http://127.0.0.1:5002/settings"},
        ],
        "missions": [
            "로그인 후 /settings 에서 이메일 변경 정상 동작 확인",
            "Burp로 요청을 Repeater에 저장",
            "CSRF 토큰이 전혀 없는 것을 확인하고, '다른 사이트의 <form>으로 동일 요청을 보낼 수 있다'는 점을 이해"
        ],
        "success_criteria": "CSRF 토큰 부재를 확인하고, 왜 이게 위험한지 설명할 수 있다.",
        "payload_examples": [
            "<form action='http://127.0.0.1:5002/settings' method='POST'> <input name='email' value='hacked@evil.com'> ... </form>"
        ],
        "hints": [
            "POST 요청에 CSRF 토큰이나 SameSite 쿠키 정책이 전혀 없다.",
            "로그인한 상태의 쿠키가 브라우저에 있으면, 공격자 사이트의 폼 submit만으로도 요청이 간다.",
            "/admin/users/xx/delete 도 같은 취약점."
        ],
        "solution": "중요한 상태 변경 요청(이메일 변경, 비번 변경, 삭제, 송금 등)에 '이 요청이 정말 이 사용자가 의도한 것인가?'를 증명하는 값(CSRF 토큰)이 없으면, 공격자가 victim's 브라우저를 통해 요청을 대신 보낼 수 있다.",
        "secure_snippet": "Flask-WTF 또는 자체 CSRF 토큰 생성 + 검증. 모든 상태 변경 POST/PUT/DELETE에 token 검사. SameSite=Strict/Lax 쿠키도 도움이 됨.",
        "book_refs": "Ch07. CSRF 취약점",
        "lab_target": "VulnBoard",
        "flags": []
    },
    {
        "id": 12,
        "num": "12",
        "part": "PART 02",
        "chapter": "Ch08 / Ch09",
        "title": "파일 다운로드 Path Traversal + 업로드 기본 취약점",
        "difficulty": "★★☆☆☆",
        "category": "파일 관련",
        "objective": "/download?file=... 로 ../ 를 사용해 상위 디렉토리 파일 읽기. /upload 로 악성 파일(웹쉘) 업로드 후 실행 시도.",
        "entry_points": [
            {"label": "다운로드", "url": "http://127.0.0.1:5002/download?file=notice.txt"},
            {"label": "파일 업로드", "url": "http://127.0.0.1:5002/upload"},
        ],
        "missions": [
            "/download?file=../../../app.py 또는 vulnboard.db 시도",
            "/upload 에서 .txt 외의 파일 (예: .py) 업로드 후 /uploads/ 로 직접 접근",
            "업로드 후 파일명에 경로 조작 (secure_filename의 한계 체감)"
        ],
        "success_criteria": "app.py 소스나 DB 파일 내용이 다운로드되거나, 업로드한 파일이 실행 가능한 위치에 저장됨을 확인",
        "payload_examples": ["?file=../../../app.py", "파일명에 ../ 포함 또는 확장자 우회"],
        "hints": [
            "send_from_directory가 사용자 입력 filename을 그대로 쓰고 있다.",
            "secure_filename은 기본적인 sanitization만 하고, 여전히 위험할 수 있다.",
            "업로드 후 바로 실행 가능한 위치에 저장 + 확장자 검사 미흡 = 웹쉘."
        ],
        "solution": "파일 경로를 사용자 입력으로 받을 때 상위 디렉토리 이동(../../../)을 막지 않으면, 서버의 중요한 파일이 노출된다. 업로드는 '어디에, 어떤 이름으로, 어떤 확장자로, 실행 가능한가?'를 모두 통제해야 안전.",
        "secure_snippet": "절대 사용자 입력을 경로로 직접 사용하지 말 것. 화이트리스트 확장자, 랜덤 파일명, 별도 비실행 저장소, Content-Type 검사, 다운로드 시 attachment + sandboxed 도메인.",
        "book_refs": "Ch08 파일 다운로드, Ch09 파일 업로드",
        "lab_target": "VulnBoard",
        "flags": []
    },
    {
        "id": 13,
        "num": "13",
        "part": "PART 02",
        "chapter": "Ch10 / Ch11",
        "title": "IDOR + Broken Access Control - 프로필과 관리자 페이지 우회",
        "difficulty": "★★☆☆☆",
        "category": "접근 제어 미흡 / IDOR",
        "objective": "로그인하지 않았거나 일반 사용자로 /profile/admin, /profile/sumi, /admin 에 직접 접근하거나, Burp로 username이나 is_admin을 조작해 권한을 얻는다.",
        "entry_points": [
            {"label": "프로필 (IDOR)", "url": "http://127.0.0.1:5002/profile/admin"},
            {"label": "관리자 패널", "url": "http://127.0.0.1:5002/admin"},
        ],
        "missions": [
            "일반 계정(chulsu)으로 로그인 후 /profile/sumi 직접 이동",
            "/admin 직접 접근 시도 (is_admin 세션 없이)",
            "SQLi로 로그인하면서 is_admin=1 세션 강제 주입",
            "Burp로 /profile 요청의 쿠키나 파라미터를 조작"
        ],
        "success_criteria": "admin의 비밀 정보 또는 /admin의 전체 사용자/ secrets 목록을 일반 권한으로 확인",
        "payload_examples": ["/profile/admin", "/admin (직접)", "SQLi 후 세션 is_admin=1"],
        "hints": [
            "서버가 '이 사용자가 이 리소스를 볼 권한이 있는가?'를 매 요청마다 확인하지 않음.",
            "세션의 is_admin 플래그만 믿고 있음 (SQLi로 세션 값을 통제 가능).",
            "URL 직접 접근, 파라미터 변조, 쿠키 변조, SQLi를 통한 권한 상승 모두 IDOR/BAC의 일부."
        ],
        "solution": "클라이언트가 보내는 '나는 admin이다' 신호(세션, 파라미터, 쿠키)를 서버가 무조건 신뢰하면 안 된다. 매번 '현재 인증된 사용자가 이 특정 리소스에 대한 권한을 가지고 있는가?'를 DB/정책으로 재확인해야 한다.",
        "secure_snippet": "def admin_panel():\n    if not session.get('is_admin'): abort(403)\n    # 추가: 실제 DB에서 다시 확인\n    user = get_user(session['user_id'])\n    if not user.is_admin: abort(403)",
        "book_refs": "Ch10 파라미터 변조, Ch11 URL 접근 제한 미흡",
        "lab_target": "VulnBoard",
        "flags": []
    },
    # ==================== PART 03 - 방어 ====================
    {
        "id": 14,
        "num": "14",
        "part": "PART 03",
        "chapter": "Ch12",
        "title": "방어 실습 - SQL Injection을 코드로 막기 (VULNERABLE 주석 찾고 고치기)",
        "difficulty": "★★☆☆☆",
        "category": "시큐어 코딩 / SQLi",
        "objective": "VulnBoard app.py를 열고 # VULNERABLE: 이 붙은 모든 f-string 쿼리를 찾는다. execute_vulnerable_query를 사용한 곳을 전부 ? placeholder 방식으로 고쳐본다. (실제로 고쳐서 /reset 후 테스트 추천)",
        "entry_points": [
            {"label": "VulnBoard 소스 (app.py)", "url": "파일 열기: app.py"},
            {"label": "취약 쿼리 위치 예시", "url": "http://127.0.0.1:5002/debug/db"},
        ],
        "missions": [
            "app.py에서 f\"... WHERE ... '{variable}'\" 형태의 쿼리 전부 찾기 (board, post, login, search 등)",
            "execute_vulnerable_query 함수의 위험성 이해",
            "하나씩 ? placeholder + c.execute(query, params) 로 고쳐보기",
            "고친 후 실제로 SQLi 페이로드가 안 먹히는지 /reset 후 테스트"
        ],
        "success_criteria": "원래 성공하던 SQLi 페이로드 (admin' -- ) 가 더 이상 로그인 우회를 못 하게 만든다.",
        "payload_examples": ["고치기 전/후 비교"],
        "hints": [
            "가장 쉬운 방어는 '문자열을 절대 쿼리에 직접 넣지 않는 것'.",
            "Prepared statement (placeholder)는 DB 드라이버가 알아서 이스케이프해준다.",
            "ORM을 쓰면 더 안전하지만, raw query를 쓸 때는 항상 신경 써야 한다."
        ],
        "solution": "공격을 배운 후, '이 한 줄 때문에 모든 게 뚫렸다'는 걸 코드로 확인하고, '이렇게 고치면 안전하다'는 걸 직접 고쳐보면서 체득하는 것이 Part 03의 핵심이다.",
        "secure_snippet": "query = \"SELECT * FROM users WHERE username = ? AND password = ?\"\nrows = c.execute(query, (username, password)).fetchall()",
        "book_refs": "Ch12. SQL 인젝션 취약점 - 방어 (12.1 원인과 대응, 12.2 시큐어 코딩 실습)",
        "lab_target": "VulnBoard 소스코드 + 실제 고쳐보기",
        "flags": []
    },
    {
        "id": 15,
        "num": "15",
        "part": "PART 03",
        "chapter": "Ch13~19",
        "title": "종합 방어 실습 - 나머지 취약점의 시큐어 버전 생각하고 코드에 반영하기",
        "difficulty": "★★★☆☆",
        "category": "시큐어 코딩 종합",
        "objective": "app.py의 모든 VULNERABLE 주석 위치를 찾고, 각 공격(Ch05~Ch11)에 해당하는 방어 코드를 직접 머릿속 또는 실제로 작성해본다. 책 Part 03의 각 챕터와 1:1 매칭.",
        "entry_points": [
            {"label": "전체 소스 분석", "url": "app.py + templates/"},
        ],
        "missions": [
            "Command Injection (ping) → shell=False + 인자 리스트화",
            "XSS (댓글) → Jinja autoescape 신뢰 + | safe 제거, 필요시 sanitizing",
            "CSRF (settings) → 토큰 추가 (Flask-WTF 추천)",
            "파일 업로드/다운로드 → 화이트리스트 + 랜덤명 + 별도 경로 + 접근 제어",
            "IDOR/BAC (/profile, /admin) → 매 요청마다 소유자/권한 재검증",
            "위 모든 수정을 한 번에 적용한 'secure_board' 버전을 만들어보기 (선택 과제)"
        ],
        "success_criteria": "각 공격 기법마다 '이 코드 한 줄/구조가 문제였고, 이렇게 고치면 안전하다'는 설명을 1개 이상 할 수 있다.",
        "payload_examples": [],
        "hints": [
            "공격 실습 때 성공했던 페이로드를 다시 시도하면서 '지금은 왜 안 될까?'를 확인하는 게 최고의 공부.",
            "방어는 '한 가지 방법'이 아니라 '여러 겹의 방어 (Defense in Depth)'가 정석.",
            "에러 메시지 노출 금지, 최소 권한, 입력 검증, 출력 인코딩, 토큰, 로깅 등."
        ],
        "solution": "Part 03은 '공격으로 배운 걸 방어로 연결'하는 챕터다. 이 문제집의 모든 공격 문제를 푼 후에 소스코드를 보면, '아 이게 바로 그 취약점이었구나'가 한눈에 들어온다. 그 상태에서 고치는 연습을 하는 것이 진짜 마스터.",
        "secure_snippet": "각 항목별로 app.py 주석과 책 Ch12~19의 '시큐어 코딩 실습' 부분을 함께 보세요.",
        "book_refs": "Ch12~19 전체 (각 공격 기법별 방어)",
        "lab_target": "VulnBoard 소스코드 전면 분석 + 수정 실습",
        "flags": []
    },
]

# ==================== 헬퍼 함수 ====================

def get_problem(pid: int):
    for p in PROBLEMS:
        if p["id"] == pid:
            return p
    return None

def get_problems_by_part(part_name: str):
    return [p for p in PROBLEMS if p["part"] == part_name]

def get_problems_by_chapter(chapter: str):
    return [p for p in PROBLEMS if p["chapter"] == chapter]

def get_all_parts():
    seen = []
    for p in PROBLEMS:
        if p["part"] not in seen:
            seen.append(p["part"])
    return seen

def get_progress_stats(solved_ids: list):
    total = len(PROBLEMS)
    solved = len([sid for sid in solved_ids if sid in [p["id"] for p in PROBLEMS]])
    return {
        "total": total,
        "solved": solved,
        "percent": int(solved / total * 100) if total else 0
    }
