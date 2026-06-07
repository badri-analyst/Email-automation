"""Conservative name splitting."""


class NameSplitter:
    """Split full names into first and last name components without aggressive assumptions."""

    def split(self, full_name: object) -> tuple[str, str]:
        """Return first and last name components."""
        if full_name is None:
            return "", ""

        parts = str(full_name).strip().split()
        if not parts:
            return "", ""
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], " ".join(parts[1:])

