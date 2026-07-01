#!/usr/bin/env python3
"""
Site Audit — scan built HTML for common technical SEO issues.

Checks:
  1. Orphan pages: in sitemap but no internal links found in built HTML
  2. Missing trailing slashes: internal links that cause 301 redirects
  3. Broken internal links: paths not present in sitemap (404 candidates)
  4. Missing canonical tags: pages without <link rel="canonical">
  5. Missing meta descriptions: pages without <meta name="description">
  6. Missing H1: pages without an <h1> tag in server HTML
  7. Multiple H1: pages with more than one <h1>

Works on any static build output (Astro, Next.js export, Hugo, etc.).

Usage:
  python3 -m zens_ink.site_audit --dist dist --sitemap dist/sitemap.xml
  python3 -m zens_ink.site_audit --dist dist --sitemap dist/sitemap.xml --base /en
  python3 -m zens_ink.site_audit --dist dist --sitemap dist/sitemap.xml --format json
  python3 -m zens_ink.site_audit --dist dist --sitemap dist/sitemap.xml --format csv --output audit.csv

Options:
  --dist       Path to build output directory (default: dist)
  --sitemap    Path to sitemap XML file (auto-detects sitemap-0.xml / sitemap.xml)
  --base       Base URL path prefix to filter (e.g., /en for English-only audit)
  --format     Output format: text, json, csv (default: text)
  --output     Write to file instead of stdout (for json/csv)
  --verbose    Show all link targets, not just issues
"""

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

_STATIC_EXTS = {
    ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".css", ".js", ".xml", ".json", ".webmanifest",
    ".woff", ".woff2", ".ttf", ".otf", ".txt", ".ico",
    ".pdf", ".zip", ".mp4", ".mp3", ".map",
}


# ── Parsing ──────────────────────────────────────────────────────────────

def parse_sitemap(sitemap_path: Path, base_path: str = "") -> set[str]:
    """Extract URL paths from sitemap XML (supports sitemap-index)."""
    if not sitemap_path.exists():
        for alt in ["sitemap-0.xml", "sitemap.xml"]:
            alt_path = sitemap_path.parent / alt
            if alt_path.exists():
                sitemap_path = alt_path
                break
        else:
            print(f"ERROR: Sitemap not found: {sitemap_path}", file=sys.stderr)
            sys.exit(1)

    content = sitemap_path.read_text(errors="ignore")

    # If this is a sitemap index, follow sub-sitemaps
    if "<sitemapindex" in content:
        sub_locs = re.findall(r"<loc>(.*?\.xml)</loc>", content)
        paths = set()
        for sub_url in sub_locs:
            parsed = urlparse(sub_url)
            sub_file = sitemap_path.parent / Path(parsed.path).name
            if sub_file.exists():
                sub_paths = parse_sitemap(sub_file, base_path)
                paths.update(sub_paths)
        # Also scan for any sitemap-*.xml siblings
        for sibling in sitemap_path.parent.glob("sitemap*.xml"):
            if sibling == sitemap_path:
                continue
            sibling_content = sibling.read_text(errors="ignore")
            if "<sitemapindex" in sibling_content:
                continue  # already handled above
            sub_paths = parse_sitemap(sibling, base_path)
            paths.update(sub_paths)
        return paths

    urls = re.findall(r"<loc>(.*?)</loc>", content)

    paths = set()
    for url in urls:
        parsed = urlparse(url)
        path = parsed.path or "/"
        if base_path and not path.startswith(base_path):
            continue
        paths.add(path.rstrip("/") or "/")

    return paths


def find_html_files(dist_dir: Path) -> list[Path]:
    """Find all .html files in the dist directory."""
    return sorted(dist_dir.rglob("*.html"))


def extract_hrefs(content: str) -> list[str]:
    """Extract all internal href="/..." paths from HTML."""
    return re.findall(r'href="(/[^"]*)"', content)


# ── Checks ───────────────────────────────────────────────────────────────

def check_orphan_pages(
    sitemap_paths: set[str],
    link_sources: dict[str, set[str]],
) -> list[dict]:
    """Pages in sitemap but no incoming internal links."""
    issues = []
    for path in sorted(sitemap_paths):
        normalized = path.rstrip("/") or "/"
        if normalized not in link_sources:
            if not any(
                normalized == k or normalized == k.rstrip("/")
                for k in link_sources
            ):
                issues.append({
                    "type": "orphan_page",
                    "severity": "warning",
                    "path": path,
                    "detail": "In sitemap but no internal links found",
                })
    return issues


def check_trailing_slashes(dist_dir: Path) -> list[dict]:
    """Internal links without trailing slash that would cause 301 redirects."""
    issues = []
    seen = set()
    for html_file in dist_dir.rglob("*.html"):
        try:
            content = html_file.read_text(errors="ignore")
        except Exception:
            continue
        hrefs = extract_hrefs(content)
        rel = str(html_file.relative_to(dist_dir))
        for href in hrefs:
            if any(href.endswith(ext) for ext in _STATIC_EXTS):
                continue
            if href.endswith("/"):
                continue
            if "?" in href or "#" in href:
                continue
            key = (rel, href)
            if key in seen:
                continue
            seen.add(key)
            issues.append({
                "type": "missing_trailing_slash",
                "severity": "info",
                "path": href,
                "source": rel,
                "detail": "May cause 301 redirect",
            })
    return issues


def check_dangling_links(
    sitemap_paths: set[str],
    dist_dir: Path,
) -> list[dict]:
    """Links in HTML that don't match any sitemap URL (potential 404s)."""
    sitemap_normalized = {p.rstrip("/") or "/" for p in sitemap_paths}
    issues = []
    seen = set()
    for html_file in dist_dir.rglob("*.html"):
        try:
            content = html_file.read_text(errors="ignore")
        except Exception:
            continue
        hrefs = extract_hrefs(content)
        rel = str(html_file.relative_to(dist_dir))
        for href in hrefs:
            clean = href.split("#")[0].split("?")[0].rstrip("/") or "/"
            if clean == "/" or clean in sitemap_normalized:
                continue
            if any(clean.endswith(ext) for ext in _STATIC_EXTS):
                continue
            key = (rel, href)
            if key in seen:
                continue
            seen.add(key)
            issues.append({
                "type": "broken_link",
                "severity": "error",
                "path": href,
                "source": rel,
                "detail": "Link target not in sitemap (potential 404)",
            })
    return issues


def check_canonical(dist_dir: Path) -> list[dict]:
    """Pages missing <link rel="canonical">."""
    issues = []
    for html_file in dist_dir.rglob("*.html"):
        try:
            content = html_file.read_text(errors="ignore")
        except Exception:
            continue
        if 'rel="canonical"' not in content and "rel='canonical'" not in content:
            rel = str(html_file.relative_to(dist_dir))
            # Skip 404 pages
            if "404" in rel:
                continue
            issues.append({
                "type": "missing_canonical",
                "severity": "warning",
                "path": rel,
                "detail": "No canonical tag found",
            })
    return issues


def check_meta_description(dist_dir: Path) -> list[dict]:
    """Pages missing <meta name="description">."""
    issues = []
    pattern = re.compile(
        r'<meta\s+name=["\']description["\']', re.IGNORECASE
    )
    for html_file in dist_dir.rglob("*.html"):
        try:
            content = html_file.read_text(errors="ignore")
        except Exception:
            continue
        rel = str(html_file.relative_to(dist_dir))
        if "404" in rel:
            continue
        if not pattern.search(content):
            issues.append({
                "type": "missing_meta_description",
                "severity": "warning",
                "path": rel,
                "detail": "No meta description tag",
            })
    return issues


def check_h1(dist_dir: Path) -> list[dict]:
    """Pages missing H1 or having multiple H1 tags."""
    issues = []
    h1_pattern = re.compile(r"<h1[\s>]", re.IGNORECASE)
    for html_file in dist_dir.rglob("*.html"):
        try:
            content = html_file.read_text(errors="ignore")
        except Exception:
            continue
        rel = str(html_file.relative_to(dist_dir))
        if "404" in rel:
            continue
        count = len(h1_pattern.findall(content))
        if count == 0:
            issues.append({
                "type": "missing_h1",
                "severity": "warning",
                "path": rel,
                "detail": "No H1 tag in server HTML",
            })
        elif count > 1:
            issues.append({
                "type": "multiple_h1",
                "severity": "info",
                "path": rel,
                "detail": f"{count} H1 tags found (recommend exactly 1)",
            })
    return issues


# ── Link source map ──────────────────────────────────────────────────────

def build_link_map(
    dist_dir: Path,
) -> tuple[dict[str, set[str]], set[str]]:
    """Scan all HTML for internal links. Returns (path→sources, all_targets)."""
    link_sources: dict[str, set[str]] = {}
    all_links: set[str] = set()
    for html_file in dist_dir.rglob("*.html"):
        try:
            content = html_file.read_text(errors="ignore")
        except Exception:
            continue
        hrefs = extract_hrefs(content)
        rel = str(html_file.relative_to(dist_dir))
        for href in hrefs:
            clean = href.split("#")[0].split("?")[0].rstrip("/")
            if clean:
                all_links.add(clean)
                if clean not in link_sources:
                    link_sources[clean] = set()
                link_sources[clean].add(rel)
    return link_sources, all_links


# ── Output ───────────────────────────────────────────────────────────────

def format_text(
    issues: list[dict],
    sitemap_count: int,
    html_count: int,
    verbose: bool,
    link_sources: dict[str, set[str]],
) -> str:
    """Format issues as human-readable text."""
    buf = io.StringIO()
    sep = "=" * 60

    buf.write(f"{sep}\nSite Audit Report\n{sep}\n")
    buf.write(f"Sitemap URLs: {sitemap_count}\n")
    buf.write(f"HTML files scanned: {html_count}\n")

    if verbose:
        buf.write(f"\n--- All link targets ({len(link_sources)}) ---\n")
        for target in sorted(link_sources):
            buf.write(f"  {target} ({len(link_sources[target])} refs)\n")

    # Group by type
    by_type: dict[str, list[dict]] = {}
    for issue in issues:
        by_type.setdefault(issue["type"], []).append(issue)

    type_labels = {
        "orphan_page": "ORPHAN PAGES",
        "missing_trailing_slash": "MISSING TRAILING SLASHES",
        "broken_link": "BROKEN LINKS (potential 404)",
        "missing_canonical": "MISSING CANONICAL TAGS",
        "missing_meta_description": "MISSING META DESCRIPTIONS",
        "missing_h1": "MISSING H1 TAGS",
        "multiple_h1": "MULTIPLE H1 TAGS",
    }

    for issue_type, label in type_labels.items():
        group = by_type.get(issue_type, [])
        unique_paths = sorted({i["path"] for i in group})
        buf.write(f"\n{sep}\n{label}: {len(unique_paths)} unique")
        if len(group) != len(unique_paths):
            buf.write(f" ({len(group)} total)")
        buf.write(f"\n{sep}\n")
        if unique_paths:
            for path in unique_paths:
                detail = next(
                    (i["detail"] for i in group if i["path"] == path), ""
                )
                source = next(
                    (i.get("source", "") for i in group if i["path"] == path), ""
                )
                suffix = f"  (in {source})" if source else ""
                buf.write(f"  {path}{suffix}\n")
                if detail:
                    buf.write(f"    → {detail}\n")
        else:
            buf.write("  None — all good.\n")

    # Summary
    errors = sum(1 for i in issues if i["severity"] == "error")
    warnings = sum(1 for i in issues if i["severity"] == "warning")
    infos = sum(1 for i in issues if i["severity"] == "info")

    buf.write(f"\n{sep}\nSUMMARY\n{sep}\n")
    buf.write(f"  Errors:   {errors}\n")
    buf.write(f"  Warnings: {warnings}\n")
    buf.write(f"  Info:     {infos}\n")
    buf.write(f"  Total:    {len(issues)}\n")
    if errors == 0 and warnings == 0:
        buf.write("\n  ✓ No critical issues found!\n")
    buf.write(sep + "\n")

    return buf.getvalue()


def format_json(issues: list[dict], sitemap_count: int, html_count: int) -> str:
    """Format as JSON."""
    errors = sum(1 for i in issues if i["severity"] == "error")
    warnings = sum(1 for i in issues if i["severity"] == "warning")
    data = {
        "summary": {
            "sitemap_urls": sitemap_count,
            "html_files": html_count,
            "total_issues": len(issues),
            "errors": errors,
            "warnings": warnings,
        },
        "issues": issues,
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_csv(issues: list[dict]) -> str:
    """Format as CSV."""
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=["type", "severity", "path", "source", "detail"],
    )
    writer.writeheader()
    for issue in issues:
        writer.writerow({
            "type": issue.get("type", ""),
            "severity": issue.get("severity", ""),
            "path": issue.get("path", ""),
            "source": issue.get("source", ""),
            "detail": issue.get("detail", ""),
        })
    return buf.getvalue()


# ── Main ─────────────────────────────────────────────────────────────────

def run(
    dist_dir: Path,
    sitemap_path: Path,
    base_path: str = "",
    output_format: str = "text",
    output_file: str = "",
    verbose: bool = False,
) -> str:
    """Run the full audit and return formatted output."""
    # 1. Parse sitemap
    sitemap_paths = parse_sitemap(sitemap_path, base_path)

    # 2. Scan HTML files
    html_files = find_html_files(dist_dir)

    # 3. Build link map
    link_sources, _ = build_link_map(dist_dir)

    # 4. Run all checks
    all_issues: list[dict] = []
    all_issues.extend(check_orphan_pages(sitemap_paths, link_sources))
    all_issues.extend(check_trailing_slashes(dist_dir))
    all_issues.extend(check_dangling_links(sitemap_paths, dist_dir))
    all_issues.extend(check_canonical(dist_dir))
    all_issues.extend(check_meta_description(dist_dir))
    all_issues.extend(check_h1(dist_dir))

    # 5. Format output
    if output_format == "json":
        result = format_json(all_issues, len(sitemap_paths), len(html_files))
    elif output_format == "csv":
        result = format_csv(all_issues)
    else:
        result = format_text(
            all_issues, len(sitemap_paths), len(html_files),
            verbose, link_sources,
        )

    if output_file:
        Path(output_file).write_text(result, encoding="utf-8")
        return f"Written to {output_file}"

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Technical SEO audit for static site builds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python3 -m zens_ink.site_audit --dist dist --sitemap dist/sitemap.xml
  python3 -m zens_ink.site_audit --dist dist --base /en --verbose
  python3 -m zens_ink.site_audit --dist dist --format json --output report.json
""",
    )
    parser.add_argument(
        "--dist", default="dist",
        help="Build output directory (default: dist)",
    )
    parser.add_argument(
        "--sitemap", default="dist/sitemap.xml",
        help="Sitemap XML path (auto-detects sitemap-0.xml)",
    )
    parser.add_argument(
        "--base", default="",
        help="Base path prefix filter (e.g., /en)",
    )
    parser.add_argument(
        "--format", choices=["text", "json", "csv"], default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--output", default="",
        help="Write to file instead of stdout",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Show all link targets",
    )
    args = parser.parse_args()

    dist_dir = Path(args.dist)
    if not dist_dir.exists():
        print(f"ERROR: dist directory not found: {dist_dir}", file=sys.stderr)
        sys.exit(1)

    sitemap_path = Path(args.sitemap)

    result = run(
        dist_dir=dist_dir,
        sitemap_path=sitemap_path,
        base_path=args.base,
        output_format=args.format,
        output_file=args.output,
        verbose=args.verbose,
    )
    print(result)


if __name__ == "__main__":
    main()
