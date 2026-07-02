#!/usr/bin/env python3
"""
ZensInk SEO Toolkit — CLI dispatcher for agent skill usage.

Usage:
  python3 scripts/seo.py <tool> [args...]

Tools:
  keyword_research   Discover keywords via Google Autocomplete (no API key needed)
  keyword_volume     Check real search volume via Bing Webmaster API
  kd                 Keyword Difficulty score via SERP structure analysis
  brave_volume       Estimate search demand via Brave Search API
  search_performance Your site's Google search data (GSC)
  competitor_gap     Analyze competitor content via sitemaps
  site_audit         Technical SEO audit of built HTML
  setup_gsc          One-time OAuth setup for Google Search Console

Examples:
  python3 scripts/seo.py keyword_research "tarot meaning" --lang en
  python3 scripts/seo.py keyword_research "tarot meaning" --expand --json
  python3 scripts/seo.py kd "tarot reading"
  python3 scripts/seo.py site_audit --dist dist --sitemap dist/sitemap.xml
  python3 scripts/seo.py competitor_gap --url https://example.com --compare https://competitor.com
  python3 scripts/seo.py keyword_volume "tarot" --lang en
"""

import os
import sys

# Ensure the scripts directory AND project root are on the path
# so the zens_ink package resolves regardless of layout
_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)
sys.path.insert(0, _PARENT)

TOOLS = {
    "keyword_research": "zens_ink.keyword_research",
    "keyword_volume": "zens_ink.keyword_volume",
    "kd": "zens_ink.kd",
    "brave_volume": "zens_ink.brave_volume",
    "search_performance": "zens_ink.search_performance",
    "competitor_gap": "zens_ink.competitor_gap",
    "site_audit": "zens_ink.site_audit",
    "setup_gsc": "zens_ink.setup_gsc",
}


def show_help():
    print("\nzens.ink SEO Toolkit — Free SEO tools for indie builders\n")
    print("Usage: python3 scripts/seo.py <tool> [options...]\n")
    print("Tools:")
    for name, mod in TOOLS.items():
        doc = ""
        try:
            m = __import__(mod, fromlist=["__doc__"])
            doc = (m.__doc__ or "").strip().split("\n")[0][:60]
        except Exception:
            pass
        print(f"  {name:25s}  {doc}")
    print("\nFor per-tool options: python3 scripts/seo.py <tool> --help")
    print("GitHub: https://github.com/respectevery01/zens-ink-seo-package\n")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        show_help()
        return

    tool = sys.argv[1]
    if tool not in TOOLS:
        print(f"Unknown tool: {tool}\n")
        show_help()
        sys.exit(1)

    # Hand off remaining args to the tool's own main()
    sys.argv = [tool] + sys.argv[2:]
    mod = __import__(TOOLS[tool], fromlist=["main"])
    mod.main()


if __name__ == "__main__":
    main()
