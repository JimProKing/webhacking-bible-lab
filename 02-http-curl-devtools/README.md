# 모듈 02 — HTTP를 손으로 직접 주고받기 (Ch02 기초 근육)

**실습 교재 내 위치**: 문제 02

이 모듈의 목적은 **Burp Suite를 배우기 전에, HTTP 프로토콜을 직접 손으로 다루는 감각**을 기르는 것입니다.

---

## 학습 목표

- curl.exe와 브라우저 Console(fetch)로 GET/POST/쿠키를 직접 작성하고 조작할 수 있다.
- "Copy as cURL", "Copy as fetch" 기능을 자유자재로 사용할 수 있다.
- 쿠키를 직접 조작해 세션 하이재킹을 체험한다.
- 나중에 Burp를 만났을 때 "이게 왜 이렇게 편한지"를 제대로 느낄 수 있다.

---

## 왜 Burp 전에 이걸 먼저 해야 하는가?

Burp는 강력한 도구지만, 처음부터 Burp만 쓰면 "HTTP가 실제로 어떻게 생겼는지"에 대한 직관이 약해집니다.  
이 모듈은 Burp 이전에 **직접 HTTP를 만들어 보는 근육**을 만드는 단계입니다.

---

## 실습 진행 방법 (추천 순서)

1. 앱 실행
   ```powershell
   cd 02-http-curl-devtools
   python app.py
   ```
   접속: http://127.0.0.1:5003

2. GET 파라미터 조작 (curl)
   - `/profile?user=chulsu` 정상 동작 확인
   - curl로 `?user=sumi`, `?user=admin` 직접 조작

3. POST + Body 다루기
   - 로그인 폼을 브라우저로 한 번 전송 → Network 탭에서 "Copy as cURL"
   - PowerShell에서 직접 curl 명령어 작성해서 로그인

4. 쿠키 / 세션 하이재킹 (가장 중요)
   - 로그인 후 발급되는 `session_user` 쿠키를 curl로 직접 넣어서 `/myinfo` 보기
   - `session_user=admin` 으로 바꿔서 관리자 정보 탈취

5. Console(fetch) 실습 (강력 추천)
   - F12 → Console에서 `fetch()`로 로그인, 정보 조회, 로그아웃 모두 해보기
   - `credentials: 'include'` 의 의미를 정확히 이해하기

6. 요청 가로채기 맛보기
   - Network 탭에서 요청을 보고 "Edit and Resend" 또는 "Copy as fetch" 연습

---

## 자가 평가 질문

- [ ] PowerShell에서 `curl.exe`와 `curl`의 차이를 설명할 수 있는가?
- [ ] 로그인 후 받은 쿠키를 직접 복사해서 다른 브라우저/터미널에서 사용할 수 있는가?
- [ ] Console에서 `fetch(..., {credentials: 'include'})` 없이 쿠키가 안 따라가는 이유를 아는가?

---

## 이 모듈을 마치고 나면

**반드시** 02-http-burp 모듈로 넘어가서, "Burp가 이 모든 걸 얼마나 편하게 해주는지"를 체감하세요.

이 모듈을 제대로 하지 않으면 Burp를 배워도 "그냥 마법의 도구"로만 보입니다.

---

**다음**: 02-http-burp 모듈 (문제 03) + 본격 VulnBoard 문제집 시작

**참고**: 이 모듈의 실습은 실습 교재의 **문제 02**와 직접 연결됩니다.