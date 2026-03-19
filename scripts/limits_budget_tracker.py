#!/usr/bin/env python3
import argparse, json, time
from pathlib import Path


def load_json(p: Path, default):
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--event', default='analysis_call', help='analysis_call|batch|delta|large_context')
    ap.add_argument('--units', type=int, default=None)
    args = ap.parse_args()

    cfg = load_json(Path(args.config), {})
    state_file = Path(cfg.get('state_file', '/tmp/limits_budget_state.json'))
    reports_dir = Path(cfg.get('reports_dir', '/tmp'))
    reports_dir.mkdir(parents=True, exist_ok=True)

    st = load_json(state_file, {
        'week_start_ts': int(time.time()),
        'spent_units': 0,
        'events': []
    })

    weights = cfg.get('weights', {})
    ev_map = {
        'analysis_call': 'analysis_call',
        'batch': 'batch_bonus',
        'delta': 'delta_bonus',
        'large_context': 'large_context_penalty'
    }
    key = ev_map.get(args.event, 'analysis_call')
    delta = args.units if args.units is not None else int(weights.get(key, 0))

    st['spent_units'] = max(0, int(st.get('spent_units', 0)) + delta)
    st.setdefault('events', []).append({'ts': int(time.time()), 'event': args.event, 'delta': delta, 'spent': st['spent_units']})

    budget = int(cfg.get('weekly_budget_units', 100))
    used_pct = int(round((st['spent_units'] / max(1, budget)) * 100))

    crossed = []
    for t in cfg.get('warn_thresholds', [15, 30, 50, 70, 85, 95]):
        if used_pct >= int(t):
            crossed.append(int(t))

    state_file.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding='utf-8')

    rep = {
        'ts': int(time.time()),
        'mode': 'limits_budget_tracker',
        'event': args.event,
        'delta_units': delta,
        'spent_units': st['spent_units'],
        'weekly_budget_units': budget,
        'used_pct': used_pct,
        'crossed_thresholds': crossed[-1:] if crossed else []
    }
    out = reports_dir / f"limits_budget_{rep['ts']}.json"
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'report': str(out), **rep}, ensure_ascii=False))


if __name__ == '__main__':
    main()
