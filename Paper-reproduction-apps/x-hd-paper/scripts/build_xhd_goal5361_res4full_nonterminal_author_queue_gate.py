#!/usr/bin/env python3
"""Build Goal5361 res4full nonterminal author-like queue gate evidence."""

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


AUTHOR_JSON = RESULTS / "perf_res4full_author_hd_exec_output_pod.json"
WRAPPER_OUTPUT = RESULTS / "xhd_goal5361_res4full_nonterminal_author_queue_wrapper_output.json"


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


def _compare_rows(
    author_rows: list[dict[str, Any]],
    rtdl_rows: list[dict[str, Any]],
    *,
    tolerance: float,
) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    if len(author_rows) != len(rtdl_rows):
        mismatches.append({"field": "iteration_count", "author": len(author_rows), "rtdl": len(rtdl_rows)})
    for index, (author, rtdl) in enumerate(zip(author_rows, rtdl_rows), start=1):
        for field in ("Iteration", "NumInputPoints", "NumOutputPoints"):
            if int(author[field]) != int(rtdl[field]):
                mismatches.append(
                    {
                        "iteration": index,
                        "field": field,
                        "author": int(author[field]),
                        "rtdl": int(rtdl[field]),
                    }
                )
        for field in ("Radius", "CMax2"):
            abs_diff = abs(float(author[field]) - float(rtdl[field]))
            if abs_diff > tolerance:
                mismatches.append(
                    {
                        "iteration": index,
                        "field": field,
                        "author": float(author[field]),
                        "rtdl": float(rtdl[field]),
                        "abs_diff": abs_diff,
                    }
                )
    return {
        "matched": len(mismatches) == 0,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }


def _run_wrapper(output: Path) -> int:
    args = [
        "-input1",
        str(FIXTURES / "stanford_dragon_res4_full.ply"),
        "-input2",
        str(FIXTURES / "stanford_happy_res4_full.ply"),
        "-n_dims",
        "3",
        "-input_type",
        "ply",
        "-variant",
        "rt",
        "-execution",
        "gpu",
        "--rtdl-route",
        "cell-mbr-author-queue-diagnostic",
        "--author-trace-json",
        str(AUTHOR_JSON),
        "--translate-each-input-to-min-bound",
        "-json",
        str(output),
        "-overwrite",
        "true",
    ]
    return int(hd_exec.main(args))


def build_artifact(*, tolerance: float = 1.0e-6) -> dict[str, Any]:
    exit_code = _run_wrapper(WRAPPER_OUTPUT)
    if exit_code != 0:
        raise RuntimeError(f"res4full wrapper route failed with exit code {exit_code}")
    wrapper = _load_json(WRAPPER_OUTPUT)
    author = _load_json(AUTHOR_JSON)
    author_rows = _core_iteration_rows(author["Running"]["Repeats"][0]["Iterations"])
    wrapper_rows = _core_iteration_rows(wrapper["Running"]["Repeats"][0]["Iterations"])
    row_comparison = _compare_rows(author_rows, wrapper_rows, tolerance=tolerance)
    hd_abs_diff = abs(float(author["HDResult"]) - float(wrapper["HDResult"]))
    route_iterations = wrapper["RTDL"]["radius_trace_metadata"]["directions"][0]["iterations"]
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5361.res4full_nonterminal_author_queue_gate.v1",
        "goal": "Goal5361",
        "date": "2026-07-09",
        "status": (
            "res4full_nonterminal_author_like_queue_trace_matches"
            if row_comparison["matched"] and hd_abs_diff <= tolerance
            else "res4full_nonterminal_author_like_queue_trace_mismatch"
        ),
        "purpose": (
            "Verify that the hd_exec-compatible RTDL wrapper can reproduce a "
            "nonterminal author radius-queue trace on the res4full Dragon -> "
            "HappyBuddha case. This exercises generic radius_growth_step in a "
            "case with NumOutputPoints > 0 before terminal convergence."
        ),
        "input_pair": "stanford_dragon_res4_full.ply -> stanford_happy_res4_full.ply",
        "wrapper_output": str(WRAPPER_OUTPUT),
        "author_artifact": str(AUTHOR_JSON),
        "preprocessing_contract": {
            "required": ["translate_each_input_to_min_bound"],
            "reason": "The author JSON input MBR starts at zero and matches the translated local PLY bounds.",
            "wrapper_reference_preprocessing": wrapper["RTDL"].get("reference_preprocessing", []),
        },
        "comparison": {
            "matched": bool(row_comparison["matched"] and hd_abs_diff <= tolerance),
            "hd_abs_diff": hd_abs_diff,
            "tolerance": tolerance,
            "row_comparison": row_comparison,
            "author_rows": author_rows,
            "wrapper_rows": wrapper_rows,
            "author_hd_result": float(author["HDResult"]),
            "wrapper_hd_result": float(wrapper["HDResult"]),
        },
        "route": {
            "route_label": wrapper["RTDL"]["route_label"],
            "route": wrapper["RTDL"]["route"],
            "route_iteration_model": wrapper["RTDL"]["radius_trace_metadata"]["route_iteration_model"],
            "uses_radius_growth_step": bool(wrapper["RTDL"]["radius_trace_metadata"]["uses_radius_growth_step"]),
            "author_tune_radius_supported": bool(
                wrapper["RTDL"]["radius_trace_metadata"]["author_tune_radius_supported"]
            ),
            "iteration_count": len(route_iterations),
            "has_nonterminal_iteration": any(int(row["NumOutputPoints"]) > 0 for row in route_iterations),
        },
        "claim_boundary": {
            "author_tune_radius_route_mapping_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "figure8_reproduction_claimed": False,
            "performance_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "exit_label": (
            "res4full_nonterminal_queue_trace_matches__explicit_tune_radius_still_unmapped"
            if row_comparison["matched"] and hd_abs_diff <= tolerance
            else "res4full_nonterminal_queue_trace_mismatch"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5361_res4full_nonterminal_author_queue_gate.json",
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
                "matched": payload["comparison"]["matched"],
                "hd_abs_diff": payload["comparison"]["hd_abs_diff"],
                "exit_label": payload["exit_label"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
