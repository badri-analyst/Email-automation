"""Route rows based on upstream validation status."""

from collections.abc import Iterable

from core.constants import VALID_CLEANING_INPUT_STATUSES


class RowRouter:
    """Decide whether a row should be cleaned or skipped."""

    def __init__(self, valid_statuses: Iterable[str] = VALID_CLEANING_INPUT_STATUSES) -> None:
        self._valid_statuses = {status.casefold() for status in valid_statuses}

    def should_clean(self, validation_status: object) -> bool:
        """Return True when the upstream validation status is cleanable."""
        if validation_status is None:
            return True

        status = str(validation_status).strip()
        if not status:
            return True

        return status.casefold() in self._valid_statuses

