# Local CPU models on free GitHub Actions

**Implemented:** `.github/workflows/local-cpu-model.yml`

## Why this costs $0 in model API calls

The workflow installs Ollama, downloads quantized model weights, starts a service bound only to `127.0.0.1:11434`, and sends prompts to that **local** HTTP endpoint. `OLLAMA_NO_CLOUD=1` disables cloud models and web search. No external inference API key is involved.

GitHub currently advertises **4 CPU cores, 16 GB memory and 14 GB SSD** for standard public-repo Linux runners, and lists usage of those runners as free and unlimited for public repositories. Large runners and private-repo usage have different billing rules. We deliberately use `ubuntu-24.04` (standard, no GPU). This is a repository-development experiment, not a hosted inference service, under GitHub Actions' product terms.

Model choices:
- Default `qwen3:4b-instruct`: approximately 2.5 GB quantized model.
- `qwen3:1.7b`: approximately 1.4 GB, faster/less capable alternative.
- `qwen2.5-coder:1.5b`: approximately 986 MB, code-specific smaller alternative.

The model tag and SHA-256 digest are recorded in each run's artifact; model weights are never uploaded as artifacts. All generations use a fixed context window of 8192 and an output cap of 320 tokens per review. The smoke test is separately capped at 24 tokens. Model downloads and CPU prefill can still make the workflow take minutes.

## How to run

1. Open **Actions** in `Kimeiga/evidence-gated-goldfish`.
2. Select **Local CPU model experiment**.
3. Select **Run workflow**, choose the model and **both** (flawed + control).
4. Open the completed run's **Summary** to see token/time figures.
5. Download the `local-cpu-architecture-review` artifact for full, ungraded reviewer outputs.

The first check also runs automatically **once on the commit that introduces the workflow**. Future ordinary pushes do not trigger it. CI unit tests continue to run independently without downloading any weights.

## What the first run proves

The smoke test verifies that the CPU model actually returned output from Ollama. Four read-only review outputs compare *direct* and *contract-guided* prompting on both deliberately flawed and control design documents.

It does **not** execute EGM, BMAD, Spec Kit, OpenSpec, or Superpowers as native skills. It does **not** benchmark code generation or repair, or score planted defects, because the answer key remains private. The tests here establish feasibility and resource requirements, not that this small CPU model is useful.

## Operational safeguards

- No scheduled triggers, PR-triggered inference, or GPU/larger runners.
- Workflow runs have a 25-minute timeout and concurrency set to 1 per branch.
- Only three explicitly allowlisted quantized models are accepted by the script.
- Ollama cloud features are disabled; all prompts stay on loopback.
- The reviewer reads only public fixture files; hidden keys are not checked in.
- Artifacts expire after 3 days and contain no model weights.
- Public CI artifacts can be viewed by repository readers. Do not put private project code or credentials into these fixtures.

References:
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features
- https://docs.ollama.com/linux
- https://docs.ollama.com/api/generate
- https://github.com/ollama/ollama/blob/main/docs/faq.mdx
- https://ollama.com/library/qwen3

## Scoped contract-check follow-up

The first live 4B model run completed four review outputs (6,924 input tokens, 644 output tokens, 279.88 seconds of inference). Direct reviewing identified some genuine planted defects but also produced unsupported concerns on the clean control; the all-requirements contract-guided prompt answered `NONE` for both designs, including the flawed one. No overall quality score is claimed.

The workflow therefore offers a **`scoped-contracts`** variant by default. It checks only two publicly known behaviors, R1 (durable acknowledgment) and R2 (stable delivery ID), on both flawed and control documents. Each model call sees a single requirement and the corresponding design section. It records the model's verdict against four explicit, manually known reference outcomes. This is a bounded calibration of prompt granularity, *not* the hidden 14-defect comparison. The optional `architecture-review` and `both` variants retain the initial reviews.
