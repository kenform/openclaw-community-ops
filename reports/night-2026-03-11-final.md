# Night Final Report — 2026-03-11

## A) Parser1 (`projects/telegram-pipeline-v1`)

### Что изучено
- `pipeline.py` (alias-обёртка)
- `behavior_layer.py`
- основной парсинг в `bot.py` (Ilya/Artur/generic)

### Найденные баги/слабые места
1. `parse_ilya_signal`: ветка `EXIT` фактически была частично недостижима/некорректно приоритизирована.
2. EXIT-сообщения (например «закрыл всё по BTC») терялись из-за `has_structure`-гейта.
3. `_has_promo_spam` пропускал часть promo-шума (пример: «взяла место на обучение в VIP...»).
4. `parse_generic_signal` пропускал шум вроде «зайду позже, стоп короткий» без asset/уровней.
5. Потеря структуры Entry/Stop/Target из-за наивного `nums[0]/nums[1]`.

### Изменения (с backup перед каждым патчем)
Файл: `projects/telegram-pipeline-v1/bot.py`
- backup-файлы: `bot.py.bak.20260311T202447Z`, `...T202515Z`, `...T202538Z`, `...T202558Z`, `...T202622Z`

Патчи:
1. Перестроен приоритет `signal_type` в `parse_ilya_signal` (EXIT/HOLD/CONDITIONAL выше неявных веток).
2. Явный `explicit_exit` добавлен в pass-условие для Ilya.
3. Усилен `_has_promo_spam`: promo разрешается только при сильных market-признаках.
4. Добавлен `structural_guard` в generic-парсер (asset/уровни/направление).
5. Улучшен keyword-based парсинг Entry/Stop/Target (`от/вход`, `стоп`, `цель/тейк`).

### Тесты (10 реалистичных кейсов)
- Набор: `reports/parser1_cases_2026-03-11.json`
- До: `reports/parser1-metrics-before.json`
- После: `reports/parser1-metrics-after.json`

**Метрики**
- До: precision **0.7143**, recall **0.8333**
- После: precision **1.0000**, recall **1.0000**

---

## B) Parser2 (`/home/openclawuser/userbot/bot.py`, `@Elven_Ai_Lab`)

### Что проверено
- scoring/dedup/time filter/emoji filter в fallback-ветке digest
- ссылки `eragon_syndicate_lab`
- `digest_config.json` (99 каналов)
- статус каналов по доступным локальным данным (trust/cache/backoff), без агрессивного сетевого скана

### Найдено
- 14 групп дубликатов (case/alias-варианты) в 99 каналах (`unique_norm=85`).
- scoring допускал referral/affiliate noise.
- time-filter был мягким (пропускал недатированные элементы).

### Изменения (с backup перед каждым патчем)
Файл: `/home/openclawuser/userbot/bot.py`
- backup: `bot.py.bak.20260311T202759Z`, `...T202813Z`

Патчи:
1. Дедуп каналов в `run_digest` по `norm_channel(...).lower()`.
2. Расширен `bad_kw` (referral/join/discount паттерны).
3. Добавлен фильтр invite/ref-ссылок (`joinchat`, `t.me/+`, `web3.okx.com/join`, `ref=` и т.п.).
4. Усилен фильтр свежести: отсутствующая дата -> skip, старше 36ч -> skip.
5. Emoji-фильтр сделан адаптивным по длине текста.

### Проверка ссылок
- `ARIA_CHANNEL_LINK` / `ARIA_CHAT_LINK`: оба указывают на `https://t.me/eragon_syndicate_lab` (корректно для parser2).

### Статус 99 каналов (локальные данные)
Артефакт: `reports/parser2-channel-status-2026-03-11.json`
- healthy: 59
- unknown: 12
- duplicate: 28
- problem: 0

---

## C) Parser3 (`/home/openclawuser/userbot2/bot.py`, `@openclaw_digest`)

### Что проверено
- AI-фильтры / bad_kw для отсечения crypto/trading
- `digest_config.json` (10 каналов OpenClaw)
- ссылки на `openclaw_digest`

### Критический баг
- В `userbot2/bot.py` был `BASE = Path.home() / "userbot"` (пересечение состояния с parser2).

### Изменения (с backup перед каждым патчем)
Файл: `/home/openclawuser/userbot2/bot.py`
- backup: `bot.py.bak.20260311T202914Z`, `...T202943Z`, `...T203010Z`, `...T203140Z`

Патчи:
1. Исправлен BASE: `userbot2`.
2. Ссылки/бренд по умолчанию переключены на `https://t.me/openclaw_digest`, `OpenClaw Digest`.
3. Дедуп каналов в `run_digest`.
4. Усилен `bad_kw` против crypto/trading leakage (`entry/stop loss/тейк/маржин/x100` и т.д.).
5. Добавлены referral-link + freshness + adaptive emoji фильтры как в parser2.

### Статус 10 каналов
Артефакт: `reports/parser3-channel-status-2026-03-11.json`
- healthy: 0
- unknown: 10
- duplicate: 0
- problem: 0

(unknown = нет достаточной локальной истории trust/cache; активный сетевой probe не выполнялся по требованию безопасного режима)

---

## Что не исправлено и почему
1. Не делался агрессивный live-check всех каналов через массовые Telegram-запросы, чтобы не поднять риск FloodWait/anti-spam.
2. Не трогал systemd-сервисы (запрещено без крайней необходимости).
3. Не выполнял глубокий runtime E2E запуск digest в прод-чате, чтобы не публиковать тестовый контент ночью.

## Что сделать руками
1. Для parser2: нормализовать `digest_config.json` (убрать case-дубли, оставить 1 каноничное имя на канал).
2. Для parser3: один ручной `/.d` в безопасном окне для warm-up trust/cache после фикса BASE.
3. Пройти 1-2 dry-run digest и проверить, что crypto/referral шум не попадает в итоговый пост.

## Ограничения и безопасность
- Сервисы `userbot.service`, `userbot2.service`, `telegram-pipeline-v1.service` **не перезапускались**.
- Ничего не удалялось (кроме отсутствия временных чисток).
- При каждом изменении файла создавался timestamp backup рядом.
