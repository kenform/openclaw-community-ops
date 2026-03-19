#!/usr/bin/env python3
"""
No-GPT обработчик входящих вопросов подписчиков из CSV (экспорт Google Sheets/Form).
Usage:
  python3 subscriber_forms_no_gpt.py --input responses.csv --out reports/subscriber_forms_report.json
"""
import argparse, csv, json, re, time
from pathlib import Path

TOPIC_RULES = {
    'openclaw': ['openclaw', 'агент', 'gateway', 'бот', 'skills'],
    'parser': ['парсер', 'pipeline', 'source', 'topic'],
    'groups': ['групп', 'чат', 'канал', 'топик'],
    'bug': ['ошибка', 'не работает', 'баг', 'error', 'traceback'],
}

TEMPLATES = {
    'openclaw': 'Приняли вопрос по OpenClaw. Подготовим короткий пошаговый ответ.',
    'parser': 'Приняли вопрос по парсерам. Проверим конфиг и предложим безопасный план правок.',
    'groups': 'Приняли вопрос по группам/каналам. Сверим структуру и дадим практичное решение.',
    'bug': 'Приняли баг-репорт. Проверим логи и вернёмся с точечным фиксом.',
    'other': 'Приняли вопрос. Подготовим ответ в ближайшем рабочем окне.'
}


def classify(text: str) -> str:
    low = (text or '').lower()
    for k, words in TOPIC_RULES.items():
      if any(w in low for w in words):
        return k
    return 'other'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    rows = []
    with open(args.input, 'r', encoding='utf-8', errors='ignore') as f:
      reader = csv.DictReader(f)
      for r in reader:
        q = r.get('Вопрос') or r.get('Question') or ''
        topic = classify(q)
        rows.append({
          'name': r.get('Имя') or r.get('Name') or '',
          'username': r.get('Telegram') or r.get('Username') or '',
          'question': q,
          'topic': topic,
          'reply_draft': TEMPLATES.get(topic, TEMPLATES['other']),
          'priority': (r.get('Срочность') or r.get('Priority') or 'medium').lower()
        })

    rep = {
      'ts': int(time.time()),
      'mode': 'subscriber_forms_no_gpt',
      'count': len(rows),
      'by_topic': {},
      'items': rows
    }
    for it in rows:
      rep['by_topic'][it['topic']] = rep['by_topic'].get(it['topic'], 0) + 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'out': str(out), 'count': rep['count'], 'by_topic': rep['by_topic']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
