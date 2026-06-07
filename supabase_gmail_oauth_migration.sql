-- Gmail OAuth2 credential migration
--
-- No schema change is required. The existing gmail_credentials table stores the
-- encrypted refresh_token in the encrypted_app_password / encryption_iv /
-- encryption_tag columns that were previously used for the SMTP App Password.
--
-- If you are migrating from the SMTP (App Password) setup, existing rows will
-- stop working because the stored value is no longer an App Password but a
-- refresh token. Users must re-connect via the new "Connect Gmail" OAuth flow.
--
-- To force a clean slate you can run:
--   truncate table gmail_credentials;
--
-- If you want to keep the table but mark old rows as stale, you can run:
--   alter table gmail_credentials add column if not exists auth_method text not null default 'oauth2';
--   update gmail_credentials set auth_method = 'smtp_app_password' where auth_method = 'oauth2';
--   -- Then truncate or delete smtp_app_password rows before users reconnect.

-- Optional: add an auth_method column for auditability
alter table gmail_credentials add column if not exists auth_method text not null default 'oauth2';
