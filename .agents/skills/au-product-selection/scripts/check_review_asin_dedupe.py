#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check that manual-review lists are deduplicated by ASIN/review key."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path


def load_renderer():
    script = Path(__file__).with_name("render_html_report.py")
    spec = importlib.util.spec_from_file_location("render_html_report", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description="Validate manual-review ASIN dedupe behavior")
    parser.add_argument("scorecard_json")
    parser.add_argument("--extended-scorecard", help="Optional full scorecard used only for extended manual-review items")
    parser.add_argument("--html", help="Optional rendered HTML file to scan for question-mark mojibake")
    parser.add_argument("--require-asin", action="append", default=[], help="ASIN that must appear in priority or extended review")
    args = parser.parse_args()

    renderer = load_renderer()
    scorecard_path = Path(args.scorecard_json)
    scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
    extended_scorecard = None
    if args.extended_scorecard:
        extended_scorecard = json.loads(Path(args.extended_scorecard).read_text(encoding="utf-8"))

    extended_opportunities = None
    if extended_scorecard is not None:
        extended_opportunities = extended_scorecard.get("opportunities", [])
    review_items = renderer.dedupe_review_items((extended_opportunities or scorecard.get("opportunities", [])))
    priority, extended = renderer.split_review_pools(scorecard.get("opportunities", []), extended_opportunities)

    priority_keys = [renderer.review_key(item) for item in priority]
    extended_keys = [renderer.review_key(item) for item in extended]
    overlap = sorted(set(priority_keys) & set(extended_keys))
    duplicate_priority = sorted({key for key in priority_keys if priority_keys.count(key) > 1})
    duplicate_extended = sorted({key for key in extended_keys if extended_keys.count(key) > 1})

    errors = []
    if overlap:
        errors.append(f"Priority and extended review lists overlap: {', '.join(overlap)}")
    if duplicate_priority:
        errors.append(f"Duplicate review keys inside priority list: {', '.join(duplicate_priority)}")
    if duplicate_extended:
        errors.append(f"Duplicate review keys inside extended list: {', '.join(duplicate_extended)}")
    review_asins = {renderer.asin(item.get("candidate", {})) for item in priority + extended}
    missing_required = sorted({asin for asin in args.require_asin if asin not in review_asins})
    if missing_required:
        errors.append(f"Required ASINs missing from manual-review lists: {', '.join(missing_required)}")

    if args.html:
        html_text = Path(args.html).read_text(encoding="ascii", errors="replace")
        if "???" in html_text:
            errors.append("Rendered HTML still contains question-mark mojibake runs")

    print(
        "review_items={0} priority_count={1} extended_count={2} overlap_count={3} merged_duplicates={4}".format(
            len(review_items),
            len(priority),
            len(extended),
            len(overlap),
            sum(int(item.get("duplicate_keyword_count") or 0) for item in review_items),
        )
    )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
