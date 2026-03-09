# CLAUDE HANDOFF — telegram-pipeline-v1

## Canonical runtime file
- Main runtime is currently: `bot.py`
- Added compatibility alias: `pipeline.py` (re-exports from `bot.py` and calls `main()`)

## Current objective
Implement/finish **Behavior Layer v2** without breaking live pipeline:
1. Artur context-bundle (±3 messages, reply-chain/media adjacency)
2. Unified state semantics (ENTRY/HOLD/EXIT/PARTIAL_EXIT/B_E_UPDATE/STOP_UPDATE/LEVEL_UPDATE/MARKET_VIEW)
3. Routing/debug reasons end-to-end
4. Test-pack examples (PASS MAIN / PASS SIGNAL / DROP per trader)

## Non-negotiable constraints
- Do **not** break existing live service behavior.
- Keep TradingView global rule intact: TV link => MAIN always.
- Keep current signal routing intact unless explicit behavior rule upgrades it.
- Keep `userbot` out of live path; only `telegram-pipeline-v1` is active reader.

## Key files
- `bot.py` — main pipeline logic (Telethon reader + filter + parser + router)
- `pipeline.py` — alias entrypoint (wrapper)
- `config.json` — runtime config, topic allowlist, targets, priority traders
- `sources.json` — source/topic->trader mapping
- `ilya_rules.json` — Ilya-specific rules
- `signals.jsonl` — storage output

## Current configured source mapping
From `sources.json`:
- ilya_topic: chat `-1003398914047`, topics `[14, 58866]`
- artur_channel: chat `-1001699376756`
- artur_topic: chat `-1003398914047`, topics `[13810, 57974]`
- evelina_topic: chat `-1003398914047`, topics `[10, 58990]`
- altador_channel: chat `-1002037215613`
- altador_topic: chat `-1003398914047`, topics `[8, 58829]`
- irina_topic: chat `-1003398914047`, topics `[4, 58926]`
- psy_topic: chat `-1003398914047`, topics `[6, 58567]`

## Priority order
From `config.json`:
`PRIORITY_TRADERS = ["altador", "artur", "evelina", "eli", "ilya"]`

## Already implemented recently
- Human-readable channel post format (hashtags + short text)
- Media sending for charts/videos via `sendDocument` (reduced compression)
- Voice handling: transcribe + summarize to text (no raw voice forward)
- Topic filter + allowlist active
- Duplicate message cache (last 500 keys)
- Reconnect backoff protection for Telethon decode glitches
- Evelina implicit stop/invalidation support in generic parser/storage

## Known pain points to finish
1. **Artur context bundling** is still partial.
2. **Unified state semantics** not fully normalized in one layer.
3. **Debug reasons** from spec not all wired through logs/storage.
4. Some messages drop as `source not configured` (expected for out-of-map topics).

## Suggested implementation shape
- Introduce `build_context_bundle(event, recent_context, window=3)`
- Introduce `normalize_state(text, trader_id, context)` -> standardized state enum
- Introduce `apply_behavior_profile(trader_id, msg, context)` -> behavior-adjusted decisions
- Route decisions via single object:
  - `main_pass: bool`
  - `signal_pass: bool`
  - `state_type: str`
  - `debug_reasons: list[str]`

## Desired debug reasons (target set)
- `TRADER_BEHAVIOR_APPLIED`
- `CONTEXT_BUNDLE_CREATED`
- `IMPLICIT_STOP_INFERRED`
- `TRADINGVIEW_FORCE_MAIN`
- `SIGNAL_FROM_CONTEXT`
- `MAIN_FROM_CONTEXT`
- `HOLD_STATE_DETECTED`
- `EXIT_STATE_DETECTED`
- `B_E_DETECTED`

## Runtime commands
- Service: `systemctl --user status telegram-pipeline-v1.service`
- Restart: `systemctl --user restart telegram-pipeline-v1.service`
- Logs: `journalctl --user -u telegram-pipeline-v1.service -n 200 --no-pager`

## Note on sessions
- Live reader session: `reader_session`
- Backfill must use separate session file (one-shot only)
