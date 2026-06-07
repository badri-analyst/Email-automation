"""Batch orchestration for professional communication analysis."""

from schemas.personalityAnalysisSchema import PersonalityAnalysisInput, PersonalityAnalysisOutput
from services.personality_analysis.personalityAnalysisController import PersonalityAnalysisController
from services.personality_analysis.personalityAnalysisRepository import PersonalityAnalysisRepository


class PersonalityAnalysisPipeline:
    """Campaign pipeline with duplicate analysis caching."""

    def __init__(self, repository: PersonalityAnalysisRepository | None = None) -> None:
        self._repository = repository or PersonalityAnalysisRepository()
        self._controller = PersonalityAnalysisController(repository=self._repository)

    def analyze(self, payload: PersonalityAnalysisInput | dict[str, object]) -> PersonalityAnalysisOutput:
        """Analyze one prospect."""
        return self._controller.analyze(payload)

    def analyze_batch(self, payloads: list[PersonalityAnalysisInput | dict[str, object]]) -> list[PersonalityAnalysisOutput]:
        """Analyze a campaign batch while isolating failures."""
        return [self.analyze(payload) for payload in payloads]
