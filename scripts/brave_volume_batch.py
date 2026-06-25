#!/usr/bin/env python3
"""
Batch Brave volume — runs Brave demand estimation on all keywords
that have no volume data in the KD cache.

Usage:
  python3 scripts/brave_volume_batch.py              # all missing volume
  python3 scripts/brave_volume_batch.py --category en_bazi
  python3 scripts/brave_volume_batch.py --output brave-volume.json
"""

import json
import csv
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from zens_ink.brave_volume import search_brave, estimate_demand

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(SCRIPT_DIR, "kd-cache.json")
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), "pro-package", "keywords-master.csv")


def load_keywords_missing_volume():
    """Load keywords that have KD data but no volume."""
    with open(CACHE_PATH) as f:
        cache = json.load(f)
    
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        csv_kws = {row["keyword"]: row for row in reader}
    
    missing = []
    for kw, data in cache.items():
        vol = data.get("search_volume", 0) or 0
        if vol == 0:
            cat = csv_kws.get(kw, {}).get("category", data.get("category", ""))
            lang = csv_kws.get(kw, {}).get("lang", data.get("lang", "en"))
            missing.append({"keyword": kw, "category": cat, "lang": lang})
    
    return missing


def main():
    import argparse
    p = argparse.ArgumentParser(description="Batch Brave volume estimation")
    p.add_argument("--category", help="Filter by category prefix")
    p.add_argument("--limit", type=int, help="Max keywords")
    p.add_argument("--output", "-o", default=os.path.join(SCRIPT_DIR, "brave-volume.json"))
    p.add_argument("--delay", type=float, default=0.5)
    args = p.parse_args()

    keywords = load_keywords_missing_volume()
    
    if args.category:
        keywords = [k for k in keywords if k["category"].startswith(args.category)]
    if args.limit:
        keywords = keywords[:args.limit]

    if not keywords:
        print("No keywords missing volume data!")
        return

    print(f"\n  Brave Volume Batch | {len(keywords)} keywords\n")

    results = []
    for i, kw_data in enumerate(keywords):
        kw = kw_data["keyword"]
        lang = kw_data.get("lang", "en")
        is_zh = lang == "zh"
        
        brave_data = search_brave(kw, count=20, 
                                   country="CN" if is_zh else "US",
                                   search_lang="zh" if is_zh else "en")
        result = estimate_demand(kw, brave_data)
        results.append(result)

        score = result.get("demand_score", 0)
        vol = result.get("estimated_monthly_volume", 0)
        print(f"  [{i+1}/{len(keywords)}] {kw[:45]:<45}  demand={score:>5}  est_vol={vol:>6}")

        # Save every 20 keywords
        if (i + 1) % 20 == 0:
            with open(args.output, "w") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

        if i < len(keywords) - 1:
            time.sleep(args.delay)

    with open(args.output, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n  Output: {args.output}")
    has_vol = [r for r in results if r.get("estimated_monthly_volume", 0) > 0]
    print(f"  With volume: {len(has_vol)}/{len(results)}")


if __name__ == "__main__":
    main()
