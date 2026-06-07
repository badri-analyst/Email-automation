"""Email personalization config loading."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=8)
def load_email_config(filename: str) -> dict[str, Any]:
    """Load email personalization config."""
    with (PROJECT_ROOT / "config" / filename).open("r", encoding="utf-8") as file:
        return json.load(file)

