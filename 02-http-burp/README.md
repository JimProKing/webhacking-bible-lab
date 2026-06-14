# 모듈 03 — Burp Suite로 모든 트래픽을 가로채고 반복 공격하기 (Ch02)

**실습 교재 내 위치**: 문제 03

이 모듈은 **Burp Suite를 진짜 해킹 도구로 사용하는 법**을 배우는 단계입니다.  
이전 모듈(02-http-curl-devtools)에서 직접 HTTP를 다뤄본 사람만이 Burp의 진가를 제대로 느낄 수 있습니다.

---

## 학습 목표

- Burp Proxy를 통해 모든 요청을 가로채고 관찰할 수 있다.
- Repeater를 사용해 하나의 요청을 수십 번 변조하면서 공격할 수 있다.
- History를 통해 과거 요청을 다시 불러와 분석하는 습관을 들인다.
- "브라우저 주소창으로 하는 행위는 진짜 해킹이 아니다"라는 마인드를 체득한다.

---

## Burp 없이 웹 해킹은 상상할 수 없다

책에서도 반복 강조하듯이, Burp Suite는 웹 해킹의 필수 도구입니다.  
이 모듈에서는 "도구 사용법"을 넘어서, **Repeater 중심의 사고방식**을 기르는 데 집중합니다.

---

## 실습 진행 방법

1. 준비
   - Burp Suite 실행 + Proxy Intercept ON
   - 브라우저 프록시를 127.0.0.1:8080으로 설정 (FoxyProxy 강력 추천)

2. 앱 실행
   ```powershell
   cd 02-http-burp
   python app.py
   ```
   접속: http://127.0.0.1:5001

3. 필수 연습 (이걸 최소 3번 이상 반복)
   - 로그인 폼 전송 → Burp에서 body 확인
   - `/profile?user=chulsu` 요청을 Repeater로 보내기
   - Repeater에서 `user` 값을 `sumi`, `admin`으로 바꿔가며 전송
   - 로그인 후 받은 쿠키를 Repeater에서 직접 `admin`으로 변경해서 `/myinfo` 요청

4. 고급 습관 들이기
   - 성공한 공격은 Repeater 탭 이름을 명확히 붙이기 (예: `profile-admin-tamper`)
   - HTTP History에서 과거 요청을 찾아 다시 Repeater로 불러오기
   - Decoder 탭으로 URL 인코딩, Base64 등 간단히 다뤄보기

---

## 자가 평가 질문

- [ ] Burp Repeater 없이 이 모듈의 모든 실습을 할 수 있겠는가? (할 수 없어야 정상)
- [ ] 한 번 본 요청을 Repeater에서 10번 이상 변조해 본 적이 있는가?
- [ ] "이 요청이 실제로 서버에 어떻게 날아가는지"를 Burp로 확인하는 것이 습관이 되었는가?

---

## 이 모듈을 마치고 나면

이제부터 **모든 실습은 Burp Repeater로만** 진행합니다.

- 01-basics, 02-http-curl-devtools는 기초 근육용
- 앞으로의 모든 문제(문제 04부터)는 **VulnBoard + Burp** 조합으로 진행

Burp를 켜지 않고 문제집을 진행하는 것은 의미가 없습니다.

---

**다음**: 본격 실습 교재 시작 — `/lab` 페이지의 문제 04부터 (Ch04 SQL Injection)

이 모듈의 실습은 실습 교재의 **문제 03**과 직접 연결됩니다.