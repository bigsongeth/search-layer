---
name: search-layer
description: >
  Smart multi-source web search for OpenClaw. Routes queries to Exa, Grok, or
  Tavily based on intent (news, evidence, trace, extract). Supports Exa key
  pool rotation for high availability. Works out of the box with just a Grok
  key; Exa and Tavily are optional power-ups.
---

# Search Layer

> 🦞 让你的龙虾真正能「联网找信息」——而不只是靠记忆回答问题。

Search Layer 是一个为 OpenClaw 设计的搜索编排技能。它不只是调一个搜索引擎，而是根据问题类型自动决定去哪里找、怎么找、找到之后怎么排序——让 AI 助手的信息获取能力从「能用」变成「好用」。

---

## 核心价值

**普通做法**：直接调一个搜索 API，把结果扔回去。

**Search Layer 的做法**：

1. 先判断这个问题是「找证据」还是「看动态」还是「追溯上下文」
2. 根据判断选择合适的搜索源（Exa / Grok / Tavily）
3. 结果按「相关性 + 时效性 + 来源权威性」综合打分排序
4. 如果单个 API Key 挂了，自动换下一个继续跑

一句话：**帮 AI 把「该去哪问」这件事想清楚了。**

---

## 能干什么

| 场景 | 例子 | 怎么处理 |
|------|------|----------|
| 找官方证据 | "OpenAI 最新定价是多少？" | Exa 语义搜索，优先官方源 |
| 看最新动态 | "今天 AI 圈发生了什么？" | Grok 实时联网，快速综述 |
| 追 GitHub 上下文 | "这个 issue 最后怎么解决的？" | fetch_thread 挖完整讨论链 |
| 读某个链接 | "帮我读这篇文章" | 正文提取 + 反爬兜底 |
| 深度研究 | "帮我调研这个领域的主要玩家" | Exa + Tavily 多源并行 + 引用链追踪 |

---

## 搜索引擎说明

### Grok（推荐首选，实时感知强）
- xAI 提供的模型，对最新事件高度敏感
- 适合：新闻、舆情、「最近发生了什么」类问题
- 注册地址：<https://console.x.ai>
- 免费额度：有，按量计费，新用户有试用额度

### Exa（语义搜索，适合找证据）
- 专注语义理解的搜索引擎，理解「你问的是什么意思」而不只是关键词
- 适合：官方文档、学术内容、技术资料、找可信来源
- 注册地址：<https://exa.ai>
- 免费额度：每月有免费搜索次数，超出按量付费
- 支持多 Key 轮询池：把多个 Key 配进去，自动轮换，抗限流

### Tavily（AI 搜索 + 自带摘要）
- 除了给链接，还能直接生成一段「AI 综合的答案」
- 适合：需要快速结论、不想自己整理搜索结果的场景
- 注册地址：<https://tavily.com>
- 免费额度：有，每月限量

---

## 快速上手

### 第一步：准备至少一个 API Key

**最低配置（只需要 Grok）：**
```json
// ~/.openclaw/credentials/search.json
{
  "grok": {
    "apiUrl": "https://api.x.ai/v1",
    "apiKey": "你的 xAI API Key",
    "model": "grok-3-fast"
  }
}
```

**推荐配置（Grok + Exa，覆盖更全）：**
```json
{
  "grok": {
    "apiUrl": "https://api.x.ai/v1",
    "apiKey": "你的 xAI API Key",
    "model": "grok-3-fast"
  },
  "exa": "你的单个 Exa API Key"
}
```

**进阶配置（Exa 多 Key 轮询池）：**
```json
{
  "grok": {
    "apiUrl": "https://api.x.ai/v1",
    "apiKey": "你的 xAI API Key",
    "model": "grok-3-fast"
  },
  "exa": {
    "apiKey": "主 Exa Key（代理或官方）",
    "apiUrl": "https://api.exa.ai/search"
  },
  "exaKeys": [
    "官方 Exa Key 1",
    "官方 Exa Key 2",
    "..."
  ],
  "tavily": "你的 Tavily API Key"
}
```

> 💡 `exaKeys` 是官方 Exa Key 的轮询池。单个 Key 限流或失败时，自动切换下一个。

### 第二步：安装依赖

```bash
cd skills/search-layer
python3 -m venv .venv
source .venv/bin/activate
pip install requests
```

### 第三步：测试一下

```bash
source .venv/bin/activate
python scripts/search.py "今天 AI 有什么大新闻" --mode fast --num 5
```

---

## 工作原理

### 第一层：Mode 识别（这是哪类问题？）

```
Evidence  → 找证据/原文     → 优先 Exa（语义搜索，来源可信）
Fresh     → 看最新动态      → 优先 Grok（实时联网，快速综述）
Trace     → 追讨论上下文    → fetch_thread（挖 GitHub/论坛链路）
Extract   → 读某个 URL     → content-extract（正文提取）
```

### 第二层：Intent 识别（更细的意图分类）

```
factual      → 查准确事实（权威性权重高）
status       → 看进展/状态（时效性权重高）
comparison   → 做对比分析
tutorial     → 找教程/操作步骤
news         → 最新新闻/动态（时效性权重最高）
exploratory  → 开放式探索
resource     → 资料汇总
```

不同 intent 会影响搜索结果的排序权重，让最终输出更贴近你真正要的东西。

### 第三层：执行 + 排序

- 根据 mode + intent 选择搜索源（可并行多源）
- 结果按「关键词相关度 + 时效性 + 来源权威性」打分
- 去重、排序，输出 JSON

---

## 命令行参数

```bash
python scripts/search.py "查询内容" [选项]

--mode      fast|deep|answer     fast=单源快速, deep=多源并行, answer=含AI摘要
--source    exa|grok|tavily      指定来源（不指定则按 mode 自动选）
--intent    factual|news|...     指定意图（可选，不传也行）
--num       N                    返回结果数（默认5）
--freshness pd|pw|pm|py          时效过滤：天/周/月/年
--domain-boost domain.com        提权指定域名
```

---

## 目录结构

```
skills/search-layer/
├── SKILL.md                    # 本文档
├── scripts/
│   ├── search.py               # 主搜索脚本（1500行，核心逻辑全在这）
│   ├── fetch_thread.py         # GitHub/论坛讨论串追踪
│   ├── exa_free_client.py      # Exa 代理专用客户端
│   ├── chain_tracker.py        # 引用链追踪（深度研究用）
│   └── relevance_gate.py       # 相关性过滤
└── references/
    ├── intent-guide.md         # Intent 分类详细指南
    ├── authority-domains.json  # 权威域名列表
    └── exa-free-proxy.md       # Exa 代理接入说明
```

---

## 和其他工具的分工

```
Search Layer    → 找信息（主搜索编排）
content-extract → 读网页正文（URL → Markdown）
web_fetch       → 轻量访问普通网页
browser         → 处理需要 JS 渲染的复杂网页
web_search      → 轻量通用备用检索（内置工具）
```

> 搜索 ≠ 读网页。这两件事分开做，各自用各自合适的工具。

---

## 注意事项

- **不要在聊天里回显 API Key**（logs 会留下来）
- `exaKeys` 里的 Key 如果收到 `401 Invalid API key`，建议手动从列表里移除
- 结果来自外部网络，重要结论建议二次验证
- Grok 的 model 名称可能随 xAI 随时更新，关注官方文档确认最新 model 名称
- SSL 抖动（SSLEOFError）是网络瞬时问题，不代表 Key 失效，重试即可
