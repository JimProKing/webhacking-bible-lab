# 문제 05. UNION 기반 SQL Injection으로 secrets 테이블 털기

**책 매핑**: Chapter 04. SQL 인젝션 (4.4 UNION 기반 공격 방법론)

**난이도**: ★★★☆☆

**실습 타겟**: VulnBoard /board 또는 /search

---

## 학습 목표

- 에러 기반으로 컬럼 수를 알아내는 방법 (ORDER BY)
- UNION SELECT로 다른 테이블 데이터 덤프
- 실제 "secrets" 테이블의 FLAG 여러 개를 직접 획득
- 컬럼 수/타입 맞추는 근육 기르기

## 미션 (중요한 순서)

1. 검색창에 `' ORDER BY 1-- ` 부터 시작해서 컬럼 수 찾기 (에러 나는 직전 숫자)
2. `' UNION SELECT 1,2,3,4,5,6 -- ` 로 기본 UNION 성공 확인
3. users 테이블 데이터 추출 (username, password, is_admin)
4. **secrets 테이블에서 FLAG 최소 3개 이상 화면에 노출** (최종 목표)

## 성공 기준

- `FLAG{SQLi_UNION_is_classic}`
- `FLAG{BLIND_SQLi_IS_POWERFUL}`
- 등 secrets 테이블의 플래그들이 보임

## 핵심 페이로드 패턴

```sql
' UNION SELECT id, owner, secret, flag, 5, 6 FROM secrets --
```

## 힌트

- 에러 메시지가 컬럼 수를 알려줍니다. 무시하지 마세요.
- secrets 테이블 구조: id, owner, secret, flag
- Burp Repeater로만 작업하세요. 브라우저에서 타이핑하는 것은 자해 행위입니다.

---

이 문제가 끝나면 Ch04의 UNION 기반은 거의 마스터한 수준입니다.

다음: 06-ID기반-SQLi (현실에서 가장 흔한 패턴)