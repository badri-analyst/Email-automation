create table if not exists company_research_results (
    id uuid primary key default gen_random_uuid(),
    campaign_id text not null,
    prospect_id text,
    company_name_original text not null default '',
    company_name_cleaned text not null default '',
    company_research_status text not null,
    company_research_reason text not null default 'Insufficient data.',
    company_website text not null default '',
    company_website_status text not null default 'missing',
    company_linkedin_url text not null default '',
    company_research_source_type text not null default 'insufficient_data',
    company_overview text not null default 'Insufficient data.',
    industry text not null default 'Insufficient data.',
    products_services_summary text not null default 'Insufficient data.',
    company_values_summary text not null default 'Insufficient data.',
    recent_company_updates jsonb not null default '[]'::jsonb,
    growth_or_hiring_signal text not null default 'Insufficient data.',
    role_relevance_context text not null default 'Insufficient data.',
    country_relevance_context text not null default 'Insufficient data.',
    company_personalization_hooks jsonb not null default '["Insufficient data."]'::jsonb,
    company_email_angle text not null default 'Insufficient data.',
    manual_review_flag boolean not null default false,
    structured_output jsonb not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint company_research_status_allowed check (
        company_research_status in (
            'ready_for_personalization',
            'company_basic_data_found',
            'recent_news_found',
            'company_values_found',
            'company_fallback_used',
            'company_website_missing',
            'company_not_found',
            'insufficient_data',
            'manual_review_required',
            'company_research_failed'
        )
    ),
    constraint company_website_status_allowed check (
        company_website_status in ('valid', 'invalid', 'inferred', 'missing')
    )
);

create index if not exists idx_company_research_results_campaign_company
    on company_research_results (campaign_id, company_name_cleaned);

create index if not exists idx_company_research_results_prospect
    on company_research_results (prospect_id);
