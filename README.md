# 크리핵티브의 한 권으로 끝내는 웹 해킹 바이블 - 정복용 인터랙티브 실습 랩

**이 랩의 목표**: 책을 읽기만 하는 것이 아니라, **사이트를 체계적으로 따라가면서 책의 거의 모든 주요 내용을 몸으로 정복**하는 것.

## 현재 추천 학습 루트

### 1. 기초 복습 (이미 책 중간까지 했다면 스킵 가능)
- `01-basics/` : 왜 웹이 공격 맛집인가? (입력값 검증 미흡의 본질)
- `02-http-curl-devtools/` : **HTTP 기초 정복 — 브라우저 개발자도구 + curl로 직접 요청 보내고 받기** (강력 추천, Burp 이전에 먼저!)
- `02-http-burp/` : HTTP + Burp Suite 완전 정복 (curl 기초를 다진 후에 하면 훨씬 효과가 좋습니다)

### 2. 메인 타겟: VulnBoard (지금부터 여기 집중!)
```
webhacking-bible-lab/vulnboard/
├── app.py                    ← 모든 취약점이 들어있는 메인 앱
├── HACKING_CHALLENGES.md     ← 구체적인 해킹 미션 + FLAG 목록 (여기서 시작)
├── templates/                ← 실제 웹사이트 UI
└── uploads/                  ← 파일 업로드 실습용 폴더
```

**실행**:
```powershell
cd vulnboard
python app.py
```
→ http://127.0.0.1:5002

**가장 먼저 할 일**: VulnBoard 접속 후 상단 **📖 학습 가이드** (책 정복 로드맵) 클릭.

이 로드맵을 따라가면 Ch01부터 Ch19(방어)까지 책의 주요 내용을 실습으로 정복할 수 있도록 설계했습니다.

- Ch04 SQL Injection은 VulnBoard가 가장 강력하게 커버
- Ch05~Ch11 주요 공격 기법도 모두 매핑
- Part 03 방어는 "공격으로 배운 후 코드에서 VULNERABLE 주석을 보면서 생각하는" 방식으로 지원

준비되면 `cd vulnboard && python app.py` 실행 → **📖 학습 가이드**부터 따라가세요.

### 학습 순서 팁 (중요)
- **curl + DevTools 먼저** (`02-http-curl-devtools`) → HTTP를 손으로 직접 만드는 감을 익히세요.
- 그 다음 Burp (`02-http-burp`)를 배우면 "이 도구가 왜 이렇게 편한지"가 제대로 와닿습니다.
- Burp는 강력하지만, 처음부터 Burp만 쓰면 curl/DevTools로 직접 조작하는 근력이 약해집니다.
