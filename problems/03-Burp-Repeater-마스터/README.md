# 문제 03. Burp Suite Repeater 완전 마스터

**책 매핑**: Chapter 02. Burp Suite의 주요 기능 + 기본 사용법

**난이도**: ★★☆☆☆

---

## 학습 목표

- 모든 웹 해킹 실습을 **Burp Repeater 중심**으로 하는 습관을 들인다.
- "브라우저 주소창으로 공격하는 것은 진짜 해킹이 아니다"는 마인드 획득
- Repeater에서 요청을 복제 → 수정 → 반복 전송하는 플로우를 체화

## 실습 타겟

폴더 안에 있는 작은 앱 (02-http-burp에서 복사됨) 또는 메인 VulnBoard를 사용하세요.

**추천**: 메인 VulnBoard를 켜고 이 문제의 미션을 수행하세요.

## 미션

1. Burp Proxy Intercept를 켜고 로그인 폼 전송 → body 구조 확인
2. `/profile?user=chulsu` 요청을 Repeater로 보내기
3. Repeater에서 `user` 값을 sumi, admin으로 여러 번 바꿔 전송
4. 로그인 후 받은 쿠키를 Repeater에서 직접 `admin`으로 변경해 요청
5. 성공한 공격은 Repeater 탭 이름을 명확히 붙이기 (예: profile-admin)

## 성공 기준

- Burp Repeater 없이 이 문제의 모든 공격을 수행할 수 없다고 느낀다.
- Repeater 탭 5개 이상 열고 작업하는 것이 자연스럽다.

## 중요한 팁 (책 정신)

- Repeater는 "생각하면서 공격"하는 공간입니다.
- 한 번 성공한 요청은 절대 잃어버리지 마세요. 탭 이름을 잘 지으세요.
- History를 자주 들여다보세요.

---

이 문제가 끝나면 이제부터 **모든 문제는 Burp Repeater로만** 풉니다.

`04-로그인-SQLi-우회` 로 이동하세요.