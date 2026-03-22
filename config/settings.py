from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-5.4-nano"
    placid_api_token: str = ""
    placid_base_url: str = "https://api.placid.app/api/rest"
    http_timeout_seconds: int = 60
    render_poll_attempts: int = 10
    render_poll_interval_seconds: int = 3
    data_dir: Path = Path("data")
    templates_path: Path = Path("data/templates.json")
    posts_db_path: Path = Path("data/posts.db")

    @classmethod
    def from_env(cls) -> "Settings":
        env_values = _load_dotenv(Path(".env"))
        return cls(
            openai_api_key=_env("OPENAI_API_KEY", "", env_values),
            openai_base_url=_env(
                "OPENAI_BASE_URL", "https://api.openai.com/v1", env_values
            ),
            openai_model=_env("OPENAI_MODEL", "gpt-5.4-nano", env_values),
            placid_api_token=_env("PLACID_API_TOKEN", "", env_values),
            placid_base_url=_env(
                "PLACID_BASE_URL", "https://api.placid.app/api/rest", env_values
            ),
            http_timeout_seconds=int(_env("HTTP_TIMEOUT_SECONDS", "60", env_values)),
            render_poll_attempts=int(_env("RENDER_POLL_ATTEMPTS", "10", env_values)),
            render_poll_interval_seconds=int(
                _env("RENDER_POLL_INTERVAL_SECONDS", "3", env_values)
            ),
            data_dir=Path(_env("DATA_DIR", "data", env_values)),
            templates_path=Path(
                _env("TEMPLATES_PATH", "data/templates.json", env_values)
            ),
            posts_db_path=Path(_env("POSTS_DB_PATH", "data/posts.db", env_values)),
        )


def _env(name: str, default: str, env_values: dict[str, str]) -> str:
    return os.getenv(name, env_values.get(name, default))


def _load_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values
