# Python DevKnife Toolkit

Python으로 구현된 일상적인 개발자 유틸리티를 통합한 올인원 터미널 툴킷입니다.

## 기능

- **인코딩/디코딩**: Base64, URL 인코딩 등
- **데이터 형식 처리**: JSON, XML, YAML 포맷팅 및 변환
- **데이터 변환**: CSV/TSV를 Markdown으로 변환
- **개발자 도구**: UUID 생성, IBAN 검증, 패스워드 생성
- **수학적 변환**: 진법 변환, 해시 생성, 타임스탬프 변환
- **웹 개발 도구**: GraphQL 포맷팅, CSS 처리, URL 추출

## 인터페이스

- **CLI**: 명령줄에서 직접 실행
- **TUI**: 대화형 터미널 인터페이스

## 설치

```bash
pip install python-devknife-toolkit
```

## 사용법

### 설치 후 개발 모드로 실행
```bash
# 현재 개발 중인 버전을 설치
pip install -e .

# 사용 가능한 명령어 확인
devknife --help
devknife list-commands
```

### 인코딩/디코딩 유틸리티

#### Base64 인코딩/디코딩
```bash
# Base64 인코딩
devknife base64 'Hello World!'
# 출력: SGVsbG8gV29ybGQh

# Base64 디코딩
devknife base64 --decode 'SGVsbG8gV29ybGQh'
# 출력: Hello World!

# 파이프를 통한 입력
echo 'Hello World!' | devknife base64

# 파일에서 읽기
devknife base64 --file input.txt

# 도움말
devknife base64 --help
```

#### URL 인코딩/디코딩
```bash
# URL 인코딩
devknife url 'Hello World! @#$%'
# 출력: Hello%20World%21%20%40%23%24%25

# URL 디코딩
devknife url --decode 'Hello%20World%21%20%40%23%24%25'
# 출력: Hello World! @#$%

# 파이프를 통한 입력
echo 'Hello World! @#$%' | devknife url

# 파일에서 읽기
devknife url --file input.txt

# 도움말
devknife url --help
```

### 💡 사용 팁

#### 따옴표 사용법
```bash
# ✅ 권장: 단일 따옴표 사용
devknife base64 'Hello World!'
echo 'Hello World!' | devknife base64

# ❌ 피하기: 이중 따옴표는 쉘에서 문제를 일으킬 수 있음
devknife base64 "Hello World!"  # 문제 발생 가능
```

#### 다양한 입력 방법
```bash
# 1. 직접 인수로 전달
devknife base64 '텍스트'

# 2. 파이프를 통한 전달
echo '텍스트' | devknife base64

# 3. 파일에서 읽기
devknife base64 --file filename.txt

# 4. 표준 입력에서 읽기 (대화형)
devknife base64  # 엔터 후 텍스트 입력
```

### TUI 모드 (개발 예정)
```bash
# 대화형 터미널 인터페이스 시작
devknife
```

### 현재 구현된 기능
- ✅ Base64 인코딩/디코딩
- ✅ URL 인코딩/디코딩
- 🚧 JSON/XML/YAML 처리 (개발 중)
- 🚧 CSV/TSV 변환 (개발 중)
- 🚧 개발자 도구 (개발 중)
- 🚧 수학적 변환 (개발 중)
- 🚧 웹 개발 도구 (개발 중)

## 실제 사용 예시

### Base64 인코딩/디코딩 예시
```bash
# 간단한 텍스트 인코딩
$ devknife base64 'Hello DevKnife!'
SGVsbG8gRGV2S25pZmUh

# 디코딩해서 원본 확인
$ devknife base64 --decode 'SGVsbG8gRGV2S25pZmUh'
Hello DevKnife!

# 특수문자가 포함된 텍스트
$ devknife base64 '안녕하세요! 🚀'
7JWI64WV7ZWY7IS47JqUISAg8J+agA==

# 파일 내용 인코딩
$ echo 'This is a secret message' > secret.txt
$ devknife base64 --file secret.txt
VGhpcyBpcyBhIHNlY3JldCBtZXNzYWdl
```

### URL 인코딩/디코딩 예시
```bash
# 공백과 특수문자가 있는 URL 인코딩
$ devknife url 'Hello World! How are you?'
Hello%20World%21%20How%20are%20you%3F

# 한글 URL 인코딩
$ devknife url '안녕하세요 개발자님!'
%EC%95%88%EB%85%95%ED%95%98%EC%84%B8%EC%9A%94%20%EA%B0%9C%EB%B0%9C%EC%9E%90%EB%8B%98%21

# URL 디코딩
$ devknife url --decode 'Hello%20World%21%20How%20are%20you%3F'
Hello World! How are you?

# 복잡한 쿼리 스트링 처리
$ devknife url 'name=John Doe&email=john@example.com&message=Hello there!'
name%3DJohn%20Doe%26email%3Djohn%40example.com%26message%3DHello%20there%21
```

### 파이프라인 활용 예시
```bash
# 여러 명령어 조합
$ echo 'Hello World!' | devknife base64 | devknife base64 --decode
Hello World!

# 파일 처리 파이프라인
$ cat data.txt | devknife url | tee encoded.txt
$ cat encoded.txt | devknife url --decode
```

## 문제 해결

### 자주 발생하는 문제

#### `dquote>` 프롬프트가 나타날 때
```bash
# 문제: 이중 따옴표 사용으로 인한 쉘 파싱 오류
$ devknife base64 "Hello World!"
dquote>

# 해결: Ctrl+C로 취소 후 단일 따옴표 사용
$ devknife base64 'Hello World!'
SGVsbG8gV29ybGQh
```

#### 한글이나 특수문자 처리
```bash
# UTF-8 인코딩이 제대로 처리됨
$ devknife base64 '한글 테스트 🎉'
7ZWc6riAIO2FjOyKpO2KuCDwn46J

$ devknife base64 --decode '7ZWc6riAIO2FjOyKpO2KuCDwn46J'
한글 테스트 🎉
```

#### 긴 텍스트나 파일 처리
```bash
# 큰 파일은 --file 옵션 사용 권장
$ devknife base64 --file large_file.txt

# 또는 파이프 사용
$ cat large_file.txt | devknife base64
```

### 오류 메시지 해석

#### Base64 디코딩 오류
```bash
$ devknife base64 --decode 'invalid base64!'
오류: Invalid Base64 format. Base64 strings should only contain A-Z, a-z, 0-9, +, /, and = for padding.
```

#### 입력 없음 오류
```bash
$ devknife base64
오류: 입력 텍스트가 필요합니다. --help를 참조하세요.
```

## 개발

```bash
# 개발 환경 설정
pip install -e ".[dev]"

# 테스트 실행
pytest

# 코드 포맷팅
black .

# 타입 체크
mypy devknife
```

## 라이선스

MIT License