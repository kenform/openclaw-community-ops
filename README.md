# openclaw-community-ops

Операционный репозиторий для автономного контура OpenClaw:
- Telegram group ops (чистка/дедуп/маршрутизация)
- no-GPT fallback пайплайны (Python + systemd)
- Obsidian housekeeping и структурирование
- Шаблоны процессов для комьюнити, контента и поддержки подписчиков

## Что уже есть
- `scripts/autopipeline_no_gpt.py` — оркестратор no-GPT цикла
- `scripts/tg_no_gpt_worker.py` — Telegram cleanup/maintenance worker
- `scripts/obsidian_no_gpt_cleaner.py` — чистка Obsidian без GPT
- `scripts/subscriber_forms_no_gpt.py` — rule-based обработка форм подписчиков
- `infra/systemd-user/*.service|*.timer` — готовые юниты для автозапуска
- `config/*.json` — настройки пайплайнов

## Быстрый старт
1. Проверь пути в `config/*.json`.
2. Запусти one-shot:
   - `python3 scripts/autopipeline_no_gpt.py`
3. Включи таймеры:
   - `systemctl --user daemon-reload`
   - `systemctl --user enable --now autopipeline-no-gpt.timer`
   - `systemctl --user enable --now obsidian-no-gpt-cleaner.timer`

## Отчёты
Все отчёты пишутся в `reports/` (локально). По умолчанию JSON-отчёты в git игнорируются.

## Безопасность
- Никогда не коммитить `.env`, `config.env`, `*.session`, ключи.
- Перед крупными изменениями — локальный backup.

## Ветки
- `main` — стабильная база
- `feat/*` — рабочие изменения и новые функции
