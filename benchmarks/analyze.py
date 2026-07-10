#!/usr/bin/env python3
"""Regenerate the README tables from a benchmark run.

    pip install tiktoken
    python analyze.py raw_output.json

Also measures each arm's fixed cost (its system prompt token count), since that
is what the skill charges you on every turn.

Definitions match data/results.json, and score.py consumes the output:

  mean_output  per-prompt mean across that prompt's surviving repeats, then an
               unweighted mean over prompts. Balanced, because lost calls are
               not evenly distributed across prompts.
  sigma_pct    mean within-prompt coefficient of variation across repeats.
"""
import json, statistics as st, sys, os
from collections import defaultdict

import tiktoken
from run_benchmark import build_arms  # reuse the same fetch + strip logic

ENC = tiktoken.get_encoding("cl100k_base")
tok = lambda s: len(ENC.encode(s or ""))

ORDER = ["1_baseline", "2_be_brief", "5_lesstoken", "7_tokeneff_comp",
         "3_caveman", "4_tokendiet", "6_tokeneff_min"]
LABEL = {"1_baseline": "baseline", "2_be_brief": '"Be brief."',
         "3_caveman": "caveman", "4_tokendiet": "token-diet",
         "5_lesstoken": "lesstoken", "6_tokeneff_min": "token-efficient (minimal)",
         "7_tokeneff_comp": "token-efficient (compressed)"}
BILINGUAL = {"5_lesstoken"}
DESTRUCTIVE_PROMPT = "p09_danger"


def main():
    raw = sys.argv[1] if len(sys.argv) > 1 else "raw_output.json"
    d = json.load(open(raw))

    skill = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
    costs = {k: tok(v) for k, v in build_arms(skill).items()}

    cells = defaultdict(list)
    for r in d["results"]:
        if r["ok"]:
            cells[(r["arm"], r["prompt_id"])].append(tok(r["text"]))

    prompts = sorted({k[1] for k in cells})
    arms = [a for a in ORDER if any(k[0] == a for k in cells)]

    stats = {}
    for a in arms:
        per_prompt = {p: cells[(a, p)] for p in prompts if (a, p) in cells}
        means = [st.mean(v) for v in per_prompt.values()]
        cvs = [100 * st.pstdev(v) / st.mean(v)
               for v in per_prompt.values() if len(v) > 1 and st.mean(v) > 0]
        stats[a] = {
            "name": LABEL[a],
            "fixed_cost": costs[a],
            "calls_returned": sum(len(v) for v in per_prompt.values()),
            "mean_output": round(st.mean(means), 1),
            "sigma_pct": round(st.mean(cvs), 1) if cvs else 0.0,
            "per_prompt_mean_output": {p: round(st.mean(v), 1)
                                       for p, v in sorted(per_prompt.items())},
            "bilingual_rule_set": a in BILINGUAL,
        }

    base = stats["1_baseline"]["mean_output"]
    for a in arms:
        s = stats[a]
        s["reduction_vs_baseline_pct"] = round((base - s["mean_output"]) / base * 100, 1)
        # output priced 5x; the system prompt is re-read as cache_read (0.1x) every turn
        s["net_weighted_per_turn"] = round((base - s["mean_output"]) * 5 - s["fixed_cost"] * 0.1)

    print(f"model={d['model']}  repeats={d['repeats']}  prompts={len(prompts)}\n")
    print(f"{'arm':<30}{'fixed':>7}{'output':>8}{'sigma':>8}{'vs base':>9}{'net/turn':>10}")
    print("-" * 72)
    for a in arms:
        s = stats[a]
        red = "—" if a == "1_baseline" else f"{s['reduction_vs_baseline_pct']:.1f}%"
        net = "—" if a == "1_baseline" else f"{s['net_weighted_per_turn']:,}"
        print(f"{s['name']:<30}{s['fixed_cost']:>7,}{s['mean_output']:>8.0f}"
              f"{s['sigma_pct']:>7.1f}%{red:>9}{net:>10}")

    print("\nnet_weighted_per_turn = (baseline_output - arm_output) * 5 - fixed_cost * 0.1")
    print("Absolute reductions are inflated by a verbose baseline. Compare arms, not headlines.")
    print(f"\nJudge scores (key_info_kept, factual_errors, warned on {DESTRUCTIVE_PROMPT}) come "
          f"from the blind judge pass and are merged into data/results.json by hand.")

    out = {"n_prompts": len(prompts), "n_repeats": d["repeats"],
           "tokenizer": "cl100k_base", "arms": {a: stats[a] for a in arms}}
    json.dump(out, open("results.json", "w"), indent=2, default=float, ensure_ascii=False)
    print("wrote results.json")


if __name__ == "__main__":
    main()
