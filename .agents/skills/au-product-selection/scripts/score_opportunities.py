#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Score AU migration opportunities with keyword growth as a hard gate."""
import argparse
import json
import re
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
EVENT_TERMS = [
    "christmas", "halloween", "easter", "valentine", "thanksgiving", "4th of july",
    "independence day", "anniversary", "patriotic", "super bowl", "new year",
    "limited edition", "movie", "k-pop", "demon hunters",
]
DISCOVERY_EXCLUDED_MAIN_CATEGORIES = {"clothing, shoes & jewelry"}
STRONG_SEASON_TERMS = ["summer", "swim", "beach", "wedding", "patriotic", "anniversary", "2026"]
MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}


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


def parse_month(month):
    match = re.match(r"^20\d{2}-(0?[1-9]|1[0-2])$", str(month or ""))
    return int(match.group(1)) if match else None


def shift_month(month, offset=6):
    return ((month - 1 + offset) % 12) + 1


def month_label(months):
    if not months:
        return "N/A"
    return ", ".join(MONTH_NAMES[m] for m in months if m in MONTH_NAMES)


def seasonality_metrics(candidate):
    history = candidate.get("keyword_history") or []
    points = []
    for item in history:
        month = parse_month(item.get("month"))
        volume = item.get("search_volume")
        if month is None or volume is None:
            continue
        try:
            points.append((month, float(volume)))
        except (TypeError, ValueError):
            continue
    text = " ".join([
        str(candidate.get("candidate", "")),
        str(candidate.get("primary_keyword", "")),
        " ".join(str(x) for x in candidate.get("long_tail_keywords", [])[:10]),
    ]).lower()
    if any(term in text for term in EVENT_TERMS):
        return {
            "label": "event_driven",
            "source_peak_months": [],
            "au_entry_window": "Event timing; validate AU cultural fit manually",
            "notes": "Title or keyword contains event/year/IP terms. Do not apply simple US-to-AU 6-month season shift automatically.",
        }
    if len(points) < 6:
        return {
            "label": "insufficient",
            "source_peak_months": [],
            "au_entry_window": "Trend history insufficient",
            "notes": "Fewer than 6 monthly trend points; cannot classify evergreen vs seasonal reliably.",
        }
    month_totals = {}
    for month, volume in points:
        month_totals.setdefault(month, []).append(volume)
    monthly_avg = {m: sum(v) / len(v) for m, v in month_totals.items()}
    avg_volume = sum(v for _, v in points) / len(points)
    peak_volume = max(monthly_avg.values()) if monthly_avg else 0
    trough_volume = min(monthly_avg.values()) if monthly_avg else 0
    if not avg_volume or not peak_volume:
        label = "insufficient"
    else:
        peak_threshold = max(avg_volume * 1.35, peak_volume * 0.70)
        peak_months = sorted([m for m, v in monthly_avg.items() if v >= peak_threshold])
        peak_ratio = peak_volume / max(trough_volume, 1)
        label = "seasonal" if peak_ratio >= 2.2 and len(peak_months) <= 5 else "evergreen"
    peak_months = sorted([m for m, v in monthly_avg.items() if v >= max(avg_volume * 1.35, peak_volume * 0.70)]) if label == "seasonal" else []
    if label == "seasonal":
        au_months = sorted({shift_month(m) for m in peak_months})
        window = f"US peak {month_label(peak_months)} -> AU rough peak {month_label(au_months)}; test/stock 1-2 months before AU peak"
        notes = "Seasonality detected from US keyword history. Because AU is in the Southern Hemisphere, shift weather/season demand by roughly 6 months."
    elif label == "evergreen":
        window = "Year-round demand; schedule tests by competition, cashflow, and inventory lead time"
        notes = "No strong monthly spike detected from keyword history."
    else:
        window = "Trend history insufficient"
        notes = "Cannot classify seasonality reliably."
    return {"label": label, "source_peak_months": peak_months, "au_entry_window": window, "notes": notes}


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


def is_apparel_candidate(candidate):
    main = str(val(candidate, "category", "main", default="") or "").strip().lower()
    return main in DISCOVERY_EXCLUDED_MAIN_CATEGORIES


def text_blob(candidate):
    return " ".join([
        str(candidate.get("candidate", "")),
        str(candidate.get("primary_keyword", "")),
        " ".join(str(x) for x in candidate.get("long_tail_keywords", [])[:12]),
        str(val(candidate, "category", "main", default="")),
        str(val(candidate, "category", "sub", default="")),
    ]).lower()


def discovery_score(candidate, hard_flags):
    if hard_flags:
        return 0, ["hard_exclusion"], ["Hard exclusion flags present"]
    if is_apparel_candidate(candidate):
        return 0, ["excluded_apparel"], ["Clothing, Shoes & Jewelry is excluded from discovery review by default"]

    market = candidate.get("market", {})
    profit = candidate.get("profit", {})
    comp = candidate.get("competition", {})
    sales = market.get("monthly_sales") or 0
    revenue = market.get("monthly_revenue") or 0
    sales_growth = market.get("monthly_sales_growth") or 0
    margin = pct(profit.get("gross_margin")) or 0
    price = profit.get("price") or 0
    fba_fee = profit.get("fba_fee") or 0
    review_count = comp.get("review_count")
    seller_count = comp.get("seller_count")
    variant_count = comp.get("variant_count")
    rating = comp.get("rating") or 0
    text = text_blob(candidate)

    parts = []
    score = 0
    sales_score = min(25, float(sales) / 10000 * 25) if sales else 0
    revenue_score = min(10, float(revenue) / 250000 * 10) if revenue else 0
    growth_score = min(12, max(0, float(sales_growth)) / 0.5 * 12) if sales_growth else 0
    margin_score = min(18, margin / 0.7 * 18) if margin else 0
    price_score = 8 if 15 <= float(price or 0) <= 45 else (4 if price else 0)
    review_score = 8 if review_count is not None and float(review_count) <= 500 else (4 if review_count is not None and float(review_count) <= 1000 else 0)
    seller_score = 6 if seller_count is not None and float(seller_count) <= 3 else 0
    variant_score = 5 if variant_count is not None and float(variant_count) <= 10 else (2 if variant_count is not None and float(variant_count) <= 30 else 0)
    fba_score = 4 if fba_fee and float(fba_fee) <= 4 else (2 if fba_fee and float(fba_fee) <= 6 else 0)
    rating_score = 4 if rating and float(rating) >= 4.0 else 0

    score = sales_score + revenue_score + growth_score + margin_score + price_score + review_score + seller_score + variant_score + fba_score + rating_score
    flags = []
    if any(term in text for term in EVENT_TERMS):
        score -= 10
        flags.append("event_driven_noise")
    elif any(term in text for term in STRONG_SEASON_TERMS):
        score -= 6
        flags.append("seasonal_noise")
    if variant_count is not None and float(variant_count) > 50:
        score -= 6
        flags.append("high_variant_complexity")
    if rating and float(rating) < 4.0:
        score -= 4
        flags.append("low_rating")

    if sales_score >= 18:
        parts.append("high monthly sales")
    if revenue_score >= 7:
        parts.append("meaningful revenue")
    if margin_score >= 14:
        parts.append("high gross margin")
    if review_score >= 8:
        parts.append("review count still approachable")
    if seller_score >= 6:
        parts.append("low seller count")
    if variant_score >= 5:
        parts.append("low variant complexity")
    if fba_score >= 4:
        parts.append("low FBA fee")
    if not parts:
        parts.append("commercial signals need manual validation")

    return round(max(0, min(100, score)), 2), flags, parts


def review_tier(total, trend_status, hard_flags, discovery, discovery_flags):
    if hard_flags:
        return "excluded"
    if trend_status == "rising" or total >= 70:
        return "priority_trend_verified"
    if "excluded_apparel" in discovery_flags:
        return "excluded"
    if discovery >= 80:
        return "priority_discovery"
    if discovery >= 75:
        return "extended_discovery"
    return "excluded"


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
    seasonality = seasonality_metrics(candidate)
    scores = {
        "market_demand": market_score(candidate, trend),
        "competition_strength": competition_score(candidate),
        "profit_space": profit_score(candidate),
        "au_migration_fit": migration_score(candidate),
    }
    risk, flags = risk_score(candidate)
    scores["beginner_fit_risk"] = risk
    total = round(sum(scores.values()), 2)
    discovery, discovery_flags, discovery_notes = discovery_score(candidate, flags)
    tier = review_tier(total, trend["trend_status"], flags, discovery, discovery_flags)
    opp_type = opportunity_type(candidate, scores["competition_strength"], candidate.get("profit", {}))
    return {
        "candidate": candidate,
        "trend": trend,
        "seasonality": seasonality,
        "scores": scores,
        "total_score": total,
        "discovery_score": discovery,
        "discovery_flags": discovery_flags,
        "discovery_notes": discovery_notes,
        "review_tier": tier,
        "verdict": verdict(total, trend["trend_status"], flags),
        "opportunity_type": opp_type,
        "hard_exclusion_flags": flags,
    }


def main():
    parser = argparse.ArgumentParser(description="Score AU product selection opportunities")
    parser.add_argument("data_json")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()
    data_path = Path(args.data_json)
    data = json.loads(data_path.read_text(encoding="utf-8"))
    scored = [score_candidate(c) for c in data.get("candidates", [])]
    scored.sort(key=lambda x: (x["trend"]["trend_status"] == "rising", x.get("discovery_score", 0), x["total_score"]), reverse=True)
    scorecard = {"metadata": data.get("metadata", {}), "opportunities": scored}
    out = Path(args.output) if args.output else data_path.with_name("scorecard.json")
    out.write_text(json.dumps(scorecard, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Scored {len(scored)} opportunities -> {out}")


if __name__ == "__main__":
    main()
