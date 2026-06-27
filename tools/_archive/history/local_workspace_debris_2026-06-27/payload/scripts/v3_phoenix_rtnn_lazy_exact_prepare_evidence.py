#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREVIOUS_EVIDENCE_ROOT = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "rtnn_self_query_20260621"
LAZY_EVIDENCE_ROOT = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "rtnn_lazy_exact_prepare_20260621"
PREVIOUS_OLD_JSON = PREVIOUS_EVIDENCE_ROOT / "old_prepared_query.json"
PREVIOUS_SELF_QUERY_JSON = PREVIOUS_EVIDENCE_ROOT / "new_prepared_self_query.json"
LAZY_OLD_JSON = LAZY_EVIDENCE_ROOT / "old_prepared_query_lazy_exact.json"
LAZY_SELF_QUERY_JSON = LAZY_EVIDENCE_ROOT / "new_prepared_self_query_lazy_exact.json"
LAZY_CUPY_JSON = LAZY_EVIDENCE_ROOT / "cupy_grid_reference_lazy_exact_compare.json"
OUT_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_lazy_exact_prepare_evidence_2026-06-21.json"
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
    return float(payload["input_pack_sec"]) + float(payload["execution_prepare_sec"]) + _median(payload)


def _optix_runner_wall(payload: dict[str, Any]) -> float:
    return float(payload["input_load_sec"]) + _optix_cold_plus_query(payload)


def _cupy_cold_plus_query(payload: dict[str, Any]) -> float:
    return float(payload["grid_prepare_sec"]) + _median(payload)


def _cupy_runner_wall(payload: dict[str, Any]) -> float:
    return float(payload["input_load_sec"]) + _cupy_cold_plus_query(payload)


def _summary(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload.get("ranked_aggregate_summary") or payload.get("summary") or {})


def build_payload() -> dict[str, Any]:
    previous_old = _read_json(PREVIOUS_OLD_JSON)
    previous_self = _read_json(PREVIOUS_SELF_QUERY_JSON)
    lazy_old = _read_json(LAZY_OLD_JSON)
    lazy_self = _read_json(LAZY_SELF_QUERY_JSON)
    lazy_cupy = _read_json(LAZY_CUPY_JSON)

    lazy_self_summary = _summary(lazy_self)
    lazy_old_summary = _summary(lazy_old)
    cupy_summary = _summary(lazy_cupy)
    integer_fields = ("row_count", "bounded_neighbor_count", "nearest_id_checksum", "kth_id_checksum")
    integer_match_cupy = all(int(lazy_self_summary[field]) == int(cupy_summary[field]) for field in integer_fields)
    integer_match_old = all(int(lazy_self_summary[field]) == int(lazy_old_summary[field]) for field in integer_fields)
    sum_delta = float(lazy_self_summary["sum_distance"]) - float(cupy_summary["sum_distance"])
    sum_relative_error = abs(sum_delta) / max(abs(float(cupy_summary["sum_distance"])), 1.0)

    previous_self_cold = _optix_cold_plus_query(previous_self)
    lazy_self_cold = _optix_cold_plus_query(lazy_self)
    lazy_cupy_cold = _cupy_cold_plus_query(lazy_cupy)
    previous_self_wall = _optix_runner_wall(previous_self)
    lazy_self_wall = _optix_runner_wall(lazy_self)
    lazy_cupy_wall = _cupy_runner_wall(lazy_cupy)
    lazy_old_cold = _optix_cold_plus_query(lazy_old)
    lazy_old_wall = _optix_runner_wall(lazy_old)
    material_floor = 2.0

    comparisons = {
        "old_prepared_query_prepare_reduction_prepatch_to_lazy": _ratio(
            float(previous_old["execution_prepare_sec"]), float(lazy_old["execution_prepare_sec"])
        ),
        "self_query_prepare_reduction_prepatch_to_lazy": _ratio(
            float(previous_self["execution_prepare_sec"]), float(lazy_self["execution_prepare_sec"])
        ),
        "self_query_cold_plus_query_reduction_prepatch_to_lazy": _ratio(
            previous_self_cold, lazy_self_cold
        ),
        "self_query_runner_wall_reduction_prepatch_to_lazy": _ratio(
            previous_self_wall, lazy_self_wall
        ),
        "lazy_old_prepared_query_to_lazy_self_query_hot_speedup": _ratio(
            _median(lazy_old), _median(lazy_self)
        ),
        "lazy_old_prepared_query_to_lazy_self_query_cold_plus_query_speedup": _ratio(
            lazy_old_cold, lazy_self_cold
        ),
        "lazy_old_prepared_query_to_lazy_self_query_runner_wall_speedup": _ratio(
            lazy_old_wall, lazy_self_wall
        ),
        "lazy_self_query_over_cupy_hot_speedup": _ratio(_median(lazy_cupy), _median(lazy_self)),
        "lazy_self_query_over_cupy_cold_plus_query_speedup": _ratio(lazy_cupy_cold, lazy_self_cold),
        "lazy_self_query_over_cupy_runner_wall_speedup": _ratio(lazy_cupy_wall, lazy_self_wall),
    }

    checks = {
        "previous_evidence_exists": PREVIOUS_OLD_JSON.exists() and PREVIOUS_SELF_QUERY_JSON.exists(),
        "lazy_evidence_exists": LAZY_OLD_JSON.exists() and LAZY_SELF_QUERY_JSON.exists() and LAZY_CUPY_JSON.exists(),
        "serious_scale": int(lazy_self["query_count"]) >= 1_048_576 and int(lazy_self["search_count"]) >= 1_048_576,
        "repeat5": int(lazy_self["repeat"]) == 5 and len(lazy_self["elapsed_runs_sec"]) == 5,
        "lazy_self_query_mode_is_explicit": (
            lazy_self["result_mode"] == "ranked-summary-aggregate-prepared-self-query-batch-float32"
            and lazy_self["contract"]["prepared_search_as_query_points"] is True
            and lazy_self["contract"]["prepared_query_points"] is False
        ),
        "lazy_old_mode_is_prepared_query_baseline": (
            lazy_old["result_mode"] == "ranked-summary-aggregate-prepared-query-batch-float32"
            and lazy_old["contract"]["prepared_query_points"] is True
            and lazy_old["contract"]["prepared_search_as_query_points"] is False
        ),
        "integer_parity_with_cupy": integer_match_cupy,
        "integer_parity_with_lazy_old": integer_match_old,
        "sum_distance_relative_error_below_tolerance": sum_relative_error <= 1.0e-4,
        "prepare_reduction_is_real": comparisons["self_query_prepare_reduction_prepatch_to_lazy"] > 1.0,
        "cold_plus_query_reduction_is_real": comparisons["self_query_cold_plus_query_reduction_prepatch_to_lazy"] > 1.0,
        "lazy_self_hot_vs_cupy_is_material": comparisons["lazy_self_query_over_cupy_hot_speedup"] >= material_floor,
        "lazy_self_cold_vs_cupy_below_material_floor": (
            comparisons["lazy_self_query_over_cupy_cold_plus_query_speedup"] < material_floor
        ),
        "lazy_self_runner_wall_vs_cupy_below_material_floor": (
            comparisons["lazy_self_query_over_cupy_runner_wall_speedup"] < material_floor
        ),
        "release_flags_false": (
            lazy_self["claim_boundary"]["rtdl_speedup_claim_authorized"] is False
            and lazy_self["claim_boundary"]["broad_rt_core_speedup_claim_authorized"] is False
            and lazy_self["claim_boundary"]["rt_core_neighbor_search_claim_authorized"] is False
        ),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = "fail" if failed_checks else "rtnn_lazy_exact_prepare_reduces_prepare_not_m7_wall_floor_not_met"

    return {
        "tool": "v3_phoenix_rtnn_lazy_exact_prepare_evidence",
        "status": status,
        "generic_capability": "fixed_radius_neighbors_3d_lazy_exact_search_device_materialization",
        "candidate_scope": (
            "generic prepared fixed-radius-neighbor handle avoids constructing and uploading the "
            "double-precision exact search device buffer for float32 aggregate/self-query routes"
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "m7_reopen_candidate_pending_2ai_review": False,
        "material_speedup_floor": material_floor,
        "evidence": {
            "previous_old_prepared_query": _rel(PREVIOUS_OLD_JSON),
            "previous_self_query": _rel(PREVIOUS_SELF_QUERY_JSON),
            "lazy_old_prepared_query": _rel(LAZY_OLD_JSON),
            "lazy_self_query": _rel(LAZY_SELF_QUERY_JSON),
            "lazy_cupy_grid_reference": _rel(LAZY_CUPY_JSON),
        },
        "measurements": {
            "previous_self_query": {
                "hot_median_sec": _median(previous_self),
                "input_load_sec": previous_self["input_load_sec"],
                "input_pack_sec": previous_self["input_pack_sec"],
                "execution_prepare_sec": previous_self["execution_prepare_sec"],
                "cold_plus_query_sec": previous_self_cold,
                "runner_wall_sec": previous_self_wall,
            },
            "lazy_old_prepared_query": {
                "hot_median_sec": _median(lazy_old),
                "input_load_sec": lazy_old["input_load_sec"],
                "input_pack_sec": lazy_old["input_pack_sec"],
                "execution_prepare_sec": lazy_old["execution_prepare_sec"],
                "cold_plus_query_sec": lazy_old_cold,
                "runner_wall_sec": lazy_old_wall,
            },
            "lazy_self_query": {
                "hot_median_sec": _median(lazy_self),
                "input_load_sec": lazy_self["input_load_sec"],
                "input_pack_sec": lazy_self["input_pack_sec"],
                "execution_prepare_sec": lazy_self["execution_prepare_sec"],
                "cold_plus_query_sec": lazy_self_cold,
                "runner_wall_sec": lazy_self_wall,
            },
            "lazy_cupy_grid_reference": {
                "hot_median_sec": _median(lazy_cupy),
                "input_load_sec": lazy_cupy["input_load_sec"],
                "grid_prepare_sec": lazy_cupy["grid_prepare_sec"],
                "cold_plus_query_sec": lazy_cupy_cold,
                "runner_wall_sec": lazy_cupy_wall,
            },
        },
        "comparisons": comparisons,
        "parity": {
            "integer_signature_match_with_cupy": integer_match_cupy,
            "integer_signature_match_with_lazy_old_prepared_query": integer_match_old,
            "sum_distance_delta_lazy_self_minus_cupy": sum_delta,
            "sum_distance_relative_error": sum_relative_error,
            "sum_distance_relative_tolerance": 1.0e-4,
        },
        "not_m7_blockers": [
            (
                "Lazy exact improves self-query execution_prepare by only "
                f"{comparisons['self_query_prepare_reduction_prepatch_to_lazy']:.3f}x and "
                "self-query cold-plus-query by only "
                f"{comparisons['self_query_cold_plus_query_reduction_prepatch_to_lazy']:.3f}x."
            ),
            (
                "Lazy self-query over same-day CuPy grid is "
                f"{comparisons['lazy_self_query_over_cupy_cold_plus_query_speedup']:.3f}x "
                "cold-plus-query and "
                f"{comparisons['lazy_self_query_over_cupy_runner_wall_speedup']:.3f}x "
                "runner-wall, both below the 2.0x material floor."
            ),
            "This is a generic overhead reduction, not a broad RTNN, V2, or whole-app claim.",
            "No external review or 2-AI consensus has promoted this row.",
        ],
        "interpretation": (
            "Lazy exact-search materialization is a valid generic engine cleanup: float32 "
            "aggregate/self-query routes no longer pay for the unused double-precision exact "
            "search device buffer during prepared search construction. The RTX POD rerun shows "
            "real but small movement: self-query prepare improves by "
            f"{comparisons['self_query_prepare_reduction_prepatch_to_lazy']:.3f}x and "
            "self-query cold-plus-query improves by "
            f"{comparisons['self_query_cold_plus_query_reduction_prepatch_to_lazy']:.3f}x. "
            "It does not solve the V3 RTNN wall problem."
        ),
        "next_engine_action": (
            "Keep RTNN ranked_summary open. The remaining useful work is larger generic "
            "ingestion/column residency or prepared-handle scope review, not more wording "
            "around this small lazy-exact improvement."
        ),
        "forbidden_shortcuts": [
            "Do not call lazy exact a major V3 performance row.",
            "Do not quote the hot-path CuPy ratio without the cold and runner-wall ratios.",
            "Do not claim RTNN, nearest-neighbor, or V3-over-V2 broad speedup from this packet.",
            "Do not promote this to M7 without external review and a material cold/runner result.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Record lazy exact-search materialization as a generic RTNN overhead reduction "
                "while keeping RTNN ranked_summary out of M7."
            ),
            "was_i_foolish": (
                "No. This records the optimization and its limits instead of pretending that "
                "a small prepare reduction fixes the V3 wall-clock problem."
            ),
            "foolish_actions": (
                "It would be foolish to market the lazy-exact change as a major V3 win, hide "
                "the same-day CuPy wall comparison, or keep tuning RTNN wording instead of "
                "larger ingestion/prepare costs."
            ),
            "other_path": (
                "I could have skipped documenting this because the gain is small, but that "
                "would make the engine change hard to audit and easy to overclaim later."
            ),
            "different_path_now": (
                "Use this packet as a closed small optimization and move to the next larger "
                "generic bottleneck: input/column residency or externally reviewed prepared-handle scope."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    m = payload["measurements"]
    c = payload["comparisons"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 RTNN Lazy Exact Prepare Evidence",
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
        f"- Previous self-query JSON: `{payload['evidence']['previous_self_query']}`",
        f"- Lazy old prepared-query JSON: `{payload['evidence']['lazy_old_prepared_query']}`",
        f"- Lazy self-query JSON: `{payload['evidence']['lazy_self_query']}`",
        f"- Same-day CuPy grid JSON: `{payload['evidence']['lazy_cupy_grid_reference']}`",
        "",
        "## Measurements",
        "",
        "| route | hot median sec | pack/prepare sec | cold+query sec | runner wall sec |",
        "| --- | ---: | ---: | ---: | ---: |",
        (
            "| previous self-query | "
            f"{m['previous_self_query']['hot_median_sec']:.6f} | "
            f"{m['previous_self_query']['input_pack_sec']:.6f} + "
            f"{m['previous_self_query']['execution_prepare_sec']:.6f} | "
            f"{m['previous_self_query']['cold_plus_query_sec']:.6f} | "
            f"{m['previous_self_query']['runner_wall_sec']:.6f} |"
        ),
        (
            "| lazy old prepared-query | "
            f"{m['lazy_old_prepared_query']['hot_median_sec']:.6f} | "
            f"{m['lazy_old_prepared_query']['input_pack_sec']:.6f} + "
            f"{m['lazy_old_prepared_query']['execution_prepare_sec']:.6f} | "
            f"{m['lazy_old_prepared_query']['cold_plus_query_sec']:.6f} | "
            f"{m['lazy_old_prepared_query']['runner_wall_sec']:.6f} |"
        ),
        (
            "| lazy self-query | "
            f"{m['lazy_self_query']['hot_median_sec']:.6f} | "
            f"{m['lazy_self_query']['input_pack_sec']:.6f} + "
            f"{m['lazy_self_query']['execution_prepare_sec']:.6f} | "
            f"{m['lazy_self_query']['cold_plus_query_sec']:.6f} | "
            f"{m['lazy_self_query']['runner_wall_sec']:.6f} |"
        ),
        (
            "| same-day CuPy grid | "
            f"{m['lazy_cupy_grid_reference']['hot_median_sec']:.6f} | "
            f"0.000000 + {m['lazy_cupy_grid_reference']['grid_prepare_sec']:.6f} | "
            f"{m['lazy_cupy_grid_reference']['cold_plus_query_sec']:.6f} | "
            f"{m['lazy_cupy_grid_reference']['runner_wall_sec']:.6f} |"
        ),
        "",
        "## Comparisons",
        "",
        f"- Self-query prepare reduction from lazy exact: `{c['self_query_prepare_reduction_prepatch_to_lazy']:.3f}x`",
        f"- Self-query cold+query reduction from lazy exact: `{c['self_query_cold_plus_query_reduction_prepatch_to_lazy']:.3f}x`",
        f"- Self-query runner-wall reduction from lazy exact: `{c['self_query_runner_wall_reduction_prepatch_to_lazy']:.3f}x`",
        f"- Lazy old prepared-query to lazy self-query hot speedup: `{c['lazy_old_prepared_query_to_lazy_self_query_hot_speedup']:.3f}x`",
        f"- Lazy self-query over CuPy hot-query speedup: `{c['lazy_self_query_over_cupy_hot_speedup']:.3f}x`",
        f"- Lazy self-query over CuPy cold+query speedup: `{c['lazy_self_query_over_cupy_cold_plus_query_speedup']:.3f}x`",
        f"- Lazy self-query over CuPy runner-wall speedup: `{c['lazy_self_query_over_cupy_runner_wall_speedup']:.3f}x`",
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
