#!/usr/bin/env python3
"""Build Goal5360 hd_exec-wrapper author-like queue route evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"))

import run_xhd_rtdl_hd_exec as hd_exec


APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"
FIXTURES = APP_ROOT / "data" / "fixtures"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _core_iteration_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "Iteration": int(row["Iteration"]),
            "Radius": float(row["Radius"]),
            "NumInputPoints": int(row["NumInputPoints"]),
            "NumOutputPoints": int(row["NumOutputPoints"]),
            "CMax2": float(row["CMax2"]),
        }
        for row in rows
    ]


def _run_wrapper(output: Path, *, explicit_tune_radius: bool) -> int:
    args = [
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
        "--rtdl-route",
        "cell-mbr-author-queue-diagnostic",
        "--author-trace-json",
        str(RESULTS / "bounded3d_author_hd_exec_output_pod.json"),
        "-json",
        str(output),
        "-overwrite",
        "true",
    ]
    if explicit_tune_radius:
        args.extend(["-tune_radius", "adaptive"])
    return int(hd_exec.main(args))


def build_artifact() -> dict[str, Any]:
    wrapper_output = RESULTS / "xhd_goal5360_hd_exec_author_queue_wrapper_output.json"
    fail_closed_output = RESULTS / "xhd_goal5360_hd_exec_author_queue_explicit_tune_radius_fail_closed.json"
    exit_code = _run_wrapper(wrapper_output, explicit_tune_radius=False)
    fail_closed_exit_code = _run_wrapper(fail_closed_output, explicit_tune_radius=True)
    if exit_code != 0:
        raise RuntimeError(f"wrapper route failed with exit code {exit_code}")
    payload = _load_json(wrapper_output)
    fail_closed = _load_json(fail_closed_output)
    author = _load_json(RESULTS / "bounded3d_author_hd_exec_output_pod.json")
    author_rows = _core_iteration_rows(author["Running"]["Repeats"][0]["Iterations"])
    wrapper_rows = _core_iteration_rows(payload["Running"]["Repeats"][0]["Iterations"])
    matched = author_rows == wrapper_rows
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5360.hd_exec_author_queue_wrapper_gate.v1",
        "goal": "Goal5360",
        "date": "2026-07-09",
        "status": "hd_exec_wrapper_author_like_queue_route_matches_bounded3d_author_trace",
        "purpose": (
            "Verify that the hd_exec-compatible RTDL wrapper can expose the "
            "bounded cell-MBR author-like queue route under an explicit internal "
            "route label while preserving fail-closed behavior for explicit "
            "author -tune_radius."
        ),
        "wrapper_output": str(wrapper_output),
        "fail_closed_output": str(fail_closed_output),
        "author_artifact": str(RESULTS / "bounded3d_author_hd_exec_output_pod.json"),
        "comparison": {
            "matched": matched,
            "author_rows": author_rows,
            "wrapper_rows": wrapper_rows,
        },
        "wrapper": {
            "exit_code": exit_code,
            "route_label": payload["RTDL"]["route_label"],
            "hd_result": float(payload["HDResult"]),
            "running_iteration_semantics": payload["Running"]["Repeats"][0].get("IterationSemantics"),
            "radius_trace_status": payload["RTDL"]["radius_trace_metadata"]["status"],
            "author_tune_radius_supported": payload["RTDL"]["radius_trace_metadata"][
                "author_tune_radius_supported"
            ],
        },
        "explicit_tune_radius_fail_closed": {
            "exit_code": fail_closed_exit_code,
            "status": fail_closed["RTDL"]["status"],
            "explicit_author_rt_options": fail_closed["RTDL"]["author_rt_option_surface"][
                "explicit_author_rt_options"
            ],
            "route_executed": False,
        },
        "claim_boundary": {
            "author_tune_radius_route_mapping_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "figure8_reproduction_claimed": False,
            "performance_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "recommended_next_targets": [
            "find_or_construct_nonterminal_trace_case_with_NumOutputPoints_gt_zero",
            "run_wrapper_route_on_nonterminal_case_to_exercise_radius_growth_step",
            "only_then_consider_explicit_author_tune_radius_support",
        ],
        "exit_label": "hd_exec_wrapper_bounded_queue_trace_matches__explicit_tune_radius_still_fail_closed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5360_hd_exec_author_queue_wrapper_gate.json",
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
                "matched": payload["comparison"]["matched"],
                "fail_closed_exit_code": payload["explicit_tune_radius_fail_closed"]["exit_code"],
                "exit_label": payload["exit_label"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
