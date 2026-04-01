# Search Layer — OpenClaw 搜索技能

> 一个面向 OpenClaw 龙虾的智能搜索技能，把「去哪找」「怎么找」「找完怎么处理」变成一套可复用的标准流程。

---

## 核心价值

### 1. 问题分流，而不是无脑搜索

所有搜索任务先按「类型」分流：

| Mode | 适合场景 | 默认引擎 |
|------|----------|----------|
| Evidence | 找官方文档、定价、API 规范 | Exa |
| Fresh | 看最新动态、新闻、舆论 | Grok |
| Trace | 追 GitHub issue / 论坛讨论链 | fetch_thread |
| Extract | 用户给了链接，要读正文 | content-extract |

### 2. 意图识别，调整排序权重

分流之后，再细分意图来调整搜索结果的排序逻辑：

- `news` → 时效性权重最高
- `factual` → 来源权威性权重最高
- `comparison` → 关键词覆盖权重最高
- 以此类推...

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

`factual` / `status` / `comparison` / `tutorial` / `exploratory` / `news` / `resource`

### 时效过滤（--freshness）

`pd`（今天）/ `pw`（一周内）/ `pm`（一月内）/ `py`（一年内）

---

## 安装指南

### 第一步：把这个技能装进你的龙虾

把你的龙虾 `workspace/skills/` 目录下克隆一份：

```bash
cd 你的龙虾workspace路径
git clone https://github.com/bigsongeth/search-layer.git skills/search-layer
```

### 第二步：告诉你的龙虾「我有这个技能了」

打开你的龙虾 `AGENTS.md` 文件，在 `available_skills` 部分加一行：

```markdown
- name: search-layer
  description: >
    Smart multi-source web search. Routes queries to Exa, Grok, or
    Tavily based on intent. Use when you need to look up current
    information, official docs, news, or trace GitHub issues.
  location: skills/search-layer/SKILL.md
```

加完之后，你的龙虾就知道在遇到「需要联网」的问题时，可以调用这个技能。

### 第三步：配置你的 API Key

在 `~/.openclaw/credentials/search.json` 里写入你的 Key：

**最简配置（推荐 Grok + Exa）：**
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

> 如果你用的是其他 OpenAI-compatible 的 Grok 接口，修改 `apiUrl` 和 `model` 为你实际的配置。

**Grok 单独使用（最小配置）：**
```json
{
  "grok": {
    "apiUrl": "https://api.x.ai/v1",
    "apiKey": "你的xAI API Key",
    "model": "grok-3-fast"
  }
}
```

> **账号从哪来？**
> - **Grok**：<https://console.x.ai/> 注册后创建 API Key
> - **Exa**：<https://exa.ai/> 注册后创建 API Key

### 第四步：安装依赖

```bash
cd skills/search-layer
python3 -m venv .venv
source .venv/bin/activate
pip install requests
```

### 第五步：测试一下

```bash
source .venv/bin/activate
python scripts/search.py "今天 AI 有什么大新闻" --mode fast --num 5
```

看到 JSON 输出里 `results` 有内容，就说明安装成功了。

---

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
