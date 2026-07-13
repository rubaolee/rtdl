#!/usr/bin/env python3
"""Build Goal5355 author radius-trace mapping evidence.

This goal maps existing author ``hd_exec`` JSON iteration traces to the generic
RTDL radius-growth schedule helper.  It does not execute an RTDL route and does
not enable explicit ``-tune_radius`` handling in the app wrapper.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"


DEFAULT_AUTHOR_CASES = [
    {
        "case_id": "full_public_dragon_happy_buddha_goal5186",
        "author_json": RESULTS / "xhd_full_public_author_hd_exec_goal5186_graphics_dragon_happy_buddha_2026-07-08.json",
    },
    {
        "case_id": "res4full_dragon_happy_buddha_perf",
        "author_json": RESULTS / "perf_res4full_author_hd_exec_output_pod.json",
    },
    {
        "case_id": "bounded3d_author_gate",
        "author_json": RESULTS / "bounded3d_author_hd_exec_output_pod.json",
    },
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _first_repeat(payload: dict[str, Any]) -> dict[str, Any]:
    running = payload.get("Running")
    if not isinstance(running, dict):
        raise ValueError("author JSON missing Running object")
    repeats = running.get("Repeats")
    if not isinstance(repeats, list) or not repeats or not isinstance(repeats[0], dict):
        raise ValueError("author JSON missing Running.Repeats[0]")
    return repeats[0]


def _first_repeat_iterations(payload: dict[str, Any]) -> list[dict[str, Any]]:
    repeat = _first_repeat(payload)
    iterations = repeat.get("Iterations")
    if not isinstance(iterations, list):
        raise ValueError("author JSON missing Running.Repeats[0].Iterations")
    return [row for row in iterations if isinstance(row, dict)]


def _target_cell_diagonal(payload: dict[str, Any]) -> float:
    repeat = _first_repeat(payload)
    grid_resolution = repeat.get("GridResolution")
    if not isinstance(grid_resolution, list) or not grid_resolution:
        raise ValueError("author JSON missing repeat GridResolution")
    input_obj = payload.get("Input")
    if not isinstance(input_obj, dict):
        raise ValueError("author JSON missing Input object")
    files = input_obj.get("Files")
    if not isinstance(files, list) or len(files) < 2 or not isinstance(files[1], dict):
        raise ValueError("author JSON missing Input.Files[1] target metadata")
    target_mbr = files[1].get("MBR")
    if not isinstance(target_mbr, list) or len(target_mbr) != len(grid_resolution):
        raise ValueError("target MBR dimensionality must match GridResolution")
    squared = 0.0
    axis_lengths: list[float] = []
    for axis, (axis_mbr, resolution) in enumerate(zip(target_mbr, grid_resolution)):
        if not isinstance(axis_mbr, dict):
            raise ValueError(f"target MBR axis {axis} is not an object")
        lower = float(axis_mbr["Lower"])
        upper = float(axis_mbr["Upper"])
        resolution_i = int(resolution)
        if resolution_i <= 0:
            raise ValueError("GridResolution values must be positive")
        length = (upper - lower) / float(resolution_i)
        axis_lengths.append(length)
        squared += length * length
    return math.sqrt(squared)


def _author_tune_radius_mode(payload: dict[str, Any]) -> str:
    running = payload.get("Running")
    if isinstance(running, dict) and running.get("TuneRadius") is not None:
        return str(running["TuneRadius"])
    return "adaptive"


def _compare_case(case_id: str, author_json: Path, *, tolerance: float) -> dict[str, Any]:
    payload = _load_json(author_json)
    repeat = _first_repeat(payload)
    iterations = _first_repeat_iterations(payload)
    mode = _author_tune_radius_mode(payload)
    cell_diagonal = _target_cell_diagonal(payload)
    upper = float(repeat["HDUpperBound"])
    transitions: list[dict[str, Any]] = []
    for left, right in zip(iterations, iterations[1:]):
        step = rt.radius_growth_step(
            radius=float(left["Radius"]),
            hd_upper_bound=upper,
            cell_diagonal=cell_diagonal,
            last_input_count=int(left["NumInputPoints"]),
            next_input_count=int(left["NumOutputPoints"]),
            mode=mode,  # type: ignore[arg-type]
        )
        observed = float(right["Radius"])
        abs_diff = abs(float(step.next_radius) - observed)
        transitions.append(
            {
                "from_iteration": int(left["Iteration"]),
                "to_iteration": int(right["Iteration"]),
                "mode": mode,
                "cell_diagonal": cell_diagonal,
                "previous_radius": float(left["Radius"]),
                "observed_next_radius": observed,
                "predicted_next_radius": float(step.next_radius),
                "abs_diff": abs_diff,
                "matched": abs_diff <= tolerance,
                "step": step.to_dict(),
            }
        )
    terminal = None
    if iterations:
        last = iterations[-1]
        terminal_step = rt.radius_growth_step(
            radius=float(last["Radius"]),
            hd_upper_bound=upper,
            cell_diagonal=cell_diagonal,
            last_input_count=int(last["NumInputPoints"]),
            next_input_count=int(last["NumOutputPoints"]),
            mode=mode,  # type: ignore[arg-type]
        )
        terminal = {
            "iteration": int(last["Iteration"]),
            "num_output_points": int(last["NumOutputPoints"]),
            "step_update_applied": bool(terminal_step.update_applied),
            "predicted_next_radius": float(terminal_step.next_radius),
            "reason": (
                "No following author iteration exists. When NumOutputPoints is zero, "
                "the generic helper also stops updating."
            ),
        }
    return {
        "case_id": case_id,
        "author_json": str(author_json),
        "hd_result": payload.get("HDResult"),
        "mode": mode,
        "grid_resolution": repeat.get("GridResolution"),
        "hd_upper_bound": repeat.get("HDUpperBound"),
        "cell_diagonal_source": "Input.Files[1].MBR / Running.Repeats[0].GridResolution",
        "derived_target_cell_diagonal": cell_diagonal,
        "iteration_count": len(iterations),
        "transition_count": len(transitions),
        "transitions": transitions,
        "all_transitions_matched": all(bool(row["matched"]) for row in transitions),
        "terminal": terminal,
    }


def build_artifact(*, tolerance: float) -> dict[str, Any]:
    cases = [_compare_case(item["case_id"], Path(item["author_json"]), tolerance=tolerance) for item in DEFAULT_AUTHOR_CASES]
    transition_cases = [case for case in cases if int(case["transition_count"]) > 0]
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5355.radius_trace_mapping.v1",
        "goal": "Goal5355",
        "date": "2026-07-09",
        "status": "radius_trace_mapping_matches_available_author_json__route_still_fail_closed",
        "purpose": (
            "Compare available author hd_exec radius iteration traces against the "
            "generic RTDL radius_growth_step helper, without enabling explicit "
            "author tune_radius route behavior."
        ),
        "tolerance": tolerance,
        "cases": cases,
        "case_count": len(cases),
        "transition_case_count": len(transition_cases),
        "total_transition_count": sum(int(case["transition_count"]) for case in cases),
        "all_transition_cases_matched": bool(transition_cases)
        and all(bool(case["all_transitions_matched"]) for case in transition_cases),
        "rtdl_api": {
            "module": "src/rtdsl/radius_schedule.py",
            "helper": "radius_growth_step",
            "contract": rt.RADIUS_GROWTH_SCHEDULE_CONTRACT_VERSION,
            "app_semantics": "none",
        },
        "current_xhd_mapping_status": {
            "author_json_trace_mapping_available": True,
            "route_uses_tune_radius_helper": False,
            "run_xhd_rtdl_hd_exec_explicit_tune_radius_still_fail_closed": True,
            "reason": (
                "Existing author JSON traces validate the schedule transition math, "
                "but RTDL route behavior still needs a separate bounded/Level-B trace "
                "gate before explicit author -tune_radius can be accepted."
            ),
        },
        "claim_boundary": {
            "author_rt_core_algorithm_equivalence_claimed": False,
            "author_tune_radius_route_mapping_claimed": False,
            "figure8_reproduction_claimed": False,
            "performance_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "recommended_next_targets": [
            "add_app_owned_radius_trace_metadata_to_cell_mbr_route_under_internal_flag",
            "compare_author_and_rtdl_radius_iteration_trace_on_bounded_or_level_b_input",
            "only_then_consider_accepting_explicit_author_tune_radius",
        ],
        "exit_label": "radius_trace_mapping_verified_for_available_author_json__await_route_trace_gate",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5355_radius_trace_mapping.json",
    )
    parser.add_argument("--tolerance", type=float, default=1.0e-6)
    args = parser.parse_args()
    payload = build_artifact(tolerance=float(args.tolerance))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "status": payload["status"],
                "all_transition_cases_matched": payload["all_transition_cases_matched"],
                "total_transition_count": payload["total_transition_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
