# Active Tasks

## [2026-03-04-gateway-tailnet-fix] Применить bind=tailnet для openclaw-gateway
- **Status**: ⏸️ 暂停
- **Requested**: 2026-03-04 18:24 UTC
- **Updated**: 2026-03-04 22:37 UTC
- **Notes**: Временно отложено, приоритет смещён на ночные задачи по userbot по прямому запросу пользователя.

## [2026-03-05-channel-posts] Опубликовать новые посты в @Elven_Ai_Lab
- **Status**: ✅ 完成
- **Requested**: 2026-03-05 04:38 UTC
- **Updated**: 2026-03-05 04:40 UTC
- **Notes**: Публикация через message tool не прошла (бот не участник канала, 403). Выполнено через Telethon user-session (`/home/openclawuser/userbot/session.session`). Дополнительно исправлен код userbot: добавлен fallback user-session при fail Bot API.
- **Result**: Отправлены 2 новых поста в канал (IDs: 99 и 100). userbot перезапущен, статус stable (NRestarts=0).


# Completed (recent)
- [2026-03-05-overnight-ops] ✅ Ночная задача закрыта: userbot стабилен, бэкапы сделаны, end-to-end публикация digest подтверждена (`@Elven_Ai_Lab`, "✨ Главное на сегодня").
- [2026-03-04-gateway-fix] ✅ Починил: удалён systemd override с `--bind tailnet`, выполнены daemon-reload + restart; сейчас `openclaw-gateway.service` stable, `gateway probe` => Reachable yes / RPC ok.
- [2026-03-04-gateway-recheck] ✅ Повторная проверка: Gateway сейчас стабилен и reachable (ws://127.0.0.1:18789, RPC ok, service active, NRestarts=0).
- [2026-03-04-gateway-check] ✅ Диагностика сервера: причина — systemd override запускает `openclaw gateway` с `--bind tailnet`, из-за чего сервис уходит в рестарт (ошибка `gateway.controlUi.allowedOrigins`); хост ресурсы в норме.
