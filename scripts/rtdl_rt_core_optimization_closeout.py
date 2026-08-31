#!/usr/bin/env python3
"""Emit the Goal4342 NVIDIA RT-core optimization closeout audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.rt_core_optimization_closeout import rt_core_optimization_closeout  # noqa: E402


def _markdown(payload: dict[str, object]) -> str:
    rows = tuple(payload["rows"])
    summary = dict(payload["summary"])
    lines = [
        "# Goal4342: NVIDIA RT-Core Optimization Closeout Audit",
        "",
        "Date: 2026-06-11",
        "",
        "Status: internal optimization closeout audit; not comparison or release authorization.",
        "",
        "## Verdict",
        "",
        "No obvious remaining high-leverage OptiX/RT-core implementation optimization "
        "is visible in the current ten-app campaign evidence. The next work should "
        "move to the Embree optimization campaign, while preserving the comparison "
        "boundaries below.",
        "",
        "Surprise findings:",
        "",
    ]
    for finding in summary["surprise_findings"]:
        lines.append(f"- {finding}")
    lines.extend(
        [
            "",
            "## Route Table",
            "",
            "| App | Row | Route Class | Optimization Status | Floor Status | Comparison Use | Remaining RT-Core Work |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row_obj in rows:
        row = dict(row_obj)
        lines.append(
            "| {app} | `{row_id}` | `{route_class}` | `{status}` | `{floor}` | `{comparison}` | {work} |".format(
                app=row["app"],
                row_id=row["row_id"],
                route_class=row["route_class"],
                status=row["optimization_status"],
                floor=row["hot_path_floor_status"],
                comparison=row["comparison_table"],
                work=row["remaining_high_leverage_rt_core_work"],
            )
        )
    lines.extend(
        [
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

    payload = rt_core_optimization_closeout()
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
