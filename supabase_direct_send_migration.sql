create table if not exists gmail_credentials (
  id uuid primary key default gen_random_uuid(),
  campaign_id text not null,
  candidate_id text not null,
  gmail_address text not null,
  encrypted_app_password text not null,
  encryption_iv text not null,
  encryption_tag text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (campaign_id, candidate_id)
);

create table if not exists email_send_results (
  id uuid primary key default gen_random_uuid(),
  campaign_id text not null,
  user_email text,
  prospect_id text not null,
  recipient_email text not null,
  subject_line text not null,
  email_body text not null,
  email_generation_status text not null,
  send_status text not null check (send_status in ('sent', 'send_failed')),
  send_reason text not null,
  provider_message_id text,
  sent_at timestamptz,
  structured_output jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_email_send_results_campaign_id on email_send_results (campaign_id);
create index if not exists idx_email_send_results_prospect_id on email_send_results (prospect_id);
create index if not exists idx_email_send_results_user_email on email_send_results (user_email);

-- Migration recommendation:
-- Stop writing review/draft approval records from the application layer.
-- Keep existing email_personalization_results only for historical audit if needed.
