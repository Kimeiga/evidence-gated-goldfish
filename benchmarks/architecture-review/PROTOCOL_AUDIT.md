# Protocol audit as of November 1, 2026

These are verified facts from the current public workflow definitions, NOT measured architecture-review benchmark outcomes.

| System | Native mechanism most relevant to pre-implementation quality | Important comparison limitation |
|---|---|---|
| EGM | `egm-review`: five review phases including zoom-out, comprehension, critique, and implementation readiness; Goldfish agents receive no conversation history. | Explicitly stops when fresh subagents are unavailable. |
| BMad Method | `bmad-review`: independent adversarial and edge-case lenses apply to behavioral design docs; other lenses review document structure/prose. | Adversarial lens demands at least 10 findings, potentially inflating low-value findings; fallback can run in same context sequentially. |
| GitHub Spec Kit | `speckit.analyze`: read-only analysis over `spec.md`, `plan.md`, `tasks.md` for gaps and contradictions, including constitution alignment. | Requires all planning artifacts and is not fundamentally a zero-context independent design critic. |
| OpenSpec | `openspec-explore` can critique alternatives and project design; `openspec-verify-change` compares implementation to spec artifacts. | No standard pre-code independent multi-agent design-review step equivalent to EGM. |
| Superpowers | `brainstorming` invokes a builder check on a written design using a fresh general-purpose subagent, asking which answers an implementer still needs. | Builder check asks unresolved high-impact questions and may not challenge a concrete but wrong decision. |

Source files:
- https://github.com/google/elephant-goldfish-model/blob/main/skills/egm-review/SKILL.md
- https://github.com/bmad-code-org/BMAD-METHOD/blob/main/skills/bmad-review/SKILL.md
- https://github.com/bmad-code-org/BMAD-METHOD/blob/main/skills/bmad-review/customize.toml
- https://github.com/bmad-code-org/BMAD-METHOD/blob/main/skills/bmad-review/references/lens-adversarial.md
- https://github.com/github/spec-kit/blob/main/templates/commands/analyze.md
- https://github.com/Fission-AI/OpenSpec/blob/main/skills/openspec-explore/SKILL.md
- https://github.com/Fission-AI/OpenSpec/blob/main/skills/openspec-verify-change/SKILL.md
- https://github.com/obra/superpowers/blob/main/skills/brainstorming/builder-check-prompt.md
