#!/usr/bin/env python3
"""Build Goal5356 route-radius trace metadata evidence.

This goal verifies that the X-HD app-owned cell-MBR route can emit internal
radius trace metadata under an explicit flag.  The emitted trace is deliberately
marked as single-pass / not author-queue-aligned; it is preparation for a later
author-vs-RTDL trace gate, not tune_radius support.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"))

import run_xhd_cell_mbr_frontier_route_gate as cell_mbr_gate
import run_xhd_rtdl_hd_exec as hd_exec


APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"
FIXTURES = APP_ROOT / "data" / "fixtures"


def _bounded3d_args() -> SimpleNamespace:
    return SimpleNamespace(
        input1=FIXTURES / "bounded3d_a.wkt",
        input2=FIXTURES / "bounded3d_b.wkt",
        n_dims=3,
        input_type="wkt",
        lift_2d_to_3d_zero_z=False,
        normalize_each_input_to_author_unit_box=False,
        author_float32_normalization=False,
        translate_each_input_to_min_bound=False,
        backend="numpy",
        grid_shape="1,1,1",
        radius=None,
        max_inline_points=64,
        initial_state="none",
        seed_cell_budget=4,
        frontier_nearest_executor="auto",
        local_grid_seed_executor="auto",
        grid_branch_bound_seed_executor="auto",
        frontier_row_order="sorted",
        cell_order="native",
        grid_cell_point_order="point-id",
        grid_cell_builder="numpy",
        frontier_inline_nearest=False,
        skip_frontier_if_exact_seed=False,
        global_bound_early_break=False,
        collect_inline_stats=False,
        collect_frontier_native_phase_timings=False,
        emit_radius_trace_metadata=True,
        frontier_row_capacity=None,
        direction_mode="directed-a-to-b",
        validation_mode="none",
        author_json=None,
        summary="",
        tolerance=1.0e-6,
    )


def _hd_exec_fail_closed_status() -> dict[str, Any]:
    parser = hd_exec.build_parser()
    args = parser.parse_args(
        [
            "-input1",
            str(FIXTURES / "bounded3d_a.wkt"),
            "-input2",
            str(FIXTURES / "bounded3d_b.wkt"),
            "-n_dims",
            "3",
            "-input_type",
            "wkt",
            "-variant",
            "rt",
            "-execution",
            "gpu",
            "-json",
            "unused.json",
            "-tune_radius",
            "adaptive",
            "--emit-radius-trace-metadata",
        ]
    )
    route_label = hd_exec._select_route_label(
        requested=args.rtdl_route,
        n_dims=args.n_dims,
        execution=args.execution,
    )
    surface = hd_exec._author_rt_option_surface(args, route_label=route_label)
    payload = hd_exec._unsupported_author_rt_options_payload(args, route_label=route_label, surface=surface)
    return {
        "explicit_tune_radius_status": payload["RTDL"]["status"],
        "explicit_author_rt_options": surface["explicit_author_rt_options"],
        "tune_radius_effective_value": surface["options"]["tune_radius"]["effective_value"],
        "route_executed": False,
    }


def build_artifact() -> dict[str, Any]:
    summary = cell_mbr_gate.build_summary(_bounded3d_args())
    trace = summary["radius_trace_metadata"]
    direction = trace["directions"][0]
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5356.route_radius_trace_metadata.v1",
        "goal": "Goal5356",
        "date": "2026-07-09",
        "status": "route_radius_trace_metadata_available__single_pass_not_author_queue_aligned",
        "purpose": (
            "Verify that the X-HD app-owned cell-MBR route can emit internal "
            "radius trace metadata under an explicit flag, while preserving the "
            "boundary that author tune_radius route semantics are not enabled."
        ),
        "route_probe": {
            "input_fixture": "bounded3d_a.wkt -> bounded3d_b.wkt",
            "backend": summary["backend"],
            "route": summary["rtdl_route"]["route"],
            "direction_mode": summary["direction_mode"],
            "emit_radius_trace_metadata": summary["emit_radius_trace_metadata"],
            "hd_result": summary["author_comparison_distance"],
            "point_count_a": summary["point_count_a"],
            "point_count_b": summary["point_count_b"],
            "grid_shape": summary["grid_shape"],
        },
        "radius_trace_metadata": trace,
        "trace_probe_summary": {
            "status": trace["status"],
            "route_iteration_model": trace["route_iteration_model"],
            "author_queue_semantics_aligned": trace["author_queue_semantics_aligned"],
            "author_trace_comparison_ready": trace["author_trace_comparison_ready"],
            "route_uses_radius_growth_helper": trace["route_uses_radius_growth_helper"],
            "direction_count": len(trace["directions"]),
            "first_direction_radius": direction["radius"],
            "first_direction_num_input_points": direction["num_input_points"],
            "first_direction_num_output_points": direction["num_output_points"],
        },
        "explicit_tune_radius_fail_closed_check": _hd_exec_fail_closed_status(),
        "claim_boundary": {
            "author_tune_radius_route_mapping_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "figure8_reproduction_claimed": False,
            "performance_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "recommended_next_targets": [
            "compare_author_and_rtdl_radius_trace_on_bounded_or_level_b_input",
            "only_if_trace_gate_passes_consider_accepting_explicit_author_tune_radius",
        ],
        "exit_label": "route_radius_trace_metadata_ready__await_author_rtdl_trace_comparison",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5356_route_radius_trace_metadata.json",
    )
    args = parser.parse_args()
    payload = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "status": payload["status"],
                "trace_status": payload["trace_probe_summary"]["status"],
                "explicit_tune_radius_status": payload["explicit_tune_radius_fail_closed_check"][
                    "explicit_tune_radius_status"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
