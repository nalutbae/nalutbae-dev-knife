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

### CLI 모드
```bash
devknife base64 "Hello World"
devknife json-format '{"name":"test"}'
```

### TUI 모드
```bash
devknife
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