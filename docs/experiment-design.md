# Preregistered pilot design (draft, freeze before first measured run)

## Decision

Choose the cheapest workflow that preserves or improves correctness on our real coding tasks while reducing manual intervention. The candidate is *Evidence-Gated Goldfish*; there is no privileged winner.

## Pilot phases

1. **Framework screening** ($5 ceiling): Run EGM, BMAD, Spec Kit, OpenSpec and Superpowers on the same intentionally flawed architecture document and clean control. Use each genuine native review command where its prerequisites are met. Note mismatched scopes. Record issue recall, false positives, wall time, and actual cost. No inference on implementation quality from design-only review.
2. **Primary comparison** ($20 ceiling): preselect ~12 tasks by category and difficulty. Each task has an unmodified repository snapshot, exact request, hidden acceptance tests (unavailable to agents), and neighboring regression checks. Run two independent attempts per arm: `baseline`, `equal-budget`, `evidence-gated`. Run arms in randomized order within task, on the same model/reasoning capability and tool access, with isolated state. Adjust the number of trials to remain within budget, preserving arm balance.
3. **Contingency** ($5): repeat uncertain or failed runs only under a rule fixed before inspection; otherwise do not spend.

## Task categories

- **Small behavior fix**: e.g. Kiokun UI or pictograph mapping rule. Hidden tests cover exact observable behavior.
- **Neighbor regression**: e.g. Perfect Web recipe changes; the hidden suite verifies adjacent hosts and components.
- **Protocol/state invariants**: e.g. Twinwire timing and compatibility; simulate delayed/reordered inputs and forged timestamps.
- **Architecture/spec review**: e.g. LevelSpec evidence verification; reviewers must find authentic missing trust boundaries and explain consequences.

The named projects are examples of suitable tasks, not permission to make changes to them during benchmarking. Use personal repositories and fixed commits; do not copy proprietary employer code into the benchmark.

## Methods and controls

- **Unit of analysis:** (task, arm, independent seed/attempt). Report per-task differences, not only pooled runs; do not treat repeat attempts as independent tasks.
- **Randomization:** preregister a fixed seed and randomize arm order within each task. No shared previous candidate output or test feedback between runs.
- **Fresh context:** critical for EGM and independent critics. Session transcripts or summaries must not leak into subsequent reviewers. Use true independent subagents; if unavailable, mark the native run not executed.
- **Budget parity:** `equal-budget` receives the same permitted total dollar ceiling as the candidate; record actual usage separately. Total-budget parity and identical token counts are not the same.
- **Ground truth:** hidden tests + independently reviewed contract outcomes; do not grade a task from a reviewer self-report. Existing tests remain mandatory as regression checks.
- **Blind grading:** human reviewer sees anonymous diffs, tests, and behavior, not arm labels. Pre-identify exceptions where the diff reveals a workflow artifact.
- **Stopping:** halt new paid runs when the reserved phase budget is exhausted. Do not choose early stopping based on which arm is winning.

## Metrics

- `verified_success`: all hidden acceptance and required regression tests pass, with no independently confirmed critical defect; otherwise false.
- `cost_per_success`: total measured billed model cost, including failures, divided by verified successful runs. Undefined when no runs succeed.
- `pass_rate`: verified successes / completed attempts.
- `human_minutes_per_success`: total measured human steering, approval, and review time divided by verified successes.
- `elapsed_minutes_per_success`: sum of wall times divided by verified successes.
- Review-specific `recall`, `precision`, `critical_recall` using the manually adjudicated hidden-key benchmark.

Do not aggregate the design-review scores with coding-task pass rates. Report separate outcome dimensions.

## Success criteria and uncertainty

The **pilot screening threshold**, not a statistical guarantee: target >=30% lower cost per verified success than the baseline and equal-budget control, with no observed increase in critical regressions or human effort and no material drop in pass rate. If fewer than ~10 informative tasks separate the arms, mark result inconclusive rather than declaring victory.

A small pilot cannot establish global novelty or generalization. A promising signal justifies a larger, preregistered out-of-sample study with uncertainty intervals and an external prior-art review.

## Auditability

For each attempt preserve: task id, category, repo commit, framework version, model id, reasoning setting, git diff hash, prompt hash, raw test output, input/output tokens, cache, billed cost, wall time, number of subagent calls, human minutes, and outcome. Prompt/trace artifacts can contain secrets; retain locally in protected storage, not in public Git history.
