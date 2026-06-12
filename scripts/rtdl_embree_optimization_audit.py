#!/usr/bin/env python3
"""Emit the Goal4343 Embree optimization audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.embree_optimization_audit import embree_optimization_audit  # noqa: E402


def _markdown(payload: dict[str, object]) -> str:
    rows = tuple(payload["rows"])
    summary = dict(payload["summary"])
    lines = [
        "# Goal4343: Embree Optimization Audit",
        "",
        "Date: 2026-06-11",
        "",
        "Status: internal Embree optimization audit; not comparison or release authorization.",
        "",
        "## Verdict",
        "",
        "LibRTS remains the only fully optimized measured Embree-vs-OptiX pair, "
        "but Goal4344 now supplies the five missing Embree scale rows. The "
        "remaining Embree campaign blockers are the four apps that still need "
        "a contract choice before a serious backend ratio can be reported.",
        "",
        "Important stale-evidence note: the full Goal4298 artifact predates the "
        "Goal4308 RTNN Embree front door, so the audit combines the historical "
        "packet with the Goal4308 RTNN follow-up, the Goal4340 LibRTS optimized "
        "summary, and the Goal4344 Embree same-contract scale probe.",
        "",
        "## Route Table",
        "",
        "| App | Registry Row | Optimization Status | Comparison Readiness | Artifact Status | Next Action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row_obj in rows:
        row = dict(row_obj)
        lines.append(
            "| {app} | `{row}` | `{status}` | `{readiness}` | `{artifact}` | {next_action} |".format(
                app=row["app"],
                row=row["registry_row_id"],
                status=row["optimization_status"],
                readiness=row["comparison_readiness"],
                artifact=row["artifact_status"],
                next_action=row["next_action"],
            )
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Optimized measured pair ready: {summary['optimized_measured_pair_ready_count']}",
            f"- Embree scale evidence ready: {summary['embree_scale_evidence_ready_count']}",
            f"- Boundary-limited scale evidence ready: {summary['boundary_limited_scale_evidence_ready_count']}",
            f"- Same-contract scale pairs needed: {summary['same_contract_scale_pair_needed_count']}",
            f"- Contract choices needed: {summary['contract_choice_needed_count']}",
            f"- LibRTS Embree speedup versus old columnar fallback: {summary['librts_query_median_speedup_vs_old_columnar_fallback']:.1f}x",
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

    payload = embree_optimization_audit()
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
