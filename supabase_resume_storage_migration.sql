-- Add resume storage path to candidate_assets_results
alter table candidate_assets_results
  add column if not exists resume_storage_path text not null default '',
  add column if not exists resume_filename text not null default '',
  add column if not exists resume_mime_type text not null default '';

-- Create resumes storage bucket (run this in Supabase Dashboard > Storage or via API)
-- insert into storage.buckets (id, name, public) values ('resumes', 'resumes', false)
-- on conflict do nothing;
