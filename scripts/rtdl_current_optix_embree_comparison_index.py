#!/usr/bin/env python3
"""Emit the current OptiX-vs-Embree comparability index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.current_optix_embree_comparison_index import (  # noqa: E402
    current_optix_embree_comparison_index,
)


def _markdown(payload: dict[str, object]) -> str:
    rows = payload["rows"]
    assert isinstance(rows, tuple)
    lines = [
        "# Current OptiX vs Embree Comparison Index",
        "",
        f"Version: `{payload['version']}`",
        "",
        "This is a comparability index, not a speedup table and not a public speedup table.",
        "",
        "Goal4341 supersedes the older planning index for the optimized LibRTS "
        "AABB same-contract row. Goal4358 adds Spatial RayJoin LSI/PIP "
        "same-stream scalar-count pairs, Goal4360 adds the RTNN same-contract "
        "ranked-summary raw-row pair, and Goal4361 adds the RT-DBSCAN "
        "same-contract configured-route pair. Goal4362 adds the Barnes-Hut "
        "same-contract native node-coverage pair. This current index remains "
        "useful for showing which broad registry artifacts should not be compared directly.",
        "",
        "| App | OptiX row | Embree CPU row | Existing artifact status | Comparability | Internal ratio scope | Next action |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row_obj in rows:
        row = dict(row_obj)
        optix = dict(row["optix"])
        embree = dict(row["embree_cpu"])
        optix_artifact = dict(optix["artifact"])
        embree_artifact = dict(embree["artifact"])
        status = "OptiX {0}; Embree {1}".format(
            optix_artifact["status"],
            embree_artifact["status"],
        )
        lines.append(
            "| {app} | `{optix_row}` | `{embree_row}` | {status} | {klass} | `{scope}` | {next_action} |".format(
                app=row["app"],
                optix_row=optix["row_id"],
                embree_row=embree["row_id"],
                status=status,
                klass=row["comparison_class"],
                scope=row["ratio_authorization_scope"],
                next_action=row["required_next_action"],
            )
        )
        same_stream_pairs = tuple(row.get("same_stream_scalar_count_pairs") or ())
        if same_stream_pairs:
            for pair_obj in same_stream_pairs:
                pair = dict(pair_obj)
                lines.append(
                    "| {app} / {workload} | `Goal4358 OptiX` | `Goal4358 Embree` | count {count}, match={match} | same-stream scalar-count pair | `{scope}` | OptiX {optix_ms:.3f} ms vs Embree {embree_ms:.3f} ms; OptiX/Embree speedup {speedup:.2f}x |".format(
                        app=row["app"],
                        workload=pair["workload"],
                        count=int(pair["row_count"]),
                        match=bool(pair["cross_backend_count_match"]),
                        scope=pair["ratio_authorization"],
                        optix_ms=float(pair["optix_hot_query_ms"]),
                        embree_ms=float(pair["embree_hot_query_ms"]),
                        speedup=float(pair["optix_faster_than_embree"]),
                    )
                )
        rtnn_pair = row.get("rtnn_same_contract_pair")
        if isinstance(rtnn_pair, dict):
            lines.append(
                "| {app} / raw-row | `Goal4360 OptiX` | `Goal4360 Embree` | rows {count}, signature={signature}, rt_core_claim={rt_core} | same-contract ranked-summary raw-row pair | `{scope}` | OptiX {optix_sec:.6f} sec vs Embree {embree_sec:.6f} sec; OptiX/Embree speedup {speedup:.2f}x |".format(
                    app=row["app"],
                    count=int(rtnn_pair["row_count"]),
                    signature=bool(rtnn_pair["integer_signature_match"])
                    and bool(rtnn_pair["sum_distance_match_exact"]),
                    rt_core=bool(rtnn_pair["rt_core_neighbor_search_claim_authorized"]),
                    scope=rtnn_pair["ratio_authorization"],
                    optix_sec=float(rtnn_pair["optix_query_median_sec"]),
                    embree_sec=float(rtnn_pair["embree_query_median_sec"]),
                    speedup=float(rtnn_pair["optix_faster_than_embree"]),
                )
            )
        rt_dbscan_pair = row.get("rt_dbscan_same_contract_pair")
        if isinstance(rt_dbscan_pair, dict):
            lines.append(
                "| {app} / configured | `Goal4361 OptiX` | `Goal4361 Embree` | signature={signature}, same_numba={same_numba}, optix_rt={optix_rt} | same-contract RTDL+Numba configured-route pair | `{scope}` | OptiX {optix_sec:.6f} sec vs Embree {embree_sec:.6f} sec; OptiX/Embree speedup {speedup:.2f}x |".format(
                    app=row["app"],
                    signature=bool(rt_dbscan_pair["signature_match"]),
                    same_numba=bool(rt_dbscan_pair["same_numba_continuation"]),
                    optix_rt=bool(rt_dbscan_pair["optix_rt_core_accelerated"]),
                    scope=rt_dbscan_pair["ratio_authorization"],
                    optix_sec=float(rt_dbscan_pair["optix_elapsed_median_sec"]),
                    embree_sec=float(rt_dbscan_pair["embree_elapsed_median_sec"]),
                    speedup=float(rt_dbscan_pair["optix_faster_than_embree"]),
                )
            )
        barnes_hut_pair = row.get("barnes_hut_same_contract_pair")
        if isinstance(barnes_hut_pair, dict):
            lines.append(
                "| {app} / node-coverage | `Goal4362 OptiX` | `Goal4362 Embree` | bodies {bodies}, oracle={oracle}, optix_rt={optix_rt} | same-contract native node-coverage pair | `{scope}` | OptiX {optix_sec:.6f} sec vs Embree {embree_sec:.6f} sec; OptiX/Embree speedup {speedup:.2f}x |".format(
                    app=row["app"],
                    bodies=int(barnes_hut_pair["body_count"]),
                    oracle=bool(barnes_hut_pair["oracle_match_both"]),
                    optix_rt=bool(barnes_hut_pair["optix_rt_core_accelerated"]),
                    scope=barnes_hut_pair["ratio_authorization"],
                    optix_sec=float(barnes_hut_pair["optix_query_median_sec"]),
                    embree_sec=float(barnes_hut_pair["embree_query_median_sec"]),
                    speedup=float(barnes_hut_pair["optix_faster_than_embree"]),
                )
            )
    lines.extend(
        [
            "",
            "Only the Goal4358 Spatial RayJoin LSI/PIP same-stream scalar-count "
            "pairs, the Goal4360 RTNN ranked-summary raw-row pair, and the "
            "Goal4361 RT-DBSCAN configured-route pair, and the Goal4362 Barnes-Hut "
            "native node-coverage pair authorize internal backend ratios from "
            "existing artifacts. Every public/release speedup and broad RT-core "
            "claim flag remains false.",
            "Fresh same-contract paired runs are still required before publishing "
            "whole-app or broad benchmark speedups.",
        ]
    )
    if any(
        dict(dict(row_obj)["embree_cpu"])["artifact"]["status"] == "missing_current_row_artifact"
        for row_obj in rows
    ):
        lines.extend(
            [
                "",
                "At least one Embree artifact mismatch remains visible here because "
                "the artifact does not contain the current registry row.",
            ]
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument("--output-json", type=Path, help="write JSON to this path")
    parser.add_argument("--output-markdown", type=Path, help="write Markdown report to this path")
    args = parser.parse_args(argv)

    payload = current_optix_embree_comparison_index()
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    markdown = _markdown(payload)
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
