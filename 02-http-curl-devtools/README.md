# 02-http-curl-devtools : HTTP 기초 정복 — 브라우저 개발자도구 + curl로 직접 보내고 받기

**이 챕터의 철학**  
Burp Suite는 강력한 도구지만, **처음부터 Burp에 의존하면 HTTP의 본질을 제대로 느끼지 못한다**.  
이 섹션은 **"직접 손으로 HTTP 요청을 만들고, 응답을 해석하는"** 근육을 만드는 데 집중합니다.

Burp를 나중에 배우면 "아, 이게 왜 이렇게 편한 건지"가 제대로 이해됩니다.

## 학습 목표

- 브라우저 개발자도구(Network 탭)의 기본 사용법 익히기
- "Copy as cURL" 기능을 자유자재로 사용하기
- Windows PowerShell에서 `curl.exe` 기본 명령어 마스터
- GET/POST, 쿼리 파라미터, 폼 데이터, 헤더, 쿠키를 **직접 타이핑**해서 보내기
- 응답 상태 코드, 헤더, 본문을 curl로 확인하는 방법
- 수동으로 쿠키를 조작해서 세션 하이재킹 맛보기 (Burp Repeater 없이)

---

## 0. 사전 준비 (Windows)

### 1. curl.exe 확인

PowerShell을 **관리자 권한이 아닌 일반**으로 열고 실행:

```powershell
curl.exe --version
```

정상적으로 버전이 나오면 OK. (Windows 10 17063 이상, Windows 11 대부분 내장)

**주의**: PowerShell에서 `curl` 만 치면 `Invoke-WebRequest`의 별칭이 실행됩니다.  
**항상 `curl.exe`** 라고 써야 진짜 curl을 사용합니다.

### 2. 브라우저 개발자도구 단축키

- Chrome / Edge: `F12` 또는 `Ctrl + Shift + I`
- Firefox: `F12` 또는 `Ctrl + Shift + I`

주로 사용할 탭: **Network** (네트워크)

---

## 1. 앱 실행

```powershell
cd 02-http-curl-devtools
python app.py
```

브라우저에서 **http://127.0.0.1:5003** 열기

이 페이지 자체가 curl 실습 가이드입니다. Burp는 아직 켜지 마세요.

---

## 2. 단계별 실습 (이 순서대로 진행하세요)

### 실습 A: DevTools로 GET 요청 관찰 + Copy as cURL (가장 중요)

1. 메인 페이지에서 `user=chulsu` 로 "회원 정보 보기" 폼 제출
2. `F12` → **Network** 탭 선택
3. 왼쪽 목록에서 `profile?user=chulsu` 요청을 찾음 (필터에 `profile` 입력하면 편함)
4. 해당 요청을 **우클릭** → **Copy** → **Copy as cURL (cmd)** 선택
5. PowerShell에 붙여넣고 실행해보기

성공했다면 브라우저에서 본 것과 **완전히 같은 결과**가 터미널에 나와야 합니다.

**다음 단계**:
- 붙여넣은 명령어에서 `user=chulsu` 를 `user=sumi` 로 바꿔서 실행
- `user=admin` 으로 바꿔서 실행 → 관리자 정보가 나오는가?

이게 바로 **파라미터 변조**의 가장 원초적인 형태입니다.

### 실습 B: Verbose와 응답 헤더 보기

```powershell
# 상세 정보 전체 보기 (요청 + 응답 헤더 + TLS 정보 등)
curl.exe "http://127.0.0.1:5003/profile?user=sumi" -v

# 응답 헤더 + 본문 함께 보기 (상태 코드 확인에 좋음)
curl.exe "http://127.0.0.1:5003/profile?user=sumi" -i
```

`-v` (verbose)는 웹 해킹에서 가장 자주 쓰는 옵션 중 하나입니다.  
TLS handshake, 실제로 서버가 받은 Host, User-Agent 등을 모두 보여줍니다.

### 실습 C: POST 요청을 curl로 직접 작성하기

1. 메인 페이지의 로그인 폼을 한 번 브라우저로 전송 (chulsu / test123)
2. Network 탭에서 `login` POST 요청 찾기
3. 우클릭 → Copy as cURL (cmd)
4. PowerShell에 붙여넣기

직접 작성하는 연습도 해보세요:

```powershell
curl.exe "http://127.0.0.1:5003/login" `
    -X POST `
    -H "Content-Type: application/x-www-form-urlencoded" `
    -d "username=chulsu&password=test123" `
    -i
```

**PowerShell 줄바꿈 팁**: 백틱(`) 문자로 줄을 이어서 씁니다.  
한 줄로 다 써도 됩니다:

```powershell
curl.exe "http://127.0.0.1:5003/login" -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "username=chulsu&password=test123" -i
```

### 실습 D: 로그인 후 쿠키를 curl로 다루기 (핵심 실습)

로그인에 성공하면 서버는 응답에 `Set-Cookie: session_user=chulsu; HttpOnly` 를 내려줍니다.

#### 방법 1: 쿠키 파일로 저장/재사용 (가장 실전적)

```powershell
# 로그인하면서 쿠키를 cookies.txt 파일로 저장
curl.exe "http://127.0.0.1:5003/login" -X POST -d "username=chulsu&password=test123" -c cookies.txt -i

# 저장된 쿠키를 사용해서 내 정보 페이지 접근
curl.exe "http://127.0.0.1:5003/myinfo" -b cookies.txt -i
```

#### 방법 2: 쿠키 값을 직접 지정 (수동 세션 하이재킹)

```powershell
# 쿠키 값을 admin으로 직접 넣어서 요청
curl.exe "http://127.0.0.1:5003/myinfo" -b "session_user=admin" -i
```

**성공 기준**: `관리자 권한!` 문구가 응답에 나타나면 성공.

이게 바로 나중에 세션 하이재킹, IDOR 등으로 발전하는 **쿠키 조작**의 가장 원초적인 형태입니다.

### 실습 E: /debug/echo 로 모든 것을 관찰하기 (curl의 최고 친구)

이 앱에서 가장 중요한 디버그 엔드포인트입니다.

```powershell
# 기본
curl.exe "http://127.0.0.1:5003/debug/echo" -v

# 쿼리 파라미터 + 커스텀 헤더 + 바디 모두 보내고 확인
curl.exe "http://127.0.0.1:5003/debug/echo?test=hello&role=hacker" `
    -H "X-Custom-Header: my-value-123" `
    -H "Referer: https://evil.com" `
    -H "User-Agent: HackingStudy/1.0" `
    -d "formfield1=aaa&formfield2=bbb" `
    -i
```

`/debug/echo` 는 받은 모든 것을 JSON(또는 pretty print)으로 돌려줍니다.  
"내가 보낸 게 서버에 어떻게 도착했는가?" 를 정확히 확인할 수 있어 실습에 최적입니다.

---

## 2.5 (추가) 개발자도구 Console에서 fetch()로 로그인하기

curl로 충분히 익혔다면, 이제 **브라우저 안에서** JavaScript로 같은 일을 해봅시다.

이건 실제 웹사이트를 해킹할 때도 매우 유용한 기술입니다 (XSS 후 JS로 요청 보내기, 또는 빠른 실험).

### 준비
1. http://127.0.0.1:5003 페이지 열기
2. `F12` → **Console** 탭 선택 (Network 탭도 같이 열어두는 걸 추천)
3. 아래 코드를 복사해서 Console에 붙여넣고 Enter

### 기본 로그인 (chulsu)

```js
fetch("http://127.0.0.1:5003/login", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({ username: "chulsu", password: "test123" }),
  credentials: "include"   // ← 이게 핵심! 쿠키 주고받기
})
.then(r => { console.log("상태:", r.status); return r.text(); })
.then(t => console.log("응답 미리보기:", t.substring(0,400)));
```

### 로그인 후 보호된 페이지 확인

```js
fetch("http://127.0.0.1:5003/myinfo", { credentials: "include" })
  .then(r => r.text())
  .then(console.log);
```

성공하면 철수의 정보가 콘솔에 출력됩니다.

### admin으로 바로 로그인 + 확인 (체인)

```js
fetch("/login", {
  method: "POST",
  headers: {"Content-Type": "application/x-www-form-urlencoded"},
  body: "username=admin&password=test123",
  credentials: "include"
})
.then(() => fetch("/myinfo", {credentials:"include"}))
.then(r => r.text())
.then(console.log);
```

이걸 실행한 뒤 브라우저 주소창에 `/myinfo` 직접 가거나 새로고침 해보면, 이미 로그인되어 있는 상태일 겁니다!

### /debug/echo 를 Console에서 JSON으로 보기 (강추)

```js
fetch("/debug/echo?format=json", {credentials: "include"})
  .then(r => r.json())
  .then(console.log);
```

### 편하게 쓰고 싶을 때 (한 번만 붙여넣기)

```js
async function login(user, pw) {
  const r = await fetch("/login", {
    method:"POST",
    headers:{"Content-Type":"application/x-www-form-urlencoded"},
    body: new URLSearchParams({username:user, password:pw}),
    credentials:"include"
  });
  console.log("login status:", r.status);
}
async function myinfo() {
  const r = await fetch("/myinfo", {credentials:"include"});
  console.log(await r.text());
}
```

이제 콘솔에서 `login("chulsu", "test123")` , `myinfo()` 만 치면 됩니다.

### 로그아웃 연습 (중요!)
사이트에 **로그아웃** 기능이 추가되었습니다 (`/logout`).

```js
// Console에서 로그아웃
fetch("/logout", { method: "POST", credentials: "include" })
  .then(() => location.reload());

// curl
curl.exe "http://127.0.0.1:5003/logout" -b cookies.txt -c cookies.txt -i
```

로그아웃 후 다시 `/myinfo`를 fetch 해보면 쿠키가 사라져서 "로그인 필요" 메시지가 나와야 합니다.

### 관찰 포인트
- Console에서 fetch를 날리는 동안 **Network 탭**을 보면 요청이 실시간으로 잡힙니다.
- Payload 탭에서 body가 어떻게 갔는지, Response 탭에서 HTML이 어떻게 왔는지 볼 수 있어요.
- 이 과정이 Burp Proxy/Repeater와 매우 비슷한 경험을 줍니다.

이제 "브라우저 콘솔에서도 curl처럼 마음대로 요청을 조작할 수 있다"는 걸 몸으로 느꼈을 거예요.

### 2.6 요청 가로채기(Intercept)와 하이재킹 (가장 중요 실습)

이 섹션에서 **"직접 작성"에서 "브라우저가 보낸 요청을 가로채서 수정"**으로 넘어갑니다.

사이트 메인 페이지 하단에 **"6. 요청 가로채기 & 하이재킹"** 카드가 있습니다. 여기서 다음을 배웁니다:

**초보자가 자주 겪는 문제와 해결**
- 전통 form submit (회원정보 보기, 로그인 폼)은 전체 페이지 이동이라 **Fetch/XHR 필터에 안 뜹니다** (`sec-fetch-mode: navigate`).
- 해결: Network 상단에서 **Fetch/XHR 필터를 끄거나**, 페이지에 추가한 **전용 연습 버튼** ("회원정보 fetch 요청 보내기", "로그인 fetch 요청")을 사용하세요.
- 이 버튼들은 실제 `fetch()`로 요청을 보내서 **Fetch/XHR에 깔끔하게** 나타납니다.

**가로채기 워크플로**
1. 위 버튼 클릭 (또는 일반 동작)
2. Network 탭 → Fetch/XHR 필터 ON
3. 요청 우클릭 → **Copy → Copy as fetch**
4. Console에 붙여넣기
5. 코드 수정 (예: `user=chulsu` → `user=admin`, 또는 Cookie 헤더 강제 주입)
6. 실행해서 결과 확인

**하이재킹 실습**
- 로그인 응답 Headers에서 `Set-Cookie` 값 복사
- 새 컨텍스트(시크릿)에서 `fetch("/myinfo", { credentials:"include", headers: { "Cookie": "session_user=xxx" } })` 로 강제 요청
- `session_user=admin` 넣으면 관리자 정보가 나오는 걸 직접 확인

이 모든 것이 Burp 없이 **순수 DevTools + Console**로 가능하다는 걸 체감하는 단계입니다.

자세한 스크린샷 스타일 가이드와 버튼은 페이지의 "6. 요청 가로채기 & 하이재킹" 섹션에 그대로 들어가 있습니다. 따라 하기만 하면 됩니다.

이 실습을 마치면 자연스럽게 "이제 모든 트래픽을 더 편하게 가로채고 싶다"는 생각이 듭니다. 그때 `02-http-burp`로 넘어가면 Burp의 가치가 제대로 느껴집니다.

---

## 3. 자주 쓰는 curl 옵션 정리 (외우기)

| 옵션          | 의미                              | 예시                              | 언제 쓰나                     |
|---------------|-----------------------------------|-----------------------------------|-------------------------------|
| `-v`          | verbose (상세)                    | `curl.exe ... -v`                 | 거의 항상 켜는 걸 추천        |
| `-i`          | response header 포함 출력         | `curl.exe ... -i`                 | 상태 코드, Set-Cookie 확인    |
| `-X POST`     | 메서드 지정                       | `curl.exe ... -X POST`            | POST, PUT, DELETE 등          |
| `-H "Name: val"` | 커스텀 헤더 추가               | `-H "X-Forwarded-For: 127.0.0.1"` | 대부분의 헤더 조작            |
| `-d "a=b&c=d"` | POST body (form)                 | `-d "username=admin&pass=123"`    | 로그인, 폼 전송               |
| `-b "k=v"`    | 쿠키 전달 (직접)                  | `-b "session_user=admin"`         | 세션 유지, 하이재킹           |
| `-b cookies.txt` | 쿠키 파일에서 읽기             | `-b cookies.txt`                  | 실제 브라우저처럼 쿠키 재사용 |
| `-c cookies.txt` | 응답 쿠키를 파일에 저장         | `-c cookies.txt`                  | 로그인 후 쿠키 보관           |
| `-o file.html` | 응답을 파일로 저장                | `-o out.html`                     | 큰 응답이나 HTML 분석할 때    |

추가 팁:
- `-L` : 리다이렉트 따라가기
- `--data-raw '...' ` : `-d` 와 비슷하지만 `@` 같은 특수문자 처리에 유리할 때
- 여러 `-H` 는 계속 붙여서 사용 가능

---

## 4. PowerShell에서 자주 만나는 함정

1. `curl` 대신 `curl.exe` 쓰기
2. 따옴표: PowerShell에서는 큰따옴표(`"`)와 작은따옴표(`'`) 동작이 다를 수 있음. URL이나 값에 공백/특수문자가 있으면 큰따옴표로 감싸는 걸 기본으로.
3. 줄바꿈: 백틱(`) 사용 (또는 한 줄로 쓰기)
4. `&` 문자가 들어간 데이터: PowerShell에서 `&` 는 명령 체인으로 해석될 수 있으니 `-d` 값은 되도록 따옴표로 감싸기

예시 (안전하게):

```powershell
curl.exe "http://127.0.0.1:5003/login" -X POST -d "username=chulsu&password=test123" -i
```

---

## 5. 실습 미션 (체크리스트)

- [ ] DevTools에서 Copy as cURL (cmd) 로 GET 요청을 5번 이상 재현했다
- [ ] `user=chulsu`, `user=sumi`, `user=admin` 을 curl로 직접 바꿔가며 정보 탈취
- [ ] 로그인 POST를 curl로 직접 작성해서 성공시켰다 (`-i` 로 Set-Cookie 확인)
- [ ] `-c cookies.txt` 로 쿠키 저장 → `-b cookies.txt` 로 /myinfo 접근
- [ ] `-b "session_user=admin"` 로 직접 쿠키 값을 조작해서 관리자 정보 획득
- [ ] `/debug/echo` 에 커스텀 헤더 3개 이상 + body를 보내고, 서버가 정확히 받은 내용인지 확인
- [ ] `-v` 옵션으로 User-Agent, Host, Accept 등 기본 헤더가 어떻게 가는지 관찰
- [ ] 응답의 HTTP 상태 코드 (200, 302 등)를 `-i` 로 직접 확인

이 미션들을 **Burp 없이** 끝냈다면, HTTP에 대한 기초 체력이 상당히 붙은 상태입니다.

---

## 6. 다음 단계

이 실습을 끝냈다면:

- "HTTP 요청은 브라우저가 자동으로 만들어주는 게 아니라, 내가 직접 만들 수 있는 것이다" 라는 감이 생겨야 함
- 이제 **02-http-burp** (또는 기존 02-http-burp 폴더) 로 넘어가서 Burp Suite의 진가를 느껴보세요.
  - Burp는 "이 모든 과정을 자동으로 가로채고, 쉽게 수정하고, 반복 전송" 해주는 도구입니다.
  - curl로 고생하면서 했던 작업들이 Burp Repeater 하나면 순식간에 됩니다.

---

## 자가 점검

1. `curl.exe "..." -b "session_user=xxx"` 와 브라우저에서 쿠키를 설정하는 것의 가장 큰 차이점은?
2. `-v` 옵션 없이도 Set-Cookie 헤더를 확인할 수 있는 옵션은?
3. PowerShell에서 `curl` 과 `curl.exe` 의 차이를 설명할 수 있는가?
4. `/debug/echo` 같은 엔드포인트가 왜 웹 해킹 학습에 유용한가?
5. "Copy as cURL" 기능을 쓰지 않고, 처음부터 직접 curl 명령어를 작성할 수 있는가?

---

**준비되면 말해 주세요**:

- "02-http-curl-devtools 끝냈어"
- "쿠키 조작 미션이 안 돼"
- "다음으로 Burp로 넘어가자"

그러면 다음 단계로 안내해드리겠습니다.

이제 진짜 HTTP를 **손으로** 느껴봅시다.
