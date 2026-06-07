"""Decision rule loading helpers."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=4)
def load_decision_config(filename: str) -> dict[str, Any]:
    """Load a decision config JSON file."""
    with (PROJECT_ROOT / "config" / filename).open("r", encoding="utf-8") as file:
        return json.load(file)

