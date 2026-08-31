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
        "row, three active clean Embree scale rows from Goal4344, and the Goal4358 "
        "RayJoin LSI/PIP same-stream scalar-count rows, the Goal4360 RTNN "
        "prepared ranked-summary raw-row same-contract backend pair, and the "
        "Goal4361 RT-DBSCAN same-contract RTDL+Numba configured-route pair, "
        "the Goal4362 Barnes-Hut same-contract native node-coverage pair, and "
        "the Goal4363 Robot Collision same-contract prepared-buffer pair, and "
        "the Goal4364 RayDB-style same-contract prepared grouped-reduction pair. "
        "All active internal comparison rows are now cleanly scoped; no active "
        "boundary-limited phase row remains.",
        "",
        "No promoted benchmark app remains in the contract-choice blocker bucket. "
        "Spatial RayJoin is now split into LSI/PIP scalar-count rows with internal-only ratios; "
        "RTNN has a same-contract raw-row backend ratio that still does not "
        "authorize RT-core wording; RT-DBSCAN has a same-contract configured-route "
        "ratio with the Numba continuation held fixed; Barnes-Hut has a native "
        "node-coverage ratio scoped away from force-vector and paper-reproduction "
        "wording; Robot Collision has a prepared-buffer compact-flag ratio scoped "
        "away from continuous collision and planner wording; RayDB-style has a "
        "prepared grouped-reduction ratio scoped away from authors-code, SQL engine, "
        "and typed hit-stream wording.",
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
            "## Same-Contract Backend Rows",
            "",
            "| App | Contract | Embree Sec | OptiX Sec | Embree / OptiX | Correctness | RT-Core Claim | Authorization |",
            "| --- | --- | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row_obj in same_contract_backend_rows:
        row = dict(row_obj)
        correctness = dict(row["correctness"])
        correctness_ok = (
            bool(correctness.get("integer_signature_match"))
            and bool(correctness.get("sum_distance_match_exact"))
        ) or (
            bool(correctness.get("signature_match"))
            and bool(correctness.get("same_numba_continuation"))
            and bool(correctness.get("same_output_contract"))
        ) or (
            bool(correctness.get("oracle_match_both"))
            and bool(correctness.get("covered_body_count_match"))
            and bool(correctness.get("same_output_contract"))
        ) or (
            bool(correctness.get("same_contract"))
            and bool(correctness.get("same_mode_family"))
            and bool(correctness.get("validation_probe_reference_signature_match"))
        ) or (
            bool(correctness.get("same_generic_contract_family"))
            and bool(correctness.get("matches_cpu_reference_both"))
            and bool(correctness.get("same_fixture_rows_groups_repeat_warmup"))
        )
        rt_core_claim = bool(row.get("rt_core_neighbor_search_claim_authorized", False)) or bool(
            row.get("rt_core_threshold_phase_claim_authorized_internal", False)
        ) or bool(
            row.get("rt_core_node_coverage_claim_authorized_internal", False)
        ) or bool(
            row.get("rt_core_prepared_buffer_claim_authorized_internal", False)
        ) or bool(
            row.get("rt_core_prepared_grouped_reduction_claim_authorized_internal", False)
        )
        lines.append(
            "| {app} | `{contract}` | {embree_metric} | {optix_metric} | {ratio:.2f}x | `{correctness}` | `{rt_core}` | `{auth}` |".format(
                app=row["app"],
                contract=row["contract"],
                embree_metric=_fmt(float(row["embree_metric"])),
                optix_metric=_fmt(float(row["optix_metric"])),
                ratio=float(row["embree_metric_divided_by_optix_metric"]),
                correctness=correctness_ok,
                rt_core=rt_core_claim,
                auth=row["ratio_authorization"],
            )
        )
    lines.extend(
        [
            "",
            "No active boundary-limited row remains in this packet; older Robot "
            "Collision and RayDB-style diagnostics are superseded by the Goal4363 "
            "and Goal4364 same-contract rows above.",
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
