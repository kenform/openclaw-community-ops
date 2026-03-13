# OpenClaw parser (userbot2) — SAFE MODE изменения

Дата: 2026-03-13

## Сделано
- Созданы бэкапы:
  - `bot.py.bak_20260313_172014_SAFE_MODE`
  - `config.env.bak_20260313_172014_SAFE_MODE`
  - `digest_config.json.bak_20260313_172014_SAFE_MODE`
- В `run_digest` сбор постов изменён на `limit=10` на канал.
- Ослаблен `bad_kw` до явной рекламы/реф/скама.
- Отключён skip по `_is_recent_duplicate_digest` в фильтрации.
- Смягчён финальный low-signal порог: длина `<90` -> `<30`.
- Отключён anti-duplicate skip в `send_digest` (channel publish guard).
- Включён debug print этапов: collected/filtered/publish.
- Добавлен fallback-режим публикации best-effort, если `scored == 0`.
- Публикация в safe-ветке через user-session send.
- Из шаблона удалена строка:
  - `SAFE MODE: публикация почти всех постов после базовой фильтрации рекламы.`

## Проверка
- `python3 -m py_compile bot.py` — OK.
- `userbot2.service` после перезапуска: active.
- Тестовый прогон `run_digest()` выполнялся успешно.

## Примечание
- Публикация в `@openclaw_digest` подтверждалась user-session отправкой.
- Тестовые/служебные посты чистятся отдельно при необходимости.
