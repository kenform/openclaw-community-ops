# Night Progress 2026-03-11

- 2026-03-11 20:22 UTC: Старт. Выбран Parser1. Прочитаны pipeline.py и behavior_layer.py, обнаружено что pipeline.py — alias на bot.py. Начинаю полный аудит bot.py + baseline тесты.
- 2026-03-11 20:26 UTC: Parser1 baseline готов: 10 реалистичных кейсов (`reports/parser1_cases_2026-03-11.json`), метрики до (`parser1-metrics-before.json`) = precision 0.7143 / recall 0.8333.
- 2026-03-11 20:26 UTC: Parser1 исправления (с backup перед каждым патчем):
  1) Исправлена логика `parse_ilya_signal`: EXIT больше не блокируется веткой `is_question`.
  2) EXIT-сообщения по Ilya с валидным asset теперь проходят как SIGNAL (не теряются).
  3) Усилен анти-спам `_has_promo_spam`: promo пропускается только при сильной market-структуре.
  4) Добавлен structural_guard в `parse_generic_signal`, чтобы не пускать шум типа "зайду позже, стоп короткий" без asset/уровней.
  5) Улучшен парсинг Entry/Stop/Target в generic: приоритет keyword-based regex (`от/вход`, `стоп`, `цель/тейк`) вместо наивного nums[0]/nums[1].
- 2026-03-11 20:27 UTC: Parser1 метрики после (`parser1-metrics-after.json`) = precision 1.0000 / recall 1.0000 на 10 кейсах. Сервисы НЕ перезапускались.
- 2026-03-11 20:31 UTC: Parser2 audit завершён. Найдено 14 групп дублей в 99 каналах, усилены scoring/time/emoji/ref-фильтры, добавлен dedup каналов в run_digest. Ссылки `eragon_syndicate_lab` проверены — корректны.
- 2026-03-11 20:32 UTC: Parser3 audit завершён. Критический фикс BASE (`userbot2` вместо `userbot`), дефолтные ссылки переключены на `openclaw_digest`, усилены AI-фильтры против crypto/trading leakage, dedup/time/emoji/ref фильтры синхронизированы.
- 2026-03-11 20:32 UTC: Финальный отчёт сформирован: `reports/night-2026-03-11-final.md`. Сервисы не перезапускались.
