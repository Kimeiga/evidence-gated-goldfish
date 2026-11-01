# Experiment prompt contracts

Each arm receives **exactly the same task brief** and repository snapshot. Attach only the arm-specific instructions below. Use tool-native skill installations for the five framework screening conditions. Do not claim a prompt imitation is a native framework run.

- `baseline.md`: no supplementary instructions, except a uniform output/reporting schema shared by all arms.
- `equal-budget.md`: no additional methodology; allow extra reasoning or retries up to the same reserved cost as evidence-gated.
- `evidence-gated.md`: candidate workflow including independent review only on an evidence trigger.

Keep hidden tests and ground-truth answer keys outside the agent's files, API prompts, and tool read access. Stopping at green visible tests does **not** prove task correctness; the hidden harness is the final judge.
