import unittest

from egg.scoped_checks import (
    EXPECTED,
    SCOPES,
    design_section,
    parse_verdict,
    requirement_text,
    scoped_prompt,
)


class ScopedChecksTests(unittest.TestCase):
    def test_public_reference_cases_are_explicit(self):
        self.assertEqual(EXPECTED, {"flawed": True, "control": False})
        self.assertEqual(len(SCOPES), 2)

    def test_scoped_inputs_keep_correct_requirement(self):
        for case in ("flawed", "control"):
            r1 = requirement_text(case, "R1")
            d1 = design_section(case, "API and persistence")
            r2 = requirement_text(case, "R2")
            d2 = design_section(case, "Workers and scheduling")
            self.assertIn("202 Accepted", r1)
            self.assertIn("delivery_id", r2)
            self.assertIn("Postgres", d1)
            self.assertIn("worker", d2.lower())
            self.assertNotIn("## Operations", d2)

    def test_prompt_has_one_requirement_and_one_section(self):
        prompt = scoped_prompt("R1", "MUST BE DURABLE", "Returns 202 too early")
        self.assertIn("CONTRACT R1: MUST BE DURABLE", prompt)
        self.assertNotIn("R2.", prompt)

    def test_parse_verdict(self):
        self.assertEqual(parse_verdict("VERDICT: VIOLATION\nEVIDENCE: x"), "VIOLATION")
        self.assertEqual(parse_verdict("VERDICT: SATISFIED\nEVIDENCE: x"), "SATISFIED")
        self.assertIsNone(parse_verdict("possibly wrong"))
