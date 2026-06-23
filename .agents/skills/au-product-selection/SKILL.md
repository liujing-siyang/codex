---
name: au-product-selection
description: AU marketplace migration product-selection skill. Use when Codex needs to evaluate Amazon product opportunities for Australia from US or other mature marketplaces using SellerSprite CSV, Sorftime MCP, TikTok, Google Trends, Exploding Topics, web evidence, keyword growth, competition, profit, compliance risk, and beginner-seller fit; produces an evidence-backed HTML decision dashboard.
---

# AU Product Selection

## Operating Rules

Act as a senior Amazon product selection manager for a seller whose main target marketplace is Australia. Use mature marketplaces, especially US, to validate trend direction, consumer acceptance, and product preferences before recommending AU listing opportunities.

Never invent data. Every market size, growth, competition, profit, trend, VOC, or risk conclusion must cite a source: input file name, Sorftime tool/API response, TikTok/Google Trends/Exploding Topics/web URL, or user-provided document. If evidence is missing, mark the conclusion as a hypothesis or data insufficient.

Keyword trend validation is mandatory. Search-volume growth rate is more important than absolute search volume. A product with large search volume but falling or flat keyword trend must not receive the 优先进入 verdict.

Default source marketplace: `US`. Default target marketplace: `AU`. Prefer SellerSprite CSV exports as the primary input when provided; use Sorftime MCP, TikTok, Google Trends, Exploding Topics, Reddit/social media, and web scraping as validation layers.

## Quick Start

1. Normalize data:
   ```bash
   python .agents/skills/au-product-selection/scripts/normalize_inputs.py --input <csv_or_folder> --topic "<topic>" --source-site US --target-site AU --output reports/au-product-selection/<run>
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

Accept SellerSprite CSV exports, Sorftime MCP data, TikTok trend data, Google Trends, Exploding Topics, Reddit/social media pages, web pages, and user-provided supplier/cost/FBA/patent/compliance notes.

### 2. Normalize And Preserve Evidence

Run `normalize_inputs.py` for CSV/JSON files. Preserve raw files under `raw/` where possible. Standardize fields according to `references/data-schema.md`.

Important normalized fields include `candidate`, `primary_keyword`, `long_tail_keywords`, `monthly_sales`, `monthly_revenue`, `search_volume`, `keyword_history`, concentration metrics, `spr`, `cpc`, `price`, `cost`, `gross_margin`, `return_rate`, and `source_refs`.

### 3. Verify Keyword Trend First

For every candidate, require at least 1 primary keyword and 2-5 long-tail or segment keywords when available. Calculate 3-month, 6-month, and 12-month search-volume growth rates whenever history exists. If history is unavailable, mark `trend_status = insufficient`.

Trend verdicts: `rising`, `flat`, `falling`, or `insufficient`. Do not assign 优先进入 unless trend status is `rising`.

### 4. Score And Classify

Read `references/evaluation-standard.md` before scoring. Use the fixed weights: market demand 30, competition strength 30, profit space 20, AU migration fit 10, beginner fit and risk 10.

Classify opportunity types as 高利润 + 大市场 + 小竞争, 高利润 + 小市场 + 小竞争, 低利润 + 大市场 + 小竞争, or non-priority.

Apply hard exclusions before scoring: liquid, supplement, medical/health product, prohibited item, obvious patent risk, strong compliance/regulatory requirement, complex assembly, fragile oversized goods, or poor AU cultural fit.

### 5. Validate AU Migration

Check consumer behavior and cultural fit, US/AU seasonality differences, AU Amazon competitors or keyword signals, and AU-specific certification, biosecurity, therapeutic, electrical, child-safety, food-contact, or import risks.

### 6. Render Decision Dashboard

Generate `index.html` with Top 10 opportunities, score, verdict, opportunity type, keyword growth, core evidence, biggest risk, AU fit label, and detail tables for market, competition, profit, keyword growth, social/VOC evidence, AU validation, hard-exclusion screen, and patent/compliance rough check.

Every important table must include a 关键洞察 paragraph with data source and collection time.

## References

Read these only when needed:
- `references/evaluation-standard.md` for scoring thresholds, market size bands, and competition indicators.
- `references/data-schema.md` for accepted CSV/JSON field mappings.
- `references/prompt-templates.md` for trend, VOC, AU migration, and patent rough-screen prompts.

## Guardrails

- Prefer growth rate over absolute keyword search volume.
- Do not use one metric alone for final decisions.
- Do not hide missing data.
- Do not treat a product as safe from patent or compliance risk; only perform rough screening and recommend manual review.
- Do not recommend beginner sellers enter capital-heavy, high-review, high-CPC, high-return, or strong-brand-dominated markets without explicit caveats.
