# Active Tasks

## [2026-03-04-gateway-tailnet-fix] Применить bind=tailnet для openclaw-gateway
- **Status**: ⏸️ 暂停
- **Requested**: 2026-03-04 18:24 UTC
- **Updated**: 2026-03-05 04:45 UTC
- **Notes**: Временно отложено, приоритет смещён на ночные задачи по userbot по прямому запросу пользователя.

## [2026-03-05-channel-posts] Опубликовать новые посты в @Elven_Ai_Lab
- **Status**: ✅ 完成
- **Requested**: 2026-03-05 04:38 UTC
- **Updated**: 2026-03-05 04:46 UTC
- **Notes**: Выяснено: `DIGEST_BOT_TOKEN` действительно указывает на `@Elven_post_bot` (getMe OK). 403 был от другого бот-отправителя (message tool), не члена канала. Выполнено через Telethon user-session (`/home/openclawuser/userbot/session.session`). Дополнительно исправлен код userbot: добавлен fallback user-session при fail Bot API.
- **Result**: Отправлены 2 новых поста в канал (IDs: 99 и 100). Прямой Bot API probe через `@Elven_post_bot` успешен (message_id 102), тест удалён; userbot stable (NRestarts=0).


# Completed (recent)
- [2026-03-05-overnight-ops] ✅ Ночная задача закрыта: userbot стабилен, бэкапы сделаны, end-to-end публикация digest подтверждена (`@Elven_Ai_Lab`, "✨ Главное на сегодня").
- [2026-03-04-gateway-fix] ✅ Починил: удалён systemd override с `--bind tailnet`, выполнены daemon-reload + restart; сейчас `openclaw-gateway.service` stable, `gateway probe` => Reachable yes / RPC ok.
- [2026-03-04-gateway-recheck] ✅ Повторная проверка: Gateway сейчас стабилен и reachable (ws://127.0.0.1:18789, RPC ok, service active, NRestarts=0).
- [2026-03-04-gateway-check] ✅ Диагностика сервера: причина — systemd override запускает `openclaw gateway` с `--bind tailnet`, из-за чего сервис уходит в рестарт (ошибка `gateway.controlUi.allowedOrigins`); хост ресурсы в норме.
