from dataclasses import dataclass, fields
import json
from pathlib import Path
from urllib.parse import urlsplit

from .database import adapter_name


@dataclass(frozen=True)
class Config:
    engine: str = "postgresql"
    host: str = "127.0.0.1"
    port: int = 5432
    database: str = "sql_grader_demo"
    user: str = "sql_runner"
    oracle_client: str | None = None
    oracle_tablespace: str = "USERS"
    connect_seconds: int = 5
    statement_ms: int = 3000
    lock_ms: int = 1000
    task_seconds: int = 35
    batch_seconds: int = 900
    max_rows: int = 1000
    max_input_bytes: int = 200000
    ai_seconds: int = 240
    ai_url: str = "http://127.0.0.1:11434/api/chat"
    model: str = "qwen3.5:2b-q4_K_M"

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if field.type is int and (type(value) is not int or value <= 0):
                raise ValueError(f"Pozitív egész szükséges: {field.name}")
            if field.type is str and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"Szöveg szükséges: {field.name}")
        adapter_name(self.engine)
        if self.port > 65535 or self.max_rows > 10000 or self.max_input_bytes > 1000000:
            raise ValueError("A port, sorlimit vagy fájlméretlimit kívül esik a támogatott tartományon.")
        url = urlsplit(self.ai_url)
        if (url.scheme != "http" or url.hostname not in {"127.0.0.1", "::1"}
                or url.username or url.password or url.path != "/api/chat" or url.query or url.fragment):
            raise ValueError("Az AI csak helyi /api/chat címen érhető el.")


def load(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict):
            raise TypeError()
        return Config(**data)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Hibás konfigurációs fájl vagy ismeretlen mező.") from exc
