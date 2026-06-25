#!/usr/bin/env python3
"""
Keyword Difficulty (KD) estimator — ZensInk lightweight edition.

Core innovation: SERP structure analysis (homepage ratio, domain age profile,
niche maturity) as the primary difficulty signal, eliminating the need for
expensive Ahrefs DR data.

Scoring model (0-100):
  Base score from weighted SERP structure (page-type × position × authority)
  + Signal modifiers (homepage density, brand dominance, niche maturity,
    weak-domain opportunity, domain age profile)

Usage:
  python -m zens_ink kd "the fool tarot meaning"
  python -m zens_ink kd "tarot meaning" --json
  python -m zens_ink kd "生辰八字" --zh
"""

import json
import sys
import os
import time
import math
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# ── Config ──────────────────────────────────────────────────────────────────

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
SERPER_URL = "https://google.serper.dev/search"
BING_API_KEY = os.getenv("BING_API_KEY", "")
BING_STATS_URL = "https://ssl.bing.com/webmaster/api.svc/json/GetKeywordStats"

# Curated authority domains (high DR proxies — no API needed)
AUTHORITY_DOMAINS = {
    # Encyclopedic (DR 95+)
    "en.wikipedia.org": 0.95, "zh.wikipedia.org": 0.95, "simple.wikipedia.org": 0.95,
    "wikimedia.org": 0.90, "britannica.com": 0.92,
    # Platforms (high authority, but beatable for informational queries)
    "youtube.com": 0.95, "www.youtube.com": 0.95,
    "reddit.com": 0.90, "www.reddit.com": 0.90,
    "quora.com": 0.88, "www.quora.com": 0.88,
    "pinterest.com": 0.92, "www.pinterest.com": 0.92,
    "medium.com": 0.90, "tiktok.com": 0.92,
    "instagram.com": 0.93, "www.instagram.com": 0.93,
    "facebook.com": 0.95, "www.facebook.com": 0.95,
    "twitter.com": 0.93, "x.com": 0.93,
    "linkedin.com": 0.93, "www.linkedin.com": 0.93,
    # App stores
    "apps.apple.com": 0.95, "play.google.com": 0.95, "apps.microsoft.com": 0.93,
    # Major tech
    "amazon.com": 0.95, "github.com": 0.94, "stackoverflow.com": 0.92,
    # Major media / news (DR 90+)
    "forbes.com": 0.93, "www.forbes.com": 0.93,
    "cnbc.com": 0.92, "www.cnbc.com": 0.92,
    "nytimes.com": 0.95, "www.nytimes.com": 0.95,
    "bbc.com": 0.95, "www.bbc.com": 0.95,
    "cnn.com": 0.94, "www.cnn.com": 0.94,
    "reuters.com": 0.94, "www.reuters.com": 0.94,
    "bloomberg.com": 0.93, "www.bloomberg.com": 0.93,
    "theguardian.com": 0.93, "www.theguardian.com": 0.93,
    "washingtonpost.com": 0.94,
    "vogue.com": 0.91, "www.vogue.com": 0.91,
    "elle.com": 0.88, "www.elle.com": 0.88,
    "cosmopolitan.com": 0.87,
    "hindustantimes.com": 0.85, "www.hindustantimes.com": 0.85,
    # Tech media
    "techcrunch.com": 0.92, "wired.com": 0.91, "www.wired.com": 0.91,
    "theverge.com": 0.91, "arstechnica.com": 0.90,
    "cnet.com": 0.91, "www.cnet.com": 0.91,
    "pcmag.com": 0.88, "engadget.com": 0.90,
    # Finance / credit
    "nerdwallet.com": 0.90, "www.nerdwallet.com": 0.90,
    "bankrate.com": 0.89, "www.bankrate.com": 0.89,
    "creditkarma.com": 0.88, "www.creditkarma.com": 0.88,
    "creditcards.com": 0.87, "www.creditcards.com": 0.87,
    "investopedia.com": 0.91, "www.investopedia.com": 0.91,
    "mastercard.com": 0.88, "www.mastercard.com": 0.88,
    "visa.com": 0.88, "www.visa.com": 0.88,
    # Health / medical
    "healthline.com": 0.90, "webmd.com": 0.90, "mayoclinic.org": 0.90,
    "psychologytoday.com": 0.88, "verywellmind.com": 0.87,
    "medicalnewstoday.com": 0.88, "medlineplus.gov": 0.90,
    "webmd.com": 0.90,
    # Travel
    "tripadvisor.com": 0.92, "www.tripadvisor.com": 0.92,
    "booking.com": 0.93, "www.booking.com": 0.93,
    "expedia.com": 0.90, "www.expedia.com": 0.90,
    # Education
    "coursera.org": 0.91, "edx.org": 0.89, "udemy.com": 0.90,
    "khanacademy.org": 0.90,
    # Reviews / recommendations
    "consumerreports.org": 0.90, "tomsguide.com": 0.88,
    "thepointsguy.com": 0.85, "www.thepointsguy.com": 0.85,
    # Q&A / reference
    "merriam-webster.com": 0.91, "dictionary.com": 0.88,
    "cambridge.org": 0.90,
    # Chinese platforms
    "baike.baidu.com": 0.90, "zhihu.com": 0.88, "www.zhihu.com": 0.88,
    "douban.com": 0.87, "weibo.com": 0.90, "www.weibo.com": 0.90,
    "csdn.net": 0.82, "www.csdn.net": 0.82,
    "juejin.cn": 0.80, "www.juejin.cn": 0.80,
    "bilibili.com": 0.88, "www.bilibili.com": 0.88,
    "sina.com.cn": 0.90, "www.sina.com.cn": 0.90,
    "sohu.com": 0.87, "www.sohu.com": 0.87,
    "163.com": 0.89, "www.163.com": 0.89,
}

PLATFORM_DOMAINS = {
    "youtube.com", "www.youtube.com", "reddit.com", "www.reddit.com",
    "quora.com", "www.quora.com", "pinterest.com", "www.pinterest.com",
    "medium.com", "instagram.com", "www.instagram.com",
    "facebook.com", "www.facebook.com", "twitter.com", "x.com",
    "linkedin.com", "www.linkedin.com", "tiktok.com",
    "apps.apple.com", "play.google.com", "apps.microsoft.com",
    "zhihu.com", "www.zhihu.com", "weibo.com", "www.weibo.com",
    "douban.com", "bilibili.com", "www.bilibili.com",
}

# ── HTTP helpers ────────────────────────────────────────────────────────────

def _http_get_json(url, headers=None, timeout=15):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def _http_post_json(url, data, headers=None, timeout=15):
    body = json.dumps(data).encode("utf-8")
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=body, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

# ── RDAP domain age ────────────────────────────────────────────────────────

def get_domain_age(domain):
    """Return registration year (int) via RDAP, or None."""
    clean = domain.replace("www.", "")
    try:
        req = urllib.request.Request(f"https://rdap.org/domain/{clean}")
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for event in data.get("events", []):
            if event.get("eventAction") == "registration":
                return int(event["eventDate"][:4])
    except Exception:
        pass
    return None

# ── Serper SERP fetch ──────────────────────────────────────────────────────

def fetch_serp(keyword, gl="us", hl="en", num=10):
    payload = {"q": keyword, "gl": gl, "hl": hl, "num": num}
    headers = {"X-API-KEY": SERPER_API_KEY}
    return _http_post_json(SERPER_URL, payload, headers=headers)

# ── Bing search volume ─────────────────────────────────────────────────────

def fetch_search_volume(keyword, market="en-US"):
    if not BING_API_KEY:
        return None
    params = urllib.parse.urlencode({"q": keyword, "market": market, "apikey": BING_API_KEY})
    url = f"{BING_STATS_URL}?{params}"
    try:
        data = _http_get_json(url, timeout=10)
        stats = data.get("d", [])
        if stats:
            return stats[0].get("BroadImpression", 0)
    except Exception:
        pass
    return None

# ── URL / domain analysis ─────────────────────────────────────────────────

def parse_url(url):
    parsed = urllib.parse.urlparse(url)
    return parsed.netloc.lower(), parsed.path.rstrip("/")

def is_homepage(url):
    _, path = parse_url(url)
    return path == "" or path == "/"

def is_platform(url):
    domain, _ = parse_url(url)
    return domain in PLATFORM_DOMAINS

def get_authority(url):
    domain, _ = parse_url(url)
    return AUTHORITY_DOMAINS.get(domain)

def title_matches_keyword(title, keyword):
    title_lower = title.lower()
    keyword_lower = keyword.lower()
    kw_words = [w for w in keyword_lower.split() if len(w) > 2]
    if not kw_words:
        return keyword_lower in title_lower
    matches = sum(1 for w in kw_words if w in title_lower)
    return matches >= max(1, len(kw_words) * 0.6)

def classify_result(result, keyword):
    url = result.get("link", "")
    title = result.get("title", "")
    pos = result.get("position", 99)
    has_sitelinks = bool(result.get("sitelinks"))

    domain, _ = parse_url(url)
    home = is_homepage(url)
    platform = is_platform(url)
    known_auth = get_authority(url)

    if home:
        page_type, type_mult = "homepage", 1.0
    elif title_matches_keyword(title, keyword):
        page_type, type_mult = "dedicated", 0.65
    else:
        page_type, type_mult = "inner", 0.45

    return {
        "position": pos, "url": url, "domain": domain, "title": title,
        "page_type": page_type, "type_multiplier": type_mult,
        "is_homepage": home, "is_platform": platform,
        "known_authority": known_auth,
        "has_sitelinks": has_sitelinks,
        "registration_year": None,
        "authority_score": known_auth,
        "auth_source": "known_list" if known_auth is not None else None,
    }

# ── Domain authority estimation ───────────────────────────────────────────

def estimate_domain_auth(domain, registration_year=None):
    """Estimate authority (0-1) without Ahrefs DR. Domain age is primary proxy."""
    known = AUTHORITY_DOMAINS.get(domain) or AUTHORITY_DOMAINS.get(domain.replace("www.", ""))
    if known is not None:
        return known, "known_list"

    if registration_year:
        age = datetime.now(timezone.utc).year - registration_year
        # Conservative age curve (can't match real DR, just a rough proxy):
        # 1yr→0.28, 2yr→0.34, 3yr→0.38, 5yr→0.45, 8yr→0.52, 10yr→0.56,
        # 15yr→0.63, 20yr→0.68, 25yr→0.72
        if age <= 0:
            score = 0.20
        else:
            score = min(0.72, 0.22 + 0.15 * math.log(age) / math.log(3))
        return score, f"age_{age}yr"

    return 0.35, "unknown"

# ── KD Scoring ────────────────────────────────────────────────────────────

def calculate_kd(serp_data, keyword, search_volume=None):
    organic = serp_data.get("organic", [])
    if not organic:
        return {"error": "No organic results", "keyword": keyword, "kd": None}

    # Phase 1: Classify all results
    results = [classify_result(r, keyword) for r in organic[:10]]

    # Phase 2: Fetch domain ages for unknown-authority domains (top 8)
    to_check = {r["domain"] for r in results[:8] if r["authority_score"] is None}
    domain_ages = {}
    for domain in to_check:
        year = get_domain_age(domain)
        if year:
            domain_ages[domain] = year
        time.sleep(0.08)

    # Phase 3: Estimate authority for all results
    for r in results:
        if r["authority_score"] is None:
            reg = domain_ages.get(r["domain"])
            r["registration_year"] = reg
            auth, src = estimate_domain_auth(r["domain"], reg)
            r["authority_score"] = auth
            r["auth_source"] = src

    # Phase 3.5: Brand keyword detection
    # If #1 result has sitelinks AND its domain name matches the keyword,
    # this is a brand query — difficulty score is not meaningful for direct targeting.
    is_brand_keyword = False
    brand_warning = None
    if results and results[0].get("has_sitelinks"):
        top_domain = results[0]["domain"].replace("www.", "").split(".")[0].lower()
        kw_lower = keyword.lower().strip()
        kw_words = kw_lower.split()
        # Only flag as brand if keyword is short (1-2 words) and primary word
        # closely matches the domain brand name
        if len(kw_words) <= 2:
            primary = kw_words[0]
            if len(primary) >= 4 and (
                primary == top_domain
                # keyword contains brand name (e.g. "notionlogin" starts with "notion")
                or (len(top_domain) >= 5 and primary.startswith(top_domain))
                # brand name close to keyword (e.g. "notion" vs "notions", max 2 char diff)
                or (top_domain.startswith(primary) and len(top_domain) - len(primary) <= 2)
            ):
                is_brand_keyword = True
                brand_warning = (
                    f"⚠ 品牌词检测：Google 将「{keyword}」识别为品牌查询（#1 结果含 Sitelinks）。\n"
                    f"  正面排名几乎不可能——建议改打衍生词：\n"
                    f"  · `{keyword} alternative` / `{keyword} 替代`\n"
                    f"  · `{keyword} vs [竞品]`\n"
                    f"  · `{keyword} review` / `{keyword} 评价`\n"
                    f"  · `best {keyword} alternatives`\n"
                    f"  · `how to use {keyword}`\n"
                    f"  · `{keyword} pricing` / `{keyword} 定价`"
                )

    # ── Phase 4: Multi-signal scoring ───────────────────────────────────

    # Signal A: Weighted SERP strength (position × page_type × authority)
    pos_weights = [1.00, 0.93, 0.86, 0.79, 0.72, 0.65, 0.58, 0.51, 0.44, 0.37]
    weighted_sum = 0.0
    weight_total = 0.0
    for i, r in enumerate(results):
        pw = pos_weights[min(i, 9)]
        weighted_sum += r["authority_score"] * r["type_multiplier"] * pw
        weight_total += pw
    serp_strength = weighted_sum / weight_total if weight_total else 0.5

    # Signal B: Homepage density (0-1)
    home_count = sum(1 for r in results if r["is_homepage"])
    home_ratio = home_count / len(results)

    # Signal C: Domain age profile
    ages = [datetime.now(timezone.utc).year - r["registration_year"]
            for r in results if r.get("registration_year")]
    avg_age = sum(ages) / len(ages) if ages else None

    # Signal D: Platform / brand dominance
    platform_count = sum(1 for r in results if r["is_platform"])
    has_sitelinks = any(r["has_sitelinks"] for r in results)

    # Signal E: Niche maturity (dedicated pages from old domains)
    mature_dedicated = sum(
        1 for r in results
        if r["page_type"] == "dedicated"
        and (r.get("registration_year") and datetime.now(timezone.utc).year - r["registration_year"] > 8
             or r["authority_score"] >= 0.70)
    )

    # Signal F: Weak domain opportunity (low authority in top 10)
    weak_domains = [r for r in results if r["authority_score"] < 0.50 and not r["is_platform"]]
    weak_in_top5 = [r for r in weak_domains if r["position"] <= 5]
    new_domains = [r for r in results if r.get("registration_year")
                   and datetime.now(timezone.utc).year - r["registration_year"] < 2]

    # ── Composite base score (0-100) ────────────────────────────────────
    # Anchor: SERP strength scaled to 0-60 range (primary component)
    base = serp_strength * 60

    # ── Signal modifiers ────────────────────────────────────────────────
    modifiers = {}

    # Homepage density
    if home_count >= 7:
        modifiers["homepage_crowded"] = 18
    elif home_count >= 5:
        modifiers["homepage_heavy"] = 10
    elif home_count >= 3:
        modifiers["homepage_moderate"] = 4
    elif home_count == 0:
        modifiers["no_homepages"] = -5

    # Niche maturity — old dedicated content sites = entrenched competition
    if mature_dedicated >= 5:
        modifiers["mature_niche"] = 14
    elif mature_dedicated >= 3:
        modifiers["established_niche"] = 7

    # Brand dominance
    if has_sitelinks and platform_count >= 3:
        modifiers["brand_dominated"] = 12
    elif platform_count >= 5:
        modifiers["platform_heavy"] = 6

    # Domain age profile
    if avg_age:
        if avg_age >= 15:
            modifiers["old_domains"] = 6
        elif avg_age <= 3:
            modifiers["young_domains"] = -6

    # Weak domain opportunity (position-weighted)
    if weak_in_top5:
        modifiers["weak_top5"] = -min(15, len(weak_in_top5) * 5)
    elif weak_domains:
        modifiers["weak_lower"] = -min(8, len(weak_domains) * 3)

    # New domain proof
    if new_domains:
        modifiers["new_domain_proof"] = -5

    # Top-3 fortress
    top3 = results[:3]
    top3_strong = all(
        r["authority_score"] >= 0.80 or (r["is_homepage"] and r["authority_score"] >= 0.60)
        for r in top3
    )
    if top3_strong:
        modifiers["top3_fortress"] = 6

    # Search volume prior
    if search_volume:
        if search_volume > 500000:
            modifiers["very_high_volume"] = 6
        elif search_volume > 100000:
            modifiers["high_volume"] = 3
        elif search_volume < 500:
            modifiers["low_volume"] = -2

    modifier_total = sum(modifiers.values())
    raw_score = base + modifier_total
    final_score = max(1, min(99, raw_score))

    # Label
    if final_score >= 70:
        label, label_en = "极难", "Very Hard"
        rec = "新站不建议正面进攻，考虑长尾变体或衍生内容"
    elif final_score >= 55:
        label, label_en = "困难", "Hard"
        rec = "需要高质量专门页 + 时间积累，长尾词优先"
    elif final_score >= 40:
        label, label_en = "中等", "Medium"
        rec = "有机会，做好内容质量和内链即可竞争"
    elif final_score >= 25:
        label, label_en = "较易", "Easy"
        rec = "好机会，一篇高质量文章即可冲击首页"
    else:
        label, label_en = "极易", "Very Easy"
        rec = "蓝海词，优先创建内容抢占先机"

    dedicated_count = sum(1 for r in results if r["page_type"] == "dedicated")
    inner_count = len(results) - home_count - dedicated_count

    return {
        "keyword": keyword,
        "kd": round(final_score, 1),
        "label": label, "label_en": label_en,
        "recommendation": rec,
        "is_brand_keyword": is_brand_keyword,
        "brand_warning": brand_warning,
        "search_volume": search_volume,
        "base_score": round(base, 1),
        "modifiers": modifiers,
        "modifier_total": modifier_total,
        "serp_analysis": {
            "homepage_count": home_count,
            "dedicated_count": dedicated_count,
            "inner_count": inner_count,
            "platform_count": platform_count,
            "has_brand_sitelinks": has_sitelinks,
            "mature_dedicated_count": mature_dedicated,
            "avg_domain_age": round(avg_age, 1) if avg_age else None,
            "weak_domain_count": len(weak_domains),
            "weak_in_top5": len(weak_in_top5),
            "new_domain_count": len(new_domains),
        },
        "results": [
            {
                "position": r["position"],
                "domain": r["domain"],
                "page_type": r["page_type"],
                "authority": round(r["authority_score"], 2),
                "auth_source": r.get("auth_source", ""),
                "is_homepage": r["is_homepage"],
                "has_sitelinks": r["has_sitelinks"],
                "registration_year": r.get("registration_year"),
            }
            for r in results
        ],
    }

# ── CLI ────────────────────────────────────────────────────────────────────

def format_report(result):
    if result.get("error"):
        return f"Error: {result['error']}"

    L = []
    w = 62
    L.append(f"┌─ KD Analysis: {result['keyword']}")
    L.append(f"│")
    
    # Brand keyword warning (takes priority over score)
    if result.get("brand_warning"):
        for line in result["brand_warning"].split("\n"):
            L.append(f"│  {line}")
        L.append(f"│")
        L.append(f"│  (FYI raw score: {result['kd']}/100 — not meaningful for brand queries)")
        L.append(f"│")
    else:
        L.append(f"│  Score: {result['kd']}/100  [{result['label']} / {result['label_en']}]")
        if result.get("search_volume"):
            L.append(f"│  Volume: ~{result['search_volume']:,}/month (Bing broad)")
        L.append(f"│  Base: {result['base_score']}  +  Modifiers: {result['modifier_total']:+.0f}")
        L.append(f"│  → {result['recommendation']}")
    L.append(f"│")

    sa = result["serp_analysis"]
    L.append(f"│  SERP Structure:")
    L.append(f"│    Homepages: {sa['homepage_count']}/10  |  Dedicated: {sa['dedicated_count']}/10  |  Inner: {sa['inner_count']}/10")
    L.append(f"│    Platforms: {sa['platform_count']}/10  |  Brand sitelinks: {'Yes' if sa['has_brand_sitelinks'] else 'No'}")
    L.append(f"│    Mature niche sites: {sa['mature_dedicated_count']}/10  |  Avg domain age: {sa['avg_domain_age'] or '?'}yr")
    L.append(f"│    Weak domains (top5): {sa['weak_in_top5']}  |  Weak domains (total): {sa['weak_domain_count']}")
    L.append(f"│    New domains (<2yr): {sa['new_domain_count']}")

    if result["modifiers"]:
        L.append(f"│")
        L.append(f"│  Signal Modifiers:")
        for name, val in result["modifiers"].items():
            L.append(f"│    {name}: {val:+d}")

    L.append(f"│")
    L.append(f"│  Top 10 Breakdown:")
    for r in result["results"]:
        flags = []
        if r["is_homepage"]: flags.append("HOME")
        if r["has_sitelinks"]: flags.append("SITELINKS")
        if r["is_homepage"] and r["authority"] >= 0.6: flags.append("STRONG")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        age_str = f" ({r['registration_year']})" if r.get("registration_year") else ""
        L.append(
            f"│    {r['position']:>2}. {r['domain']:<32} "
            f"{r['page_type']:<10} "
            f"A≈{r['authority']:.2f}{age_str}{flag_str}"
        )
    L.append(f"└{'─' * w}")
    return "\n".join(L)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog="zens_ink kd",
        description="Keyword Difficulty estimator (SERP structure based)",
    )
    parser.add_argument("keyword", help="Keyword to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--gl", default="us", help="Geo location (default: us)")
    parser.add_argument("--hl", default="en", help="Language (default: en)")
    parser.add_argument("--zh", action="store_true", help="Chinese mode (gl=cn, hl=zh-CN)")
    parser.add_argument("--no-volume", action="store_true", help="Skip search volume lookup")

    args = parser.parse_args()

    if not SERPER_API_KEY:
        print("Error: SERPER_API_KEY not set", file=sys.stderr)
        print("Get a free key at https://serper.dev (2500 free searches)", file=sys.stderr)
        sys.exit(1)

    gl = "cn" if args.zh else args.gl
    hl = "zh-CN" if args.zh else args.hl
    market = "zh-CN" if args.zh else "en-US"

    serp = fetch_serp(args.keyword, gl=gl, hl=hl)
    volume = None if args.no_volume else fetch_search_volume(args.keyword, market=market)
    result = calculate_kd(serp, args.keyword, volume)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_report(result))

if __name__ == "__main__":
    main()
