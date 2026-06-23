# Evaluation Standard

## Non-Negotiable Trend Rule

Keyword trend must be verified before a candidate can be recommended. Search-volume growth rate is weighted above absolute search volume.

Growth windows:
- 3-month growth: latest month compared with 3 months earlier.
- 6-month growth: latest month compared with 6 months earlier.
- 12-month growth: latest month compared with 12 months earlier.

Trend status:
- `rising`: positive 3-month growth and no strong 6/12-month contradiction.
- `flat`: weak, mixed, or near-zero growth.
- `falling`: negative recent or long-window growth.
- `insufficient`: fewer than 4 monthly data points or no reliable trend source.

Decision constraint:
- `优先进入` requires `rising`.
- High search volume with `falling` or `flat` trend cannot be `优先进入`.
- Low search volume with sustained growth may be `可小批量测试` or better if competition and profit are favorable.

## Market Size Bands

Use source-site category or keyword market volume when available:
- `3W以内`: cold/niche market.
- `5W以内`: small market.
- `5-15W`: small-to-mid market.
- `15-30W`: medium market.
- `30-50W`: medium-large market.
- `50-80W`: large, likely red-ocean market.
- `80W+`: ultra red-ocean market.

For beginner sellers, prefer small-to-mid or segmented blue-ocean pockets unless competition is clearly weak and profit is defensible.

## Competition Indicators

Category side: monthly total sales, Top3 product/brand/seller concentration, Amazon owned share, new product count and share, average price, return rate, average review count, and rating.

Keyword side: search-volume growth rate, SPR, click concentration, conversion concentration, CPC, price-to-CPC ratio, demand/supply ratio, and keyword trend shape.

## Score Weights

| Dimension | Weight | Main Evidence |
| --- | ---: | --- |
| Market demand | 30 | Keyword growth rate, search volume, sales, trend sources, TikTok/social heat, new-product acceptance |
| Competition strength | 30 | CR3, review count, click/conversion concentration, SPR, CPC, Amazon share |
| Profit space | 20 | Price, cost, FBA/logistics, gross margin, CPC pressure |
| AU migration fit | 10 | Cultural fit, AU competitors, seasonality, AU compliance |
| Beginner fit and risk | 10 | Capital, supplier complexity, return risk, variant complexity, patent/compliance rough screen |

## Verdict Mapping

- `80-100`: `优先进入`, only if trend is `rising`.
- `70-79`: `可小批量测试`.
- `60-69`: `观察或补数据`.
- `<60`: `不建议进入`.

If trend is `flat`, `falling`, or `insufficient`, cap verdict at `可小批量测试` even when total score is high.

## Opportunity Types

- `高利润 + 大市场 + 小竞争`
- `高利润 + 小市场 + 小竞争`
- `低利润 + 大市场 + 小竞争`
- `非优先机会`

Profit bands: low under 20%, medium 20-30%, high 35%+.
