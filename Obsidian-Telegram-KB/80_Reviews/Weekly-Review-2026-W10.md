# Weekly Review — 2026-W10

## 1) Что сработало (Top 5)
- Стабилизирован формат постов `.d` (ссылки/отступы/футер/теги).
- Починены проблемы с отображением раскрывающихся блоков в канале.
- Введён контроль публикации: отправка только по команде `тест`.
- Собран каркас `cex-arcana` (collector + API + DB schema + docs).
- Добавлен прототип сайта в стиле Eragon с CTA-блоками бирж.

## 2) Что не сработало
- Повторные поломки spoiler из-за смены parse/render режимов.
- Отсутствие Docker на хосте остановило быстрый запуск infra.

## 3) Лучшие связи (knowledge graph wins)
- Канальный контент -> шаблон поста -> стабильный публикационный формат.
- Пост deployladeploy -> MOC/Zettelkasten подход -> усиление Obsidian процесса.
- CEX blueprint -> каркас проекта -> готовность к реальному API-интегрированию.

## 4) Дубликаты/шум на удаление
- [ ] Удалить/архивировать старые тестовые посты в канале (по желанию).
- [ ] Почистить временные/черновые правила форматирования, неиспользуемые ветки.

## 5) Решения на следующую неделю
- [ ] Поставить Docker и поднять `cex-arcana` через compose.
- [ ] Заменить mock-collector на реальные API Bybit/Bitget/MEXC.
- [ ] Сделать фронт страницы funding/volume/arbitrage/liquidations.

## KPI
- Notes created: 2+ (deployladeploy analysis + second-brain templates)
- Notes merged: 0
- Notes deleted: 0
- Useful links discovered: 4+
- Actions shipped: 20+ фиксов по userbot/формату
