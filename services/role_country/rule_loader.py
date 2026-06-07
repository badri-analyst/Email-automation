"""Config rule loading helpers."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=8)
def load_json_config(filename: str) -> dict[str, Any]:
    """Load a JSON config file from the project config directory."""
    path = PROJECT_ROOT / "config" / filename
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

