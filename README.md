# Search Layer — OpenClaw 搜索技能

> 一个面向 OpenClaw 龙虾的智能搜索技能，把「去哪找」「怎么找」「找完怎么处理」这三件事变成一套可复用的标准流程。

## 这个技能是什么？

Search Layer 是一个搜索编排层，不是单纯的搜索引擎封装。

它解决的核心问题是：

- 不同问题应该用不同方式搜索（找官方文档 vs 找今日新闻 vs 追 GitHub issue，根本不是同一件事）
- 单一 API Key 容易限流、单点挂掉，需要有轮询兜底
- 搜索结果需要按相关性、时效性、来源权威性综合打分排序，不能原样甩给用户

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

分流之后，再细分意图（intent）来调整结果的排序逻辑：

- `news` → 时效性权重最高
- `factual` → 来源权威性权重最高
- `comparison` → 关键词覆盖权重最高
- 以此类推...

### 3. 多 Key 轮询池，高可用

Exa 支持配置多个官方 Key 组成池子：

- 当前 Key 限流（429）→ 自动切下一个
- 当前 Key 失效（401）→ 跳过继续
- 官方池全挂 → 还有 BigSong 代理兜底

### 4. 结果打分 + 去重

多源结果汇总后会经过：
- 关键词相关度打分
- 发布时间新鲜度打分
- 来源权威性打分
- URL 去重（忽略 utm_ 等追踪参数）
- 综合排序后输出

---

## 功能说明

### 支持的搜索来源

| 来源 | 特点 | 配置项 |
|------|------|--------|
| Grok | xAI 模型，实时感知强，适合新闻/舆情 | `grok.apiKey` + `grok.apiUrl` |
| Exa | 语义搜索，适合官方文档/技术内容 | `exa` 或 `exaKeys[]` |
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

## 快速上手

### 第一步：获取 API Key

**Grok（必须，Fresh 模式的核心）**

1. 前往 <https://console.x.ai/>
2. 注册 / 登录 xAI 账号
3. 创建 API Key
4. 目前有一定免费额度，超出后按量计费

**Exa（推荐，Evidence 模式更好用）**

1. 前往 <https://exa.ai/>
2. 注册账号
3. 在 Dashboard → API Keys 里创建 Key
4. 免费版每月有一定次数，够用于日常搜索

**Tavily（可选）**

1. 前往 <https://tavily.com/>
2. 注册账号，进入 Dashboard 创建 Key
3. 有免费 tier

---

### 第二步：配置 credentials

在 `~/.openclaw/credentials/search.json` 里写入你的 Key：

**最简配置（仅 Grok）：**
```json
{
  "grok": {
    "apiUrl": "https://api.x.ai/v1",
    "apiKey": "xai-你的Key",
    "model": "grok-3-fast"
  }
}
```

**推荐配置（Grok + Exa）：**
```json
{
  "grok": {
    "apiUrl": "https://api.x.ai/v1",
    "apiKey": "xai-你的Key",
    "model": "grok-3-fast"
  },
  "exa": "你的Exa单个Key"
}
```

**进阶配置（Exa 多 Key 轮询池）：**
```json
{
  "grok": {
    "apiUrl": "https://api.x.ai/v1",
    "apiKey": "xai-你的Key",
    "model": "grok-3-fast"
  },
  "exaKeys": [
    "第一个Exa Key",
    "第二个Exa Key",
    "第三个Exa Key"
  ]
}
```

> 如果你同时配了 `exa`（单个）和 `exaKeys`（池子），skill 会先用单个 key，失败后再轮询池子。

---

### 第三步：安装依赖

```bash
cd skills/search-layer
python3 -m venv .venv
source .venv/bin/activate
pip install requests
```

---

### 第四步：测一下

```bash
source .venv/bin/activate
python scripts/search.py "今天 AI 有什么大新闻" --mode fast --num 5
```

成功的话你会看到一个 JSON 输出，里面有 `results` 列表。

---

## 目录结构

```
search-layer/
├── SKILL.md                    # 给 OpenClaw 龙虾看的调度指南
├── README.md                   # 本文件
├── scripts/
│   ├── search.py               # 主搜索脚本（Exa + Grok + Tavily）
│   ├── fetch_thread.py         # GitHub / 论坛讨论链追踪
│   ├── exa_free_client.py      # Exa 代理客户端
│   ├── chain_tracker.py        # 引用链深挖
│   └── relevance_gate.py       # 结果相关性过滤
└── references/
    ├── authority-domains.json  # 权威域名列表（影响打分）
    ├── intent-guide.md         # 意图选择参考
    └── exa-free-proxy.md       # Exa 代理端点说明
```

---

## 常见问题

**Q: Grok 搜索没结果怎么办？**
A: 检查 `grok.apiKey` 是否正确，以及 `grok.apiUrl` 是否是 OpenAI-compatible endpoint（`/v1` 结尾）。

**Q: Exa Key 报 401？**
A: Key 已失效，从 `exaKeys` 列表里删掉这个，换一个新的。

**Q: 搜出来的结果都是英文，怎么搜中文？**
A: 直接用中文 query 就行，Exa 和 Grok 都支持多语言。

**Q: 出现 SSLEOFError？**
A: 网络瞬时抖动，不是 Key 问题，重试一次通常就好了。

**Q: 我想同时用 Exa 的免费代理怎么配？**
A: 在 credentials 里把 `exa` 配成对象形式：
```json
{
  "exa": {
    "apiKey": "你的Key",
    "apiUrl": "https://exa.chengtx.vip/search"
  }
}
```

---

## License

MIT
