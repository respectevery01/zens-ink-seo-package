#!/usr/bin/env python3
"""
Merge volume data from multiple sources into KD cache.

Priority: Bing (absolute) > Brave (estimated) > 0

Usage:
  python3 scripts/merge_volume.py --brave brave-volume.json
  python3 scripts/merge_volume.py --brave brave-volume.json --bing bing-volume.json
"""

import json
import csv
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(SCRIPT_DIR, "kd-cache.json")


def load_cache():
    with open(CACHE_PATH) as f:
        return json.load(f)


def save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def main():
    import argparse
    p = argparse.ArgumentParser(description="Merge volume data into KD cache")
    p.add_argument("--brave", help="Brave volume JSON file (list of dicts)")
    p.add_argument("--bing", help="Bing volume CSV file")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    cache = load_cache()
    updated = 0

    # Merge Bing (highest priority — absolute numbers)
    if args.bing:
        with open(args.bing, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                kw = row.get("keyword", "").strip()
                if not kw:
                    continue
                vol = 0
                try:
                    vol = int(float(row.get("avg_weekly", 0) or 0)) * 4  # weekly → monthly
                except ValueError:
                    pass
                if vol > 0 and kw in cache:
                    old_vol = cache[kw].get("search_volume", 0) or 0
                    if old_vol == 0:  # only fill gaps, don't overwrite existing Bing data
                        cache[kw]["search_volume"] = vol
                        cache[kw]["volume_source"] = "bing"
                        updated += 1

    # Merge Brave (fills gaps where Bing returns 0)
    if args.brave:
        with open(args.brave) as f:
            brave_data = json.load(f)
        for item in brave_data:
            kw = item.get("keyword", "").strip()
            if not kw or kw not in cache:
                continue
            est_vol = item.get("estimated_monthly_volume", 0) or 0
            old_vol = cache[kw].get("search_volume", 0) or 0
            if old_vol == 0 and est_vol > 0:
                cache[kw]["search_volume"] = est_vol
                cache[kw]["volume_source"] = "brave_estimate"
                cache[kw]["demand_score"] = item.get("demand_score", 0)
                updated += 1

    if not args.dry_run:
        save_cache(cache)

    print(f"Updated {updated} keywords with volume data")
    print(f"Total in cache: {len(cache)}")
    has_vol = sum(1 for v in cache.values() if (v.get("search_volume") or 0) > 0)
    print(f"With volume: {has_vol}/{len(cache)}")


if __name__ == "__main__":
    main()
