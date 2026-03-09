import json
import time
import logging
import importlib.util
import argparse
from pathlib import Path
from collections import defaultdict

from telethon import TelegramClient
from telethon.tl.functions.channels import GetForumTopicsRequest

BASE = Path('/home/openclawuser/.openclaw/workspace/projects/telegram-pipeline-v1')
BOTPY = BASE / 'bot.py'
REPORT = Path('/home/openclawuser/.openclaw/workspace/tmp/topic_backfill_by_ids_report.json')

spec = importlib.util.spec_from_file_location('pipeline_bot', str(BOTPY))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

logger = logging.getLogger('topic-backfill-by-ids')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

parser = argparse.ArgumentParser()
parser.add_argument('--session', default='')
args = parser.parse_args()

cfg = json.loads((BASE / 'config.json').read_text(encoding='utf-8'))
engine_cfg = mod.load_engine_configs(BASE, logger)
engine_sources = engine_cfg.get('sources', [])
trader_profiles = engine_cfg.get('traders', {})
rules = mod.load_ilya_rules(cfg, logger)
rules['signal_threshold'] = int(cfg.get('SIGNAL_CONFIDENCE_THRESHOLD', rules.get('signal_threshold', 7)))

api_id = int(cfg['TELEGRAM_API_ID'])
api_hash = cfg['TELEGRAM_API_HASH']
session_name = args.session.strip() if args.session.strip() else cfg['SESSION_NAME']
bot_token = cfg['BOT_TOKEN']

allowed_group_ref = mod.parse_ref(cfg.get('ALLOWED_GROUP'))
main_target_ref = mod.parse_ref(cfg.get('MAIN_TARGET_CHANNEL_ID', cfg.get('TARGET_CHANNEL_ID')))
signal_target_ref = mod.parse_ref(cfg.get('SIGNAL_TARGET_CHANNEL_ID', cfg.get('TARGET_CHANNEL_ID')))

allowed_topic_ids = {int(x) for x in cfg.get('ALLOWED_TOPIC_IDS', []) if str(x).strip().lstrip('-').isdigit()}
ilya_topic_id = int(cfg.get('ILYA_TOPIC_ID', 58866))
allowed_topic_ids.add(ilya_topic_id)
artur_enabled = bool(cfg.get('ARTUR_ENABLED', True))
artur_topic_id = int(cfg.get('ARTUR_TOPIC_ID', 57974))
signal_parser_enabled = bool(cfg.get('SIGNAL_PARSER_ENABLED', True))
ilya_main_filter_enabled = bool(cfg.get('ILYA_MAIN_FILTER_ENABLED', True))


client = TelegramClient(session_name, api_id, api_hash, auto_reconnect=True, sequential_updates=True)


def classify_and_send(group_id, topic_id, topic_title, msg, main_target, signal_target):
    text = msg.message or ''
    media_only = bool(msg.media) and not text.strip()

    trader_id = mod.resolve_trader_by_source(int(group_id), int(topic_id), engine_sources)
    if int(topic_id) in {ilya_topic_id, 14, 58866, 59433}:
        trader_id = 'ilya'
    if artur_enabled and int(topic_id) in {artur_topic_id, 13810, 57974}:
        trader_id = 'artur'

    if not trader_id:
        return {'main': False, 'signal': False, 'reason': 'source_not_configured'}

    if trader_id == 'artur':
        main_result = mod.classify_artur_main(text)
    elif trader_id == 'ilya':
        main_result = mod.classify_main_ilya_message(text, has_media=bool(msg.media), rules=rules) if ilya_main_filter_enabled else {'pass': True, 'score': 0, 'type': 'VIEW', 'reason': 'PASS_VIEW'}
    else:
        main_result = {'pass': True, 'type': 'VIEW', 'reason': 'PASS_MAIN_MARKET_VIEW'}

    tv_link = mod.has_tradingview_link(text, engine_cfg.get('tradingview_patterns', ['tradingview.com']))
    if tv_link:
        main_result = {'pass': True, 'type': main_result.get('type') or 'VIEW', 'reason': 'PASS_MAIN_TRADINGVIEW', 'hold_only': False}

    sent_main = False
    sent_signal = False

    if main_result.get('pass'):
        payload = f"[Type: {main_result.get('type') or 'VIEW'}]\n" + mod.format_payload('Интра 2.0 ☃️', int(group_id), int(topic_id), text, media_only, topic_title=topic_title)
        sent_main = mod.send_via_bot_api(bot_token, str(main_target), payload, logger, dry_run=False)

    if signal_parser_enabled and not main_result.get('hold_only', False):
        if trader_id == 'artur':
            sig = mod.parse_artur_signal(text) if text.strip() else {'pass': False}
            if sig.get('pass'):
                sent_signal = mod.send_via_bot_api(bot_token, str(signal_target), mod.format_artur_signal(sig), logger, dry_run=False)
        elif trader_id == 'ilya':
            sig = mod.parse_ilya_signal(text, rules)
            if sig.get('pass'):
                sent_signal = mod.send_via_bot_api(bot_token, str(signal_target), mod.format_signal_message(sig), logger, dry_run=False)
        else:
            threshold = int((trader_profiles.get(trader_id, {}) or {}).get('signal_threshold', 6))
            sig = mod.parse_generic_signal(text, threshold=threshold)
            if sig.get('pass'):
                sig_msg = (
                    f"#Signal\nTrader: {trader_id}\nAsset: {sig.get('asset')}\nType: {sig.get('signal_type')}\n"
                    f"Entry: {sig.get('entry')}\nStop: {sig.get('stop')}\nTarget: {sig.get('target')}\n"
                    f"Confidence: {sig.get('confidence')}\n\nRaw:\n{sig.get('raw')}"
                )
                sent_signal = mod.send_via_bot_api(bot_token, str(signal_target), sig_msg, logger, dry_run=False)

    if sent_main or sent_signal:
        return {'main': sent_main, 'signal': sent_signal, 'reason': 'pass'}
    return {'main': False, 'signal': False, 'reason': 'filtered'}


async def run():
    await client.start()
    group_id = await mod.resolve_chat_ref(client, allowed_group_ref)
    if group_id is None:
        raise RuntimeError('Cannot resolve ALLOWED_GROUP')
    group_entity = await client.get_entity(group_id)

    main_target = await mod.resolve_chat_ref(client, main_target_ref)
    signal_target = await mod.resolve_chat_ref(client, signal_target_ref)
    if main_target is None or signal_target is None:
        raise RuntimeError('Cannot resolve targets')

    topics_resp = await client(GetForumTopicsRequest(channel=group_entity, offset_date=None, offset_id=0, offset_topic=0, limit=400, q=''))
    topics = getattr(topics_resp, 'topics', []) or []

    topic_title_by_runtime = {}
    wanted_runtime = set()
    for t in topics:
        t_title = str(getattr(t, 'title', '')).strip()
        t_top = int(getattr(t, 'top_message', 0) or 0)
        t_id = int(getattr(t, 'id', 0) or 0)
        if t_top:
            topic_title_by_runtime[t_top] = t_title
        if t_id:
            topic_title_by_runtime[t_id] = t_title
        if t_top in allowed_topic_ids or t_id in allowed_topic_ids:
            if t_top:
                wanted_runtime.add(t_top)
            if t_id:
                wanted_runtime.add(t_id)

    if not wanted_runtime:
        wanted_runtime = set(allowed_topic_ids)

    # only runtime IDs that look like top IDs in this forum + static Artur/Ilya aliases
    wanted_runtime |= {57974, 13810, 59433, 59432, 59475, 58829, 58567}

    latest = None
    async for m in client.iter_messages(group_entity, limit=1):
        latest = int(m.id)
    if not latest:
        raise RuntimeError('Cannot detect latest message id')

    # collect last 20 per topic via per-id safe fetches
    buckets = defaultdict(list)
    scanned = 0
    fetch_errors = 0
    low = max(1, latest - 12000)

    for msg_id in range(latest, low, -1):
        done = all(len(buckets[t]) >= 20 for t in wanted_runtime)
        if done:
            break
        try:
            msg = await client.get_messages(group_entity, ids=msg_id)
            if not msg:
                continue
            scanned += 1
            t = mod.extract_topic_id(msg)
            if t in wanted_runtime and len(buckets[t]) < 20:
                buckets[t].append(msg)
        except Exception:
            fetch_errors += 1
            continue

    report = {
        'started_at': int(time.time()),
        'wanted_runtime_topics': sorted(list(wanted_runtime)),
        'scan': {'scanned_ids': scanned, 'fetch_errors': fetch_errors, 'latest_id': latest, 'low_bound': low},
        'topics': [],
        'totals': {'scanned_msgs': 0, 'sent_main': 0, 'sent_signal': 0, 'dropped': 0},
    }

    for topic_id in sorted(wanted_runtime):
        msgs = list(reversed(buckets.get(topic_id, [])))
        st = {
            'topic_id': topic_id,
            'title': topic_title_by_runtime.get(topic_id, f'topic:{topic_id}'),
            'collected': len(msgs),
            'processed': 0,
            'sent_main': 0,
            'sent_signal': 0,
            'dropped': 0,
        }
        for msg in msgs:
            st['processed'] += 1
            report['totals']['scanned_msgs'] += 1
            out = classify_and_send(group_id, topic_id, st['title'], msg, main_target, signal_target)
            if out['main']:
                st['sent_main'] += 1
                report['totals']['sent_main'] += 1
            if out['signal']:
                st['sent_signal'] += 1
                report['totals']['sent_signal'] += 1
            if (not out['main']) and (not out['signal']):
                st['dropped'] += 1
                report['totals']['dropped'] += 1
        report['topics'].append(st)

    report['finished_at'] = int(time.time())
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    client.loop.run_until_complete(run())
