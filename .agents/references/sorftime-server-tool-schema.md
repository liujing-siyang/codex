# Sorftime Server MCP Live Tool Schema

This project must treat the active MCP tool schema as the source of truth for Sorftime calls.

Codex can only call tools registered under the live `mcp__sorftime_server` namespace. Older repository docs, screenshots, and official API pages can be useful for business context, but they are not callable unless the same tool name and argument names are exposed in the current MCP schema.

Last verified in this project from the live Codex tool schema on 2026-07-01.

## Required Calling Rules

1. Prefer direct MCP tool calls over manual `curl` calls to `https://mcp.sorftime.com`.
2. Use the exact live tool name and exact argument names from the schema.
3. For Amazon keyword tools, the site argument is usually `keywordSupportSite`; for Amazon product/category tools, it is usually `amzSite`.
4. Treat older names, aliases, and official API endpoint names as unsafe unless they appear in this file or in a fresh live schema discovery.
5. If an expected endpoint is not registered as a live MCP tool, mark it unavailable instead of inventing a call.
6. Store evidence with tool name, arguments, source, and collection time when generating reports.

## Amazon Keyword Tools

| Live tool | Purpose | Main arguments |
| --- | --- | --- |
| `keyword_list` | Real-time Amazon hot keyword list by weekly search volume | `keywordSupportSite`, `page`, `rank_min`, `rank_max`, `search_volume_min`, `search_volume_max` |
| `keyword_list_from_history` | Historical Amazon hot keyword list | `date`, `keywordSupportSite`, `page`, `rank_min`, `rank_max`, `search_volume_min`, `search_volume_max` |
| `keyword_detail` | Amazon hot keyword detail | `keyword`, `keywordSupportSite` |
| `keyword_search_results` | Amazon keyword SERP products, natural/ad/all positions | `keyword`, `keywordSupportSite`, `page`, `positionType` |
| `keyword_trend` | Amazon keyword search volume, rank, and CPC trend | `keyword`, `keywordSupportSite` |
| `keyword_extends` | Amazon related/long-tail keyword discovery | `keyword`, `keywordSupportSite`, `page` |
| `favorite_keyword` | Add Amazon keyword favorite | `keyword`, `keywordSupportSite`, `dict` |
| `del_favorite_keyword` | Delete Amazon keyword favorite | `keyword`, `keywordSupportSite`, `dict` |
| `change_favorite_keyword` | Move Amazon favorite keyword to a folder | `keyword`, `keywordSupportSite`, `fromDict`, `toDict` |
| `get_favorite_keyword` | List Amazon favorite keywords | `keywordSupportSite`, `dict`, `page` |
| `get_favorite_keyword_dict` | List Amazon favorite keyword folders | `keywordSupportSite`, `page` |

## Amazon Product Tools

| Live tool | Purpose | Main arguments |
| --- | --- | --- |
| `product_search` | Real-time Amazon product search, default sorted by monthly sales | `amzSite`, `searchName`, `brand`, `seller_name`, price/sales/rating/review/variation/category rank filters, `delivery_type`, `seasonal_popular_product`, `sortby_potential_index`, `page` |
| `product_search_from_history` | Historical Amazon product search by month | `searchTime`, `amzSite`, `searchName`, price/sales/rating/review filters, `delivery_type`, `page` |
| `potential_product` | Amazon potential-product search | `amzSite`, `searchName`, `delivery_type`, `price_min`, `price_max`, `month_sales_volume_min`, `month_sales_volume_max`, `page` |
| `product_detail` | Product detail for one ASIN | `asin`, `amzSite` |
| `product_report` | Single-product analysis report | `asin`, `amzSite` |
| `product_variations` | Product child variation details | `asin`, `amzSite` |
| `product_reviews` | Recent-year reviews, up to 100 | `asin`, `amzSite`, `reviewType` |
| `product_trend` | Product sales volume, sales amount, price, or rank trend | `asin`, `amzSite`, `productTrendType` |
| `product_traffic_terms` | Reverse ASIN traffic keywords from recent top-3-page exposure | `asin`, `amzSite`, `page` |
| `product_ranking_trend_by_keyword` | Product exposure rank trend under one keyword | `asin`, `keyword`, `amzSite`, `page` |
| `competitor_product_keywords` | Competitor/core keyword organic exposure positions | `asin`, `keywordSupportSite`, `page` |
| `ali1688_similar_product` | 1688 sourcing matches for cost reference | `searchName`, `page` |

## Amazon Category And Market Tools

| Live tool | Purpose | Main arguments |
| --- | --- | --- |
| `category_tree` | Amazon category tree and child nodes | `amzSite`, `nodeid` |
| `category_name_search` | Search Amazon fine categories by category name | `categoryName`, `amzSite` |
| `category_report` | Real-time Amazon category Top100 product report | `nodeId`, `amzSite` |
| `category_report_from_history` | Historical Amazon category Top100 product report | `nodeId`, `amzSite`, `startDate`, `endDate` |
| `category_trend` | Amazon fine category trend based on Top100 products | `nodeId`, `amzSite`, `trendIndex` |
| `category_keywords` | Core keywords for a fine category | `nodeId`, `amzSite`, `page` |
| `search_categories_broadly` | Broad multi-filter category/market search | `amzSite`, sales/price/rating/review/share/season filters, `page` |
| `category_search_from_top_node` | Search fine categories under a top category | `topNode`, `amzSite`, sales/price/rating/review/share/season filters, `page` |
| `category_search_from_product_name` | Search fine categories by product/category name | `productName`, `amzSite`, sales/price/rating/review/share/season filters, `page` |
| `similar_product_feature` | Feature signals for a category/product name | `productName`, `amzSite` |

Common Amazon category filter families include `month_sales_volume_min/max`, `price_min/max`, `ratings_min/max`, `ratings_count_min/max`, `amazonOwned_sales_share_min/max`, `newproduct_sales_share_min/max`, `top100_top400_sales_share_min/max`, `top3Product_sales_share_min/max`, and `seasonal_popular_product`.

## Shopee Tools

| Live tool | Purpose | Main arguments |
| --- | --- | --- |
| `shopee_product_search` | Shopee product search with multi-dimensional filters | `site`, `asin`, `nodeId`, price/sales/rating/review/variation/date/shop filters, `page` |
| `shopee_product_search_from_name` | Search Shopee products by name | `name`, `site`, `page` |
| `shopee_product_request` | Shopee product detail | `productId`, `site` |
| `shopee_product_trend` | Shopee product trend for star, reviews, price, cumulative sales, recent sales | `productId`, `site`, `queryStart`, `queryEnd` |
| `shopee_shop_request` | Shopee shop detail | `shopId`, `site` |
| `shopee_keyword_search` | Shopee hot keyword list | `keyword`, `site`, `rankMin`, `rankMax`, `searchVolumeMin`, `searchVolumeMax`, `page` |
| `shopee_keyword_relation_results` | Shopee products related to a keyword | `keyword`, `site`, `page` |
| `shopee_category_search_from_name` | Search Shopee categories by name | `name`, `site` |
| `shopee_category_request` | Shopee category Best Seller Top 500 products | `nodeId`, `site`, `queryDate`, `page` |
| `shopee_category_trend` | Shopee category market trend | `nodeId`, `site`, `trendIndex` |
| `shopee_favorite_keyword` | Add Shopee keyword favorite | `keyword`, `site`, `dict` |
| `shopee_del_favorite_keyword` | Delete Shopee keyword favorite | `keyword`, `site`, `dict` |
| `shopee_change_favorite_keyword` | Move Shopee favorite keyword to a folder | `keyword`, `site`, `fromDict`, `toDict` |
| `shopee_get_favorite_keyword` | List Shopee favorite keywords | `site`, `dict`, `page` |
| `shopee_get_favorite_keyword_dict` | List Shopee favorite keyword folders | `site`, `page` |

## Walmart Tools

| Live tool | Purpose | Main arguments |
| --- | --- | --- |
| `walmart_product_detail_by_product_id` | Walmart product detail | `productId` |
| `walmart_product_variations_by_product_id` | Walmart product variation sales details | `productId`, `beginDate`, `endDate`, `page` |
| `walmart_product_trend_by_product_id` | Walmart product trend for sales, amount, price, rank, reviews, star | `productId`, `trendType`, `beginDate`, `endDate` |
| `walmart_product_traffic_terms` | Walmart reverse product traffic keywords | `productId`, `page` |
| `walmart_category_report_by_node_id` | Real-time Walmart category Top100 product report | `nodeId` |
| `walmart_keyword_list` | Real-time Walmart hot keyword list by monthly search volume | `rank_min`, `rank_max`, `page` |
| `walmart_keyword_detail` | Walmart hot keyword detail | `keyword` |
| `walmart_keyword_search_from_name` | Search Walmart hot keywords by name | `name`, `page` |
| `walmart_keyword_search_results` | Walmart keyword SERP products from recent 15 days | `keyword`, `page` |
| `walmart_keyword_extends` | Walmart related/long-tail keyword discovery | `keyword`, `page` |
| `walmart_favorite_keyword` | Add Walmart keyword favorite | `keyword`, `dict` |
| `walmart_del_favorite_keyword` | Delete Walmart keyword favorite | `keyword`, `dict` |
| `walmart_change_favorite_keyword` | Move Walmart favorite keyword to a folder | `keyword`, `fromDict`, `toDict` |
| `walmart_get_favorite_keyword` | List Walmart favorite keywords | `dict`, `page` |
| `walmart_get_favorite_keyword_dict` | List Walmart favorite keyword folders | `page` |

## Temu Tools

| Live tool | Purpose | Main arguments |
| --- | --- | --- |
| `temu_product_search` | Temu product search with multi-dimensional filters | `site`, `productId`, `nodeId`, `brand`, `sellerName`, price/sales/rating/review/date/manage filters, `page` |
| `temu_product_search_from_name` | Search Temu products by name | `name`, `site`, `page` |
| `temu_product_request` | Temu product detail | `productId`, `site` |
| `temu_product_trend` | Temu product trend for sales, cumulative sales, amount, price, reviews, star | `productId`, `site`, `queryStart`, `queryEnd` |
| `temu_shop_request` | Temu shop detail | `shopId`, `site` |
| `temu_category_search` | Temu category search with multi-dimensional filters | `site`, `nodeId`, price/sales/rating/review/seller/brand/share filters, `page` |
| `temu_category_search_from_name` | Search Temu categories by name | `name`, `site` |
| `temu_category_request` | Temu category Best Seller products | `nodeId`, `site`, `page` |

## TikTok Tools

| Live tool | Purpose | Main arguments |
| --- | --- | --- |
| `tiktok_product_detail` | TikTok product detail | `productId`, `site` |
| `tiktok_product_video` | TikTok product sales videos | `productId`, `site`, `page` |
| `tiktok_product_video_author` | TikTok product sales creators | `productId`, `site` |
| `tiktok_product_trend` | TikTok product trend across sales, price, star, reviews, new videos, new authors | `productId`, `site` |
| `tiktok_similar_product` | TikTok similar products by product name | `productName`, `site`, `page` |
| `tiktok_author` | TikTok author detail, US only | `authorId` |
| `tiktok_category_report` | TikTok category data report | `nodeId`, `site` |
| `tiktok_category_name_search` | Search TikTok category markets by product name | `searchName`, `site` |
| `tikto_category_search_from_name` | Search TikTok categories by category name; live schema uses the typo-like `tikto` prefix | `name`, `site` |

## Utility Tools

| Live tool | Purpose | Main arguments |
| --- | --- | --- |
| `get_time` | Get current time from Sorftime MCP server | none |

## Site Argument Notes

Use the enum exposed by the selected tool.

Common Amazon product/category `amzSite` values include `US`, `GB`, `DE`, `FR`, `IN`, `CA`, `JP`, `ES`, `IT`, `MX`, `AE`, `AU`, `BR`, and `SA`. Some Amazon history or keyword tools expose a smaller set, so check the tool before passing `IN`, `AU`, or `BR`.

Common Amazon keyword `keywordSupportSite` values include `US`, `GB`, `DE`, `FR`, `CA`, `JP`, `ES`, `IT`, `MX`, `AE`, `AU`, `BR`, and `SA`.

Shopee `site` values include `VN`, `ID`, `SG`, `TH`, `MY`, `TW`, `PH`, and `BR`.

Temu `site` values include `US` and `EU`.

TikTok `site` values include `US`, `MY`, `PH`, `VN`, `TH`, `ID`, `GB`, and `JP`.

Do not pass unsupported sites even when another Sorftime tool accepts that marketplace.

## Workflow Guidance

For ASIN research:

1. Call `product_detail` or `product_report`.
2. Call `product_traffic_terms`.
3. Call `product_reviews` for VOC.
4. Call `product_trend` for product history.
5. Call `keyword_detail`, `keyword_trend`, `keyword_extends`, and `keyword_search_results` for demand and SERP validation.

For keyword research:

1. Call `keyword_list` or `keyword_list_from_history` for broad discovery when needed.
2. Call `keyword_detail`.
3. Call `keyword_trend`.
4. Call `keyword_extends`.
5. Call `keyword_search_results`.
6. Use `product_traffic_terms` and `competitor_product_keywords` only when an ASIN is available.

For category/market research:

1. Use `category_name_search`, `category_tree`, `category_search_from_product_name`, `category_search_from_top_node`, or `search_categories_broadly` to find node IDs.
2. Use `category_report` or `category_report_from_history` for Top100 products.
3. Use `category_trend` and `category_keywords` for market trend and keyword seeds.
4. Validate demand and competition with keyword/product tools.
5. Use marketplace-specific category tools for Shopee, Walmart, Temu, and TikTok when researching those platforms.
