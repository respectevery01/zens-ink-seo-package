<div align="center">

# zens.ink

### SEO Toolkit for Indie Builders

CLI tools for keyword research, competitor analysis, and technical audits. Zero dependencies, pure Python.

[English](README.md) · [中文](README.zh.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-7c3aed?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-0-059669?style=flat-square)](https://github.com/respectevery01/zens-ink-seo-package)
[![GitHub stars](https://img.shields.io/github/stars/respectevery01/zens-ink-seo-package?style=flat-square&color=7c3aed)](https://github.com/respectevery01/zens-ink-seo-package)
[![GitHub last commit](https://img.shields.io/github/last-commit/respectevery01/zens-ink-seo-package?style=flat-square&color=a8a29e)](https://github.com/respectevery01/zens-ink-seo-package)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-7c3aed?style=flat-square)](https://github.com/respectevery01/zens-ink-seo-package/pulls)

</div>

---

Eight CLI tools that cover the full SEO workflow — from discovering what people search, to analyzing competitors, to auditing your own site. No paid APIs. No Ahrefs. No subscriptions. Just free data sources wired together with Python.

| Tool | What it does | API needed |
|------|-------------|-----------|
| `keyword_research` | Discover long-tail keywords via Google Autocomplete | None |
| `keyword_volume` | Real search volume via Bing Webmaster API | Free Bing key |
| `kd` | Keyword difficulty score via SERP structure analysis | Free Serper key |
| `brave_volume` | Cross-check search demand via Brave SERP signals | Free Brave key |
| `search_performance` | Your site's real Google ranking data (GSC) | Free GSC OAuth |
| `competitor_gap` | Compare multiple competitor sitemaps, find content gaps | None |
| `site_audit` | Technical SEO audit: broken links, orphan pages, missing canonical/meta/H1 | None |
| `setup_gsc` | One-time OAuth setup for Google Search Console | — |

## Why

Ahrefs costs $200/month. SEMrush costs $130/month. For indie builders who just need to find keywords worth writing about, that's overkill.

zens.ink wires together free public data sources — Google Autocomplete, Bing Webmaster Tools, Google Search Console, Brave Search — with zero Python dependencies.

## Quick Start

```bash
git clone https://github.com/respectevery01/zens-ink-seo-package.git
cd zens-ink-seo-package

# Discover keywords (with a-z long-tail expansion)
python3 -m zens_ink.keyword_research "tarot" --expand

# Check real search volume
python3 -m zens_ink.keyword_volume "tarot reading" --country us

# Keyword difficulty (SERP-based, with Chinese mode)
python3 -m zens_ink.kd "塔罗牌" --zh

# Compare 3 competitors at once
python3 -m zens_ink.competitor_gap \
  --url https://yoursite.com/sitemap.xml \
  --compare https://competitor-a.com/sitemap.xml https://competitor-b.com/sitemap.xml

# Audit your build for SEO issues
python3 -m zens_ink.site_audit --dist dist --sitemap dist/sitemap.xml

# Check your own Google search performance
python3 -m zens_ink.search_performance
```

## Typical Workflow

```
keyword_research  →  find what people actually search
        ↓
keyword_volume    →  filter by real demand
        ↓
kd                →  pick keywords you can actually rank for
        ↓
competitor_gap    →  see what competitors already cover
        ↓
site_audit        →  make sure your pages are crawlable
```

## Requirements

- Python 3.10+
- No pip install required — uses standard library only
- API keys (Bing, Serper, Brave, GSC) are stored in `.env` — see `.env.example`

## Documentation

- **Full docs & case studies**: [zens.ink/docs](https://zens.ink/docs)
- **Pro package** (automated full-audit pipeline, HTML reports, GEO score): [zens.ink](https://zens.ink)

## License

MIT — free for personal and commercial use.

---

<div align="center">

Made by [Jask](https://github.com/respectevery01)

</div>
