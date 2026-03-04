# Active Tasks

（无）

# Completed (recent)
- [2026-03-04-gateway-recheck] ✅ Повторная проверка: Gateway сейчас стабилен и reachable (ws://127.0.0.1:18789, RPC ok, service active, NRestarts=0).
- [2026-03-04-gateway-check] ✅ Диагностика сервера: причина — systemd override запускает `openclaw gateway` с `--bind tailnet`, из-за чего сервис уходит в рестарт (ошибка `gateway.controlUi.allowedOrigins`); хост ресурсы в норме.
