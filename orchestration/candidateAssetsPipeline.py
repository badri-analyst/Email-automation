"""Pipeline orchestration for candidate assets."""

from schemas.candidateAssetsSchema import CandidateAssetInput, CandidateAssetsOutput
from services.candidate_assets.candidateAssetsController import CandidateAssetsController
from services.candidate_assets.candidateAssetsRepository import CandidateAssetsRepository


class CandidateAssetsPipeline:
    """Batch pipeline for candidate proof metadata."""

    def __init__(self, repository: CandidateAssetsRepository | None = None) -> None:
        self._repository = repository or CandidateAssetsRepository()
        self._controller = CandidateAssetsController(repository=self._repository)

    def process(self, payload: CandidateAssetInput | dict[str, object]) -> CandidateAssetsOutput:
        """Process one candidate asset payload."""
        return self._controller.process(payload)

    def process_batch(self, payloads: list[CandidateAssetInput | dict[str, object]]) -> list[CandidateAssetsOutput]:
        """Process candidate asset payloads in batch."""
        return [self.process(payload) for payload in payloads]
