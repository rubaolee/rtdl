#!/usr/bin/env python3
"""Build Goal5367 explicit author-radius lb probe evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"

GOAL5365 = RESULTS / "xhd_goal5365_rtdl_lb_counterpart_gate.json"
GOAL5366 = RESULTS / "xhd_goal5366_lb_denominator_reconciliation.json"
AUTHOR_RADIUS_PROBE = RESULTS / "xhd_goal5367_rtdl_lb256_author_radius_probe_pod.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _route_row(payload: dict[str, Any]) -> dict[str, Any]:
    directed = payload["rtdl_route"]["directed_a_to_b"]
    memory = directed["frontier_native_memory_telemetry"]
    phases = directed["phase_timings_sec"]
    return {
        "hd_result": float(directed["distance"]),
        "radius": float(directed["radius"]),
        "heavy_offload_peak_rows": int(memory["heavy_offload_peak_rows"]),
        "author_width_candidate_bytes": int(memory["heavy_offload_peak_rows"]) * 2 * 4,
        "generic_queue_peak_bytes": int(memory["heavy_offload_queue_peak_bytes"]),
        "attempted_count": int(memory["attempted_count"]),
        "emitted_count": int(memory["emitted_count"]),
        "candidate_distance_evaluations": int(directed["candidate_distance_evaluations"]),
        "rtdl_route_sec": float(payload["run_phases"]["rtdl_route_sec"]),
        "frontier_rows_sec": float(phases["frontier_rows"]),
        "nearest_continuation_sec": float(phases["nearest_continuation"]),
        "frontier_native_phase_timings": directed.get("frontier_native_phase_timings"),
    }


def build_artifact(*, tolerance: float = 5.0e-6) -> dict[str, Any]:
    goal5365 = _load_json(GOAL5365)
    goal5366 = _load_json(GOAL5366)
    probe = _load_json(AUTHOR_RADIUS_PROBE)
    raw_full_cover = _load_json(Path(goal5365["input_artifacts"]["rtdl_lb256"]))
    author = goal5365["author_pair"]["lb_256"]
    author_rows = int(author["iteration_3"]["OffloadingSize"])
    author_radius = float(author["iteration_3"]["Radius"])
    author_hd = float(author["hd_result"])

    full_cover = _route_row(raw_full_cover)
    author_radius_route = _route_row(probe)
    full_cover_abs_diff = abs(author_hd - full_cover["hd_result"])
    author_radius_abs_diff = abs(author_hd - author_radius_route["hd_result"])
    explicit_radius_matches_author_value = author_radius_abs_diff <= tolerance
    radius_aligned = abs(author_radius_route["radius"] - author_radius) <= 1.0e-12
    row_count_parity = author_radius_route["heavy_offload_peak_rows"] == author_rows
    row_delta_vs_author = author_rows - author_radius_route["heavy_offload_peak_rows"]
    row_delta_vs_full_cover = full_cover["heavy_offload_peak_rows"] - author_radius_route["heavy_offload_peak_rows"]

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5367.lb_author_radius_probe.v1",
        "goal": "Goal5367",
        "date": "2026-07-09",
        "status": "author_radius_lb_probe_ready__radius_alignment_not_sufficient_for_row_parity",
        "purpose": (
            "Test whether setting the RTDL lb256 route radius to the author "
            "iteration radius explains the offload row-count denominator gap."
        ),
        "input_artifacts": {
            "goal5365": str(GOAL5365),
            "goal5366": str(GOAL5366),
            "rtdl_full_cover_lb256": str(goal5365["input_artifacts"]["rtdl_lb256"]),
            "rtdl_author_radius_probe": str(AUTHOR_RADIUS_PROBE),
        },
        "author_reference": {
            "input_scope": goal5365["author_pair"]["input_scope"],
            "lb": int(author["lb"]),
            "hd_result": author_hd,
            "offloading_size_rows": author_rows,
            "wl_heavy_peak_bytes": int(author["memory"]["WL Heavy Peak"]),
            "iteration_radius": author_radius,
            "iteration_num_input_points": int(author["iteration_3"]["NumInputPoints"]),
        },
        "rtdl_routes": {
            "full_cover_radius_lb256_from_goal5365": full_cover,
            "author_iteration_radius_lb256_probe": author_radius_route,
        },
        "comparison": {
            "tolerance": tolerance,
            "full_cover_abs_diff": full_cover_abs_diff,
            "author_radius_abs_diff": author_radius_abs_diff,
            "explicit_radius_matches_author_value": explicit_radius_matches_author_value,
            "radius_aligned": radius_aligned,
            "row_count_parity": row_count_parity,
            "full_cover_row_count": full_cover["heavy_offload_peak_rows"],
            "author_radius_row_count": author_radius_route["heavy_offload_peak_rows"],
            "author_offloading_size_rows": author_rows,
            "row_delta_author_minus_author_radius_rtdl": row_delta_vs_author,
            "row_ratio_author_radius_rtdl_div_author": author_radius_route["heavy_offload_peak_rows"] / author_rows,
            "row_delta_full_cover_minus_author_radius": row_delta_vs_full_cover,
            "author_radius_reduces_rows_vs_full_cover": author_radius_route["heavy_offload_peak_rows"]
            < full_cover["heavy_offload_peak_rows"],
            "author_radius_closes_denominator_gap": False,
        },
        "interpretation": {
            "result": (
                "Aligning RTDL radius to the author iteration radius preserves the "
                "HD value but reduces RTDL heavy rows from the full-cover probe and "
                "moves farther from the author OffloadingSize row count."
            ),
            "denominator_implication": (
                "The row-count gap is not solved by radius alignment alone. The "
                "next parity target must align author queue/in_queue/cmin2/offload "
                "iteration semantics, not only the scalar radius."
            ),
            "depends_on_goal5366": goal5366["exit_label"],
        },
        "decision": {
            "explicit_lb_support_authorized_now": False,
            "row_count_parity_authorized_now": False,
            "next_gate": (
                "author_queue_aligned_lb_trace_with_in_queue_cmin2_and_raw_offload_denominator"
            ),
        },
        "claim_boundary": {
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "same_denominator_memory_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "rtdl_author_performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "exit_label": "author_radius_alignment_preserves_value_but_not_lb_denominator_parity",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5367_lb_author_radius_probe.json",
    )
    args = parser.parse_args()
    payload = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": payload["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
