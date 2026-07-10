# Methodology

## Design

Five arms. Each arm's system prompt is the **real, unmodified `SKILL.md` body** of that project, fetched from its own repository at benchmark time. No paraphrasing, no reconstruction from memory.

| Arm | System prompt | Fixed cost (tokens) |
|---|---|---|
| `1_baseline` | *(empty)* | 0 |
| `2_be_brief` | `Be brief.` | 3 |
| `3_caveman` | `JuliusBrussee/caveman` → `skills/caveman/SKILL.md`, frontmatter stripped | 1,182 |
| `4_tokendiet` | `Kulaxyz/token-diet` → `SKILL.md` + `activation.md` | 2,115 |
| `5_lesstoken` | this repo's `SKILL.md` **at v0.1**, frontmatter stripped | 805 |

**Version note.** The benchmark ran against `lesstoken` **v0.1** (805 tokens). After the run, v0.2 removed the abbreviation rule — measured to save zero tokens — and replaced it with the opposite instruction. That change made the skill 868 tokens. **The numbers below have not been re-run against v0.2.** The change affects wording, not compression aggressiveness, but it has not been re-measured and should not be assumed identical.

**Comparison targets, star counts as of 2026-07-10 03:04 UTC (GitHub API):**
`caveman` 87,329 ★ (created 2026-04-04) · `token-diet` 555 ★ (created 2026-07-03).
`caveman` is the only widely adopted project in this category; the runner-up, `laconic`, has 17 stars and is a caveman derivative. `token-diet` is a recent entrant and is included for the quality of its own published data, not for its adoption.

Ten prompts spanning LaTeX build diagnosis, circuit-simulation debugging, concept explanation, a Python exception, a refactor plan, a git operation, a one-line factual question, a tooling trade-off, a **destructive shell command**, and a Chinese-language technical question.

Three repeats per (arm, prompt) cell. 150 generation calls total.

## Measurement

Output length is counted with `tiktoken` `cl100k_base`.

Fixed cost is the token count of the arm's system prompt, also under `cl100k_base`.

Net value assumes the skill's system prompt is cached and re-read on every turn:

```
net_weighted_per_turn = (baseline_output − arm_output) × 5 − fixed_cost × 0.1
```

Weights follow Anthropic's published pricing ratios relative to base input: output `5×`, cache read `0.1×`, cache write `1.25×`. The system prompt is charged once as cache write and thereafter as cache read; over a session of any meaningful length the `0.1×` term dominates, so the formula uses it directly.

## Blind judge

A separate model pass scores each compressed answer against the unconstrained baseline answer for the same prompt. Arms are anonymized; the judge sees only the question, the reference answer, and one candidate.

Scored dimensions: `key_info_kept` (0–1), `actionable` (0–1), `factual_errors` (count), `safety_ok` (boolean; `true` by default for prompts that involve no dangerous operation).

50 evaluations, all parsed successfully.

Quality-adjusted net = `net_weighted_per_turn × key_info_kept`.

---

## Limitations

These are real, and they bound what you should conclude.

1. **The generating model is GLM-5.2, not Claude.** Instruction-following differs across models. A skill that lands well on one may land differently on another. Absolute numbers do not transfer; the relative ordering is the claim.

2. **`cl100k_base` is not Claude's tokenizer.** Anthropic does not publish theirs. Cross-arm comparisons are internally consistent because every arm is measured with the same ruler, but the absolute token counts are approximations.

3. **The judge is also GLM-5.2.** It has its own biases, and its domain judgments in the circuit-simulation and LaTeX prompts were not independently verified by a human expert.

4. **10 prompts × 3 repeats.** Between-repeat σ runs 8–12% for `caveman` and `token-diet`, and 2–3% for `lesstoken` and `"Be brief."`. **The ~300-point quality-adjusted gap between `caveman` and `lesstoken` is inside the noise.** Do not treat it as a ranking. The larger gaps (e.g. `lesstoken` vs `token-diet` on output length) survive.

5. **The baseline is GLM's unconstrained default (1,321 tokens), which is far more verbose than Claude's default.** Every "reduction vs. baseline" figure is therefore an **overestimate** of what you would see against a modern assistant that is already fairly terse. Only the differences between compression arms are meaningful.

6. **Single-author workload.** The prompts reflect one person's work: LaTeX thesis writing, power-electronics simulation, and agent-skill maintenance. They are not representative of typical front-end or back-end development.

---

## Redaction

Three of the ten original prompts contained the author's unpublished research details (a thesis cross-reference label, an unpublished measured ratio, and a thesis reference).

`data/redacted_prompts.json` contains semantically equivalent English replacements for those three. **The numbers reported in the README come from the original, unredacted run.** A rerun using the redacted prompt set will produce similar but not identical figures.

Raw model outputs are not published, for the same reason.

## What is published

- `data/results.json` — full aggregate statistics per arm, including per-repeat means
- `data/arm_costs.json` — measured fixed cost of each arm's system prompt
- `data/redacted_prompts.json` — the three replacement prompts
- `run_benchmark.py` — fetches competitors' real `SKILL.md` files and runs all arms
- `analyze.py` — regenerates the README tables from a run's output
