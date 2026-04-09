# 디자인 패턴 PoC 어플리케이션 — Application Spec

> 최종 업데이트: 2026-04-09 | **V1 완료** / 다음: V2

---

## 1. 기술 스택

| 영역 | 기술 | 비고 |
|------|------|------|
| 백엔드 | Python 3.11+ / FastAPI | 경량 REST API 서버 |
| 프론트엔드 | HTML5 / Vanilla JS / CSS3 | 빌드 도구 없음, 순수 정적 파일 |
| 코드 하이라이팅 | highlight.js 11.9 (CDN) | Java 구문 강조 |
| AI (기능 2 / V3) | Anthropic Claude (claude-sonnet-4-6) | 파일 분석 및 패키지 구조 생성 |
| 환경 변수 | python-dotenv / `.env` | API Key 관리 |

> **기능 1은 AI를 사용하지 않습니다.** GoF 23개 패턴 예제는 `data/patterns_static.py`에 사전 작성된 정적 데이터로 제공됩니다.

---

## 2. 프로젝트 구조

```
pocPattern/
├── backend/
│   ├── main.py                        # FastAPI 앱 진입점, 정적 파일 서빙
│   ├── requirements.txt
│   ├── routers/
│   │   ├── __init__.py
│   │   └── patterns.py                # 패턴 목록 / 예제 조회 API (기능 1)
│   ├── services/
│   │   ├── __init__.py
│   │   └── llm_service.py             # Anthropic Claude API 연동 (기능 2 / V3 예정)
│   └── data/
│       ├── __init__.py
│       └── patterns_static.py         # GoF 23개 패턴 정적 데이터 (Java Spring Boot 예제)
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── .env                               # API Key (git 제외 대상)
├── .env.example                       # API Key 템플릿
├── 요구사항.md
└── 어플리케이션 spec.md

※ 분석용 기준 파일 (기능 2 / V3 입력 데이터)
   functionAnaylyzeCheck.csv
   functionAnaylyzeProvision.csv
   functionAnaylyzeSave.csv
```

---

## 3. API 명세

### Base URL
```
http://localhost:8000
```

---

### 3.1 패턴 목록 조회

```
GET /api/patterns
```

**Response**
```json
{
  "patterns": {
    "creational": [
      { "name": "Singleton", "name_ko": "싱글턴", "available": true },
      { "name": "Factory Method", "name_ko": "팩토리 메서드", "available": true }
    ],
    "structural": [ "..." ],
    "behavioral": [ "..." ]
  }
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| name | string | 패턴 영문명 |
| name_ko | string | 패턴 한국어명 |
| available | boolean | 정적 데이터 탑재 여부 (현재 23개 전체 true) |

---

### 3.2 패턴 예제 조회

```
POST /api/patterns/example
Content-Type: application/json
```

**Request Body**
```json
{
  "pattern_name": "Singleton"
}
```

**Response (성공)**
```json
{
  "pattern_name": "Singleton",
  "category": "creational",
  "overview": "...",
  "use_case": "...",
  "layers_used": ["domain", "infra"],
  "example_code": "// ===== [domain/ApplicationConfigManager.java] =====\n...",
  "package_structure": "com.example.singleton\n├── domain\n│   └── ...",
  "key_benefits": ["이점1", "이점2", "이점3"]
}
```

**Response 필드**

| 필드 | 타입 | 설명 |
|------|------|------|
| pattern_name | string | 패턴 영문명 |
| category | string | creational / structural / behavioral |
| overview | string | 패턴 개요 (한국어) |
| use_case | string | Spring Boot 활용 시나리오 (한국어) |
| layers_used | array | 해당 패턴에 사용된 레이어 목록 |
| example_code | string | Java Spring Boot 전체 코드 (클래스 구분자 포함) |
| package_structure | string | ASCII 디렉토리 트리 문자열 |
| key_benefits | array | 핵심 이점 목록 (한국어) |

**Error Response**
```json
{
  "detail": "패턴 'XXX'을 찾을 수 없습니다. GoF 23개 패턴만 지원합니다."
}
```

| HTTP 상태 | 사유 |
|-----------|------|
| 200 | 정상 |
| 404 | 지원하지 않는 패턴명 또는 데이터 미탑재 |

---

## 4. 정적 데이터 구조

### data/patterns_static.py

GoF 23개 패턴 전체를 Python 딕셔너리로 사전 작성하여 관리합니다.

```python
PATTERNS_DATA = {
    "Singleton": {
        "pattern_name": "Singleton",
        "category": "creational",
        "overview": "한국어 설명",
        "use_case": "한국어 활용 시나리오",
        "layers_used": ["domain", "infra"],
        "example_code": "// ===== [domain/클래스명.java] =====\n...",
        "package_structure": "ASCII 트리 구조",
        "key_benefits": ["이점1", "이점2", "이점3"]
    },
    "Factory Method": { "..." },
    # ... GoF 23개 전체
}
```

| 항목 | 내용 |
|------|------|
| 위치 | `backend/data/patterns_static.py` |
| 관리 방식 | Python 소스 코드 직접 수정 |
| AI 의존성 | 없음 (완전 정적) |
| 패턴 수 | 23개 (GoF 전체) |

---

## 5. 레이어 아키텍처

예제 코드에 적용되는 기본 패키지 레이어:

| 레이어 | 패키지 | 역할 |
|--------|--------|------|
| contract | `com.example.{pattern}.contract` | 인터페이스, 포트 정의 |
| application | `com.example.{pattern}.application` | 애플리케이션 서비스, 유스케이스 |
| domain | `com.example.{pattern}.domain` | 도메인 객체, 비즈니스 로직 |
| infra | `com.example.{pattern}.infra` | Repository 구현체, 외부 연동 어댑터 |
| presentation | `com.example.{pattern}.presentation` | Controller, DTO, Request/Response |

> **원칙**: 패턴에 필요한 레이어만 선택적으로 사용. 모든 패턴이 5개 레이어를 모두 포함하지 않는다.

**패턴별 레이어 사용 현황**

| 패턴 | 사용 레이어 |
|------|------------|
| Singleton | domain, infra |
| Factory Method | contract, domain, application |
| Abstract Factory | contract, infra |
| Builder | domain, presentation |
| Prototype | contract, domain |
| Adapter | contract, infra |
| Bridge | contract, domain, infra |
| Composite | contract, domain |
| Decorator | contract, application |
| Facade | application, presentation |
| Flyweight | domain, infra |
| Proxy | contract, application, infra |
| Chain of Responsibility | contract, application |
| Command | contract, domain, application |
| Interpreter | contract, domain |
| Iterator | contract, domain |
| Mediator | contract, application, domain |
| Memento | domain |
| Observer | contract, domain, application |
| State | contract, domain |
| Strategy | contract, domain, application |
| Template Method | contract, application, domain |
| Visitor | contract, domain |

---

## 6. LLM 연동 명세

### 6.1 기능 1 — LLM 미사용

기능 1의 패턴 예제는 정적 데이터(`patterns_static.py`)로 제공합니다.  
AI API 호출이 없으므로 API Key 및 응답 대기 시간이 불필요합니다.

### 6.2 Anthropic Claude (기능 2 — V3에서 구현)

| 항목 | 값 |
|------|----|
| 모델 | claude-sonnet-4-6 |
| 호출 방식 | Async (AsyncAnthropic) |
| 용도 | CSV/Excel 파일 Factor 분석 → 패턴 추천 → 패키지 구조 생성 |
| 호출 시점 | V3 구현 시 |

---

## 7. 프론트엔드 명세

### 7.1 화면 구성

```
┌─────────────────┬─────────────────────────────────────────┐
│  사이드바(260px) │  메인 영역                              │
│                 │                                         │
│ [GoF] 패턴      │  [환영화면 / 로딩 / 결과]               │
│                 │                                         │
│ ┌─ 검색창 ────┐ │                                         │
│ └─────────────┘ │                                         │
│ [검색 버튼]     │                                         │
│                 │                                         │
│ ▸ 생성 패턴     │                                         │
│   Singleton ●   │                                         │
│   Factory M ●   │                                         │
│   ...           │                                         │
│ ▸ 구조 패턴     │                                         │
│   Adapter ●     │                                         │
│   ...           │                                         │
│ ▸ 행동 패턴     │                                         │
│   ...           │                                         │
└─────────────────┴─────────────────────────────────────────┘
```
`●` = 예제 탑재됨 (현재 23개 전체)

### 7.2 뷰(View) 상태

| 상태 | 표시 조건 |
|------|-----------|
| welcome | 초기 진입 시 |
| loading | 패턴 선택 후 API 응답 대기 중 |
| result | API 응답 완료 후 |

### 7.3 결과 화면 구성

| 섹션 | 내용 |
|------|------|
| 헤더 | 패턴명 + 카테고리 배지 + `📦 사전 탑재` 배지 |
| 01. 패턴 개요 | overview 텍스트 (한국어) |
| 02. Spring Boot 활용 시나리오 | use_case 텍스트 (한국어) |
| 03. 패키지 구조 | ASCII 트리 (monospace) |
| 04. 핵심 이점 | 체크마크(✓) 목록 |
| 05. 예제 코드 | 사용 레이어 태그 + 코드 블록(highlight.js) + 복사/전체화면 버튼 |

### 7.4 예제 코드 전체화면

| 항목 | 내용 |
|------|------|
| 진입 | `전체화면 ↗` 버튼 클릭 (예제 코드 섹션 우상단) |
| 표시 | 다크 배경(#0f1117) 풀스크린 오버레이 (`position: fixed`, `z-index: 9999`) |
| 구성 | 상단 헤더(패턴명 + 언어 배지 + 복사/닫기 버튼) + 코드 스크롤 영역 |
| 닫기 | `✕ 닫기` 버튼 또는 `ESC` 키 |
| 구현 방식 | 오버레이를 `index.html`에 정적 배치 후 JS로 내용 주입. 버튼 이벤트는 `addEventListener` 방식 사용 (Chrome 보안 정책 대응, inline onclick 미사용) |

### 7.5 예제 코드 표시 방식

| 항목 | 내용 |
|------|------|
| 높이 제한 | 없음 (max-height 제거) — 전체 코드 펼침 |
| 스크롤 | 페이지 전체 스크롤로 코드 탐색 |
| 전체화면 | 별도 풀스크린 오버레이에서 집중 열람 가능 |

### 7.6 UI 색상 규칙

| 요소 | 색상 |
|------|------|
| 사이드바 배경 | #0f1117 (다크 네이비) |
| 활성 패턴 | #4f46e5 (인디고) |
| Creational 배지 | #dbeafe / #1e40af (파란 계열) |
| Structural 배지 | #d1fae5 / #065f46 (초록 계열) |
| Behavioral 배지 | #fef3c7 / #92400e (노란 계열) |
| 사전탑재 배지 | #d1fae5 / #065f46 (초록 계열) |
| 예제 탑재 점(●) | #10b981 (에메랄드) |
| 전체화면 버튼 | #4f46e5 (인디고) |

---

## 8. 실행 환경

### 사전 요구사항

- Python 3.11 이상
- pip

### requirements.txt (V1 기준)

```
fastapi
uvicorn[standard]
anthropic
python-dotenv
aiofiles
```

> `anthropic` 패키지는 V3(기능 2) 구현 시 사용됩니다. V1에서는 호출되지 않습니다.

### 설치 및 실행

```bash
# 1. 패키지 설치
cd D:\projects\pocPattern\backend
pip install -r requirements.txt

# 2. API Key 설정 (V3 기능 2 사용 시 필요)
# .env 파일
ANTHROPIC_API_KEY=sk-ant-...

# 3. 서버 실행
uvicorn main:app --reload --port 8000

# 4. 브라우저 접속
# http://localhost:8000
```

---

## 9. 버전별 추가 개발 항목

### V2 추가 항목 (기능 3 — MD 생성)

| 항목 | 내용 |
|------|------|
| 신규 API | `GET /api/patterns/list` — 조회 가능한 패턴 목록 (MD 선택용) |
| 신규 API | `POST /api/export/patterns` — 선택한 패턴 MD 생성 및 다운로드 |
| 프론트엔드 | 패턴 선택 체크박스 UI |
| 프론트엔드 | MD 다운로드 버튼 |

### V3 추가 항목 (기능 2 — 파일 분석 + 시각화)

| 항목 | 내용 |
|------|------|
| 신규 라우터 | `routers/analysis.py` — 파일 업로드 및 분석 API |
| 신규 서비스 | `services/file_service.py` — CSV/Excel 파싱 |
| 신규 서비스 | `services/claude_service.py` — Anthropic Claude API 연동 |
| 신규 API | `POST /api/analysis/upload` — 파일 업로드 |
| 신규 API | `POST /api/analysis/recommend` — 패턴 추천 |
| 신규 API | `POST /api/analysis/structure` — 패키지 구조 생성 |
| 신규 API | `POST /api/export/analysis` — 분석 결과 MD 다운로드 |
| 프론트엔드 | 파일 업로드 UI |
| 프론트엔드 | 패턴 추천 결과 및 선택 UI |
| 프론트엔드 | 트리 시각화 + 다이어그램 시각화 (두 가지) |
| 추가 패키지 | `pandas`, `openpyxl` |
