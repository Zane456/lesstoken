# lesstoken

> Bilingual (中文 / English) output-compression skill for coding agents.
> Benchmarked against the popular alternatives. Honest about what it cannot do.

Most output-compression skills are English-first and treat other languages as an afterthought. `lesstoken` ships **two independent rule sets** — one for English, one for Chinese — each with its own examples, and switches on the language you actually wrote in.

It also refuses to lie to you about savings. Read [Honest Numbers](#honest-numbers) before you install.

---

## The one-paragraph version

On a real agent workload with extended thinking enabled, **visible text is only 4.7% of billed output tokens**. The rest is thinking tokens and tool-call arguments, which no output-compression skill can touch. Output is roughly 19% of weighted spend. Multiply it out and the **global ceiling for this entire category is under 1% of your total bill**.

Within that 1%, `lesstoken` produces the **shortest output of anything we tested** (−80.9% vs. an unconstrained baseline) at the **lowest fixed cost of any real skill** (805 tokens/turn, vs. caveman's 1,182). It also **retains the least information** (0.570, the worst score in the field).

All three statements are true at once. Install it for **readability and speed**. Not for your bill.

---

## Why bilingual matters

`caveman` and `token-diet` are written in English and rely on a single instruction like *"preserve the user's dominant language"* to cover everything else. That works, sort of. What it does not give you is a rule set tuned to the target language's actual filler.

Chinese filler is not English filler. Dropping articles (`a`/`an`/`the`) is meaningless in Chinese. What you want to drop instead is 语气词 (的/了/呢/吧/啊), 口头禅 (其实/就是/基本上/实际上), 客套 (好的/当然/没问题), and 模糊词 (可能/大概/也许). `lesstoken` says so explicitly, in Chinese, with Chinese examples.

**English**

> **Q:** Why does my React component keep re-rendering?
> **A:** Inline obj prop -> new ref -> re-render. `useMemo`.

**中文**

> **问：** 为什么 React 组件一直在重新渲染？
> **答：** 内联对象 prop -> 新引用 -> 重渲染。用 `useMemo`。

The skill detects the language you wrote in and applies the matching rules. No flag, no mode switch.

---

## Install

Claude Code:

```bash
mkdir -p ~/.claude/skills/lesstoken
curl -sL https://raw.githubusercontent.com/Zane456/lesstoken/main/SKILL.md \
  -o ~/.claude/skills/lesstoken/SKILL.md
```

Trigger it by saying `lesstoken`, `be brief`, `省token`, `极简模式`, or `少废话`. Turn it off with `stop lesstoken` / `正常模式`.

It is a plain `SKILL.md` with YAML frontmatter, so any agent that reads that format should work. **Only Claude Code has been tested.**

---

## What it does

Drops filler, pleasantries, and hedging. Keeps fragments. Prefers short synonyms. One word when one word is enough.

Never touches technical terms, code blocks, or error strings — those are reproduced verbatim.

Response shape: `[thing] [action] [reason]. [next step].`

> ❌ "Sure! I'd be happy to help you with that. The issue you're experiencing is likely caused by..."
> ✅ "Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:"

### Auto-Clarity Exception

Compression switches **off** automatically for security warnings, irreversible operations, and multi-step sequences where fragment order could be misread. Then it resumes.

This is not decoration. In our blind evaluation, `lesstoken` scored **100% on safety**, meaning every dangerous or irreversible operation got an explicit warning. **`caveman` scored 90%** — it dropped the warning once.

---

## Benchmarks

### Method

Five arms. Each arm's system prompt is the **real, unmodified `SKILL.md`** of that project, fetched from its own repository. Same 10 prompts, same model, **3 repeats** (150 calls). Output measured with `tiktoken` `cl100k_base`.

Then a separate **blind judge** pass: 50 evaluations, arms anonymized, each compressed answer scored against the unconstrained baseline answer.

Net value accounts for the fact that a skill is not free — its system prompt is re-read as `cache_read` on **every single turn**:

```
net_weighted_per_turn = (baseline_output − arm_output) × 5 − fixed_cost × 0.1
```

(Anthropic pricing weights: output 5×, cache_read 0.1×, relative to input 1×.)

### Fixed cost — what the skill charges you every turn

| Arm | System prompt tokens |
|---|---|
| `"Be brief."` | **3** |
| **lesstoken** | **805** |
| caveman | 1,182 |
| token-diet | 2,115 |

caveman's own docs claim it "costs ~1–1.5k input tokens every turn." We measured **1,182**. The claim is accurate.

### Results (3 repeats, mean)

| Arm | Fixed | Mean output | σ across repeats | vs. baseline | **Net weighted/turn** |
|---|---|---|---|---|---|
| baseline (no instruction) | 0 | 1,321 | 0.2% | — | — |
| **lesstoken** | 805 | **252** | **2.6%** | **−80.9%** | **5,268** |
| caveman | 1,182 | 341 | 11.8% | −74.2% | 4,785 |
| `"Be brief."` | 3 | 434 | 2.1% | −67.1% | 4,436 |
| token-diet | 2,115 | 476 | 9.7% | −64.0% | 4,017 |

`lesstoken` is the shortest and the most consistent (σ 2.6%).

### Blind judge — the part that hurts

| Arm | Info retained | Actionable | Factual errors/answer | Safety | **Quality-adjusted net** |
|---|---|---|---|---|---|
| caveman | 0.690 | 0.665 | 0.20 | **90%** | **3,302** |
| **lesstoken** | **0.570** | 0.655 | 0.50 | 100% | 3,003 |
| `"Be brief."` | 0.665 | 0.700 | 0.30 | 100% | 2,950 |
| token-diet | 0.660 | 0.735 | **0.70** | 100% | 2,651 |

Quality-adjusted net = net × info-retained.

**`lesstoken` wins on raw tokens and loses on information retention.** Once you weight for how much of the answer survives compression, caveman comes out ahead. We are not going to hide that by omitting the column.

The judge flagged concrete failures in `lesstoken`'s answers: it dropped a root-cause chain in a LaTeX debugging question, forced a spurious numerical coincidence in a simulation question, and missed several causes (BOM, encoding) in a JSON parsing question.

Note that the σ between repeats runs 8–12% for caveman and token-diet. **The ~300-point quality-adjusted gap between caveman and lesstoken is not statistically significant** at this sample size. Do not read it as a ranking.

---

## Honest Numbers

Named after, and inspired by, [caveman's `HONEST-NUMBERS.md`](https://github.com/JuliusBrussee/caveman/blob/main/docs/HONEST-NUMBERS.md). If a skill's own docs will not tell you when it loses, do not install it.

### 1. The ceiling for this whole category is under 1%

Measured on one real user's 1,994 local agent sessions (26.9 billion tokens):

| Category | Share of all tokens |
|---|---|
| `cache_read` | 94.67% |
| `cache_write` | 4.07% |
| **`output`** | **0.71%** |
| `input` (uncached) | 0.55% |

Isolating assistant messages that contain **only text** — no tool calls, no thinking blocks (n = 9,070): the API billed 9,180,549 output tokens for 1,742,539 tokens of visible text. **A ratio of 5.27.** The other 4.27× is thinking tokens that never appear in the transcript.

So visible text — the only thing this skill can compress — is **4.7% of billed output**. Weighted by price, output is ~19% of total spend. Best case:

```
4.7% × 83% (best measured compression) × 19% ≈ 0.74%
```

**Under one percent.** If someone tells you an output-compression skill cut their bill by 50%, ask what fraction of their output was thinking tokens.

### 2. It compresses hardest, so it drops the most

`key_info_kept = 0.570`, the lowest of every arm tested. This is the direct cost of being the most aggressive. If you are debugging something subtle, turn it off.

### 3. Two of its rules save nothing

`SKILL.md` currently instructs the model to abbreviate common terms (`DB`/`auth`/`config`/`req`/`res`/`fn`/`impl`) and to use arrows for causality. **Both save zero tokens.** BPE encodes common words as single tokens:

| Abbreviation | tokens | Full word | tokens |
|---|---|---|---|
| `cfg` | 1 | `config` | 1 |
| `impl` | 1 | `implementation` | 1 |
| `fn` | 1 | `function` | 1 |
| `auth` | 1 | `authentication` | 1 |
| `DB` | 1 | `database` | 1 |

`Update cfg, restart fn, check req/res in DB.` = **12 tokens**
`Update config, restart function, check request/response in database.` = **12 tokens**

Identical under both `cl100k_base` and `o200k_base`. Same for `→` (1 token) versus ` therefore` (1 token).

caveman's `SKILL.md` says exactly this, and **caveman is right**:

> "never invent new abbreviations (cfg/impl/req/res/fn) — tokenizer split them same as full word: zero token saved, reader still decode. Full word cheaper AND clearer."

**The abbreviation rule is scheduled for removal.** Arrows will stay as a readability preference, with no claim of token savings.

### 4. When not to use it

- **Your replies are already short.** caveman's docs put it bluntly: *"the skill costs ~1–1.5k input tokens every turn. If it saves less output than that, you are paying to use it."* At 805 tokens `lesstoken` has more headroom than caveman, but the arithmetic is the same.
- **You are billed per request, not per token.**
- **The task is subtle debugging.** Info retention is 0.570.
- **You want maximum information density.** Use `"Be brief."` — three tokens, 0.665 retention, and per an [independent Hacker News benchmark](https://news.ycombinator.com/item?id=47954745) it matches caveman on both tokens and quality.

---

## How it compares

| | lesstoken | caveman | token-diet | `"Be brief."` |
|---|---|---|---|---|
| Fixed cost/turn | 805 | 1,182 | 2,115 | 3 |
| Output reduction | **−80.9%** | −74.2% | −64.0% | −67.1% |
| Info retained | 0.570 | **0.690** | 0.660 | 0.665 |
| Factual errors | 0.50 | **0.20** | 0.70 | 0.30 |
| Safety pass | **100%** | 90% | 100% | 100% |
| Consistency (σ) | **2.6%** | 11.8% | 9.7% | 2.1% |
| Independent CN rule set | **yes** | no | no | no |
| Auto-exit on dangerous ops | **yes** | partial | no | no |

Pick `lesstoken` if you write in Chinese and English and you want the shortest possible replies with an explicit safety carve-out. Pick `caveman` if information retention matters more than length. Pick `"Be brief."` if you want 90% of the benefit for 3 tokens.

**Not comparable, different layer:** [`rtk`](https://github.com/rtk-ai/rtk) compresses shell output, [`context-mode`](https://github.com/mksglu/context-mode) compresses MCP results, [`headroom`](https://github.com/headroomlabs-ai/headroom) proxies the API. Those attack `cache_read`, which is 94.67% of the tokens. **They have far more headroom than anything in this README.** If you are here to save money rather than to read less, start there.

---

## Reproduce

```bash
pip install tiktoken
python benchmarks/run_benchmark.py    # fetches competitors' real SKILL.md, runs all arms
python benchmarks/analyze.py          # regenerates the tables above
```

Aggregate results: [`benchmarks/data/results.json`](benchmarks/data/results.json). Method and caveats: [`benchmarks/METHODOLOGY.md`](benchmarks/METHODOLOGY.md).

**Raw model outputs are not published.** Three of the ten original prompts contained the author's unpublished research details. `benchmarks/data/redacted_prompts.json` holds semantically equivalent replacements. The numbers reported above come from the original run; a rerun with the redacted prompts will not reproduce them exactly.

---

## Credits

- **[caveman](https://github.com/JuliusBrussee/caveman)** by Julius Brussee — for the `HONEST-NUMBERS.md` format this README imitates, and for being right that abbreviations save nothing.
- **[token-diet](https://github.com/Kulaxyz/token-diet)** by Kulaxyz — for publishing a per-scenario bill breakdown instead of a single headline number.
- **[max-t-dev's HN benchmark](https://news.ycombinator.com/item?id=47954745)** — for the `"Be brief."` control arm, which is embarrassingly hard to beat.

---

## License

MIT © [Zane456](https://github.com/Zane456)
