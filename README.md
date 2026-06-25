# zens-ink

> Free SEO keyword research toolkit for indie builders. No paid APIs, no subscriptions.

Four CLI tools that cover the full keyword research workflow:

| Tool | What it does | API needed |
|------|-------------|-----------|
| `keyword_research` | Discover what people search via Google Autocomplete | None |
| `keyword_volume` | Real search demand via Bing Webmaster API | Free Bing key |
| `search_performance` | Your site's real Google ranking data | Free GSC OAuth |
| `competitor_gap` | Analyze competitor content via sitemaps | None |

## Why

Ahrefs costs $200/month. SEMrush costs $130/month. For indie builders and solo
founders who just need keyword research, that's overkill.

zens.ink wires together free public data sources — Google Autocomplete, Bing
Webmaster Tools, Google Search Console — with zero Python dependencies.

## Quick Start

```bash
git clone https://github.com/respectevery01/zens-ink.git
cd zens-ink

# Discover keywords
python3 keyword_research.py "tarot" --expand

# Check search volume
python3 keyword_volume.py "tarot reading" --country us

# Analyze a competitor
python3 competitor_gap.py --url https://example.com/sitemap.xml

# Check your own search performance
python3 search_performance.py
```

## Requirements

- Python 3.10+
- No pip install required — uses standard library only

## Documentation

Full case study and documentation at [zens.ink](https://zens.ink).

## License

MIT — free for personal and commercial use.

---

Made by [UZEN Labs](https://uzenlabs.com)
