# PAY2PASS_DISCORD_RUNBOOK.md

No-GPT интеграция: платежи USDT (BSC) -> выдача Discord ролей.

## Исходные данные
- Адрес: `0x694bf4e92113d6d92216c532326ffb1bb6e2dab3`
- Сеть: BNB Smart Chain (BEP20)
- Тарифы:
  - Premium: `25 USDT`
  - Mid: `69 USDT`
  - VIP: `150 USDT`

## Что делает bridge
- Polling BscScan каждые 10 сек
- Ищет входящие `USDT` на адрес
- Идемпотентно обрабатывает tx_hash
- Определяет tier по сумме
- Находит связку Discord через `link_code`
- Выдаёт роль в Discord
- Пишет логи в `#mod-logs`
- Daily expiry-check отзывает роль после срока

---

## 1) Подготовка env
```bash
cp /home/openclawuser/.openclaw/workspace/config/pay2pass_bridge.env.example /home/openclawuser/.openclaw/workspace/config/pay2pass_bridge.env
nano /home/openclawuser/.openclaw/workspace/config/pay2pass_bridge.env
```

Заполни обязательно:
- `DISCORD_TOKEN`
- `MOD_LOG_CHANNEL`
- `ROLE_PREMIUM_MEMBER_ID`
- `ROLE_MID_MEMBER_ID`
- `ROLE_VIP_MEMBER_ID`
- `BSCSCAN_API_KEY`

---

## 2) Команда создания линк-кода (для пользователя)
```bash
python3 /home/openclawuser/.openclaw/workspace/scripts/pay2pass_discord_bridge.py \
  --mode create-link \
  --env-file /home/openclawuser/.openclaw/workspace/config/pay2pass_bridge.env \
  --discord-id <DISCORD_USER_ID> \
  --tier premium
```

Выход: JSON с `code`, суммой и адресом.
Пользователь платит по этому инвойсу в пределах TTL.

---

## 3) Установка systemd
```bash
mkdir -p ~/.config/systemd/user
cp /home/openclawuser/.openclaw/workspace/infra/systemd-user/pay2pass-bridge.service ~/.config/systemd/user/
cp /home/openclawuser/.openclaw/workspace/infra/systemd-user/pay2pass-bridge-expiry.service ~/.config/systemd/user/
cp /home/openclawuser/.openclaw/workspace/infra/systemd-user/pay2pass-bridge.timer ~/.config/systemd/user/
systemctl --user daemon-reload
```

Запуск polling сервиса:
```bash
systemctl --user enable --now pay2pass-bridge.service
systemctl --user status pay2pass-bridge.service --no-pager -l
```

Запуск daily expiry:
```bash
systemctl --user enable --now pay2pass-bridge.timer
systemctl --user list-timers --all | grep pay2pass-bridge
```

Логи live:
```bash
journalctl --user -u pay2pass-bridge -f
```

---

## 4) Проверка
- Создай link-code для тестового discord id
- Сделай тест-платеж нужной суммы USDT
- Проверь лог в `#mod-logs`
- Проверь что роль выдана

---

## 5) Безопасность
- `.env` не коммитить
- токены/API ключи не отправлять в чат
- роль бота должна быть выше управляемых ролей
- проверять idempotency по `tx_hash`
