# Data Schema

## Normalized Candidate Fields

Each candidate in `data.json` should use this shape:

```json
{
  "candidate": "product title or segment name",
  "primary_keyword": "main seed or verified keyword",
  "long_tail_keywords": ["seed keyword 1", "seed keyword 2"],
  "title_seed_keywords": ["keywords extracted from product title"],
  "verified_trend_keywords": ["keywords with search history evidence"],
  "source_site": "US",
  "target_site": "AU",
  "identifiers": {"asin": "", "brand": "", "product_url": "", "image_url": ""},
  "category": {"path": "", "main": "", "sub": ""},
  "market": {"monthly_sales": 0, "monthly_sales_growth": 0, "monthly_revenue": 0, "search_volume": 0, "new_product_count": 0, "new_product_sales_share": 0},
  "competition": {"top3_product_concentration": 0, "top3_brand_concentration": 0, "top3_seller_concentration": 0, "click_concentration": 0, "conversion_concentration": 0, "spr": 0, "cpc": 0, "review_count": 0, "rating": 0, "seller_count": 0, "variant_count": 0, "amazon_owned_share": 0},
  "profit": {"price": 0, "cost": 0, "fba_fee": 0, "gross_margin": 0, "return_rate": 0},
  "migration": {"au_fit_notes": "", "au_competitor_count": null, "seasonality_risk": "", "compliance_risk": ""},
  "seasonality": {"label": "evergreen|seasonal|event_driven|insufficient", "source_peak_months": [6, 7], "au_entry_window": "US peak Jun, Jul -> AU rough peak Dec, Jan; test/stock 1-2 months before AU peak", "notes": "Seasonality interpretation and AU timing caveat"},
  "risk": {"forbidden_flags": [], "patent_risk": "", "assembly_complexity": "", "variant_complexity": "", "package_size_segment": ""},
  "keyword_history": [{"keyword": "main keyword", "month": "2026-01", "search_volume": 1000, "source": "SellerSprite keyword export.csv"}],
  "source_refs": [{"source": "SellerSprite", "file": "Product-US-Last-30-days-580346.xlsx", "collected_at": "2026-06-23", "fields": ["\u5546\u54c1\u6807\u9898"]}]
}
```

## SellerSprite Product Export Mapping

Default folder: `references/sellersprite/`.

Product discovery fields:
- Candidate/title: `\u5546\u54c1\u6807\u9898`.
- Identifiers: `ASIN`, `\u54c1\u724c`, `\u5546\u54c1\u8be6\u60c5\u9875\u94fe\u63a5`, `\u5546\u54c1\u4e3b\u56fe`.
- Category: `\u7c7b\u76ee\u8def\u5f84`, `\u5927\u7c7b\u76ee`, `\u5c0f\u7c7b\u76ee`.
- Market: `\u6708\u9500\u91cf`, `\u6708\u9500\u91cf\u589e\u957f\u7387`, `\u6708\u9500\u552e\u989d($)`.
- Competition: `\u8bc4\u5206\u6570`, `\u8bc4\u5206`, `\u5356\u5bb6\u6570`, `\u53d8\u4f53\u6570`, `BuyBox\u7c7b\u578b`, `\u5356\u5bb6\u6240\u5c5e\u5730`.
- Profit/logistics: `\u4ef7\u683c($)`, `FBA($)`, `\u6bdb\u5229\u7387`, `\u5305\u88c5\u5c3a\u5bf8\u5206\u6bb5`.
- Keyword seeds: `\u5546\u54c1\u6807\u9898`, `AC\u5173\u952e\u8bcd`.

`\u5546\u54c1\u6807\u9898` is treated as a keyword bundle for discovery only. It does not prove trend growth.

## Common Field Aliases

Candidate/name: `candidate`, `product`, `product_name`, `\u54c1\u540d`, `\u4ea7\u54c1`, `\u4ea7\u54c1\u540d\u79f0`, `\u5546\u54c1\u6807\u9898`.

Keyword: `primary_keyword`, `keyword`, `\u5173\u952e\u8bcd`, `\u4e3b\u5173\u952e\u8bcd`, `\u641c\u7d22\u8bcd`.

Long-tail keywords: `long_tail_keywords`, `related_keywords`, `\u957f\u5c3e\u8bcd`, `\u7ec6\u5206\u5173\u952e\u8bcd`, `\u76f8\u5173\u5173\u952e\u8bcd`, `AC\u5173\u952e\u8bcd`.

Search and trend: `search_volume`, `monthly_search`, `\u6708\u641c\u7d22\u91cf`, `\u641c\u7d22\u91cf`, and monthly history columns such as `2026-01`, `2026/01`, `Jan 2026`, `\u8fd13\u6708\u641c\u7d22\u91cf`.



## Sorftime MCP Evidence Mapping

Use live tools under `mcp__sorftime_server` when available. See `references/sorftime-mcp.md` for call order and tool arguments.

- `keyword_trend`: append monthly search-volume points to `keyword_history`; add the keyword to `verified_trend_keywords` only when a usable history series is returned.
- `keyword_detail`: map returned search volume, ranking, CPC, or competition fields into `market.search_volume` and `competition.cpc` when present.
- `keyword_extends`: map related phrases into `long_tail_keywords`; do not count them as verified trend evidence until each term has trend history.
- `keyword_search_results`: map visible competitor counts, price/review/rating signals, and organic/ad position data into competition evidence.
- `product_report`: map ASIN-level validation into identifiers, market, competition, profit, and source references when fields are returned.
- `product_ranking_trend_by_keyword`: store keyword ranking history as supporting competitor/product acceptance evidence.
- `category_tree` and `similar_product_feature`: store category path and feature-pattern support; do not use alone as market-size proof.
- `tiktok_product_detail`, `tiktok_product_video`, `tiktok_product_video_author`, and `tikto_category_search_from_name`: store social-commerce evidence, content volume, creator signals, and category fit notes.

## Evidence Rules

Every candidate must carry `source_refs`. If a script cannot identify sources, it must create a source reference from the input file path and row number.

Evidence quality levels: `direct`, `derived`, `hypothesis`.

## Seasonality Fields

`score_opportunities.py` adds `seasonality` to each scored opportunity, based on verified `keyword_history`.

- `seasonality.label`: `evergreen`, `seasonal`, `event_driven`, or `insufficient`.
- `seasonality.source_peak_months`: source-market peak month numbers, usually from US keyword history.
- `seasonality.au_entry_window`: AU timing guidance. For US weather/season demand, shift peak months by about 6 months.
- `seasonality.notes`: explanation and caveat, especially for holiday/IP/year-driven demand that needs manual AU cultural validation.
