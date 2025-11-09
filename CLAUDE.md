# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

네이버 블로그 자동 댓글 작성 봇입니다. Selenium을 사용하여 웹 브라우저를 제어하고, OpenAI GPT-4o-mini API를 활용하여 자연스러운 댓글을 생성합니다.

**주요 기술 스택**:
- Python 3.10
- Selenium (웹 자동화)
- OpenAI API (댓글 생성)
- BeautifulSoup4 (HTML 파싱)

**핵심 목적**:
- 최근 댓글 작성자의 블로그 글에 자동으로 댓글 등록
- 서로이웃의 최근 게시글에 자동으로 댓글 등록

## 필수 개발 명령어

```bash
# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 프로그램 실행
python main.py

# VSCode에서 디버그 실행
# F5 키 또는 "Python: main.py 실행" 구성 사용
```

## 환경 설정 요구사항

프로젝트 실행 전 필수 설정:

1. **환경 변수**: `.env` 파일에 `OPENAI_API_KEY` 필요
2. **Chrome WebDriver**: 사용자 데이터 경로 `C:\chrome-driver\chrome-user-data` 필요
3. **로그 디렉토리**: `C:\logs` 디렉토리 생성 (로그 파일: `app.log`)

## 아키텍처 및 데이터 흐름

### 전체 구조

```
main.py (진입점)
  └─> CommentProcessor (핵심 비즈니스 로직)
        ├─> CommentScraper (최근 댓글 작성자 수집)
        ├─> BuddyScraper (서로이웃 최근 게시자 수집)
        ├─> BlogScraper (블로그 제목/본문 추출)
        ├─> OpenAI API (댓글 생성)
        ├─> CommentWriter (공감 버튼 클릭 + 댓글 작성)
        └─> DriverManager (WebDriver 관리)
```

### 데이터 흐름

1. **수집 단계**: CommentScraper 또는 BuddyScraper가 타겟 블로그 ID 수집
2. **크롤링 단계**: BlogScraper가 블로그 제목/본문 추출 및 정제
3. **생성 단계**: OpenAI API로 자연스러운 댓글 생성
4. **작성 단계**: CommentWriter가 공감 버튼 클릭 후 댓글 작성
5. **로깅 단계**: 모든 활동 로그 기록 (`C:\logs\app.log`)

## 주요 파일 및 역할

### 루트 디렉토리

- [main.py](main.py): 프로그램 진입점, DriverManager 초기화 및 예외 처리
- [comment_process.py](comment_process.py): 핵심 비즈니스 로직, 댓글 작성 프로세스 조율
- [requirements.txt](requirements.txt): 36개 의존성 패키지 정의

### driver/ - WebDriver 관리

- [driver/driver_manager.py](driver/driver_manager.py): Chrome WebDriver 생성, 관리, 재시작
- [driver/base_driver.py](driver/base_driver.py): 모든 Scraper의 기본 클래스, URL 이동 및 랜덤 대기

### naver/ - 네이버 블로그 특화 모듈

- [naver/blog_scraper.py](naver/blog_scraper.py): 블로그 게시글 제목/본문 추출, HTML 파싱, 텍스트 정제
- [naver/comment_scraper.py](naver/comment_scraper.py): 내 블로그의 최근 댓글 작성자 ID 수집
- [naver/buddy_scraper.py](naver/buddy_scraper.py): 서로이웃 중 최근 게시글 작성자 ID 수집
- [naver/comment_writer.py](naver/comment_writer.py): 공감 버튼 클릭 및 댓글 작성, 댓글 수 제한 확인

### api/ - OpenAI API 통합

- [api/generate_comment.py](api/generate_comment.py): GPT-4o-mini를 사용한 댓글 생성, 프롬프트 관리

### common/ - 공통 유틸리티

- [common/constants.py](common/constants.py): 블로그 ID, 제외 대상 목록, 상수 정의
- [common/time_utils.py](common/time_utils.py): 랜덤 대기 함수 (1-3초)
- [common/log_utils.py](common/log_utils.py): 로깅 설정 (파일 + 콘솔)

## 프로젝트 특화 규칙

### 안전 장치

- **댓글 수 제한**: 100개 이하 게시글만 댓글 작성 ([naver/comment_writer.py](naver/comment_writer.py))
- **공감 버튼 우선**: 공감 버튼 미클릭 시 댓글 작성 제외
- **토큰 제한**: 본문 토큰 수 300개 미만 시 제외 ([api/generate_comment.py](api/generate_comment.py))
- **Alert 제한**: Alert 5회 이상 시 자동 중단 ([comment_process.py](comment_process.py))
- **API Rate Limit 처리**: OpenAI API Rate Limit 초과 시 즉시 프로그램 중단 ([comment_process.py](comment_process.py))

### 제외 대상 관리 ([common/constants.py](common/constants.py))

- `MY_BLOG_ID`: 자기 블로그 제외
- `EXCLUSION_LIST`: 30개 특정 블로그 ID 제외
- 새로운 제외 대상 추가 시 `EXCLUSION_LIST`에 블로그 ID 추가

## 중요한 비즈니스 로직

### 1. 최근 댓글 작성자 처리 ([comment_process.py](comment_process.py))

최근 댓글 작성자 수집한 후, 각 블로그를 방문하여 제목/본문을 추출하고 댓글을 생성하여 작성합니다.

### 2. 서로이웃 최근 게시자 처리 ([comment_process.py](comment_process.py))

서로이웃 중 최근 게시자 수집하고, 이미 처리한 ID를 제외한 후 동일한 댓글 작성 프로세스를 반복합니다.

### 3. 공감 버튼 + 댓글 작성 순서 ([naver/comment_writer.py](naver/comment_writer.py))

**중요**: 반드시 공감 버튼을 먼저 클릭한 후 댓글을 작성해야 합니다. 순서: 공감 버튼 클릭 → 댓글 입력 → 등록 버튼 클릭

### 4. 예외 처리 전략

- **NoSuchElementException**: 로그만 기록하고 계속 진행 (흔한 예외)
- **네이버 댓글 제한 Alert**: 즉시 중단 (하루 댓글 제한 도달)
- **Alert 5회 이상**: 자동 중단 (비정상 상태)
- **OpenAI RateLimitError**: 즉시 중단 (API 요금 한도 초과 또는 요청 제한)
  - 예외 발생 시 에러 로그 기록
  - WebDriver 종료
  - 프로그램 즉시 중단 (`sys.exit()`)

## Windows 특화 사항

이 프로젝트는 Windows 환경에 최적화되어 있습니다:

- Chrome 드라이버 경로: `C:\chrome-driver\chrome-user-data` ([driver/driver_manager.py](driver/driver_manager.py))
- 로그 파일 경로: `C:\logs\app.log` ([common/log_utils.py](common/log_utils.py))
- 가상환경 활성화: `.venv\Scripts\activate` (Windows 전용)

다른 OS에서 실행 시 경로 수정 필요합니다.

## 개발 가이드라인

### 코딩 스타일

- **코드 포맷터**: 이 프로젝트는 **Black** 포맷터를 사용합니다. 모든 Python 코드는 Black 스타일 가이드를 따라 작성되어야 합니다. **별도로 `black` 명령어를 실행하지 마세요**
- **이모지 사용 금지**: 코드, 주석, 로그 메시지 등 모든 곳에서 이모지 사용을 피하세요
- **주석 작성 규칙**:
  - 복잡한 로직은 넘버링 주석으로 단계별 설명 (여러 단계의 처리 흐름이 있을 경우)
  - 코드 수정 시 관련 주석도 함께 업데이트하여 불일치 방지
  - 구체적 수치 대신 일반적 표현 사용 (예: "5회 이상" → "임계값 초과 시")
- **로깅 정책**: logger는 **info, error, warning** 세 가지 레벨만 사용합니다

### 수정 제한 파일

- **[api/generate_comment.py](api/generate_comment.py)**: 이 파일은 별도 명령이 있을 때까지 임의로 수정하지 마세요. 댓글 생성 로직과 프롬프트가 최적화되어 있습니다.

## 코드 수정 시 주의사항

### 1. 크롤링 로직 변경 시

네이버 블로그 UI가 자주 변경되므로 CSS 선택자나 XPath 수정이 필요할 수 있습니다.

### 2. 상수 변경 시

주요 상수는 [common/constants.py](common/constants.py)에서 관리합니다:
- 최근 댓글 작성자 수집 개수
- 서로이웃 최근 게시자 수집 개수
- 댓글 수 제한

## 보안 주의사항

- **API 키 관리**: `.env` 파일에 `OPENAI_API_KEY` 저장 (절대 커밋 금지)
- **로그 파일**: API 사용량이 기록되므로 로그 파일 노출 주의
- **GitHub PAT**: Git remote에 PAT이 하드코딩되어 있으므로 주의 필요
