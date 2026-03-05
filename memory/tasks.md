# Active Tasks

## [2026-03-04-overnight-ops] Ночная стабилизация userbot + фиксация прогресса в Obsidian
- **Status**: 🔄 进行中
- **Requested**: 2026-03-04 22:37 UTC
- **Updated**: 2026-03-05 04:24 UTC
- **Notes**: Сделано: создан Obsidian handoff, userbot проверен (active), синтаксис bot.py валиден, сервис перезапущен в чистое состояние (NRestarts=0), бэкапы созданы. Осталось: подтвердить утром факт свежей публикации в канал и при необходимости дожать digest вручную.

## [2026-03-04-gateway-tailnet-fix] Применить bind=tailnet для openclaw-gateway
- **Status**: ⏸️ 暂停
- **Requested**: 2026-03-04 18:24 UTC
- **Updated**: 2026-03-04 22:37 UTC
- **Notes**: Временно отложено, приоритет смещён на ночные задачи по userbot по прямому запросу пользователя.


# Completed (recent)
- [2026-03-04-gateway-fix] ✅ Починил: удалён systemd override с `--bind tailnet`, выполнены daemon-reload + restart; сейчас `openclaw-gateway.service` stable, `gateway probe` => Reachable yes / RPC ok.
- [2026-03-04-gateway-recheck] ✅ Повторная проверка: Gateway сейчас стабилен и reachable (ws://127.0.0.1:18789, RPC ok, service active, NRestarts=0).
- [2026-03-04-gateway-check] ✅ Диагностика сервера: причина — systemd override запускает `openclaw gateway` с `--bind tailnet`, из-за чего сервис уходит в рестарт (ошибка `gateway.controlUi.allowedOrigins`); хост ресурсы в норме.
