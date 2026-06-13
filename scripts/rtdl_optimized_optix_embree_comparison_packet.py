#!/usr/bin/env python3
"""Emit the current optimized Embree-vs-OptiX comparison packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.optimized_optix_embree_comparison_packet import (  # noqa: E402
    optimized_optix_embree_comparison_packet,
)


def _fmt(value: float) -> str:
    return f"{value:.9f}".rstrip("0").rstrip(".")


def _markdown(payload: dict[str, object]) -> str:
    measured_pair = dict(tuple(payload["measured_pairs"])[0])
    embree = dict(measured_pair["embree_cpu_optimized"])
    optix = dict(measured_pair["optix_rt"])
    scale_rows = tuple(payload["scale_comparison_rows"])
    same_stream_rows = tuple(payload["same_stream_comparison_rows"])
    same_contract_backend_rows = tuple(payload["same_contract_backend_comparison_rows"])
    planning_rows = tuple(payload["planning_rows"])
    lines = [
        "# Goal4359: Optimized Embree vs OptiX Comparison Packet",
        "",
        "Date: 2026-06-13",
        "",
        "Status: internal comparison packet; not public speedup authorization.",
        "",
        "## Verdict",
        "",
        "This packet accepts one fully optimized LibRTS prepared-query comparison "
        "row, five fresh Embree scale rows from Goal4344, and the Goal4358 "
        "RayJoin LSI/PIP same-stream scalar-count rows, plus the Goal4360 RTNN "
        "prepared ranked-summary raw-row same-contract backend pair. Three "
        "Goal4344 rows are clean internal query-ratio candidates; Robot "
        "Collision and RayDB-style remain boundary-limited because the current "
        "OptiX rows use stronger resident/device output paths.",
        "",
        "The remaining serious comparison blockers are contract-choice apps: "
        "RT-DBSCAN and Barnes-Hut. Spatial RayJoin is now split into LSI/PIP "
        "scalar-count rows with internal-only ratios, and RTNN has a same-contract "
        "raw-row backend ratio that still does not authorize RT-core wording.",
        "",
        "## Measured Pair",
        "",
        "| App | Contract | Scale | Embree CPU Query Median Sec | OptiX RT Query Median Sec | OptiX Query Median Faster | Boundary |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
        "| {app} | `{contract}` | 1024 boxes x 1024 queries, `operation=all`, skip-counts | {embree_q} | {optix_q} | {ratio:.1f}x | query-median only; elapsed totals not ratio-authorized |".format(
            app=measured_pair["app"],
            contract=measured_pair["contract"],
            embree_q=_fmt(float(embree["query_median_sec"])),
            optix_q=_fmt(float(optix["query_median_sec"])),
            ratio=float(measured_pair["optix_query_median_faster_than_optimized_embree"]),
        ),
        "",
        "The same Embree row improved from the pre-Goal4340 columnar fallback query "
        "median by about {speedup:.1f}x. That is evidence for the new generic "
        "Embree AABB primitive route, not a broad CPU-vs-GPU claim.".format(
            speedup=float(measured_pair["optimized_embree_query_median_speedup_vs_old_columnar_fallback"])
        ),
        "",
        "## Scale Rows",
        "",
        "| App | Metric | Embree | OptiX | Embree / OptiX | Faster Backend | Authorization |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row_obj in scale_rows:
        row = dict(row_obj)
        lines.append(
            "| {app} | `{metric}` ({unit}) | {embree_metric} | {optix_metric} | {ratio:.2f}x | `{faster}` | `{auth}` |".format(
                app=row["app"],
                metric=row["metric_name"],
                unit=row["metric_unit"],
                embree_metric=_fmt(float(row["embree_metric"])),
                optix_metric=_fmt(float(row["optix_metric"])),
                ratio=float(row["embree_metric_divided_by_optix_metric"]),
                faster=row["faster_backend_for_metric"],
                auth=row["ratio_authorization"],
            )
        )
    lines.extend(
        [
            "",
            "## RayJoin Same-Stream Rows",
            "",
            "| Workload | Embree ms | OptiX ms | Embree / OptiX | Count | Authorization |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row_obj in same_stream_rows:
        row = dict(row_obj)
        correctness = dict(row["correctness"])
        lines.append(
            "| {workload} | {embree_metric} | {optix_metric} | {ratio:.2f}x | {count} | `{auth}` |".format(
                workload=row["workload"],
                embree_metric=_fmt(float(row["embree_metric"])),
                optix_metric=_fmt(float(row["optix_metric"])),
                ratio=float(row["embree_metric_divided_by_optix_metric"]),
                count=int(correctness["optix_row_count"]),
                auth=row["ratio_authorization"],
            )
        )
    lines.extend(
        [
            "",
            "## RTNN Same-Contract Backend Row",
            "",
            "| Contract | Embree Sec | OptiX Sec | Embree / OptiX | Row Count | Signature Match | RT-Core Claim | Authorization |",
            "| --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row_obj in same_contract_backend_rows:
        row = dict(row_obj)
        correctness = dict(row["correctness"])
        lines.append(
            "| `{contract}` | {embree_metric} | {optix_metric} | {ratio:.2f}x | {count} | `{signature}` | `{rt_core}` | `{auth}` |".format(
                contract=row["contract"],
                embree_metric=_fmt(float(row["embree_metric"])),
                optix_metric=_fmt(float(row["optix_metric"])),
                ratio=float(row["embree_metric_divided_by_optix_metric"]),
                count=int(correctness["optix_row_count"]),
                signature=bool(correctness["integer_signature_match"])
                and bool(correctness["sum_distance_match_exact"]),
                rt_core=bool(row["rt_core_neighbor_search_claim_authorized"]),
                auth=row["ratio_authorization"],
            )
        )
    lines.extend(
        [
            "",
            "Boundary-limited rows are useful engineering evidence, but they are not "
            "clean end-to-end backend ratios.",
            "",
            "## App Table",
            "",
            "| App | OptiX Registry Row | Embree Registry Row | Goal4341 Status | Evidence Or Reason | Next Action |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row_obj in planning_rows:
        row = dict(row_obj)
        optix_registry = dict(row["optix_registry"])
        embree_registry = dict(row["embree_cpu_registry"])
        lines.append(
            "| {app} | `{optix_row}` | `{embree_row}` | `{status}` | {reason} | {next_action} |".format(
                app=row["app"],
                optix_row=optix_registry["row_id"],
                embree_row=embree_registry["row_id"],
                status=row["goal4341_status"],
                reason=row["evidence_or_reason"],
                next_action=row["next_action"],
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
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

    payload = optimized_optix_embree_comparison_packet()
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
