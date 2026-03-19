---
type: claim-analysis
status: pending-verification
date: 2026-03-03
tags: [polymarket, x-post, ai-agent, latency, sentiment, copytrade, high-risk]
---

# X-пост клейм: "$1k -> $10k за 24 часа" на Polymarket

## Сводка клейма (из присланного текста)
- Hour 4: front-run mispriced BTC markets после Fed hold.
- Hour 8: сентимент по посту Elon (заявленное преимущество ~340ms).
- Hour 14: thin ETH/BTC ratio markets, покупка обеих сторон на 3c на 11 рынках.
- Hour 18: паттерн BTC move 1.2%/4min -> YES underpriced 8-12c, заявлено 31 повторение.
- Hour 24: итог $10,001.
- В конце есть реф-ссылка на copytrade-бота.

## Red flags
1. Экстремальная доходность за 24ч без верифицируемого trade-log.
2. Смешение разных механизмов edge в одном нарративе (latency + sentiment + pattern) — типичный маркетинговый “stacked claim”.
3. Нет net-метрик: fees, slippage, reject rate, latency end-to-end.
4. Призыв к copytrade через реф-ссылку усиливает риск рекламного оверстейтмента.

## Что может быть частично правдой
- На тонких prediction markets и event spikes действительно бывают короткие mispricing-окна.
- Сентимент/новости могут двигать вероятности с лагом на части рынков.

## Что нужно для верификации
- Timestamped execution log (вход/выход, размер, fill price).
- Net PnL после комиссий и проскальзывания.
- Повторяемость на серии (>=30 сделок) без ручного cherry-pick.
- Разделение PnL по стратегиям (latency / sentiment / pattern).

## Вердикт
Пока это high-volatility маркетинговый кейс с потенциально реальными элементами микро-альфы, но без доказуемой воспроизводимости.
