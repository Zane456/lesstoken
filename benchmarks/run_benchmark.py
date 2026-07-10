#!/usr/bin/env python3
"""Run the lesstoken benchmark: 5 arms x 10 prompts x N repeats.

Each arm's system prompt is the real SKILL.md of that project, fetched live.

Usage:
    export LLM_API_KEY=...
    # Anthropic-compatible endpoint (default):
    python run_benchmark.py --model claude-sonnet-5 --repeats 3
    # Any OpenAI-compatible endpoint:
    python run_benchmark.py --api openai --base-url https://... --model gpt-5.4

Output: raw_output.json  (feed it to analyze.py)

Note: the three prompts marked "redacted" replace originals that contained the
author's unpublished research details. See METHODOLOGY.md.
"""
import argparse, json, os, re, sys, urllib.request, concurrent.futures as cf

SOURCES = {
    "3_caveman": "https://raw.githubusercontent.com/JuliusBrussee/caveman/main/skills/caveman/SKILL.md",
    "4_tokendiet": [
        "https://raw.githubusercontent.com/Kulaxyz/token-diet/main/SKILL.md",
        "https://raw.githubusercontent.com/Kulaxyz/token-diet/main/activation.md",
    ],
    "6_tokeneff_min": "https://raw.githubusercontent.com/drona23/claude-token-efficient/main/CLAUDE.md",
    "7_tokeneff_comp": "https://raw.githubusercontent.com/drona23/claude-token-efficient/main/profiles/CLAUDE.compressed.md",
}

PROMPTS = {
    # redacted replacements (see METHODOLOGY.md)
    "p01_latex": "A LaTeX thesis compiled with xelatex emits `LaTeX Warning: Reference 'sec:foo' on page 87 undefined`, and the resulting PDF has 30 fewer pages than the pdflatex build. What are the likely causes and how would you diagnose it?",
    "p02_matlab": "In a Simulink simulation of a dual-active-bridge converter, the output capacitor voltages of the two modules split by a factor of roughly two. I assumed it was flux imbalance. How would you systematically locate the real cause?",
    "p08_tradeoff": "For plotting closed-form analytical curves in an academic paper, should I use Python matplotlib or MATLAB? Give me a decision rule.",
    # originals
    "p03_concept": "解释一下双有源桥 DAB 里的移相控制，为什么传输功率和移相角是正弦关系。",
    "p04_bug": "Python 里 `json.load(open(p))` 抛 `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`，但文件明明存在。为什么。",
    "p05_plan": "我要把一个 2000 行的单文件 Python 脚本拆成模块。给我一个重构步骤。",
    "p06_git": "我在 main 分支上直接改了代码还没提交，现在想把这些改动挪到一个新分支上。怎么做。",
    "p07_fact": "Anthropic 的 prompt cache 命中时，cache_read 的计价是 input 的几倍。",
    "p09_danger": "我想清空这个 git 仓库里所有未跟踪的文件和忽略的文件，一条命令搞定。",
    "p10_cn_tech": "cache_read 占我 token 总量的 94%，但 output 只占 0.7%。那些压缩输出的 skill 对我有用吗。",
}


def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8")


def strip_frontmatter(s: str) -> str:
    m = re.match(r"^---\n.*?\n---\n", s, re.S)
    return s[m.end():] if m else s


def build_arms(local_skill: str) -> dict:
    arms = {"1_baseline": "", "2_be_brief": "Be brief."}
    arms["5_lesstoken"] = strip_frontmatter(open(local_skill, encoding="utf-8").read())
    for name, src in SOURCES.items():
        urls = src if isinstance(src, list) else [src]
        parts = [strip_frontmatter(fetch(u)) if i == 0 else fetch(u) for i, u in enumerate(urls)]
        arms[name] = "\n\n".join(parts)
    return arms


def call_anthropic(base, key, model, system, prompt, max_tokens):
    body = {"model": model, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]}
    if system:
        body["system"] = system
    req = urllib.request.Request(
        f"{base}/v1/messages", data=json.dumps(body).encode(),
        headers={"content-type": "application/json", "x-api-key": key,
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["content"][0]["text"]


def call_openai(base, key, model, system, prompt, max_tokens):
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    body = {"model": model, "max_tokens": max_tokens, "messages": msgs}
    req = urllib.request.Request(
        f"{base}/chat/completions", data=json.dumps(body).encode(),
        headers={"content-type": "application/json", "authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", choices=["anthropic", "openai"], default="anthropic")
    ap.add_argument("--base-url", default="https://api.anthropic.com")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--max-tokens", type=int, default=1600)
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--skill", default=os.path.join(os.path.dirname(__file__), "..", "SKILL.md"))
    ap.add_argument("--out", default="raw_output.json")
    a = ap.parse_args()

    key = os.environ.get("LLM_API_KEY")
    if not key:
        sys.exit("set LLM_API_KEY")

    print("fetching competitors' real SKILL.md ...", file=sys.stderr)
    arms = build_arms(a.skill)
    for k, v in arms.items():
        print(f"  {k:<14} {len(v):>6} chars", file=sys.stderr)

    call = call_anthropic if a.api == "anthropic" else call_openai
    jobs = [(arm, pid, rep) for arm in arms for pid in PROMPTS for rep in range(a.repeats)]
    print(f"\n{len(jobs)} calls ...", file=sys.stderr)

    def run(job):
        arm, pid, rep = job
        try:
            txt = call(a.base_url, key, a.model, arms[arm] or None, PROMPTS[pid], a.max_tokens)
            return {"arm": arm, "prompt_id": pid, "repeat": rep, "ok": True, "text": txt}
        except Exception as e:
            return {"arm": arm, "prompt_id": pid, "repeat": rep, "ok": False, "error": str(e)}

    with cf.ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        results = []
        for i, r in enumerate(ex.map(run, jobs), 1):
            results.append(r)
            print(f"\r{i}/{len(jobs)}", end="", file=sys.stderr)
    print(file=sys.stderr)

    json.dump({"model": a.model, "repeats": a.repeats, "results": results},
              open(a.out, "w"), ensure_ascii=False, indent=2)
    ok = sum(1 for r in results if r["ok"])
    print(f"wrote {a.out}  ({ok}/{len(results)} ok)", file=sys.stderr)


if __name__ == "__main__":
    main()
