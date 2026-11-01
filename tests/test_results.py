import tempfile
import unittest
from pathlib import Path
from egg.results import summarize,parse_jsonl

class ResultsTests(unittest.TestCase):
    def test_includes_failures_in_cost(self):
        rows = [
            {"run_id":"1","task_id":"x","arm":"baseline","verified_success":False,"cost_usd":.03,"wall_seconds":30,"human_minutes":1},
            {"run_id":"2","task_id":"x","arm":"baseline","verified_success":True,"cost_usd":.02,"wall_seconds":30,"human_minutes":1},
        ]
        s = summarize(rows)['baseline']
        self.assertEqual(s['passes'], 1)
        self.assertAlmostEqual(s['cost_per_verified_pass_usd'], .05)
        self.assertEqual(s['human_minutes_per_verified_pass'], 2)

    def test_zero_success_has_undefined_cost(self):
        rows = [{"run_id":"x","task_id":"t","arm":"baseline","verified_success":False,"cost_usd":1,"wall_seconds":30,"human_minutes":0}]
        self.assertIsNone(summarize(rows)['baseline']['cost_per_verified_pass_usd'])

    def test_reject_duplicate_run_id(self):
        import json
        row = {"run_id":"x","task_id":"t","arm":"baseline","verified_success":True,"cost_usd":1,"wall_seconds":30,"human_minutes":0}
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'rows.jsonl'
            p.write_text(json.dumps(row)+'\n'+json.dumps(row)+'\n')
            with self.assertRaises(ValueError):
                parse_jsonl(p)
