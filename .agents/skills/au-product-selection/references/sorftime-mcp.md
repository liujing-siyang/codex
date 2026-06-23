# Sorftime MCP Supplementary Data Sources

Official entry: `https://open.sorftime.com/mcp?atag=MjAxODA5MTMyMzIwMzU1NzAwMDE~`.

Use the configured `sorftime-server` MCP as a supplement to SellerSprite product-discovery exports. Prefer live tool discovery over older repository examples because callable names can differ from historical docs. Never use Sorftime data to bypass the core rule: verified keyword growth is required before a candidate can receive `????`.

## Live Namespace

Use tools exposed under `mcp__sorftime_server`. The currently verified Amazon/TikTok tools for this skill are listed below.

## Priority Tool Map For AU Product Selection

### Keyword Trend And Demand

Use these first when a SellerSprite product export only has title seed keywords.

| Need | Live tool | Required arguments | Use in report |
| --- | --- | --- | --- |
| Keyword details and demand | `keyword_detail` | `keyword`, `keywordSupportSite` | Current keyword demand, competition/CPC fields if returned |
| Keyword history trend | `keyword_trend` | `keyword`, `keywordSupportSite` | 3/6/12-month growth, trend status, verified trend keywords |
| SERP/product competition | `keyword_search_results` | `keyword`, `keywordSupportSite`, optional `page`, `positionType` | Natural/ad result products, review wall, price band, competitor density |
| Long-tail discovery | `keyword_extends` | `keyword`, `keywordSupportSite`, optional `page` | Expand title seeds into long-tail opportunities; not trend evidence by itself |

Recommended sequence for each candidate:

1. Take 3-8 `title_seed_keywords` and any `AC???`.
2. Call `keyword_extends` for the strongest seed to expand long tails.
3. Call `keyword_detail` and `keyword_trend` for the primary seed plus 2-5 long tails.
4. Store keyword history into `keyword_history` and matching names into `verified_trend_keywords`.
5. Call `keyword_search_results` only after trend is rising or strategically interesting.

### Product, Category, And Competitor Validation

| Need | Live tool | Required arguments | Use in report |
| --- | --- | --- | --- |
| Product/ASIN analysis report | `product_report` | `asin`, optional `amzSite` | Validate price, sales/rank/review/category fields if returned |
| Category tree | `category_tree` | optional `amzSite`, optional `nodeid` | Locate category structure; not a market-size substitute by itself |
| Category/product feature signals | `similar_product_feature` | `productName`, optional `amzSite` | Extract common feature patterns and differentiation clues |
| Product rank by keyword trend | `product_ranking_trend_by_keyword` | `asin`, `keyword`, optional `amzSite`, `page` | Ranking stability for core terms and competitor traction |

Use product/category data to support market size, competition, and AU migration scores. Do not let category or product trend replace keyword trend; it is supporting evidence.

### TikTok Validation

Use TikTok as social-commerce trend evidence, especially for visual, giftable, fashion, home, beauty-adjacent, and impulse-buy products.

| Need | Live tool | Required arguments | Use in report |
| --- | --- | --- | --- |
| TikTok product details | `tiktok_product_detail` | `productId`, optional `site` | Product price, shop, rating, sales/content fields if returned |
| TikTok product videos | `tiktok_product_video` | `productId`, optional `site`, `page` | Video volume, creator/content signals |
| TikTok product creators | `tiktok_product_video_author` | `productId`, optional `site` | Creator concentration and reach clues |
| TikTok category lookup | `tikto_category_search_from_name` | `name`, optional `site` | Category-level social validation |

TikTok sites exposed by the current MCP include `US`, `GB`, `MY`, `PH`, `VN`, `TH`, `ID`, and `JP`. Use `US` or `GB` as proxy social signals for AU unless AU-specific TikTok data is provided elsewhere.

## Supported Amazon Sites

Amazon sites exposed by the current keyword tools include `US`, `GB`, `DE`, `FR`, `CA`, `JP`, `ES`, `IT`, `MX`, `AE`, `AU`, `BR`, and `SA`. Some product/category tools also expose `IN`. Always pass the exact enum supported by the selected live tool.

## Evidence Integration Rules

Store Sorftime outputs in `data.json` or adjacent raw files with source references:

```json
{
  "source_refs": [
    {"source": "Sorftime MCP", "tool": "keyword_trend", "arguments": {"keywordSupportSite": "US", "keyword": "sun stick"}, "collected_at": "2026-06-23"}
  ],
  "verified_trend_keywords": ["sun stick"],
  "keyword_history": [
    {"keyword": "sun stick", "month": "2026-05", "search_volume": 18364, "source": "Sorftime keyword_trend"}
  ]
}
```

If a Sorftime response is unavailable, too sparse, or returns no trend series, mark that candidate as `trend_status = insufficient` and list the missing evidence in the report.

## Recommended Call Budget

For a SellerSprite product file with many rows, do not call Sorftime for every product initially.

1. First screen locally by hard exclusions, gross margin, review count, rating, monthly sales, variant count, and title seeds.
2. Pick the top 20-50 candidates for Sorftime keyword validation.
3. For each candidate, validate 1 primary seed and 2-5 long-tail seeds.
4. Run deeper product/category/TikTok checks only for candidates with rising keyword trend and acceptable competition.

## Legacy Name Notes

Older repo references or screenshots may mention names such as `keyword_search_result`, `keyword_related_words`, `product_detail`, `product_trend`, `category_report`, or `tiktok_product_videos`. Do not call those names unless live tool discovery exposes them. Map them to the live tools above where possible.
