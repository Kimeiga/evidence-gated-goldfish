# Evidence-Gated Goldfish

An experiment in **cost-aware coding agents**: can a single coding agent plus selective, evidence-triggered independent review produce more *verified correct changes per dollar* than default coding agents and heavyweight skill frameworks?

**Status: research scaffold, not a validated new method.** The framework workflows have **not** been run here. No claim of novelty or improved coding performance is established.

## The hypothesis

Most tasks should start with one coding agent. We record explicit user-facing contracts, implement once, then choose the *next* action using evidence:

1. Check contracts, tests, and relevant neighboring behavior.
2. If evidence is missing, obtain verification, not more brainstorming.
3. If evidence contradicts the implementation, assign an **independent, fresh-context critic** a targeted question and demand a reproducible counterexample.
4. Repair only a verified defect, then recheck. Stop escalation when the evidence is clean, subject to a separate high-risk gate.

The control arm gets **equal budget** to spend on the model with higher reasoning effort, so a gain cannot be attributed merely to additional tokens.

## Experiment arms

| Arm | Behavior |
| --- | --- |
| `baseline` | Ordinary coding agent. No additional instructions. |
| `equal-budget` | Same task, same model, additional reasoning budget but no framework. |
| `evidence-gated` | Cheap contract extraction, ordinary implementation, verification gate, targeted fresh-context criticism only when triggered. |

Before the primary experiment, screen **EGM, BMAD, Spec Kit, OpenSpec and Superpowers** on the architecture fixture. Native workflows must actually run; loading a prompt alone does not count. These frameworks are not functional equivalents, and their results should not be interpreted as an identical-capability leaderboard.

## Budget

Planning envelope: **$30**, divided into **$5 framework screen**, **$20 focused comparison**, **$5 contingency**. These are ceilings, **not quotes**. API pricing, available credits, and per-run usage vary. Run plans must fit in a reserved amount before submitting a paid call. Configure provider-side spending limits as well: the local ledger **cannot enforce an absolute billing cap** on providers or on a request that exceeds its reservation.

```
python -m egg budget init
python -m egg budget reserve --id pilot-01 --phase screening --usd 0.50
python -m egg budget finish --id pilot-01 --actual-usd 0.18
python -m egg budget status
```

Run from repository root after `export PYTHONPATH=src`, or install locally with `python -m pip install -e .`. Local budget and result files live under `.runs/` and are ignored by Git. No command in this project calls a model or incurs API charges.

## Reproducible first steps

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m egg gate --input examples/evidence-clean.json
python -m egg gate --input examples/evidence-uncertain.json
python -m egg results --input examples/results.sample.jsonl
python benchmarks/architecture-review/prepare.py egm
```

The last command creates a disposable isolated fixture. For the complete five-framework protocol, see [`benchmarks/architecture-review/RUNBOOK.md`](benchmarks/architecture-review/RUNBOOK.md).

## What we measure

**Primary:** cost per *externally verified successful change* on unseen tasks, with failed attempts included in the denominator. **Guardrails:** correctness/pass rate, critical regressions, human intervention minutes, and wall time. Compare independent attempts at pinned repository revisions with private hidden tests and blinded adjudication. See [`docs/experiment-design.md`](docs/experiment-design.md).

For the first pilot, select approximately 12 tasks across small bug fixes, cross-component regressions, state/protocol changes, and architecture design. Two independent attempts per arm provide useful direction, not statistical proof. Fix the task set and evaluator before running any measured candidate. Do not choose test tasks from knowledge of the winning arm's outputs.

### Source material and safeguards

The architecture fixture adapts the five-framework benchmark prepared earlier. **Its hidden issue key is intentionally omitted from this repository**. Keep that key offline, outside review-agent workspaces. The included case is not yet a scored benchmark result.

This repository is public. Only sanitized example fixtures are included. Keep proprietary code, private project tasks, secrets, and hidden scoring keys outside this repository. CI only runs deterministic local tests; it never spends money on agents.

## Disqualifying outcomes

- The candidate performs worse on correctness or introduces a critical regression.
- The purported improvement comes from leaked test cases or an unequal token budget.
- Gains disappear when measured on unseen work or after accounting for human intervention.
- The result cannot be reproduced from logged models, revisions, tasks, prompts, and measured costs.

Related ideas, such as model cascades, adversarial review, test-gated agents, and reasoning-budget allocation, already exist. The specific routing policy is a **hypothesis**, not a claimed invention.
