# Agent architecture-review benchmark

**Status:** Benchmark fixture created and locally validated; **five native agent runs have NOT been performed**. A local coding-agent CLI and hosted subagents were unavailable in the preparation environment, so no claims of comparative defect-detection performance or token cost are made.

- `RUNBOOK.md` is the reproducible blind evaluation protocol.
- `PROTOCOL_AUDIT.md` reports verified source-based workflow differences.
- `case/` contains a flawed webhook delivery design, the product requirements, and implementation tasks.
- The private `answer-key/` from the earlier benchmark archive is deliberately **excluded from this repository**. It contains 14 seeded defects and four intentional non-issues; `control/` provides a clean control case without intentionally seeded violations.
- `prepare.py` creates isolated copies of the public fixture so that reviewers cannot see the answer key.
- `scoring/score.py` scores human-adjudicated reviewer findings; it does not invent results or use keyword-matching shortcuts.

Quick fixture setup: `python prepare.py egm` (flawed), or `python prepare.py egm --scenario control` (clean control). Use bmad, spec-kit, openspec, or superpowers similarly.
Scoring annotations now identify each trial and scenario separately, preventing clean-control false positives from distorting flawed-case precision.
To score, keep the answer key outside the repository and set `EGG_ARCH_ANSWER_KEY` to its `seeded-issues.json` path, then run `python scoring/score.py annotations.csv`. No reviewer should be able to read the key.
