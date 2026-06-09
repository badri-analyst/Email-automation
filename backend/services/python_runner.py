"""Bridge Express controllers to the existing Python orchestration modules."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def run(module_name: str, payload: dict) -> dict:
    if module_name == "parse-spreadsheet":
        from backend.services.spreadsheet_parser import parse_spreadsheet
        return parse_spreadsheet(payload)
    if module_name == "candidate-assets":
        from orchestration.candidateAssetsPipeline import CandidateAssetsPipeline
        return CandidateAssetsPipeline().process(payload).model_dump()
    if module_name == "role-country":
        from orchestration.roleCountryPipeline import RoleCountryPipeline
        return RoleCountryPipeline().build_intelligence(payload).model_dump()
    if module_name == "linkedin-research":
        from services.orchestration.linkedin_research_pipeline import LinkedInResearchPipeline
        return LinkedInResearchPipeline().research(payload).model_dump()
    if module_name == "company-research":
        from orchestration.companyResearchPipeline import CompanyResearchPipeline
        return CompanyResearchPipeline().research_company(payload).model_dump()
    if module_name == "personality-analysis":
        from orchestration.personalityAnalysisPipeline import PersonalityAnalysisPipeline
        return PersonalityAnalysisPipeline().analyze(payload).model_dump()
    if module_name == "decision-engine":
        from orchestration.decisionEnginePipeline import DecisionEnginePipeline
        return DecisionEnginePipeline().decide(payload).model_dump()
    if module_name == "email-personalization":
        from orchestration.emailGenerationPipeline import EmailGenerationPipeline
        return EmailGenerationPipeline().generate(payload).model_dump()
    raise ValueError(f"Unsupported module: {module_name}")


if __name__ == "__main__":
    module = sys.argv[1]
    request_payload = json.loads(sys.stdin.read() or "{}")

    # Redirect stdout to stderr while running the module so any stray print()
    # calls inside pipeline steps don't corrupt the JSON output that Node.js reads.
    _real_stdout = sys.stdout
    sys.stdout = sys.stderr
    try:
        result = run(module, request_payload)
    finally:
        sys.stdout = _real_stdout

    print(json.dumps(result))
