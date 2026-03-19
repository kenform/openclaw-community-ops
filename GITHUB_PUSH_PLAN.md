# GitHub Push Plan (Safe)

## What is already done
- Added `.gitignore` with secret/session/venv/node_modules/log/tmp filters.
- Autonomous no-GPT pipeline code is committed locally.

## Your only action needed
1. Create a GitHub repository (empty) and send me its URL.
   - Example: `https://github.com/<you>/<repo>.git`

## What I will do after you send URL
1. Add remote `origin`
2. Create branch `feat/no-gpt-autopipeline`
3. Push current prepared commits
4. Verify no secrets are included
5. Send you compare/PR link

## Optional split into multiple repos
If you want, we can split into:
- `automation-core` (scripts/config/systemd)
- `parsers` (parser projects)
- `content-ops` (reports/docs)

Default recommendation: start with one repo, split later.
