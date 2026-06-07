create table if not exists decision_engine_results (
    id uuid primary key default gen_random_uuid(),
    campaign_id text not null,
    prospect_id text,
    decision_status text not null,
    decision_reason text not null,
    next_action text not null,
    selected_research_path text not null,
    selected_personalization_source text not null,
    email_send_permission text not null,
    email_send_block_reason text not null default '',
    manual_review_flag boolean not null default false,
    manual_review_reason text not null default '',
    fallback_used boolean not null default false,
    fallback_reason text not null default '',
    final_personalization_payload jsonb not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint decision_status_allowed check (
        decision_status in (
            'ready_for_email_personalization',
            'ready_for_draft_generation',
            'ready_for_sending',
            'blocked_invalid_email',
            'skipped_duplicate',
            'company_fallback_selected',
            'role_country_only_selected',
            'manual_review_required',
            'insufficient_data',
            'smtp_not_configured',
            'decision_failed'
        )
    ),
    constraint next_action_allowed check (
        next_action in (
            'generate_email',
            'generate_draft',
            'send_email',
            'skip_sending',
            'skip_duplicate',
            'run_company_research',
            'run_role_country_only_personalization',
            'manual_review',
            'stop_processing'
        )
    ),
    constraint email_send_permission_allowed check (
        email_send_permission in ('allowed', 'draft_only', 'blocked')
    )
);

create index if not exists idx_decision_engine_results_campaign
    on decision_engine_results (campaign_id);

create index if not exists idx_decision_engine_results_prospect
    on decision_engine_results (prospect_id);
