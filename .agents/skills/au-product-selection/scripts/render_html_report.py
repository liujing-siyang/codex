#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render AU product selection scorecard as an HTML decision dashboard."""
import argparse
import html
import json
from datetime import datetime
from pathlib import Path

ZH = {
    "source_missing": "\u6765\u6e90\u4e0d\u8db3",
    "no_hard_risk": "\u65e0\u660e\u663e\u786c\u6027\u6dd8\u6c70",
    "trend_missing": "\u8d8b\u52bf\u8bc1\u636e\u4e0d\u8db3",
    "score": "\u603b\u5206",
    "decision": "\u51b3\u7b56",
    "trend": "\u8d8b\u52bf",
    "au_label": "AU\u6807\u7b7e",
    "migration": "\u8fc1\u79fb",
    "score_breakdown": "\u8bc4\u5206\u62c6\u89e3",
    "market_demand": "\u5e02\u573a\u9700\u6c42",
    "competition": "\u7ade\u4e89\u5f3a\u5ea6",
    "profit": "\u5229\u6da6\u7a7a\u95f4",
    "au_fit": "\u6fb3\u6d32\u9002\u914d",
    "beginner_risk": "\u65b0\u624b\u98ce\u9669",
    "insight": "\u5173\u952e\u6d1e\u5bdf",
    "market_comp": "\u5e02\u573a\u4e0e\u7ade\u4e89",
    "monthly_sales": "\u6708\u9500\u91cf",
    "search_volume": "\u641c\u7d22\u91cf",
    "brand_conc": "Top3\u54c1\u724c\u96c6\u4e2d\u5ea6",
    "click_conc": "\u70b9\u51fb\u96c6\u4e2d\u5ea6",
    "reviews": "\u8bc4\u5206\u6570",
    "profit_risk": "\u5229\u6da6\u4e0e\u98ce\u9669",
    "price": "\u552e\u4ef7",
    "cost": "\u6210\u672c",
    "margin": "\u6bdb\u5229\u7387",
    "return_rate": "\u9000\u8d27\u7387",
    "hard_exclusion": "\u786c\u6027\u6dd8\u6c70",
    "patent_compliance": "\u4e13\u5229/\u5408\u89c4",
    "keyword_detail": "\u5173\u952e\u8bcd\u8d8b\u52bf\u660e\u7ec6",
    "keyword": "\u5173\u952e\u8bcd",
    "month": "\u6708\u4efd",
    "source": "\u6765\u6e90",
    "title": "\u6fb3\u6d32\u7ad9\u8fc1\u79fb\u9009\u54c1\u51b3\u7b56\u770b\u677f",
    "top10": "Top 10\u673a\u4f1a",
    "candidate_keyword": "\u5019\u9009\u4ea7\u54c1/\u5173\u952e\u8bcd",
    "type": "\u673a\u4f1a\u7c7b\u578b",
    "keyword_trend": "\u5173\u952e\u8bcd\u8d8b\u52bf",
    "core_source": "\u6838\u5fc3\u6765\u6e90",
    "max_risk": "\u6700\u5927\u98ce\u9669",
    "enter": "\u4f18\u5148\u8fdb\u5165",
    "test": "\u53ef\u5c0f\u6279\u91cf\u6d4b\u8bd5",
    "watch": "\u89c2\u5bdf\u6216\u8865\u6570\u636e",
    "reject": "\u4e0d\u5efa\u8bae\u8fdb\u5165",
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


def evidence_text(candidate):
    refs = candidate.get("source_refs") or []
    parts = []
    for ref in refs[:3]:
        bits = [ref.get("source"), ref.get("file"), ref.get("collected_at")]
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


def render(scorecard):
    rows = []
    details = []
    for rank, opp in enumerate(scorecard.get("opportunities", [])[:10], start=1):
        cand = opp["candidate"]
        trend = opp.get("trend", {})
        verdict = opp.get("verdict")
        rows.append(f"""
<tr>
  <td>{rank}</td>
  <td><strong>{esc(cand.get('candidate'))}</strong><br><small>{esc(cand.get('primary_keyword'))}</small></td>
  <td>{opp.get('total_score')}</td>
  <td><span class="pill {verdict_class(verdict)}">{esc(verdict)}</span></td>
  <td>{esc(opp.get('opportunity_type'))}</td>
  <td>{esc(trend.get('trend_status'))}<br><small>3M {fmt_pct(trend.get('growth_3m'))} / 6M {fmt_pct(trend.get('growth_6m'))} / 12M {fmt_pct(trend.get('growth_12m'))}</small></td>
  <td>{esc(evidence_text(cand))}</td>
  <td>{esc(', '.join(opp.get('hard_exclusion_flags') or []) or ZH['no_hard_risk'])}</td>
</tr>""")
        scores = opp.get("scores", {})
        market = cand.get("market", {})
        comp = cand.get("competition", {})
        profit = cand.get("profit", {})
        keyword_rows = "".join(
            f"<tr><td>{esc(p.get('keyword'))}</td><td>{esc(p.get('month'))}</td><td>{fmt_num(p.get('search_volume'))}</td><td>{esc(p.get('source'))}</td></tr>"
            for p in (cand.get("keyword_history") or [])[-12:]
        ) or f"<tr><td colspan='4'>{ZH['trend_missing']}</td></tr>"
        details.append(f"""
<section class="card">
  <h2>{rank}. {esc(cand.get('candidate'))}</h2>
  <div class="grid">
    <div><b>{ZH['score']}</b><span>{opp.get('total_score')}</span></div>
    <div><b>{ZH['decision']}</b><span>{esc(verdict)}</span></div>
    <div><b>{ZH['trend']}</b><span>{esc(trend.get('trend_status'))}</span></div>
    <div><b>{ZH['au_label']}</b><span>{esc(cand.get('target_site', 'AU'))}{ZH['migration']}</span></div>
  </div>
  <h3>{ZH['score_breakdown']}</h3>
  <table><tr><th>{ZH['market_demand']}</th><th>{ZH['competition']}</th><th>{ZH['profit']}</th><th>{ZH['au_fit']}</th><th>{ZH['beginner_risk']}</th></tr>
  <tr><td>{scores.get('market_demand')}</td><td>{scores.get('competition_strength')}</td><td>{scores.get('profit_space')}</td><td>{scores.get('au_migration_fit')}</td><td>{scores.get('beginner_fit_risk')}</td></tr></table>
  <p class="insight"><b>{ZH['insight']}:</b> Keyword growth outranks absolute volume. Current 3M/6M/12M growth: {fmt_pct(trend.get('growth_3m'))}, {fmt_pct(trend.get('growth_6m'))}, {fmt_pct(trend.get('growth_12m'))}. Source: {esc(evidence_text(cand))}</p>
  <h3>{ZH['market_comp']}</h3>
  <table><tr><th>{ZH['monthly_sales']}</th><th>{ZH['search_volume']}</th><th>{ZH['brand_conc']}</th><th>{ZH['click_conc']}</th><th>SPR</th><th>CPC</th><th>{ZH['reviews']}</th></tr>
  <tr><td>{fmt_num(market.get('monthly_sales'))}</td><td>{fmt_num(market.get('search_volume'))}</td><td>{fmt_pct(comp.get('top3_brand_concentration'))}</td><td>{fmt_pct(comp.get('click_concentration'))}</td><td>{fmt_num(comp.get('spr'))}</td><td>{esc(comp.get('cpc'))}</td><td>{fmt_num(comp.get('review_count'))}</td></tr></table>
  <p class="insight"><b>{ZH['insight']}:</b> Judge competition through concentration, review barriers, SPR, and CPC together.</p>
  <h3>{ZH['profit_risk']}</h3>
  <table><tr><th>{ZH['price']}</th><th>{ZH['cost']}</th><th>{ZH['margin']}</th><th>{ZH['return_rate']}</th><th>{ZH['hard_exclusion']}</th><th>{ZH['patent_compliance']}</th></tr>
  <tr><td>{esc(profit.get('price'))}</td><td>{esc(profit.get('cost'))}</td><td>{fmt_pct(profit.get('gross_margin'))}</td><td>{fmt_pct(profit.get('return_rate'))}</td><td>{esc(', '.join(opp.get('hard_exclusion_flags') or []) or 'None')}</td><td>{esc(cand.get('risk', {}).get('patent_risk') or cand.get('migration', {}).get('compliance_risk'))}</td></tr></table>
  <h3>{ZH['keyword_detail']}</h3>
  <table><tr><th>{ZH['keyword']}</th><th>{ZH['month']}</th><th>{ZH['search_volume']}</th><th>{ZH['source']}</th></tr>{keyword_rows}</table>
</section>""")
    meta = scorecard.get("metadata", {})
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AU Product Selection</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;margin:0;background:#f6f7f9;color:#17202a}} .wrap{{max-width:1200px;margin:auto;padding:28px}} h1{{font-size:28px;margin:0 0 8px}} .sub{{color:#64748b;margin-bottom:24px}} .card{{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:20px;margin:18px 0;box-shadow:0 1px 2px rgba(0,0,0,.04)}} table{{width:100%;border-collapse:collapse;margin:12px 0}} th,td{{border-bottom:1px solid #e5e7eb;padding:10px;text-align:left;vertical-align:top}} th{{background:#f8fafc;color:#475569}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}} .grid div{{background:#f8fafc;border-radius:8px;padding:12px}} .grid b{{display:block;color:#64748b;font-size:12px}} .grid span{{font-size:22px;font-weight:700}} .pill{{display:inline-block;border-radius:999px;padding:4px 10px;background:#e2e8f0}} .enter{{background:#dcfce7;color:#166534}} .test{{background:#fef9c3;color:#854d0e}} .watch{{background:#e0f2fe;color:#075985}} .reject{{background:#fee2e2;color:#991b1b}} .insight{{background:#eff6ff;border-left:4px solid #2563eb;padding:10px 12px;color:#1e3a8a}} small{{color:#64748b}} @media(max-width:760px){{.wrap{{padding:14px}} table{{font-size:13px}}}}
</style></head><body><main class="wrap">
<h1>{ZH['title']}</h1><div class="sub">Topic: {esc(meta.get('topic'))} | Source: {esc(meta.get('source_site'))} -> Target: {esc(meta.get('target_site'))} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
<section class="card"><h2>{ZH['top10']}</h2><table><tr><th>#</th><th>{ZH['candidate_keyword']}</th><th>{ZH['score']}</th><th>{ZH['decision']}</th><th>{ZH['type']}</th><th>{ZH['keyword_trend']}</th><th>{ZH['core_source']}</th><th>{ZH['max_risk']}</th></tr>{''.join(rows)}</table><p class="insight"><b>{ZH['insight']}:</b> Ranking prioritizes verified rising keyword trends. High-volume candidates with falling or insufficient trend evidence are not marked as {ZH['enter']}.</p></section>
{''.join(details)}
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
