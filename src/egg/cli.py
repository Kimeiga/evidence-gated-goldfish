"""Local experiment tools. No external model endpoints are called."""
import argparse
import json
from . import budget, gate, results


def main(argv=None):
    parser = argparse.ArgumentParser(prog='egg')
    commands = parser.add_subparsers(dest='command', required=True)

    b = commands.add_parser('budget', help='Maintain a local spending reservation ledger')
    b.add_argument('operation', choices=('init','status','reserve','finish'))
    b.add_argument('--ledger', default=str(budget.DEFAULT_PATH))
    b.add_argument('--id')
    b.add_argument('--phase', choices=tuple(budget.PHASE_CAPS))
    b.add_argument('--usd', type=str)
    b.add_argument('--actual-usd', type=str)

    g = commands.add_parser('gate', help='Decide whether to verify, escalate, or stop')
    g.add_argument('--input', required=True)

    r = commands.add_parser('results', help='Summarize externally adjudicated manifests')
    r.add_argument('--input', required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == 'budget':
            if args.operation == 'init':
                state = budget.init(args.ledger)
            else:
                state = budget.load(args.ledger)
                if args.operation == 'reserve':
                    if not all((args.id, args.phase, args.usd)):
                        parser.error('budget reserve requires --id, --phase, --usd')
                    budget.reserve(state, args.id, args.phase, args.usd)
                    budget.save(args.ledger, state)
                elif args.operation == 'finish':
                    if not args.id or args.actual_usd is None:
                        parser.error('budget finish requires --id, --actual-usd')
                    budget.finish(state, args.id, args.actual_usd)
                    budget.save(args.ledger, state)
            output = budget.summary(state)
        elif args.command == 'gate':
            with open(args.input, encoding='utf-8') as fh:
                output = gate.decide(json.load(fh))
        else:
            output = results.summarize(results.parse_jsonl(args.input))
        print(json.dumps(output, indent=2))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f'error: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
