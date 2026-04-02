# Search Layer — OpenClaw 搜索技能

> 一个面向 OpenClaw 龙虾的智能搜索技能，把「去哪找」「怎么找」「找完怎么处理」变成一套可复用的标准流程。

---

## 核心价值

### 1. 问题分流，而不是无脑搜索

你可以把 Search Layer 理解成两层判断：

- **Mode**：先决定这是什么类型的问题，应该走哪条搜索路线
- **Intent**：再决定这条路线里，什么最重要（准确性？时效性？对比信息？）

一句话：
- `mode` 决定 **走哪条路**
- `intent` 决定 **这条路上更重视什么**

所有搜索任务先按「类型」分流：

| Mode | 适合场景 | 默认引擎 |
|------|----------|----------|
| Evidence | 找官方文档、定价、API 规范 | Exa |
| Fresh | 看最新动态、新闻、舆论 | Grok |
| Trace | 追 GitHub issue / 论坛讨论链 | fetch_thread |
| Extract | 用户给了链接，要读正文 | content-extract |

### 2. 意图识别，调整排序权重

分流之后，再细分 `intent`，决定这次搜索到底更看重什么。

- **factual**：查一个明确事实
  - 适合：参数、定价、发布时间、定义、配置项
  - 排序更偏向：**权威来源 + 准确性**
  - 例子：`OpenAI 最新 API 定价是多少？`

- **status**：看某件事现在进展到哪了
  - 适合：项目状态、功能上线情况、issue 是否修复、模型是否发布
  - 排序更偏向：**最近进展 + 状态更新**
  - 例子：`GPT-5 现在开放给哪些用户了？`

- **comparison**：比较两个或多个人/产品/方案
  - 适合：A vs B、优缺点、差异、取舍
  - 排序更偏向：**覆盖面 + 对比信息密度**
  - 例子：`Exa 和 Tavily 哪个更适合做研究型搜索？`

- **tutorial**：找教程或操作步骤
  - 适合：安装、配置、排错、上手流程
  - 排序更偏向：**步骤清晰 + 可操作性**
  - 例子：`怎么在 OpenClaw 里安装一个自定义 skill？`

- **exploratory**：开放式探索一个主题
  - 适合：趋势扫描、赛道调研、方向梳理
  - 排序更偏向：**信息广度 + 代表性来源**
  - 例子：`最近 AI Agent 领域有哪些值得关注的新方向？`

- **news**：看最新新闻和动态
  - 适合：今天发生了什么、最近的大事、舆论变化
  - 排序更偏向：**时效性**
  - 例子：`今天 AI 圈有哪些大新闻？`

- **resource**：找资源集合
  - 适合：工具列表、论文合集、数据集、学习资料导航
  - 排序更偏向：**整理度 + 汇总质量**
  - 例子：`给我一份多模态模型学习资源清单`

简单理解：
- `mode` 决定 **走哪条路**
- `intent` 决定 **这条路上更重视什么**

### 3. 结果打分 + 去重

多源结果汇总后经过：关键词相关度打分 + 时效性打分 + 来源权威性打分 + URL 去重。

---

## 功能说明

### 支持的搜索来源

| 来源 | 特点 | 配置项 |
|------|------|--------|
| Grok | xAI 模型，实时感知强，适合新闻/舆情 | `grok.apiKey` + `grok.apiUrl` |
| Exa | 语义搜索，适合官方文档/技术内容 | `exa` |
| Tavily | AI 搜索，可直接生成答案 | `tavily` |

### 搜索模式（--mode）

- `fast`：Exa only，低延迟
- `deep`：Exa + Tavily + Grok 并行，最大覆盖
- `answer`：Tavily AI 答案模式

### 意图类型（--intent）

你可以手动指定 intent，让 skill 更懂你这次到底想要什么：

- `factual`：查一个准确事实
- `status`：看最新状态 / 进展
- `comparison`：做对比分析
- `tutorial`：找教程 / 步骤
- `exploratory`：开放式探索
- `news`：最新新闻 / 动态
- `resource`：资料 / 工具 / 资源汇总

如果你不确定，就先不传，skill 会自己判断；但如果你的问题很明确，手动指定会更稳。

### 时效过滤（--freshness）

`pd`（今天）/ `pw`（一周内）/ `pm`（一月内）/ `py`（一年内）

---

## 安装

就一件事：**把这个 GitHub 仓库复制到你龙虾的 `skills/search-layer` 目录里。**

```bash
cd 你的龙虾 workspace 路径
git clone https://github.com/bigsongeth/search-layer.git skills/search-layer
```

剩下的首次配置（比如注册到 `AGENTS.md`、填写 `credentials/search.json`、安装 `requests`），不在这里写死，而是交给龙虾在第一次触发 Search Layer 时去主动引导主人完成。

## 目录结构

```
search-layer/
├── SKILL.md                    # 技能调度指南（给龙虾看的说明书）
├── README.md                   # 本文件（给龙虾主人看的安装指南）
├── scripts/
│   ├── search.py               # 主搜索脚本
│   ├── fetch_thread.py          # GitHub / 论坛讨论链追踪
│   ├── exa_free_client.py      # Exa 代理客户端
│   ├── chain_tracker.py         # 引用链深挖
│   └── relevance_gate.py        # 结果相关性过滤
└── references/
    ├── authority-domains.json   # 权威域名列表（影响打分）
    ├── intent-guide.md          # 意图选择参考
    └── exa-free-proxy.md        # Exa 代理端点说明
```

---

## 常见问题

**Q: Grok 搜索没结果？**
检查 `grok.apiKey` 是否正确，`apiUrl` 是否是 `/v1` 结尾的 OpenAI-compatible 地址。

**Q: Exa 报 401 Invalid API key？**
Key 已失效，去 Exa Dashboard 重新创建一个新的 Key，替换掉 `search.json` 里的旧值。

**Q: 出现 SSLEOFError？**
网络瞬时抖动，不是 Key 问题，重试一次就好。

**Q: 搜出来的结果不理想？**
尝试加 `--intent` 参数指定意图类型，或加 `--freshness` 指定时效范围。

---

## 和其他工具的分工

```
Search Layer    → 找信息（主搜索编排）
content-extract → 读网页正文（URL → Markdown）
web_fetch       → 轻量访问普通网页
browser         → 处理 JS 渲染的复杂网页
web_search      → 内置轻量备用检索
```

---

## License

MIT
