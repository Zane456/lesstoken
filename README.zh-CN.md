# lesstoken

**中英双语，一个 skill。实测输出最短，也如实告诉你天花板在哪。**

[English](README.md) · [简体中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skill](https://img.shields.io/badge/Claude%20Code-skill-orange)](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
[![Benchmarked](https://img.shields.io/badge/benchmark-3%20次重复%20%2B%2050%20次盲评-green)](benchmarks/METHODOLOGY.md)

---

## 特点

- **一眼能读完的回答。** 回复长度压到平常的五分之一左右，技术术语、代码块、报错原文一个字节不动。
- **中文和英文都是一等公民。** 两套独立规则，两套示例。不是一套英文规则外加一句「保持用户的语言」。
- **该啰嗦的时候它会啰嗦。** 删表、强推分支、跑不可逆的命令，极简模式自动关掉，把警告说清楚再回来。盲评安全通过率 100%，而最流行的那个同类是 90%。
- **它会告诉你什么时候它不划算。** 这个品类的天花板不到你账单的 1%。这个数字就写在下面，配图，算式摊开给你看。

---

## 介绍

`lesstoken` 就是一个 `SKILL.md` 文件。它让 coding agent 用压缩过的语言回答，不要填充词，不要客套，不要模棱两可，能用碎片句就用碎片句。技术术语、代码、命令、报错信息原样穿过。

它和同类不一样的地方在于**自带一套独立的中文规则**。英文的废话和中文的废话不是一回事。中文里砍冠词毫无意义，该砍的是语气词、口头禅、客套和模糊词。`lesstoken` 用中文把这件事写明白了，配中文示例。别的项目靠一句「保持用户的语言」，剩下的听天由命。

它还带一个 **Auto-Clarity Exception**。碰到安全警告、不可逆操作、以及顺序读错就会出事的多步流程，压缩自动挂起。这是唯一一个「少说几个字」等于错误答案的场合。

它也不会自吹。装之前先读 [诚实数字](#诚实数字)。一句话版本，在开了 extended thinking 的现代 agent 上，**可见文字只占你 output 计费的 4.7%**。这个品类里任何 skill 都省不了你总开销的 0.74% 以上。装 `lesstoken` 是因为你想少读几个字，不是因为你想少付几块钱。

---

## 展示

**English**

> **Q:** Why does my React component keep re-rendering?
> **A:** Inline obj prop -> new ref -> re-render. `useMemo`.

**中文**

> **问：** 为什么 React 组件一直在重新渲染？
> **答：** 内联对象 prop -> 新引用 -> 重渲染。用 `useMemo`。

**该停下来的时候**

> **问：** 生产库上直接 `DROP TABLE users` 行不行？
> **答：**
> **警告：** 此操作将永久删除 `users` 表所有行，不可恢复。
> ```sql
> DROP TABLE users;
> ```
> 极简恢复。先确认备份存在。

警告用完整句子说。危险一过，立刻回到碎片句。

---

## 实测对比

五个 arm。每个 arm 的 system prompt 都是该项目**真实、未经改动的 `SKILL.md`**，跑的时候从它自己的仓库现取。同样 10 个 prompt，同一个模型，重复 3 次。之后 50 次盲评，拿每个压缩版回答去对照未压缩的基准答案打分。

### 到底在和谁比

| 项目 | 星数 | 创建于 | 说明 |
|---|---|---|---|
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | **87,329** ★ | 2026-04-04 | 这个品类唯一的巨头 |
| [Kulaxyz/token-diet](https://github.com/Kulaxyz/token-diet) | 555 ★ | 2026-07-03 | 新入场者，收录是因为它公布了分场景的账单数据 |
| `"Be brief."` | — | — | 一个对照组，不是项目。取自 [max-t-dev 的 HN 实验](https://news.ycombinator.com/item?id=47954745) |

*星数快照 **2026-07-10 03:04 UTC**，GitHub API。*

两件事要说清楚。**`caveman` 不只是流行，它就是这个品类本身。** 输出压缩类里排第二的 [`laconic`](https://github.com/GabrielBarberini/laconic) 只有 17 星，而且是 caveman 的改编。**`token-diet` 算不上知名**，555 星，做这次 benchmark 时它才建了一周。它能进这张表，靠的是对自家数字异常诚实，不是靠装机量。

### 权衡

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/tradeoff-dark.png">
  <img alt="输出长度与信息保留的权衡。lesstoken 最短，也丢得最多。" src="assets/tradeoff-light.png">
</picture>

`lesstoken` 输出全场最短，信息保留也全场最低。这两件事是同一份激进带来的。气泡面积是每个 skill 光靠待在 system prompt 里、每一轮都要向你收的钱。

### 输出长度与成本

| Arm | 每轮固定成本 | 平均输出 | 重复间 σ | 相对基准 |
|---|---|---|---|---|
| baseline（无指令） | 0 | 1,321 | 0.2% | — |
| **lesstoken** | 805 | **252** | **2.6%** | **−80.9%** |
| caveman | 1,182 | 341 | 11.8% | −74.2% |
| `"Be brief."` | **3** | 434 | 2.1% | −67.1% |
| token-diet | 2,115 | 476 | 9.7% | −64.0% |

caveman 自己的文档写着这个 skill「每轮花掉约 1–1.5k input token」。我们实测 **1,182**。这个说法准确。

### 质量，以及它如何改变排名

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/net-dark.png">
  <img alt="每轮净省的加权 token，按信息保留折算前后。" src="assets/net-light.png">
</picture>

| Arm | 信息保留 | 可行动 | 事实错误/答 | 安全通过 |
|---|---|---|---|---|
| caveman | **0.690** | 0.665 | **0.20** | **90%** |
| **lesstoken** | 0.570 | 0.655 | 0.50 | **100%** |
| `"Be brief."` | 0.665 | **0.700** | 0.30 | 100% |
| token-diet | 0.660 | 0.735 | 0.70 | 100% |

**`lesstoken` 赢在纯 token，一旦把质量算进价格就输了。** 我们不会靠删掉这一列来遮掩。

评审点了名。`lesstoken` 在一道 LaTeX 调试题里漏掉了根因链条，在一道仿真题里把一个数值巧合强行附会成规律，在一道 JSON 解析题里漏了好几个原因。

有一条对我们有利的提醒，也照说不误。caveman 和 token-diet 的重复间 σ 有 8–12%。**caveman 和 lesstoken 之间那 300 分的质量折扣差距落在噪声里。** 那不是排名。就当它俩打平。

---

## 诚实数字

名字和格式都学自 [caveman 的 `HONEST-NUMBERS.md`](https://github.com/JuliusBrussee/caveman/blob/main/docs/HONEST-NUMBERS.md)。一个自家文档不肯告诉你它什么时候不划算的 skill，不值得装。

### 整个品类的天花板不到 1%

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/ceiling-dark.png">
  <img alt="为什么每个输出压缩 skill 的天花板都不到 1%。" src="assets/ceiling-light.png">
</picture>

数据来自一位用户本机 1,994 个 agent session、269 亿 token。单独挑出那些**只含文字**的 assistant 消息，没有工具调用，没有 thinking 块（n = 9,070）。API 为 1,742,539 token 的可见文字计费了 9,180,549 个 output token。**比值 5.27。** 多出来的 4.27 倍是 thinking token，它们从不出现在对话记录里。

可见文字，也就是这个 skill 唯一能碰到的表面，占计费 output 的 **4.7%**。而 output 占加权开销约 19%。最好情况

```
4.7%  ×  83%（实测最佳压缩率）  ×  19%  =  0.74%
```

如果有人告诉你某个输出压缩 skill 把他账单砍了一半，问问他 output 里有多少是 thinking token。

### 它压得最狠，所以丢得最多

`key_info_kept = 0.570`，全场最低。这是最激进的直接代价。在调一个微妙的 bug，把它关掉。

### 它自己有一条规则零收益，已经删了

在 v0.1 之前，这个 skill 让模型缩写常用词。**那条规则一个 token 都没省下来。** BPE 把常用词整个编成单个 token。

| 缩写 | token | 全词 | token |
|---|---|---|---|
| `cfg` | 1 | `config` | 1 |
| `impl` | 1 | `implementation` | 1 |
| `fn` | 1 | `function` | 1 |
| `auth` | 1 | `authentication` | 1 |
| `DB` | 1 | `database` | 1 |

`Update cfg, restart fn, check req/res in DB.` = **12 token**
`Update config, restart function, check request/response in database.` = **12 token**

`cl100k_base` 和 `o200k_base` 下结果完全一致。caveman 的 `SKILL.md` 写的正是这一点，而且 **caveman 是对的**

> "never invent new abbreviations (cfg/impl/req/res/fn) — tokenizer split them same as full word: zero token saved, reader still decode. Full word cheaper AND clearer."

**v0.2 删掉了这条规则，换成了相反的指令。** 这让 skill 重了 63 token（805 → 868），也让它的输出在同样的价格下更好读。本 README 里的 benchmark 数字产自 **v0.1，805 token**，没有重跑。

因果箭头（`X -> Y`）同样**不省** token，`→` 和 ` therefore` 各是 1 个 token。箭头保留，作为可读性偏好，不附带任何省 token 的说法。

### 什么时候别用它

- **你的回复本来就很短。** caveman 的文档说得直白，「这个 skill 每轮花掉约 1–1.5k input token。如果它省下的 output 比这还少，你是在花钱用它。」`lesstoken` 868 token，余量大一些，但算式一模一样。
- **你按请求计费，不按 token 计费。**
- **你在调一个微妙的 bug。** 0.570。
- **你想要最高的收益复杂度比。** 用 `"Be brief."`。三个 token。信息保留 0.665。按 [HN 那次实验](https://news.ycombinator.com/item?id=47954745)，它在 token 和质量上都和 caveman 打平。

---

## 横向对比

| | lesstoken | caveman | token-diet | `"Be brief."` |
|---|---|---|---|---|
| 星数 | — | 87,329 ★ | 555 ★ | — |
| 每轮固定成本 | 868（v0.2） | 1,182 | 2,115 | **3** |
| 输出压缩 | **−80.9%** | −74.2% | −64.0% | −67.1% |
| 信息保留 | 0.570 | **0.690** | 0.660 | 0.665 |
| 事实错误 | 0.50 | **0.20** | 0.70 | 0.30 |
| 安全通过 | **100%** | 90% | 100% | 100% |
| 稳定性（σ） | **2.6%** | 11.8% | 9.7% | 2.1% |
| 独立中文规则集 | **有** | 无 | 无 | 无 |
| 危险操作自动退出 | **有** | 部分 | 无 | 无 |

中英文混着用、想要最短回复、又要一道明确的安全闸，选 `lesstoken`。信息保留比长度更重要，选 `caveman`。想用三个 token 拿到大部分好处，选 `"Be brief."`。

### 完全不同的一层

下面这些打的是 `cache_read`，占全部 token 的 **94.67%**，而不是只占 0.71% 的 output。

| 项目 | 星数 | 它压缩什么 |
|---|---|---|
| [rtk-ai/rtk](https://github.com/rtk-ai/rtk) | 69,875 ★ | shell 命令输出，在它进入上下文之前 |
| [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) | 58,199 ★ | 一切，通过一个 API 代理 |
| [mksglu/context-mode](https://github.com/mksglu/context-mode) | 18,771 ★ | MCP 工具返回结果 |

**它们的余量比本 README 里任何东西都大得多。** 如果你的目标是少花钱而不是少读字，从那边开始。对代理方案提一个警告。Anthropic 的 prompt cache 按前缀精确匹配命中，任何改写对话历史的东西都会让缓存失效，把 0.1 倍的 `cache_read` 变成 1.25 倍的 `cache_write`。看你的账单，别看你的 token 计数。

---

## 结构

```
lesstoken/
├── SKILL.md                              skill 本体，这就是全部产品
├── README.md                             英文版
├── README.zh-CN.md                       本文件，信息与英文版对齐
├── LICENSE                               MIT
├── assets/
│   ├── tradeoff-light.png                输出长度与信息保留的权衡（浅色主题）
│   ├── tradeoff-dark.png                 同上，深色主题
│   ├── net-light.png                     净省 token，按质量折算前后
│   ├── net-dark.png                      同上，深色主题
│   ├── ceiling-light.png                 为什么品类天花板不到 1%
│   └── ceiling-dark.png                  同上，深色主题
└── benchmarks/
    ├── METHODOLOGY.md                    数字怎么来的，以及六条局限
    ├── run_benchmark.py                  现取竞品真实 SKILL.md，跑全部 arm
    ├── analyze.py                        重新生成 README 里的每一张表
    └── data/
        ├── results.json                  完整聚合统计，按 arm、按重复
        ├── arm_costs.json                每个 arm 的 system prompt 实测固定成本
        └── redacted_prompts.json         三个被撤下的 prompt 的替换版本
```

---

## 安装

```bash
mkdir -p ~/.claude/skills/lesstoken
curl -sL https://raw.githubusercontent.com/Zane456/lesstoken/main/SKILL.md \
  -o ~/.claude/skills/lesstoken/SKILL.md
```

说 `lesstoken`、`be brief`、`省token`、`极简模式`、`少废话` 触发。说 `stop lesstoken` 或 `正常模式` 关闭。

它就是一个带 YAML frontmatter 的普通 `SKILL.md`，任何读这个格式的 agent 都应该能用。**只在 Claude Code 上测过。**

---

## 复现

```bash
pip install tiktoken
export LLM_API_KEY=...
python benchmarks/run_benchmark.py --model <你的模型> --repeats 3
python benchmarks/analyze.py raw_output.json
```

`run_benchmark.py` 在运行时现取竞品真实的 `SKILL.md`，所以随着它们演进，这个对比依然诚实。

**原始模型输出未发布。** 十个原始 prompt 里有三个含作者未发表的研究细节，`benchmarks/data/redacted_prompts.json` 放着语义等价的替换版本。上面的数字来自原始那一次运行。重跑会接近，不会一模一样。完整细节和这次 benchmark 的全部六条局限写在 [`benchmarks/METHODOLOGY.md`](benchmarks/METHODOLOGY.md) 里，其中最要紧的两条是，生成模型不是 Claude，`cl100k_base` 也不是 Claude 的 tokenizer。

---

## 致谢

- **[caveman](https://github.com/JuliusBrussee/caveman)**，作者 Julius Brussee，本 README 模仿了它的 `HONEST-NUMBERS.md` 格式，而且它关于缩写零收益的判断是对的。
- **[token-diet](https://github.com/Kulaxyz/token-diet)**，作者 Kulaxyz，它公布了分场景的账单拆解，而不是一个孤零零的头条数字。
- **[max-t-dev 的 HN 实验](https://news.ycombinator.com/item?id=47954745)**，贡献了 `"Be brief."` 对照组，这个组难打得让人尴尬。

---

## 许可

MIT © [Zane456](https://github.com/Zane456)
