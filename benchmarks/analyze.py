#!/usr/bin/env python3
"""Regenerate the README tables from a benchmark run.

    pip install tiktoken
    python analyze.py raw_output.json

Also measures each arm's fixed cost (its system prompt token count), since that
is what the skill charges you on every turn.
"""
import json, statistics as st, sys, os
from collections import defaultdict

import tiktoken
from run_benchmark import build_arms  # reuse the same fetch + strip logic

ENC = tiktoken.get_encoding("cl100k_base")
tok = lambda s: len(ENC.encode(s or ""))

ORDER = ["1_baseline", "2_be_brief", "5_lesstoken", "3_caveman", "4_tokendiet"]
LABEL = {"1_baseline": "baseline", "2_be_brief": '"Be brief."',
         "3_caveman": "caveman", "4_tokendiet": "token-diet", "5_lesstoken": "lesstoken"}


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
        per_prompt = [st.mean(cells[(a, p)]) for p in prompts if (a, p) in cells]
        reps = []
        for i in range(d["repeats"]):
            v = [cells[(a, p)][i] for p in prompts if (a, p) in cells and len(cells[(a, p)]) > i]
            if v:
                reps.append(st.mean(v))
        stats[a] = {
            "fixed_cost": costs[a],
            "mean_output": st.mean(per_prompt),
            "rep_means": reps,
            "rep_sigma_pct": (st.stdev(reps) / st.mean(reps) * 100) if len(reps) > 1 else 0.0,
        }

    base = stats["1_baseline"]["mean_output"]
    for a in arms:
        s = stats[a]
        s["reduction_pct"] = (base - s["mean_output"]) / base * 100
        # output priced 5x; the system prompt is re-read as cache_read (0.1x) every turn
        s["net_weighted_per_turn"] = (base - s["mean_output"]) * 5 - s["fixed_cost"] * 0.1

    print(f"model={d['model']}  repeats={d['repeats']}  prompts={len(prompts)}\n")
    print(f"{'arm':<13}{'fixed':>7}{'output':>8}{'sigma':>8}{'vs base':>9}{'net/turn':>10}")
    print("-" * 55)
    for a in arms:
        s = stats[a]
        red = "—" if a == "1_baseline" else f"{s['reduction_pct']:.1f}%"
        net = "—" if a == "1_baseline" else f"{s['net_weighted_per_turn']:,.0f}"
        print(f"{LABEL[a]:<13}{s['fixed_cost']:>7,}{s['mean_output']:>8.0f}"
              f"{s['rep_sigma_pct']:>7.1f}%{red:>9}{net:>10}")

    print("\nnet_weighted_per_turn = (baseline_output - arm_output) * 5 - fixed_cost * 0.1")
    print("Absolute reductions are inflated by a verbose baseline. Compare arms, not headlines.")
    json.dump(stats, open("results.json", "w"), indent=2, default=float)
    print("\nwrote results.json")


if __name__ == "__main__":
    main()
