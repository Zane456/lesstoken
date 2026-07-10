# Methodology

## Design

Six compression arms plus an unconstrained baseline. Each arm's system prompt is the **real, unmodified file** of that project, fetched from its own repository at benchmark time. No paraphrasing, no reconstruction from memory.

| Arm | System prompt | Fixed cost (tokens) |
|---|---|---|
| `1_baseline` | *(empty)* | 0 |
| `2_be_brief` | `Be brief.` | 3 |
| `3_caveman` | `JuliusBrussee/caveman` → `skills/caveman/SKILL.md`, frontmatter stripped | 1,182 |
| `4_tokendiet` | `Kulaxyz/token-diet` → `SKILL.md` + `activation.md` | 2,115 |
| `5_lesstoken` | this repo's `SKILL.md` **at v0.1**, frontmatter stripped | 805 |
| `6_tokeneff_minimal` | `drona23/claude-token-efficient` → `CLAUDE.md` | 85 |
| `7_tokeneff_compressed` | `drona23/claude-token-efficient` → `profiles/CLAUDE.compressed.md` | 220 |

**Version note.** The benchmark ran against `lesstoken` **v0.1** (805 tokens). After the run, v0.2 removed the abbreviation rule — measured to save zero tokens — and replaced it with the opposite instruction. That change made the skill 868 tokens. **The numbers have not been re-run against v0.2.** The change affects wording, not compression aggressiveness, but it has not been re-measured and should not be assumed identical.

**Comparison targets, star counts as of 2026-07-10 03:04 UTC (GitHub API):**

| Project | Stars | Created |
|---|---|---|
| `JuliusBrussee/caveman` | 87,330 | 2026-04-04 |
| `drona23/claude-token-efficient` | 5,804 | 2026-03-30 |
| `Kulaxyz/token-diet` | 555 | 2026-07-03 |

Two independent GitHub sweeps (43 keyword sets, 396 deduplicated repositories) found no other output-compression skill above 1,500 stars. `caveman` is the category. The runner-up by adoption, `laconic`, has 17 stars and is a caveman derivative.

`token-diet` is a recent, low-adoption entrant. **It is included only for the quality of its own published per-scenario billing data, not for its adoption.** It should not be read as a representative competitor.

The `"Be brief."` arm is a control, not a project. It comes from [max-t-dev's HN experiment](https://news.ycombinator.com/item?id=47954745).

**Prompts.** Ten, spanning LaTeX build diagnosis, circuit-simulation debugging, concept explanation, a Python exception, a refactor plan, a git operation, a one-line factual question, a tooling trade-off, a **destructive shell command**, and a Chinese-language technical question.

Three repeats per (arm, prompt) cell. 210 generation calls attempted, 204 returned. The six failures were transient provider overloads (HTTP 529), distributed across arms; the affected cells fell back to two repeats.

An earlier attempt returned only 53 of 210 calls under provider overload, with between-repeat σ of 63–130%. **That run was discarded, not reported.**

## Measurement

Output length is counted with `tiktoken` `cl100k_base`. Fixed cost is the token count of the arm's system prompt under the same encoder.

**Mean output** is a balanced mean: per-prompt mean across that prompt's surviving repeats, then an unweighted mean over the ten prompts. This matters. The six lost calls were not evenly spread — `2_be_brief` lost two of three repeats on `p03_concept`, the longest prompt in the set. A naive mean over surviving calls reports `2_be_brief` at 373 tokens; the balanced mean reports 424.

**σ** is the mean within-prompt coefficient of variation of output length across repeats. For each prompt, `100 × pstdev(repeats) / mean(repeats)`; then averaged over prompts. It answers "ask this arm the same question three times, how much does the answer length move?"

An earlier version of this document carried a different σ column (`5_lesstoken` 6.0%, `2_be_brief` 24.1%) produced by a script that was not preserved. **Those values do not reproduce** from `ab2_out.json` under any aggregation that could be reconstructed — not σ of per-repeat means (4.7% for `2_be_brief`), not mean within-prompt CV (26.2%), not σ of balanced per-repeat means over the common prompt set (7.8%). They have been discarded and recomputed under the stated definition. The correction lowered `lesstoken`'s Deployability Score from 0.852 to 0.791 and its lead over second place from 48% to 30%.

Net value assumes the skill's system prompt is cached and re-read on every turn:

```
net_weighted_per_turn = (baseline_output − arm_output) × 5 − fixed_cost × 0.1
```

Weights follow Anthropic's published pricing ratios relative to base input: output `5×`, cache read `0.1×`, cache write `1.25×`. The system prompt is charged once as cache write and thereafter as cache read; over a session of any meaningful length the `0.1×` term dominates, so the formula uses it directly.

## Blind judge

A separate model pass scores each compressed answer against the unconstrained baseline answer for the same prompt. Arms are anonymized; the judge sees only the question, the reference answer, and one candidate.

Scored dimensions: `key_info_kept` (0–1), `actionable` (0–1), `factual_errors` (count), `safety_ok` (boolean; `true` by default for prompts that involve no dangerous operation).

52 evaluations, all parsed successfully.

### `key_info_kept` is length-biased and is not used as a quality proxy

Across the six arms:

```
r(mean output length, key_info_kept)  =  +0.720
r(factual errors,     key_info_kept)  =  -0.307
```

The judge rewards length **2.3× more strongly than it punishes being wrong**. This is mechanical, not a defect of the judge: it scores a candidate by how much of the reference answer it recovers, and a longer candidate recovers more. In a benchmark whose independent variable *is* output length, discounting by `key_info_kept` scores arms on the quantity under test.

`factual_errors` shows no such coupling and is used instead. Both correlations are recomputed by `score.py`.

An earlier version of the README used `net × key_info_kept` as its headline ranking. **That ranking has been retracted.** The number it produced is still printed by `score.py` under "key_info_kept as the sole quality proxy," so the retraction can be checked.

## Deployability Score

```
Deployability = 0.35 × net_tokens_saved      / max(net_tokens_saved)
              + 0.30 × (1 − factual_errors   / max(factual_errors))
              + 0.20 × (1 − sigma            / max(sigma))
              + 0.15 × bilingual             (1 if a native non-English rule set exists, else 0)
```

Weights were declared before scoring. Rationale:

- **0.35 net.** The purpose of the artifact.
- **0.30 accuracy.** Tokens saved on a wrong answer are a liability. The only length-independent quality signal available.
- **0.20 stability.** Mean within-prompt σ. An arm at σ = 40.1% has not produced a budgetable saving.
- **0.15 bilingual.** A binary. Only `lesstoken` ships a native Chinese rule set.

**Safety is deliberately not a term.** It rests on a single prompt (`n = 1`) and would be the weakest evidence in the score. It is reported separately.

Three sensitivity checks, all printed by `score.py`:

| Perturbation | Winner | Runner-up | Margin |
|---|---|---|---|
| All six arms, no gate (headline) | `lesstoken` 0.791 | `"Be brief."` 0.607 | +0.183 |
| Bilingual dimension deleted, others renormalised | `lesstoken` 0.754 | `"Be brief."` 0.715 | **+0.039, narrow** |
| Safety applied as a hard gate (2 arms eliminated) | `lesstoken` 0.791 | `token-diet` 0.536 | +0.255 |
| `key_info_kept` as sole quality proxy | `"Be brief."` 0.802 | `caveman` 0.780 | `lesstoken` third at 0.747 |

Row 2 is the weakest case for `lesstoken` among the defensible weightings: strip its bilingual advantage and it beats a three-token instruction by 0.039. Row 4 is the weighting under which it loses outright, and it is the one disqualified by the r-values above. Both are printed anyway.

---

## Limitations

These are real, and they bound what you should conclude.

1. **The generating model is GLM-5.2, not Claude.** Instruction-following differs across models. A skill that lands well on one may land differently on another. Absolute numbers do not transfer; the relative ordering is the claim.

2. **`cl100k_base` is not Claude's tokenizer.** Anthropic does not publish theirs. Cross-arm comparisons are internally consistent because every arm is measured with the same ruler, but the absolute token counts are approximations.

3. **The judge is also GLM-5.2.** It has its own biases — the length bias above is measured and corrected for, but its domain judgments in the circuit-simulation and LaTeX prompts were not independently verified by a human expert.

4. **10 prompts × 3 repeats.** Within-prompt σ runs 17.3–40.1%. **The 26-net-point gap between `lesstoken` and `token-efficient (compressed)` is inside the noise.** Treat those two as tied on raw economics. The Deployability Score separates them on accuracy and stability, not on savings. The larger gaps (e.g. `lesstoken` vs `token-efficient (minimal)` on output length) survive.

5. **The baseline is GLM's unconstrained default (1,330 tokens), which is far more verbose than Claude's default.** Every "reduction vs. baseline" figure is therefore an **overestimate** of what you would see against a modern assistant that is already fairly terse. Only the differences between compression arms are meaningful.

6. **Single-author workload.** The prompts reflect one person's work: LaTeX thesis writing, power-electronics simulation, and agent-skill maintenance. They are not representative of typical front-end or back-end development.

7. **`n = 1` on safety.** One prompt requested a destructive, irreversible command. Four arms warned, two did not. This is a signal, not a rate. Do not quote it as a percentage.

---

## Redaction

Three of the ten original prompts contained the author's unpublished research details (a thesis cross-reference label, an unpublished measured ratio, and a thesis reference).

`data/redacted_prompts.json` contains semantically equivalent English replacements for those three. **The numbers reported in the README come from the original, unredacted run.** A rerun using the redacted prompt set will produce similar but not identical figures.

Raw model outputs are not published, for the same reason.

## What is published

- `data/results.json` — full aggregate statistics per arm, including per-repeat means
- `data/arm_costs.json` — measured fixed cost of each arm's system prompt
- `data/redacted_prompts.json` — the three replacement prompts
- `score.py` — Deployability Score, the two r-values, all sensitivity checks. No API key needed
- `run_benchmark.py` — fetches competitors' real files and runs all arms
- `analyze.py` — regenerates the README tables from a run's output
