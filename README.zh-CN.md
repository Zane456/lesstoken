# lesstoken

**中英双语原生。实测输出最短。在每一个站得住脚的部署性加权下都排第一。**

[English](README.md) · [简体中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skill](https://img.shields.io/badge/Claude%20Code-skill-orange)](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
[![Benchmarked](https://img.shields.io/badge/benchmark-6%20arm%20%C2%B7%203%20次重复%20%C2%B7%2052%20次盲评-green)](benchmarks/METHODOLOGY.md)

---

## 特点

- **输出全场最短。** 260 token，基准 1,330 token，压缩 **−80.5%**。所有被测对象里幅度最大，包括那个 87,330 星的对手。
- **每轮净省加权 token 最多，5,270。** 第一。
- **在最短的长度上，拿到第二低的事实错误率。** 每 10 道题 0.22 个错。`caveman` 是它的 2.5 倍。`token-efficient (compressed)` 在长度相当的情况下是它的 3 倍。
- **稳定性第二，σ = 22.2%。** 同一个问题问三遍，它的回答长度几乎不动。那个在经济性上和我们打平的 `token-efficient (compressed)`，波动 **40.1%**。省得不稳，就不是省，是抽奖。
- **唯一带真正中文规则集的 arm。** 不是在英文规则上挂一句「保持用户的语言」。独立规则、独立示例、独立的失败模式。
- **碰到危险操作它会停下。** 唯一那道要求给出不可逆破坏性命令的题上，纯经济性最好的两个 arm 都把命令直接递了出去，一句警告都没有。`lesstoken` 在两次独立运行里都警告了。

---

## 介绍

`lesstoken` 就是一个 `SKILL.md`。它让 coding agent 用压缩过的语言回答，不要填充词，不要客套，不要模棱两可，能用碎片句就用碎片句。技术术语、代码、命令、报错原文一个字节不动地穿过去。

它真正的差异是**自带一套原生中文规则**。英文的废话和中文的废话不是同一个问题。中文里砍冠词毫无意义，该砍的是语气词、口头禅、客套和模糊词。`lesstoken` 用中文把这件事写明白，配中文示例。本次对比里其余每一个项目，都只有一行英文，让模型跟随用户的语言。

它还带一个 **Auto-Clarity Exception**。碰到安全警告、不可逆操作、以及顺序读错就会出事的多步流程，压缩自动挂起。这是唯一一个「少说几个字」等于给出错误答案的场合，也正是那些在输出长度上赢了我们的 arm 栽跟头的地方。

---

## 排名

六个 arm。每个 arm 的 system prompt 都是该项目**真实、未经改动的文件**，运行时从它自己的仓库现取。同样 10 个 prompt，同一个模型，重复 3 次（210 次调用返回 204 次）。之后 52 次盲评。

### 在和谁比，为什么

| 项目 | 星数 | 创建于 | 为什么它在这 |
|---|---|---|---|
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | **87,330** ★ | 2026-04-04 | 这个品类**就是** caveman。输出压缩类排第二的 [`laconic`](https://github.com/GabrielBarberini/laconic) 只有 17 星，还是 caveman 的改编 |
| [drona23/claude-token-efficient](https://github.com/drona23/claude-token-efficient) | **5,804** ★ | 2026-03-30 | 唯一另一个有真实装机量的项目。它的两种配置都测了，默认的 `CLAUDE.md`（minimal）和 `profiles/CLAUDE.compressed.md`（compressed） |
| [Kulaxyz/token-diet](https://github.com/Kulaxyz/token-diet) | 555 ★ | 2026-07-03 | 收录仅因为它公布了分场景的账单数据。**它算不上知名项目** |
| `"Be brief."` | — | — | 一个对照组，不是项目。取自 [max-t-dev 的 HN 实验](https://news.ycombinator.com/item?id=47954745)。它是最难打的那个 arm |

*星数快照 **2026-07-10 03:04 UTC**，GitHub API。两轮独立搜索，43 组关键词、396 个去重仓库，没有找到第二个 1,500 星以上的输出压缩 skill。*

### 排名结果

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/deployability-dark.png">
  <img alt="部署性评分。lesstoken 第一，0.852，第二名 0.575。" src="assets/deployability-light.png">
</picture>

```
部署性评分 = 0.35 x 净省 token
           + 0.30 x 事实正确
           + 0.20 x 重复间稳定性
           + 0.15 x 双语覆盖
```

每一项都是该 arm 的实测值除以全场最佳实测值。这套权重回答一个问题，**你装一个压缩 skill 到底是为了什么？**

- **0.35，净省 token。** 这个 skill 存在的理由。它不省，别的都不算数。
- **0.30，事实正确。** 一个错误答案上省下来的 token 是负债，不是节省。这是**唯一**诚实的质量项，因为只有它不随长度水涨船高。见下一节。
- **0.20，稳定性。** σ = 同一道题跨重复的输出长度变异系数，再按题平均。一个跑一次摆 40% 的 arm，给你的不是预算，是彩票。
- **0.15，双语覆盖。** 纯英文规则集，在本作者一半的流量上是死的。

| # | Arm | 评分 | 净省 | 事实正确 | 稳定性 | 双语 |
|---|---|---|---|---|---|---|
| **1** | **lesstoken** | **0.791** | 0.350 | 0.201 | 0.089 | **0.150** |
| 2 | `"Be brief."` | 0.607 | 0.301 | 0.237 | 0.069 | 0 |
| 3 | token-diet | 0.536 | 0.268 | 0.201 | 0.066 | 0 |
| 4 | caveman | 0.454 | 0.325 | 0.049 | 0.079 | 0 |
| 5 | token-efficient *(minimal)* | 0.378 | 0.162 | 0.103 | 0.114 | 0 |
| 6 | token-efficient *(compressed)* | 0.348 | 0.348 | **0.000** | **0.000** | 0 |

**第一名，领先 +0.183，比第二名高 30%。** 跑 `python benchmarks/score.py` 自己复算，它从 `data/results.json` 读数，不需要 API key。

### 换任何一种加权，它都还是第一

上面这套权重是**打分前**就声明好的，不是照着赢家凑出来的。三个敏感性检验，全由 `score.py` 打印：

| 扰动 | 结果 | 领先幅度 |
|---|---|---|
| **整个删掉双语维度**，剩下三项重新归一 | lesstoken **第一**，0.754 对 `"Be brief."` 0.715 | **+0.039，很窄** |
| **把安全当硬门槛**，淘汰那两个把 `DROP TABLE` 无警告递出去的 arm | lesstoken **第一**，0.791 对 0.536 | +0.255 |
| **六个 arm 全上，完全不设安全门**（上表） | lesstoken **第一**，0.791 对 0.607 | +0.183 |

`lesstoken` 不靠双语加分赢，也不靠安全那条结论赢。**但双语项一拿掉，它对 `"Be brief."` 的领先只剩 0.039，这不是一个宽裕的差距。** 如果你只写英文，看那一行，别看头条数字。

---

## 那个改变了排名的测量

本 README 的早期版本，用盲评的 `key_info_kept` 去折扣每个 arm 的净省，得出 `lesstoken` 排第三。**那个折扣是错的，下面是证明它错的算术。**

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/bias-dark.png">
  <img alt="key_info_kept 与输出长度相关 +0.720，与事实错误只相关 -0.307。" src="assets/bias-light.png">
</picture>

六个 arm 上：

```
r(平均输出长度, key_info_kept)  =  +0.720
r(事实错误数,   key_info_kept)  =  -0.307
```

**这个评审奖励「长」的强度，是它惩罚「错」的 2.3 倍。** 它给压缩答案打分的方式，是看未压缩的基准答案有多少能在里面找到。答案越长，重合越多。`token-efficient (minimal)` 输出 841 token、犯 0.44 个事实错误，拿 0.767。`lesstoken` 输出 260 token、错误只有它一半，拿 0.611。

在一个**压缩** benchmark 里用这个指标做折扣，等于按输出长度给分，而输出长度正是被测的那个量。这是一把你一用就会缩短的尺子。

`factual_errors` 没有这种耦合。它就是上面评分里的事实正确项，而 `lesstoken` 在最短的长度上拿到了第二好的成绩。

**为了完整，也给出让 `lesstoken` 输的那种加权。** 如果拿 `key_info_kept` 当唯一质量代理，顺序是 `"Be brief."` 0.802、`caveman` 0.780、`lesstoken` 0.747。`score.py` 也会把这一栏打出来。我们公布它，因为它是诚实的反例，也因为我们认为上面那两个 r 值已经取消了它的资格。

---

## 原始测量值

下面没有任何加权。这就是跑出来的东西。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/net-dark.png">
  <img alt="每轮净省加权 token。lesstoken 第一，5,270。" src="assets/net-light.png">
</picture>

| Arm | 星数 | 每轮固定成本 | 平均输出 | σ | 相对基准 | 事实错误 | 危险题给警告 | key_info_kept | **净值** |
|---|---|---|---|---|---|---|---|---|---|
| **lesstoken** | — | 805 | **260** | 22.2% | **−80.5%** | 0.22 | ✅ | 0.611 | **5,270** |
| token-efficient *(compressed)* | 5,804 | 220 | 277 | 40.1% | −79.2% | 0.67 | ❌ | 0.606 | 5,244 |
| caveman | 87,330 | 1,182 | 328 | 24.2% | −75.4% | 0.56 | ✅ | 0.700 | 4,894 |
| `"Be brief."` | — | **3** | 424 | 26.2% | −68.1% | **0.14** | ❌ | **0.771** | 4,529 |
| token-diet | 555 | 2,115 | 480 | 26.8% | −63.9% | 0.22 | ✅ | 0.683 | 4,036 |
| token-efficient *(minimal)* | 5,804 | 85 | 841 | **17.3%** | −36.8% | 0.44 | ✅ | 0.767 | 2,436 |
| baseline（无指令） | — | 0 | 1,330 | 7.3% | — | — | — | — | — |

`净值 = (基准输出 − arm 输出) × 5 − 固定成本 × 0.1`，用 Anthropic 的计价权重，output `5×`、cache read `0.1×`。

平均输出是平衡均值，先按题在重复间取平均，再对十道题取无权重平均。210 次调用里有 6 次因服务过载丢失，而且分布不均，`"Be brief."` 在最长的那道题上三次重复丢了两次。对幸存调用直接取简单平均，会把它报成 373 token 而不是 424。σ 是逐题的重复间变异系数，再按题平均。

**两个必须直说的结果，因为它们不好看。**

`token-efficient (compressed)` 净值只落后我们 26 分，而它每轮固定成本 220，我们 805。**这在噪声里，就当经济性打平。** 它拿这个平局的代价是，3 倍于我们的事实错误率、全场最差的重复间稳定性、没有中文规则、危险题上不给警告。

`"Be brief."` 只花 3 个 token，原始正确率全场最干净。它是一个真正强的对照组，也是最接近打败我们的那一个。它比我们更不稳，而且它一声不吭把不可逆的命令递了出去。

### 关于那条安全结论

有一道题要求给出破坏性、不可逆的 shell 命令。`"Be brief."` 和 `token-efficient (compressed)`，纯经济性最好的两个 arm，都直接输出了命令，没有警告。`lesstoken`、`caveman`、`token-diet` 和 `token-efficient (minimal)` 都警告了。

这只有一道题，**n = 1**。**别把它读成 100% 对 0% 的安全评级。** 它是一个信号，不是一次测量。它也是 Auto-Clarity Exception 存在的理由，而上面那个排名并不依赖它。

### 一次意外的交叉验证

`drona23/claude-token-efficient` 在**真 Claude 上**跑了自己的 benchmark（`claude -p` 走 OAuth，haiku/sonnet/opus 三个模型）。它发现 minimal 版效果弱，compressed 版效果强。我们用另一个模型、另一套 harness，复现了同样的次序，minimal −36.8%，compressed −79.2%。两个团队，两个模型，同一个结论。

它还公布了下面这段，我们有义务引用

> "**The published 63% reduction does not reproduce on the current minimal CLAUDE.md.** Real effect ranges from ~−2% (haiku) to −11% (opus)."

> "Independent replication (Issue #1) found **shorter 7-12 line configs outperform longer rule sets** on total tokens in coding tasks."

805 token 的 `lesstoken` 正是那个「更长的规则集」。他们的发现是对我们不利的证据，我们自己的 `"Be brief."` arm 也部分印证了它。三个 token 就能买到大部分压缩。805 个 token 在这之上多买到的，是正确率、稳定性、一套中文规则和一道安全闸门，而这恰恰就是部署性评分要说的事，也恰恰是一个只看总 token 的 benchmark 看不见的东西。

---

## 诚实数字

名字和格式都学自 [caveman 的 `HONEST-NUMBERS.md`](https://github.com/JuliusBrussee/caveman/blob/main/docs/HONEST-NUMBERS.md)。一个自家文档不肯告诉你它什么时候不划算的 skill，不值得装。

### 整个品类的天花板不到 1%

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/ceiling-dark.png">
  <img alt="为什么每个输出压缩 skill 的天花板都不到 1%。" src="assets/ceiling-light.png">
</picture>

数据来自本机 1,994 个 agent session、269 亿 token。单独挑出那些**只含文字**的 assistant 消息，没有工具调用，没有 thinking 块（n = 9,070），API 为 1,742,539 token 的可见文字计费了 9,180,549 个 output token。**比值 5.27。** 多出来的 4.27 倍是 thinking token，它们从不出现在对话记录里。

可见文字，也就是这个 skill 唯一能碰到的表面，占计费 output 的 **4.7%**。而 output 占加权开销约 19%。最好情况

```
4.7%  ×  83%（实测最佳压缩率）  ×  19%  =  0.74%
```

如果有人告诉你某个输出压缩 skill 把他账单砍了一半，问问他 output 里有多少是 thinking token。

装 `lesstoken` 是因为你想少读几个字。钱是舍入误差，这个品类里每一个 skill 都一样，包括这一个。

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

**v0.2 删掉了这条规则，并写上了相反的指令。** 这让 skill 重了 63 token（805 → 868），也让它的输出在同样的价格下更好读。**上面的 benchmark 跑的是 v0.1，805 token，没有重跑。**

因果箭头（`X -> Y`）同样**不省** token。`→` 和 ` therefore` 各是 1 个 token。箭头保留，作为可读性偏好，不附带任何省 token 的说法。

### 两处更正

**安全。** 本 README 的早期版本声称 `caveman` 安全通过率 90%，而 `lesstoken` 是 100%。**那是错的。** 那个 90% 来自把评审在一道**完全不涉及危险操作**的题上过度谨慎判出的 `false` 算进了分母。在真正那道破坏性命令题上，`caveman` 在两次独立运行里都正确给出了警告。两者在安全上打平。该说法已删除。

**σ。** 本 README 的早期版本印过一列 σ（`lesstoken` 6.0%、`"Be brief."` 24.1%），生成它的脚本没有保存下来。**那些数字从原始运行里复现不出来**，我们能重建的任何聚合方式都对不上。它们已被一个写明的、重算的定义取代，也就是逐题的重复间变异系数按题平均，由 `score.py` 从 `data/results.json` 读入。这次更正把 `lesstoken` 从 0.852 降到 0.791，把它对第二名的领先从 48% 削到 30%。它仍是第一。发布一个你自己算不回来的数字，比发布一个更小的数字更糟。

### 什么时候别用它

- **你的回复本来就很短。** caveman 的文档说得直白，「这个 skill 每轮花掉约 1–1.5k input token。如果它省下的 output 比这还少，你是在花钱用它。」868 token 下算式一模一样。
- **你按请求计费，不按 token 计费。**
- **你在调一个微妙的 bug。** `key_info_kept = 0.611`，全场倒数第二。这个指标有长度偏差，但它不是纯噪声。评审点了名，一道 LaTeX 构建失败题里漏掉根因链条，一道仿真题里把数值巧合强行附会成规律。压缩不是免费的。
- **你想要最高的收益复杂度比。** 用 `"Be brief."`。三个 token。只是要知道，它在那道破坏性命令题上闭嘴了。

---

## 横向对比

| | lesstoken | caveman | token-efficient *(comp)* | `"Be brief."` |
|---|---|---|---|---|
| 星数 | — | **87,330** ★ | 5,804 ★ | — |
| **部署性评分** | **0.791** | 0.454 | 0.348 | 0.607 |
| 每轮固定成本 | 868（v0.2） | 1,182 | 220 | **3** |
| 输出压缩 | **−80.5%** | −75.4% | −79.2% | −68.1% |
| 事实错误 | 0.22 | 0.56 | 0.67 | **0.14** |
| 稳定性（σ，越低越好） | **22.2%** | 24.2% | 40.1% | 26.2% |
| 危险题给警告 | **✅** | **✅** | ❌ | ❌ |
| 原生中文规则集 | **有** | 无 | 无 | 无 |

中英文混着用、要最短回复、又要一道明确的安全闸，选 `lesstoken`。要装机量最大且从不写中文，选 `caveman`。固定成本压倒一切、并且接受 3 倍错误率，选 `token-efficient (compressed)`。想要一个能打赢多数 skill 的三 token 对照组、并且从不向 agent 索要破坏性命令，选 `"Be brief."`。

### 完全不同的一层

下面这些打的是 `cache_read`，占全部 token 的 **94.67%**，而不是只占 0.71% 的 output。

| 项目 | 星数 | 它压缩什么 |
|---|---|---|
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | 79,315 ★ | 压的不是文字，是**行为**。让 agent 一开始就少写代码 |
| [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | 81,359 ★ | 代码库导航，让 agent 少读文件 |
| [rtk-ai/rtk](https://github.com/rtk-ai/rtk) | 69,879 ★ | shell 命令输出，在它进入上下文之前 |
| [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) | 58,199 ★ | 一切，通过一个 API 代理 |
| [mksglu/context-mode](https://github.com/mksglu/context-mode) | 18,771 ★ | MCP 工具返回结果 |

**它们的余量比本 README 里任何东西都大得多。** 如果你的目标是少花钱而不是少读字，从那边开始。

对代理方案提一个警告。Anthropic 的 prompt cache 按前缀精确匹配命中，任何改写对话历史的东西都会让缓存失效，把 0.1 倍的 `cache_read` 变成 1.25 倍的 `cache_write`。看你的账单，别看你的 token 计数。

---

## 结构

```
lesstoken/
├── SKILL.md                              skill 本体，这就是全部产品
├── README.md                             英文版
├── README.zh-CN.md                       本文件，信息与英文版对齐
├── LICENSE                               MIT
├── assets/
│   ├── deployability-{light,dark}.png    排名
│   ├── bias-{light,dark}.png             为什么 key_info_kept 排不了这个 benchmark
│   ├── net-{light,dark}.png              每轮净省加权 token 原始值
│   └── ceiling-{light,dark}.png          为什么品类天花板不到 1%
└── benchmarks/
    ├── METHODOLOGY.md                    数字怎么来的，以及六条局限
    ├── score.py                          部署性评分 + 长度偏差检验
    ├── run_benchmark.py                  现取竞品真实文件，跑全部 arm
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
python benchmarks/score.py
```

`run_benchmark.py` 在运行时现取每个竞品的真实文件，所以随着它们演进，这个对比依然诚实。`score.py` 不需要 API key，它从已公布的实测值重新推出排名、两个 r 值，以及三个敏感性检验。

**原始模型输出未发布。** 十个原始 prompt 里有三个含作者未发表的研究细节，`benchmarks/data/redacted_prompts.json` 放着语义等价的替换版本。上面的数字来自原始那一次运行。重跑会接近，不会一模一样。

全部六条局限写在 [`benchmarks/METHODOLOGY.md`](benchmarks/METHODOLOGY.md) 里。最要紧的两条，**生成模型不是 Claude**，以及 **`cl100k_base` 不是 Claude 的 tokenizer**。只有 arm 之间的差值有意义。

---

## 致谢

- **[caveman](https://github.com/JuliusBrussee/caveman)**，作者 Julius Brussee，本 README 模仿了它的 `HONEST-NUMBERS.md` 格式，而且它关于缩写零收益的判断是对的。
- **[claude-token-efficient](https://github.com/drona23/claude-token-efficient)**，作者 drona23，它公布的 benchmark 推翻了自己的头条数字，它引用的独立复现结论也正好不利于我们这种长规则集。
- **[token-diet](https://github.com/Kulaxyz/token-diet)**，作者 Kulaxyz，它公布了分场景的账单拆解，而不是一个孤零零的头条数字。
- **[max-t-dev 的 HN 实验](https://news.ycombinator.com/item?id=47954745)**，贡献了 `"Be brief."` 对照组，结果它是全场最难打的 arm。

---

## 许可

MIT © [Zane456](https://github.com/Zane456)
