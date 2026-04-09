import json
from pathlib import Path
from datetime import datetime

CACHE_FILE = Path(__file__).parent.parent / "data" / "pattern_cache.json"


class CacheService:
    def __init__(self):
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not CACHE_FILE.exists():
            CACHE_FILE.write_text("{}", encoding="utf-8")

    def _load(self) -> dict:
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _persist(self, data: dict):
        CACHE_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def get(self, pattern_name: str) -> dict | None:
        return self._load().get(pattern_name)

    def save(self, pattern_name: str, pattern_data: dict):
        data = self._load()
        data[pattern_name] = {
            **pattern_data,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        self._persist(data)

    def get_all(self) -> dict:
        return self._load()
