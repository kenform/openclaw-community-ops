---
type: moc
status: active
date: 2026-03-04
tags: [monitoring, research, intelligence, workflow]
---

# MOC — Intelligence Monitor

## Policy
- Level-3 Autonomous Web Research Monitor enabled.
- Limits: 12/day total, 3/source/day.
- Dedup: URL exact + text similarity >80%.
- Uncertain claims must be marked `hypothesis`.

## Storage map
- `00_Inbox` — raw intake
- `10_Channels` — by source
- `20_Summaries` — condensed intelligence
- `90_MOC` — navigation and topic maps

## Outputs
- Daily Intelligence Brief
- Weekly Digest + metrics (X notes / Y ideas / Z voice / W links)
