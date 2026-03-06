# Active Tasks

## [2026-03-06-diana-core-foundation] Пояснить шаг A2 (docker-compose.yml) для diana-core пошагово
- **Status**: 🔄 进行中
- **Requested**: 2026-03-06 12:15 UTC
- **Updated**: 2026-03-06 13:36 UTC
- **Notes**: Docker установлен, но `docker-compose.yml` был с неправильными отступами (YAML-ключи на одном уровне), из-за чего дубли ключей. Файл исправлен на валидный; `docker compose config` проходит (только warning про устаревшее поле `version`). Следующий шаг: `docker compose up -d --build`, затем `docker compose ps` и проверка `/health`.


## [2026-03-05-eragon-site] Сделать сайт в стиле Eragon с реферальными кнопками бирж
- **Status**: 🔄 进行中
- **Requested**: 2026-03-05 06:18 UTC
- **Updated**: 2026-03-06 13:50 UTC
- **Notes**: Приоритет на сегодня подтверждён пользователем: доделать задачи по Eragon-сайту в первую очередь (tailnet отложить). Runtime Error оказался от браузерного расширения Talisman (`chrome-extension://...`), не от кода Next.js. V4 и V5 собраны и переданы (cinematic fog + premium CTA). Пользователь поднял проект на Vercel и подтвердил live-ссылку. Текущий следующий шаг: настроить workflow “по-взрослому” — `main` production, `feat/*` preview, PR-only protection, опционально custom domain.

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


# Completed (recent)
- [2026-03-05-overnight-ops] ✅ Ночная задача закрыта: userbot стабилен, бэкапы сделаны, end-to-end публикация digest подтверждена (`@Elven_Ai_Lab`, "✨ Главное на сегодня").
- [2026-03-04-gateway-fix] ✅ Починил: удалён systemd override с `--bind tailnet`, выполнены daemon-reload + restart; сейчас `openclaw-gateway.service` stable, `gateway probe` => Reachable yes / RPC ok.
- [2026-03-04-gateway-recheck] ✅ Повторная проверка: Gateway сейчас стабилен и reachable (ws://127.0.0.1:18789, RPC ok, service active, NRestarts=0).
- [2026-03-04-gateway-check] ✅ Диагностика сервера: причина — systemd override запускает `openclaw gateway` с `--bind tailnet`, из-за чего сервис уходит в рестарт (ошибка `gateway.controlUi.allowedOrigins`); хост ресурсы в норме.
