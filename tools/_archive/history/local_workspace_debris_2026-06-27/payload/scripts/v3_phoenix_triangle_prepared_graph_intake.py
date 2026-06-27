#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
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
    / "phoenix_v3_triangle_prepared_graph_20260620"
    / "triangle_prepared_graph_intake_summary.json"
)

GROUPS = (
    "triangle_count_rt_graph_2a1_cliques_20000",
    "triangle_count_rt_graph_2a1_cliques_80000",
)

FALSE_CLAIM_FLAGS = (
    "public_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "triangle_count_rt_core_claim_authorized",
    "true_zero_copy_claim_authorized",
    "full_graph_database_claim",
    "distributed_graph_claim",
    "paper_reproduction",
    "app_specific_native_engine_logic_allowed",
    "automatic_partner_selection_authorized",
    "native_engine_customization",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Phoenix V3 Triangle prepared-graph candidate intake from the all-app artifact."
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
        if row.get("app_id") == "triangle_counting" and row.get("comparison_group") in GROUPS
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
        "all_match_oracle": all(row["triangle_count_matches_oracle"] for row in compact_rows),
        "all_claim_flags_blocked": all(row["claim_flags_blocked"] for row in compact_rows),
        "all_phase_timing_accept": all(row["phase_timing_accept"] for row in compact_rows),
        "optix_rt_core_and_embree_non_rt_core": all(
            pair["optix_rt_core_accelerated"] and not pair["embree_rt_core_accelerated"] for pair in pairs
        ),
        "same_metric_source": all(pair["same_metric_source"] for pair in pairs),
        "same_contract": all(pair["same_contract"] for pair in pairs),
        "m7_qualified": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
    }
    return {
        "version": "phoenix_v3_triangle_prepared_graph_intake_2026_06_20",
        "status": "internal_triangle_prepared_graph_candidate_not_m7",
        "source_artifact": _rel(source),
        "generic_capability": "prepared_graph_chunk",
        "generic_capability_status": "candidate_executor_linkage_not_closed",
        "app_id": "triangle_counting",
        "artifact_scope": "all_app_calibrated_summary_extraction",
        "rows": compact_rows,
        "pairs": pairs,
        "comparison": comparison,
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "graph_database_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "triangle_count_rt_core_claim_authorized": False,
            "m7_qualified_release_rows": 0,
        },
        "m7_blockers": (
            "synthetic_k4_clique_ladder_not_paper_dataset",
            "not_graph_database_or_full_triangle_counting_app",
            "no_author_code_or_paper_dataset_comparison",
            "prepared_graph_chunk_executor_linkage_not_closed",
            "hot_query_vs_wall_timing_ratio_not_characterized_for_release",
            "public_row_level_external_review_not_done",
        ),
        "allowed_reading": (
            "On the generated K4 clique ladder rows, the generic RT-Graph 2A1 "
            "ray-triangle weighted-any-hit subpath has internal same-contract "
            "OptiX-over-Embree hot-query wins."
        ),
        "forbidden_reading": (
            "V3 proves public Triangle/RT-Graph paper reproduction, graph database "
            "acceleration, or a release-authorized prepared-graph M7 row."
        ),
        "goal_level_decision_audit": {
            "decision": "extract Triangle prepared-graph candidate evidence instead of rerunning pod immediately",
            "was_i_foolish": "No. The existing all-app artifact already has serious Triangle rows; the missing step is boundary intake.",
            "foolish_actions": (
                "It would be foolish to quote the 347x ratio as a public RT-Graph result "
                "before proving M7 row qualification."
            ),
            "other_path": "Rerun the pod first, but that would spend time before classifying the existing evidence gap.",
            "different_path_now": "Build a focused intake that identifies accepted internal facts and M7 blockers.",
        },
    }


def _compact_row(row: dict[str, Any]) -> dict[str, Any]:
    payload = row["payload"]
    timing = payload["timing_ms"]
    phase = payload["v2_4_phase_timing"]
    claim_boundary = payload["claim_boundary"]
    return {
        "case_id": row["case_id"],
        "comparison_group": row["comparison_group"],
        "backend": row["backend"],
        "status": row["status"],
        "primary_metric_sec": float(row["primary_metric_sec"]),
        "primary_metric_source": row["primary_metric_source"],
        "wall_median_sec": float(row["wall_median_sec"]),
        "mode": payload["mode"],
        "contract": payload["contract"],
        "partner": payload["partner"],
        "partner_summary_contract_used": bool(payload["partner_summary_contract_used"]),
        "rt_core_accelerated": bool(payload["rt_core_accelerated"]),
        "triangle_count_matches_oracle": bool(payload["triangle_count_matches_oracle"]),
        "oracle_triangle_count": int(payload["oracle_triangle_count"]),
        "generic_rt_weighted_triangle_count": int(payload["generic_rt_weighted_triangle_count"]),
        "primitive_count": int(payload["primitive_count"]),
        "ray_count": int(payload["ray_count"]),
        "clique_count": _clique_count(row["comparison_group"]),
        "query_repeat": int(timing["query_repeat"]),
        "query_warmup": int(timing["query_warmup"]),
        "query_median_ms": float(timing["query_median_ms"]),
        "scene_build_ms": float(timing["prepare_scene_ms"]),
        "query_preparation_ms": float(timing["build_geometry"]),
        "materialization_ms": float(timing["reduce_hits"]),
        "phase_timing_accept": phase["validation"]["status"] == "accept",
        "same_phase_contract_as_basis": bool(phase["same_phase_contract_as_basis"]),
        "phase_contract_version": phase["phase_contract_version"],
        "claim_flags_blocked": all(not bool(claim_boundary.get(flag)) for flag in FALSE_CLAIM_FLAGS),
        "public_speedup_claim_authorized": bool(claim_boundary["public_speedup_claim_authorized"]),
        "paper_reproduction": bool(claim_boundary["paper_reproduction"]),
        "full_graph_database_claim": bool(claim_boundary["full_graph_database_claim"]),
        "synthetic_fixture_boundary": "K4 clique ladder; not graph database or paper dataset",
    }


def _pair_summary(group: str, embree: dict[str, Any], optix: dict[str, Any]) -> dict[str, Any]:
    e = _compact_row(embree)
    o = _compact_row(optix)
    errors: list[str] = []
    if e["contract"] != o["contract"]:
        errors.append(f"{group}: contracts differ")
    if e["primary_metric_source"] != o["primary_metric_source"]:
        errors.append(f"{group}: primary metric sources differ")
    if e["oracle_triangle_count"] != o["oracle_triangle_count"]:
        errors.append(f"{group}: oracle counts differ")
    if not e["triangle_count_matches_oracle"] or not o["triangle_count_matches_oracle"]:
        errors.append(f"{group}: oracle mismatch")
    if e["rt_core_accelerated"]:
        errors.append(f"{group}: Embree row unexpectedly marked RT-core accelerated")
    if not o["rt_core_accelerated"]:
        errors.append(f"{group}: OptiX row not marked RT-core accelerated")
    if not e["claim_flags_blocked"] or not o["claim_flags_blocked"]:
        errors.append(f"{group}: claim flags are not fully blocked")
    if not e["phase_timing_accept"] or not o["phase_timing_accept"]:
        errors.append(f"{group}: phase timing validation did not accept")
    ratio = e["primary_metric_sec"] / o["primary_metric_sec"]
    wall_ratio = e["wall_median_sec"] / o["wall_median_sec"]
    return {
        "comparison_group": group,
        "clique_count": _clique_count(group),
        "oracle_triangle_count": e["oracle_triangle_count"],
        "embree_query_median_sec": e["primary_metric_sec"],
        "optix_query_median_sec": o["primary_metric_sec"],
        "optix_speedup_vs_embree": ratio,
        "embree_wall_median_sec": e["wall_median_sec"],
        "optix_wall_median_sec": o["wall_median_sec"],
        "optix_wall_speedup_vs_embree": wall_ratio,
        "same_metric_source": e["primary_metric_source"] == o["primary_metric_source"],
        "same_contract": e["contract"] == o["contract"],
        "embree_rt_core_accelerated": e["rt_core_accelerated"],
        "optix_rt_core_accelerated": o["rt_core_accelerated"],
        "claim_status": "internal_candidate_not_m7",
        "errors": errors,
    }


def _clique_count(group: str) -> int:
    match = re.search(r"cliques_(\d+)$", group)
    if not match:
        raise ValueError(f"cannot parse clique count from {group}")
    return int(match.group(1))


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
