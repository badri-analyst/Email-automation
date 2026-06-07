create table if not exists personality_analysis_results (
    id uuid primary key default gen_random_uuid(),
    campaign_id text not null,
    prospect_id text,
    person_name text not null default '',
    job_title text not null default '',
    company_name text not null default '',
    personality_analysis_status text not null,
    personality_analysis_reason text not null default 'Insufficient data.',
    analysis_source_type text not null default 'insufficient_data',
    communication_style jsonb not null default '{}'::jsonb,
    professional_behavioral_signals jsonb not null default '[]'::jsonb,
    professional_motivators jsonb not null default '[]'::jsonb,
    persuasion_profile jsonb not null default '{}'::jsonb,
    personalization_guidance jsonb not null default '["Insufficient data."]'::jsonb,
    evidence_notes jsonb not null default '[]'::jsonb,
    manual_review_flag boolean not null default false,
    structured_output jsonb not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint personality_analysis_status_allowed check (
        personality_analysis_status in (
            'ready_for_personalization',
            'insufficient_data',
            'linkedin_profile_analysis_used',
            'linkedin_posts_analysis_used',
            'company_based_analysis_used',
            'manual_review_required',
            'personality_analysis_failed',
            'unsafe_analysis_blocked'
        )
    )
);

create index if not exists idx_personality_analysis_campaign_prospect
    on personality_analysis_results (campaign_id, prospect_id);

create index if not exists idx_personality_analysis_campaign_person
    on personality_analysis_results (campaign_id, person_name, company_name);
