# Active Tasks

## [2026-03-09-topic-autopost-check] Проверка автопостинга из топиков в канал по последним сообщениям
- **Status**: ✅ 完成
- **Requested**: 2026-03-09 07:03 UTC
- **Updated**: 2026-03-09 07:08 UTC
- **Notes**: Проверены runtime-конфиг, актуальные логи pipeline, dryrun_report и tail signals.jsonl.
- **Result**: Применено по запросу: в `projects/telegram-pipeline-v1/config.json` отключён фильтр тем (`TOPIC_FILTER_ENABLED=false`), выполнен controlled restart `telegram-pipeline-v1.service` (active). Новая конфигурация подхватилась: `Topic filter: enabled=False`.

## [2026-03-09-night-window-apply] Применить оптимизации в тихое окно ночью с 04:00
- **Status**: ⏸️ 暂停
- **Requested**: 2026-03-09 05:44 UTC
- **Updated**: 2026-03-09 05:45 UTC
- **Notes**: Пользователь подтвердил применение изменений в ночное окно. Нужна фиксация таймзоны и даты запуска (сегодня/завтра), затем выполнить controlled restart/checklist.

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
- **Status**: ⏸️ 暂停
- **Requested**: 2026-03-08 05:42 UTC
- **Updated**: 2026-03-08 05:57 UTC
- **Notes**: Повторная проверка: в текущем процессе по-прежнему `GH_TOKEN/GITHUB_TOKEN` отсутствуют. Вероятно токен задан в другой shell/сессии и не подхватился агентом. Нужна установка переменной в среду процесса OpenClaw (или передача remote URL для ручного push).


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
- **Status**: ⏸️ 暂停
- **Requested**: 2026-03-04 18:24 UTC
- **Updated**: 2026-03-06 11:39 UTC
- **Notes**: Отложено по подтверждению пользователя; вернуться после закрытия приоритета по Eragon-сайту.

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
- [2026-03-05-overnight-ops] ✅ Ночная задача закрыта: userbot стабилен, бэкапы сделаны, end-to-end публикация digest подтверждена (`@Elven_Ai_Lab`, "✨ Главное на сегодня").
- [2026-03-04-gateway-fix] ✅ Починил: удалён systemd override с `--bind tailnet`, выполнены daemon-reload + restart; сейчас `openclaw-gateway.service` stable, `gateway probe` => Reachable yes / RPC ok.
- [2026-03-04-gateway-recheck] ✅ Повторная проверка: Gateway сейчас стабилен и reachable (ws://127.0.0.1:18789, RPC ok, service active, NRestarts=0).
- [2026-03-04-gateway-check] ✅ Диагностика сервера: причина — systemd override запускает `openclaw gateway` с `--bind tailnet`, из-за чего сервис уходит в рестарт (ошибка `gateway.controlUi.allowedOrigins`); хост ресурсы в норме.
