#!/usr/bin/env python3
"""Build Goal5362 narrow tune_radius option-surface gate evidence."""

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

RES4FULL_AUTHOR_JSON = RESULTS / "perf_res4full_author_hd_exec_output_pod.json"
BOUNDED_AUTHOR_JSON = RESULTS / "bounded3d_author_hd_exec_output_pod.json"

ADAPTIVE_OUTPUT = RESULTS / "xhd_goal5362_tune_radius_adaptive_supported_output.json"
DOUBLE_FAIL_OUTPUT = RESULTS / "xhd_goal5362_tune_radius_double_fail_closed.json"
TERMINAL_FAIL_OUTPUT = RESULTS / "xhd_goal5362_tune_radius_terminal_trace_fail_closed.json"
LB_FAIL_OUTPUT = RESULTS / "xhd_goal5362_other_author_rt_option_fail_closed.json"


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


def _run_res4full_wrapper(output: Path, *, tune_radius: str, extra_args: list[str] | None = None) -> int:
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
        str(RES4FULL_AUTHOR_JSON),
        "--translate-each-input-to-min-bound",
        "-tune_radius",
        tune_radius,
        "-json",
        str(output),
        "-overwrite",
        "true",
    ]
    if extra_args:
        args.extend(extra_args)
    return int(hd_exec.main(args))


def _run_bounded_terminal_wrapper(output: Path, *, tune_radius: str) -> int:
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
        str(BOUNDED_AUTHOR_JSON),
        "-tune_radius",
        tune_radius,
        "-json",
        str(output),
        "-overwrite",
        "true",
    ]
    return int(hd_exec.main(args))


def _fail_closed_summary(path: Path, *, expected_option: str) -> dict[str, Any]:
    payload = _load_json(path)
    surface = payload["RTDL"]["author_rt_option_surface"]
    return {
        "output": str(path),
        "status": payload["RTDL"]["status"],
        "explicit_author_rt_options": surface["explicit_author_rt_options"],
        "supported_explicit_author_rt_options": surface["supported_explicit_author_rt_options"],
        "unsupported_explicit_author_rt_options": surface["unsupported_explicit_author_rt_options"],
        "all_explicit_author_rt_options_supported": surface["all_explicit_author_rt_options_supported"],
        "expected_unsupported_option_present": expected_option
        in surface["unsupported_explicit_author_rt_options"],
        "route_executed": False,
    }


def build_artifact(*, tolerance: float = 1.0e-6) -> dict[str, Any]:
    adaptive_exit = _run_res4full_wrapper(ADAPTIVE_OUTPUT, tune_radius="adaptive")
    double_exit = _run_res4full_wrapper(DOUBLE_FAIL_OUTPUT, tune_radius="double")
    terminal_exit = _run_bounded_terminal_wrapper(TERMINAL_FAIL_OUTPUT, tune_radius="adaptive")
    lb_exit = _run_res4full_wrapper(LB_FAIL_OUTPUT, tune_radius="adaptive", extra_args=["-lb", "0"])

    adaptive = _load_json(ADAPTIVE_OUTPUT)
    author = _load_json(RES4FULL_AUTHOR_JSON)
    author_rows = _core_iteration_rows(author["Running"]["Repeats"][0]["Iterations"])
    adaptive_rows = _core_iteration_rows(adaptive["Running"]["Repeats"][0]["Iterations"])
    row_comparison = _compare_rows(author_rows, adaptive_rows, tolerance=tolerance)
    hd_abs_diff = abs(float(author["HDResult"]) - float(adaptive["HDResult"]))
    adaptive_surface = adaptive["RTDL"]["author_rt_option_surface"]
    radius_metadata = adaptive["RTDL"]["radius_trace_metadata"]

    adaptive_supported = (
        adaptive_exit == 0
        and row_comparison["matched"]
        and hd_abs_diff <= tolerance
        and adaptive_surface["supported_explicit_author_rt_options"] == ["tune_radius"]
        and adaptive_surface["unsupported_explicit_author_rt_options"] == []
        and bool(adaptive_surface["all_explicit_author_rt_options_supported"])
        and bool(radius_metadata["author_tune_radius_supported"])
        and bool(radius_metadata["uses_radius_growth_step"])
    )

    double_fail = _fail_closed_summary(DOUBLE_FAIL_OUTPUT, expected_option="tune_radius")
    terminal_fail = _fail_closed_summary(TERMINAL_FAIL_OUTPUT, expected_option="tune_radius")
    lb_fail = _fail_closed_summary(LB_FAIL_OUTPUT, expected_option="lb")
    fail_closed_matched = (
        double_exit == 2
        and terminal_exit == 2
        and lb_exit == 2
        and double_fail["expected_unsupported_option_present"]
        and terminal_fail["expected_unsupported_option_present"]
        and lb_fail["expected_unsupported_option_present"]
        and "tune_radius" in lb_fail["supported_explicit_author_rt_options"]
    )

    matched = bool(adaptive_supported and fail_closed_matched)
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5362.tune_radius_option_surface_gate.v1",
        "goal": "Goal5362",
        "date": "2026-07-09",
        "status": (
            "narrow_internal_adaptive_tune_radius_mapping_passed"
            if matched
            else "narrow_internal_adaptive_tune_radius_mapping_failed"
        ),
        "purpose": (
            "Decide the narrow option-surface mapping after Goal5361: explicit "
            "-tune_radius adaptive may be accepted only for the internal "
            "cell-mbr-author-queue-diagnostic route with a nonterminal author "
            "trace; other author RT options and unsupported tune_radius modes "
            "must still fail closed."
        ),
        "adaptive_supported_case": {
            "exit_code": adaptive_exit,
            "output": str(ADAPTIVE_OUTPUT),
            "author_artifact": str(RES4FULL_AUTHOR_JSON),
            "preprocessing_contract": adaptive["RTDL"].get("reference_preprocessing", []),
            "hd_abs_diff": hd_abs_diff,
            "row_comparison": row_comparison,
            "author_rows": author_rows,
            "rtdl_rows": adaptive_rows,
            "author_hd_result": float(author["HDResult"]),
            "rtdl_hd_result": float(adaptive["HDResult"]),
            "author_rt_option_surface": adaptive_surface,
            "radius_trace_metadata": {
                "status": radius_metadata["status"],
                "route_iteration_model": radius_metadata["route_iteration_model"],
                "uses_radius_growth_step": radius_metadata["uses_radius_growth_step"],
                "author_tune_radius_supported": radius_metadata["author_tune_radius_supported"],
                "author_tune_radius_support_scope": radius_metadata.get("author_tune_radius_support_scope"),
            },
        },
        "fail_closed_controls": {
            "double_mode": {
                "exit_code": double_exit,
                **double_fail,
            },
            "terminal_trace_adaptive": {
                "exit_code": terminal_exit,
                **terminal_fail,
            },
            "other_author_rt_option_lb": {
                "exit_code": lb_exit,
                **lb_fail,
            },
        },
        "comparison": {
            "matched": matched,
            "adaptive_supported": bool(adaptive_supported),
            "fail_closed_controls_matched": bool(fail_closed_matched),
            "tolerance": tolerance,
        },
        "claim_boundary": {
            "author_tune_radius_general_support_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "figure8_reproduction_claimed": False,
            "performance_claimed": False,
            "exact_paper_dataset_identity_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "exit_label": (
            "narrow_internal_adaptive_tune_radius_option_mapping_ready"
            if matched
            else "narrow_internal_adaptive_tune_radius_option_mapping_failed"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5362_tune_radius_option_surface_gate.json",
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
                "adaptive_exit_code": payload["adaptive_supported_case"]["exit_code"],
                "double_exit_code": payload["fail_closed_controls"]["double_mode"]["exit_code"],
                "terminal_exit_code": payload["fail_closed_controls"]["terminal_trace_adaptive"]["exit_code"],
                "lb_exit_code": payload["fail_closed_controls"]["other_author_rt_option_lb"]["exit_code"],
                "exit_label": payload["exit_label"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
