#!/usr/bin/env python3
import asyncio
import datetime as dt
import json
import random
from pathlib import Path
from telethon import TelegramClient

WORKSPACE = Path('/home/openclawuser/.openclaw/workspace')
CFG = WORKSPACE / 'scripts' / 'elven_ai_lab_config.json'
USERBOT_ENV = Path('/home/openclawuser/userbot/config.env')
SESSION = '/home/openclawuser/userbot/session.session'
VAULT = WORKSPACE / 'Obsidian-Telegram-KB'


def load_cfg():
    if not CFG.exists():
        return {
            'channel_name': 'Elven AI Lab',
            'language': 'ru',
            'max_lines': 12,
            'min_lines': 8,
            'daily_slots': ['09:00','12:00','15:00','18:00','21:00','23:00'],
            'enabled': True
        }
    return json.loads(CFG.read_text(encoding='utf-8'))


def load_env(path: Path):
    out = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k,v = line.split('=',1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def latest_insights(limit=20):
    files = sorted((VAULT / '20_Summaries').glob('*.md'), key=lambda p: p.stat().st_mtime, reverse=True)
    snippets = []
    for p in files[:limit]:
        txt = p.read_text(encoding='utf-8', errors='ignore')
        title = txt.splitlines()[0].replace('#','').strip() if txt else p.stem
        snippets.append((p, title))
    return snippets


def pick_post(slot_idx: int):
    insights = latest_insights(30)
    title_pool = [t for _, t in insights] or ['AI signal of the day']
    t = random.choice(title_pool)

    if slot_idx == 0:
        return f"""⚡ AI Signal

Рынок смещается в сторону агентных систем, где важен не “умный ответ”, а стабильный workflow.
• Спрос растёт на связки: Telegram + Obsidian + automation
• Выигрывает тот, кто быстрее превращает инфопоток в действия
• Главное конкурентное преимущество — дисциплина процессов

Почему важно:
Скорость исполнения уже важнее, чем просто количество знаний."""

    if slot_idx == 1:
        return f"""🧰 Tool Breakdown: OpenClaw + Skills

Ключ к пользе OpenClaw — не в модели, а в правильно собранном стеке skills.
• База: мониторинг, суммаризация, сохранение в Obsidian
• Безопасность: аудит скиллов до прод-использования
• Производство: task-tracker + step-sequencer для повторяемых циклов

Почему важно:
Навыки и процессы дают предсказуемый результат каждый день."""

    if slot_idx == 2:
        return f"""🤖 Automation Guide

Как сделать простой AI-конвейер за 30 минут:
• Источник (Telegram/X/YouTube)
• Автовыжимка (summary)
• Сохранение в Obsidian
• Короткий daily brief в канал

Почему важно:
Ты перестаёшь тонуть в шуме и начинаешь работать с системой."""

    if slot_idx == 3:
        return f"""📈 AI Business Model

Один из рабочих путей монетизации: “AI Ops под ключ” для авторов/каналов.
• Настройка контент-конвейера
• Автоматизация дайджестов и базы знаний
• Поддержка и оптимизация по KPI

Почему важно:
Люди платят не за ИИ, а за стабильный результат и экономию времени."""

    if slot_idx == 4:
        return f"""🔍 Research Note

Тема дня: {t}
• Проверяй первоисточники, а не пересказы
• Отмечай противоречия и уровень уверенности
• Отделяй факт от мнения (hypothesis, если данных мало)

Почему важно:
Качественный ресерч напрямую влияет на качество решений и контента."""

    return f"""🧪 Practical Routine (вечер)

Мини-ритуал на 10 минут:
• Что сработало сегодня?
• Что не сработало и почему?
• Что переносим на завтра?

Почему важно:
Именно ежедневный цикл улучшений даёт эффект на дистанции."""


def build_weekly_digest():
    insights = latest_insights(50)
    top = [t for _, t in insights[:10]]
    bullets = '\n'.join([f"• {x}" for x in top]) if top else '• Нет новых релевантных материалов'
    return f"""🗓 Weekly Digest — Top 10 AI/Automation Signals

{bullets}

Почему важно:
Эти темы формируют практический стек: AI агенты, automation, инфраструктура и монетизация."""


async def publish(mode='slot'):
    cfg = load_cfg()
    if not cfg.get('enabled', True):
        return

    env = load_env(USERBOT_ENV)
    client = TelegramClient(SESSION, int(env['TELEGRAM_API_ID']), env['TELEGRAM_API_HASH'])
    await client.start()

    target = None
    dialogs = await client.get_dialogs(limit=400)
    for d in dialogs:
        if (d.name or '').strip().lower() == cfg['channel_name'].strip().lower():
            target = d.entity
            break
    if not target:
        for d in dialogs:
            if cfg['channel_name'].strip().lower() in (d.name or '').lower():
                target = d.entity
                break

    if not target:
        await client.disconnect()
        return

    if mode == 'weekly':
        msg = build_weekly_digest()
    else:
        now = dt.datetime.utcnow()
        slot_idx = now.hour % 6
        msg = pick_post(slot_idx)

    # Quality filter: basic line count guard
    lines = [x for x in msg.splitlines() if x.strip()]
    if not (6 <= len(lines) <= 14):
        await client.disconnect()
        return

    await client.send_message(target, msg, link_preview=False)
    await client.disconnect()


if __name__ == '__main__':
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else 'slot'
    asyncio.run(publish(mode))
