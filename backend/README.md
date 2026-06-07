# AI Outreach Backend

Express API layer for the React frontend. It exposes REST routes for upload, orchestration, module calls, Gmail credential validation, and direct Gmail SMTP sending.

## Setup

```bash
npm install
cp .env.example .env
npm run dev
```

## Environment

```text
PORT=8080
FRONTEND_ORIGIN=http://localhost:5173
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
PYTHON_BIN=python
GMAIL_CREDENTIAL_ENCRYPTION_KEY=
```

`SUPABASE_SERVICE_ROLE_KEY` must stay backend-only. Never expose it through frontend env variables.
`GMAIL_CREDENTIAL_ENCRYPTION_KEY` must also stay backend-only. Use a 32-byte base64 or 64-character hex key in production.

## Direct Gmail Sending

The backend uses Gmail SMTP defaults internally:

- Host: `smtp.gmail.com`
- Port: `465`
- Secure TLS: enabled

Users only provide a Gmail address and Google App Password from the candidate profile form. The app validates the credentials before saving them, encrypts the app password before Supabase storage, and sends generated recruiter emails immediately after email personalization.

Removed workflow:

- Draft review API route
- SMTP settings API route
- Manual send blocking route
- Frontend Drafts page
- Frontend SMTP Settings page

Supabase migration:

```bash
psql "$SUPABASE_DATABASE_URL" -f ../supabase_direct_send_migration.sql
```

## Render

Use:

```bash
npm install
npm start
```

Set `PYTHON_BIN` to the Python runtime that has this project’s Python dependencies installed.
