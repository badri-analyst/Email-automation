# Spreadsheet Validation, Outreach Cleaning, And Research Workbench

Production-grade Streamlit application plus modular outreach cleaning, role-country intelligence, LinkedIn research, company research, professional communication signals, candidate proof assets, central decision orchestration, recruiter-facing email generation, and direct Gmail SMTP sending.

## Project Structure

```text
project/
|-- app.py
|-- requirements.txt
|-- core/
|   |-- config.py
|   |-- constants.py
|   `-- exceptions.py
|-- models/
|   `-- schemas.py
|-- schemas/
|   |-- research_schema.py
|   |-- companyResearchSchema.py
|   |-- roleCountrySchema.py
|   |-- personalityAnalysisSchema.py
|   |-- decisionSchema.py
|   |-- emailPersonalizationSchema.py
|   `-- candidateAssetsSchema.py
|-- config/
|   |-- role_mappings.json
|   |-- country_mappings.json
|   |-- role_country_rules.json
|   |-- decision_rules.json
|   |-- status_rules.json
|   |-- subject_rules.json
|   |-- tone_rules.json
|   `-- forbidden_phrases.json
|-- templates/
|   |-- recruiter_templates/
|   `-- hiring_manager_templates/
|-- prompts/
|   `-- linkedin_research_prompt.txt
|-- cache/
|   |-- campaignCompanyCache.py
|   |-- roleCountryCache.py
|   `-- personalityAnalysisCache.py
|-- orchestration/
|   |-- companyResearchPipeline.py
|   |-- roleCountryPipeline.py
|   |-- personalityAnalysisPipeline.py
|   |-- decisionEnginePipeline.py
|   `-- emailGenerationPipeline.py
|-- safety/
|   |-- unsafeInferenceBlocker.py
|   `-- sensitiveContentFilter.py
|-- services/
|   |-- candidate_assets/
|   |   |-- candidateAssetsController.py
|   |   |-- linkedinAssetValidator.py
|   |   |-- videoAssetValidator.py
|   |   |-- resumeAssetManager.py
|   |   |-- proofSnippetBuilder.py
|   |   |-- positioningSummaryBuilder.py
|   |   |-- whyRelevantBuilder.py
|   |   |-- proofStatusService.py
|   |   `-- candidateAssetsRepository.py
|   |-- email_personalization/
|   |   |-- emailPersonalizationController.py
|   |   |-- hookModelEmailBuilder.py
|   |   |-- subjectLineGenerator.py
|   |   |-- subjectSignalMapper.py
|   |   |-- openingTriggerSelector.py
|   |   |-- candidatePositioningService.py
|   |   |-- candidateProofPointService.py
|   |   |-- resumeMentionBuilder.py
|   |   |-- ctaBuilder.py
|   |   |-- toneAdapterService.py
|   |   |-- fallbackEmailBuilder.py
|   |   |-- emailSafetyFilter.py
|   |   |-- emailQualityValidator.py
|   |   `-- emailPersonalizationRepository.py
|   |-- decision_engine/
|   |   |-- decisionEngineController.py
|   |   |-- rowEligibilityService.py
|   |   |-- sendPermissionService.py
|   |   |-- researchPathSelector.py
|   |   |-- fallbackDecisionService.py
|   |   |-- manualReviewService.py
|   |   |-- scoreFieldGuardService.py
|   |   |-- finalPayloadBuilder.py
|   |   |-- decisionStatusService.py
|   |   `-- decisionRepository.py
|   |-- personality_analysis/
|   |   |-- personalityAnalysisController.py
|   |   |-- communicationStyleAnalyzer.py
|   |   |-- professionalSignalExtractor.py
|   |   |-- professionalMotivatorExtractor.py
|   |   |-- persuasionProfileBuilder.py
|   |   |-- personalizationGuidanceBuilder.py
|   |   |-- safetyFilterService.py
|   |   |-- personalityAnalysisStatusService.py
|   |   `-- personalityAnalysisRepository.py
|   |-- role_country/
|   |   |-- roleCountryIntelligenceController.py
|   |   |-- roleNormalizationService.py
|   |   |-- countryNormalizationService.py
|   |   |-- roleKnowledgeService.py
|   |   |-- countryRoleExpectationService.py
|   |   |-- skillKeywordService.py
|   |   |-- emailPositioningService.py
|   |   |-- proofPointService.py
|   |   |-- roleCountryStatusService.py
|   |   `-- roleCountryRepository.py
|   |-- company_research/
|   |   |-- companyResearchController.py
|   |   |-- companyNameService.py
|   |   |-- companyWebsiteService.py
|   |   |-- companySourceSelector.py
|   |   |-- companyProfileExtractor.py
|   |   |-- companyNewsExtractor.py
|   |   |-- companyValuesExtractor.py
|   |   |-- companyPersonalizationBuilder.py
|   |   |-- companyResearchStatusService.py
|   |   `-- companyResearchRepository.py
|   |-- linkedin_research/
|   |   |-- profile_analyzer.py
|   |   |-- communication_analyzer.py
|   |   |-- motivator_analyzer.py
|   |   |-- persuasion_generator.py
|   |   |-- insight_generator.py
|   |   |-- status_manager.py
|   |   |-- evidence_manager.py
|   |   `-- json_validator.py
|   |-- cleaning/
|   |   |-- whitespace_cleaner.py
|   |   |-- unicode_cleaner.py
|   |   |-- html_cleaner.py
|   |   `-- punctuation_cleaner.py
|   |-- normalization/
|   |   |-- column_alias_normalizer.py
|   |   |-- company_normalizer.py
|   |   |-- country_normalizer.py
|   |   `-- linkedin_normalizer.py
|   |-- inference/
|   |   |-- name_splitter.py
|   |   |-- seniority_inference.py
|   |   `-- department_inference.py
|   |-- orchestration/
|   |   |-- cleaning_pipeline.py
|   |   |-- linkedin_research_pipeline.py
|   |   `-- row_router.py
|   |-- cleaning_service.py
|   |-- duplicate_service.py
|   |-- export_service.py
|   |-- file_service.py
|   |-- normalization_service.py
|   `-- validation_service.py
|-- ui/
|-- utils/
`-- tests/
```

## Features

- Upload `.csv` and `.xlsx` files.
- Parse XLSX files through `pandas` and `openpyxl`.
- Best-effort CSV encoding detection with malformed-row skipping.
- Validate required columns: `Name`, `Email`, `Company`, `Role`, `Country`.
- Canonicalize headers using trimmed, case-insensitive matching.
- Validate emails with `email-validator`.
- Detect duplicates by email or by `Name` + `Company`.
- Normalize common country aliases such as `USA`, `UK`, and `UAE`.
- Clean whitespace, lower-case emails, remove fully empty rows, and handle null values safely.
- Preview cleaned records and validation reports with pagination.
- Export valid cleaned records, duplicate records, and validation errors as CSV files.

## Outreach Cleaning Engine

The outreach cleaning engine starts after the validation module has already accepted or rejected rows. It does not revalidate files, emails, LinkedIn URLs, or duplicate state.

Pipeline order:

1. Column normalization
2. Whitespace cleanup
3. Unicode cleanup
4. HTML cleanup
5. Company normalization
6. Country normalization
7. LinkedIn normalization
8. Name splitting
9. Seniority inference
10. Department inference
11. Final standardization
12. Output generation

The output contract is `OutreachRecord` in `models/schemas.py`. It preserves original values and emits deterministic AI-ready fields such as `full_name`, `first_name`, `normalized_company_name`, `seniority_level`, `department`, and `cleaning_status`.

Allowed cleaning statuses are:

- `cleaned`
- `partially_cleaned`
- `skipped`
- `failed`

Example usage:

```python
import pandas as pd

from services.orchestration.cleaning_pipeline import CleaningPipeline

validated_records = pd.DataFrame(
    [
        {
            "Full Name": "  joHN   smITh ",
            "Email Address": " JOHN@Example.COM ",
            "company_name": "Google LLC",
            "Job Title": "Senior Software Engineer",
            "Country": "USA",
            "LinkedIn Profile": "https://linkedin.com/in/john/?trk=abc",
            "Validation Status": "valid",
        }
    ]
)

result = CleaningPipeline().clean_dataframe(validated_records)
outreach_dataframe = result.dataframe
```

## Role-Country Intelligence Module

The Role-Country Intelligence Module runs after validation and cleaning and before personalization. It answers: for this role in this country, what should outreach emphasize?

It is MVP rule-based and uses only configured mappings and approved professional role expectations. It does not perform live labor-market research, create scores, rank candidates, or generate country stereotypes.

Core files:

- `schemas/roleCountrySchema.py`
- `config/role_mappings.json`
- `config/country_mappings.json`
- `config/role_country_rules.json`
- `services/role_country/roleCountryIntelligenceController.py`
- `services/role_country/roleNormalizationService.py`
- `services/role_country/countryNormalizationService.py`
- `services/role_country/roleKnowledgeService.py`
- `services/role_country/countryRoleExpectationService.py`
- `services/role_country/skillKeywordService.py`
- `services/role_country/emailPositioningService.py`
- `services/role_country/proofPointService.py`
- `services/role_country/roleCountryStatusService.py`
- `services/role_country/roleCountryRepository.py`
- `orchestration/roleCountryPipeline.py`
- `cache/roleCountryCache.py`
- `supabase_role_country_intelligence_results.sql`

Role-country statuses:

- `ready_for_personalization`
- `role_only_intelligence_used`
- `country_missing`
- `role_missing`
- `role_country_not_supported`
- `industry_refinement_used`
- `seniority_refinement_used`
- `insufficient_data`
- `manual_review_required`
- `role_country_research_failed`

Example usage:

```python
from orchestration.roleCountryPipeline import RoleCountryPipeline

payload = {
    "campaign_id": "campaign-1",
    "prospect_id": "prospect-1",
    "target_role": "BA",
    "target_country": "USA",
    "industry": "fintech",
    "seniority_level": "senior",
    "candidate_positioning": "process improvement and stakeholder alignment",
}

result = RoleCountryPipeline().build_intelligence(payload)
role_country_json = result.model_dump()
```

## LinkedIn Research Module

The LinkedIn Research Module starts after validation and cleaning. It remains independent from email generation, SMTP sending, analytics, and scraping.

It accepts cleaned prospect fields plus approved public professional/company text and returns the stable `LinkedInResearchOutput` schema in `schemas/research_schema.py`.

Core files:

- `services/linkedin_research/profile_analyzer.py`
- `services/linkedin_research/communication_analyzer.py`
- `services/linkedin_research/motivator_analyzer.py`
- `services/linkedin_research/persuasion_generator.py`
- `services/linkedin_research/insight_generator.py`
- `services/linkedin_research/status_manager.py`
- `services/linkedin_research/evidence_manager.py`
- `services/linkedin_research/json_validator.py`
- `services/orchestration/linkedin_research_pipeline.py`
- `prompts/linkedin_research_prompt.txt`

Research statuses:

- `ready_for_personalization`
- `insufficient_data`
- `company_fallback_used`
- `linkedin_missing`
- `linkedin_invalid`
- `linkedin_inaccessible`
- `research_failed`

Safety rules enforced by design:

- No scraping of unauthorized sources.
- No hidden scores, rankings, percentages, or lead-fit metrics.
- No sensitive inferences about age, gender, religion, politics, ethnicity, health, family status, or private life.
- Imported profile text is sanitized and treated as data, never instructions.
- Unsupported claims return `Insufficient data.`
- Every generated personalization insight includes an evidence phrase or the insufficient-data marker.

Example usage:

```python
from services.orchestration.linkedin_research_pipeline import LinkedInResearchPipeline

payload = {
    "full_name": "Jane Smith",
    "role_title": "Head of Engineering",
    "company_name": "Acme",
    "normalized_company_name": "Acme",
    "industry": "SaaS",
    "linkedin_url": "https://linkedin.com/in/jane-smith",
    "profile_summary": "Jane leads engineering strategy for customer value and automation.",
    "company_updates": ["Acme announced a product launch in 2026."],
}

research = LinkedInResearchPipeline().research(payload)
research_json = research.model_dump()
```

## Company Research Module

The Company Research Module is a fallback and enrichment layer after LinkedIn research. It performs company-level research only and remains independent from email generation, sending, scoring, campaign analytics, and dashboards.

It accepts cleaned company data, LinkedIn research status, fallback/enrichment flags, and approved source snippets. It does not scrape unauthorized sources. API keys for future approved providers should be read only from backend environment variables and never exposed to the frontend.

Core files:

- `schemas/companyResearchSchema.py`
- `services/company_research/companyResearchController.py`
- `services/company_research/companyNameService.py`
- `services/company_research/companyWebsiteService.py`
- `services/company_research/companySourceSelector.py`
- `services/company_research/companyProfileExtractor.py`
- `services/company_research/companyNewsExtractor.py`
- `services/company_research/companyValuesExtractor.py`
- `services/company_research/companyPersonalizationBuilder.py`
- `services/company_research/companyResearchStatusService.py`
- `services/company_research/companyResearchRepository.py`
- `orchestration/companyResearchPipeline.py`
- `cache/campaignCompanyCache.py`
- `supabase_company_research_results.sql`

Company research statuses:

- `ready_for_personalization`
- `company_basic_data_found`
- `recent_news_found`
- `company_values_found`
- `company_fallback_used`
- `company_website_missing`
- `company_not_found`
- `insufficient_data`
- `manual_review_required`
- `company_research_failed`

Example usage:

```python
from orchestration.companyResearchPipeline import CompanyResearchPipeline

payload = {
    "campaign_id": "campaign-1",
    "prospect_id": "prospect-1",
    "company_name": "Acme LLC",
    "company_website": "https://acme.com",
    "company_linkedin_url": "https://linkedin.com/company/acme",
    "target_role": "Business Analyst",
    "target_country": "India",
    "linkedin_research_status": "linkedin_inaccessible",
    "approved_sources": [
        {
            "source_type": "official_website",
            "url": "https://acme.com",
            "text": "Acme is a SaaS platform offering workflow automation for enterprise customers.",
        }
    ],
}

result = CompanyResearchPipeline().research_company(payload)
company_json = result.model_dump()
```

## Professional Communication Signals Module

This module analyzes observable professional communication patterns only. It is not a psychological profiler and does not diagnose, score, rank, or infer sensitive/private traits.

Core files:

- `schemas/personalityAnalysisSchema.py`
- `services/personality_analysis/personalityAnalysisController.py`
- `services/personality_analysis/communicationStyleAnalyzer.py`
- `services/personality_analysis/professionalSignalExtractor.py`
- `services/personality_analysis/professionalMotivatorExtractor.py`
- `services/personality_analysis/persuasionProfileBuilder.py`
- `services/personality_analysis/personalizationGuidanceBuilder.py`
- `services/personality_analysis/safetyFilterService.py`
- `services/personality_analysis/personalityAnalysisStatusService.py`
- `services/personality_analysis/personalityAnalysisRepository.py`
- `safety/unsafeInferenceBlocker.py`
- `safety/sensitiveContentFilter.py`
- `orchestration/personalityAnalysisPipeline.py`
- `cache/personalityAnalysisCache.py`
- `supabase_personality_analysis_results.sql`

Statuses:

- `ready_for_personalization`
- `insufficient_data`
- `linkedin_profile_analysis_used`
- `linkedin_posts_analysis_used`
- `company_based_analysis_used`
- `manual_review_required`
- `personality_analysis_failed`
- `unsafe_analysis_blocked`

Example usage:

```python
from orchestration.personalityAnalysisPipeline import PersonalityAnalysisPipeline

payload = {
    "campaign_id": "campaign-1",
    "prospect_id": "prospect-1",
    "person_name": "Jane Smith",
    "job_title": "Business Analyst",
    "company_name": "Acme",
    "linkedin_posts_summary": "Shared practical workflow improvements for customer value and stakeholder collaboration.",
    "role_country_intelligence": "Emphasize stakeholder alignment and measurable outcomes.",
}

result = PersonalityAnalysisPipeline().analyze(payload)
communication_json = result.model_dump()
```

## Candidate Assets And Proof Module

The Candidate Assets & Proof Module centralizes candidate-provided proof assets and recruiter-safe positioning metadata. It validates and normalizes LinkedIn, resume, video, and portfolio references, then prepares concise proof snippets and relevance summaries for downstream decisioning and email personalization.

It does not invent achievements, metrics, certifications, portfolio work, or credibility claims.

Core files:

- `schemas/candidateAssetsSchema.py`
- `services/candidate_assets/candidateAssetsController.py`
- `services/candidate_assets/linkedinAssetValidator.py`
- `services/candidate_assets/videoAssetValidator.py`
- `services/candidate_assets/resumeAssetManager.py`
- `services/candidate_assets/proofSnippetBuilder.py`
- `services/candidate_assets/positioningSummaryBuilder.py`
- `services/candidate_assets/whyRelevantBuilder.py`
- `services/candidate_assets/proofStatusService.py`
- `services/candidate_assets/candidateAssetsRepository.py`
- `orchestration/candidateAssetsPipeline.py`
- `supabase_candidate_assets_results.sql`

Proof statuses:

- `proof_ready`
- `partial_proof_available`
- `insufficient_supporting_proof`
- `invalid_asset_link`
- `manual_review_required`
- `proof_processing_failed`

Example usage:

```python
from orchestration.candidateAssetsPipeline import CandidateAssetsPipeline

payload = {
    "campaign_id": "campaign-1",
    "candidate_id": "candidate-1",
    "linkedin_url": "linkedin.com/in/jane",
    "resume_url": "https://drive.google.com/resume",
    "youtube_video_url": "https://youtube.com/watch?v=abc",
    "portfolio_links": ["https://github.com/jane/project"],
    "candidate_positioning": "Business Analyst focused on workflow clarity.",
    "candidate_proof_points": ["requirements clarification example"],
}

assets = CandidateAssetsPipeline().process(payload)
assets_json = assets.model_dump()
```

## Decision Engine Module

The Decision Engine is the central orchestration and safety gate. It decides whether a row can continue, whether personalization or sending is allowed, which research path to use, whether fallback/manual review is required, and what structured payload should go downstream.

It is rule-based and deterministic. It does not generate email copy, perform research, send emails, hallucinate missing context, or create scores.

Core files:

- `schemas/decisionSchema.py`
- `config/decision_rules.json`
- `config/status_rules.json`
- `services/decision_engine/decisionEngineController.py`
- `services/decision_engine/rowEligibilityService.py`
- `services/decision_engine/sendPermissionService.py`
- `services/decision_engine/researchPathSelector.py`
- `services/decision_engine/fallbackDecisionService.py`
- `services/decision_engine/manualReviewService.py`
- `services/decision_engine/scoreFieldGuardService.py`
- `services/decision_engine/finalPayloadBuilder.py`
- `services/decision_engine/decisionStatusService.py`
- `services/decision_engine/decisionRepository.py`
- `orchestration/decisionEnginePipeline.py`
- `supabase_decision_engine_results.sql`

Decision statuses:

- `ready_for_email_personalization`
- `ready_for_draft_generation`
- `ready_for_sending`
- `blocked_invalid_email`
- `skipped_duplicate`
- `company_fallback_selected`
- `role_country_only_selected`
- `manual_review_required`
- `insufficient_data`
- `smtp_not_configured`
- `decision_failed`

Next actions:

- `generate_email`
- `generate_draft`
- `send_email`
- `skip_sending`
- `skip_duplicate`
- `run_company_research`
- `run_role_country_only_personalization`
- `manual_review`
- `stop_processing`

Example usage:

```python
from orchestration.decisionEnginePipeline import DecisionEnginePipeline

payload = {
    "campaign_id": "campaign-1",
    "prospect_id": "prospect-1",
    "cleaning_output": {"email": "jane@example.com", "validation_status": "valid"},
    "role_country_output": {"role_country_status": "ready_for_personalization"},
    "linkedin_research_output": {"research_status": "ready_for_personalization"},
    "company_research_output": {"company_research_status": "company_basic_data_found"},
    "personality_analysis_output": {"personality_analysis_status": "linkedin_profile_analysis_used"},
    "campaign_settings": {"smtp_configured": True, "smtp_valid": True, "sending_enabled": True},
}

decision = DecisionEnginePipeline().decide(payload)
decision_json = decision.model_dump()
```

## Email Personalization And Direct Send Flow

The Email Personalization Module consumes only the Decision Engine `final_personalization_payload` and generates recruiter-facing email content. In the React/Express product flow, generated emails are sent immediately through backend-managed Gmail SMTP using the candidate Gmail address and Google App Password. There is no draft approval queue or SMTP settings page.

Core files:

- `schemas/emailPersonalizationSchema.py`
- `config/subject_rules.json`
- `config/tone_rules.json`
- `config/forbidden_phrases.json`
- `templates/recruiter_templates/default.txt`
- `templates/hiring_manager_templates/default.txt`
- `services/email_personalization/emailPersonalizationController.py`
- `services/email_personalization/hookModelEmailBuilder.py`
- `services/email_personalization/subjectLineGenerator.py`
- `services/email_personalization/subjectSignalMapper.py`
- `services/email_personalization/openingTriggerSelector.py`
- `services/email_personalization/candidatePositioningService.py`
- `services/email_personalization/candidateProofPointService.py`
- `services/email_personalization/resumeMentionBuilder.py`
- `services/email_personalization/ctaBuilder.py`
- `services/email_personalization/toneAdapterService.py`
- `services/email_personalization/fallbackEmailBuilder.py`
- `services/email_personalization/emailSafetyFilter.py`
- `services/email_personalization/emailQualityValidator.py`
- `services/email_personalization/emailPersonalizationRepository.py`
- `orchestration/emailGenerationPipeline.py`
- `supabase_email_personalization_results.sql`

Email generation statuses from the generation layer:

- `email_ready`
- `draft_ready`
- `fallback_email_created`
- `manual_review_required`
- `insufficient_data`
- `blocked_invalid_payload`
- `blocked_unsafe_content`
- `email_generation_failed`

Example usage:

```python
from orchestration.emailGenerationPipeline import EmailGenerationPipeline

payload = {
    "campaign_id": "campaign-1",
    "prospect_id": "prospect-1",
    "final_personalization_payload": {
        "prospect": {"company": "Acme", "role": "Business Analyst"},
        "role_country_context": {
            "normalized_role": "Business Analyst",
            "business_keywords": ["workflow clarity"],
            "proof_points_to_use": ["workflow improvement example"],
        },
        "selected_hooks": ["Acme builds workflow software for enterprise teams. Evidence: approved source."],
    },
}

email = EmailGenerationPipeline().generate(payload)
email_json = email.model_dump()
```

Direct-send database setup:

```bash
psql "$SUPABASE_DATABASE_URL" -f supabase_direct_send_migration.sql
```

Supabase setup:

```bash
psql "$SUPABASE_DATABASE_URL" -f supabase_company_research_results.sql
psql "$SUPABASE_DATABASE_URL" -f supabase_role_country_intelligence_results.sql
psql "$SUPABASE_DATABASE_URL" -f supabase_personality_analysis_results.sql
psql "$SUPABASE_DATABASE_URL" -f supabase_candidate_assets_results.sql
psql "$SUPABASE_DATABASE_URL" -f supabase_decision_engine_results.sql
psql "$SUPABASE_DATABASE_URL" -f supabase_email_personalization_results.sql
psql "$SUPABASE_DATABASE_URL" -f supabase_direct_send_migration.sql
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Frontend setup:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Backend setup:

```bash
cd backend
npm install
cp .env.example .env
npm run dev
```

The React app calls the Express backend, and the Express backend bridges into the existing Python orchestration modules.

Hosted deployment:

- Frontend: Vercel
- Backend: Render
- Database: Supabase

See [DEPLOYMENT.md](DEPLOYMENT.md).

## Run

```bash
streamlit run app.py
```

For the React dashboard, run frontend and backend together:

```bash
cd backend && npm run dev
cd frontend && npm run dev
```

On Windows without PowerShell, double-click or run:

```bat
RUN_APP.cmd
```

Or run them separately:

```bat
start-all.cmd
start-backend.cmd
start-frontend.cmd
```

## Test

```bash
pytest
```

When Windows denies access to old pytest temp folders, run:

```bash
pytest tests -p no:cacheprovider
```

## Example Workflow

1. Start the app with `streamlit run app.py`.
2. Upload a CSV or XLSX file containing the required columns.
3. Review the summary metrics, cleaned preview, validation errors, and duplicate records.
4. Download the valid cleaned CSV, duplicate CSV, or validation report CSV.

## Security Notes

- Uploaded files are processed in memory and are not persisted.
- File extensions and upload size are validated before parsing.
- Filenames are sanitized to remove path components.
- Uploaded spreadsheet content is never executed.
- Exports are generated directly from validated in-memory dataframes.
- Research modules sanitize imported profile/company text and treat it as data, never instructions.
- Research modules store structured output only, not full scraped pages or unnecessary raw HTML.
- Role-country intelligence uses configured rule files only and avoids country stereotypes or unsupported hiring claims.
- Professional communication analysis uses observable professional content only and blocks sensitive inference, diagnosis, manipulation, and scoring language.
- Candidate assets module stores only metadata and approved links, validates URLs safely, and flags risky proof claims for review.
- Decision engine strips forbidden score/rating/ranking fields, flags manual review when detected, and never exposes SMTP credentials.
- Email personalization uses deterministic templates, one CTA, concise draft limits, and blocks hallucinated, manipulative, sensitive, or score-like content.

## Suggested Production Improvements

- Add authentication and role-based access controls.
- Add virus scanning for uploaded files before parsing.
- Store audit logs in a centralized observability platform.
- Add configurable validation rules per tenant or business unit.
- Load outreach alias, company suffix, country, seniority, and department maps from tenant-scoped configuration.
- Add approved-data connectors for company pages or internal CRM enrichment, with explicit source attribution.
- Store research outputs and source evidence in an auditable enrichment store.
- Add async background processing for files larger than the default limit.
- Add OpenTelemetry tracing and dashboarded performance metrics.
- Containerize the app and deploy behind a reverse proxy with strict upload limits.
