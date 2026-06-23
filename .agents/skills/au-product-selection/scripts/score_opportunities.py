#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Score AU migration opportunities with keyword growth as a hard gate."""
import argparse
import json
from pathlib import Path

ZH = {
    "enter": "\u4f18\u5148\u8fdb\u5165",
    "test": "\u53ef\u5c0f\u6279\u91cf\u6d4b\u8bd5",
    "watch": "\u89c2\u5bdf\u6216\u8865\u6570\u636e",
    "reject": "\u4e0d\u5efa\u8bae\u8fdb\u5165",
    "hp_big_low": "\u9ad8\u5229\u6da6 + \u5927\u5e02\u573a + \u5c0f\u7ade\u4e89",
    "hp_small_low": "\u9ad8\u5229\u6da6 + \u5c0f\u5e02\u573a + \u5c0f\u7ade\u4e89",
    "lp_big_low": "\u4f4e\u5229\u6da6 + \u5927\u5e02\u573a + \u5c0f\u7ade\u4e89",
    "non_priority": "\u975e\u4f18\u5148\u673a\u4f1a",
}
FORBIDDEN_TERMS = [
    "liquid", "\u6db2\u4f53", "supplement", "\u4fdd\u5065", "medical", "\u533b\u7597",
    "medicine", "\u836f", "food", "\u98df\u54c1", "\u6613\u71c3", "weapon", "\u5200", "cbd",
]


def val(obj, *keys, default=0):
    cur = obj
    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return default if cur is None else cur


def pct(value):
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value / 100 if value > 1 else value


def growth(history, months):
    points = sorted([p for p in history if p.get("search_volume") is not None], key=lambda p: p.get("month", ""))
    if len(points) <= months:
        return None
    old = float(points[-months-1]["search_volume"])
    new = float(points[-1]["search_volume"])
    if old <= 0:
        return None
    return (new - old) / old


def trend_metrics(candidate):
    history = candidate.get("keyword_history") or []
    g3, g6, g12 = growth(history, 3), growth(history, 6), growth(history, 12)
    if len(history) < 4:
        status = "insufficient"
    elif g3 is not None and g3 > 0.08 and (g6 is None or g6 > -0.05) and (g12 is None or g12 > -0.10):
        status = "rising"
    elif any(g is not None and g < -0.05 for g in (g3, g6, g12)):
        status = "falling"
    else:
        status = "flat"
    return {"growth_3m": g3, "growth_6m": g6, "growth_12m": g12, "trend_status": status, "history_points": len(history)}


def market_score(candidate, trend):
    search = val(candidate, "market", "search_volume", default=0) or 0
    sales = val(candidate, "market", "monthly_sales", default=0) or 0
    new_share = pct(val(candidate, "market", "new_product_sales_share", default=0)) or 0
    growth_score = 0
    g3 = trend.get("growth_3m")
    if trend["trend_status"] == "rising":
        growth_score = 14 if (g3 or 0) >= 0.25 else 11
    elif trend["trend_status"] == "flat":
        growth_score = 5
    elif trend["trend_status"] == "falling":
        growth_score = 0
    search_score = min(6, search / 25000 * 6) if search else 0
    sales_score = min(6, sales / 150000 * 6) if sales else 0
    new_score = min(4, new_share / 0.15 * 4) if new_share else 0
    return round(min(30, growth_score + search_score + sales_score + new_score), 2)


def competition_score(candidate):
    comp = candidate.get("competition", {})
    concentrations = [pct(comp.get(k)) for k in ("top3_product_concentration", "top3_brand_concentration", "top3_seller_concentration", "click_concentration", "conversion_concentration")]
    concentrations = [x for x in concentrations if x is not None]
    avg_conc = sum(concentrations) / len(concentrations) if concentrations else None
    review_count = comp.get("review_count")
    cpc = comp.get("cpc")
    spr = comp.get("spr")
    amazon_share = pct(comp.get("amazon_owned_share")) or 0
    score = 30
    if avg_conc is not None:
        score -= max(0, (avg_conc - 0.25) * 35)
    if review_count:
        score -= min(7, float(review_count) / 2500 * 7)
    if cpc:
        score -= min(5, float(cpc) / 3 * 5)
    if spr:
        score -= min(5, float(spr) / 120 * 5)
    score -= min(5, amazon_share / 0.30 * 5)
    return round(max(0, min(30, score)), 2)


def profit_score(candidate):
    profit = candidate.get("profit", {})
    margin = pct(profit.get("gross_margin"))
    price = profit.get("price") or 0
    cpc = val(candidate, "competition", "cpc", default=0) or 0
    return_rate = pct(profit.get("return_rate")) or 0
    if margin is None and profit.get("cost") and price:
        margin = (float(price) - float(profit["cost"])) / float(price)
    score = 0
    if margin is not None:
        score += min(12, max(0, margin) / 0.35 * 12)
    if price:
        score += 4 if price >= 20 else 2
    if cpc and price:
        score += 2 if price / cpc >= 20 else 0
    elif price:
        score += 2
    score += max(0, 2 - return_rate / 0.08 * 2)
    return round(max(0, min(20, score)), 2)


def migration_score(candidate):
    mig = candidate.get("migration", {})
    text = " ".join(str(mig.get(k, "")) for k in mig)
    score = 6
    if "strong" in text.lower() or "\u5f3a" in text:
        score += 2
    if mig.get("au_competitor_count") not in (None, ""):
        score += 1
    if any(term in text for term in ("\u5408\u89c4\u9ad8", "\u8ba4\u8bc1", "\u5b63\u8282\u98ce\u9669", "\u5f31")):
        score -= 3
    return round(max(0, min(10, score)), 2)


def risk_score(candidate):
    risk = candidate.get("risk", {})
    text = " ".join([str(candidate.get("candidate", "")), str(candidate.get("primary_keyword", "")), json.dumps(risk, ensure_ascii=False)]).lower()
    score = 10
    flags = list(risk.get("forbidden_flags") or [])
    for term in FORBIDDEN_TERMS:
        if term.lower() in text:
            flags.append(term)
    if flags:
        score -= 8
    if any(x in text for x in ("patent", "\u4e13\u5229", "infringement", "\u4fb5\u6743")):
        score -= 3
    if any(x in text for x in ("complex", "\u590d\u6742", "variant", "\u591a\u53d8\u4f53")):
        score -= 2
    return round(max(0, min(10, score)), 2), sorted(set(flags))


def opportunity_type(candidate, comp_score, profit):
    margin = pct(profit.get("gross_margin"))
    sales = val(candidate, "market", "monthly_sales", default=0) or 0
    high_profit = margin is not None and margin >= 0.35
    low_profit = margin is not None and margin < 0.20
    big_market = sales >= 150000
    small_market = sales < 150000 if sales else False
    low_comp = comp_score >= 22
    if high_profit and big_market and low_comp:
        return ZH["hp_big_low"]
    if high_profit and small_market and low_comp:
        return ZH["hp_small_low"]
    if low_profit and big_market and low_comp:
        return ZH["lp_big_low"]
    return ZH["non_priority"]


def verdict(total, trend_status, flags):
    if flags:
        return ZH["reject"]
    if total >= 80 and trend_status == "rising":
        return ZH["enter"]
    if total >= 70:
        return ZH["test"]
    if total >= 60:
        return ZH["watch"]
    return ZH["reject"]


def score_candidate(candidate):
    trend = trend_metrics(candidate)
    scores = {
        "market_demand": market_score(candidate, trend),
        "competition_strength": competition_score(candidate),
        "profit_space": profit_score(candidate),
        "au_migration_fit": migration_score(candidate),
    }
    risk, flags = risk_score(candidate)
    scores["beginner_fit_risk"] = risk
    total = round(sum(scores.values()), 2)
    opp_type = opportunity_type(candidate, scores["competition_strength"], candidate.get("profit", {}))
    return {"candidate": candidate, "trend": trend, "scores": scores, "total_score": total, "verdict": verdict(total, trend["trend_status"], flags), "opportunity_type": opp_type, "hard_exclusion_flags": flags}


def main():
    parser = argparse.ArgumentParser(description="Score AU product selection opportunities")
    parser.add_argument("data_json")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()
    data_path = Path(args.data_json)
    data = json.loads(data_path.read_text(encoding="utf-8"))
    scored = [score_candidate(c) for c in data.get("candidates", [])]
    scored.sort(key=lambda x: (x["trend"]["trend_status"] == "rising", x["total_score"]), reverse=True)
    scorecard = {"metadata": data.get("metadata", {}), "opportunities": scored}
    out = Path(args.output) if args.output else data_path.with_name("scorecard.json")
    out.write_text(json.dumps(scorecard, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Scored {len(scored)} opportunities -> {out}")


if __name__ == "__main__":
    main()
