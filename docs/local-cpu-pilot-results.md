# Local CPU inference: measured feasibility pilot

Date: 2026-11-01. Repository: [Kimeiga/evidence-gated-goldfish](https://github.com/Kimeiga/evidence-gated-goldfish).

## Setup

- Workflow: `.github/workflows/local-cpu-model.yml`, `ubuntu-24.04`, public-repository standard runner.
- Model: Ollama `qwen3:4b-instruct`, sha256 `0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0`.
- Local loopback API only, `OLLAMA_NO_CLOUD=1`; model API charge: $0.
- All outputs are *read-only design reviews*, not native EGM/BMAD/Spec Kit/OpenSpec/Superpowers runs.
- This test did not generate or edit production code.

## Experiment 1: Broad architecture review prompts

[Successful Actions run](https://github.com/Kimeiga/evidence-gated-goldfish/actions/runs/41362848923)

| Metric | Observed |
|---|---:|
| Prompt calls completed | 4 |
| Input tokens | 6,924 |
| Output tokens | 644 |
| Model inference wall time | 279.88 seconds |
| Model API charges | $0 |

Findings from inspecting the actual generated answers:

- Direct review of the flawed design identified the durable-acknowledgment and changing-delivery-ID defects, but reached its 320-token output cap.
- Direct review of the clean control produced unsupported objections, including confusing at-least-once duplicate delivery with loss of durable acknowledgment.
- Contract-guided review returned `NONE` after only two output tokens on **both** designs, failing to identify obvious contradictions in the flawed design.

These are qualitative observations, not a scored review-precision/recall benchmark.

## Experiment 2: Two scoped requirements, both designs

[Successful Actions run](https://github.com/Kimeiga/evidence-gated-goldfish/actions/runs/41363732116)

Four model calls each receive exactly one requirement and the matching design section. The expected outcomes are publicly known calibration labels, **not** the private 14-defect answer key.

| Case | Requirement | Expected | Model answered | Match |
|---|---|---|---|---|
| Flawed | R1: durable acknowledgment | VIOLATION | SATISFIED | No |
| Flawed | R2: stable delivery ID | VIOLATION | VIOLATION | Yes |
| Control | R1: durable acknowledgment | SATISFIED | SATISFIED | Yes |
| Control | R2: stable delivery ID | SATISFIED | SATISFIED | Yes |

- **3/4** reference outcomes matched.
- Input tokens: **1,363**; output tokens: **136**.
- Model inference wall time: **38.94 seconds**.
- Model API charges: **$0**.

The scoped approach reduced measured inference work compared with broad prompts on these tasks, but still missed an important real defect. This experiment cannot establish a general cost/quality improvement.

## Interpretation

**Infrastructure feasibility: demonstrated.** A public GitHub Actions standard CPU runner can install Ollama, download a quantized model, generate multiple responses, and upload auditable outputs with no external model API charges.

**Quality superiority: not demonstrated.** The tested local 4B model missed a critical violation and produced unsupported conclusions. The existing Evidence-Gated Goldfish research question remains open. Do not use these outputs as proof that a cheaper agent would produce safer production changes.

Follow-up research should use unseen coding tasks, hidden acceptance/regression tests, the same task/model budget per arm, and independent adjudication. Larger models or more structured validation can be tested, but their utility must be measured rather than assumed.

References: [GitHub public-runner specifications](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job), [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions), [GitHub Actions terms](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features), [Ollama API](https://docs.ollama.com/api/generate).
