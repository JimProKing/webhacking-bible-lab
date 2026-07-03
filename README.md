# VulnBoard

**크리핵티브의 「한 권으로 끝내는 웹 해킹 바이블」을 읽으면서, 직접 부숴보는 실습장**

책만 읽다 보면 SQL Injection이나 XSS가 "남의 이야기"처럼 느껴진다.  
이 프로젝트는 그 갭을 메우려고 만든 **의도적으로 취약한 게시판**이다. 로그인을 우회하고, DB를 털고, 세션을 훔치고, 코드를 고쳐본다. 공격이 성공하는 순간, 방어가 왜 필요한지 비로소 보인다.

> **교육용 전용.** 실제 서비스나 남의 시스템에 쓰지 마세요.

**🌐 배포 사이트 (Railway):** [https://web-production-debfb.up.railway.app/](https://web-production-debfb.up.railway.app/)

로컬 설치 없이 바로 접속해서 문제집(`/lab`)과 실습을 시작할 수 있습니다. Burp로 본격 연습할 때는 로컬 실행을 권장합니다.

---

## 이 저장소에서 하는 일

| 구성 요소 | 역할 |
|-----------|------|
| **`app.py`** | 메인 취약 게시판 (Flask + SQLite). 문제 04번부터 대부분의 공격이 여기서 일어남 |
| **`/practice/01~03`** | 문제 1~3 미니 실습 (파라미터 변조, curl, Burp) — Railway 배포에도 포함 |
| **`problems/`** | **여기가 진짜 교재.** 문제 01~20, 폴더 하나 = 문제 하나. `README.md` → 풀기 → `풀이.md` |
| **`/lab`** | 웹 UI 문제집 인덱스 (참고용). 진행 추적은 `problems/` 폴더가 더 명확함 |
| **`HACKING_CHALLENGES.md`** | 자유 연습용 챌린지 목록 (FLAG, 난이도별 미션) |

---

## 30초 만에 시작

**가장 빠른 방법:** [배포 사이트](https://web-production-debfb.up.railway.app/) 열기 → [정복 문제집](https://web-production-debfb.up.railway.app/lab)에서 문제 01부터

**로컬에서 실행:**

```powershell
git clone https://github.com/JimProKing/webhacking-bible-lab.git
cd webhacking-bible-lab
pip install -r requirements.txt
python app.py
```

브라우저: **http://127.0.0.1:5002**

**Burp Suite**를 켜세요. 이 프로젝트의 절반은 Burp Repeater로 공격하는 습관을 만드는 데 쓰입니다.

기본 계정 (연습용):
- `admin` / `admin123!@#`
- `chulsu` / `test123`

DB가 꼬이면 **http://127.0.0.1:5002/reset** — 실험하다 망가뜨려도 괜찮습니다.

---

## 어떻게 공부하면 되나

**`problems/` 폴더를 01번부터 순서대로** 여세요.

```
problems/
├── 01-파라미터-변조-기초/     ← Ch01. "입력값 검증 미흡"이 뭔지 몸으로 느끼기
├── 02-HTTP-직접-조작-curl-devtools/
├── 03-Burp-Repeater-마스터/
├── 04-로그인-SQLi-우회/       ← 여기부터 VulnBoard 본격 공격
├── ...
└── 20-종합-방어/
```

한 문제의 흐름:

1. 폴더 안 `README.md` 읽기
2. 미션 수행 (막히면 30분은 스스로 고민)
3. `풀이.md`로 근본 원인 확인
4. 다음 번호 폴더로 이동

웹의 `/lab` 페이지도 있지만, **"내가 어디까지 했지?"** 는 폴더 구조가 더 잘 보여줍니다.

---

## 커리큘럼 한눈에

| 구간 | 책 | 내용 |
|------|-----|------|
| 01~03 | Ch01~02 | 파라미터 변조, curl/DevTools, Burp Repeater |
| 04~08 | Ch04 | SQL Injection 전부 (로그인 우회, UNION, Blind, Time-based) |
| 09~13 | Ch05~11 | Command Injection, XSS, CSRF, 파일 취약점, IDOR |
| 14~20 | Ch12~19 | 소스 열어서 방어 코드 직접 쓰기 |

자세한 학습 가이드: [`MASTER_PROBLEM_BOOK.md`](MASTER_PROBLEM_BOOK.md)

---

## 프로젝트 구조

```
.
├── README.md                 ← 지금 읽는 파일
├── app.py                    ← VulnBoard 메인 (취약점은 # VULNERABLE: 주석)
├── lab_problems.py           ← /lab 페이지 문제 데이터
├── HACKING_CHALLENGES.md     ← 추가 챌린지
├── MASTER_PROBLEM_BOOK.md    ← 상세 커리큘럼
├── requirements.txt
├── templates/                ← 게시판 UI
├── problems/                 ← 문제집 (학습의 중심)
└── uploads/
```

---

## 이 프로젝트를 쓰기 전에

- [ ] **Burp Suite Community** 설치됨
- [ ] Python 3 설치됨
- [ ] 책 해당 챕터를 최소 한 번 읽었음 (이론 없이 페이로드만 외우면 금방 막힘)
- [ ] 풀이를 바로 열지 않기로 다짐함

---

## 완료했다고 말할 수 있는 기준

- [ ] `admin' --` 로 로그인 우회를 **왜** 되는지 SQL 쿼리 수준에서 설명할 수 있다
- [ ] UNION / Boolean Blind / Time-based를 각각 한 번 이상 성공시켰다
- [ ] XSS, CSRF, IDOR을 Repeater로 재현했다
- [ ] `app.py`의 `# VULNERABLE:` 부분을 열어 방어 코드를 직접 써봤다
- [ ] 각 문제 풀이를 읽고 "근본 원인 + 막는 법"을 말로 설명할 수 있다

---

## 다음에 할 것

책 + 이 문제집을 끝냈다면:

- [PortSwigger Web Security Academy](https://portswigger.net/web-security) — 무료, 품질 좋음
- 책 저자 공식 `insecure_board` (JSP + Tomcat) — 더 현실적인 환경
- CTF (pwnable.kr, webhacking.kr 등)

---

## 주의

이 코드는 **일부러** 안전하지 않게 짜여 있습니다.  
로컬에서만 돌리세요. 실제 서비스에 배포하거나, 허가 없는 시스템에 테스트하면 법적 문제가 됩니다.

---

**문제 01 폴더를 열고, Burp를 켜고, 시작하세요.**

공격이 되는 순간, 그때 비로소 웹 해킹이 "내 것"이 됩니다.