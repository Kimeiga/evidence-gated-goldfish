import unittest
from unittest.mock import patch
from egg import local_llm


class LocalModelTests(unittest.TestCase):
    def test_fixture_never_reads_hidden_answer_key(self):
        flawed = local_llm.fixture_text("flawed")
        control = local_llm.fixture_text("control")
        self.assertIn("R1.", flawed)
        self.assertIn("202 Accepted", flawed)
        self.assertIn("R1.", control)
        self.assertIn("durable", control.lower())
        with self.assertRaises(ValueError):
            local_llm.fixture_text("../../answer-key")

    def test_review_styles_distinct(self):
        fixture = local_llm.fixture_text("flawed")
        a = local_llm.make_review_prompt(fixture, "direct")
        b = local_llm.make_review_prompt(fixture, "contract-guided")
        self.assertNotEqual(a, b)
        self.assertIn("R12.", b)
        self.assertIn("observable", b)
        with self.assertRaises(ValueError):
            local_llm.make_review_prompt(fixture, "egm")

    def test_invalid_scenario_rejected(self):
        with self.assertRaises(ValueError):
            local_llm.scenarios_from_option("anything")
        self.assertEqual(local_llm.scenarios_from_option("both"), ["flawed", "control"])

    def test_generation_uses_local_loopback_and_bounded_output(self):
        reply = {
            "done": True,
            "done_reason": "stop",
            "response": "A failure is confirmed.",
            "prompt_eval_count": 54,
            "eval_count": 5,
            "prompt_eval_duration": 1000000000,
            "eval_duration": 2000000000,
            "model": "qwen3:4b-instruct",
        }
        with patch.object(local_llm, "local_json", return_value=reply) as fake:
            out = local_llm.generate("qwen3:4b-instruct", "Review the code", 64)
        self.assertEqual(out["output_tokens"], 5)
        self.assertEqual(out["eval_seconds"], 2)
        args, kwargs = fake.call_args
        self.assertEqual(args, ("POST", "/api/generate"))
        self.assertEqual(kwargs["payload"]["think"], False)
        self.assertEqual(kwargs["payload"]["options"]["num_predict"], 64)
        self.assertEqual(local_llm.HOST, "http://127.0.0.1:11434")

    def test_empty_response_fails(self):
        with patch.object(local_llm, "local_json", return_value={"done": True, "response": ""}):
            with self.assertRaises(RuntimeError):
                local_llm.generate("qwen3:4b-instruct", "abc")

    def test_model_whitelist_prevents_cloud_or_unbounded_models(self):
        for name in ("qwen3:235b", "gemma4:cloud", "gpt-6"):
            with self.assertRaises(ValueError):
                local_llm.generate(name, "hello")
        with self.assertRaises(ValueError):
            local_llm.generate("qwen3:1.7b", "test", max_tokens=1000)
