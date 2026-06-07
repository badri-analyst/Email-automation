-- =============================================================================
-- Phase 1: gmail_oauth_accounts table
--
-- Purpose:
--   Replaces the single-Gmail-per-campaign constraint in gmail_credentials with
--   a proper per-user, multi-account table.  The existing gmail_credentials table
--   is left untouched so campaigns already in flight continue to work during the
--   transition period (Phase 5 drops it).
--
-- Run this in the Supabase SQL editor (or via psql) before deploying the Phase 2
-- backend changes.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. New table: gmail_oauth_accounts
-- -----------------------------------------------------------------------------

create table if not exists gmail_oauth_accounts (
  id                      uuid        primary key default gen_random_uuid(),

  -- Recruiter identity (from Supabase auth)
  user_id                 uuid        not null,
  user_email              text        not null,

  -- The Gmail address that was actually authorized by Google
  gmail_address           text        not null,

  -- AES-256-GCM encrypted OAuth2 refresh token
  -- Column names are intentionally clearer than the legacy gmail_credentials columns
  encrypted_refresh_token text        not null,
  encryption_iv           text        not null,
  encryption_tag          text        not null,

  -- Account lifecycle
  is_active               boolean     not null default true,
  connected_at            timestamptz not null default now(),
  revoked_at              timestamptz,
  updated_at              timestamptz not null default now(),

  -- One record per Gmail address per user (re-connecting overwrites via upsert)
  unique (user_id, gmail_address)
);

-- -----------------------------------------------------------------------------
-- 2. Indexes
-- -----------------------------------------------------------------------------

-- Fast lookup of all accounts for a given recruiter
create index if not exists idx_gmail_oauth_accounts_user_id
  on gmail_oauth_accounts (user_id)
  where is_active = true;

-- Lookup by login email (used when user_id is not yet available in fallback paths)
create index if not exists idx_gmail_oauth_accounts_user_email
  on gmail_oauth_accounts (user_email);

-- Fast lookup of a specific gmail_address within a user's accounts
create index if not exists idx_gmail_oauth_accounts_gmail_address
  on gmail_oauth_accounts (user_id, gmail_address);

-- -----------------------------------------------------------------------------
-- 3. Row-Level Security
--    Users may only see and modify their own rows.
--    The backend uses the service-role key (bypasses RLS), but enabling RLS
--    is good practice in case direct client queries are ever used.
-- -----------------------------------------------------------------------------

alter table gmail_oauth_accounts enable row level security;

-- Service-role key (used by the backend) always bypasses RLS, so no policy
-- is needed for it.  These policies protect against direct anon/user key access.

create policy "Users can view their own Gmail accounts"
  on gmail_oauth_accounts for select
  using (auth.uid() = user_id);

create policy "Users can insert their own Gmail accounts"
  on gmail_oauth_accounts for insert
  with check (auth.uid() = user_id);

create policy "Users can update their own Gmail accounts"
  on gmail_oauth_accounts for update
  using (auth.uid() = user_id);

-- Deletes are intentionally blocked at the RLS level; the backend soft-deletes
-- via is_active = false and revoked_at so audit history is preserved.

-- -----------------------------------------------------------------------------
-- 4. Back-fill: copy existing gmail_credentials rows into the new table
--    so that users who already connected do not need to re-authorize.
--
--    The legacy table stores the refresh token in encrypted_app_password.
--    candidate_id in that table is the recruiter's Supabase login email.
--
--    NOTE: user_id cannot be back-filled from gmail_credentials because that
--    table does not store the Supabase UUID.  We set user_id to a sentinel
--    value (00000000-0000-0000-0000-000000000000) and populate user_email.
--    The backend will overwrite the row (via upsert on user_id, gmail_address)
--    the next time the user connects, which will set the correct user_id.
--
--    Run this block only if gmail_credentials already has rows you want to
--    preserve.  Safe to skip on a fresh deployment.
-- -----------------------------------------------------------------------------

insert into gmail_oauth_accounts (
  user_id,
  user_email,
  gmail_address,
  encrypted_refresh_token,
  encryption_iv,
  encryption_tag,
  is_active,
  connected_at,
  updated_at
)
select
  '00000000-0000-0000-0000-000000000000'::uuid  as user_id,
  candidate_id                                   as user_email,
  gmail_address,
  encrypted_app_password                         as encrypted_refresh_token,
  encryption_iv,
  encryption_tag,
  true                                           as is_active,
  created_at                                     as connected_at,
  updated_at
from gmail_credentials
on conflict (user_id, gmail_address) do nothing;

-- -----------------------------------------------------------------------------
-- 5. Verification queries — run these after applying the migration to confirm
--    the table was created and the back-fill succeeded.
-- -----------------------------------------------------------------------------

-- Should return the new table with all columns:
-- select column_name, data_type from information_schema.columns
-- where table_name = 'gmail_oauth_accounts' order by ordinal_position;

-- Should return the count of back-filled rows (0 on a fresh deployment):
-- select count(*) from gmail_oauth_accounts;

-- Should return the count of rows from the legacy table for comparison:
-- select count(*) from gmail_credentials;
