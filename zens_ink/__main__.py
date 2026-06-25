#!/usr/bin/env python3
"""Entry point: show available tools."""

import sys

TOOLS = [
    ("keyword_research", "Discover keywords via Google Autocomplete"),
    ("keyword_volume",   "Check real search volume via Bing API"),
    ("search_performance", "Your site's Google search data (GSC)"),
    ("competitor_gap",   "Analyze competitor content via sitemaps"),
    ("setup_gsc",        "One-time OAuth setup for Search Console"),
]

def main():
    print(f"\nzens.ink CLI v0.1.0 — Free SEO keyword research toolkit\n")
    print("Usage: python3 -m zens_ink.<tool> [options]\n")
    print("Tools:")
    for name, desc in TOOLS:
        print(f"  {name:25s}  {desc}")
    print(f"\nDocs: https://github.com/uzenlabs/zens-ink\n")

if __name__ == "__main__":
    main()
