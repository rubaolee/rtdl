#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import socket
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_polygon_pair_overlap_area_rows as pair_app
from examples import rtdl_polygon_set_jaccard as jaccard_app


GOAL = "Goal877 polygon overlap OptiX phase profiler"
DATE = "2026-04-24"


def _canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _canonical(item)
            for key, item in value.items()
            if key not in {
                "backend",
                "backend_mode",
                "candidate_row_count",
                "rt_core_accelerated",
                "rt_core_candidate_discovery_active",
                "optix_performance",
                "boundary",
            }
        }
    if isinstance(value, list) or isinstance(value, tuple):
        return sorted((_canonical(item) for item in value), key=repr)
    if isinstance(value, float):
        return round(value, 12)
    return value


def _pair_refine(case, candidate_pairs):
    if isinstance(candidate_pairs, set):
        pairs = candidate_pairs
    else:
        pairs = set(candidate_pairs)
    rows = pair_app._exact_overlap_rows_for_candidates(case["left"], case["right"], pairs)
    return {
        "rows": rows,
        "summary": pair_app._summarize_rows(tuple(rows)),
        "row_count": len(rows),
    }


def _jaccard_refine_from_pairs(case, candidate_pairs):
    pairs = set(candidate_pairs)
    rows = jaccard_app._exact_jaccard_rows_for_candidates(case["left"], case["right"], pairs)
    return rows, pairs


def run_profile(*, app: str, mode: str, copies: int) -> dict[str, Any]:
    if app not in {"pair_overlap", "jaccard"}:
        raise ValueError("app must be 'pair_overlap' or 'jaccard'")
    if mode not in {"dry-run", "optix"}:
        raise ValueError("mode must be 'dry-run' or 'optix'")
    if copies < 1:
        raise ValueError("copies must be >= 1")

    phases: dict[str, float | None] = {}
    start = time.perf_counter()
    case = (
        pair_app.make_authored_polygon_pair_overlap_case(copies=copies)
        if app == "pair_overlap"
        else jaccard_app.make_authored_polygon_set_jaccard_case(copies=copies)
    )
    phases["input_build_sec"] = time.perf_counter() - start

    start = time.perf_counter()
    cpu_payload = (
        pair_app.run_case("cpu_python_reference", copies=copies, output_mode="rows")
        if app == "pair_overlap"
        else jaccard_app.run_case("cpu_python_reference", copies=copies)
    )
    phases["cpu_reference_sec"] = time.perf_counter() - start

    optix_payload = None
    error = None
    if mode == "optix":
        try:
            start = time.perf_counter()
            candidate_pairs = (
                pair_app._positive_candidate_pairs_optix(case["left"], case["right"])
                if app == "pair_overlap"
                else jaccard_app._positive_candidate_pairs_optix(case["left"], case["right"])
            )
            phases["optix_candidate_discovery_sec"] = time.perf_counter() - start

            start = time.perf_counter()
            if app == "pair_overlap":
                refined = _pair_refine(case, candidate_pairs)
                optix_payload = {
                    "app": "polygon_pair_overlap_area_rows",
                    "backend": "optix",
                    "backend_mode": "optix_native_assisted",
                    "copies": copies,
                    "output_mode": "rows",
                    "left_polygon_count": len(case["left"]),
                    "right_polygon_count": len(case["right"]),
                    "row_count": refined["row_count"],
                    "candidate_row_count": len(candidate_pairs),
                    "summary": refined["summary"],
                    "rows": refined["rows"],
                    "rt_core_accelerated": False,
                    "rt_core_candidate_discovery_active": True,
                }
            else:
                refined = _jaccard_refine_from_pairs(case, candidate_pairs)
                rows = refined[0]
                optix_payload = {
                    "app": "polygon_set_jaccard",
                    "backend": "optix",
                    "backend_mode": "optix_native_assisted",
                    "copies": copies,
                    "left_polygon_count": len(case["left"]),
                    "right_polygon_count": len(case["right"]),
                    "row_count": len(rows),
                    "candidate_row_count": len(candidate_pairs),
                    "rows": rows,
                    "rt_core_accelerated": False,
                    "rt_core_candidate_discovery_active": True,
                }
            phases["cpu_exact_refinement_sec"] = time.perf_counter() - start
        except Exception as exc:  # noqa: BLE001 - optional backend profiler records absence.
            error = {"type": type(exc).__name__, "message": str(exc)}
            phases.setdefault("optix_candidate_discovery_sec", None)
            phases.setdefault("cpu_exact_refinement_sec", None)
    else:
        phases["optix_candidate_discovery_sec"] = None
        phases["cpu_exact_refinement_sec"] = None

    parity = optix_payload is not None and _canonical(optix_payload) == _canonical(cpu_payload)
    if error is not None:
        status = "needs_optix_runtime"
    elif mode == "dry-run" or parity:
        status = "pass"
    else:
        status = "fail"
    return {
        "goal": GOAL,
        "date": DATE,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "app": app,
        "mode": mode,
        "copies": copies,
        "phases": phases,
        "cpu_digest": _canonical(cpu_payload),
        "optix_digest": _canonical(optix_payload) if optix_payload is not None else None,
        "optix_metadata": (
            {
                "rt_core_accelerated": bool(optix_payload["rt_core_accelerated"]),
                "rt_core_candidate_discovery_active": bool(optix_payload["rt_core_candidate_discovery_active"]),
                "backend_mode": str(optix_payload["backend_mode"]),
            }
            if optix_payload is not None
            else None
        ),
        "parity_vs_cpu": parity if optix_payload is not None else None,
        "error": error,
        "status": status,
        "boundary": (
            "This profiler separates OptiX LSI/PIP candidate discovery from CPU/Python exact "
            "area/Jaccard refinement. It does not authorize full polygon-overlap RTX speedup claims."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Profile polygon overlap/Jaccard OptiX native-assisted phases.")
    parser.add_argument("--app", choices=("pair_overlap", "jaccard"), required=True)
    parser.add_argument("--mode", choices=("dry-run", "optix"), default="dry-run")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = run_profile(app=args.app, mode=args.mode, copies=args.copies)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "status": payload["status"]}, sort_keys=True))
    return 0 if payload["status"] in {"pass", "needs_optix_runtime"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
