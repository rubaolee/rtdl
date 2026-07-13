#!/usr/bin/env python3
"""Drive the RTDL hd_exec-compatible entrypoint over cases from a summary file."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import run_xhd_rtdl_hd_exec as rtdl_hd_exec


def _case_author_hd(case: dict[str, object]) -> float | None:
    author_normalized = case.get("author_normalized")
    if isinstance(author_normalized, dict) and author_normalized.get("hd_result") is not None:
        return float(author_normalized["hd_result"])
    author_log = case.get("author_log")
    if isinstance(author_log, dict) and author_log.get("hd_result") is not None:
        return float(author_log["hd_result"])
    return None


def _case_public_paths(case: dict[str, object]) -> tuple[str, str]:
    public_paths = case.get("public_paths")
    if not isinstance(public_paths, list) or len(public_paths) != 2:
        raise ValueError("case must contain public_paths with two entries")
    return str(public_paths[0]), str(public_paths[1])


def _case_name(case: dict[str, object], index: int) -> str:
    name = case.get("case_name")
    if isinstance(name, str) and name:
        return name
    return f"case_{index:04d}"


def _runner_args(args: argparse.Namespace, *, input1: str, input2: str) -> SimpleNamespace:
    return SimpleNamespace(
        input1=input1,
        input2=input2,
        n_dims=args.n_dims,
        input_type=args.input_type,
        variant="rt",
        execution=args.execution,
        json_path="",
        overwrite=True,
        check=False,
        rtdl_route=args.rtdl_route,
        grid_shape=args.grid_shape,
        max_inline_points=args.max_inline_points,
        seed_cell_budget=args.seed_cell_budget,
        normalize_each_input_to_author_unit_box=args.normalize_each_input_to_author_unit_box,
        author_float32_normalization=args.author_float32_normalization,
        translate_each_input_to_min_bound=args.translate_each_input_to_min_bound,
        tolerance=args.tolerance,
    )


def _select_cases(cases: list[dict[str, object]], *, start_index: int, max_cases: int | None) -> list[tuple[int, dict[str, object]]]:
    if start_index < 0:
        raise ValueError("--start-index must be non-negative")
    indexed = list(enumerate(cases))
    if max_cases is None:
        return indexed[start_index:]
    if max_cases < 0:
        raise ValueError("--max-cases must be non-negative")
    return indexed[start_index : start_index + max_cases]


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    source = json.loads(Path(args.case_summary).read_text(encoding="utf-8"))
    raw_cases = source.get("cases")
    if not isinstance(raw_cases, list):
        raise ValueError("--case-summary must contain a cases list")
    cases = [case for case in raw_cases if isinstance(case, dict)]
    selected = _select_cases(cases, start_index=args.start_index, max_cases=args.max_cases)
    started = time.perf_counter()
    outputs: list[dict[str, object]] = []
    for case_index, case in selected:
        input1, input2 = _case_public_paths(case)
        author_hd = _case_author_hd(case)
        case_started = time.perf_counter()
        payload = rtdl_hd_exec.run_rtdl_hd_exec(_runner_args(args, input1=input1, input2=input2))
        case_wall_sec = time.perf_counter() - case_started
        abs_diff = None if author_hd is None else abs(float(payload["HDResult"]) - author_hd)
        matched = None if abs_diff is None else bool(abs_diff <= args.tolerance)
        outputs.append(
            {
                "case_index": int(case_index),
                "case_name": _case_name(case, case_index),
                "input1": input1,
                "input2": input2,
                "author_hd_result": author_hd,
                "rtdl_hd_result": float(payload["HDResult"]),
                "author_abs_diff": abs_diff,
                "matched_author": matched,
                "route_label": payload["RTDL"]["route_label"],
                "per_source_witness_exact": bool(payload["RTDL"]["route"].get("per_source_witness_exact", False)),
                "point_count_a": int(payload["RTDL"]["point_count_a"]),
                "point_count_b": int(payload["RTDL"]["point_count_b"]),
                "reference_preprocessing": payload["RTDL"]["reference_preprocessing"],
                "running_avg_time_ms": float(payload["Running"]["AvgTime"]),
                "running_time_semantics": payload["Running"]["TimeSemantics"],
                "case_wall_sec": case_wall_sec,
                "rtdl_payload": payload if args.include_payloads else None,
            }
        )
    matched_cases = [case for case in outputs if case["matched_author"] is True]
    failed_cases = [case for case in outputs if case["matched_author"] is False]
    return {
        "schema": "rtdl.paper_reproduction.xhd.rtdl_hd_exec_summary_batch.v1",
        "paper_app": "x-hd-paper",
        "case_summary": str(args.case_summary),
        "source_summary_schema": source.get("schema"),
        "route_label": args.rtdl_route,
        "n_dims": int(args.n_dims),
        "input_type": args.input_type,
        "execution": args.execution,
        "start_index": int(args.start_index),
        "requested_max_cases": args.max_cases,
        "selected_case_count": len(outputs),
        "matched_case_count": len(matched_cases),
        "failed_case_count": len(failed_cases),
        "all_cases_matched": bool(len(outputs) > 0 and len(matched_cases) == len(outputs)),
        "cases": outputs,
        "elapsed_sec": time.perf_counter() - started,
        "claim_boundary": {
            "hd_exec_compatible_batch_bridge_claimed": True,
            "bulk_all400_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "exact_paper_dataset_identity_proved": False,
            "author_performance_parity_claimed": False,
            "performance_claimed": False,
        },
        "boundary": (
            "App-owned batch bridge that drives the RTDL hd_exec-compatible "
            "entrypoint over cases listed by an existing evidence summary. It "
            "does not add dataset, X-HD, or hd_exec semantics to RTDL core and "
            "does not replace the original all-400 evidence unless run over all "
            "cases with matching review."
        ),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-summary", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--rtdl-route", default="cell-mbr-exact-witness", choices=rtdl_hd_exec.ROUTE_LABELS)
    parser.add_argument("--n-dims", type=int, default=3)
    parser.add_argument("--input-type", default="off", choices=("wkt", "ply", "off"))
    parser.add_argument("--execution", default="gpu", choices=("cpu", "gpu"))
    parser.add_argument("--grid-shape", default="96,60,72")
    parser.add_argument("--max-inline-points", type=int, default=64)
    parser.add_argument("--seed-cell-budget", type=int, default=4)
    parser.add_argument("--normalize-each-input-to-author-unit-box", action="store_true")
    parser.add_argument("--author-float32-normalization", action="store_true")
    parser.add_argument("--translate-each-input-to-min-bound", action="store_true")
    parser.add_argument("--tolerance", type=float, default=1e-6)
    parser.add_argument("--include-payloads", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    summary = build_summary(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "schema": summary["schema"],
                "selected_case_count": summary["selected_case_count"],
                "matched_case_count": summary["matched_case_count"],
                "failed_case_count": summary["failed_case_count"],
                "all_cases_matched": summary["all_cases_matched"],
            },
            sort_keys=True,
        )
    )
    return 0 if summary["all_cases_matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
