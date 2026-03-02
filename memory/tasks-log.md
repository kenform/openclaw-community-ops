# memory/tasks-log.md

Лог автономных задач. Только факты и артефакты.

---

## Entry Template

### [YYYY-MM-DD HH:mm UTC] Task: <название>
- Owner session: <main/subagent label>
- Context: <коротко>
- Goal: <что должно быть на выходе>
- Actions taken:
  - ...
  - ...
- Artifacts:
  - <path/to/file>
  - <path/to/file>
- Result: ✅ done / ⚠️ partial / ❌ blocked
- Blockers:
  - ...
- Next step:
  - ...
- Notes:
  - ...

---

## Example

### [2026-03-02 16:46 UTC] Task: OpenClaw autonomous baseline
- Owner session: main
- Context: Нужна базовая архитектура автономной работы без конфликтов.
- Goal: Создать стабильные файлы политики и лога задач.
- Actions taken:
  - Создан `AUTONOMOUS.md`
  - Создан `memory/tasks-log.md`
- Artifacts:
  - `/home/openclawuser/.openclaw/workspace/AUTONOMOUS.md`
  - `/home/openclawuser/.openclaw/workspace/memory/tasks-log.md`
- Result: ✅ done
- Blockers:
  - Нет
- Next step:
  - Подключить ежедневный цикл (10:00 план, 08:00 отчёт)
- Notes:
  - Рекомендуется один управляющий оркестратор и ограничение фоновых задач до 3.

