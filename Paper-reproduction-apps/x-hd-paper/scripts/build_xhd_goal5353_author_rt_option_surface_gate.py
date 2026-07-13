#!/usr/bin/env python3
"""Build the Goal5353 X-HD author RT option-surface gate artifact."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"
RUNNER_PATH = APP_ROOT / "scripts" / "run_xhd_rtdl_hd_exec.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_xhd_rtdl_hd_exec_goal5353", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _parse_runner_args(runner: Any, extra: list[str]):
    base = [
        "-input1",
        "author-rt-option-surface-gate-input-a.ply",
        "-input2",
        "author-rt-option-surface-gate-input-b.ply",
        "-json",
        "author-rt-option-surface-gate-output.json",
        "-variant",
        "rt",
        "-execution",
        "gpu",
    ]
    return runner.build_parser().parse_args(base + extra)


def build_gate_artifact() -> dict[str, Any]:
    runner = _load_runner()
    default_args = _parse_runner_args(runner, [])
    route_label = runner._select_route_label(
        requested=default_args.rtdl_route,
        n_dims=default_args.n_dims,
        execution=default_args.execution,
    )
    default_surface = runner._author_rt_option_surface(default_args, route_label=route_label)

    explicit_args = _parse_runner_args(
        runner,
        [
            "-fast_build_bvh=true",
            "-rebuild_bvh=true",
            "-eb=false",
            "-prune=false",
            "-lb",
            "0",
            "-n_points_cell",
            "8",
            "-tune_grid=true",
            "-tune_radius",
            "double",
        ],
    )
    explicit_route_label = runner._select_route_label(
        requested=explicit_args.rtdl_route,
        n_dims=explicit_args.n_dims,
        execution=explicit_args.execution,
    )
    explicit_surface = runner._author_rt_option_surface(explicit_args, route_label=explicit_route_label)
    fail_closed_payload = runner._unsupported_author_rt_options_payload(
        explicit_args, route_label=explicit_route_label, surface=explicit_surface
    )

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5353.author_rt_option_surface_gate.v1",
        "goal": "Goal5353",
        "date": "2026-07-09",
        "status": "author_rt_option_surface_gate_ready__explicit_options_fail_closed",
        "purpose": (
            "Expose the author RT option surface in the RTDL hd_exec-compatible "
            "wrapper as an auditable fail-closed gate instead of silently ignoring "
            "author RT flags."
        ),
        "runner": str(RUNNER_PATH.relative_to(ROOT)),
        "author_rt_option_specs": runner.AUTHOR_RT_OPTION_SPECS,
        "radius_cli_flag_present": "radius" in runner.AUTHOR_RT_OPTION_SPECS,
        "default_surface": default_surface,
        "explicit_surface": explicit_surface,
        "fail_closed_payload_status": fail_closed_payload["RTDL"]["status"],
        "fail_closed_payload_claim_boundary": fail_closed_payload["RTDL"]["claim_boundary"],
        "claim_boundary": {
            "author_rt_option_surface_complete_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "performance_parity_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "interpretation": (
            "Omitted author RT defaults are recorded for audit only. Explicit author "
            "RT options fail closed until a later goal maps each option to generic "
            "RTDL behavior with evidence. This improves user-facing correctness "
            "over argparse rejection or silent ignore, but it does not close author "
            "RT-core parity."
        ),
        "recommended_next_targets": [
            "map_tune_radius_to_generic_radius_schedule_or_keep_unsupported",
            "map_lb_heavy_offload_to_generic_worklist_denominator_or_keep_unsupported",
            "map_eb_prune_to_exact_scalar_vs_exact_witness_contracts_or_keep_unsupported",
        ],
        "exit_label": "author_rt_option_surface_gate_ready__next_target_semantic_mapping",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5353_author_rt_option_surface_gate.json",
    )
    args = parser.parse_args()
    payload = build_gate_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": payload["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
