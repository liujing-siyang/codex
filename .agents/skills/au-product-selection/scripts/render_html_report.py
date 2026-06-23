#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render AU product selection scorecard as an HTML decision dashboard."""
import argparse
import html
import json
from datetime import datetime
from pathlib import Path

ZH = {
    "title": "???????????",
    "priority_review": "??????",
    "extended_review": "????????",
    "asin": "ASIN",
    "keyword": "?????",
    "search_volume": "???",
    "growth": "????",
    "trend_type": "????",
    "seasonality": "???",
    "au_window": "AU????",
    "score": "??",
    "decision": "??",
    "max_risk": "????",
    "source_missing": "????",
    "no_hard_risk": "???????",
    "trend_missing": "??????",
    "score_breakdown": "????",
    "market_demand": "????",
    "competition": "????",
    "profit": "????",
    "au_fit": "????",
    "beginner_risk": "????",
    "insight": "????",
    "market_comp": "?????",
    "monthly_sales": "???",
    "brand_conc": "Top3?????",
    "click_conc": "?????",
    "reviews": "???",
    "profit_risk": "?????",
    "price": "??",
    "cost": "??",
    "margin": "???",
    "return_rate": "???",
    "hard_exclusion": "????",
    "patent_compliance": "??/??",
    "keyword_detail": "???????",
    "month": "??",
    "source": "??",
    "type": "????",
    "core_source": "????",
    "enter": "????",
    "test": "??????",
    "watch": "??????",
    "reject": "?????",
    "title_seeds": "?????",
    "verified_keywords": "??????",
    "trend_pending": "?????",
    "product_title": "????",
    "seasonality_notes": "?????",
}

SEASONALITY_LABELS = {
    "evergreen": "????",
    "seasonal": "????",
    "event_driven": "??/????",
    "insufficient": "??????",
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
    return not opp.get("hard_exclusion_flags") and (opp.get("total_score", 0) >= 70 or (opp.get("trend") or {}).get("trend_status") == "rising")


def opportunity_row(rank, opp):
    cand = opp["candidate"]
    trend = opp.get("trend", {})
    market = cand.get("market", {})
    season = opp.get("seasonality", {})
    return f"""
<tr>
  <td>{rank}</td>
  <td><strong>{esc(asin(cand))}</strong></td>
  <td>{esc(representative_keyword(cand))}</td>
  <td>{fmt_num(market.get('search_volume'))}</td>
  <td><small>3M {fmt_pct(trend.get('growth_3m'))}<br>6M {fmt_pct(trend.get('growth_6m'))}<br>12M {fmt_pct(trend.get('growth_12m'))}</small></td>
  <td>{esc(trend_label(opp))}</td>
  <td>{esc(seasonality_label(opp))}</td>
  <td>{esc(season.get('au_entry_window') or 'N/A')}</td>
  <td>{opp.get('total_score')}</td>
  <td><span class="pill {verdict_class(opp.get('verdict'))}">{esc(opp.get('verdict'))}</span></td>
  <td>{esc(', '.join(opp.get('hard_exclusion_flags') or []) or ZH['no_hard_risk'])}</td>
</tr>"""


def compact_row(rank, opp):
    cand = opp["candidate"]
    trend = opp.get("trend", {})
    market = cand.get("market", {})
    season = opp.get("seasonality", {})
    return f"""
<tr>
  <td>{rank}</td>
  <td>{esc(asin(cand))}</td>
  <td>{esc(representative_keyword(cand))}</td>
  <td>{fmt_num(market.get('search_volume'))}</td>
  <td>3M {fmt_pct(trend.get('growth_3m'))} / 6M {fmt_pct(trend.get('growth_6m'))} / 12M {fmt_pct(trend.get('growth_12m'))}</td>
  <td>{esc(seasonality_label(opp))}</td>
  <td>{esc(season.get('au_entry_window') or 'N/A')}</td>
  <td>{esc(opp.get('verdict'))}</td>
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
    return f"""
<section class="card">
  <h2>{rank}. {esc(asin(cand))} / {esc(representative_keyword(cand))}</h2>
  <p class="muted"><b>{ZH['product_title']}:</b> {esc(cand.get('candidate'))}</p>
  <div class="grid">
    <div><b>{ZH['score']}</b><span>{opp.get('total_score')}</span></div>
    <div><b>{ZH['decision']}</b><span>{esc(opp.get('verdict'))}</span></div>
    <div><b>{ZH['trend_type']}</b><span>{esc(trend_label(opp))}</span></div>
    <div><b>{ZH['seasonality']}</b><span>{esc(seasonality_label(opp))}</span></div>
  </div>
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


def render(scorecard):
    opportunities = scorecard.get("opportunities", [])
    review_items = [opp for opp in opportunities if reviewable(opp)]
    priority = review_items[:10]
    extended = review_items[10:]
    priority_rows = "".join(opportunity_row(rank, opp) for rank, opp in enumerate(priority, start=1))
    if not priority_rows:
        priority_rows = "<tr><td colspan='11'>No opportunities meet the manual-review threshold.</td></tr>"
    extended_rows = "".join(compact_row(rank, opp) for rank, opp in enumerate(extended, start=11))
    if not extended_rows:
        extended_rows = "<tr><td colspan='8'>No additional reviewable opportunities beyond the priority list.</td></tr>"
    details = "".join(detail_section(rank, opp) for rank, opp in enumerate(priority, start=1))
    meta = scorecard.get("metadata", {})
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AU Product Selection</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;margin:0;background:#f6f7f9;color:#17202a}} .wrap{{max-width:1280px;margin:auto;padding:28px}} h1{{font-size:28px;margin:0 0 8px}} .sub,.muted{{color:#64748b}} .sub{{margin-bottom:24px}} .card{{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:20px;margin:18px 0;box-shadow:0 1px 2px rgba(0,0,0,.04)}} table{{width:100%;border-collapse:collapse;margin:12px 0}} th,td{{border-bottom:1px solid #e5e7eb;padding:10px;text-align:left;vertical-align:top}} th{{background:#f8fafc;color:#475569}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}} .grid div{{background:#f8fafc;border-radius:8px;padding:12px}} .grid b{{display:block;color:#64748b;font-size:12px}} .grid span{{font-size:21px;font-weight:700}} .pill,.tag{{display:inline-block;border-radius:999px;padding:4px 10px;background:#e2e8f0;margin:2px}} .enter{{background:#dcfce7;color:#166534}} .test{{background:#fef9c3;color:#854d0e}} .watch{{background:#e0f2fe;color:#075985}} .reject{{background:#fee2e2;color:#991b1b}} .insight{{background:#eff6ff;border-left:4px solid #2563eb;padding:10px 12px;color:#1e3a8a}} small{{color:#64748b}} @media(max-width:760px){{.wrap{{padding:14px}} table{{font-size:13px}}}}
</style></head><body><main class="wrap">
<h1>{ZH['title']}</h1><div class="sub">Topic: {esc(meta.get('topic'))} | Mode: {esc(meta.get('input_mode'))} | Source: {esc(meta.get('source_site'))} -> Target: {esc(meta.get('target_site'))} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
<section class="card"><h2>{ZH['priority_review']}</h2><table><tr><th>#</th><th>{ZH['asin']}</th><th>{ZH['keyword']}</th><th>{ZH['search_volume']}</th><th>{ZH['growth']}</th><th>{ZH['trend_type']}</th><th>{ZH['seasonality']}</th><th>{ZH['au_window']}</th><th>{ZH['score']}</th><th>{ZH['decision']}</th><th>{ZH['max_risk']}</th></tr>{priority_rows}</table><p class="insight"><b>{ZH['insight']}:</b> Manual-review threshold is total score >= 70 or rising trend, excluding hard eliminations. US seasonal demand is shifted by about 6 months for AU weather/season planning; event-driven demand requires manual cultural validation.</p></section>
<section class="card"><h2>{ZH['extended_review']}</h2><table><tr><th>#</th><th>{ZH['asin']}</th><th>{ZH['keyword']}</th><th>{ZH['search_volume']}</th><th>{ZH['growth']}</th><th>{ZH['seasonality']}</th><th>{ZH['au_window']}</th><th>{ZH['decision']}</th></tr>{extended_rows}</table></section>
{details}
</main></body></html>"""


def main():
    parser = argparse.ArgumentParser(description="Render AU product selection HTML dashboard")
    parser.add_argument("scorecard_json")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()
    path = Path(args.scorecard_json)
    scorecard = json.loads(path.read_text(encoding="utf-8"))
    output = Path(args.output) if args.output else path.with_name("index.html")
    output.write_text(render(scorecard), encoding="utf-8")
    print(f"Rendered HTML -> {output}")


if __name__ == "__main__":
    main()
