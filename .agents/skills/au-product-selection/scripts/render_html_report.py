#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render AU product selection scorecard as an HTML decision dashboard."""
import argparse
import html
import json
from datetime import datetime
from pathlib import Path

ZH = {
    "title": "\u6fb3\u6d32\u7ad9\u8fc1\u79fb\u9009\u54c1\u51b3\u7b56\u770b\u677f",
    "priority_review": "\u91cd\u70b9\u4eba\u5de5\u5ba1\u6838",
    "extended_review": "\u6269\u5c55\u4eba\u5de5\u5ba1\u6838\u6e05\u5355",
    "asin": "ASIN",
    "keyword": "\u4ee3\u8868\u5173\u952e\u8bcd",
    "search_volume": "\u641c\u7d22\u91cf",
    "growth": "\u589e\u957f\u8d8b\u52bf",
    "trend_type": "\u8d8b\u52bf\u7c7b\u578b",
    "seasonality": "\u5b63\u8282\u6027",
    "au_window": "AU\u8fdb\u5165\u7a97\u53e3",
    "score": "\u603b\u5206",
    "discovery_score": "\u6269\u5c55\u53d1\u73b0\u5206",
    "decision": "\u51b3\u7b56",
    "review_tier": "\u5ba1\u6838\u5c42\u7ea7",
    "max_risk": "\u6700\u5927\u98ce\u9669",
    "source_missing": "\u6765\u6e90\u4e0d\u8db3",
    "no_hard_risk": "\u65e0\u660e\u663e\u786c\u6027\u6dd8\u6c70",
    "trend_missing": "\u8d8b\u52bf\u8bc1\u636e\u4e0d\u8db3",
    "score_breakdown": "\u8bc4\u5206\u62c6\u89e3",
    "market_demand": "\u5e02\u573a\u9700\u6c42",
    "competition": "\u7ade\u4e89\u5f3a\u5ea6",
    "profit": "\u5229\u6da6\u7a7a\u95f4",
    "au_fit": "\u6fb3\u6d32\u9002\u914d",
    "beginner_risk": "\u65b0\u624b\u98ce\u9669",
    "insight": "\u5173\u952e\u6d1e\u5bdf",
    "market_comp": "\u5e02\u573a\u4e0e\u7ade\u4e89",
    "monthly_sales": "\u6708\u9500\u91cf",
    "monthly_revenue": "\u6708\u9500\u552e\u989d",
    "brand_conc": "Top3\u54c1\u724c\u96c6\u4e2d\u5ea6",
    "click_conc": "\u70b9\u51fb\u96c6\u4e2d\u5ea6",
    "reviews": "\u8bc4\u5206\u6570",
    "seller_count": "\u5356\u5bb6\u6570",
    "variant_count": "\u53d8\u4f53\u6570",
    "discovery_notes": "\u53d1\u73b0\u7406\u7531",
    "profit_risk": "\u5229\u6da6\u4e0e\u98ce\u9669",
    "price": "\u552e\u4ef7",
    "cost": "\u6210\u672c",
    "margin": "\u6bdb\u5229\u7387",
    "return_rate": "\u9000\u8d27\u7387",
    "hard_exclusion": "\u786c\u6027\u6dd8\u6c70",
    "patent_compliance": "\u4e13\u5229/\u5408\u89c4",
    "keyword_detail": "\u5173\u952e\u8bcd\u8d8b\u52bf\u660e\u7ec6",
    "month": "\u6708\u4efd",
    "source": "\u6765\u6e90",
    "type": "\u673a\u4f1a\u7c7b\u578b",
    "core_source": "\u6838\u5fc3\u6765\u6e90",
    "enter": "\u4f18\u5148\u8fdb\u5165",
    "test": "\u53ef\u5c0f\u6279\u91cf\u6d4b\u8bd5",
    "watch": "\u89c2\u5bdf\u6216\u8865\u6570\u636e",
    "reject": "\u4e0d\u5efa\u8bae\u8fdb\u5165",
    "title_seeds": "\u6807\u9898\u79cd\u5b50\u8bcd",
    "verified_keywords": "\u5df2\u9a8c\u8bc1\u8d8b\u52bf\u8bcd",
    "trend_pending": "\u8d8b\u52bf\u5f85\u9a8c\u8bc1",
    "product_title": "\u4ea7\u54c1\u6807\u9898",
    "seasonality_notes": "\u5b63\u8282\u6027\u8bf4\u660e",
    "dedupe_note": "\u540cASIN\u591a\u5173\u952e\u8bcd\u5408\u5e76",
    "priority_insight": "\u91cd\u70b9\u4eba\u5de5\u5ba1\u6838\u5c55\u793a\u8d8b\u52bf\u4e0a\u5347/\u603b\u520670+\u7684\u9a8c\u8bc1\u673a\u4f1a\uff0c\u4ee5\u53ca\u6269\u5c55\u53d1\u73b0\u520680+\u4ee5\u4e0a\u3001\u975e\u670d\u88c5\u978b\u5305\u3001\u65e0\u786c\u6027\u6dd8\u6c70\u7684\u5f3a\u5546\u4e1a\u4fe1\u53f7ASIN\u3002\u7f3a\u8d8b\u52bf\u7684\u53d1\u73b0\u578b\u5019\u9009\u53ea\u80fd\u7528\u4e8e\u9ad8\u4f18\u5148\u7ea7\u8865\u8d8b\u52bf\u9a8c\u8bc1\uff0c\u4e0d\u80fd\u76f4\u63a5\u5224\u4e3a\u4f18\u5148\u8fdb\u5165\u3002",
    "extended_insight": "\u6269\u5c55\u4eba\u5de5\u5ba1\u6838\u6e05\u5355\u5c55\u793a\u91cd\u70b9\u4e4b\u5916\u3001\u6269\u5c55\u53d1\u73b0\u520675+\u3001\u975e\u670d\u88c5\u978b\u5305\u3001\u65e0\u786c\u6027\u6dd8\u6c70\u7684ASIN\u3002\u8fd9\u662f\u503c\u5f97\u8865\u8d8b\u52bf/\u8865\u6210\u672c/\u8865AU\u9a8c\u8bc1\u7684\u5019\u9009\u6c60\uff0c\u4e0d\u662f\u6700\u7ec8\u8fdb\u5165\u5efa\u8bae\u3002",
}

SEASONALITY_LABELS = {
    "evergreen": "\u5168\u5e74\u9700\u6c42",
    "seasonal": "\u5b63\u8282\u9700\u6c42",
    "event_driven": "\u8282\u65e5/\u4e8b\u4ef6\u9700\u6c42",
    "insufficient": "\u5b63\u8282\u8bc1\u636e\u4e0d\u8db3",
}


def esc(value):
    return html.escape("" if value is None else str(value))


def fmt_pct(value):
    if value is None:
        return "N/A"
    return f"{value * 100:.1f}%"


def fmt_num(value):
    if value is None:
        return "N/A"
    try:
        return f"{float(value):,.0f}"
    except (TypeError, ValueError):
        return esc(value)


def representative_keyword(candidate):
    verified = [x for x in candidate.get("verified_trend_keywords", []) if str(x).strip()]
    if verified:
        return str(verified[0]).strip()
    primary = candidate.get("primary_keyword")
    if primary:
        return str(primary).strip()
    seeds = [x for x in candidate.get("title_seed_keywords", []) if str(x).strip()]
    return str(seeds[0]).strip() if seeds else "N/A"


def asin(candidate):
    value = (candidate.get("identifiers") or {}).get("asin")
    return str(value).strip() if value not in (None, "") else "N/A"


def review_key(opp):
    cand = opp.get("candidate", {})
    candidate_asin = asin(cand)
    if candidate_asin != "N/A":
        return candidate_asin
    return f"N/A::{representative_keyword(cand).lower()}"


def review_priority(opp):
    cand = opp.get("candidate", {})
    trend_status = (opp.get("trend") or {}).get("trend_status")
    market = cand.get("market", {})
    search_volume = market.get("search_volume") or 0
    try:
        search_volume = float(search_volume)
    except (TypeError, ValueError):
        search_volume = 0
    return (
        2 if opp.get("review_tier") == "priority_trend_verified" else 1 if opp.get("review_tier") == "priority_discovery" else 0,
        1 if trend_status == "rising" else 0,
        float(opp.get("discovery_score") or 0),
        float(opp.get("total_score") or 0),
        search_volume,
    )


def is_priority_review(opp):
    if opp.get("hard_exclusion_flags"):
        return False
    if opp.get("review_tier") == "excluded" or "excluded_apparel" in (opp.get("discovery_flags") or []):
        return False
    if opp.get("review_tier") in ("priority_trend_verified", "priority_discovery"):
        return True
    return opp.get("total_score", 0) >= 70 or (opp.get("trend") or {}).get("trend_status") == "rising" or float(opp.get("discovery_score") or 0) >= 80


def is_extended_review(opp):
    if opp.get("hard_exclusion_flags") or is_priority_review(opp):
        return False
    if opp.get("review_tier") == "excluded" or "excluded_apparel" in (opp.get("discovery_flags") or []):
        return False
    if opp.get("review_tier") == "extended_discovery":
        return True
    return float(opp.get("discovery_score") or 0) >= 75


def dedupe_review_items(opportunities):
    grouped = {}
    for opp in opportunities:
        if opp.get("hard_exclusion_flags"):
            continue
        key = review_key(opp)
        bucket = grouped.setdefault(key, [])
        bucket.append(opp)
    deduped = []
    for key, bucket in grouped.items():
        bucket.sort(key=review_priority, reverse=True)
        best = dict(bucket[0])
        best["duplicate_keyword_count"] = len(bucket) - 1
        if len(bucket) > 1:
            best["duplicate_keywords"] = [representative_keyword(item.get("candidate", {})) for item in bucket[1:]]
        deduped.append(best)
    deduped.sort(key=review_priority, reverse=True)
    return deduped


def split_review_items(opportunities):
    review_items = dedupe_review_items(opportunities)
    priority = [opp for opp in review_items if is_priority_review(opp)]
    priority_keys = {review_key(opp) for opp in priority}
    extended = [
        opp
        for opp in review_items
        if review_key(opp) not in priority_keys and is_extended_review(opp)
    ]
    return priority, extended


def split_review_pools(priority_opportunities, extended_opportunities=None):
    priority_source = list(priority_opportunities)
    if extended_opportunities is not None:
        priority_source.extend(extended_opportunities)
    priority_pool = dedupe_review_items(priority_source)
    priority = [opp for opp in priority_pool if is_priority_review(opp)]
    priority_keys = {review_key(opp) for opp in priority}
    extended_source = priority_opportunities if extended_opportunities is None else extended_opportunities
    extended_pool = dedupe_review_items(extended_source)
    extended = [
        opp
        for opp in extended_pool
        if review_key(opp) not in priority_keys and is_extended_review(opp)
    ]
    return priority, extended


def evidence_text(candidate):
    refs = candidate.get("source_refs") or []
    parts = []
    for ref in refs[:3]:
        bits = [ref.get("source"), ref.get("tool") or ref.get("file"), ref.get("collected_at")]
        parts.append(" / ".join(str(x) for x in bits if x))
    return "; ".join(parts) or ZH["source_missing"]


def verdict_class(verdict):
    if verdict == ZH["enter"]:
        return "enter"
    if verdict == ZH["test"]:
        return "test"
    if verdict == ZH["watch"]:
        return "watch"
    return "reject"


def pill_list(items, empty):
    items = [str(x) for x in (items or []) if str(x).strip()]
    if not items:
        return f"<span class='muted'>{esc(empty)}</span>"
    return " ".join(f"<span class='tag'>{esc(x)}</span>" for x in items[:12])


def seasonality_label(opp):
    raw = (opp.get("seasonality") or {}).get("label") or "insufficient"
    return SEASONALITY_LABELS.get(raw, raw)


def trend_label(opp):
    cand = opp.get("candidate", {})
    trend = opp.get("trend", {})
    label = trend.get("trend_status") or "unknown"
    if label == "insufficient" and cand.get("title_seed_keywords") and not cand.get("verified_trend_keywords"):
        return ZH["trend_pending"]
    return label


def reviewable(opp):
    return is_priority_review(opp) or is_extended_review(opp)


def opportunity_row(rank, opp):
    cand = opp["candidate"]
    trend = opp.get("trend", {})
    market = cand.get("market", {})
    comp = cand.get("competition", {})
    profit = cand.get("profit", {})
    season = opp.get("seasonality", {})
    return f"""
<tr>
  <td>{rank}</td>
  <td><strong>{esc(asin(cand))}</strong></td>
  <td>{esc(representative_keyword(cand))}</td>
  <td>{fmt_num(market.get('search_volume'))}</td>
  <td>{opp.get('discovery_score', 'N/A')}</td>
  <td>{fmt_num(market.get('monthly_sales'))}</td>
  <td>{fmt_num(market.get('monthly_revenue'))}</td>
  <td>{fmt_pct(profit.get('gross_margin'))}</td>
  <td>{fmt_num(comp.get('review_count'))}</td>
  <td>{fmt_num(comp.get('seller_count'))}</td>
  <td>{fmt_num(comp.get('variant_count'))}</td>
  <td><small>3M {fmt_pct(trend.get('growth_3m'))}<br>6M {fmt_pct(trend.get('growth_6m'))}<br>12M {fmt_pct(trend.get('growth_12m'))}</small></td>
  <td>{esc(trend_label(opp))}</td>
  <td>{esc(seasonality_label(opp))}</td>
  <td>{esc(season.get('au_entry_window') or 'N/A')}</td>
  <td>{opp.get('total_score')}</td>
  <td><span class="pill {verdict_class(opp.get('verdict'))}">{esc(opp.get('verdict'))}</span></td>
  <td>{esc(opp.get('review_tier') or 'N/A')}</td>
  <td>{esc('; '.join(opp.get('discovery_notes') or []))}</td>
  <td>{esc(', '.join(opp.get('hard_exclusion_flags') or []) or ZH['no_hard_risk'])}</td>
</tr>"""


def compact_row(rank, opp):
    cand = opp["candidate"]
    trend = opp.get("trend", {})
    market = cand.get("market", {})
    comp = cand.get("competition", {})
    profit = cand.get("profit", {})
    season = opp.get("seasonality", {})
    return f"""
<tr>
  <td>{rank}</td>
  <td>{esc(asin(cand))}</td>
  <td>{esc(representative_keyword(cand))}</td>
  <td>{opp.get('discovery_score', 'N/A')}</td>
  <td>{fmt_num(market.get('monthly_sales'))}</td>
  <td>{fmt_num(market.get('monthly_revenue'))}</td>
  <td>{fmt_pct(profit.get('gross_margin'))}</td>
  <td>{fmt_num(comp.get('review_count'))}</td>
  <td>{fmt_num(comp.get('seller_count'))}</td>
  <td>{fmt_num(comp.get('variant_count'))}</td>
  <td>3M {fmt_pct(trend.get('growth_3m'))} / 6M {fmt_pct(trend.get('growth_6m'))} / 12M {fmt_pct(trend.get('growth_12m'))}</td>
  <td>{esc(seasonality_label(opp))}</td>
  <td>{esc(season.get('au_entry_window') or 'N/A')}</td>
  <td>{esc(opp.get('verdict'))}</td>
  <td>{esc('; '.join(opp.get('discovery_notes') or []))}</td>
</tr>"""


def detail_section(rank, opp):
    cand = opp["candidate"]
    trend = opp.get("trend", {})
    scores = opp.get("scores", {})
    market = cand.get("market", {})
    comp = cand.get("competition", {})
    profit = cand.get("profit", {})
    season = opp.get("seasonality", {})
    keyword_rows = "".join(
        f"<tr><td>{esc(p.get('keyword'))}</td><td>{esc(p.get('month'))}</td><td>{fmt_num(p.get('search_volume'))}</td><td>{esc(p.get('source'))}</td></tr>"
        for p in (cand.get("keyword_history") or [])[-12:]
    ) or f"<tr><td colspan='4'>{ZH['trend_missing']}</td></tr>"
    duplicate_note = ""
    if opp.get("duplicate_keyword_count"):
        duplicate_note = f"<p class=\"insight\"><b>{ZH['dedupe_note']}:</b> {opp.get('duplicate_keyword_count')} additional keyword opportunities for this ASIN were hidden from the manual-review lists. Other keywords: {esc(', '.join(opp.get('duplicate_keywords') or []))}</p>"
    return f"""
<section class="card">
  <h2>{rank}. {esc(asin(cand))} / {esc(representative_keyword(cand))}</h2>
  <p class="muted"><b>{ZH['product_title']}:</b> {esc(cand.get('candidate'))}</p>
  <div class="grid">
    <div><b>{ZH['score']}</b><span>{opp.get('total_score')}</span></div>
    <div><b>{ZH['discovery_score']}</b><span>{opp.get('discovery_score', 'N/A')}</span></div>
    <div><b>{ZH['decision']}</b><span>{esc(opp.get('verdict'))}</span></div>
    <div><b>{ZH['review_tier']}</b><span>{esc(opp.get('review_tier') or 'N/A')}</span></div>
    <div><b>{ZH['trend_type']}</b><span>{esc(trend_label(opp))}</span></div>
    <div><b>{ZH['seasonality']}</b><span>{esc(seasonality_label(opp))}</span></div>
  </div>
  {duplicate_note}
  <p class="insight"><b>{ZH['discovery_notes']}:</b> {esc('; '.join(opp.get('discovery_notes') or []) or 'N/A')}</p>
  <p class="insight"><b>{ZH['seasonality_notes']}:</b> {esc(season.get('notes') or 'N/A')} AU window: {esc(season.get('au_entry_window') or 'N/A')}</p>
  <h3>{ZH['title_seeds']} / {ZH['verified_keywords']}</h3>
  <p>{pill_list(cand.get('title_seed_keywords'), 'No title seeds')}</p>
  <p>{pill_list(cand.get('verified_trend_keywords'), 'No verified trend keywords')}</p>
  <h3>{ZH['score_breakdown']}</h3>
  <table><tr><th>{ZH['market_demand']}</th><th>{ZH['competition']}</th><th>{ZH['profit']}</th><th>{ZH['au_fit']}</th><th>{ZH['beginner_risk']}</th></tr>
  <tr><td>{scores.get('market_demand')}</td><td>{scores.get('competition_strength')}</td><td>{scores.get('profit_space')}</td><td>{scores.get('au_migration_fit')}</td><td>{scores.get('beginner_fit_risk')}</td></tr></table>
  <p class="insight"><b>{ZH['insight']}:</b> Keyword growth outranks absolute volume. Current 3M/6M/12M growth: {fmt_pct(trend.get('growth_3m'))}, {fmt_pct(trend.get('growth_6m'))}, {fmt_pct(trend.get('growth_12m'))}. Source: {esc(evidence_text(cand))}</p>
  <h3>{ZH['market_comp']}</h3>
  <table><tr><th>{ZH['monthly_sales']}</th><th>{ZH['search_volume']}</th><th>{ZH['brand_conc']}</th><th>{ZH['click_conc']}</th><th>SPR</th><th>CPC</th><th>{ZH['reviews']}</th></tr>
  <tr><td>{fmt_num(market.get('monthly_sales'))}</td><td>{fmt_num(market.get('search_volume'))}</td><td>{fmt_pct(comp.get('top3_brand_concentration'))}</td><td>{fmt_pct(comp.get('click_concentration'))}</td><td>{fmt_num(comp.get('spr'))}</td><td>{esc(comp.get('cpc'))}</td><td>{fmt_num(comp.get('review_count'))}</td></tr></table>
  <h3>{ZH['profit_risk']}</h3>
  <table><tr><th>{ZH['price']}</th><th>{ZH['cost']}</th><th>FBA</th><th>{ZH['margin']}</th><th>{ZH['return_rate']}</th><th>{ZH['hard_exclusion']}</th><th>{ZH['patent_compliance']}</th></tr>
  <tr><td>{esc(profit.get('price'))}</td><td>{esc(profit.get('cost'))}</td><td>{esc(profit.get('fba_fee'))}</td><td>{fmt_pct(profit.get('gross_margin'))}</td><td>{fmt_pct(profit.get('return_rate'))}</td><td>{esc(', '.join(opp.get('hard_exclusion_flags') or []) or 'None')}</td><td>{esc(cand.get('risk', {}).get('patent_risk') or cand.get('migration', {}).get('compliance_risk'))}</td></tr></table>
  <h3>{ZH['keyword_detail']}</h3>
  <table><tr><th>{ZH['keyword']}</th><th>{ZH['month']}</th><th>{ZH['search_volume']}</th><th>{ZH['source']}</th></tr>{keyword_rows}</table>
</section>"""


def render(scorecard, extended_scorecard=None):
    opportunities = scorecard.get("opportunities", [])
    extended_opportunities = None
    if extended_scorecard is not None:
        extended_opportunities = extended_scorecard.get("opportunities", [])
    priority, extended = split_review_pools(opportunities, extended_opportunities)
    priority_rows = "".join(opportunity_row(rank, opp) for rank, opp in enumerate(priority, start=1))
    if not priority_rows:
        priority_rows = "<tr><td colspan='20'>No opportunities meet the manual-review threshold.</td></tr>"
    extended_rows = "".join(compact_row(rank, opp) for rank, opp in enumerate(extended, start=1))
    if not extended_rows:
        extended_rows = "<tr><td colspan='15'>No additional discovery candidates beyond the priority list.</td></tr>"
    details = "".join(detail_section(rank, opp) for rank, opp in enumerate(priority, start=1))
    meta = scorecard.get("metadata", {})
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AU Product Selection</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;margin:0;background:#f6f7f9;color:#17202a}} .wrap{{max-width:1280px;margin:auto;padding:28px}} h1{{font-size:28px;margin:0 0 8px}} .sub,.muted{{color:#64748b}} .sub{{margin-bottom:24px}} .card{{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:20px;margin:18px 0;box-shadow:0 1px 2px rgba(0,0,0,.04)}} table{{width:100%;border-collapse:collapse;margin:12px 0}} th,td{{border-bottom:1px solid #e5e7eb;padding:10px;text-align:left;vertical-align:top}} th{{background:#f8fafc;color:#475569}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}} .grid div{{background:#f8fafc;border-radius:8px;padding:12px}} .grid b{{display:block;color:#64748b;font-size:12px}} .grid span{{font-size:21px;font-weight:700}} .pill,.tag{{display:inline-block;border-radius:999px;padding:4px 10px;background:#e2e8f0;margin:2px}} .enter{{background:#dcfce7;color:#166534}} .test{{background:#fef9c3;color:#854d0e}} .watch{{background:#e0f2fe;color:#075985}} .reject{{background:#fee2e2;color:#991b1b}} .insight{{background:#eff6ff;border-left:4px solid #2563eb;padding:10px 12px;color:#1e3a8a}} small{{color:#64748b}} @media(max-width:760px){{.wrap{{padding:14px}} table{{font-size:13px}}}}
</style></head><body><main class="wrap">
<h1>{ZH['title']}</h1><div class="sub">Topic: {esc(meta.get('topic'))} | Mode: {esc(meta.get('input_mode'))} | Source: {esc(meta.get('source_site'))} -> Target: {esc(meta.get('target_site'))} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
<section class="card"><h2>{ZH['priority_review']}</h2><table><tr><th>#</th><th>{ZH['asin']}</th><th>{ZH['keyword']}</th><th>{ZH['search_volume']}</th><th>{ZH['discovery_score']}</th><th>{ZH['monthly_sales']}</th><th>{ZH['monthly_revenue']}</th><th>{ZH['margin']}</th><th>{ZH['reviews']}</th><th>{ZH['seller_count']}</th><th>{ZH['variant_count']}</th><th>{ZH['growth']}</th><th>{ZH['trend_type']}</th><th>{ZH['seasonality']}</th><th>{ZH['au_window']}</th><th>{ZH['score']}</th><th>{ZH['decision']}</th><th>{ZH['review_tier']}</th><th>{ZH['discovery_notes']}</th><th>{ZH['max_risk']}</th></tr>{priority_rows}</table><p class="insight"><b>{ZH['insight']}:</b> {ZH['priority_insight']}</p></section>
<section class="card"><h2>{ZH['extended_review']}</h2><table><tr><th>#</th><th>{ZH['asin']}</th><th>{ZH['keyword']}</th><th>{ZH['discovery_score']}</th><th>{ZH['monthly_sales']}</th><th>{ZH['monthly_revenue']}</th><th>{ZH['margin']}</th><th>{ZH['reviews']}</th><th>{ZH['seller_count']}</th><th>{ZH['variant_count']}</th><th>{ZH['growth']}</th><th>{ZH['seasonality']}</th><th>{ZH['au_window']}</th><th>{ZH['decision']}</th><th>{ZH['discovery_notes']}</th></tr>{extended_rows}</table><p class="insight"><b>{ZH['insight']}:</b> {ZH['extended_insight']}</p></section>
{details}
</main></body></html>"""


def main():
    parser = argparse.ArgumentParser(description="Render AU product selection HTML dashboard")
    parser.add_argument("scorecard_json")
    parser.add_argument("--extended-scorecard", help="Optional full scorecard used only for extended manual-review items")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()
    path = Path(args.scorecard_json)
    scorecard = json.loads(path.read_text(encoding="utf-8"))
    extended_scorecard = None
    if args.extended_scorecard:
        extended_scorecard = json.loads(Path(args.extended_scorecard).read_text(encoding="utf-8"))
    output = Path(args.output) if args.output else path.with_name("index.html")
    html_text = render(scorecard, extended_scorecard).encode("ascii", "xmlcharrefreplace").decode("ascii")
    output.write_text(html_text, encoding="ascii")
    print(f"Rendered HTML -> {output}")


if __name__ == "__main__":
    main()
