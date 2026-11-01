#!/usr/bin/env python3
"""Score human-adjudicated design-review findings by framework, trial and scenario.

CSV columns: framework,trial,scenario,issue_id,outcome,description
  scenario: flawed or control
  outcome: tp (confirmed seeded defect), fp (unsupported), note (valid non-seeded
           observation), duplicate (repeated finding; excluded from precision).

The answer key must be kept out of reviewer workspaces. All classifications
must be made by an independent evaluator before running this scorer.
"""
import argparse
import csv
import json
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
def read_issue_key():
    key = os.environ.get('EGG_ARCH_ANSWER_KEY')
    if not key:
        raise ValueError('Set EGG_ARCH_ANSWER_KEY to the private seeded-issues.json file; it is intentionally excluded from this repository.')
    path = Path(key)
    if not path.is_file():
        raise ValueError(f'Key file does not exist: {path}')
    issues = {issue['id']: issue for issue in json.loads(path.read_text())}
    if not issues:
        raise ValueError('Empty hidden issue key')
    return issues
FRAMEWORKS = {'egm', 'bmad', 'spec-kit', 'openspec', 'superpowers'}
SCENARIOS = {'flawed', 'control'}
OUTCOMES = {'tp', 'fp', 'note', 'duplicate'}


def grade(rows, issues):
    critical = {issue_id for issue_id, value in issues.items() if value['severity'] == 'critical'}
    buckets = defaultdict(lambda: {
        'tp_ids': set(), 'false_positives': 0, 'notes': 0,
        'duplicates': 0, 'annotations': 0,
    })
    for number, row in enumerate(rows, 2):
        framework = (row.get('framework') or '').strip().lower()
        trial = (row.get('trial') or '').strip() or '1'
        scenario = (row.get('scenario') or '').strip().lower() or 'flawed'
        outcome = (row.get('outcome') or '').strip().lower()
        issue_id = (row.get('issue_id') or '').strip().upper()
        if framework not in FRAMEWORKS:
            raise ValueError(f'Row {number}: invalid framework {framework!r}')
        if scenario not in SCENARIOS:
            raise ValueError(f'Row {number}: invalid scenario {scenario!r}')
        if outcome not in OUTCOMES:
            raise ValueError(f'Row {number}: invalid outcome {outcome!r}')
        if outcome == 'tp' and scenario == 'control':
            raise ValueError(f'Row {number}: cannot assign seeded-defect TP to clean control')
        if outcome == 'tp' and issue_id not in issues:
            raise ValueError(f'Row {number}: invalid seeded defect ID {issue_id!r}')
        if outcome != 'tp' and issue_id:
            raise ValueError(f'Row {number}: only tp outcomes can reference seeded IDs')
        b = buckets[(framework, trial, scenario)]
        b['annotations'] += 1
        if outcome == 'tp':
            if issue_id in b['tp_ids']:
                b['duplicates'] += 1
            else:
                b['tp_ids'].add(issue_id)
        elif outcome == 'fp':
            b['false_positives'] += 1
        elif outcome == 'note':
            b['notes'] += 1
        else:
            b['duplicates'] += 1

    result = {}
    for (framework, trial, scenario), b in sorted(buckets.items()):
        tp = len(b['tp_ids'])
        fp = b['false_positives']
        if scenario == 'flawed':
            recall = tp / len(issues)
            precision = tp / (tp + fp) if tp + fp else None
            f1 = (2 * precision * recall / (precision + recall)
                  if precision is not None and precision + recall
                  else 0.0 if precision is not None else None)
            critical_recall = len(b['tp_ids'] & critical) / len(critical)
        else:
            recall = precision = f1 = critical_recall = None
        result[f'{framework}/{trial}/{scenario}'] = {
            'framework': framework, 'trial': trial, 'scenario': scenario,
            'issues_found': tp, 'issues_total': len(issues) if scenario == 'flawed' else 0,
            'false_positives': fp,
            'recall': round(recall, 3) if recall is not None else None,
            'critical_recall': round(critical_recall, 3) if critical_recall is not None else None,
            'precision': round(precision, 3) if precision is not None else None,
            'f1': round(f1, 3) if f1 is not None else None,
            'issue_ids': sorted(b['tp_ids']),
            'notes': b['notes'], 'duplicates': b['duplicates'],
            'annotations': b['annotations'],
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('annotations', type=Path)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    with args.annotations.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    result = grade(rows, read_issue_key())
    if not result:
        print('No adjudicated reviewer findings recorded; no quality scores available.')
        return
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{'Framework/trial/scenario':<32} {'Hits':>7} {'FP':>4} {'Recall':>8} {'Crit R':>8} {'Precision':>10}")
        for label, stats in result.items():
            percent = lambda v: 'n/a' if v is None else f'{v*100:.1f}%'
            hits = (f"{stats['issues_found']}/{stats['issues_total']}" if
                    stats['scenario'] == 'flawed' else 'n/a')
            print(f"{label:<32} {hits:>7} {stats['false_positives']:>4} "
                  f"{percent(stats['recall']):>8} {percent(stats['critical_recall']):>8} "
                  f"{percent(stats['precision']):>10}")


if __name__ == '__main__':
    main()
