# Починить баг с ссылками в Eragon-сайте

- Дата: 2026-03-08
- Контекст: в live Vercel-деплое Eragon сайта местами остаются заглушки `https://example.com/bybit` и `https://example.com/bitget`, несмотря на обновлённый код в workspace.

## Что нужно исправить
1. Проверить Vercel Project → Settings → Git (правильный репозиторий и ветка `main`).
2. Проверить Root Directory для проекта (чтобы деплоился нужный код).
3. Перезапустить актуальный деплой (Redeploy latest commit).
4. После деплоя верифицировать live URL:
   - Bybit: `https://www.bybit.com/invite?ref=W2DDND`
   - Bitget: `https://www.bitget.com/ru/referral/register?clacCode=GF5KD76T&from=%2Fru%2Fevents%2Freferral-all-program&source=events&utmSource=PremierInviter`

## Симптом бага
- На части доменов Vercel по-прежнему отображаются `example.com` ссылки.

## Статус
- TODO / требуется ручная проверка настроек Vercel.
