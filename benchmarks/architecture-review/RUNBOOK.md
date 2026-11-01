# Reproducible architecture-review comparison: five frameworks

Date prepared: 2026-11-01. Source repositories: Google EGM, BMad Method, GitHub Spec Kit, Fission-AI OpenSpec, obra Superpowers.

## What this tests

This is an intentionally flawed design for a multi-tenant outbound webhook delivery feature. The five systems do not implement identical capabilities, so this benchmark tests the nearest available **pre-implementation design review / ambiguity finding** workflow rather than treating them as interchangeable full software-delivery systems.

The flawed case has 14 preseeded, testable defects and four intentional non-issues. A separate clean control design has no intentionally planted violations of the requirements. It is not guaranteed defect-free, so a human adjudicator must evaluate each finding before marking it false. The answer key is intentionally **not checked in**; keep the separately supplied prior benchmark answer key outside this repository and all reviewer workspaces. In the original archive it is under `answer-key/`; do NOT make it available to the reviewing agent. Only the human adjudicator should open it *after* review outputs are saved.

## Preparation

Run from this archive's root, separately for each framework:

```
python prepare.py egm
python prepare.py bmad
python prepare.py spec-kit
python prepare.py openspec
python prepare.py superpowers
```

To review the control, append `--scenario control` to each command, for example `python prepare.py egm --scenario control`. The command prints an **isolated temporary working directory** containing only the public fixture, not the answer key. Open a clean agent session for each run and run the system's own initialization/install flow as needed. Use the same coding agent, exact model, system permissions, and same time/token budget for all five runs. Keep web access off and do not let agents inspect the answer key or previous reviewers' output. Record the agent and framework versions for each run.

Recommended common prompt:

> Perform a read-only, pre-implementation review of `case/design.md` against `case/requirements.md` and `case/tasks.md`. Identify concrete design defects, missing decisions, operational risks, and false assumptions. Do not fix code or rewrite documents. Return actionable findings with a concise explanation and the exact section that supports each finding. Do not ask the author questions if the document already answers them. Favor real errors over stylistic criticism.

### Per-framework run instructions

- **EGM**: Install the official EGM plugin for the agent. Invoke `egm-review` with `case/design.md`, select **full review / consolidated report**, and include `case/requirements.md` and `case/tasks.md` as reviewer reading context. Must have real fresh subagents. If unavailable, mark `NOT RUN`: EGM explicitly disallows pretending a same-context review is a Goldfish review.
- **BMAD**: Install/setup BMad Method. Invoke `bmad-review` on `case/design.md`, with `case/requirements.md` and `case/tasks.md` as additional context, using the default applicable lenses. If the environment lacks subagents, flag fallback sequential execution in the result. Note the shipped adversarial lens asks for at least ten findings, which may affect false-positive rates.
- **Spec Kit**: Initialize a Spec Kit project and place the **unaltered** fixture material into its conventional spec, plan, and tasks locations for the feature. Invoke `speckit.analyze` in a fresh session. This examines cross-artifact consistency; it is not the same as an independent architecture critique. Document any conversion you had to make to match the required layout and do not alter substantive content. If feature prerequisites cannot be satisfied without generating changed artifacts, mark `NOT RUN` rather than substituting a different workflow.
- **OpenSpec**: Initialize OpenSpec for the project. Invoke `openspec-explore` with an explicit request to critique the *existing* three documents (read only), rather than `openspec-verify-change`, which checks **implemented code** against artifacts. This is a less structured comparison: OpenSpec has no direct equivalent of EGM's full review. Track that distinction.
- **Superpowers**: Install Superpowers. Run its **builder check** with a fresh general-purpose subagent using the exact `skills/brainstorming/builder-check-prompt.md` instructions, referring it to `case/design.md`, and provide requirements/tasks as context. Its criterion is whether a talented builder would still need high-impact answers, not whether every explicit decision is good. Avoid claiming this is equivalent to an EGM hostile design critique.

Save each **raw, unchanged** report separately as `results/<framework>-<scenario>.md` in the archive *after* leaving the reviewer's isolated working directory. Do not expose prior reports to subsequent reviewers.

## Metrics

1. **True-positive recall:** of 14 seeded defects, how many did the report identify as a meaningful problem?
2. **Precision:** confirmed distinct defects divided by confirmed distinct defects plus spurious findings on the flawed case. For the clean control, report the number of adjudicated unsupported findings separately. Mark duplicates as `duplicate`, and valid non-seeded observations as `note`, rather than treating them as extra detections.
3. **High-severity recall:** count critical IDs in `answer-key/seeded-issues.json`.
4. **Actionability:** can a developer state a concrete change or a necessary decision from the finding? Rate each on a 0-2 scale.
5. **Cost:** record actual measured wall time, model calls, input/output tokens, and monetary cost if the harness exposes them. Use `not available` rather than estimates for missing values.

After reviewers complete, have an independent evaluator map each unique finding to an issue ID from `answer-key/seeded-issues.json` or mark it `fp`. Do not let the model annotate its own outputs using the answer key. Record rows in a copy of `scoring/annotations-template.csv` with framework, trial (run number), scenario, issue_id, outcome, and description. The scorer separates the clean control and each repetition from the flawed case, reports critical recall, and excludes duplicates. A clean-control finding is classified as `fp` only after independent adjudication. `tp` is forbidden on controls; `note` records a valid non-seeded concern. Do not include the hidden answer key in any reviewer prompt. For comments that are accurate but outside the planted issues, record `note` and discuss them separately.

Then run:

```
EGG_ARCH_ANSWER_KEY=/safe/offline/seeded-issues.json python scoring/score.py your-annotations.csv
python -m unittest discover -s tests -v  # from repository root, deterministic pilot checks
```

The scorer deliberately prints no framework scores until real, human-adjudicated review findings are supplied. Run **both flawed and control** scenarios for all five frameworks. Re-run each at least 3 times with fresh isolated contexts before making reliability claims; one run measures only one sample. A finding against the clean control is not automatically false, as a non-seeded real concern may exist.

## Interpretation limits

Five frameworks are not five different models. Any quality differences are attributable to prompt/workflow plus the agent/model/harness interaction. Keep the model, review conditions, context access, and budget stable. A reviewer with four independent agents may cost more than one asking builder questions. Report cost and quality together. A static source inspection or an unblinded same-chat simulation cannot establish real defect detection rates.
