from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5371_inline_global_bound_lb_probe.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact() -> dict[str, Any]:
    goal5367 = _read_json(RESULTS / "xhd_goal5367_lb_author_radius_probe.json")
    goal5368 = _read_json(RESULTS / "xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json")
    inline = _read_json(RESULTS / "xhd_goal5371_dragon_asian_lb256_author_radius_inline_kind_count_pod.json")
    inline_global = _read_json(
        RESULTS / "xhd_goal5371_dragon_asian_lb256_author_radius_inline_global_bound_kind_count_pod.json"
    )

    author_rows = int(goal5367["author_reference"]["offloading_size_rows"])
    materialized_rows = int(goal5367["comparison"]["author_radius_row_count"])
    noinline_rows = int(goal5368["comparison"]["rtdl_noinline_raw_kind2_rows"])
    inline_rows = int(inline["frontier"]["raw_frontier_kind2_rows"])
    inline_global_rows = int(inline_global["frontier"]["raw_frontier_kind2_rows"])
    return {
        "goal": "Goal5371",
        "date": "2026-07-09",
        "schema": "rtdl.paper_reproduction.xhd.goal5371.inline_global_bound_lb_probe.v1",
        "status": "inline_and_global_bound_lb_probes_ready__author_denominator_still_unmatched",
        "exit_label": "inline_payload_and_existing_global_bound_do_not_explain_author_offloading_size",
        "purpose": (
            "Probe whether RTDL inline-nearest payload state or existing generic "
            "global-bound early-break explains the author lb256 OffloadingSize "
            "denominator on Dragon -> AsianDragon."
        ),
        "system_changes": {
            "kind_count_probe_supports_inline_nearest": True,
            "kind_count_probe_supports_global_bound_early_break": True,
            "overflow_telemetry_only_tolerates_missing_nearest_columns": True,
            "core_app_specific_behavior_added": False,
        },
        "input_scope": {
            "input1": inline["input1"],
            "input2": inline["input2"],
            "point_count_a": int(inline["point_count_a"]),
            "point_count_b": int(inline["point_count_b"]),
            "preprocessing": list(inline["preprocessing"]),
            "grid_shape": list(inline["grid_shape"]),
            "radius": float(inline["radius"]),
            "max_inline_points": int(inline["max_inline_points"]),
            "exact_paper_dataset_identity_proven": False,
        },
        "comparison": {
            "author_offloading_size_rows": author_rows,
            "rtdl_author_radius_materialized_rows_from_goal5367": materialized_rows,
            "rtdl_author_radius_noinline_raw_kind2_rows_from_goal5368": noinline_rows,
            "rtdl_author_radius_inline_count_only_kind2_rows": inline_rows,
            "rtdl_author_radius_inline_global_bound_kind2_rows": inline_global_rows,
            "materialized_equals_inline_count_only": materialized_rows == inline_rows,
            "global_bound_changed_kind2_rows": inline_global_rows != inline_rows,
            "inline_div_author": inline_rows / author_rows,
            "inline_global_div_author": inline_global_rows / author_rows,
            "noinline_div_author": noinline_rows / author_rows,
            "inline_row_delta_author_minus_rtdl": author_rows - inline_rows,
            "row_count_parity": inline_rows == author_rows == inline_global_rows,
        },
        "probe_results": {
            "inline_count_only": {
                "path": str(RESULTS / "xhd_goal5371_dragon_asian_lb256_author_radius_inline_kind_count_pod.json"),
                "inline_nearest": bool(inline["inline_nearest"]),
                "global_bound_early_break": bool(inline["global_bound_early_break"]),
                "overflow_telemetry_only": bool(inline["frontier"]["overflow_telemetry_only"]),
                "raw_kind_counts": dict(inline["frontier"]["raw_frontier_kind_counts"]),
                "raw_kind2_rows": inline_rows,
                "frontier_probe_sec": float(inline["timings_sec"]["frontier_probe"]),
            },
            "inline_global_bound_count_only": {
                "path": str(
                    RESULTS / "xhd_goal5371_dragon_asian_lb256_author_radius_inline_global_bound_kind_count_pod.json"
                ),
                "inline_nearest": bool(inline_global["inline_nearest"]),
                "global_bound_early_break": bool(inline_global["global_bound_early_break"]),
                "global_bound_early_break_count": int(
                    inline_global["frontier"]["global_bound_early_break_count"] or 0
                ),
                "global_bound_distance": float(inline_global["frontier"]["global_bound_distance"] or 0.0),
                "overflow_telemetry_only": bool(inline_global["frontier"]["overflow_telemetry_only"]),
                "raw_kind_counts": dict(inline_global["frontier"]["raw_frontier_kind_counts"]),
                "raw_kind2_rows": inline_global_rows,
                "frontier_probe_sec": float(inline_global["timings_sec"]["frontier_probe"]),
            },
        },
        "interpretation": {
            "materialization_sort_hypothesis": (
                "Rejected. The inline count-only raw kind2 count is exactly the "
                "same as the prior materialized author-radius row count."
            ),
            "existing_global_bound_hypothesis": (
                "Rejected for this probe. Enabling RTDL's generic global-bound "
                "early-break changes neither raw kind2 rows nor early-break count."
            ),
            "next_required_alignment": (
                "Model or instrument the author shader status machine: dynamic "
                "cmin2 updates, cmax2 abort status, miss/offload queue updates, "
                "and load-balance post-processing over offloaded cells."
            ),
        },
        "claim_boundary": {
            "generic_probe_capability_claimed": True,
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
        "input_artifacts": {
            "goal5367": str(RESULTS / "xhd_goal5367_lb_author_radius_probe.json"),
            "goal5368": str(RESULTS / "xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json"),
            "inline_pod_probe": str(
                RESULTS / "xhd_goal5371_dragon_asian_lb256_author_radius_inline_kind_count_pod.json"
            ),
            "inline_global_bound_pod_probe": str(
                RESULTS / "xhd_goal5371_dragon_asian_lb256_author_radius_inline_global_bound_kind_count_pod.json"
            ),
        },
    }


def main() -> None:
    artifact = build_artifact()
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, sort_keys=True))


if __name__ == "__main__":
    main()
