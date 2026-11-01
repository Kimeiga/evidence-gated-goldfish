"""Local *reservation* ledger; provider spending limits must be enforced separately."""
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path

PHASE_CAPS = {"screening": Decimal("5.00"), "primary": Decimal("20.00"), "contingency": Decimal("5.00")}
TOTAL_CAP = sum(PHASE_CAPS.values())
DEFAULT_PATH = Path('.runs/budget.json')

class BudgetError(ValueError):
    pass


def money(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as e:
        raise BudgetError(f"Invalid dollar amount: {value!r}") from e
    if not amount.is_finite() or amount < 0:
        raise BudgetError('Dollar amount must be finite and nonnegative')
    return amount.quantize(Decimal('0.000001'))


def init(path=DEFAULT_PATH):
    path = Path(path)
    if path.exists():
        raise BudgetError(f'Ledger already exists at {path}; refusing to overwrite')
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {"currency": "USD", "total_cap": str(TOTAL_CAP),
             "phase_caps": {k: str(v) for k, v in PHASE_CAPS.items()}, "runs": {}}
    save(path, state)
    return state


def load(path=DEFAULT_PATH):
    path = Path(path)
    if not path.exists():
        raise BudgetError(f'No ledger at {path}. Run budget init first.')
    state = json.loads(path.read_text(encoding='utf-8'))
    if state.get('currency') != 'USD' or 'runs' not in state:
        raise BudgetError('Invalid ledger format')
    return state


def save(path, state):
    """Atomic replace for single-process usage. Do not run concurrent writers."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    temporary.replace(path)


def usage(state, phase=None):
    """Count actual spending plus outstanding reservations, never just successes."""
    return sum((money(x['actual_usd'] if x['status'] == 'finished' else x['reserved_usd'])
                for x in state['runs'].values() if phase is None or x['phase'] == phase),
               Decimal('0'))


def reserve(state, run_id, phase, usd):
    if phase not in PHASE_CAPS:
        raise BudgetError('Unknown phase')
    if not run_id or run_id in state['runs']:
        raise BudgetError('Run id must be unique and nonempty')
    amount = money(usd)
    if amount == 0:
        raise BudgetError('Cannot reserve zero dollars')
    if usage(state, phase) + amount > money(state['phase_caps'][phase]):
        raise BudgetError(f'{phase} phase cap would be exceeded')
    if usage(state) + amount > money(state['total_cap']):
        raise BudgetError('Total cap would be exceeded')
    state['runs'][run_id] = {"phase": phase, "reserved_usd": str(amount), "status": "reserved"}
    return state


def finish(state, run_id, usd):
    try:
        row = state['runs'][run_id]
    except KeyError as e:
        raise BudgetError('Unknown run') from e
    if row['status'] != 'reserved':
        raise BudgetError('Run already finished; refusing to double-count')
    actual = money(usd)
    row['status'] = 'finished'
    row['actual_usd'] = str(actual)
    # Accounting cannot roll back a bill. Flag overages; subsequent reservations
    # fail once the phase or total usage exceeds the declared cap.
    row['over_reservation'] = actual > money(row['reserved_usd'])
    return state


def summary(state):
    return {"cap_usd": state['total_cap'],
            "committed_usd": str(usage(state)),
            "remaining_usd": str(max(Decimal('0'), money(state['total_cap']) - usage(state))),
            "phase_usage_usd": {k: str(usage(state, k)) for k in PHASE_CAPS},
            "over_reservation_run_ids": sorted(k for k,v in state['runs'].items() if v.get('over_reservation')),
            "run_count": len(state['runs'])}
