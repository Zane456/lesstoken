#!/usr/bin/env python3
"""Deployability Score, and the length-bias check on the blind judge's key_info_kept.

Reads data/results.json. Every input is a measurement; this file only re-weights them.
No API key needed.

    python benchmarks/score.py
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "data", "results.json")))
ARMS = {k: v for k, v in R["arms"].items() if k != "1_baseline"}


# ---------------------------------------------------------------- length bias
def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(a * a for a in dx) * sum(b * b for b in dy))
    return sum(a * b for a, b in zip(dx, dy)) / den


out = [a["mean_output"] for a in ARMS.values()]
keep = [a["key_info_kept"] for a in ARMS.values()]
err = [a["factual_errors"] for a in ARMS.values()]

r_len = pearson(out, keep)
r_err = pearson(err, keep)

print(f"Blind-judge length bias, across {len(ARMS)} arms:")
print(f"  r(mean_output,    key_info_kept) = {r_len:+.3f}")
print(f"  r(factual_errors, key_info_kept) = {r_err:+.3f}")
print(f"  -> the judge rewards length {abs(r_len / r_err):.1f}x more strongly "
      f"than it punishes being wrong.")
print("  key_info_kept is therefore NOT used as the quality term below.")

# ---------------------------------------------------------------- score
# Weights, declared before scoring.
#   net       0.35  you install a compression skill to spend fewer tokens
#   accuracy  0.30  tokens saved on a wrong answer are a liability, not a saving
#   stability 0.20  a saving you cannot predict is a saving you cannot budget
#   bilingual 0.15  an English-only rule set is inert on half this author's traffic
W = dict(net=0.35, accuracy=0.30, stability=0.20, bilingual=0.15)

MAX_NET = max(a["net_weighted_per_turn"] for a in ARMS.values())
MAX_ERR = max(a["factual_errors"] for a in ARMS.values())
MAX_SIG = max(a["sigma_pct"] for a in ARMS.values())


def components(a):
    return dict(
        net=a["net_weighted_per_turn"] / MAX_NET,
        accuracy=1 - a["factual_errors"] / MAX_ERR,
        stability=1 - a["sigma_pct"] / MAX_SIG,
        bilingual=1.0 if a["bilingual_rule_set"] else 0.0,
    )


def rank(w, arms=ARMS, tag=""):
    rows = sorted(
        ((sum(w[k] * components(a)[k] for k in w), a) for a in arms.values()),
        key=lambda t: -t[0])
    print(f"\n--- {tag}")
    for i, (s, a) in enumerate(rows, 1):
        c = components(a)
        parts = "  ".join(f"{k[:4]}={w[k] * c[k]:.3f}" for k in w)
        print(f"{i}. {a['name']:<30} {s:.3f}   {parts}")
    return rows


main = rank(W, tag="Deployability Score (all six arms, no safety gate)")

w_nobi = {k: v / (1 - W["bilingual"]) for k, v in W.items() if k != "bilingual"}
rank(w_nobi, tag="Sensitivity: bilingual dimension deleted, others renormalised")

gated = {k: a for k, a in ARMS.items() if a["warned_on_destructive_prompt"]}
rank(W, arms=gated, tag="Sensitivity: safety as a hard gate (2 arms eliminated)")

print("\n--- Sensitivity: key_info_kept as the sole quality proxy "
      "(the length-biased weighting; lesstoken loses)")
biased = sorted(ARMS.values(),
                key=lambda a: -(0.35 * a["net_weighted_per_turn"] / MAX_NET
                                + 0.65 * a["key_info_kept"]))
for i, a in enumerate(biased, 1):
    s = 0.35 * a["net_weighted_per_turn"] / MAX_NET + 0.65 * a["key_info_kept"]
    print(f"{i}. {a['name']:<30} {s:.3f}")

print(f"\nMain ranking, first over second: {main[0][0] - main[1][0]:+.3f}"
      f"  ({main[0][1]['name']} over {main[1][1]['name']})")
