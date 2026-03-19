# Active Tasks

## [2026-03-19-channel-routing-bug-report] Исправить маршрут ответа: посты в канал, не в личный чат
- **Status**: ✅ 完成
- **Requested**: 2026-03-19 04:45 UTC
- **Updated**: 2026-03-19 04:46 UTC
- **Notes**: Пользователь сообщил о повторяющемся баге: контент для канала уходит в личный диалог.
- **Result**: Подтверждено правило маршрута: команды про «свой канал» отправляю в `@Arya_claw`; в личный чат даю только подтверждение/статус.

## [2026-03-19-heartbeat-night-report-0035] Ночной heartbeat-проход (safe-check + сигнал)
- **Status**: ✅ 完成
- **Requested**: 2026-03-19 00:35 UTC
- **Updated**: 2026-03-19 00:36 UTC
- **Notes**: Выполнен ночной maintenance-check по HEARTBEAT.md: safe system check без рестартов/изменений.
- **Result**: Диск/память в норме, failed user units = 0. Обнаружен повторяющийся инцидент: `sudo: a password is required` для `tailscale serve --bg --yes 18789` (каждые ~20 минут, продолжается до 00:05 UTC).

## [2026-03-18-night-excluded-groups-autocleanup] Ночной автономный порядок в группах-исключениях (1/2/3/4/6/7)
- **Status**: 🔄 进行中
- **Requested**: 2026-03-18 22:52 UTC
- **Updated**: 2026-03-18 22:52 UTC
- **Notes**: Пользователь поручил после текущей задачи, ночью и без дополнительных уточнений, спокойно навести порядок в ранее исключённых группах.
- **Result**: Запланировано в safe-режиме: структурный аудит → мягкая чистка служебки/мусора → навигация/топики по WT-логике → отчёт к утру.

## [2026-03-18-master-hub-bootstrap] Подключиться к новой мастер-группе и развернуть базовую структуру
- **Status**: 🔄 进行中
- **Requested**: 2026-03-18 22:49 UTC
- **Updated**: 2026-03-18 22:53 UTC
- **Notes**: Пользователь дал команду «Делай» на следующий этап после bootstrap.
- **Result**: Запускаю миграцию 1→1 из старых групп в WT Master Hub (без удаления источников), с checkpoint/resume.

## [2026-03-18-garbage-clean-pass] Почистить мусор/системные сообщения в рабочих группах
- **Status**: ✅ 完成
- **Requested**: 2026-03-18 22:43 UTC
- **Updated**: 2026-03-18 22:44 UTC
- **Notes**: Пользователь попросил убрать мусор, системные и служебные хвосты.
- **Result**: Выполнен безопасный cleanup-pass по рабочему контуру (с сохранением исключений 1/2/3/4/6/7): обработано 6 групп, найдено 16 кандидатов, удалено 16, ошибок 0. Отчёт: `reports/garbage_clean_pass_1773873873.json`. `userbot.service` возвращён в `active`.

## [2026-03-18-wt-structure-phase15] Этап 1.5: добавить единый вход (навигационные посты) в оставшиеся группы
- **Status**: ✅ 完成
- **Requested**: 2026-03-18 22:42 UTC
- **Updated**: 2026-03-18 22:43 UTC
- **Notes**: Пользователь подтвердил запуск этапа 1.5.
- **Result**: Выполнено: опубликованы 3 навигационных поста в оставшихся группах (`BAS`, `Мой спот`, `Отработки зоны 141-161`) в якорных управляющих топиках. Ошибок нет. Отчёт: `reports/wt_phase15_nav_1773873781.json`. `userbot.service` возвращён в `active`.

## [2026-03-18-wt-structure-phase1] Этап 1 WT-структуры: создать служебные топики и навигацию (без удалений)
- **Status**: ✅ 完成
- **Requested**: 2026-03-18 22:24 UTC
- **Updated**: 2026-03-18 22:34 UTC
- **Notes**: Пользователь подтвердил запуск этапа 1 по логике WT.
- **Result**: Выполнено для 5 групп (разрешённый контур без 1/2/3/4/6/7): создано 16 новых служебных топиков, размещены 2 навигационных поста (в группах, где целевой топик `🧭 Навигатор` предусмотрен), удалений не выполнялось. Отчёт: `reports/wt_phase1_structure_1773873299.json`. `userbot.service` возвращён в `active`.

## [2026-03-18-group-consolidation-plan] Оценить консолидацию похожих групп в одну мастер-группу
- **Status**: ✅ 完成
- **Requested**: 2026-03-18 22:23 UTC
- **Updated**: 2026-03-18 22:23 UTC
- **Notes**: Пользователь спросил, есть ли общая инфа и стоит ли сделать одну группу с объединённым содержанием вместо нескольких старых.
- **Result**: Подготовлен план консолидации: создавать 1 мастер-форум имеет смысл для пересекающихся потоков (Spot/TW/BAS/Отработки), но удалять старые группы только после миграции ядра (топики+навигация+проверка ссылок+7-дневный буфер).

## [2026-03-18-topic-structure-audit] Проверить, нужны ли новые топики/структура по контексту групп (по логике WT)
- **Status**: 🔄 进行中
- **Requested**: 2026-03-18 22:21 UTC
- **Updated**: 2026-03-18 22:21 UTC
- **Notes**: Пользователь запросил валидацию: достаточно ли текущей чистки, и нужно ли создавать новые топики по контексту групп.
- **Result**: В процессе (делаю структурный аудит групп и предлагаю план наведения порядка уровня WT).

## [2026-03-18-interactive-heavy-confirm] Добавить интерактивный Y/N-порог перед тяжёлыми задачами
- **Status**: ✅ 完成
- **Requested**: 2026-03-18 22:16 UTC
- **Updated**: 2026-03-18 22:17 UTC
- **Notes**: Пользователь подтвердил включение подтверждения перед тяжёлыми AI-запросами.
- **Result**: Реализовано в `/home/openclawuser/userbot/bot.py`: для тяжёлых запросов (`>1600` симв.) `ask_openclaw` теперь требует подтверждение (`[upstream confirm required ...]`), если не активировано окно подтверждения. Добавлена команда управления `.heavy y|n|status`; `.heavy y` открывает окно на 10 минут (`HARD_ECON_CONFIRM_WINDOW_SEC`, default 600). `userbot.service` перезапущен и `active` (`NRestarts=0`).

## [2026-03-18-groups-inventory-for-cleanup] Собрать список доступных групп для следующего этапа уборки
- **Status**: ✅ 完成
- **Requested**: 2026-03-18 22:15 UTC
- **Updated**: 2026-03-18 22:19 UTC
- **Notes**: Пользователь попросил продолжить наведение порядка и сначала дать список видимых групп.
- **Result**: Сформирован инвентарь по последнему maintenance-циклу (`reports/sort_groups_maintenance_cycle_v3_1773493360.json`): 12 целевых групп в контуре «Сортировать»: `2025 Pro Defi`, `2025 БАЗА Defi`, `БАЗА и ПРО 2023`, `ДОП DEFI 24`, `Общак Спот`, `Материалы`, `Syndicate`, `BAS`, `TW`, `Мой спот`, `Отработки зоны 141-161`, `Уроки Вайкофа в картинках`. По новому запросу выполнен targeted-cleanup с исключениями (1,2,3,4,6,7): обработаны `Общак Спот`, `BAS`, `TW`, `Мой спот`, `Отработки зоны 141-161`, `Уроки Вайкофа в картинках`; отчёт `reports/sort_groups_targeted_cleanup_1773872359.json` (кандидатов на удаление: 0, удалено: 0).

## [2026-03-18-hard-economy-mode] Включить жёсткий режим экономии лимитов
- **Status**: ✅ 完成
- **Requested**: 2026-03-18 22:14 UTC
- **Updated**: 2026-03-18 22:16 UTC
- **Notes**: Пользователь подтвердил запуск жёсткого режима экономии.
- **Result**: Включено: (1) строгие AI-лимиты в `/home/openclawuser/userbot/ai_limits.json` (`max_input_chars=1800`, `max_calls_per_hour=40`, `max_calls_per_source_per_hour=12`, `dedup_ttl_min=180`), (2) hard-economy guardrails в `/home/openclawuser/userbot/bot.py` для `ask_openclaw`: блок абсолютного контекста `>5000`, блок больших запросов при расходе `>=85%` и `>1600` символов, (3) параметры режима добавлены в `/home/openclawuser/userbot/config.env`. `userbot.service` перезапущен: `active`, `NRestarts=0`.

## [2026-03-18-limits-optimization-rollout] Внедрить экономию лимитов и базовый трекер расходов
- **Status**: ✅ 完成
- **Requested**: 2026-03-18 22:11 UTC
- **Updated**: 2026-03-18 22:13 UTC
- **Notes**: Пользователь прислал промпт по экономии лимитов и мониторингу порогов.
- **Result**: Применён безопасный rollout: (1) ранее снижена нагрузка digest (`interval_minutes=240`, 20 каналов, `DIGEST_MAX_CHANNELS_PER_RUN=10`), (2) создан файл трекера `/home/openclawuser/.ari_limits_tracker.json`, (3) в `/home/openclawuser/userbot/bot.py` добавлен учёт rough token usage на каждом `ask_openclaw` + пороговые алерты 15/30/50/70/85/95 в Telegram owner. `userbot.service` перезапущен и active (`NRestarts=0`).

## [2026-03-18-lifeos-status-and-resource-fix] Уточнить статус Life OS и снизить расход лимитов на «Сортировать»
- **Status**: ✅ 完成
- **Requested**: 2026-03-18 22:06 UTC
- **Updated**: 2026-03-18 22:08 UTC
- **Notes**: Пользователь сообщил, что старые группы удалены, и попросил объяснить права + исправить перерасход ресурсов.
- **Result**: Подтверждено: `ChannelPrivateError` по старым source-группам в Life OS ожидаем и прав больше не требуется, если миграция завершена. Для снижения нагрузки оптимизирован `userbot`: backup `digest_config.json.bak_20260318T2208Z`, список каналов в `/home/openclawuser/userbot/digest_config.json` сокращён до 20 целевых, `interval_minutes` увеличен до 240, в `/home/openclawuser/userbot/config.env` снижено `DIGEST_MAX_CHANNELS_PER_RUN=10`; `userbot.service` перезапущен и `active` (`NRestarts=0` после запуска).

## [2026-03-18-arya-manual-test-post] Опубликовать тестовый ручной пост в @Arya_claw в новом авторском стиле
- **Status**: ✅ 完成
- **Requested**: 2026-03-18 22:04 UTC
- **Updated**: 2026-03-18 22:05 UTC
- **Notes**: Пользователь подтвердил «Хочу» на тестовый ручной пост после фикса бага формата.
- **Result**: Тестовый авторский пост опубликован в `@Arya_claw`, `message_id=121`.

## [2026-03-18-arya-channel-style-bugfix] Исправить баг: в @Arya_claw публикуется парсерный контент вместо авторских мыслей
- **Status**: ✅ 完成
- **Requested**: 2026-03-18 21:58 UTC
- **Updated**: 2026-03-18 21:59 UTC
- **Notes**: Пользователь указал на неправильный тип контента в канале Арьи. Нужен фикс формата и источника постов.
- **Result**: Исправлено в `/home/openclawuser/userbot2/bot.py`: добавлен отдельный режим для `publish_chat=@Arya_claw` — теперь scheduler публикует авторские рефлексивные посты Арьи (без SOURCE/дайджеста/чужих ссылок), а не парсерный digest. Добавлены guardrails на запрещённые маркеры (`Источник/Главное/Ссылки/дайджест`) + безопасный fallback-текст. `userbot2.service` перезапущен, статус `active`, `NRestarts=0`.

## [2026-03-18-services-health-and-bugfix] Проверить все сервисы и мягко исправить сбои без поломок
- **Status**: ✅ 完成
- **Requested**: 2026-03-18 20:49 UTC
- **Updated**: 2026-03-18 21:05 UTC
- **Notes**: Выполнен безопасный health-check (`openclaw status`, `systemctl --user`, `journalctl`) без рестартов по месту, затем мягкие фиксы багов.
- **Result**: Все ключевые сервисы активны и enabled: `openclaw-gateway`, `telegram-obsidian`, `telegram-pipeline-v1`, `userbot`, `userbot2` (везде `NRestarts=0`, failed units=0). Найдены 2 проблемы: (1) `tailscale serve` в gateway периодически падает из-за отсутствия sudo-прав у `openclawuser`; (2) LifeOS raw-migrate падал traceback при `ChannelPrivateError`. Исправлено (2): в `/home/openclawuser/userbot/lifeos_raw_migrate.py` и `/home/openclawuser/userbot/lifeos_raw_batch.py` добавлена безопасная обработка `ChannelPrivateError` с JSON-отчётом вместо крэша. Проверка пройдена: migrate теперь завершает работу корректно и отдаёт структурированный отчёт с `error=source_channel_private`.
- **Next**: Пользователь отложил tailscale-fix до завтра (ожидаем запуск 2 sudo-команд вручную на хосте).

## [2026-03-18-lifeos-finish-pass] Доделать контур Life OS (добивка миграции + проверка)
- **Status**: ⚠️ 阻塞
- **Requested**: 2026-03-18 19:23 UTC
- **Updated**: 2026-03-18 19:24 UTC
- **Notes**: Пользователь попросил «по Life OS доделать, что делали». Выполнен safe-pass проверки и попытка raw-copy миграции.
- **Result**: Блокер доступа: все 3 исходника (`Дисциплина=-1003540600872`, `Здоровье=-1003259431494`, `Финансы=-1002989342111`) возвращают `ChannelPrivateError` (нет доступа/возможен бан для текущей Telegram-сессии userbot). Из-за этого добивка новых сообщений сейчас невозможна. Destination `Life OS` доступен, топики живы: `🧠=142`, `💪=41`, `💸=24` сообщений. Для продолжения нужен возврат доступа к исходным чатам (реинвайт userbot-аккаунта) или новые source ID/ссылки.

## [2026-03-18-2w-status-and-channel-resume] Сводка за 2 недели + возобновить ведение канала @Arya_claw
- **Status**: ✅ 完成
- **Requested**: 2026-03-18 19:18 UTC
- **Updated**: 2026-03-18 19:19 UTC
- **Notes**: Пользователь запросил: (1) полный статус по задачам за 2 недели, (2) отдельно отложенные/недоделанные, (3) снова вести канал «как прежде».
- **Result**: Сформирована сводка по `memory/tasks.md` (период 2026-03-05..2026-03-18). Автопостинг в `@Arya_claw` возвращён: в `/home/openclawuser/userbot2/digest_config.json` выставлено `enabled=true`, `interval_minutes=120`, `jitter_minutes=7`, `publish_chat=@Arya_claw`; `userbot2.service` перезапущен и `active/running` (`NRestarts=0`).

## [2026-03-14-lifeos-raw-migration] Запустить перенос в Life OS в режиме raw copy only
- **Status**: 🔄 进行中
- **Requested**: 2026-03-14 06:46 UTC
- **Updated**: 2026-03-14 09:22 UTC
- **Notes**: Пользователь подтвердил запуск: переносить голосовые/медиа как есть, без расшифровки. Фоновые сессии `grand-ocean` и `calm-fjord` завершились без финального отчёта.
- **Result**: Есть частичный прогресс в checkpoint `/home/openclawuser/userbot/lifeos_migration_state.json` (для источника Дисциплина уже сохранены ID до 60, `updated_at=1773472646`). Файлы `lifeos_migration_last_report.json` и `lifeos_migration_crash.json` отсутствуют. `userbot.service` сейчас `active/running`.

## [2026-03-14-arya-channel-manual-post] Опубликовать пост в канал @Arya_claw по команде пользователя
- **Status**: ✅ 完成
- **Requested**: 2026-03-14 06:43 UTC
- **Updated**: 2026-03-14 06:49 UTC
- **Notes**: Пользователь дал прямую команду «Пост сделай».
- **Result**: Опубликован новый пост в `@Arya_claw`, message_id `115`.

## [2026-03-14-lifeos-final-pass] Финальный прогон Life OS (добивка + контроль)
- **Status**: ✅ 完成
- **Requested**: 2026-03-14 08:21 UTC
- **Updated**: 2026-03-14 11:14 UTC
- **Notes**: Пользователь запросил финальный прогон. Выполнена добивка хвоста Дисциплина + cleanup технически битых media (`application/octet-stream`) после подтверждённой доставки корректных voice-версий. Затем выполнен контрольный аудит Life OS и собран сводный отчёт.
- **Result**: Финальный дожим Дисциплина завершён (`tracked_ids=216`). Чистка `🧠 Дисциплина`: найдено `130` и удалено `130` octet-stream сообщений (`/home/openclawuser/userbot/lifeos_reports/1773486674_Дисциплина_cleanup_octet_stream.json`). Финальный аудит: `reports/lifeos_final_audit_1773486844.json`, `reports/lifeos_final_report_1773486844.md` (сводка: msgs=264, dupes=44, broken_links=0, tech_empty=9).

## [2026-03-14-lifeos-topic-nav] Сделать навигацию в каждом топике под его контекст
- **Status**: ✅ 完成
- **Requested**: 2026-03-14 08:07 UTC
- **Updated**: 2026-03-14 08:10 UTC
- **Notes**: По команде пользователя созданы контекстные nav-посты внутри Life OS топиков (с подборкой актуальных ссылок по теме).
- **Result**: Созданы посты: `🧠` id 225 (8 refs), `💪` id 226 (8 refs), `💸` id 227 (3 refs), `🎯` id 228 (1 ref), `📊` id 229 (0 refs).

## [2026-03-14-openclaw-news-check] Проверить OpenClaw News: навигация/ссылки/состояние
- **Status**: ✅ 完成
- **Requested**: 2026-03-14 06:42 UTC
- **Updated**: 2026-03-14 06:47 UTC
- **Notes**: Проверен канал `@openclaw_digest` (OpenClaw Parser) через Telethon, просмотрены последние публикации и шаблоны ссылок; проверен текущий publishing-target (`@Arya_claw`) и статус news-сервиса.
- **Result**: В последних сообщениях `@openclaw_digest` битых ссылок не найдено (паттерны `None/undefined` отсутствуют). По запросу пользователя выполнено восстановление навигации: опубликован новый nav-пост и закреплён (`message_id=13`). Финальная проверка 30 последних сообщений: `broken_link_patterns=0`, структура канала валидна; служебное сообщение `MessageActionPinMessage` (id=14) подтверждает успешный pin.

## [2026-03-14-transfer-log-check] Проверить финальный статус переноса tide-crustacean
- **Status**: ✅ 完成
- **Requested**: 2026-03-14 06:40 UTC
- **Updated**: 2026-03-14 06:44 UTC
- **Notes**: Поднят лог старой сессии `/home/openclawuser/.openclaw/agents/main/sessions/3e88f8de-189a-4039-95c9-99bbf92ec668.jsonl`, проверены записи `process list/poll/kill` и текущее состояние PID/сервиса.
- **Result**: Перенос `tide-crustacean` был жив ~7 минут, затем сессия пропала (на `kill` ответ: `No active session found`). Финального JSON-отчёта из скрипта нет; файл состояния `/home/openclawuser/userbot/lifeos_migration_state.json` отсутствует. Это указывает, что полный проход не завершился/оборвался до сохранения прогресса. `userbot.service` при этом сейчас `active/running`.
- **Update**: Пользователь уточнил правило: голосовые не расшифровывать при миграции, только пересылать raw (forward/copy media as-is).

## [2026-03-14-arya-channel-autopost-start] Запустить автопостинг в канал @Arya_claw
- **Status**: ✅ 完成
- **Requested**: 2026-03-14 06:40 UTC
- **Updated**: 2026-03-14 06:42 UTC
- **Notes**: Сделаны backup конфигов userbot2 перед правками; переключён target-паблишинг на канал Арьи и включён интервальный автопостинг.
- **Result**: `DIGEST_PUBLISH_CHAT=@Arya_claw`, ссылки канала обновлены, в `digest_config.json` выставлено `interval_minutes=120` и `jitter_minutes=7`; `userbot2.service` перезапущен и работает (`active/running`, `NRestarts=0`).

## [2026-03-14-parser-autonomy-check] Поднять и проверить все парсеры после перезапуска агента
- **Status**: ✅ 完成
- **Requested**: 2026-03-14 06:40 UTC
- **Updated**: 2026-03-14 06:41 UTC
- **Notes**: Проверены user services, относящиеся к парсерам/пайплайнам: `telegram-obsidian`, `telegram-pipeline-v1` (крипто-парсер), `userbot`, `userbot2`.
- **Result**: Все 4 сервиса `enabled + active/running`, политика `Restart=always`, рестартов в текущем окне нет (`NRestarts=0`). Дополнительный подъём не потребовался.

## [2026-03-14-heartbeat-0200] Heartbeat-проверка по NIGHT protocol
- **Status**: ✅ 完成
- **Requested**: 2026-03-14 02:00 UTC
- **Updated**: 2026-03-14 02:01 UTC
- **Notes**: Выполнен безопасный ночной срез: проверены daily note, диск/память, failed user services и последние user-level ошибки journalctl.
- **Result**: Найден повторяющийся инцидент: регулярные ошибки `sudo: a password is required` для команды `tailscale serve --bg --yes 18789` (каждые ~20–25 минут с 19:40 UTC до 01:30 UTC). Критичных отказов user services не выявлено.

## [2026-03-13-upscale-demo-autonomous-v1] Автономное тестирование открытия позиций в Upscale Demo по регламенту V1
- **Status**: 🔄 进行中
- **Requested**: 2026-03-13 06:25 UTC
- **Updated**: 2026-03-13 06:34 UTC
- **Notes**: Пользователь подтвердил автономный режим B, риск 0.25% от депозита на сделку (по стопу), осторожный human-like темп и новое правило TP для RR 1:3 (SL 0.25% / TP 0.75%). Выполнен первый автономный прогон: BTC/USD, Market Long, сумма 50 USD (x5), стоп выставлен вручную 64,229, позиция открыта и отображается в `Позиции` со статусом `SL`.
- **Result**: Контур открытия/валидации работает. Продолжаю последовательные тесты на ETH/SOL/HYPE/AXS с обязательными SL+TP.

## [2026-03-13-vps-trading-agent-deploy] Подготовка автономного деплоя trading-agent на VPS по mega-промпту
- **Status**: 🔄 进行中
- **Requested**: 2026-03-13 06:39 UTC
- **Updated**: 2026-03-13 06:52 UTC
- **Notes**: Пользователь подтвердил приоритет B (сразу переключиться), дал токен нового бота, owner id и канал отчётов. Файлы из inbound успешно разложены в `/home/openclawuser/trading-agent`, создан venv, зависимости установлены, права `config.env=600`. В конфиг внесены `TRADING_BOT_TOKEN`, `OWNER_TG_ID`, `TRADING_REPORT_CHAT`.
- **Result**: Блокер: отсутствуют реальные `UPSCALE_DEMO_EMAIL` и `UPSCALE_DEMO_PASSWORD` (в шаблоне placeholder), поэтому полноценный тест логина/торгового цикла и запуск сервиса отложен до получения этих двух значений.

## [2026-03-12-elven-post-285-fix] Починить повторы и сломанные ссылки в Elven автопостинге
- **Status**: ✅ 完成
- **Requested**: 2026-03-12 16:30 UTC
- **Updated**: 2026-03-12 16:38 UTC
- **Notes**: Добавлен freshness-guard в `elven_ai_lab_poster_bot.py`: публикация только по заметкам не старше `MAX_NOTE_AGE_HOURS` (из env). В env добавлено `MAX_NOTE_AGE_HOURS=48`.
- **Result**: Постер больше не берёт старые «уникальные» записи за пределами окна свежести; логика повторов дополнительно ужесточена.

## [2026-03-12-userbot2-quiet-hardening] Тихий hardening userbot2 (без изменения логики)
- **Status**: ✅ 完成
- **Requested**: 2026-03-12 16:58 UTC
- **Updated**: 2026-03-12 17:00 UTC
- **Notes**: Сделан backup `/home/openclawuser/userbot2/bot.py.bak_20260312T1700Z`; добавлено quiet-логирование для Telethon transport logger (`telethon.network.connection.connection`/`mtprotosender` -> ERROR) и health-marker запись в `health_summary.json` при событиях. Логика задач/публикаций не менялась.
- **Result**: `userbot2.service` перезапущен и активен/running; шум reconnect-сообщений снижен, контур сохранён без функциональных изменений.

## [2026-03-12-pipeline-format-payload-hotfix] Починить TypeError format_payload(timestamp=...) в parser1
- **Status**: 🔄 进行中
- **Requested**: 2026-03-12 16:51 UTC
- **Updated**: 2026-03-12 16:56 UTC
- **Notes**: Запущен контрольный live-check по запросу пользователя (15–20 минут после фикса).
- **Result**: Наблюдаю логи parser1 на живом трафике.

## [2026-03-12-parser-health-report] Дать health-report по парсерам (24ч, аптайм, ошибки, последний успех)
- **Status**: ✅ 完成
- **Requested**: 2026-03-12 15:20 UTC
- **Updated**: 2026-03-12 15:21 UTC
- **Notes**: Собраны live-метрики по `telegram-pipeline-v1`, `userbot`, `userbot2` (systemd status + journalctl 24ч + последние успешные события).
- **Result**: Отчёт передан: все сервисы active/running; pipeline активен с частыми drops по нерелевантным source/topic, userbot/userbot2 имеют периодические reconnection/рестарты, критических падений контура не обнаружено.

## [2026-03-12-openclaw-news-recovery] Восстановить поток публикаций в OpenClaw News безопасно
- **Status**: ⏸️ 暂停
- **Requested**: 2026-03-12 10:55 UTC
- **Updated**: 2026-03-12 13:49 UTC
- **Notes**: Приостановлено новым приоритетом пользователя (система второго мозга Obsidian+Telegram).
- **Result**: Вернусь после закрытия новой задачи.

## [2026-03-12-telegram-obsidian-vault-cleanup] Безопасная очистка и структурирование Obsidian vault
- **Status**: ✅ 完成
- **Requested**: 2026-03-12 14:08 UTC
- **Updated**: 2026-03-12 14:25 UTC
- **Notes**: Выполнен pass №2: создан `90 MOC/MOC - Vault Home.md`, проставлены дополнительные `Related`-ссылки в оставшихся orphan заметках; проверена legacy-структура (дополнительных перемещений не потребовалось).
- **Result**: orphan notes снижены до 0 (в рабочем контуре, excluding `90 Archive/auto-clean`), структура и MOC-кластер завершены.

## [2026-03-12-telegram-obsidian-second-brain] Развернуть Telegram -> Obsidian second brain с автозапуском
- **Status**: ✅ 完成
- **Requested**: 2026-03-12 13:49 UTC
- **Updated**: 2026-03-12 13:55 UTC
- **Notes**: Использован vault `/home/openclawuser/vault`; созданы недостающие папки (включая `00 Inbox/voice`). Сервис обновлён: text ingest, `/idea /note /task`, voice->Whisper, команды `/digest /review /search /ask`, встроенный Markdown RAG и авто-rebuild индекса после каждой новой заметки.
- **Result**: `telegram-obsidian.service` активен (running), автозапуск включён, резервная копия кода: `/home/openclawuser/telegram_to_obsidian.py.bak_20260312T1354Z`.

## [2026-03-12-voice-3550-transcribe] Расшифровать входящее голосовое 3550
- **Status**: ✅ 完成
- **Requested**: 2026-03-12 10:50 UTC
- **Updated**: 2026-03-12 10:51 UTC
- **Notes**: Выполнена локальная транскрипция Whisper (`tiny`), качество среднее из-за шума/дикции.
- **Result**: Смысл: пользователь просит срочно проверить, почему в канале OpenClaw News мало постов, сделать мониторинг по последним ~100 постам/источникам, пересобрать список отслеживаемых источников и опубликовать хорошие материалы, чтобы канал/группа не были пустыми.

## [2026-03-11-night-3parsers-autonomy] Ночной автономный аудит и улучшение 3 парсеров до утра
- **Status**: 🔄 进行中
- **Requested**: 2026-03-11 20:21 UTC
- **Updated**: 2026-03-12 08:31 UTC
- **Notes**: По запросу пользователя продолжаю в safe-режиме «ничего не ломать». Выполнены read-only проверки: `userbot` и `telegram-pipeline-v1` active/running. Подтверждён источник сбоя digest: `payme99` (`UsernameInvalidError`) в `userbot_events.jsonl`.
- **Result**: Сделан безопасный фикс без рестартов: создан backup `digest_config.json.bak_20260312T0831Z`, из `digest_config.json` удалён невалидный источник `payme99`; наблюдаю следующий цикл digest.

## [2026-03-11-openclaw-safe-skills-rollout] Осторожно дооснастить агента skills-ами без поломки gateway/userbot
- **Status**: ⚠️ 阻塞
- **Requested**: 2026-03-11 19:47 UTC
- **Updated**: 2026-03-11 19:49 UTC
- **Notes**: Шаги 1–3 выполнены: статус снят, backup создан, список skills получен. На шаге 4 первая же команда `openclaw skills enable coding-agent` завершилась ошибкой CLI (`too many arguments`), т.к. в текущей версии доступно только `skills list/check/info`.
- **Result**: Остановлено по регламенту при первой ошибке; изменений в конфиге/сервисах нет, откат не потребовался. Нужен выбор совместимого пути (через `npx clawhub`/ручная установка или апдейт OpenClaw).

## [2026-03-11-bookflow-open-long-btc] Открыть Long BTC на demo с заданными SL/TP и риском 0.25%
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 19:55 UTC
- **Updated**: 2026-03-11 20:07 UTC
- **Notes**: После подтверждения пользователя TP обновлён до 71000 (с полной очисткой поля), ордер отправлен кнопкой Long.
- **Result**: Позиция открыта: `0.031135 BTC`, `x5`, Margin `439.02 USD`, Entry `~70,504`, Liq `56,972.9`; во вкладке Positions отображается `1` активная позиция, в Orders — `2` (TP/SL).

## [2026-03-11-btc-price-check-web] Найти текущую цену BTC в USD без использования открытой вкладки
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 20:12 UTC
- **Updated**: 2026-03-11 20:12 UTC
- **Notes**: Веб-поиск недоступен из-за лимита кредитов, использован прямой публичный API CoinGecko.
- **Result**: BTC/USD ≈ 70,479 USD на момент запроса (вне вкладки).

## [2026-03-11-btc-price-check] Найти текущую цену BTC в USD
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 20:11 UTC
- **Updated**: 2026-03-11 20:11 UTC
- **Notes**: Снята live-цена с открытой вкладки bookflow/Upscale.
- **Result**: На момент проверки BTC/USD ≈ 70,448.8 USD (цена рыночная, меняется в реальном времени).

## [2026-03-11-tab-review-live] Изучить открытую вкладку и описать содержимое
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 19:45 UTC
- **Updated**: 2026-03-11 19:46 UTC
- **Notes**: Получен snapshot активной вкладки через Browser Relay (bookflow trade terminal).
- **Result**: Передан краткий разбор интерфейса: рынок BTC/USD, график, вкладка Positions без открытых позиций, форма ордера Long/Short и предупреждение о scheduled maintenance.

## [2026-03-11-session-startup-sequence] Выполнить стартовую инициализацию новой сессии и приветствие
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 19:33 UTC
- **Updated**: 2026-03-11 19:33 UTC
- **Notes**: Прочитаны обязательные контекстные файлы (SOUL/USER/daily/MEMORY где доступно), подготовлено приветствие в заданной персоне.
- **Result**: Сессия синхронизирована; готова к работе по новому запросу.

## [2026-03-11-bookflow-tab-review] Изучить открытую вкладку bookflow.sh и описать данные/кнопки/позиции
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 19:31 UTC
- **Updated**: 2026-03-11 19:45 UTC
- **Notes**: Повторный snapshot через Chrome relay успешно получен; вкладка `BTC/USD` на `app.bookflow.sh`, активен таб `Positions`.
- **Result**: Подтверждено: открытых позиций нет (`There are no open positions at the moment`), доступен полный торговый интерфейс (Market/Limit/Stop, Long/Short, плечо x1–x5, TradingView-график 5m, блок Position info, баланс demo 10,000 USD).

## [2026-03-11-language-coach-lite15] Дать «ленивую» версию языковой тренировки на 15 минут
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 19:31 UTC
- **Updated**: 2026-03-11 19:31 UTC
- **Notes**: Пользователь подтвердил, что хочет облегчённый режим на дни с низкой энергией.
- **Result**: Отправляю готовый copy-paste шаблон Lite-15 (EN+CN) для поддержания непрерывности без перегруза.

## [2026-03-11-language-coach-template] Дать готовый ежедневный шаблон Language Coach 30/10
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 19:00 UTC
- **Updated**: 2026-03-11 19:00 UTC
- **Notes**: Пользователь подтвердил "хочу" на запрос готового ежедневного шаблона.
- **Result**: Отправляю copy-paste шаблон (EN 30 + CN 10) с автопроверкой, трекингом и форматами ответа.

## [2026-03-11-language-coach-setup] Запустить внедрение агента Language Coach 30/10
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 18:56 UTC
- **Updated**: 2026-03-11 18:59 UTC
- **Notes**: Пользователь выбрал идею №5 и подтвердил время ежедневного языкового блока: 12:00.
- **Result**: Зафиксирован запуск режима EN/CN 30/10 с ежедневной доставкой в 12:00; отправляю 7-дневный план старта.

## [2026-03-11-voice-3448-transcribe] Расшифровать входящее голосовое 3448
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 15:56 UTC
- **Updated**: 2026-03-11 15:58 UTC
- **Notes**: Выполнена локальная транскрипция Whisper (`tiny`), качество среднее.
- **Result**: Смысл извлечён: пользователь хочет в будущем довести агента до полуавто/авто-исполнения на demo-счёте Upscale по сигналам из парсера/топиков и/или по заданной торговой системе/лимиткам, чтобы снизить влияние эмоций; на текущем этапе готов к схеме «агент готовит информацию + выставляет лимитки на demo по правилам».

## [2026-03-11-voice-3438-transcribe] Расшифровать входящее голосовое 3438
- **Status**: ✅ 完成 (отменено)
- **Requested**: 2026-03-11 15:48 UTC
- **Updated**: 2026-03-12 08:07 UTC
- **Notes**: Пользователь прислал новое голосовое после уточнения, что ранее имелось в виду другое сообщение.
- **Result**: Отменено по запросу пользователя 2026-03-12; повторная отправка голосового не требуется.

## [2026-03-11-trading-journal-podcast] Подготовить развёрнутый подкаст-разбор по анализу торгового журнала
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 15:38 UTC
- **Updated**: 2026-03-11 15:40 UTC
- **Notes**: Пользователь просит развернуть тему для всех: анализ торгового журнала в контексте типичных проблем трейдеров и практического решения.
- **Result**: Даны готовые тезисы и структурированный скелет подкаста (проблемы трейдеров → рамка журнала → цикл улучшений → 7-дневный план внедрения).

## [2026-03-11-ai-strategist-plan] Сгенерировать персональный AI-план (3 секции)
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 16:44 UTC
- **Updated**: 2026-03-11 16:45 UTC
- **Notes**: Пользователь подтвердил "давай" после intake.
- **Result**: Выдан персональный план: (1) простое AI-применение + 10 промптов + 3 делегируемые задачи; (2) 3 пошаговых workflow; (3) 3–5 идей агентной автоматизации под OpenClaw/трейдинг/новости/дневник.

## [2026-03-11-ai-strategist-intake] Запустить intake как AI workflow strategist
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 15:19 UTC
- **Updated**: 2026-03-11 16:40 UTC
- **Notes**: Пользователь задал формат работы: начать с 5 фиксированных вопросов, затем уточнять по одному вопросу за раз и построить персональные AI-рекомендации/воркфлоу/агент-автоматизации. Доп. требование: всегда отвечать пользователю на русском языке.
- **Result**: Intake завершён. Ключевые вводные: перегруз/дефицит отдыха/кризис идей; узкие места — анализ графиков, новости (10–20 каналов), настройка OpenClaw и структурирование данных; сделки ведутся через Google Forms -> Google Sheets, но нет общего итога дня. Предпочтения: утренняя выжимка 10:00 (кратко+действия), вечерний итог 22:00 (короткий+полный), запуск с завтра; трейдинг-вектор — demo полуавтомат с ручным подтверждением и риском 0.25% на сделку; языки — 40 мин/день (EN 30 + CN 10). Следующий шаг: предложить сгенерировать персональный план из 3 секций.

## [2026-03-11-wyckoff-topics-status-check] Проверить текущий статус парсера топиков Wyckoff
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 14:52 UTC
- **Updated**: 2026-03-11 14:54 UTC
- **Notes**: Выполнена безопасная проверка без рестартов: systemd status, runtime config (`config.json`), journald, tail `signals.jsonl`.
- **Result**: Парсер активен и стабилен (`active/running`, `NRestarts=0`), topic-filter включён, backfill выключен. По логам фильтр отсекает неразрешённые источники/топики (`Dropped source not configured`) и обрабатывает разрешённые сообщения (есть свежие pipeline/forward события).

## [2026-03-11-night-mode-knowledge-ops] Включить ночной режим: чистка/классификация/сводки/безопасные микро-улучшения
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 14:49 UTC
- **Updated**: 2026-03-12 08:31 UTC
- **Notes**: Закрыто по запросу пользователя как отчётная задача.
- **Result**: Отчёт: выполнен безопасный ночной контур (без рискованных рестартов/глубоких переписок), зафиксированы ключевые сигналы по парсерам (фильтрация источников в pipeline и `UsernameInvalidError` в digest), дальнейшие действия перенесены в приоритетную задачу `2026-03-11-night-3parsers-autonomy`.

## [2026-03-11-voice-3392-transcribe] Расшифровать входящее голосовое 3392
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 09:54 UTC
- **Updated**: 2026-03-11 09:55 UTC
- **Notes**: Выполнена локальная транскрипция Whisper (`tiny`), качество среднее из-за шумов/дикции.
- **Result**: Смысл извлечён: пользователь сегодня занимался Obsidian и доработкой 2 парсеров (оптимизация/стабилизация/фиксы), сейчас один контур парсит каналы, второй — топики; дальше план — протестировать и, вероятно, расширять парсинг после стабилизации.

## [2026-03-11-voice-3391-transcribe] Расшифровать входящее голосовое 3391
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 09:52 UTC
- **Updated**: 2026-03-11 09:55 UTC
- **Notes**: Получено новое voice-сообщение (ogg/opus). Первая попытка `turbo` прервана по времени (SIGTERM), успешная транскрипция выполнена моделью `tiny`.
- **Result**: Смысл извлечён: пользователь тестирует voice, автоматизировал учёт сделок через Google Form -> Excel/таблицу со статистикой, доволен упрощением и делает акцент на дисциплине заполнения без переусложнения.

## [2026-03-11-brand-name-meaning] Объяснить полный смысл названия Eragon Syndicate Lab
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 09:44 UTC
- **Updated**: 2026-03-11 09:45 UTC
- **Notes**: Пользователь попросил объяснить, как понимать всё название целиком.
- **Result**: Дана расшифровка каждого слова + общий смысл бренда и тон позиционирования.

## [2026-03-11-brand-term-syndicate] Объяснить значение слова «синдикат»
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 09:44 UTC
- **Updated**: 2026-03-11 09:44 UTC
- **Notes**: Пользователь спросил, что означает термин в контексте брендинга.
- **Result**: Дано простое объяснение: объединение сильных участников/команд для общей цели; в бренде подчёркивает координацию, силу и стратегию.

## [2026-03-11-brand-final-pick] Помочь выбрать финальное название без перегруза
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 06:37 UTC
- **Updated**: 2026-03-11 09:43 UTC
- **Notes**: Пользователь сообщил, что не может выбрать из нескольких вариантов, затем подтвердил «Ок».
- **Result**: Финально зафиксировано название `Eragon Syndicate Lab`; выдаю комплект: username + bio + слоган.

## [2026-03-11-note-eragon-names] Добавить в заметки названия бренда
- **Status**: ✅ 完成
- **Requested**: 2026-03-11 06:32 UTC
- **Updated**: 2026-03-11 06:33 UTC
- **Notes**: Пользователь прислал 3 варианта названия и попросил добавить их в заметки.
- **Result**: Сохранено в Obsidian заметку `Obsidian-Telegram-KB/00_Inbox/2026-03-11__brand-name-ideas.md`.

## [2026-03-10-remove-psybot-legacy] Безопасно удалить старый psybot_api проект
- **Status**: ✅ 完成
- **Requested**: 2026-03-10 18:45 UTC
- **Updated**: 2026-03-10 18:45 UTC
- **Notes**: По просьбе пользователя удалён legacy psybot_api без риска: сначала disable/stop/reset-failed юнит, затем файлы перемещены в корзину (recoverable), не через rm.
- **Result**: Перемещено в `/home/openclawuser/.Trash/old_projects_cleanup_20260310_184552`; `psybot-api.service` now not-found/inactive; `telegram-pipeline-v1.service` active.

## [2026-03-10-pipeline-output-evelina-dryrun] Dry-run фиксы telegram-pipeline-v1 (output + Evelina parser)
- **Status**: ✅ 完成
- **Requested**: 2026-03-10 08:22 UTC
- **Updated**: 2026-03-12 08:31 UTC
- **Notes**: Закрыто по запросу пользователя как отчётная задача.
- **Result**: Отчёт: dry-run контур с safe-caption fallback был выполнен ранее; финально подтверждено рабочее состояние сервиса `telegram-pipeline-v1` (active/running), но качество выдачи зависит от корректности allowlist источников (в логах есть `Dropped (source not configured)`).

## [2026-03-09-portfolio-revive-vercel-3181] Реанимировать портфолио-сайт и подготовить деплой на Vercel
- **Status**: ✅ 完成
- **Requested**: 2026-03-09 17:03 UTC
- **Updated**: 2026-03-09 18:19 UTC
- **Notes**: Выполнены техправки по проекту Portfolio: cleanup импортов, mobile baseline `@media (max-width: 768px)` блоки в SCSS, фиксы путей Header/Footer, `.env` для CI eslint, commit/push в main.
- **Result**: Последний коммит `f7d799c` (`fix: code cleanup and mobile optimization`) запушен в `origin/main`.

## [2026-03-09-behavior-layer-3124] Доделать behavior layer и выдать полный отчёт
- **Status**: ⏸️ 暂停
- **Requested**: 2026-03-09 15:51 UTC
- **Updated**: 2026-03-12 08:31 UTC
- **Notes**: По текущему решению пользователя задача временно заморожена («5 — не знаю») до отдельного подтверждения приоритета.


## [2026-03-09-portfolio-local-run] Проверить локальный запуск сайта из github.com/kenform/Portfolio (без старта)
- **Status**: ✅ 完成
- **Requested**: 2026-03-09 15:43 UTC
- **Updated**: 2026-03-09 17:00 UTC
- **Notes**: Репозиторий клонирован в `/home/openclawuser/.openclaw/workspace/Portfolio`. Проверена структура: `package.json`, `public/index.html`, `src/`, CRA README.
- **Result**: Стек — React (Create React App, `react-scripts`). Команда запуска: `npm install` (если зависимости не установлены) и `npm start`. Порт по умолчанию: `3000` (`http://localhost:3000`).

## [2026-03-09-disable-userbot-parser-3041] Временно отключить parser-контур userbot (~100 каналов)
- **Status**: ✅ 完成 (реверс выполнен)
- **Requested**: 2026-03-09 09:53 UTC
- **Updated**: 2026-03-09 17:02 UTC
- **Notes**: По новому запросу пользователя старый parser возвращён в обычный режим.
- **Result**: В `/home/openclawuser/userbot/digest_config.json` выставлен `enabled=true`; `userbot.service` enabled+active/running.


## [2026-03-09-pipeline-hardening-checklist] No-history + dedupe + cache + auto-restart + flow/usage/TV confirmation
- **Status**: ✅ 完成
- **Requested**: 2026-03-09 08:21 UTC
- **Updated**: 2026-03-09 08:24 UTC
- **Notes**: В `telegram-pipeline-v1` добавлена защита `skip_duplicate_message` с persistent cache последних 500 ключей `chat_id:message_id` (`memory.json`). Добавлен явный flow-log при старте и reconnect backoff/streak protection для Telethon decode glitches.
- **Validation**: Логи подтверждают `Backfill enabled=False`, flow line присутствует, сервис active после рестарта, memory current ~46MB, RSS ~58MB, TasksCurrent=1.

## [2026-03-09-evelina-implicit-stop] Добавить implicit stop/invalidation для профиля Эвелины
- **Status**: ✅ 完成
- **Requested**: 2026-03-09 07:35 UTC
- **Updated**: 2026-03-09 07:38 UTC
- **Notes**: Реализовано правило для `trader_id in {evelina, eli}`: при фразах `нельзя терять|если потеряем|если не удержим|нужно/надо/важно удержать|не должны терять|ниже нельзя|ниже не уходить` ближайший уровень интерпретируется как `invalidation_level` и выводится как `Stop`.
- **Result**: В generic signal добавлены поля `invalidation_level`, `stop_inferred`; в storage JSONL теперь пишутся `stop`, `invalidation_level`, `stop_inferred`.

## [2026-03-09-unified-layer-and-backfill] Unified behavior-layer + backfill 20x per topic
- **Status**: 🔄 进行中 (приоритет)
- **Requested**: 2026-03-09 07:08 UTC
- **Updated**: 2026-03-09 08:13 UTC
- **Notes**: Пользователь поднял задачу в приоритет. Дополнительно по запросу: остановлен и disabled `userbot.service` (широкий парсер по ~100 каналам), оценена его ресурсная/лимитная нагрузка.
- **Result (interim)**: `userbot` inactive+disabled; исторически memory peak ~50–62MB, CPU time по рестартам низкий. В userbot_events.jsonl за 24ч доминируют `collect_channel_posts_error`/`telethon_decode_error`; вызовы `ask_openclaw_*` почти отсутствуют в последние сутки, значит расход GPT-кредитов по этому парсеру сейчас минимальный.
- **Patch applied**: в `/home/openclawuser/userbot/bot.py` исправлен критичный контур стабильности: `collect_channel_posts` теперь пробрасывает исключение вверх (чтобы `fetch_channel_posts_safe` включал backoff/auto-mute вместо тихого флуда), добавлен skip для пустых prompt (`ask_openclaw_skip_empty_prompt`), и усилен cooldown для decode/RPC ошибок.

## [2026-03-09-topic-backfill-20x] Прогон 20 последних сообщений по whitelisted топикам и отправка PASS в каналы
- **Status**: ⚠️ 阻塞
- **Requested**: 2026-03-09 07:08 UTC
- **Updated**: 2026-03-09 07:16 UTC
- **Notes**: Запущен one-shot backfill-скрипт `/tmp/topic_backfill_send.py` по whitelisted runtime topics.
- **Blocker**: Telethon `TypeNotFoundError` (Constructor ID `9815cec8`) при чтении истории `iter_messages`, из-за чего скрипт падает до завершения 20x per-topic цикла.
- **Result**: Отчёт по allowlist готов; массовый backfill-send не завершён из-за decode-glitch Telegram API.

## [2026-03-09-topic-autopost-check] Проверка автопостинга из топиков в канал по последним сообщениям
- **Status**: ✅ 完成
- **Requested**: 2026-03-09 07:03 UTC
- **Updated**: 2026-03-09 07:08 UTC
- **Notes**: Проверены runtime-конфиг, актуальные логи pipeline, dryrun_report и tail signals.jsonl.
- **Result**: Применено по уточнению: включён whitelist-only режим по нужным топикам (`TOPIC_FILTER_ENABLED=true`) и задан список разрешённых topic IDs (Irina/Psy/Altador/Evelina/Ilya/Artur). Выполнен controlled restart `telegram-pipeline-v1.service`; конфиг подхватился: `Topic filter: enabled=True ...` и runtime IDs резолвятся корректно.

## [2026-03-09-night-window-apply] Применить оптимизации в тихое окно ночью с 04:00
- **Status**: ⏸️ 暂停
- **Requested**: 2026-03-09 05:44 UTC
- **Updated**: 2026-03-09 05:45 UTC
- **Notes**: Пользователь подтвердил применение изменений в ночное окно. Нужна фиксация таймзоны и даты запуска (сегодня/завтра), затем выполнить controlled restart/checklist.

## [2026-03-09-monitor-3005] Мониторинг системы каждые 10 минут + мягкий автофикс без рестартов
- **Status**: ⏸️ 暂停
- **Requested**: 2026-03-09 07:26 UTC
- **Updated**: 2026-03-09 14:33 UTC
- **Background**: watchdog process stopped by user request during full restart sequence.
- **Notes**: После подтверждения пользователя выполнен controlled restart стека и остановка фонового watchdog (как часть «поставить текущие задачи на стоп»).
- **Result**: `userbot.service active/running`, `openclaw-gateway.service active/running`, `gateway probe ok=true`.

## [2026-03-09-full-restart-3089] Поставить задачи на стоп и перезапустить систему (без ломки)
- **Status**: ✅ 完成
- **Requested**: 2026-03-09 13:06 UTC
- **Updated**: 2026-03-09 14:33 UTC
- **Notes**: По прямому подтверждению пользователя выполнен безопасный рестарт рабочего стека без reboot ОС.
- **Result**: Остановлен фон `watchdog_10m_softfix.sh`; перезапущены `openclaw-gateway.service` и `userbot.service`; обе службы в `active/running`, `NRestarts=0`, probe успешный.

## [2026-03-09-token-saver-night-3050] Ночью включить режим экономии лимита GPT
- **Status**: 🔄 进行中
- **Requested**: 2026-03-09 10:07 UTC
- **Updated**: 2026-03-09 10:08 UTC
- **Notes**: Пользователь подтвердил включение «эконом-режима» ночью: короткие ответы по умолчанию, минимум промежуточных отчётов, алерты только по важному, детализация по запросу «подробно».

## [2026-03-09-obsidian-note-2986] Добавить в Obsidian заметку по интерпретации мыслей (зоны/стопы)
- **Status**: ✅ 完成
- **Requested**: 2026-03-09 05:42 UTC
- **Updated**: 2026-03-09 05:43 UTC
- **Notes**: Пользователь попросил зафиксировать в Obsidian: мысль «зоны нельзя терять» интерпретировать как правило постановки стопа.
- **Result**: Создана заметка `/home/openclawuser/.openclaw/workspace/Obsidian-Telegram-KB/00_Inbox/2026-03-09__мысли-зоны-и-стопы.md` с интерпретацией и шаблоном действий (вход/invalidation/стоп/риск%).


## [2026-03-09-capacity-forecast] Оценить нагрузку 1+2 parser и порог апгрейда сервера
- **Status**: ✅ 完成
- **Requested**: 2026-03-09 05:23 UTC
- **Updated**: 2026-03-09 05:39 UTC
- **Notes**: Пользователь уточнил 2 активных parser. Проведена быстрая проверка `psybot_api`: это отдельный aiogram MVP для /scan и записи в storage; `.env` пустой, при этом service с `Restart=always`, из-за чего шёл цикл рестартов.
- **Result**: Выполнено: `psybot-api` заморожен (`systemctl --user disable --now`, status=inactive/disabled). В `userbot` внедрены runtime-ограничители GPT (max_input_chars, hourly quota global/source, dedup TTL, quota/dedup event logging) через `ai_limits.json` без принудительного рестарта. Для parser-v1 добавлен шаблон `projects/telegram-pipeline-v1/limits.json`. Изменения в workspace закоммичены (`7b70edb`).

## [2026-03-09-userbot-live-check-opt] Проверить и оптимизировать userbot без остановки текущих задач
- **Status**: ✅ 完成
- **Requested**: 2026-03-09 05:20 UTC
- **Updated**: 2026-03-09 05:23 UTC
- **Notes**: Выполнена live-диагностика: userbot active/running, 1 процесс, lock на session корректный, память ~53MB, CPU низкий, открытых FD ~36. В логах повторяющиеся Telethon `TypeNotFoundError` (каналы/диффы), но сервис не падает. Обнаружены внешние рестарты в 05:06/05:10 UTC (не моё действие).
- **Result**: Применена безопасная runtime-оптимизация без остановки задач: снижен приоритет конкурирующего `telegram-pipeline-v1` до nice=5, userbot оставлен на nice=0 для лучшей отзывчивости.

## [2026-03-09-post-dedup-2966] Проверить защиту от одинаковых постов в userbot
- **Status**: ✅ 完成
- **Requested**: 2026-03-09 05:09 UTC
- **Updated**: 2026-03-09 05:11 UTC
- **Notes**: Проверен и усилен антидубль в `userbot/bot.py`: (1) `digest_post_history` теперь хранит нормализованный текст и ловит near-duplicate (SequenceMatcher >= 0.93), а не только exact hash; (2) добавлен structure-guard для channel publish — блокирует multi-card payload с повторяющимися секциями `Источник/Главное`.
- **Result**: userbot перезапущен, `active/running`, `NRestarts=0`. Повторы одинаковых/почти одинаковых дайджестов и «склейка из нескольких карточек» теперь должны отсекаться до публикации.


## [2026-03-09-quick-health-2958] Быстрая проверка userbot/sessions/logs/cache
- **Status**: ✅ 完成
- **Requested**: 2026-03-09 05:04 UTC
- **Updated**: 2026-03-09 05:08 UTC
- **Notes**: Выполнен read-only срез + точечный hardening по подтверждению пользователя: `openclaw gateway probe`, фикс PATH (`~/.local/bin/openclaw` symlink), обновлён обработчик `TypeNotFoundError` в `userbot/bot.py` (без гигантского дампа байт, с ctor-id), перезапуск `userbot.service`.
- **Result**: gateway probe `ok=true`; userbot после рестарта `active/running`, `NRestarts=0`; openclaw CLI доступна по PATH в shell. Корневая причина decode-ошибок Telethon полностью не устранена (ошибки связаны с конкретными каналами/разницей updates), но reconnect-loop стабилизирован и лог-шум снижен для новых срабатываний. Пользователь подтвердил: пока без ре-авторизации и без изоляции/mute каналов.


## [2026-03-09-night-report-2956] Запрошен отчёт по ночному автономному прогону
- **Status**: 🔄 进行中
- **Requested**: 2026-03-09 05:03 UTC
- **Updated**: 2026-03-09 05:06 UTC
- **Background**: tender-prairie (pid 1962859) on localhost — `night full run checks + dry-run + journald snapshot`
- **Notes**: Пользователь подтвердил запуск полного прогона. Запущен цикл: stability/crash-protection → cleanup TTL/limits → voice/transcription hardening check → TradingView rules verification → dry-run tests → metrics/log/storage safety.

## [2026-03-08-watchdog-3h] Мониторинг состояния каждые 15 минут в течение 3 часов + авто-ремонт
- **Status**: 🔄 进行中
- **Requested**: 2026-03-08 19:51 UTC
- **Updated**: 2026-03-08 19:51 UTC
- **Background**: keen-shell (pid 1754026) on localhost — `scripts/watchdog_3h.sh`
- **Notes**: Пользователь запросил 3-часовой цикл watchdog (15m): проверка зависаний/статусов сервисов и авто-починка при зависании. Первый watchdog отработал 2 цикла и завершился раньше ожидания; перезапущен новый watchdog в 20:27 UTC. Зафиксирован флап `psybot-api` (auto-restart), выполнен ручной restart, состояние `active/running`.


## [2026-03-08-userbot-parser-check] Проверить работу userbot и второго parser
- **Status**: ✅ 完成
- **Requested**: 2026-03-08 17:58 UTC
- **Updated**: 2026-03-08 21:04 UTC
- **Notes**: По запросу пользователя "Хочу" выполнен точечный hardening userbot без влияния на остальные сервисы: в `userbot/bot.py` для `TelegramClient` включены `auto_reconnect`, `sequential_updates`, повышены retry-параметры (`connection_retries`, `request_retries`, `retry_delay`). После этого `userbot.service` перезапущен.
- **Result**: userbot после hardening: `active/running`, `NRestarts=0`. Ошибки `TypeNotFoundError` ранее в логах были, но после свежего рестарта в текущем окне проверок новых падений не зафиксировано.


## [2026-03-08-night-openclaw-update] Ночной системный апдейт OpenClaw с sudo
- **Status**: 🔄 进行中
- **Requested**: 2026-03-08 17:48 UTC
- **Updated**: 2026-03-08 17:52 UTC
- **Notes**: Пользователь дал разрешение на ночной системный апдейт (sudo) и подтвердил окно выполнения: 04:00–06:00 (ночью, МСК). План: backup конфига/версии -> `npm i -g openclaw@latest` -> `openclaw doctor` -> controlled `openclaw gateway restart` -> post-check (`openclaw health --json`, systemd status).


## [2026-03-08-post-format-filter] Настроить фильтр и формат постов для канала parser
- **Status**: 🔄 进行中
- **Requested**: 2026-03-08 17:38 UTC
- **Updated**: 2026-03-08 18:04 UTC
- **Notes**: Пользователь начал этап фильтрации и оформления постов. Добавлен двухконтурный Ilya-only режим (MAIN+SIGNAL), JSON rules, классификация/парсер и dry-run отчёт.

## [2026-03-08-wyckoff-topics-lock] Зафиксировать pipeline: только группа и 6 topic_id, добавить медиа-отправку
- **Status**: ✅ 完成
- **Requested**: 2026-03-08 17:23 UTC
- **Updated**: 2026-03-08 17:36 UTC
- **Notes**: Зафиксирован режим group-only + topic filter, backfill off; каналы остаются видимыми, но sender игнорирует. Добавлена отправка photo/video/voice/document с caption/fallback.
- **Result**: Сервис активен после перезапуска, ограничения применены.

## [2026-03-08-evening-status-check] Проверить статус сервера, OpenClaw и userbot (память/очереди/кэш)
- **Status**: ✅ 完成
- **Requested**: 2026-03-08 17:31 UTC
- **Updated**: 2026-03-08 17:49 UTC
- **Notes**: По подтверждению пользователя выполнены безопасные фиксы без ломания текущих задач: (1) userbot уже ранее укреплён reconnect-loop и остаётся стабильным; (2) добавлена ежедневная авто-чистка inbound media cache через user systemd timer (`openclaw-inbound-cleanup.timer`, retention 72h, лог в `workspace/logs/inbound-cleanup.log`); (3) контрольные проверки статуса после изменений.
- **Result**: `userbot` active/running (`NRestarts=0`), `openclaw-gateway` active/running (`NRestarts=0`), `openclaw health ok=true`. Таймер чистки включён и активен (следующий запуск завтра ~04:22 UTC). Нерешённое: апдейт OpenClaw до 2026.3.7 упирается в права (`npm -g` EACCES на `/usr/lib/node_modules`) — нужен запуск с повышенными правами или смена способа установки.


## [2026-03-08-spring-landing] Создать новый проект сайта-поздравления и подготовить к деплою
- **Status**: ✅ 完成 (отменено)
- **Requested**: 2026-03-08 05:42 UTC
- **Updated**: 2026-03-12 08:07 UTC
- **Notes**: Отменено по запросу пользователя 2026-03-12; ожидание токена в окружении остановлено.
- **Result**: Задача закрыта как неактуальная.

## [2026-03-08-voice-2513] Расшифровать и ответить на голосовое сообщение (msg 2513)
- **Status**: ✅ 完成
- **Requested**: 2026-03-08 05:26 UTC
- **Updated**: 2026-03-08 05:27 UTC
- **Notes**: Транскрипция получена, но с шумами/искажениями. Пользователю дано подтверждение намерения (начать делать «дорогой» сайт) и запрос на уточнение референса/структуры.

## [2026-03-08-voice-mode] Переключить режим распознавания voice на приоритет скорости
- **Status**: ✅ 完成
- **Requested**: 2026-03-08 05:38 UTC
- **Updated**: 2026-03-08 05:38 UTC
- **Notes**: Пользователь выбрал режим «быстрее»; в дальнейших ответах держу приоритет latency над идеальной точностью.


## [2026-03-08-voice-2512] Расшифровать и ответить на голосовое сообщение (msg 2512)
- **Status**: ✅ 完成
- **Requested**: 2026-03-08 05:25 UTC
- **Updated**: 2026-03-08 05:26 UTC
- **Notes**: Выполнена транскрипция (качество среднее из-за шумов/распознавания), пользователю дан ответ с подтверждением сути и запросом на уточнение при необходимости.


## [2026-03-08-voice-2495] Расшифровать и проанализировать голосовое сообщение (msg 2495)
- **Status**: ❌ 失败
- **Requested**: 2026-03-08 05:09 UTC
- **Updated**: 2026-03-08 05:10 UTC
- **Notes**: Локальная транскрипция Whisper прервана SIGTERM (две попытки: turbo/tiny). Требуется повторный запуск/альтернативный путь.


## [2026-03-08-stability-check] Проверить стабильность работы OpenClaw/хоста (read-only)
- **Status**: ✅ 完成
- **Requested**: 2026-03-08 05:08 UTC
- **Updated**: 2026-03-08 05:25 UTC
- **Notes**: Выполнены read-only проверки: `openclaw status --deep`, `openclaw health --json`, `openclaw gateway status`, `openclaw update status`, `systemctl --user show/journalctl`, `ps`. Gateway active, NRestarts=0, Telegram probe OK. Найден риск стабильности: зависший `whisper` PID 1337084 + параллельный PID 1339696. По подтверждению пользователя выполнена полная стабилизация: `pkill -f '/whisper( |$)'` + принудительная очистка `pkill -9` для хвостов, затем контрольная верификация. Пользователь подтвердил очистку inbound media cache.
- **Result**: Выполнена безопасная чистка inbound-кэша по правилу `mtime +7 days`: удалений нет (в каталоге 155 файлов, но старше 7 дней — 0). Система стабильна, дисковое использование без изменений.


## [2026-03-07-voice-transcribe-integration-eval] Оценить интеграцию @voice_transcribot и сравнить с текущей расшифровкой
- **Status**: ✅ 完成
- **Requested**: 2026-03-07 09:32 UTC
- **Updated**: 2026-03-07 16:44 UTC
- **Notes**: После жалобы пользователя на дубли/утечки служебного промпта и `AlreadyInConversationError` внесены дополнительные фиксы в autorun: (1) глобальный `VOICEAUTO_LOCK` — только одна автообработка за раз; (2) блокировка повторного запуска при занятости; (3) анти-утечка служебного промпта в финальное сообщение (guard по сигнатурам + безопасный fallback-ответ). Сервис `userbot.service` перезапущен, status=active.
- **Result**: Авто-режим стал стабильнее: без конкурентных коллизий и без публикации служебных шаблонов в чат.
- **Progress**: Пользователь подтвердил `.voiceauto off` (шум автоцепочки остановлен). Следующий шаг — включить чистый ретест после короткой паузы.
- **Hotfix**: После повторного `⚠️ voiceauto: [no final transcript received]` добавлен retry транскрипции (вторая попытка с увеличенным timeout) и отключён вывод ошибок voiceauto в чат; ошибки теперь только в логах.
- **New request**: Пользователь попросил: обработать все неразобранные голосовые, повторно проверить баги/ошибки и убедиться, что очередь не переполнена после большого объёма сообщений.
- **Implemented by request (1/4/5)**: (1) confidence-flag для voiceauto (`🟢/🟡/🟠` в ответе + confidence в логах), (4) anti-duplicate fingerprint (SHA1 аудио + TTL окно, чтобы не отвечать повторно на один и тот же voice), (5) mini-metrics логирование pipeline (`ms_download`, `ms_transcribe`, `ms_analyze`, `ms_total`) в `userbot_events.jsonl`.
- **New request**: Пользователь подтвердил запуск V1 EN-пайплайна (RU voice -> EN transcript/summary/polished). Внедрил команду `.voiceen [literal|natural|business]` (reply-to-voice), использует @voice_transcribot для RU транскрипции и OpenClaw для EN pack; сохраняет в vault/voice и vault/notes. userbot перезапущен, active.
- **Bugfix**: Подтверждена утечка служебного prompt-текста в чат из auto-цепочки. Немедленный mitigation: принудительно выключен `voiceauto` (`voice_auto_state.json: enabled=false`) для прекращения промпт-спама/дублей; оставлены ручные безопасные команды `.voicebot`/`.voiceen`.
- **User question**: Запрошен текущий статус: работает ли расшифровка голосовых сейчас и в каком состоянии EN-пайплайн.
- **Leak hardening**: По запросу пользователя "почини" добавлен анти-утечка guard для `.voiceen`: детект service-prompt текста, авто-fallback перевод без RU service-шаблона, и защитный безопасный шаблон при повторном leak. Дополнительно усилена валидация формата EN-pack (`## EN transcript/summary/polished`) с повторной попыткой и безопасным fallback при невалидном ответе (чтобы не пролетали посторонние ответы в `.en`). userbot перезапущен, active.
- **Regression**: Пользователь сообщил о новом повторе утечки service-prompt в `.en` после фикса; требуется добить источник (вероятно, очередь старых job/response-mix) и перевести `.en` в strict-only output pipeline.
- **Silent mode requested**: По подтверждению пользователя отключено промежуточное сообщение `✅ queued: voiceen (...)` для `.en/.voiceen`; теперь в чат приходит только финальный EN-результат. userbot перезапущен, active.
- **User confirmation**: Пользователь продолжает видеть service-template leak и поручил закрыть все подобные баги ночью. Запланирован ночной hardening: strict response matching, queue isolation, and anti-leak guards until zero template emissions.
- **Priority change**: Пользователь уточнил приоритет на ночь: в первую очередь стабильность и качество русской транскрипции (EN-функция вторична, используется реже).
- **Diagnostic update**: Проверка логов показала: очередь не залита (`queue=0`), но `.voiceen` ловит invalid ответы (response-mix) и из-за fallback-цепочки даёт задержки на коротких ГС. План: ночью изолировать EN-ответы и сократить ретраи/таймауты; RU-контур держать в стабильном режиме.
- **Night run request**: Пользователь попросил ночной автономный прогон (00:00–07:00 МСК): автотесты voice-пайплайна, отлов ошибок/багов без участия пользователя, утром прислать отчёт о фикcах и текущем статусе стабильности.
- **New request**: Добавить в этом чате удобный триггер `.en` (reply на русское голосовое) для получения английской расшифровки прямо сюда, без перехода между чатами.
- **New request**: Пользователь подтвердил запуск второго parser pipeline и попросил пошаговую инструкцию (что именно сделать со своей стороны).
- **Critical bug report**: Пользователь запретил публикацию багового повторяющегося поста (`How To/Tool [unknown] ... Полимаркет — следующие шаги`) и попросил убрать его, найти первопричину повторов и починить публикацию.
- **Clarification**: Сообщение `⚠️ voiceauto: [voice_transcribot: no final transcript received]` пришло до последнего рестарта (16:55 UTC), то есть это старый хвост до hotfix/silent-mode.


## [2026-03-06-diana-core-foundation] diana-core A→B bootstrap и отладка persistent history
- **Status**: 🔄 进行中
- **Requested**: 2026-03-06 12:15 UTC
- **Status**: ✅ 完成
- **Status**: ✅ 完成
- **Updated**: 2026-03-07 01:51 UTC
- **Notes**: По запросу пользователя дожато единообразие формата: удалены остаточные функции/следы старого `Вывод`-блока и legacy-формата в userbot + workspace постер-скрипте. Проверка grep по ключам старого шаблона чистая, userbot перезапущен и активен.


## [2026-03-05-eragon-site] Сделать сайт в стиле Eragon с реферальными кнопками бирж
- **Status**: 🔄 进行中
- **Requested**: 2026-03-05 06:18 UTC
- **Updated**: 2026-03-06 16:28 UTC
- **Notes**: Приоритет по Eragon-сайту выполняется в авто-режиме (branch→push→PR→merge). Выпущен V8 bold redesign по запросу пользователя: полная переработка hero и визуального языка в более cinematic/premium Eragon-inspired стиле, при сохранении структуры link-hub. Дополнительно по новому ТЗ внедрена мягкая система moonlight beams в hero (3 размытых луча, медленный drift/pulse, центр-композиции усилен без потери читаемости текста/CTA), mobile-safe. Изменены `app/page.jsx` и `app/globals.css`, сборка OK.
- **Extra**: По запросу пользователя удалён шаблонный вывод "Вывод: применимо на практике, если внедрить в ближайшие 24 часа." из формата постов userbot (`/home/openclawuser/userbot/bot.py`) и из workspace-скрипта `scripts/elven_ai_lab_poster_bot.py`.

## [2026-03-04-gateway-tailnet-fix] Применить bind=tailnet для openclaw-gateway
- **Status**: ✅ 完成 (отменено)
- **Requested**: 2026-03-04 18:24 UTC
- **Updated**: 2026-03-12 08:07 UTC
- **Notes**: Отменено по запросу пользователя 2026-03-12; возврат к задаче не требуется.
- **Result**: Задача закрыта как неактуальная.

## [2026-03-05-channel-posts] Опубликовать новые посты в @Elven_Ai_Lab
- **Status**: 🔄 进行中
- **Requested**: 2026-03-05 04:38 UTC
- **Updated**: 2026-03-06 08:07 UTC
- **Notes**: Ранее публикации работали (последний post id 127), но пользователь сообщил, что новые посты сейчас не доходят в канал. Диагностика подтвердила: сервис живой, причина была в daily-расписании. По запросу пользователя включён интервальный scheduler в `/home/openclawuser/userbot/bot.py` (`interval_minutes`, `last_run_ts`). Изначально поставлен режим 30 мин, затем по уточнению пользователя скорректирован на `interval_minutes=60` (слишком часто).

## [2026-03-05-eragon-site-next-v3] V3 wow-эффекты (parallax+rune-border+reveal)
- **Status**: ✅ 完成
- **Requested**: 2026-03-05 11:11 UTC
- **Updated**: 2026-03-05 18:40 UTC
- **Notes**: V3 для Next.js сделана, но пользователь решил отказаться от Next.js в пользу статической версии.

## [2026-03-05-userbot-healthcheck-post] Протестировать userbot и опубликовать свежий пост из новых TG-постов
- **Status**: ✅ 完成
- **Requested**: 2026-03-05 20:10 UTC
- **Updated**: 2026-03-05 20:11 UTC
- **Notes**: Проверка пройдена: `userbot.service active`, `NRestarts=0`, критичных ошибок в текущем цикле нет. Свежие посты с каналов проверены, шум отфильтрован, пост опубликован в канал (message_id 127).

## [2026-03-05-next-fantasy-landing] Сгенерировать Next.js+TS+Tailwind+Framer landing (fantasy elf aesthetic)
- **Status**: 🔄 进行中
- **Requested**: 2026-03-05 19:30 UTC
- **Updated**: 2026-03-05 19:30 UTC
- **Notes**: Пользователь запросил готовую структуру проекта и код: app/page.tsx + компоненты ButtonCard/Background + tailwind config + запуск.

## [2026-03-05-eragon-style-from-github] Изучить GitHub kenform и перенести стиль в Eragon-сайт
- **Status**: 🔄 进行中
- **Requested**: 2026-03-05 19:01 UTC
- **Updated**: 2026-03-05 19:18 UTC
- **Notes**: V1 отправлен, пользователь запросил радикальный редизайн. Запускаю V2 в варианте «1» — темнее и пафоснее, с усиленным cinematic hero и премиальными карточками.

## [2026-03-05-eragon-site-static-final] Переключение на статическую версию без Next.js
- **Status**: ✅ 完成
- **Requested**: 2026-03-05 18:40 UTC
- **Updated**: 2026-03-05 18:40 UTC
- **Notes**: Финальный статический архив сайта (HTML/CSS) отправлен пользователю.

## [2026-03-05-eragon-site-next-polish] Улучшение Next.js версии (визуал+анимации+deploy)
- **Status**: ✅ 完成
- **Requested**: 2026-03-05 08:57 UTC
- **Updated**: 2026-03-05 09:00 UTC
- **Notes**: Добавлены фоновые glow-эффекты, микро-анимации карточек/фона, улучшен UX hero/gates, добавлены deploy-конфиги `vercel.json` и `netlify.toml`, обновлён README.
- **Result**: Отправлены 2 новых поста в канал (IDs: 99 и 100). Прямой Bot API probe через `@Elven_post_bot` успешен (message_id 102), тест удалён; userbot stable (NRestarts=0). Дополнительно опубликованы: авто-срез (103), эталонный тест (104), spoiler-тест (105), plain-style тест (107), актуальный пост (108), link-style тест (109) и точный plain-шаблон (110). Фолбэк форматтер зафиксирован под plain-эталон (без markdown-ссылок/spoiler).


## [2026-03-07-agent-systemd-pack] Подготовить готовые .service-файлы для 7-агентной схемы
- **Status**: ✅ 完成
- **Requested**: 2026-03-07 00:36 UTC
- **Updated**: 2026-03-07 00:40 UTC
- **Notes**: Пользователь подтвердил «Да, хочу». Подготовлен комплект из 8 user-systemd юнитов + универсальный runner + инструкция установки и лимитов.
- **Result**: `infra/systemd-user/*.service`, `scripts/oc-role-runner.sh`, `config/agent-commands.env.example`; commit: `782d65f`.

## [2026-03-07-mom-agent-hardening] Настроить mama-agent в безопасном режиме + маршрутизацию
- **Status**: 🔄 进行中
- **Requested**: 2026-03-07 00:48 UTC
- **Updated**: 2026-03-07 00:49 UTC
- **Notes**: Пользователь попросил немягкий тон и максимально безопасную среду, чтобы мама ничего не сломала; запрошен пошаговый план действий.

# Completed (recent)
- [2026-03-13-capabilities-and-user-summary] ✅ Ответил пользователю: кратко описал мои возможности и что уже знаю о нём (русский язык, интерес к трейдингу/крипте, автоматизация, Obsidian, стиль коммуникации).
- [2026-03-05-overnight-ops] ✅ Ночная задача закрыта: userbot стабилен, бэкапы сделаны, end-to-end публикация digest подтверждена (`@Elven_Ai_Lab`, "✨ Главное на сегодня").
- [2026-03-04-gateway-fix] ✅ Починил: удалён systemd override с `--bind tailnet`, выполнены daemon-reload + restart; сейчас `openclaw-gateway.service` stable, `gateway probe` => Reachable yes / RPC ok.
- [2026-03-04-gateway-recheck] ✅ Повторная проверка: Gateway сейчас стабилен и reachable (ws://127.0.0.1:18789, RPC ok, service active, NRestarts=0).
- [2026-03-04-gateway-check] ✅ Диагностика сервера: причина — systemd override запускает `openclaw gateway` с `--bind tailnet`, из-за чего сервис уходит в рестарт (ошибка `gateway.controlUi.allowedOrigins`); хост ресурсы в норме.
