# Data Schema

## Normalized Candidate Fields

Each candidate in `data.json` should use this shape:

```json
{
  "candidate": "product or segment name",
  "primary_keyword": "main keyword",
  "long_tail_keywords": ["keyword 1", "keyword 2"],
  "source_site": "US",
  "target_site": "AU",
  "market": {"monthly_sales": 0, "monthly_revenue": 0, "search_volume": 0, "new_product_count": 0, "new_product_sales_share": 0},
  "competition": {"top3_product_concentration": 0, "top3_brand_concentration": 0, "top3_seller_concentration": 0, "click_concentration": 0, "conversion_concentration": 0, "spr": 0, "cpc": 0, "review_count": 0, "rating": 0, "amazon_owned_share": 0},
  "profit": {"price": 0, "cost": 0, "gross_margin": 0, "return_rate": 0},
  "migration": {"au_fit_notes": "", "au_competitor_count": null, "seasonality_risk": "", "compliance_risk": ""},
  "risk": {"forbidden_flags": [], "patent_risk": "", "assembly_complexity": "", "variant_complexity": ""},
  "keyword_history": [{"keyword": "main keyword", "month": "2026-01", "search_volume": 1000, "source": "SellerSprite export.csv"}],
  "source_refs": [{"source": "SellerSprite", "file": "export.csv", "collected_at": "2026-06-23", "fields": ["search_volume"]}]
}
```

## Common Field Aliases

Candidate/name: `candidate`, `product`, `product_name`, `品名`, `产品`, `产品名称`, `类目`, `细分市场`.

Keyword: `primary_keyword`, `keyword`, `关键词`, `主关键词`, `搜索词`.

Long-tail keywords: `long_tail_keywords`, `related_keywords`, `长尾词`, `细分关键词`, `相关关键词`.

Search and trend: `search_volume`, `monthly_search`, `月搜索量`, `搜索量`, and monthly history columns such as `2026-01`, `2026/01`, `Jan 2026`, `近3月搜索量`.

Sales: `monthly_sales`, `月销量`, `月销售量`, `top100_monthly_sales`, `monthly_revenue`, `月销售额`, `销售额`.

Competition: `top3_product_concentration`, `商品集中度`, `链接集中度`, `top3_brand_concentration`, `品牌集中度`, `top3_seller_concentration`, `卖家集中度`, `店铺集中度`, `click_concentration`, `点击集中度`, `conversion_concentration`, `转化集中度`, `转化总占比`, `spr`, `SPR`, `cpc`, `PPC`, `CPC`, `推荐CPC`.

Profit: `price`, `售价`, `价格`, `客单价`, `cost`, `采购成本`, `成本`, `gross_margin`, `利润率`, `毛利率`, `return_rate`, `退货率`.

Risk: `forbidden_flags`, `禁入`, `风险标签`, `patent_risk`, `专利风险`, `compliance_risk`, `合规风险`.

## Evidence Rules

Every candidate must carry `source_refs`. If a script cannot identify sources, it must create a source reference from the input file path and row number.

Evidence quality levels: `direct`, `derived`, `hypothesis`.
