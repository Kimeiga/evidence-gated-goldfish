"""Outcome summaries from externally adjudicated run manifests."""
from collections import defaultdict
import json
from pathlib import Path

ARMS = {'baseline', 'equal-budget', 'evidence-gated'}


def parse_jsonl(path):
    rows = []
    for lineno, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if row['arm'] not in ARMS:
                raise ValueError(f"unknown arm {row['arm']!r}")
            if type(row['verified_success']) is not bool:
                raise ValueError('verified_success must be boolean')
            for field in ('cost_usd', 'wall_seconds', 'human_minutes'):
                if not isinstance(row[field], (float,int)) or isinstance(row[field], bool) or row[field] < 0:
                    raise ValueError(f'{field} must be a nonnegative number')
            if not row['run_id'] or not row['task_id']:
                raise ValueError('run_id and task_id are required')
            rows.append(row)
        except (ValueError, KeyError, TypeError) as e:
            raise ValueError(f'Invalid manifest row {lineno}: {e}') from e
    ids = [r['run_id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate run_id detected')
    return rows


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row['arm']].append(row)
    output = {}
    for arm, items in sorted(groups.items()):
        attempts = len(items)
        passes = sum(1 for x in items if x['verified_success'])
        cost = sum(x['cost_usd'] for x in items)
        human = sum(x['human_minutes'] for x in items)
        wall = sum(x['wall_seconds'] for x in items) / 60
        output[arm] = {
            'attempts': attempts, 'tasks': len({x['task_id'] for x in items}),
            'passes': passes, 'pass_rate': round(passes / attempts, 4),
            'total_cost_usd': round(cost, 6),
            'cost_per_verified_pass_usd': round(cost / passes, 6) if passes else None,
            'human_minutes_per_verified_pass': round(human / passes, 3) if passes else None,
            'wall_minutes_per_verified_pass': round(wall / passes, 3) if passes else None
        }
    return output
