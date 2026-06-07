create table if not exists candidate_assets_results (
    id uuid primary key default gen_random_uuid(),
    campaign_id text not null,
    candidate_id text not null,
    proof_status text not null,
    proof_reason text not null default 'Insufficient supporting proof.',
    linkedin_profile_url text not null default '',
    linkedin_profile_status text not null default 'missing',
    resume_reference jsonb not null default '{}'::jsonb,
    video_assets jsonb not null default '[]'::jsonb,
    portfolio_assets jsonb not null default '[]'::jsonb,
    professional_positioning_summary text not null default 'Insufficient supporting proof.',
    why_relevant_summary text not null default 'Insufficient supporting proof.',
    candidate_proof_snippets jsonb not null default '["Insufficient supporting proof."]'::jsonb,
    asset_types_detected jsonb not null default '[]'::jsonb,
    manual_review_flag boolean not null default false,
    structured_output jsonb not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint proof_status_allowed check (
        proof_status in (
            'proof_ready',
            'partial_proof_available',
            'insufficient_supporting_proof',
            'invalid_asset_link',
            'manual_review_required',
            'proof_processing_failed'
        )
    )
);

create index if not exists idx_candidate_assets_campaign_candidate
    on candidate_assets_results (campaign_id, candidate_id);
