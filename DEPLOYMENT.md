# Hosted Deployment Guide

This project is set up for:

- Frontend: Vercel
- Backend: Render
- Database: Supabase
- Secrets/API keys: backend environment variables only

## 1. Supabase

Create a Supabase project, then run these SQL files in the Supabase SQL editor:

```sql
-- Run each file from the project root:
supabase_candidate_assets_results.sql
supabase_campaigns_migration.sql
supabase_company_research_results.sql
supabase_decision_engine_results.sql
supabase_direct_send_migration.sql
supabase_email_personalization_results.sql -- optional historical generation audit
supabase_personality_analysis_results.sql
supabase_role_country_intelligence_results.sql
```

Copy:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Use the service role key only in Render, never in Vercel.

## 2. Render Backend

Create a Render Web Service from this repo.

Recommended deployment:

- Environment: Docker
- Dockerfile: `backend/Dockerfile`
- Health check path: `/api/health`

Set Render environment variables:

```env
PORT=8080
PYTHON_BIN=/opt/venv/bin/python
FRONTEND_ORIGIN=https://your-vercel-app.vercel.app
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
ROLE_COUNTRY_API_KEY=your_role_country_nvidia_key
ROLE_COUNTRY_AI_MODEL=nvidia/nemotron-mini-4b-instruct
LINKEDIN_RESEARCH_API_KEY=your_linkedin_research_nvidia_key
LINKEDIN_RESEARCH_AI_MODEL=mistralai/mistral-large-3-675b-instruct-2512
COMPANY_RESEARCH_API_KEY=your_company_research_nvidia_key
COMPANY_RESEARCH_AI_MODEL=meta/llama-4-maverick-17b-128e-instruct
COMMUNICATION_SIGNAL_API_KEY=your_communication_signal_nvidia_key
COMMUNICATION_SIGNAL_AI_MODEL=stepfun-ai/step-3.5-flash
EMAIL_WRITING_API_KEY=your_email_writing_nvidia_key
EMAIL_WRITING_AI_MODEL=mistralai/mistral-large-3-675b-instruct-2512
NVIDIA_API_BASE_URL=https://integrate.api.nvidia.com/v1
AI_API_KEY=optional_shared_fallback_key
AI_API_BASE_URL=optional_shared_fallback_base_url
AI_MODEL=optional_shared_fallback_model
GMAIL_CREDENTIAL_ENCRYPTION_KEY=generate_a_32_byte_base64_or_64_character_hex_key
```

After deploy, test:

```text
https://your-render-backend.onrender.com/api/health
```

## 3. Vercel Frontend

Create a Vercel project from the same repo.

Settings:

- Root directory: `frontend`
- Framework preset: Vite
- Build command: `npm run build`
- Output directory: `dist`

Set Vercel environment variable:

```env
VITE_API_BASE_URL=https://your-render-backend.onrender.com/api
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_PUBLISHABLE_KEY=your_supabase_anon_or_publishable_key
```

Redeploy after setting the variable.

## 4. API Keys

Module API keys belong only in Render:

```env
ROLE_COUNTRY_API_KEY=
LINKEDIN_RESEARCH_API_KEY=
COMPANY_RESEARCH_API_KEY=
COMMUNICATION_SIGNAL_API_KEY=
EMAIL_WRITING_API_KEY=
NVIDIA_API_BASE_URL=https://integrate.api.nvidia.com/v1
```

Gmail App Passwords are entered by users in the Candidate Profile page. They are sent only to the Render backend over HTTPS, encrypted, and stored in Supabase. Do not add Gmail credentials to Vercel.

Do not put these in:

- `frontend/.env`
- Vercel variables
- browser code

## 5. Localhost Not Required

After hosted deployment, users open only:

```text
https://your-vercel-app.vercel.app
```

The frontend calls:

```text
https://your-render-backend.onrender.com/api
```
