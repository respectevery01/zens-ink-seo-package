#!/usr/bin/env python3
"""Run KD batch on all remaining Echoir keywords — writes progress to log."""
import sys, os, time, json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from zens_ink.kd import fetch_serp, calculate_kd, fetch_search_volume

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(os.path.dirname(SCRIPT_DIR))
CSV_PATH = os.path.join(WORKSPACE, "pro-package", "keywords-master.csv")
CACHE_PATH = os.path.join(SCRIPT_DIR, "kd-cache.json")
LOG_PATH = os.path.join(SCRIPT_DIR, "kd-progress.log")
DELAY = 1.0

def load_cache():
    try:
        with open(CACHE_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")

def main():
    import csv
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        all_kws = [{"keyword": r["keyword"].strip(), "category": r.get("category",""), "lang": r.get("lang","en")} 
                    for r in reader if r["keyword"].strip()]

    cache = load_cache()
    todo = [k for k in all_kws if k["keyword"] not in cache]
    log(f"Total: {len(all_kws)} | Cached: {len(cache)} | Todo: {len(todo)}")

    done = 0
    errors = 0
    for kw_data in todo:
        kw = kw_data["keyword"]
        lang = kw_data["lang"]
        cat = kw_data["category"]
        is_zh = lang == "zh"
        gl = "cn" if is_zh else "us"
        hl = "zh-CN" if is_zh else "en"
        market = "zh-CN" if is_zh else "en-US"

        try:
            serp = fetch_serp(kw, gl=gl, hl=hl)
            volume = fetch_search_volume(kw, market=market)
            result = calculate_kd(serp, kw, volume)

            cache[kw] = {
                "keyword": kw, "category": cat, "lang": lang,
                "kd": result.get("kd"), "label": result.get("label"),
                "label_en": result.get("label_en"),
                "is_brand": result.get("is_brand_keyword", False),
                "search_volume": result.get("search_volume"),
                "serp_analysis": result.get("serp_analysis"),
            }
            done += 1
            label = result.get("label_en", "?")
            kd_val = result.get("kd", 0)
            log(f"  [{done}/{len(todo)}] KD={kd_val:>5} [{label}] {cat} | {kw}")

            if done % 10 == 0:
                save_cache(cache)
        except Exception as e:
            errors += 1
            log(f"  [ERROR] {kw}: {e}")

        time.sleep(DELAY)

    save_cache(cache)
    log(f"DONE: {done} scored, {errors} errors, {len(cache)} total in cache")

if __name__ == "__main__":
    main()
