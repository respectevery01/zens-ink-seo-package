# 路线图

> 从「我该做 SEO」到「我做了」的最短路径。免费工具发现问题，Pro 引擎交付结果。

## 设计原则

- **开源给工具，Pro 给结果。** Pro 的每个增量必须把多个工具编排成一个 outcome，而不是多加一个数据点。
- **做 Ahrefs 做不到的事。** 更便宜、聚焦 indie、Agent 原生。
- **每个大版本只加一个杀手级增量。** 不堆功能。

---

## Phase 0 — 发布（现在）

**开源（v0.2）**
- 6 个工具：`keyword_research`、`keyword_volume`、`kd`、`brave_volume`、`competitor_gap`、`search_performance`
- 纯 Python stdlib，零依赖
- clone 即用，无安装摩擦

**Pro（v7）**
- Winability Score、Content Radar、Competitor Radar
- 每买家水印、Agent Skills 兼容

**目标**：公开发布，收集早期用户反馈。

---

## Phase 1 — 基础（0–2 个月）

### 开源

- [ ] `pyproject.toml` → `pip install zens-ink`
- [ ] README 加 GIF demo（每个工具 3 秒动图）
- [ ] `zens_ink audit` —— 一键技术 SEO 审计（canonical、孤儿页、sitemap、H1 检测）
- [ ] 修复社区反馈的 bug 和 edge case

### Pro v8 —— Content Briefs

当前最大断档：用户知道「该写什么词」但不知道「该怎么写」。

- 关键词 → 结构化内容大纲（推荐 H2 结构、应覆盖实体、PAA 问题、目标字数）
- Content Radar + Briefs 联动：日历中每个关键词一键生成 brief
- **交付**：「我知道写什么、怎么组织。」

---

## Phase 2 —— GEO（2–4 个月）

### 开源

- [ ] `serp_features` —— 检测 SERP 特性占位（featured snippet、PAA、AI Overview 是否存在）
- [ ] `internal_links` —— 站内链接结构分析，找孤儿页和链接机会
- [ ] pip 下载量增长

### Pro v9 —— GEO Score + Backlink Radar

- **GEO Score**：你的内容被 AI 搜索引用的可能性有多大？（BLUF 前置、结构化数据、事实密度、llms.txt 是否存在）。基于 Echoir 自身 GEO 实验验证的指标体系。
- **Backlink Radar**：用免费数据源（Common Crawl、公开链接索引）发现竞品反向链接来源。
- **交付**：「我知道 AI 是否会引用我、竞品的权威性来自哪里。」

---

## Phase 3 —— 自动化（4–8 个月）

### 开源

- [ ] 插件架构（`zens_ink.plugins`）—— 社区贡献自定义分析器
- [ ] `zens_ink monitor` —— 持续 SERP 追踪 + 变动通知

### Pro v10 —— Agent Workflow

- 端到端管线：关键词发现 → Winability 过滤 → Content Brief → 草稿生成 → 内链建议 → 发布
- 定制周报（GSC 数据 + SERP 变化 + 新机会词，自动邮件）
- 多站点支持（一个 license 管理 N 个项目）
- **交付**：「我审阅和批准，引擎做其余一切。」

---

## Phase 4 —— 生态（8–12 个月）

- [ ] 开放 API / 轻量托管 dashboard（无需装 Python）
- [ ] 社区 workflow 市场（类似 Agent Skills 注册表）
- [ ] CMS 集成（Astro / Next.js / Hugo 自动注入内容建议）
- [ ] Pro 定价随价值增长（$39 → $59 → $79）；early bird 用户永久锁定原价

---

## 发布节奏

| 类型 | 频率 | 内容 |
|------|------|------|
| Pro 大版本 | ~2 个月 | 一个杀手级增量 |
| Pro 小版本 | 按需 | bug 修复、打磨 |
| 开源版本 | 持续 | 新工具、社区 PR |

## 竞争壁垒

每个增量用两个问题检验：

1. **Ahrefs 能做吗？**（能就不做。）
2. **免费或近免费吗？**（月费 $500 的不依赖。）

等竞品适配 Agent-native 工作流时，我们已经积累了一年的工作流数据和社区信任。
