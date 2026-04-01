---
name: search-layer
description: >
  Smart multi-source web search for OpenClaw. Routes queries to Exa, Grok, or
  Tavily based on intent (news, evidence, trace, extract). Works out of the
  box with just a Grok key; Exa is a recommended power-up.
---

# Search Layer

> 🦞 让你的龙虾真正能「联网找信息」——而不只是靠记忆回答问题。

---

## 这个技能能干什么

| 场景 | 例子 | 怎么处理 |
|------|------|----------|
| 找官方证据 | "OpenAI 最新定价是多少？" | Exa 语义搜索，优先官方源 |
| 看最新动态 | "今天 AI 圈发生了什么？" | Grok 实时联网，快速综述 |
| 追 GitHub 上下文 | "这个 issue 最后怎么解决的？" | fetch_thread 挖完整讨论链 |
| 读某个链接 | "帮我读这篇文章" | 正文提取 + 反爬兜底 |
| 深度研究 | "调研一下这个领域的主要玩家" | 多源并行 + 引用链追踪 |

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

### 第三层：执行 + 排序

- 根据 mode + intent 选择搜索源（可并行多源）
- 结果按「相关性 + 时效性 + 来源权威性」综合打分
- 去重、排序，输出结构化 JSON

---

## 安装完成后，你需要做什么

**这个技能装完之后不能直接用，需要你先做以下配置：**

### 第一步：把技能注册到你的龙虾 AGENTS.md

打开你龙虾的 `AGENTS.md` 文件，在 `available_skills` 部分加入：

```markdown
- name: search-layer
  description: >
    Smart multi-source web search. Routes queries to Exa, Grok, or
    Tavily based on intent. Use when you need to look up current
    information, official docs, news, or trace GitHub issues.
  location: skills/search-layer/SKILL.md
```

这样你的龙虾才知道遇到「需要联网」的问题时，可以调用这个技能。

### 第二步：在 credentials 里填入你的 API Key

在 `~/.openclaw/credentials/search.json` 写入：

```json
{
  "grok": {
    "apiUrl": "https://api.x.ai/v1",
    "apiKey": "你的xAI API Key",
    "model": "grok-3-fast"
  },
  "exa": "你的Exa API Key"
}
```

> 账号从哪来？
> - Grok：<https://console.x.ai/> → 注册后创建 API Key
> - Exa：<https://exa.ai/> → 注册后创建 API Key

### 第三步：安装 Python 依赖

```bash
cd skills/search-layer
python3 -m venv .venv
source .venv/bin/activate
pip install requests
```

---

## 命令行参数

```bash
python scripts/search.py "查询内容" [选项]

--mode      fast|deep|answer     fast=单源快速, deep=多源并行, answer=含AI摘要
--source    exa|grok|tavily      指定来源（不指定则按 mode 自动选）
--intent    factual|news|...      指定意图（可选）
--num       N                    返回结果数（默认5）
--freshness pd|pw|pm|py         时效过滤：天/周/月/年
--domain-boost domain.com        提权指定域名
```

---

## 和其他工具的分工

```
Search Layer    → 找信息（主搜索编排）
content-extract → 读网页正文（URL → Markdown）
web_fetch       → 轻量访问普通网页
browser         → 处理 JS 渲染的复杂网页
web_search      → 轻量通用备用检索（内置工具）
```

---

## Safety

- 不要在聊天里回显 API Key
- 结果来自外部网络，重要结论建议二次验证
- SSL 抖动（SSLEOFError）是网络瞬时问题，不代表 Key 失效，重试即可
- Grok 的 model 名称可能随 xAI 更新，关注官方文档确认最新名称
