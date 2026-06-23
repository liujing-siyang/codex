#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate that scored opportunities have source and trend evidence."""
import argparse
import json
import sys
from pathlib import Path

ENTER = "\u4f18\u5148\u8fdb\u5165"


def main():
    parser = argparse.ArgumentParser(description="Validate evidence for AU product selection reports")
    parser.add_argument("scorecard_json")
    parser.add_argument("--allow-insufficient", action="store_true", help="Warn instead of failing on insufficient trends")
    args = parser.parse_args()
    scorecard = json.loads(Path(args.scorecard_json).read_text(encoding="utf-8"))
    errors = []
    warnings = []
    for idx, opp in enumerate(scorecard.get("opportunities", []), start=1):
        cand = opp.get("candidate", {})
        name = cand.get("candidate") or f"row {idx}"
        refs = cand.get("source_refs") or []
        history = cand.get("keyword_history") or []
        trend = opp.get("trend", {})
        if not refs:
            errors.append(f"{name}: missing source_refs")
        if len(history) < 4:
            msg = f"{name}: insufficient keyword trend history ({len(history)} points)"
            (warnings if args.allow_insufficient else errors).append(msg)
        if opp.get("verdict") == ENTER and trend.get("trend_status") != "rising":
            errors.append(f"{name}: {ENTER} requires rising trend")
        if opp.get("verdict") == ENTER and opp.get("hard_exclusion_flags"):
            errors.append(f"{name}: hard exclusion cannot be {ENTER}")
    for warning in warnings:
        print("WARN:", warning)
    for error in errors:
        print("ERROR:", error)
    if errors:
        sys.exit(1)
    print(f"Evidence validation passed for {len(scorecard.get('opportunities', []))} opportunities")


if __name__ == "__main__":
    main()
