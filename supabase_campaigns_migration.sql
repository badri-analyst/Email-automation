create table if not exists campaigns (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  user_email text not null,
  campaign_name text not null,
  file_name text not null,
  total_emails integer not null default 0,
  sent_count integer not null default 0,
  failed_count integer not null default 0,
  pending_count integer not null default 0,
  status text not null default 'Uploaded'
    check (status in ('Uploaded', 'Processing', 'Completed', 'Failed', 'Partially Completed', 'No Recipients')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table campaigns
  drop constraint if exists campaigns_status_check;

alter table campaigns
  add constraint campaigns_status_check
  check (status in ('Uploaded', 'Processing', 'Completed', 'Failed', 'Partially Completed', 'No Recipients'));

create index if not exists idx_campaigns_user_email on campaigns (user_email);
create index if not exists idx_campaigns_created_at on campaigns (created_at desc);

alter table email_send_results
  add column if not exists user_email text;

create index if not exists idx_email_send_results_user_email on email_send_results (user_email);

create table if not exists campaign_emails (
  id uuid primary key default gen_random_uuid(),
  campaign_id uuid not null references campaigns(id) on delete cascade,
  user_id uuid,
  user_email text not null,
  recipient_email text not null,
  recipient_name text,
  company_name text,
  subject text,
  email_body text,
  status text not null default 'Pending'
    check (status in ('Pending', 'Sent', 'Failed')),
  error_message text,
  row_data jsonb not null default '{}'::jsonb,
  sent_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_campaign_emails_campaign_id on campaign_emails (campaign_id);
create index if not exists idx_campaign_emails_user_email on campaign_emails (user_email);
create index if not exists idx_campaign_emails_status on campaign_emails (status);
