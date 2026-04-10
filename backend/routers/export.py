from fastapi import APIRouter
from data.patterns_static import PATTERNS_DATA

router = APIRouter()

_PATTERN_META = {
    "creational": [
        {"name": "Singleton",        "name_ko": "싱글턴"},
        {"name": "Factory Method",   "name_ko": "팩토리 메서드"},
        {"name": "Abstract Factory", "name_ko": "추상 팩토리"},
        {"name": "Builder",          "name_ko": "빌더"},
        {"name": "Prototype",        "name_ko": "프로토타입"},
    ],
    "structural": [
        {"name": "Adapter",   "name_ko": "어댑터"},
        {"name": "Bridge",    "name_ko": "브릿지"},
        {"name": "Composite", "name_ko": "컴포짓"},
        {"name": "Decorator", "name_ko": "데코레이터"},
        {"name": "Facade",    "name_ko": "파사드"},
        {"name": "Flyweight", "name_ko": "플라이웨이트"},
        {"name": "Proxy",     "name_ko": "프록시"},
    ],
    "behavioral": [
        {"name": "Chain of Responsibility", "name_ko": "책임 연쇄"},
        {"name": "Command",                 "name_ko": "커맨드"},
        {"name": "Interpreter",             "name_ko": "인터프리터"},
        {"name": "Iterator",                "name_ko": "이터레이터"},
        {"name": "Mediator",                "name_ko": "미디에이터"},
        {"name": "Memento",                 "name_ko": "메멘토"},
        {"name": "Observer",                "name_ko": "옵저버"},
        {"name": "State",                   "name_ko": "스테이트"},
        {"name": "Strategy",                "name_ko": "스트래티지"},
        {"name": "Template Method",         "name_ko": "템플릿 메서드"},
        {"name": "Visitor",                 "name_ko": "비지터"},
    ],
    "ddd": [
        {"name": "Aggregate Root",      "name_ko": "애그리거트 루트"},
        {"name": "Value Object",        "name_ko": "값 객체"},
        {"name": "Domain Event",        "name_ko": "도메인 이벤트"},
        {"name": "Repository",          "name_ko": "리포지토리"},
        {"name": "Domain Service",      "name_ko": "도메인 서비스"},
        {"name": "Application Service", "name_ko": "애플리케이션 서비스"},
        {"name": "Specification",       "name_ko": "스펙"},
        {"name": "CQRS",                "name_ko": "CQRS"},
        {"name": "Event Sourcing",      "name_ko": "이벤트 소싱"},
        {"name": "Saga",                "name_ko": "사가"},
    ],
}


@router.get("/patterns/list")
async def get_all_patterns_for_export():
    """MD 다운로드 선택용 — 전체 패턴 목록 반환 (available 포함)"""
    result = {}
    for cat, patterns in _PATTERN_META.items():
        result[cat] = [
            {**p, "available": p["name"] in PATTERNS_DATA}
            for p in patterns
        ]
    return {"patterns": result}
