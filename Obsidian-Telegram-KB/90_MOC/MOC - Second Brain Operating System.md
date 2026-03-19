# MOC - Second Brain Operating System

## Контуры
- [[MOC - AI Agents]]
- [[MOC - OpenClaw]]
- [[MOC - Crypto Exchanges]]
- [[MOC - Product Monetization]]

## Ежедневный цикл (15-25 мин)
1. Ingest: добавить 3-10 новых материалов
2. Normalize: привести к шаблону Knowledge-Note
3. Link: минимум 2 связи на заметку
4. Action: выбрать 1-2 шага на 24-72ч

## Правила качества (gate)
- Практическая ценность: да/нет
- Есть конкретика (цифры/шаги/команды): да/нет
- Применимо в 24-72ч: да/нет

Если 2+ ответа «нет» -> в архив/удаление.

## Дедуп-правила
- Совпадает URL -> merge
- Семантический дубль (>80%) -> merge
- Короткий шум без actionable смысла -> delete

## Недельный ритуал
- Использовать шаблон [[Weekly-Review]]
- Чистить шум и поднимать лучшие связи в MOC

## Быстрый обзор новых заметок (Dataview)
```dataview
TABLE date(file.mtime) as Updated, Source, Relevance
FROM "10_Channels" OR "20_Summaries"
SORT file.mtime DESC
LIMIT 20
```
