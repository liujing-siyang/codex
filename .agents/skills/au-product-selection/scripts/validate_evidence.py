#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate that scored opportunities have source and trend evidence."""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ENTER = "\u4f18\u5148\u8fdb\u5165"


def main():
    parser = argparse.ArgumentParser(description="Validate evidence for AU product selection reports")
    parser.add_argument("scorecard_json")
    parser.add_argument("--allow-insufficient", action="store_true", help="Warn instead of failing on insufficient trends")
    parser.add_argument("--max-examples", type=int, default=10, help="Maximum example rows per validation issue")
    args = parser.parse_args()
    scorecard = json.loads(Path(args.scorecard_json).read_text(encoding="utf-8"))
    errors = []
    warnings = []
    missing_refs = []
    insufficient_trend = []
    bad_enter = []
    hard_enter = []
    trend_counts = Counter()
    for idx, opp in enumerate(scorecard.get("opportunities", []), start=1):
        cand = opp.get("candidate", {})
        name = cand.get("candidate") or f"row {idx}"
        refs = cand.get("source_refs") or []
        history = cand.get("keyword_history") or []
        trend = opp.get("trend", {})
        trend_status = trend.get("trend_status") or "unknown"
        trend_counts[trend_status] += 1
        if not refs:
            missing_refs.append(name)
        if len(history) < 4:
            insufficient_trend.append(name)
        if opp.get("verdict") == ENTER and trend_status != "rising":
            bad_enter.append(name)
        if opp.get("verdict") == ENTER and opp.get("hard_exclusion_flags"):
            hard_enter.append(name)
    def summarize(label, items, target):
        if not items:
            return
        sample = "; ".join(str(x)[:100] for x in items[:args.max_examples])
        target.append(f"{label}: {len(items)} candidates. Examples: {sample}")
    summarize("missing source_refs", missing_refs, errors)
    summarize("insufficient keyword trend history", insufficient_trend, warnings if args.allow_insufficient else errors)
    summarize(f"{ENTER} without rising trend", bad_enter, errors)
    summarize(f"hard exclusion cannot be {ENTER}", hard_enter, errors)
    print("Trend status summary:", dict(trend_counts))
    for warning in warnings:
        print("WARN:", warning)
    for error in errors:
        print("ERROR:", error)
    if errors:
        sys.exit(1)
    print(f"Evidence validation passed for {len(scorecard.get('opportunities', []))} opportunities")


if __name__ == "__main__":
    main()
