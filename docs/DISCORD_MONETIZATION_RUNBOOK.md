# DISCORD_MONETIZATION_RUNBOOK.md

Runbook для приватного Discord сервера с монетизацией доступа (no-GPT).

## 0) Параметры твоего сервера
- `GUILD_ID=1484209988653027440`
- `DISCORD_TOKEN=<твой bot token>`
- `STRIPE_WEBHOOK_SECRET=<твой Stripe signing secret>`
- `DATABASE=/home/openclawuser/.openclaw/workspace/data/discord_billing.db`
- `MOD_LOG_CHANNEL=123456789` (замени на реальный channel id `#mod-logs`)

---

## 1) Создание ролей (Discord UI)
Server Settings -> Roles -> Create Role

Создай роли:
1. `Verified`
2. `Premium Member`
3. `VIP Member`
4. `Moderator`
5. `Bot`

Важно: роль бота должна быть выше Premium/VIP в списке ролей.

---

## 2) Категории и каналы

### 📌 ОБЩЕЕ (видно всем)
- `#welcome`
- `#free-content`
- `#announcements`
- `#support`

### 🔐 PREMIUM (только Premium Member)
- `#premium-content`
- `#discussions`
- `#resources`
- `#ai-assistant`

### 👑 VIP (только VIP Member)
- `#vip-exclusive`
- `#live-calls`
- `#one-on-one`
- `#vip-resources`

### 🛠️ ADMIN (только Moderator)
- `#mod-logs`
- `#mod-panel`
- `#stats`

Permission overrides:
- Для PREMIUM/VIP категорий: `@everyone` -> deny View Channel
- Для соответствующих ролей -> allow View Channel + Send Messages

---

## 3) Stripe интеграция

1. Stripe Dashboard -> Developers -> Webhooks -> Add endpoint
2. Endpoint URL:
   - `https://<твой_домен>/webhook/stripe`
   - или через reverse tunnel/Nginx на `127.0.0.1:8091/webhook/stripe`
3. Подпишись минимум на события:
   - `checkout.session.completed`
   - `invoice.paid`
   - `invoice.payment_failed`
   - `customer.subscription.deleted`
4. Скопируй `Signing secret` -> это `STRIPE_WEBHOOK_SECRET`

Metadata в платеже (обязательно):
- `discord_user_id`
- `tier` (premium/vip/course_lifetime/wt_vip)
- `expires_at` (YYYY-MM-DD для периодических)

---

## 4) Подготовка .env

```bash
cp /home/openclawuser/.openclaw/workspace/config/discord_billing.env.example /home/openclawuser/.openclaw/workspace/config/discord_billing.env
nano /home/openclawuser/.openclaw/workspace/config/discord_billing.env
```

Заполни:
- `DISCORD_TOKEN`
- `GUILD_ID=1484209988653027440`
- `STRIPE_WEBHOOK_SECRET`
- `MOD_LOG_CHANNEL`
- `ROLE_PREMIUM_MEMBER_ID`, `ROLE_VIP_MEMBER_ID`, ...

---

## 5) Установка systemd units

```bash
mkdir -p ~/.config/systemd/user
cp /home/openclawuser/.openclaw/workspace/infra/systemd-user/discord-billing-sync.service ~/.config/systemd/user/
cp /home/openclawuser/.openclaw/workspace/infra/systemd-user/discord-billing-expiry.service ~/.config/systemd/user/
cp /home/openclawuser/.openclaw/workspace/infra/systemd-user/discord-billing-sync.timer ~/.config/systemd/user/
systemctl --user daemon-reload
```

---

## 6) Запуск сервиса webhook

```bash
systemctl --user enable discord-billing-sync.service
systemctl --user start discord-billing-sync.service
systemctl --user status discord-billing-sync.service --no-pager -l
```

Логи live:
```bash
journalctl --user -u discord-billing-sync -f
```

---

## 7) Запуск ежедневного expiry-check (00:00 UTC)

```bash
systemctl --user enable --now discord-billing-sync.timer
systemctl --user list-timers --all | grep discord-billing-sync
```

Ручной тест проверки expiry:
```bash
python3 /home/openclawuser/.openclaw/workspace/scripts/discord_billing_sync.py --mode expiry-check --env-file /home/openclawuser/.openclaw/workspace/config/discord_billing.env
```

---

## 8) Тест webhook локально

Healthcheck:
```bash
curl -s http://127.0.0.1:8091/health
```

Тест Stripe CLI (опционально):
```bash
stripe listen --forward-to http://127.0.0.1:8091/webhook/stripe
```

---

## 9) Чеклист запуска (21 пункт)

1. [ ] Созданы роли Verified/Premium/VIP/Moderator/Bot
2. [ ] Роль бота выше Premium/VIP
3. [ ] Создана категория ОБЩЕЕ
4. [ ] Создана категория PREMIUM
5. [ ] Создана категория VIP
6. [ ] Создана категория ADMIN
7. [ ] PREMIUM скрыт для @everyone
8. [ ] VIP скрыт для @everyone
9. [ ] `#mod-logs` создан и ID записан в env
10. [ ] Stripe endpoint создан
11. [ ] Stripe signing secret записан в env
12. [ ] Metadata содержит discord_user_id
13. [ ] Metadata содержит tier
14. [ ] `discord_billing.env` заполнен
15. [ ] `discord-billing-sync.service` enabled+started
16. [ ] `discord-billing-sync.timer` enabled+running
17. [ ] healthcheck `127.0.0.1:8091/health` = ok
18. [ ] webhook событие доходит (лог в journalctl)
19. [ ] роль Premium выдаётся после успешной оплаты
20. [ ] роль снимается после expiry/revoke
21. [ ] нет секретов/токенов в git

---

## 10) Важные команды

```bash
systemctl --user enable discord-billing-sync.service
systemctl --user start discord-billing-sync.service
journalctl --user -u discord-billing-sync -f

systemctl --user enable --now discord-billing-sync.timer
systemctl --user status discord-billing-sync.timer
```
