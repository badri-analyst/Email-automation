create table if not exists role_country_intelligence_results (
    id uuid primary key default gen_random_uuid(),
    campaign_id text not null,
    prospect_id text,
    target_role text not null default '',
    target_country text not null default '',
    normalized_role text not null default '',
    normalized_country text not null default '',
    role_country_status text not null,
    role_country_reason text not null default 'Insufficient data.',
    intelligence_source_type text not null default 'insufficient_data',
    role_summary text not null default 'Insufficient data.',
    core_responsibilities jsonb not null default '["Insufficient data."]'::jsonb,
    country_role_expectations jsonb not null default '["Insufficient data."]'::jsonb,
    priority_skills jsonb not null default '["Insufficient data."]'::jsonb,
    tools_or_frameworks jsonb not null default '["Insufficient data."]'::jsonb,
    business_keywords jsonb not null default '["Insufficient data."]'::jsonb,
    email_positioning_angle text not null default 'Insufficient data.',
    country_specific_email_tone text not null default 'Insufficient data.',
    proof_points_to_use jsonb not null default '["Insufficient data."]'::jsonb,
    things_to_avoid jsonb not null default '["Insufficient data."]'::jsonb,
    personalization_guidance jsonb not null default '["Insufficient data."]'::jsonb,
    structured_output jsonb not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint role_country_status_allowed check (
        role_country_status in (
            'ready_for_personalization',
            'role_only_intelligence_used',
            'country_missing',
            'role_missing',
            'role_country_not_supported',
            'industry_refinement_used',
            'seniority_refinement_used',
            'insufficient_data',
            'manual_review_required',
            'role_country_research_failed'
        )
    )
);

create index if not exists idx_role_country_intelligence_campaign_combo
    on role_country_intelligence_results (campaign_id, normalized_role, normalized_country);

create index if not exists idx_role_country_intelligence_prospect
    on role_country_intelligence_results (prospect_id);
