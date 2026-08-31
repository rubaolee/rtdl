#!/usr/bin/env python3
"""Emit the Goal4344 Embree same-contract scale probe report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.embree_same_contract_scale_probe import embree_same_contract_scale_probe  # noqa: E402


def _fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.9f}".rstrip("0").rstrip(".")
    return str(value)


def _markdown(payload: dict[str, object]) -> str:
    rows = tuple(payload["rows"])
    summary = dict(payload["summary"])
    lines = [
        "# Goal4344: Embree Same-Contract Scale Probe",
        "",
        "Date: 2026-06-11",
        "",
        "Status: internal Embree scale evidence; not comparison or release authorization.",
        "",
        "## Verdict",
        "",
        "Goal4344 moves the five previously missing Embree scale rows out of the "
        "`needs_same_contract_scale_pair` bucket. Three are clean query-ratio "
        "candidates against the current OptiX scale artifacts; Robot Collision "
        "and RayDB-style are scale-ready but boundary-limited because their "
        "current OptiX rows use stronger resident/device output paths.",
        "",
        "## Embree Rows",
        "",
        "| App | Artifact | Comparison Class | Metric | Value | Correctness | Boundary |",
        "| --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for row_obj in rows:
        row = dict(row_obj)
        correctness = dict(row["correctness"])
        lines.append(
            "| {app} | `{artifact}` | `{klass}` | `{metric}` | {value} {unit} | `{correctness}` | {boundary} |".format(
                app=row["app"],
                artifact=row["artifact_name"],
                klass=row["comparison_class"],
                metric=row["metric_name"],
                value=_fmt(row["metric_value"]),
                unit=row["metric_unit"],
                correctness=correctness,
                boundary=row["boundary"],
            )
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Embree scale artifacts: {summary['embree_scale_artifact_count']}",
            f"- Clean query-ratio candidates: {summary['same_contract_query_ratio_candidate_count']}",
            f"- Boundary-limited scale artifacts: {summary['boundary_limited_scale_artifact_count']}",
            f"- All process statuses zero: {summary['all_status_zero']}",
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

    payload = embree_same_contract_scale_probe()
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
