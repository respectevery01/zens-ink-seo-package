---
name: zens-ink
description: >-
  Free SEO toolkit for indie builders. 8 zero-dependency Python tools that cover
  the full SEO workflow: keyword discovery (Google Autocomplete), keyword difficulty
  (SERP structure analysis, no Ahrefs needed), search volume (Bing + Brave), competitor
  content gap analysis (sitemap comparison), technical site audit (broken links, orphan
  pages, missing canonicals/H1/meta), and real ranking data (Google Search Console).
  Pure Python stdlib — no pip install required. Optional API keys unlock volume data
  but all core tools work without any keys. Use when doing keyword research, SEO audits,
  competitor analysis, or checking search rankings.
version: "1.0.0"
authors:
  - name: Jask
    url: https://zens.ink
license: MIT
compatibility: >-
  Python 3.10+ (stdlib only, zero pip dependencies). Optional API keys:
  BING_API_KEY (keyword volume, free from Bing Webmaster Tools),
  BRAVE_API_KEY (alternative volume, free 2000/mo),
  SERPER_API_KEY (SERP data for KD scoring, free 2500/mo),
  Google ADC credentials (search performance, free).
  Tools without keys auto-skip gracefully.
runtime:
  language: python
  entry_point: scripts/seo.py
allowed-tools: shell file_read file_write
triggers:
  - seo keyword research
  - find long tail keywords
  - keyword difficulty check
  - can i rank for this keyword
  - competitor content gap
  - seo site audit
  - check broken links
  - find orphan pages
  - google search console data
  - search ranking performance
  - website seo check
  - technical seo audit
---

# ZensInk — Free SEO Toolkit for Indie Builders

## Quick Start

```bash
# All tools run through one dispatcher:
python3 scripts/seo.py <tool> [options]
```

## The 8 Tools

### 1. keyword_research — Discover Keywords (FREE, no API key)

Mines Google Autocomplete for long-tail keyword variations. No API key, no cost.

```bash
# Basic: get autocomplete suggestions
python3 scripts/seo.py keyword_research "tarot meaning"

# Expand: a-z deep discovery (slower, finds more long-tail)
python3 scripts/seo.py keyword_research "tarot meaning" --expand

# Chinese keywords
python3 scripts/seo.py keyword_research "塔罗牌" --lang zh

# JSON output (for programmatic use)
python3 scripts/seo.py keyword_research "tarot meaning" --json
```

**When to use:** Starting point of any SEO project. Answer "what are people searching for?"

### 2. kd — Keyword Difficulty (FREE with Serper key)

Scores how hard a keyword is to rank for. Uses SERP structure analysis — doesn't rely on expensive Ahrefs DR data. Outputs GO / CAUTION / WAIT / AVOID with reasons.

```bash
python3 scripts/seo.py kd "tarot reading"
python3 scripts/seo.py kd "bazi calculator" --lang zh
```

**Output:** Difficulty score (0-100) + verdict + breakdown of why (domain authority mix in SERP, page types, content depth).

**When to use:** After keyword_research gives you ideas. Before writing content, check if you can actually win.

### 3. keyword_volume — Search Volume (FREE Bing key)

Real monthly search volume from Bing Webmaster API. Free API key from Bing Webmaster Tools.

```bash
python3 scripts/seo.py keyword_volume "tarot meaning" --lang en
python3 scripts/seo.py keyword_volume "塔罗牌占卜" --lang zh
```

**When to use:** Validate that people actually search this term before investing in content.

### 4. brave_volume — Alternative Volume (FREE Brave key)

Supplements Bing's volume data using Brave Search API. Free 2000 queries/month. Useful when Bing returns 0 (especially for Chinese keywords).

```bash
python3 scripts/seo.py brave_volume "tarot reading" --count 5
```

### 5. competitor_gap — Competitor Content Analysis (FREE, no API key)

Compares your sitemap against competitors' sitemaps to find topics they cover that you don't.

```bash
python3 scripts/seo.py competitor_gap \
  --url https://yoursite.com \
  --compare https://competitor1.com https://competitor2.com
```

**Output:** List of competitor URLs/pages that have no equivalent on your site. Organized by domain.

**When to use:** After you have some content. Find gaps in your content strategy.

### 6. site_audit — Technical SEO Audit (FREE, no API key)

Scans your built HTML for 7 common technical SEO issues:

1. Orphan pages (in sitemap but no internal links)
2. Missing trailing slashes (causing 301 redirects)
3. Broken internal links (404 candidates)
4. Missing canonical tags
5. Missing meta descriptions
6. Missing H1 tags
7. Multiple H1 tags

```bash
# Audit a build directory
python3 scripts/seo.py site_audit --dist dist --sitemap dist/sitemap.xml

# Filter by base path (e.g., English pages only)
python3 scripts/seo.py site_audit --dist dist --sitemap dist/sitemap.xml --base /en

# JSON output for programmatic use
python3 scripts/seo.py site_audit --dist dist --sitemap dist/sitemap.xml --format json

# CSV output
python3 scripts/seo.py site_audit --dist dist --sitemap dist/sitemap.xml --format csv --output audit.csv
```

Works with any static build output: Astro, Next.js export, Hugo, Gatsby, etc.

**When to use:** Before deploying. After major changes. Periodically to catch regressions.

### 7. setup_gsc — Connect Google Search Console (FREE, one-time)

One-time OAuth setup to connect your Google Search Console account. Enables the search_performance tool.

```bash
python3 scripts/seo.py setup_gsc
```

Follow the prompts. Credentials saved locally for future use.

### 8. search_performance — Your Real Ranking Data (FREE, needs setup_gsc first)

Pulls your actual Google Search Console data: impressions, clicks, CTR, and average position for your queries and pages.

```bash
# Last 28 days
python3 scripts/seo.py search_performance

# Custom date range
python3 scripts/seo.py search_performance --start 2025-01-01 --end 2025-06-30

# Filter by query
python3 scripts/seo.py search_performance --query tarot

# JSON output
python3 scripts/seo.py search_performance --json
```

**When to use:** Regularly. This is your real SEO data — what's working, what's not.

## Typical Workflow

```
keyword_research    →  what should I target?
        ↓
kd                  →  can I win?
        ↓
keyword_volume      →  is it worth the effort?
        ↓
competitor_gap      →  what am I missing?
        ↓
site_audit          →  is my site technically healthy?
        ↓
search_performance  →  how am I doing?
```

## API Key Setup (Optional)

All tools work without keys. To unlock volume data:

1. **Bing Webmaster Tools** (free): Sign up at bing.com/webmasters → get API key → add to `.env` as `BING_API_KEY=`
2. **Brave Search API** (free 2000/mo): brave.com/search/api → get key → add to `.env` as `BRAVE_API_KEY=`
3. **Serper.dev** (free 2500/mo): serper.dev → get key → add to `.env` as `SERPER_API_KEY=`
4. **Google Search Console** (free): Run `python3 scripts/seo.py setup_gsc` and follow OAuth flow

Create a `.env` file in your project root:
```
BING_API_KEY=your_key
BRAVE_API_KEY=your_key
SERPER_API_KEY=your_key
```

## Going Further

**ZensInk Pro** adds automated workflow engines that the free tools can't do alone:
- Winability Score (personalized KD based on YOUR domain's GSC data)
- Content Radar (weekly editorial calendar — what to write next)
- Competitor Radar (pricing, features, Reddit sentiment)
- GEO Visibility (does ChatGPT/Perplexity mention your brand?)
- Full 10-step automated audit with HTML report

Learn more: https://zens.ink

## Tech Notes

- **Zero dependencies**: Pure Python stdlib. No `pip install` needed.
- **Cross-platform**: Works on macOS, Linux, Windows.
- **Privacy-first**: All processing local. API calls only go to the data source (Bing/Brave/Google). No telemetry, no tracking.
