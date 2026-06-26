# Roadmap

> The shortest path from "I should do SEO" to "I did it." Free tools for discovery, Pro engine for outcomes.

## Design Philosophy

- **OSS gives tools. Pro gives outcomes.**
  Every Pro increment must orchestrate multiple tools into a single result — not just add another data point.
- **Be where Ahrefs isn't.** Cheaper, indie-focused, Agent-native.
- **Ship one killer increment per major version.** No feature bloat.

---

## Phase 0 — Ship (Now)

**OSS (v0.2)**
- 6 tools: `keyword_research`, `keyword_volume`, `kd`, `brave_volume`, `competitor_gap`, `search_performance`
- Pure Python stdlib, zero dependencies
- Clone and run — no install friction

**Pro (v7)**
- Winability Score, Content Radar, Competitor Radar
- Per-buyer watermarking, Agent Skills compliant

**Goal**: Public release, collect early user feedback.

---

## Phase 1 — Foundation (0–2 months)

### OSS

- [ ] `pyproject.toml` → `pip install zens-ink`
- [ ] GIF demos in README (3-second animation per tool)
- [ ] `zens_ink audit` — one-command technical SEO audit (canonical, orphan pages, sitemap, H1 checks)
- [ ] Bug fixes and edge cases from community feedback

### Pro v8 — Content Briefs

The biggest gap right now: users know *which keywords* to target but not *how to write* for them.

- Keyword → structured content brief (recommended H2 structure, entities to cover, PAA questions, target word count)
- Content Radar + Briefs integration: one click from calendar to brief
- **Outcome**: "I know what to write and how to structure it."

---

## Phase 2 — GEO (2–4 months)

### OSS

- [ ] `serp_features` — detect SERP feature occupancy (featured snippets, PAA, AI Overview presence)
- [ ] `internal_links` — site link structure analysis, find orphan pages and linking opportunities
- [ ] Growing pip download numbers

### Pro v9 — GEO Score + Backlink Radar

- **GEO Score**: How likely is your content to be cited by AI search? (BLUF presence, structured data, fact density, llms.txt existence). Validated against Echoir's own GEO experiments (dogfooding).
- **Backlink Radar**: Discover competitor backlink sources using free data (Common Crawl, public link indices).
- **Outcome**: "I know if AI will cite me and where my competitors' authority comes from."

---

## Phase 3 — Automation (4–8 months)

### OSS

- [ ] Plugin architecture (`zens_ink.plugins`) — community-contributed analyzers
- [ ] `zens_ink monitor` — continuous SERP tracking + change notifications

### Pro v10 — Agent Workflow

- End-to-end pipeline: keyword discovery → Winability filter → Content Brief → draft generation → internal link suggestions → publish
- Custom weekly report (GSC data + SERP changes + new opportunity keywords, auto-emailed)
- Multi-site support (one license, N projects)
- **Outcome**: "I review and approve; the engine does the rest."

---

## Phase 4 — Ecosystem (8–12 months)

- [ ] Open API / lightweight hosted dashboard (no Python needed)
- [ ] Community workflow marketplace (similar to Agent Skills registry)
- [ ] CMS integrations (Astro / Next.js / Hugo auto-injected content suggestions)
- [ ] Pro pricing scales with value ($39 → $59 → $79); early bird users locked at original price

---

## Release Cadence

| Type | Frequency | Content |
|------|-----------|---------|
| Major Pro version | ~2 months | One killer increment |
| Minor Pro version | As needed | Bug fixes, refinements |
| OSS release | Continuous | New tools, community PRs |

## Competitive Moat

Every increment is judged by two questions:

1. **Can Ahrefs do this?** (If yes, we don't build it.)
2. **Is it free or near-free?** (If it costs $500/mo, we don't depend on it.)

By the time competitors adapt to Agent-native workflows, we'll have a year of accumulated workflow data and community trust.
