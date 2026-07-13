#!/usr/bin/env python3
"""Build Goal5365 RTDL lb0/lb256 counterpart gate evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"

AUTHOR_CONTRACT = RESULTS / "xhd_goal5364_lb_trace_gate_author_pair_contract.json"
RTDL_LB0 = RESULTS / "xhd_goal5365_rtdl_lb0_disabled_raw_dragon_asian_translated_initial_none_pod.json"
RTDL_LB256 = RESULTS / "xhd_goal5365_rtdl_lb256_raw_dragon_asian_translated_initial_none_pod.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rtdl_summary(payload: dict[str, Any]) -> dict[str, Any]:
    directed = payload["rtdl_route"]["directed_a_to_b"]
    memory = directed["frontier_native_memory_telemetry"]
    phases = directed["phase_timings_sec"]
    return {
        "input1": payload["input1"],
        "input2": payload["input2"],
        "reference_preprocessing": payload["reference_preprocessing"],
        "grid_shape": payload["grid_shape"],
        "max_inline_points": int(payload["max_inline_points"]),
        "initial_state": payload["initial_state"],
        "frontier_inline_nearest": bool(payload["frontier_inline_nearest"]),
        "hd_result": float(directed["distance"]),
        "source_id": int(directed["source_id"]),
        "target_id": int(directed["target_id"]),
        "frontier_row_count": int(directed["frontier_row_count"]),
        "heavy_offload_peak_rows": int(memory["heavy_offload_peak_rows"]),
        "heavy_offload_queue_peak_bytes_generic_u64": int(memory["heavy_offload_queue_peak_bytes"]),
        "heavy_offload_queue_peak_bytes_author_u32_equivalent": int(memory["heavy_offload_peak_rows"]) * 2 * 4,
        "in_queue_capacity": int(memory["in_queue_capacity"]),
        "miss_queue_capacity": int(memory["miss_queue_capacity"]),
        "rtdl_route_sec": float(payload["run_phases"]["rtdl_route_sec"]),
        "total_sec": float(payload["run_phases"]["total_sec"]),
        "frontier_rows_sec": float(phases["frontier_rows"]),
        "nearest_continuation_sec": float(phases["nearest_continuation"]),
        "frontier_native_phase_timings": directed.get("frontier_native_phase_timings"),
        "candidate_distance_evaluations": int(directed["candidate_distance_evaluations"]),
    }


def build_artifact(*, tolerance: float = 5.0e-6) -> dict[str, Any]:
    contract = _load_json(AUTHOR_CONTRACT)
    rtdl_lb0_payload = _load_json(RTDL_LB0)
    rtdl_lb256_payload = _load_json(RTDL_LB256)
    author = contract["author_pair"]
    author_lb0 = author["lb_0"]
    author_lb256 = author["lb_256"]
    rtdl_lb0 = _rtdl_summary(rtdl_lb0_payload)
    rtdl_lb256 = _rtdl_summary(rtdl_lb256_payload)

    lb0_abs_diff = abs(float(author_lb0["hd_result"]) - rtdl_lb0["hd_result"])
    lb256_abs_diff = abs(float(author_lb256["hd_result"]) - rtdl_lb256["hd_result"])
    input_match = (
        rtdl_lb0["input1"].endswith("/tmp/xhd_goal5234/data/dragon.ply")
        and rtdl_lb0["input2"].endswith("/tmp/xhd_goal5234/data/asian_dragon.ply")
        and rtdl_lb256["input1"] == rtdl_lb0["input1"]
        and rtdl_lb256["input2"] == rtdl_lb0["input2"]
    )
    preprocessing_match = (
        rtdl_lb0["reference_preprocessing"] == ["translate_each_input_to_min_bound"]
        and rtdl_lb256["reference_preprocessing"] == ["translate_each_input_to_min_bound"]
    )
    lb0_behavior = (
        rtdl_lb0["heavy_offload_peak_rows"] == 0
        and rtdl_lb0["heavy_offload_queue_peak_bytes_generic_u64"] == 0
        and rtdl_lb0["heavy_offload_queue_peak_bytes_author_u32_equivalent"] == 0
    )
    lb256_behavior = (
        rtdl_lb256["heavy_offload_peak_rows"] > 0
        and rtdl_lb256["heavy_offload_queue_peak_bytes_generic_u64"] > 0
        and rtdl_lb256["heavy_offload_queue_peak_bytes_author_u32_equivalent"] > 0
    )
    value_match = lb0_abs_diff <= tolerance and lb256_abs_diff <= tolerance
    matched = bool(input_match and preprocessing_match and lb0_behavior and lb256_behavior and value_match)

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5365.rtdl_lb_counterpart_gate.v1",
        "goal": "Goal5365",
        "date": "2026-07-09",
        "status": (
            "rtdl_lb0_lb256_counterpart_behavior_gate_passed__row_count_denominator_not_parity"
            if matched
            else "rtdl_lb0_lb256_counterpart_behavior_gate_failed"
        ),
        "purpose": (
            "Run RTDL same-input lb0/lb256 counterpart routes against the Goal5364 "
            "author-pair contract and decide whether the behavior gate is strong "
            "enough to consider a narrow explicit -lb mapping later."
        ),
        "input_artifacts": {
            "author_contract": str(AUTHOR_CONTRACT),
            "rtdl_lb0": str(RTDL_LB0),
            "rtdl_lb256": str(RTDL_LB256),
        },
        "author_pair": {
            "level": author["level"],
            "input_scope": author["input_scope"],
            "lb_0": author_lb0,
            "lb_256": author_lb256,
        },
        "rtdl_counterparts": {
            "lb0_disabled_offload": rtdl_lb0,
            "lb256_heavy_offload": rtdl_lb256,
        },
        "comparison": {
            "matched": matched,
            "tolerance": tolerance,
            "input_match": bool(input_match),
            "preprocessing_match": bool(preprocessing_match),
            "value_match": bool(value_match),
            "lb0_abs_diff": lb0_abs_diff,
            "lb256_abs_diff": lb256_abs_diff,
            "lb0_behavior_zero_offload": bool(lb0_behavior),
            "lb256_behavior_positive_offload": bool(lb256_behavior),
            "author_lb256_offloading_size": int(author_lb256["iteration_3"]["OffloadingSize"]),
            "rtdl_lb256_heavy_offload_peak_rows": rtdl_lb256["heavy_offload_peak_rows"],
            "author_lb256_wl_heavy_peak_bytes": int(author_lb256["memory"]["WL Heavy Peak"]),
            "rtdl_lb256_author_width_wl_heavy_peak_candidate_bytes": rtdl_lb256[
                "heavy_offload_queue_peak_bytes_author_u32_equivalent"
            ],
            "row_count_or_byte_parity_claimed": False,
            "performance_ratio_claimed": False,
        },
        "decision": {
            "bounded_lb_behavior_gate_passed": bool(matched),
            "explicit_lb_support_authorized_now": False,
            "reason_support_not_authorized": (
                "The same-input behavior gate passes at the qualitative level "
                "(value match, lb0 zero offload, lb256 positive offload), but "
                "author and RTDL offload row counts / byte denominators are not "
                "equal and this is a Level-B temporary input rather than the full "
                "Figure 7 matrix."
            ),
            "next_allowed_goal": (
                "Add a narrow explicit -lb mapping only if the owner accepts this "
                "behavior-level gate, or tighten the gate to row-count/denominator "
                "parity before exposing -lb."
            ),
        },
        "claim_boundary": {
            "explicit_lb_support_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "same_denominator_memory_claimed": False,
            "row_count_parity_claimed": False,
            "rtdl_author_performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "exit_label": "rtdl_lb_counterpart_behavior_gate_passed__decide_narrow_lb_mapping_or_tighten",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5365_rtdl_lb_counterpart_gate.json",
    )
    parser.add_argument("--tolerance", type=float, default=5.0e-6)
    args = parser.parse_args()
    payload = build_artifact(tolerance=args.tolerance)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": payload["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
