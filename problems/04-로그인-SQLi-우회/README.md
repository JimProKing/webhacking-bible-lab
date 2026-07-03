# 문제 04. 로그인 SQL Injection 우회 (가장 기본)

**책 매핑**: Chapter 04. SQL 인젝션 취약점 (4.1~4.4, 로그인 우회 파트)

**난이도**: ★★☆☆☆

**실습 타겟**: 메인 VulnBoard (`python app.py` — 저장소 루트에서 실행)

---

## 학습 목표

- SQL Injection의 가장 고전적이고 강력한 형태 (인증 우회)를 직접 성공
- 쿼리 구조를 역으로 상상하는 능력 기르기
- 주석(`-- `, `#`)의 역할 이해
- Burp Repeater로 반복 공격하는 습관

## 진입점

VulnBoard 실행 후: http://127.0.0.1:5002/login

## 미션

1. chulsu / test123 로 정상 로그인 관찰 (Burp Repeater에 저장)
2. 다음 페이로드로 admin 계정 우회 시도:
   - `admin' -- `
   - `admin' OR '1'='1' -- `
   - `' OR '1'='1' LIMIT 1 -- `
3. 로그인 성공 후 /admin 접근 가능한지 확인 (is_admin 세션)

## 성공 기준

- admin으로 로그인 성공
- 상단에 관리자 메뉴가 보이거나 /admin 페이지가 열림
- "이 쿼리가 실제로 어떻게 생겼을까?"를 상상하면서 공격한 경험

## 추천 페이로드 (직접 타이핑하면서 테스트)

```text
admin' -- 
admin' OR 1=1 --
' OR '1'='1' --
admin' OR '1'='1' LIMIT 1 --
```

**각 페이로드를 넣으면서 Burp Repeater에서 한 번씩 Send 해보고, 응답이 어떻게 달라지는지 관찰하세요.**

## 힌트 (더 자세히)

서버가 로그인할 때 실행하는 쿼리는 대략 이런 형태일 가능성이 매우 높습니다:

```sql
SELECT * FROM users 
WHERE username = '사용자가 입력한 값' 
  AND password = '사용자가 입력한 값'
```

여기에 `admin' -- ` 를 넣으면 실제로 서버에 전달되는 쿼리는 다음과 같이 변형됩니다:

```sql
SELECT * FROM users 
WHERE username = 'admin' -- ' 
  AND password = '아무거나'
```

- `'` : 기존 따옴표를 닫아서 username 조건을 끝냄
- `-- ` : 뒤에 오는 모든 내용을 **SQL 주석**으로 만들어 버림 (AND password 부분이 사라짐)
- 결과적으로 `WHERE username = 'admin'` 만 남아서 admin 계정이 반환됨

에러 메시지와 응답 길이, 리다이렉트 여부 등을 잘 관찰하면 쿼리 구조를 역으로 유추할 수 있습니다.

## 자가 점검

- [ ] 왜 비밀번호를 모르고도 로그인이 되는가?
- [ ] 주석이 없으면 이 공격이 왜 어려워지는가?

---

**다음**: 05-UNION-SQLi-데이터-추출 (더 강력한 데이터 탈취)