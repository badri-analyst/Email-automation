"""Skill and keyword refinement service."""


class SkillKeywordService:
    """Combine configured skills, tools, keywords, and refinements."""

    @staticmethod
    def merge_unique(*groups: list[str]) -> list[str]:
        """Merge lists while preserving deterministic order."""
        output: list[str] = []
        for group in groups:
            for item in group:
                if item and item not in output:
                    output.append(item)
        return output
