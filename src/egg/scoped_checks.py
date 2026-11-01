"""A small, falsifiable test of requirement-scoped local model verification.

These two public checks are calibration tasks, not the hidden benchmark key.
They do not establish performance on full coding-agent or design-review tasks.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from .local_llm import FIXTURE, MODELS, generate, local_model_digest

# Requirement IDs and document sections were selected before the model runs.
SCOPES = (("R1", "API and persistence"), ("R2", "Workers and scheduling"))
# Public, manually obvious sanity-check labels. Not the private 14-defect key.
EXPECTED = {"flawed": True, "control": False}


def requirement_text(case: str, requirement_id: str) -> str:
    if case not in EXPECTED or requirement_id not in {r for r, _ in SCOPES}:
        raise ValueError("Unsupported sanity-check case or requirement")
    root = FIXTURE / ("case" if case == "flawed" else "control")
    source = (root / "requirements.md").read_text(encoding="utf-8")
    match = re.search(rf"(?m)^{re.escape(requirement_id)}\.\s+(.+)$", source)
    if not match:
        raise ValueError(f"Cannot locate {requirement_id} in requirements")
    return match.group(1)


def design_section(case: str, title: str) -> str:
    if case not in EXPECTED or title not in {t for _, t in SCOPES}:
        raise ValueError("Unsupported sanity-check section")
    root = FIXTURE / ("case" if case == "flawed" else "control")
    document = (root / "design.md").read_text(encoding="utf-8")
    marker = f"## {title}\n"
    if marker not in document:
        raise ValueError(f"Section missing: {title}")
    return document.split(marker, 1)[1].split("\n## ", 1)[0].strip()


def scoped_prompt(requirement_id: str, requirement: str, design: str) -> str:
    return (
        "You are checking ONE explicit software contract against ONE design excerpt. "
        "Check whether the design actually contradicts the contract. "
        "A compliant design may mention failures as valid at-least-once behavior. "
        "Do not invent requirements or review other sections.\n"
        "Reply with exactly two lines:\n"
        "VERDICT: VIOLATION or VERDICT: SATISFIED\n"
        "EVIDENCE: one specific fact (up to 25 words).\n"
        f"CONTRACT {requirement_id}: {requirement}\n"
        f"DESIGN EXCERPT:\n{design}\n"
    )


def parse_verdict(output: str) -> str | None:
    matched = re.search(r"(?im)^\s*VERDICT:\s*(VIOLATION|SATISFIED)\s*$", output)
    return matched.group(1).upper() if matched else None


def run(model: str, directory: Path) -> dict:
    if model not in MODELS:
        raise ValueError("Unsupported model")
    directory.mkdir(parents=True, exist_ok=True)
    digest = local_model_digest(model)
    if not digest:
        raise RuntimeError("Specified model has not been downloaded")
    rows = []
    for case in ("flawed", "control"):
        for identifier, section in SCOPES:
            prompt = scoped_prompt(
                identifier,
                requirement_text(case, identifier),
                design_section(case, section),
            )
            print(f"Scoped check case={case} requirement={identifier}", flush=True)
            generation = generate(model, prompt, max_tokens=96)
            verdict = parse_verdict(generation["response"])
            correct = verdict == ("VIOLATION" if EXPECTED[case] else "SATISFIED")
            result = {
                "scenario": case,
                "requirement": identifier,
                "model": model,
                "model_digest": digest,
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "observed_verdict": verdict,
                "reference_verdict": "VIOLATION" if EXPECTED[case] else "SATISFIED",
                "correct": correct,
                "response": generation["response"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source_revision": os.environ.get("GITHUB_SHA", "local"),
                "model_api_charge_usd": 0,
                **{k: v for k, v in generation.items() if k != "response"},
            }
            rows.append(result)
            (directory / f"{case}-{identifier}.json").write_text(
                json.dumps(result, indent=2) + "\n", encoding="utf-8"
            )
            print(
                f"Verdict={verdict!r} expected={result['reference_verdict']} "
                f"match={correct}, {result['wall_seconds']}s",
                flush=True,
            )
    tally = sum(row["correct"] for row in rows)
    report = {
        "model": model,
        "model_digest": digest,
        "checks": len(rows),
        "matched_reference": tally,
        "input_tokens": sum(int(row["prompt_tokens"] or 0) for row in rows),
        "output_tokens": sum(int(row["output_tokens"] or 0) for row in rows),
        "inference_seconds": round(sum(row["wall_seconds"] for row in rows), 2),
        "api_charge_usd": 0,
        "qualified_claim": "Two public requirements only; not a five-framework comparison",
    }
    (directory / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = [
        "## Local CPU scoped contract checks",
        "",
        f"- Model: `{model}`",
        f"- Reference matches: **{tally}/{len(rows)}** (two known public requirements, not hidden tests)",
        f"- Input/output tokens: {report['input_tokens']}/{report['output_tokens']}",
        f"- Inference: {report['inference_seconds']} seconds; LLM API: $0",
        "",
        "| Design | Requirement | Model verdict | Reference | Match |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        md.append(
            f"| {row['scenario']} | {row['requirement']} | "
            f"{row['observed_verdict'] or 'UNPARSABLE'} | {row['reference_verdict']} | "
            f"{'Yes' if row['correct'] else 'No'} |"
        )
    text = "\n".join(md) + "\n"
    (directory / "summary.md").write_text(text, encoding="utf-8")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as out:
            out.write(text)
    print(json.dumps(report, indent=2), flush=True)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=MODELS, default="qwen3:4b-instruct")
    parser.add_argument("--output", type=Path, default=Path("results/local-scoped"))
    args = parser.parse_args(argv)
    try:
        run(args.model, args.output)
        return 0
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"SCOPED CHECK FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
