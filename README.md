<div align="center">

# zens.ink

### 免费 SEO 关键词研究工具包 / Free SEO Keyword Research Toolkit

面向独立开发者的命令行工具。零依赖，纯 Python。 / CLI tools for indie builders. Zero dependencies, pure Python.

[English](#english) · [中文](#中文)

</div>

---

## English

Four CLI tools that cover the full keyword research workflow. No paid APIs. No Ahrefs. No subscriptions.

| Tool | What it does | API needed |
|------|-------------|-----------|
| `keyword_research` | Discover what people search via Google Autocomplete | None |
| `keyword_volume` | Real search demand via Bing Webmaster API | Free Bing key |
| `search_performance` | Your site's real Google ranking data | Free GSC OAuth |
| `competitor_gap` | Analyze competitor content via sitemaps | None |

### Why

Ahrefs costs $200/month. SEMrush costs $130/month. For indie builders who just need keyword research, that's overkill.

zens.ink wires together free public data sources — Google Autocomplete, Bing Webmaster Tools, Google Search Console — with zero Python dependencies.

### Quick Start

```bash
git clone https://github.com/respectevery01/zens-ink-seo-package.git
cd zens-ink-seo-package

# Discover keywords
python3 -m zens_ink.keyword_research "tarot" --expand

# Check search volume
python3 -m zens_ink.keyword_volume "tarot reading" --country us

# Analyze a competitor
python3 -m zens_ink.competitor_gap --url https://example.com/sitemap.xml

# Check your own search performance
python3 -m zens_ink.search_performance
```

### Requirements

- Python 3.10+
- No pip install required — uses standard library only

### Documentation

Full case study and Pro package at [zens.ink](https://zens.ink).

---

## 中文

四个命令行工具，覆盖完整的关键词研究流程。不需要付费 API，不需要 Ahrefs，不需要订阅。

| 工具 | 功能 | 需要密钥 |
|------|------|---------|
| `keyword_research` | 通过 Google 自动补全发现用户搜索什么 | 无 |
| `keyword_volume` | 通过 Bing 站长 API 获取真实搜索量 | 免费 Bing key |
| `search_performance` | 你在 Google 上的真实排名数据 | 免费 GSC OAuth |
| `competitor_gap` | 通过 sitemap 分析竞品内容 | 无 |

### 为什么做这个

Ahrefs 每月 $200，SEMrush 每月 $130。对独立开发者来说，只是做关键词研究，太贵了。

zens.ink 把免费公开数据源 —— Google 自动补全、Bing 站长工具、Google Search Console —— 串在一起，零 Python 依赖。

### 快速开始

```bash
git clone https://github.com/respectevery01/zens-ink-seo-package.git
cd zens-ink-seo-package

# 发现关键词
python3 -m zens_ink.keyword_research "塔罗牌" --lang zh --expand

# 查搜索量
python3 -m zens_ink.keyword_volume "塔罗牌" --country cn --lang zh-CN

# 分析竞品
python3 -m zens_ink.competitor_gap --url https://example.com/sitemap.xml

# 查看自己站点的搜索表现
python3 -m zens_ink.search_performance
```

### 环境要求

- Python 3.10+
- 无需 pip install — 纯标准库实现

### 文档

完整案例和 Pro 增值包见 [zens.ink](https://zens.ink)

---

<div align="center">

**License**: MIT — 个人和商业项目均可自由使用

Made by [UZEN Labs](https://uzenlabs.com)

</div>
