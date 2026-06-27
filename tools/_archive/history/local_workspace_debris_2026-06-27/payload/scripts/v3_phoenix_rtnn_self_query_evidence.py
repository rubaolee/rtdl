#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "rtnn_self_query_20260621"
OLD_JSON = EVIDENCE_ROOT / "old_prepared_query.json"
NEW_JSON = EVIDENCE_ROOT / "new_prepared_self_query.json"
CUPY_JSON = EVIDENCE_ROOT / "cupy_grid_reference.json"
CALL_FOR_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_rtnn_prepared_self_query_evidence_2026-06-21.md"
)
EXTERNAL_REVIEW_BLOCKED = (
    ROOT
    / "docs"
    / "reviews"
    / "external_review_blocked_phoenix_v3_rtnn_prepared_self_query_evidence_2026-06-21.md"
)
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_prepared_self_query_evidence_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def _median(payload: dict[str, Any]) -> float:
    if "elapsed_median_sec" in payload:
        return float(payload["elapsed_median_sec"])
    return float(statistics.median(float(value) for value in payload["elapsed_runs_sec"]))


def _optix_cold_plus_query(payload: dict[str, Any]) -> float:
    return (
        float(payload["input_pack_sec"])
        + float(payload["execution_prepare_sec"])
        + _median(payload)
    )


def _optix_runner_wall(payload: dict[str, Any]) -> float:
    return float(payload["input_load_sec"]) + _optix_cold_plus_query(payload)


def _cupy_cold_plus_query(payload: dict[str, Any]) -> float:
    return float(payload["grid_prepare_sec"]) + _median(payload)


def _cupy_runner_wall(payload: dict[str, Any]) -> float:
    return float(payload["input_load_sec"]) + _cupy_cold_plus_query(payload)


def _summary(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload.get("ranked_aggregate_summary") or payload.get("summary") or {})


def build_payload() -> dict[str, Any]:
    old = _read_json(OLD_JSON)
    new = _read_json(NEW_JSON)
    cupy = _read_json(CUPY_JSON)

    old_summary = _summary(old)
    new_summary = _summary(new)
    cupy_summary = _summary(cupy)
    integer_fields = ("row_count", "bounded_neighbor_count", "nearest_id_checksum", "kth_id_checksum")
    integer_match = all(int(new_summary[field]) == int(cupy_summary[field]) for field in integer_fields)
    old_new_integer_match = all(int(new_summary[field]) == int(old_summary[field]) for field in integer_fields)
    sum_delta = float(new_summary["sum_distance"]) - float(cupy_summary["sum_distance"])
    sum_relative_error = abs(sum_delta) / max(abs(float(cupy_summary["sum_distance"])), 1.0)

    old_hot = _median(old)
    new_hot = _median(new)
    cupy_hot = _median(cupy)
    old_cold_plus_query = _optix_cold_plus_query(old)
    new_cold_plus_query = _optix_cold_plus_query(new)
    cupy_cold_plus_query = _cupy_cold_plus_query(cupy)
    old_runner_wall = _optix_runner_wall(old)
    new_runner_wall = _optix_runner_wall(new)
    cupy_runner_wall = _cupy_runner_wall(cupy)
    material_floor = 2.0

    comparisons = {
        "old_prepared_query_to_new_self_query_hot_speedup": _ratio(old_hot, new_hot),
        "old_prepared_query_to_new_self_query_cold_plus_query_speedup": _ratio(
            old_cold_plus_query, new_cold_plus_query
        ),
        "old_prepared_query_to_new_self_query_runner_wall_speedup": _ratio(
            old_runner_wall, new_runner_wall
        ),
        "new_self_query_over_cupy_hot_speedup": _ratio(cupy_hot, new_hot),
        "new_self_query_over_cupy_cold_plus_query_speedup": _ratio(
            cupy_cold_plus_query, new_cold_plus_query
        ),
        "new_self_query_over_cupy_runner_wall_speedup": _ratio(cupy_runner_wall, new_runner_wall),
        "input_pack_reduction_old_to_new": _ratio(
            float(old["input_pack_sec"]), float(new["input_pack_sec"])
        ),
        "execution_prepare_reduction_old_to_new": _ratio(
            float(old["execution_prepare_sec"]), float(new["execution_prepare_sec"])
        ),
    }

    checks = {
        "old_evidence_exists": OLD_JSON.exists(),
        "new_evidence_exists": NEW_JSON.exists(),
        "cupy_evidence_exists": CUPY_JSON.exists(),
        "call_for_review_exists": CALL_FOR_REVIEW.exists(),
        "external_review_blocked_exists": EXTERNAL_REVIEW_BLOCKED.exists(),
        "serious_scale": int(new["query_count"]) >= 1_048_576 and int(new["search_count"]) >= 1_048_576,
        "repeat5": int(new["repeat"]) == 5 and len(new["elapsed_runs_sec"]) == 5,
        "new_mode_is_explicit_self_query": (
            new["result_mode"] == "ranked-summary-aggregate-prepared-self-query-batch-float32"
            and new["contract"]["prepared_search_as_query_points"] is True
            and new["contract"]["prepared_query_points"] is False
        ),
        "old_mode_is_baseline_prepared_query": (
            old["result_mode"] == "ranked-summary-aggregate-prepared-query-batch-float32"
            and old["contract"]["prepared_query_points"] is True
            and old["contract"]["prepared_search_as_query_points"] is False
        ),
        "integer_parity_with_cupy": integer_match,
        "integer_parity_with_old_prepared_query": old_new_integer_match,
        "sum_distance_relative_error_below_tolerance": sum_relative_error <= 1.0e-4,
        "hot_speedup_vs_old_is_material": (
            comparisons["old_prepared_query_to_new_self_query_hot_speedup"] >= material_floor
        ),
        "input_pack_reduction_vs_old_is_material": (
            comparisons["input_pack_reduction_old_to_new"] >= material_floor
        ),
        "hot_speedup_vs_cupy_is_material": (
            comparisons["new_self_query_over_cupy_hot_speedup"] >= material_floor
        ),
        "cold_plus_query_vs_cupy_below_material_floor": (
            comparisons["new_self_query_over_cupy_cold_plus_query_speedup"] < material_floor
        ),
        "runner_wall_vs_cupy_below_material_floor": (
            comparisons["new_self_query_over_cupy_runner_wall_speedup"] < material_floor
        ),
        "release_flags_false": (
            new["claim_boundary"]["rtdl_speedup_claim_authorized"] is False
            and new["claim_boundary"]["broad_rt_core_speedup_claim_authorized"] is False
            and new["claim_boundary"]["rt_core_neighbor_search_claim_authorized"] is False
        ),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = (
        "fail"
        if failed_checks
        else "rtnn_prepared_self_query_hot_path_material_not_m7_wall_floor_not_met"
    )

    return {
        "tool": "v3_phoenix_rtnn_self_query_evidence",
        "status": status,
        "generic_capability": "fixed_radius_neighbors_3d_prepared_self_query_aggregate_batch",
        "candidate_scope": (
            "generic prepared fixed-radius self-query aggregate batch; RTNN is the serious "
            "same-contract evidence harness"
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "m7_reopen_candidate_pending_2ai_review": False,
        "material_speedup_floor": material_floor,
        "review_records": {
            "call_for_review": _rel(CALL_FOR_REVIEW),
            "external_review_blocked": _rel(EXTERNAL_REVIEW_BLOCKED),
            "external_review_status": "blocked_no_external_ai_verdict",
            "two_ai_consensus_exists": False,
        },
        "evidence": {
            "old_prepared_query": _rel(OLD_JSON),
            "new_prepared_self_query": _rel(NEW_JSON),
            "cupy_grid_reference": _rel(CUPY_JSON),
        },
        "measurements": {
            "old_prepared_query": {
                "hot_median_sec": old_hot,
                "input_load_sec": old["input_load_sec"],
                "input_pack_sec": old["input_pack_sec"],
                "execution_prepare_sec": old["execution_prepare_sec"],
                "cold_plus_query_sec": old_cold_plus_query,
                "runner_wall_sec": old_runner_wall,
            },
            "new_prepared_self_query": {
                "hot_median_sec": new_hot,
                "input_load_sec": new["input_load_sec"],
                "input_pack_sec": new["input_pack_sec"],
                "execution_prepare_sec": new["execution_prepare_sec"],
                "cold_plus_query_sec": new_cold_plus_query,
                "runner_wall_sec": new_runner_wall,
            },
            "cupy_grid_reference": {
                "hot_median_sec": cupy_hot,
                "input_load_sec": cupy["input_load_sec"],
                "grid_prepare_sec": cupy["grid_prepare_sec"],
                "cold_plus_query_sec": cupy_cold_plus_query,
                "runner_wall_sec": cupy_runner_wall,
            },
        },
        "comparisons": comparisons,
        "parity": {
            "integer_signature_match_with_cupy": integer_match,
            "integer_signature_match_with_old_prepared_query": old_new_integer_match,
            "sum_distance_delta_new_minus_cupy": sum_delta,
            "sum_distance_relative_error": sum_relative_error,
            "sum_distance_relative_tolerance": 1.0e-4,
        },
        "not_m7_blockers": [
            (
                "New self-query cold-plus-query vs CuPy is only "
                f"{comparisons['new_self_query_over_cupy_cold_plus_query_speedup']:.3f}x, "
                "below the 2.0x material floor."
            ),
            (
                "New self-query runner-wall vs CuPy is only "
                f"{comparisons['new_self_query_over_cupy_runner_wall_speedup']:.3f}x, "
                "so file/input overhead still dominates whole-run evidence."
            ),
            "This is a prepared/reuse-path win, not a broad V3-vs-V2 or whole-app win.",
            "No external Claude/Gemini review has accepted this as an M7 release row.",
        ],
        "interpretation": (
            "The self-query path is a real generic engine improvement: it reuses prepared "
            "search device columns as query columns for fixed_radius_neighbors_3d aggregate "
            "workloads. On the RTX 4000 Ada POD it gives 2.482x hot-query speedup and "
            "2.784x input-pack reduction over the prior prepared-query batch route, while "
            "preserving same-contract integer parity. It also gives a 19.437x hot-query "
            "speedup over the CuPy grid reference. It is not an M7 row yet: cold-plus-query "
            "vs CuPy is only 1.214x and runner-wall is only 1.030x."
        ),
        "next_engine_action": (
            "Keep RTNN ranked_summary open. The next reusable work is reducing prepared "
            "search construction and file/column ingestion overhead, or documenting this "
            "strictly as a prepared-handle repeated-query capability rather than a one-shot "
            "whole-run speed claim."
        ),
        "forbidden_shortcuts": [
            "Do not quote 19.437x without saying it is hot-query prepared self-query only.",
            "Do not call 1.030x runner-wall speedup a major V3 performance win.",
            "Do not claim broad V3 faster-than-V2 from this packet.",
            "Do not promote this row to M7 without external review and a material cold/runner result.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Record prepared self-query as a real generic engine optimization, but keep "
                "RTNN ranked_summary out of M7 because cold/runner wall speed is still below "
                "the material floor."
            ),
            "was_i_foolish": (
                "No. This decision separates a material prepared-path improvement from a "
                "release-quality whole-run claim."
            ),
            "foolish_actions": (
                "It would be foolish to market the 19.437x hot-query number alone or hide "
                "the 1.030x runner-wall result."
            ),
            "other_path": (
                "I could have stopped at the old prepared-query route and argued from 7.7x "
                "hot speedup, but that left duplicated query packing and weaker evidence."
            ),
            "different_path_now": (
                "Use self-query as one Phoenix V3 engine capability, then continue toward "
                "generic ingestion/prepare amortization before any major release claim."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    measurements = payload["measurements"]
    comparisons = payload["comparisons"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 RTNN Prepared Self-Query Evidence",
        "",
        f"Status: `{payload['status']}`.",
        "",
        payload["interpretation"],
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"whole_app_speedup_claim_authorized: {str(payload['whole_app_speedup_claim_authorized']).lower()}",
        f"broad_v3_faster_than_v2_claim_authorized: {str(payload['broad_v3_faster_than_v2_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}",
        f"M7 rows added by this packet: {payload['m7_qualified_release_rows_added']}",
        "```",
        "",
        "## Evidence",
        "",
        f"- Old prepared-query JSON: `{payload['evidence']['old_prepared_query']}`",
        f"- New prepared-self-query JSON: `{payload['evidence']['new_prepared_self_query']}`",
        f"- CuPy grid reference JSON: `{payload['evidence']['cupy_grid_reference']}`",
        f"- Call for review: `{payload['review_records']['call_for_review']}`",
        f"- External review blocked: `{payload['review_records']['external_review_blocked']}`",
        f"- 2-AI consensus exists: `{str(payload['review_records']['two_ai_consensus_exists']).lower()}`",
        "",
        "## Measurements",
        "",
        "| route | hot median sec | pack/prepare sec | cold+query sec | runner wall sec |",
        "| --- | ---: | ---: | ---: | ---: |",
        (
            "| old prepared-query | "
            f"{measurements['old_prepared_query']['hot_median_sec']:.6f} | "
            f"{measurements['old_prepared_query']['input_pack_sec']:.6f} + "
            f"{measurements['old_prepared_query']['execution_prepare_sec']:.6f} | "
            f"{measurements['old_prepared_query']['cold_plus_query_sec']:.6f} | "
            f"{measurements['old_prepared_query']['runner_wall_sec']:.6f} |"
        ),
        (
            "| new prepared-self-query | "
            f"{measurements['new_prepared_self_query']['hot_median_sec']:.6f} | "
            f"{measurements['new_prepared_self_query']['input_pack_sec']:.6f} + "
            f"{measurements['new_prepared_self_query']['execution_prepare_sec']:.6f} | "
            f"{measurements['new_prepared_self_query']['cold_plus_query_sec']:.6f} | "
            f"{measurements['new_prepared_self_query']['runner_wall_sec']:.6f} |"
        ),
        (
            "| CuPy grid reference | "
            f"{measurements['cupy_grid_reference']['hot_median_sec']:.6f} | "
            f"0.000000 + {measurements['cupy_grid_reference']['grid_prepare_sec']:.6f} | "
            f"{measurements['cupy_grid_reference']['cold_plus_query_sec']:.6f} | "
            f"{measurements['cupy_grid_reference']['runner_wall_sec']:.6f} |"
        ),
        "",
        "## Comparisons",
        "",
        f"- Old prepared-query to new self-query hot speedup: `{comparisons['old_prepared_query_to_new_self_query_hot_speedup']:.3f}x`",
        f"- Old prepared-query to new self-query cold+query speedup: `{comparisons['old_prepared_query_to_new_self_query_cold_plus_query_speedup']:.3f}x`",
        f"- Old prepared-query to new self-query runner-wall speedup: `{comparisons['old_prepared_query_to_new_self_query_runner_wall_speedup']:.3f}x`",
        f"- Input-pack reduction: `{comparisons['input_pack_reduction_old_to_new']:.3f}x`",
        f"- New self-query over CuPy hot-query speedup: `{comparisons['new_self_query_over_cupy_hot_speedup']:.3f}x`",
        f"- New self-query over CuPy cold+query speedup: `{comparisons['new_self_query_over_cupy_cold_plus_query_speedup']:.3f}x`",
        f"- New self-query over CuPy runner-wall speedup: `{comparisons['new_self_query_over_cupy_runner_wall_speedup']:.3f}x`",
        "",
        "## Not M7",
        "",
        *[f"- {item}" for item in payload["not_m7_blockers"]],
        "",
        "## Forbidden Shortcuts",
        "",
        *[f"- {item}" for item in payload["forbidden_shortcuts"]],
        "",
        "## Goal-Level Decision Audit",
        "",
        f"1. Was I foolish? {audit['was_i_foolish']}",
        f"2. If yes, what made it foolish? {audit['foolish_actions']}",
        f"3. Was there another path? {audit['other_path']}",
        f"4. Can I try a different path now? {audit['different_path_now']}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if not payload["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
