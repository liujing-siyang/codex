#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalize SellerSprite/Sorftime/TikTok/Trend CSV or JSON files for AU product selection."""
import argparse
import csv
import json
import re
import shutil
from datetime import date
from pathlib import Path

ALIASES = {
    "candidate": ["candidate", "product", "product_name", "\u54c1\u540d", "\u4ea7\u54c1", "\u4ea7\u54c1\u540d\u79f0", "\u7c7b\u76ee", "\u7ec6\u5206\u5e02\u573a", "\u6807\u9898"],
    "primary_keyword": ["primary_keyword", "keyword", "\u5173\u952e\u8bcd", "\u4e3b\u5173\u952e\u8bcd", "\u641c\u7d22\u8bcd"],
    "long_tail_keywords": ["long_tail_keywords", "related_keywords", "\u957f\u5c3e\u8bcd", "\u7ec6\u5206\u5173\u952e\u8bcd", "\u76f8\u5173\u5173\u952e\u8bcd"],
    "monthly_sales": ["monthly_sales", "\u6708\u9500\u91cf", "\u6708\u9500\u552e\u91cf", "top100_monthly_sales"],
    "monthly_revenue": ["monthly_revenue", "\u6708\u9500\u552e\u989d", "\u9500\u552e\u989d"],
    "search_volume": ["search_volume", "monthly_search", "\u6708\u641c\u7d22\u91cf", "\u641c\u7d22\u91cf"],
    "top3_product_concentration": ["top3_product_concentration", "\u5546\u54c1\u96c6\u4e2d\u5ea6", "\u94fe\u63a5\u96c6\u4e2d\u5ea6"],
    "top3_brand_concentration": ["top3_brand_concentration", "\u54c1\u724c\u96c6\u4e2d\u5ea6"],
    "top3_seller_concentration": ["top3_seller_concentration", "\u5356\u5bb6\u96c6\u4e2d\u5ea6", "\u5e97\u94fa\u96c6\u4e2d\u5ea6"],
    "click_concentration": ["click_concentration", "\u70b9\u51fb\u96c6\u4e2d\u5ea6"],
    "conversion_concentration": ["conversion_concentration", "\u8f6c\u5316\u96c6\u4e2d\u5ea6", "\u8f6c\u5316\u603b\u5360\u6bd4"],
    "spr": ["spr", "SPR"],
    "cpc": ["cpc", "PPC", "CPC", "\u63a8\u8350CPC"],
    "review_count": ["review_count", "\u8bc4\u8bba\u6570", "\u8bc4\u5206\u6570"],
    "rating": ["rating", "\u8bc4\u5206", "\u661f\u7ea7"],
    "amazon_owned_share": ["amazon_owned_share", "Amazon\u81ea\u8425\u5360\u6bd4", "\u4e9a\u9a6c\u900a\u81ea\u8425\u5360\u6bd4"],
    "new_product_count": ["new_product_count", "\u65b0\u54c1\u6570\u91cf", "\u534a\u5e74\u65b0\u54c1\u6570"],
    "new_product_sales_share": ["new_product_sales_share", "\u65b0\u54c1\u9500\u91cf\u5360\u6bd4"],
    "price": ["price", "\u552e\u4ef7", "\u4ef7\u683c", "\u5ba2\u5355\u4ef7"],
    "cost": ["cost", "\u91c7\u8d2d\u6210\u672c", "\u6210\u672c"],
    "gross_margin": ["gross_margin", "\u5229\u6da6\u7387", "\u6bdb\u5229\u7387"],
    "return_rate": ["return_rate", "\u9000\u8d27\u7387"],
    "forbidden_flags": ["forbidden_flags", "\u7981\u5165", "\u98ce\u9669\u6807\u7b7e"],
    "patent_risk": ["patent_risk", "\u4e13\u5229\u98ce\u9669"],
    "compliance_risk": ["compliance_risk", "\u5408\u89c4\u98ce\u9669"],
}
MONTH_RE = re.compile(r"^(20\d{2})[-/\u5e74.]?(0?[1-9]|1[0-2])\u6708?$")


def read_csv(path):
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            with path.open("r", encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("csv", b"", 0, 1, f"cannot decode {path}")


def read_json(path):
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return json.loads(path.read_text(encoding=enc))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"cannot decode {path}")


def as_number(value):
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    raw = str(value)
    text = raw.strip().replace(",", "").replace("$", "").replace("\uffe5", "")
    is_percent = "%" in text
    text = text.replace("%", "")
    try:
        num = float(text)
    except ValueError:
        return None
    if is_percent or (0 < num <= 100 and any(k in raw for k in ("%", "\u5360\u6bd4", "\u7387", "\u96c6\u4e2d\u5ea6"))):
        return num / 100
    return num


def pick(row, field):
    lower = {str(k).strip().lower(): v for k, v in row.items()}
    for alias in ALIASES[field]:
        if alias in row and row[alias] not in (None, ""):
            return row[alias]
        val = lower.get(alias.lower())
        if val not in (None, ""):
            return val
    return None


def split_keywords(value):
    if not value:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return [x.strip() for x in re.split(r"[,;\uff0c\uff1b|/]+", str(value)) if x.strip()]


def month_key(header):
    m = MONTH_RE.match(str(header).strip())
    if not m:
        return None
    return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}"


def extract_history(row, primary_keyword, source):
    history = []
    for key, value in row.items():
        mk = month_key(key)
        if not mk:
            continue
        num = as_number(value)
        if num is not None:
            history.append({"keyword": primary_keyword, "month": mk, "search_volume": int(num), "source": source})
    return sorted(history, key=lambda x: x["month"])


def normalize_row(row, source_file, row_number, source_site, target_site):
    primary = pick(row, "primary_keyword") or pick(row, "candidate") or "Unknown keyword"
    candidate = pick(row, "candidate") or primary
    long_tail = split_keywords(pick(row, "long_tail_keywords"))
    source_ref = {"source": "input_file", "file": source_file.name, "row": row_number, "collected_at": str(date.today()), "fields": list(row.keys())}
    return {
        "candidate": str(candidate).strip(),
        "primary_keyword": str(primary).strip(),
        "long_tail_keywords": long_tail,
        "source_site": source_site,
        "target_site": target_site,
        "market": {"monthly_sales": as_number(pick(row, "monthly_sales")), "monthly_revenue": as_number(pick(row, "monthly_revenue")), "search_volume": as_number(pick(row, "search_volume")), "new_product_count": as_number(pick(row, "new_product_count")), "new_product_sales_share": as_number(pick(row, "new_product_sales_share"))},
        "competition": {"top3_product_concentration": as_number(pick(row, "top3_product_concentration")), "top3_brand_concentration": as_number(pick(row, "top3_brand_concentration")), "top3_seller_concentration": as_number(pick(row, "top3_seller_concentration")), "click_concentration": as_number(pick(row, "click_concentration")), "conversion_concentration": as_number(pick(row, "conversion_concentration")), "spr": as_number(pick(row, "spr")), "cpc": as_number(pick(row, "cpc")), "review_count": as_number(pick(row, "review_count")), "rating": as_number(pick(row, "rating")), "amazon_owned_share": as_number(pick(row, "amazon_owned_share"))},
        "profit": {"price": as_number(pick(row, "price")), "cost": as_number(pick(row, "cost")), "gross_margin": as_number(pick(row, "gross_margin")), "return_rate": as_number(pick(row, "return_rate"))},
        "migration": {"au_fit_notes": "", "au_competitor_count": None, "seasonality_risk": "", "compliance_risk": pick(row, "compliance_risk") or ""},
        "risk": {"forbidden_flags": split_keywords(pick(row, "forbidden_flags")), "patent_risk": pick(row, "patent_risk") or "", "assembly_complexity": "", "variant_complexity": ""},
        "keyword_history": extract_history(row, str(primary).strip(), source_file.name),
        "source_refs": [source_ref],
    }


def flatten_json_records(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("candidates", "opportunities", "products", "keywords", "data"):
            value = data.get(key)
            if isinstance(value, list):
                return value
        return [data]
    return []


def main():
    parser = argparse.ArgumentParser(description="Normalize AU product selection inputs")
    parser.add_argument("--input", required=True, help="CSV/JSON file or folder")
    parser.add_argument("--topic", default="opportunities")
    parser.add_argument("--source-site", default="US")
    parser.add_argument("--target-site", default="AU")
    parser.add_argument("--output", help="Output run directory")
    args = parser.parse_args()
    input_path = Path(args.input)
    run_name = f"{args.topic}_{args.source_site}_to_{args.target_site}_{date.today().strftime('%Y%m%d')}".replace(" ", "_")
    output = Path(args.output) if args.output else Path("reports/au-product-selection") / run_name
    raw_dir = output / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    paths = [p for p in (input_path.rglob("*") if input_path.is_dir() else [input_path]) if p.suffix.lower() in (".csv", ".json")]
    candidates = []
    for source in paths:
        shutil.copy2(source, raw_dir / source.name)
        rows = read_csv(source) if source.suffix.lower() == ".csv" else flatten_json_records(read_json(source))
        for idx, row in enumerate(rows, start=1):
            if isinstance(row, dict):
                candidates.append(normalize_row(row, source, idx, args.source_site, args.target_site))
    data = {"metadata": {"topic": args.topic, "source_site": args.source_site, "target_site": args.target_site, "created_at": str(date.today())}, "candidates": candidates}
    (output / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    evidence = {"sources": [{"file": p.name, "path": str(raw_dir / p.name), "type": p.suffix.lower().lstrip(".")} for p in paths]}
    (output / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Normalized {len(candidates)} candidates -> {output / 'data.json'}")


if __name__ == "__main__":
    main()
