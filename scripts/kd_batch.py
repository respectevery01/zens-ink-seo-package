#!/usr/bin/env python3
"""
Batch KD analysis — runs KD on all keywords from keywords-master.csv.
Features:
  - JSON cache (resume-safe, no wasted API calls)
  - Categorizes results: 避雷 (traps) / 蓝海 (blue ocean) / 中等
  - Outputs summary report + CSV with all scores
"""

import json
import csv
import sys
import os
import time

# Add zens_ink to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from zens_ink.kd import fetch_serp, calculate_kd, fetch_search_volume

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # workspace root
CSV_PATH = os.path.join(WORKSPACE, "pro-package", "keywords-master.csv")
CACHE_PATH = os.path.join(SCRIPT_DIR, "kd-cache.json")
OUTPUT_CSV = os.path.join(SCRIPT_DIR, "kd-results.csv")
OUTPUT_REPORT = os.path.join(SCRIPT_DIR, "kd-report.json")


def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def load_keywords():
    """Load keywords from CSV, skip duplicates."""
    keywords = []
    seen = set()
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kw = row["keyword"].strip()
            cat = row.get("category", "")
            lang = row.get("lang", "en")
            if kw and kw not in seen:
                seen.add(kw)
                keywords.append({"keyword": kw, "category": cat, "lang": lang})
    return keywords


def run_batch(keywords, cache, limit=None, delay=1.5):
    """Run KD on keywords, using cache for resume."""
    total = len(keywords) if limit is None else min(limit, len(keywords))
    done = 0
    skipped = 0
    errors = []

    for i, kw_data in enumerate(keywords):
        if limit and i >= limit:
            break

        kw = kw_data["keyword"]
        lang = kw_data["lang"]
        is_zh = lang == "zh"

        if kw in cache:
            skipped += 1
            continue

        gl = "cn" if is_zh else "us"
        hl = "zh-CN" if is_zh else "en"
        market = "zh-CN" if is_zh else "en-US"

        try:
            serp = fetch_serp(kw, gl=gl, hl=hl)
            volume = fetch_search_volume(kw, market=market)
            result = calculate_kd(serp, kw, volume)

            # Trim result for storage (drop verbose fields)
            cache[kw] = {
                "keyword": kw,
                "category": kw_data["category"],
                "lang": lang,
                "kd": result.get("kd"),
                "label": result.get("label"),
                "label_en": result.get("label_en"),
                "recommendation": result.get("recommendation"),
                "is_brand": result.get("is_brand_keyword", False),
                "search_volume": result.get("search_volume"),
                "base_score": result.get("base_score"),
                "modifier_total": result.get("modifier_total"),
                "serp_analysis": result.get("serp_analysis"),
                "modifiers": result.get("modifiers"),
            }
            done += 1

            label = result.get("label_en", "?")
            kd_val = result.get("kd", 0)
            brand = " ⚠BRAND" if result.get("is_brand_keyword") else ""
            print(f"  [{done + skipped}/{total}] KD={kd_val:>5} [{label}] {kw}{brand}")

            # Save cache every 10 keywords
            if done % 10 == 0:
                save_cache(cache)

        except Exception as e:
            errors.append({"keyword": kw, "error": str(e)})
            print(f"  [ERROR] {kw}: {e}")

        time.sleep(delay)

    save_cache(cache)
    return done, skipped, errors


def generate_report(cache):
    """Generate categorized report from cached results."""
    results = [v for v in cache.values() if v.get("kd") is not None]
    results.sort(key=lambda x: x["kd"])

    # Categorize
    traps = [r for r in results if r["kd"] >= 55 or r.get("is_brand")]
    medium = [r for r in results if 40 <= r["kd"] < 55 and not r.get("is_brand")]
    easy = [r for r in results if 25 <= r["kd"] < 40 and not r.get("is_brand")]
    blue_ocean = [r for r in results if r["kd"] < 25 and not r.get("is_brand")]

    # Category breakdown
    cat_stats = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in cat_stats:
            cat_stats[cat] = {"count": 0, "kd_sum": 0, "kd_min": 999, "kd_max": 0}
        cs = cat_stats[cat]
        cs["count"] += 1
        cs["kd_sum"] += r["kd"]
        cs["kd_min"] = min(cs["kd_min"], r["kd"])
        cs["kd_max"] = max(cs["kd_max"], r["kd"])

    for cat, cs in cat_stats.items():
        cs["kd_avg"] = round(cs["kd_sum"] / cs["count"], 1) if cs["count"] else 0

    report = {
        "total_analyzed": len(results),
        "summary": {
            "traps": len(traps),
            "medium": len(medium),
            "easy": len(easy),
            "blue_ocean": len(blue_ocean),
        },
        "category_stats": cat_stats,
        "blue_ocean": blue_ocean[:30],
        "easy": easy[:20],
        "medium": medium[:20],
        "traps": traps[:20],
    }

    with open(OUTPUT_REPORT, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Also write CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "keyword", "category", "lang", "kd", "label_en", "is_brand",
            "search_volume", "homepages", "dedicated", "platforms",
            "weak_domains", "mature_niche", "recommendation"
        ])
        for r in results:
            sa = r.get("serp_analysis", {})
            writer.writerow([
                r["keyword"], r.get("category", ""), r.get("lang", ""),
                r["kd"], r.get("label_en", ""), r.get("is_brand", False),
                r.get("search_volume", ""),
                sa.get("homepage_count", ""), sa.get("dedicated_count", ""),
                sa.get("platform_count", ""), sa.get("weak_domain_count", ""),
                sa.get("mature_dedicated_count", ""),
                r.get("recommendation", "")
            ])

    return report


def print_summary(report):
    """Print human-readable summary."""
    s = report["summary"]
    print(f"\n{'=' * 60}")
    print(f"  KD BATCH REPORT — {report['total_analyzed']} keywords analyzed")
    print(f"{'=' * 60}")
    print(f"\n  📊 Distribution:")
    print(f"     蓝海 (KD<25):  {s['blue_ocean']:>3}  ← 优先做内容")
    print(f"     较易 (25-39):  {s['easy']:>3}  ← 高质量文章可竞争")
    print(f"     中等 (40-54):  {s['medium']:>3}  ← 需要时间积累")
    print(f"     避雷 (55+):    {s['traps']:>3}  ← 浪费时间，别碰")

    print(f"\n  📈 Category Averages:")
    for cat, cs in sorted(report["category_stats"].items(), key=lambda x: x[1]["kd_avg"]):
        print(f"     {cat:<20} avg={cs['kd_avg']:>5}  range={cs['kd_min']}-{cs['kd_max']}  n={cs['count']}")

    print(f"\n  🟢 TOP 15 蓝海词 (KD<25):")
    for r in report["blue_ocean"][:15]:
        vol = f" vol={r['search_volume']:,}" if r.get("search_volume") else ""
        print(f"     KD={r['kd']:>5}  {r['keyword'][:45]:<45}{vol}")

    print(f"\n  🔴 TOP 10 避雷词 (KD≥55 or 品牌词):")
    for r in report["traps"][:10]:
        brand = " [品牌词]" if r.get("is_brand") else ""
        print(f"     KD={r['kd']:>5}  {r['keyword'][:45]:<45}{brand}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch KD analysis")
    parser.add_argument("--limit", type=int, help="Max keywords to process (for testing)")
    parser.add_argument("--category", help="Filter by category prefix (e.g. en_tarot)")
    parser.add_argument("--report-only", action="store_true", help="Skip API calls, just generate report from cache")
    args = parser.parse_args()

    keywords = load_keywords()

    if args.category:
        keywords = [k for k in keywords if k["category"].startswith(args.category)]

    print(f"Loaded {len(keywords)} keywords")

    if not args.report_only:
        cache = load_cache()
        done, skipped, errors = run_batch(keywords, cache, limit=args.limit)
        print(f"\nDone: {done} new, {skipped} cached, {len(errors)} errors")
    else:
        print("Report-only mode (using cache)")

    cache = load_cache()
    report = generate_report(cache)
    print_summary(report)
    print(f"\n  📁 Full report: {OUTPUT_REPORT}")
    print(f"  📁 CSV export:  {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
