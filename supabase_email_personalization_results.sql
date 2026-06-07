create table if not exists email_personalization_results (
    id uuid primary key default gen_random_uuid(),
    campaign_id text not null,
    prospect_id text,
    subject_line text not null default '',
    subject_type text not null default 'fallback',
    email_body text not null default '',
    email_generation_status text not null,
    email_generation_reason text not null default 'Insufficient data.',
    personalization_used jsonb not null default '{}'::jsonb,
    sources_used jsonb not null default '{}'::jsonb,
    cta_type text not null default 'resume review',
    tone_used text not null default 'professional',
    word_count integer not null default 0,
    manual_review_flag boolean not null default false,
    manual_review_reason text not null default '',
    structured_output jsonb not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint email_generation_status_allowed check (
        email_generation_status in (
            'email_ready',
            'draft_ready',
            'fallback_email_created',
            'manual_review_required',
            'insufficient_data',
            'blocked_invalid_payload',
            'blocked_unsafe_content',
            'email_generation_failed'
        )
    )
);

create index if not exists idx_email_personalization_campaign
    on email_personalization_results (campaign_id);

create index if not exists idx_email_personalization_prospect
    on email_personalization_results (prospect_id);
