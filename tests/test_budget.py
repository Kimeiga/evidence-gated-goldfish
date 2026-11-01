import tempfile
import unittest
from pathlib import Path
from egg import budget

class BudgetTests(unittest.TestCase):
    def test_init_and_phase_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'budget.json'
            state = budget.init(path)
            budget.reserve(state, 'a', 'screening', '4.99')
            with self.assertRaises(budget.BudgetError):
                budget.reserve(state, 'b', 'screening', '.02')
            budget.finish(state, 'a', '1.00')
            budget.reserve(state, 'c', 'screening', '4.00')
            self.assertEqual(budget.summary(state)['phase_usage_usd']['screening'], '5.000000')

    def test_over_reservation_accounted_not_silenced(self):
        state = budget.init(Path(tempfile.mkdtemp()) / 'ledger.json')
        budget.reserve(state, 'r1', 'screening', '1')
        budget.finish(state, 'r1', '6')
        self.assertEqual(budget.summary(state)['over_reservation_run_ids'], ['r1'])
        with self.assertRaises(budget.BudgetError):
            budget.reserve(state, 'r2', 'screening', '.01')

    def test_reject_duplicate_and_invalid_amounts(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = budget.init(Path(tmp)/'ledger.json')
            for amount in ('NaN', 'Infinity', '-1'):
                with self.assertRaises(budget.BudgetError):
                    budget.reserve(state, amount, 'screening', amount)
            budget.reserve(state, 'r', 'screening', '.10')
            with self.assertRaises(budget.BudgetError):
                budget.reserve(state, 'r', 'screening', '.01')

    def test_persists_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'ledger.json'
            state = budget.init(path)
            budget.reserve(state, 'run-1', 'primary', '.12')
            budget.save(path, state)
            self.assertEqual(budget.load(path)['runs']['run-1']['phase'], 'primary')
