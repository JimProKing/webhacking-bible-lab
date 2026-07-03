# 문제 02. HTTP를 손으로 직접 조작하기 (curl + DevTools)

**책 매핑**: Chapter 02. 반드시 알아야 할 웹 해킹 기본 지식 (2.2 HTTP 핵심, 2.8 웹 프록시 이전 단계)

**난이도**: ★☆☆☆☆

---

## 학습 목표

- Burp를 배우기 전에 HTTP 요청/응답을 **직접 손으로** 만들고 수정하는 근육을 기른다.
- "Copy as cURL", Console fetch, 쿠키 조작 등을 자연스럽게 할 수 있다.
- 나중에 Burp를 만났을 때 왜 그렇게 강력한지 체감한다.

## 실습 타겟

이 문제 전용 앱이 폴더 안에 있습니다.

```powershell
cd problems/02-HTTP-직접-조작-curl-devtools
python app.py
```

접속: http://127.0.0.1:5003

## 주요 미션 (자세히 따라하세요)

### 1. GET 파라미터 변조 (curl 기초)
- 먼저 브라우저로 `http://127.0.0.1:5003/profile?user=chulsu` 정상 확인
- PowerShell에서 아래 명령어를 직접 타이핑해서 실행해보세요:

```powershell
curl.exe "http://127.0.0.1:5003/profile?user=sumi" -v
curl.exe "http://127.0.0.1:5003/profile?user=admin" -i
```

**이 명령어들을 치면서 다음을 스스로 생각해보기**:
- `-v` 는 무엇을 보여줄까?
- `-i` 는 `-v` 와 어떻게 다를까?
- URL 뒤 `?user=xxx` 부분을 바꾸는 것이 정확히 어떤 HTTP 요청을 만드는 것일까?

### 2. POST + Body 다루기
- 브라우저에서 로그인 폼을 한 번 전송 (chulsu / test123)
- F12 → Network 탭 → "login" 요청 찾기 → 우클릭 → **Copy as cURL (cmd)**
- PowerShell에 붙여넣은 후, 아래처럼 직접 작성해보기:

```powershell
curl.exe "http://127.0.0.1:5003/login" `
  -X POST `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=chulsu&password=test123" `
  -i
```

### 3. 쿠키 / 세션 하이재킹 (가장 중요한 미션)
로그인 후 발급되는 쿠키를 직접 빼내서 조작하는 연습입니다.

기본 패턴 (반드시 외우고 손으로 쳐보세요):

```powershell
# 1. 로그인하면서 쿠키를 파일로 저장
curl.exe "http://127.0.0.1:5003/login" -X POST -d "username=chulsu&password=test123" -c cookies.txt -i

# 2. 저장된 쿠키를 사용해서 요청 보내기 (정상 세션)
curl.exe "http://127.0.0.1:5003/myinfo" -b cookies.txt -i

# 3. 쿠키 값을 직접 조작해서 세션 하이재킹 (이게 핵심!)
curl.exe "http://127.0.0.1:5003/myinfo" -b "session_user=admin" -i
```

### 4. 브라우저 Console(fetch) 실습
F12 → Console 탭에서 아래 코드를 붙여넣고 실행해보세요.

```js
// 로그인
fetch("http://127.0.0.1:5003/login", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({ username: "chulsu", password: "test123" }),
  credentials: "include"
}).then(r => r.text()).then(console.log);

// 로그인 후 내 정보 확인
fetch("http://127.0.0.1:5003/myinfo", { credentials: "include" })
  .then(r => r.text()).then(console.log);
```

## 성공 기준

- 위 curl 명령어들을 **직접 손으로 타이핑**하면서 각 플래그(`-v`, `-i`, `-b`, `-c`, `-H`, `-d`, `-X`)의 의미를 설명할 수 있다.
- 쿠키 값을 직접 바꿔서 admin 정보를 보는 데 성공했다.
- "HTTP는 브라우저가 알아서 해주는 게 아니라, 내가 직접 만드는 것"이라는 감각이 생겼다.

## 반드시 알아야 할 curl 주요 플래그 (이 문제에서 꼭 이해하기)

| 플래그       | 의미                                      | 이 문제에서 왜 중요한가?                  | 예시 |
|--------------|-------------------------------------------|-------------------------------------------|------|
| `-v`         | Verbose (자세한 정보 출력)                 | 요청 헤더 + 응답 헤더 + TLS 정보까지 모두 보여줌 | `-v` |
| `-i`         | Include response headers                   | 응답 헤더(Set-Cookie 등)를 쉽게 확인     | `-i` |
| `-b`         | Bring cookie (쿠키 파일 또는 직접 값)      | 저장된 쿠키나 직접 쿠키 값으로 요청      | `-b cookies.txt` 또는 `-b "session_user=admin"` |
| `-c`         | Cookie jar (쿠키 저장)                     | 로그인 후 받은 쿠키를 파일로 저장        | `-c cookies.txt` |
| `-H`         | Header 추가                                | Content-Type, Cookie 등을 직접 지정      | `-H "Content-Type: ..."` |
| `-d`         | Data (POST body)                           | 폼 데이터를 전송                         | `-d "username=xx&password=yy"` |
| `-X`         | Request method 지정 (GET/POST/PUT 등)      | POST 요청을 명시적으로 만들 때           | `-X POST` |
| `--data-raw` | 원본 문자열 그대로 body로 전송             | 복잡한 페이로드 테스트할 때 유용         | `--data-raw '...' ` |

**PowerShell 팁**: 긴 명령어는 백틱(`)으로 줄바꿈할 수 있습니다. (위 예시 참조)

## 힌트

- Windows에서 그냥 `curl` 이라고 치면 PowerShell의 `Invoke-WebRequest` 별칭이 실행됩니다. **반드시 `curl.exe`** 라고 써야 진짜 curl이 나옵니다.
- `-v` 를 자주 쓰세요. 처음에는 정보가 많아 보이지만, 이게 바로 "무슨 일이 일어나고 있는지"를 알려주는 최고의 친구입니다.
- Set-Cookie 헤더를 보면서 쿠키가 언제, 어떤 값으로 발급되는지 관찰하세요.

## 자가 점검

- [ ] `-v` 와 `-i` 의 차이를 설명할 수 있는가?
- [ ] `-b "session_user=admin"` 이 정확히 어떤 HTTP 요청을 만드는지 설명할 수 있는가?
- [ ] Console fetch에서 `credentials: "include"` 를 빼면 쿠키가 왜 안 따라가는가?

## 자가 점검

- [ ] Burp 없이도 HTTP를 내 손으로 만들 수 있는가?
- [ ] 쿠키 값을 직접 바꿔서 다른 사용자로 위장할 수 있는가?

---

**다음 문제**: 03-Burp-Repeater-마스터

이 근육이 없으면 Burp를 배워도 "그냥 편한 도구"로만 보입니다.