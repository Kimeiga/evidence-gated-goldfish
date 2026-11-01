import unittest
from egg.gate import decide

GOOD = dict(tests_available=True,tests_passed=True,contracts_checked=True,
            contract_conflicts=[],neighbor_regressions=[],unresolved_critical_risks=[],
            high_impact_change=False)

class GateTests(unittest.TestCase):
    def test_clean_stops(self):
        self.assertEqual(decide(GOOD)['action'], 'stop_extra_review')

    def test_missing_evidence_verifies(self):
        self.assertEqual(decide({**GOOD, 'tests_available':False})['action'], 'verify')
        self.assertEqual(decide({**GOOD, 'contracts_checked':False})['action'], 'verify')

    def test_failed_tests_escalate(self):
        self.assertEqual(decide({**GOOD,'tests_passed':False})['action'], 'escalate')

    def test_contract_conflict_escalates_even_when_green(self):
        self.assertEqual(decide({**GOOD,'contract_conflicts':['bad status code']})['action'], 'escalate')

    def test_high_impact_escalates(self):
        self.assertEqual(decide({**GOOD, 'high_impact_change':True})['action'], 'escalate')

    def test_missing_or_invalid_fields_fail(self):
        with self.assertRaises(ValueError):
            decide({})
        with self.assertRaises(ValueError):
            decide({**GOOD,'tests_passed':'true'})
