# Active Tasks

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
- **Night run request**: Пользователь попросил ночной автономный прогон (00:00–07:00 МСК): автотесты voice-пайплайна, отлов ошибок/багов без участия пользователя, утром прислать отчёт о фикcах и текущем статусе стабильности.
- **New request**: Добавить в этом чате удобный триггер `.en` (reply на русское голосовое) для получения английской расшифровки прямо сюда, без перехода между чатами.
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
