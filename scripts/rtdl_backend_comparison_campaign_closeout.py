#!/usr/bin/env python3
"""Emit the Goal4345 backend comparison campaign closeout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.backend_comparison_campaign_closeout import backend_comparison_campaign_closeout  # noqa: E402


def _markdown(payload: dict[str, object]) -> str:
    answers = dict(payload["answers"])
    buckets = dict(payload["comparison_buckets"])
    policy = dict(payload["partner_policy"])
    lines = [
        "# Goal4345: Backend Comparison Campaign Closeout",
        "",
        "Date: 2026-06-11",
        "",
        "Status: internal closeout; not release or public speedup authorization.",
        "",
        "## Verdict",
        "",
        "- NVIDIA RT cores: yes, internally ready for the current OptiX benchmark routes; Goal4342 found no obvious remaining high-leverage RT-core implementation work.",
        "- Intel Embree CPUs: yes, internally ready for the native Embree primitive rows with contract boundaries; Goal4343 now reports zero missing same-contract scale rows.",
        "- Serious comparison: yes, as a bucketted internal packet; the v2.12 packet separates clean query ratios, RTNN and RT-DBSCAN scoped paired rows, boundary-limited phase rows, and one remaining contract-choice route.",
        "",
        "## Answers",
        "",
    ]
    for key, value_obj in answers.items():
        value = dict(value_obj)
        lines.extend(
            [
                f"### {key}",
                "",
                f"- Answer: `{value['answer']}`",
                f"- Evidence: {value['evidence']}",
                f"- Boundary: {value['boundary']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Comparison Buckets",
            "",
            "| Bucket | Count |",
            "| --- | ---: |",
        ]
    )
    for key, value in buckets.items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Partner Policy",
            "",
            f"- Default: `{policy['default']}`",
            f"- Pure RTDL table: {policy['pure_rtdl_table']}",
            f"- Configured-route table: {policy['configured_route_table']}",
            f"- Partner-only rows: {policy['partner_only_rows']}",
            f"- Automatic partner selection authorized: `{policy['automatic_partner_selection_authorized']}`",
            "",
            "## Boundary",
            "",
            str(payload["claim_boundary"]),
            "",
            "Validation status: `{}`.".format(dict(payload["validation"])["status"]),
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument("--output-json", type=Path, help="write JSON to this path")
    parser.add_argument("--output-markdown", type=Path, help="write Markdown report to this path")
    args = parser.parse_args(argv)

    payload = backend_comparison_campaign_closeout()
    markdown = _markdown(payload)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.output_markdown:
        args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.output_markdown.write_text(markdown, encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(markdown, end="")
    return 0 if payload["validation"]["status"] == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
