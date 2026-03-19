# Pay2Pass Discord Bridge Runbook (pay2pass/)

## 1) Подготовка
```bash
cd /home/openclawuser/.openclaw/workspace/pay2pass
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config/pay2pass_bridge.env.example config/.env
nano config/.env
```

Заполни в `config/.env`:
- DISCORD_TOKEN
- GUILD_ID=1484209988653027440
- MOD_LOG_CHANNEL=<id канала mod-logs>
- ROLE_PREMIUM_MEMBER_ID, ROLE_MID_MEMBER_ID, ROLE_VIP_MEMBER_ID
- BSCSCAN_API_KEY

## 2) Быстрый тест
```bash
source .venv/bin/activate
python scripts/pay2pass_discord_bridge.py --mode expiry-check --env-file config/.env
python scripts/pay2pass_discord_bridge.py --mode create-link --env-file config/.env --discord-id <DISCORD_ID> --tier premium
```

## 3) Установка systemd (user)
```bash
mkdir -p ~/.config/systemd/user
cp infra/systemd-user/pay2pass-bridge.service ~/.config/systemd/user/
cp infra/systemd-user/pay2pass-bridge-expiry.service ~/.config/systemd/user/
cp infra/systemd-user/pay2pass-bridge.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now pay2pass-bridge.service
systemctl --user enable --now pay2pass-bridge.timer
```

## 4) Проверка статуса и логов
```bash
systemctl --user status pay2pass-bridge.service --no-pager -l
systemctl --user status pay2pass-bridge.timer --no-pager -l
journalctl --user -u pay2pass-bridge -f
```

## 5) Принцип работы
- Polling BscScan каждые 10 сек
- Ищет входящие USDT на адрес `0x694bf4e92113d6d92216c532326ffb1bb6e2dab3`
- Идемпотентность по `tx_hash`
- tier по сумме: 25/69/150 USDT
- выдача роли в Discord и лог в #mod-logs
- ежедневный expiry-check в 00:00 UTC

## 6) Безопасность
- Не хранить токены в git
- `config/.env` держать локально
- Роль бота должна быть выше Premium/Mid/VIP
