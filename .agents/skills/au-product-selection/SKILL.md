---
name: au-product-selection
description: AU marketplace migration product-selection skill. Use when Codex needs to evaluate Amazon product opportunities for Australia from US or other mature marketplaces using SellerSprite CSV/XLSX exports from references/sellersprite, Sorftime MCP, TikTok, Google Trends, Exploding Topics, web evidence, keyword growth, competition, profit, compliance risk, and beginner-seller fit; produces an evidence-backed HTML decision dashboard.
---

# AU Product Selection

## Operating Rules

Act as a senior Amazon product selection manager for a seller whose main target marketplace is Australia. Use mature marketplaces, especially US, to validate trend direction, consumer acceptance, and product preferences before recommending AU listing opportunities.

Never invent data. Every market size, growth, competition, profit, trend, VOC, or risk conclusion must cite a source: input file name, Sorftime tool/API response, TikTok/Google Trends/Exploding Topics/web URL, or user-provided document. If evidence is missing, mark the conclusion as a hypothesis or data insufficient.

Keyword trend validation is mandatory. Search-volume growth rate is more important than absolute search volume. A product with large search volume but falling or flat keyword trend must not receive the \u4f18\u5148\u8fdb\u5165 verdict.

Default source marketplace: `US`. Default target marketplace: `AU`. Prefer SellerSprite exports under `references/sellersprite/` as the primary product-discovery input when provided. Use Sorftime MCP, TikTok, Google Trends, Exploding Topics, Reddit/social media, and web scraping as validation layers. When Sorftime is available, prefer the live `mcp__sorftime_server` tools and read `references/sorftime-mcp.md`; treat older repo docs or official pages as conceptual references when tool names differ.

## Quick Start

1. Normalize SellerSprite product data:
   ```bash
   python .agents/skills/au-product-selection/scripts/normalize_inputs.py --input E:/code/codex/references/sellersprite/Product-US-Last-30-days-580346.xlsx --topic seller_sprite_real --source-site US --target-site AU --output reports/au-product-selection/<run>
   ```
2. Score opportunities:
   ```bash
   python .agents/skills/au-product-selection/scripts/score_opportunities.py reports/au-product-selection/<run>/data.json
   ```
3. Validate evidence:
   ```bash
   python .agents/skills/au-product-selection/scripts/validate_evidence.py reports/au-product-selection/<run>/scorecard.json
   ```
4. Render HTML:
   ```bash
   python .agents/skills/au-product-selection/scripts/render_html_report.py reports/au-product-selection/<run>/scorecard.json
   ```

Default output directory:

```text
reports/au-product-selection/{topic}_{sourceSite}_to_AU_{YYYYMMDD}/
```

The run directory must keep `data.json`, `scorecard.json`, `evidence.json`, `index.html`, and `raw/` files when available.

## Workflow

### 1. Gather Inputs

Accept SellerSprite CSV/XLSX exports, Sorftime MCP data, TikTok trend data, Google Trends, Exploding Topics, Reddit/social media pages, web pages, and user-provided supplier/cost/FBA/patent/compliance notes.

SellerSprite product exports are product-discovery data. They can identify candidates and seed keywords, but they do not by themselves prove keyword trend.

### 2. Normalize And Preserve Evidence

Run `normalize_inputs.py` for CSV/XLSX/JSON files. Preserve raw files under `raw/` where possible. Standardize fields according to `references/data-schema.md`.

Important normalized fields include `candidate`, `primary_keyword`, `long_tail_keywords`, `title_seed_keywords`, `verified_trend_keywords`, `monthly_sales`, `monthly_revenue`, `search_volume`, `keyword_history`, `seasonality`, concentration metrics, `spr`, `cpc`, `price`, `fba_fee`, `gross_margin`, `return_rate`, and `source_refs`.

### 3. Use Product Titles As Keyword Seeds

Treat SellerSprite `\u5546\u54c1\u6807\u9898` as a product-keyword and attribute-keyword bundle. Extract the product noun phrase, modifiers, specs, use cases, and risk terms into `title_seed_keywords`.

Merge `AC\u5173\u952e\u8bcd` with title-derived seeds into `long_tail_keywords`. These are discovery seeds only. They do not count as verified trend evidence until matched with SellerSprite keyword-history exports, Sorftime, Google Trends, Exploding Topics, TikTok, or another trend source.

### 4. Verify Keyword Trend First

For every candidate, require at least 1 primary keyword and 2-5 long-tail or segment keywords when available. Calculate 3-month, 6-month, and 12-month search-volume growth rates whenever history exists. If history is unavailable, mark `trend_status = insufficient` and show `\u8d8b\u52bf\u5f85\u9a8c\u8bc1` in the dashboard.

Trend verdicts: `rising`, `flat`, `falling`, or `insufficient`. Do not assign \u4f18\u5148\u8fdb\u5165 unless trend status is `rising`.

### 5. Score And Classify

Read `references/evaluation-standard.md` before scoring. Use the fixed weights: market demand 30, competition strength 30, profit space 20, AU migration fit 10, beginner fit and risk 10.

Classify opportunity types as \u9ad8\u5229\u6da6 + \u5927\u5e02\u573a + \u5c0f\u7ade\u4e89, \u9ad8\u5229\u6da6 + \u5c0f\u5e02\u573a + \u5c0f\u7ade\u4e89, \u4f4e\u5229\u6da6 + \u5927\u5e02\u573a + \u5c0f\u7ade\u4e89, or non-priority.

Apply hard exclusions before scoring: liquid, supplement, medical/health product, prohibited item, obvious patent risk, strong compliance/regulatory requirement, complex assembly, fragile oversized goods, or poor AU cultural fit.

### 6. Validate AU Migration

Check consumer behavior and cultural fit, US/AU seasonality differences, AU Amazon competitors or keyword signals, and AU-specific certification, biosecurity, therapeutic, electrical, child-safety, food-contact, or import risks.

For US-to-AU migration, always treat weather/season demand as opposite-season by default. If a US keyword peaks in summer/winter months, shift the rough AU test/stock window by about 6 months. Do not automatically shift holiday, IP, anniversary, or other event-driven demand; mark those for manual AU cultural validation.

### 7. Render Decision Dashboard

Generate `index.html` with a priority manual-review table and an extended manual-review table. The priority table should show at most the first 10 reviewable opportunities, using ASIN and representative keyword instead of long product titles. The extended table should include every other reviewable opportunity with ASIN, keyword, search volume, keyword growth, seasonality label, AU entry window, and recommended action.

Reviewable means total score >= 70 or `trend_status = rising`, excluding hard-elimination candidates. Detail sections should use `ASIN / representative keyword` as the heading. Product titles may appear only as secondary source context.

Every important table must include a \u5173\u952e\u6d1e\u5bdf paragraph with data source and collection time.

## References

Read these only when needed:
- `references/evaluation-standard.md` for scoring thresholds, market size bands, and competition indicators.
- `references/data-schema.md` for accepted CSV/XLSX/JSON field mappings.
- `references/prompt-templates.md` for trend, VOC, AU migration, and patent rough-screen prompts.
- `references/sorftime-mcp.md` when supplementing SellerSprite data with the configured `sorftime-server` MCP tools.

## Guardrails

- Prefer growth rate over absolute keyword search volume.
- Do not treat product-title keywords as trend evidence.
- Do not ignore Northern/Southern Hemisphere seasonality when migrating US trends to AU.
- Do not use one metric alone for final decisions.
- Do not hide missing data.
- Do not treat a product as safe from patent or compliance risk; only perform rough screening and recommend manual review.
- Do not recommend beginner sellers enter capital-heavy, high-review, high-CPC, high-return, or strong-brand-dominated markets without explicit caveats.
