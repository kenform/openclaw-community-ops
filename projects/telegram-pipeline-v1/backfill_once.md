# Backfill one-shot (separate session)

Purpose: run historical backfill without conflicting with live reader session.

## Session isolation
- Live session: `reader_session`
- Backfill session: `backfill_session` (separate file)

## Steps
1. Keep `telegram-pipeline-v1.service` running for live messages.
2. Run backfill script with separate session:

```bash
cd /home/openclawuser/.openclaw/workspace/projects/telegram-pipeline-v1
.venv/bin/python /home/openclawuser/.openclaw/workspace/tmp/topic_backfill_by_ids.py \
  --session /home/openclawuser/.openclaw/workspace/projects/telegram-pipeline-v1/backfill_session
```

3. Wait until report is produced in `/home/openclawuser/.openclaw/workspace/tmp/*report.json`.
4. Stop backfill process (it should exit itself).

## Rules
- Never run backfill with `reader_session`.
- Backfill is one-shot only.
- If decode glitches appear, retry with smaller ID window.
