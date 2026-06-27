#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "v3_claim_grade_all_benchmarks_calibrated_20260620"
    / "summary.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_rtnn_ranked_summary_20260620"
    / "rtnn_ranked_summary_intake_summary.json"
)

GROUPS = (
    "rtnn_clustered_65536_ranked_summary",
    "rtnn_shell_65536_ranked_summary",
    "rtnn_uniform_65536_ranked_summary",
)

FALSE_CLAIM_FLAGS = (
    "broad_rt_core_speedup_claim_authorized",
    "device_ranked_summary_aggregate",
    "device_resident_query_points",
    "embree_ranked_summary_aggregate",
    "float32_precision",
    "materializes_neighbor_rows",
    "paper_equivalent_rtnn_row",
    "prepared_cuda_graph_replay",
    "rt_core_neighbor_search_claim_authorized",
    "rtdl_speedup_claim_authorized",
    "same_stream_partner_consumer",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Phoenix V3 RTNN ranked-summary candidate intake from the all-app artifact."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = build_payload(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "comparison": payload["comparison"]}, indent=2, sort_keys=True))
    print(f"wrote {args.output}")
    return 0 if payload["comparison"]["intake_pass"] else 1


def build_payload(source: Path) -> dict[str, Any]:
    data = json.loads(source.read_text(encoding="utf-8"))
    rows = [
        row
        for row in data.get("rows", ())
        if row.get("app_id") == "rtnn" and row.get("comparison_group") in GROUPS
    ]
    by_key = {(row["comparison_group"], row["backend"]): row for row in rows}
    missing = [
        f"{group}/{backend}"
        for group in GROUPS
        for backend in ("embree", "optix")
        if (group, backend) not in by_key
    ]

    compact_rows = []
    pairs = []
    errors = []
    if missing:
        errors.append(f"missing rows: {', '.join(missing)}")

    for group in GROUPS:
        embree = by_key.get((group, "embree"))
        optix = by_key.get((group, "optix"))
        if embree is None or optix is None:
            continue
        compact_rows.extend([_compact_row(embree), _compact_row(optix)])
        pair = _pair_summary(group, embree, optix)
        pairs.append(pair)
        errors.extend(pair["errors"])

    comparison = {
        "intake_pass": not errors,
        "errors": errors,
        "group_count": len(pairs),
        "row_count": len(compact_rows),
        "all_rows_ok": all(row["status"] == "ok" for row in compact_rows),
        "all_same_metric_source": all(pair["same_metric_source"] for pair in pairs),
        "all_same_contract": all(pair["same_contract"] for pair in pairs),
        "all_aggregate_summaries_match": all(pair["aggregate_summary_matches"] for pair in pairs),
        "all_claim_flags_blocked": all(row["claim_flags_blocked"] for row in compact_rows),
        "all_hot_optix_faster_than_embree": all(pair["hot_optix_speedup_vs_embree"] > 1.0 for pair in pairs),
        "all_wall_optix_slower_than_embree": all(pair["wall_optix_speedup_vs_embree"] < 1.0 for pair in pairs),
        "m7_qualified": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
    }
    return {
        "version": "phoenix_v3_rtnn_ranked_summary_intake_2026_06_20",
        "status": "internal_rtnn_ranked_summary_candidate_not_m7",
        "source_artifact": _rel(source),
        "generic_capability": "ranked_summary",
        "generic_capability_status": "distribution_specific_candidate_wall_regression",
        "app_id": "rtnn",
        "artifact_scope": "all_app_calibrated_summary_extraction",
        "rows": compact_rows,
        "pairs": pairs,
        "comparison": comparison,
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "universal_rtnn_acceleration_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "m7_qualified_release_rows": 0,
        },
        "m7_blockers": (
            "wall_timing_optix_slower_than_embree_for_all_three_distributions",
            "distribution_specific_not_universal_rtnn_acceleration",
            "paper_equivalent_rtnn_row_false",
            "summary_rows_materialized",
            "no_author_code_or_external_ann_baseline_comparison",
            "prepared_cuda_graph_replay_false",
            "no_multi_run_variance_evidence",
            "public_row_level_external_review_not_done",
        ),
        "allowed_reading": (
            "On the 65,536-point distribution ladder, OptiX hot elapsed ranked-summary "
            "rows beat Embree hot elapsed rows, with the strongest result on clustered data."
        ),
        "forbidden_reading": (
            "V3 proves universal RTNN acceleration, paper reproduction, or release-authorized "
            "ranked-summary performance."
        ),
        "goal_level_decision_audit": {
            "decision": "extract RTNN ranked-summary candidate evidence before any promotion",
            "was_i_foolish": "No. The wall-timing regression must be exposed before any claim work.",
            "foolish_actions": (
                "It would be foolish to quote the clustered 3.333x hot result as universal "
                "RTNN acceleration while wall timing is slower for OptiX."
            ),
            "other_path": "Rerun the pod first, but classification of the current artifact is the immediate gap.",
            "different_path_now": "Build a focused intake that accepts hot-row signal and blocks M7 promotion.",
        },
    }


def _compact_row(row: dict[str, Any]) -> dict[str, Any]:
    payload = row["payload"]
    claim_boundary = payload["claim_boundary"]
    missing_claim_boundary_flags = sorted(set(FALSE_CLAIM_FLAGS) - set(claim_boundary))
    aggregate = payload.get("raw_ranked_summary_aggregate") or payload.get("ranked_aggregate_summary")
    return {
        "case_id": row["case_id"],
        "comparison_group": row["comparison_group"],
        "distribution": _distribution(row["comparison_group"]),
        "backend": row["backend"],
        "status": row["status"],
        "primary_metric_sec": float(row["primary_metric_sec"]),
        "primary_metric_source": row["primary_metric_source"],
        "wall_median_sec": float(row["wall_median_sec"]),
        "mode": payload["mode"],
        "query_count": int(payload["query_count"]),
        "row_count": int(payload["row_count"]),
        "search_count": int(payload["search_count"]),
        "radius": float(payload["radius"]),
        "k_max": int(payload["k_max"]),
        "batch_count": int(payload["batch_count"]),
        "query_batch_size": int(payload["query_batch_size"]),
        "contract": payload["contract"],
        "aggregate_summary": aggregate,
        "materializes_summary_rows": bool(claim_boundary["materializes_summary_rows"]),
        "materializes_neighbor_rows": bool(claim_boundary["materializes_neighbor_rows"]),
        "paper_equivalent_rtnn_row": bool(claim_boundary["paper_equivalent_rtnn_row"]),
        "prepared_cuda_graph_replay": bool(claim_boundary["prepared_cuda_graph_replay"]),
        "rt_core_neighbor_search_claim_authorized": bool(
            claim_boundary["rt_core_neighbor_search_claim_authorized"]
        ),
        "rtdl_speedup_claim_authorized": bool(claim_boundary["rtdl_speedup_claim_authorized"]),
        "missing_claim_boundary_flags": missing_claim_boundary_flags,
        "claim_flags_blocked": not missing_claim_boundary_flags
        and all(not bool(claim_boundary[flag]) for flag in FALSE_CLAIM_FLAGS),
    }


def _pair_summary(group: str, embree: dict[str, Any], optix: dict[str, Any]) -> dict[str, Any]:
    e = _compact_row(embree)
    o = _compact_row(optix)
    errors: list[str] = []
    if e["primary_metric_source"] != o["primary_metric_source"]:
        errors.append(f"{group}: primary metric sources differ")
    if e["contract"] != o["contract"]:
        errors.append(f"{group}: contracts differ")
    if e["aggregate_summary"] != o["aggregate_summary"]:
        errors.append(f"{group}: aggregate summaries differ")
    if not e["claim_flags_blocked"] or not o["claim_flags_blocked"]:
        errors.append(f"{group}: claim flags are not fully blocked")
    hot_ratio = e["primary_metric_sec"] / o["primary_metric_sec"]
    wall_ratio = e["wall_median_sec"] / o["wall_median_sec"]
    return {
        "comparison_group": group,
        "distribution": _distribution(group),
        "query_count": e["query_count"],
        "embree_hot_elapsed_sec": e["primary_metric_sec"],
        "optix_hot_elapsed_sec": o["primary_metric_sec"],
        "hot_optix_speedup_vs_embree": hot_ratio,
        "embree_wall_median_sec": e["wall_median_sec"],
        "optix_wall_median_sec": o["wall_median_sec"],
        "wall_optix_speedup_vs_embree": wall_ratio,
        "same_metric_source": e["primary_metric_source"] == o["primary_metric_source"],
        "same_contract": e["contract"] == o["contract"],
        "aggregate_summary_matches": e["aggregate_summary"] == o["aggregate_summary"],
        "claim_status": "internal_candidate_not_m7",
        "errors": errors,
    }


def _distribution(group: str) -> str:
    if "clustered" in group:
        return "clustered"
    if "shell" in group:
        return "shell"
    if "uniform" in group:
        return "uniform"
    raise ValueError(f"unknown RTNN distribution in {group}")


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
