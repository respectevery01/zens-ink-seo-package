<div align="center">

# zens.ink

### Free SEO Keyword Research Toolkit

CLI tools for indie builders. Zero dependencies, pure Python.

[English](README.md) · [中文](README.zh.md)

</div>

---

Four CLI tools that cover the full keyword research workflow. No paid APIs. No Ahrefs. No subscriptions. Just free data sources wired together with Python.

| Tool | What it does | API needed |
|------|-------------|-----------|
| `keyword_research` | Discover what people search via Google Autocomplete | None |
| `keyword_volume` | Real search demand via Bing Webmaster API | Free Bing key |
| `search_performance` | Your site's real Google ranking data | Free GSC OAuth |
| `competitor_gap` | Analyze competitor content via sitemaps | None |

## Why

Ahrefs costs $200/month. SEMrush costs $130/month. For indie builders who just need keyword research, that's overkill.

zens.ink wires together free public data sources — Google Autocomplete, Bing Webmaster Tools, Google Search Console — with zero Python dependencies.

## Quick Start

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

## Requirements

- Python 3.10+
- No pip install required — uses standard library only

## Documentation

Full case study and Pro package at [zens.ink](https://zens.ink).

## License

MIT — free for personal and commercial use.

---

<div align="center">

Made by [UZEN Labs](https://uzenlabs.com)

</div>
