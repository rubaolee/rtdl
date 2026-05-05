#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import subprocess
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
SCHEMA_VERSION = "goal877_polygon_overlap_optix_phase_contract_v2"
JACCARD_PUBLIC_SAFE_CHUNK_MIN = 1024
JACCARD_PUBLIC_SAFE_CHUNK_MAX = 4096


def _jaccard_chunk_policy(app: str, output_mode: str, chunk_copies: int) -> dict[str, Any] | None:
    if app != "jaccard" or output_mode != "summary":
        return None
    public_safe = JACCARD_PUBLIC_SAFE_CHUNK_MIN <= chunk_copies <= JACCARD_PUBLIC_SAFE_CHUNK_MAX
    return {
        "policy": "public_safe" if public_safe else "diagnostic_only",
        "public_safe": public_safe,
        "chunk_copies": chunk_copies,
        "safe_min": JACCARD_PUBLIC_SAFE_CHUNK_MIN,
        "safe_max": JACCARD_PUBLIC_SAFE_CHUNK_MAX,
        "reason": (
            "Goal1260 evidence supports public Jaccard summary checks only for reviewed safe chunks."
            if public_safe
            else "This chunk size is diagnostic-only; current RTX evidence showed chunk 512 can miss candidates."
        ),
    }


def _source_commit() -> str | None:
    if os.environ.get("RTDL_SOURCE_COMMIT"):
        return os.environ["RTDL_SOURCE_COMMIT"]
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode == 0:
        value = completed.stdout.strip()
        return value or None
    return None


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
                "native_continuation_active",
                "native_continuation_backend",
                "optix_performance",
                "boundary",
                "run_phases",
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
    rows = pair_app._native_overlap_rows_for_candidates(case["left"], case["right"], pairs)
    return {
        "rows": rows,
        "summary": pair_app._summarize_rows(tuple(rows)),
        "row_count": len(rows),
    }


def _jaccard_refine_from_pairs(case, candidate_pairs):
    pairs = set(candidate_pairs)
    rows = jaccard_app._native_jaccard_rows_for_candidates(case["left"], case["right"], pairs)
    return rows, pairs


def _expected_payload(app: str, copies: int) -> dict[str, Any]:
    if app == "pair_overlap":
        return {
            "app": "polygon_pair_overlap_area_rows",
            "copies": copies,
            "output_mode": "summary",
            "row_count": 2 * copies,
            "candidate_row_count": 3 * copies,
            "summary": {
                "overlap_pair_count": 2 * copies,
                "total_intersection_area": 5 * copies,
                "total_union_area": 19 * copies,
            },
            "rt_core_candidate_discovery_active": True,
        }
    return {
        "app": "polygon_set_jaccard",
        "copies": copies,
        "output_mode": "summary",
        "row_count": 1,
        "candidate_row_count": 3 * copies,
        "summary": {
            "intersection_area": 5 * copies,
            "left_area": 13 * copies,
            "right_area": 11 * copies,
            "union_area": 19 * copies,
            "jaccard_similarity": 5 / 19,
        },
        "rt_core_candidate_discovery_active": True,
    }


def _cpu_payload(app: str, copies: int, output_mode: str) -> dict[str, Any]:
    if app == "pair_overlap":
        payload = pair_app.run_case("cpu_python_reference", copies=copies, output_mode=output_mode)
        if output_mode == "summary":
            return {
                "app": "polygon_pair_overlap_area_rows",
                "copies": copies,
                "output_mode": "summary",
                "row_count": payload["row_count"],
                "candidate_row_count": payload["row_count"],
                "summary": payload["summary"],
                "rt_core_candidate_discovery_active": False,
            }
        return payload
    payload = jaccard_app.run_case("cpu_python_reference", copies=copies)
    if output_mode == "summary":
        row = payload["rows"][0]
        return {
            "app": "polygon_set_jaccard",
            "copies": copies,
            "output_mode": "summary",
            "row_count": 1,
            "candidate_row_count": 2 * copies,
            "summary": row,
            "rt_core_candidate_discovery_active": False,
        }
    return payload


def _candidate_pairs(app: str, case: dict[str, Any]) -> set[tuple[int, int]]:
    return (
        pair_app._positive_candidate_pairs_optix(case["left"], case["right"])
        if app == "pair_overlap"
        else jaccard_app._positive_candidate_pairs_optix(case["left"], case["right"])
    )


def _optix_summary_payload(app: str, copies: int, chunk_copies: int) -> tuple[dict[str, Any], int, float, float]:
    remaining = copies
    chunk_count = 0
    candidate_row_count = 0
    candidate_sec = 0.0
    refinement_sec = 0.0
    if app == "pair_overlap":
        summary = {
            "overlap_pair_count": 0,
            "total_intersection_area": 0,
            "total_union_area": 0,
        }
    else:
        summary = {
            "intersection_area": 0,
            "left_area": 0,
            "right_area": 0,
            "union_area": 0,
            "jaccard_similarity": 0.0,
        }
    while remaining:
        current = min(chunk_copies, remaining)
        case = (
            pair_app.make_authored_polygon_pair_overlap_case(copies=current)
            if app == "pair_overlap"
            else jaccard_app.make_authored_polygon_set_jaccard_case(copies=current)
        )
        start = time.perf_counter()
        pairs = _candidate_pairs(app, case)
        candidate_sec += time.perf_counter() - start
        candidate_row_count += len(pairs)
        start = time.perf_counter()
        if app == "pair_overlap":
            chunk_summary = pair_app._exact_overlap_summary_for_candidates(case["left"], case["right"], pairs)
            summary["overlap_pair_count"] += int(chunk_summary["overlap_pair_count"])
            summary["total_intersection_area"] += int(chunk_summary["total_intersection_area"])
            summary["total_union_area"] += int(chunk_summary["total_union_area"])
        else:
            rows = jaccard_app._exact_jaccard_rows_for_candidates(case["left"], case["right"], pairs)
            row = rows[0]
            summary["intersection_area"] += int(row["intersection_area"])
            summary["left_area"] += int(row["left_area"])
            summary["right_area"] += int(row["right_area"])
            summary["union_area"] += int(row["union_area"])
        refinement_sec += time.perf_counter() - start
        chunk_count += 1
        remaining -= current
    if app == "jaccard":
        union_area = int(summary["union_area"])
        summary["jaccard_similarity"] = 0.0 if union_area == 0 else float(summary["intersection_area"]) / union_area
    return (
        {
            "app": "polygon_pair_overlap_area_rows" if app == "pair_overlap" else "polygon_set_jaccard",
            "backend": "optix",
            "backend_mode": "optix_native_assisted",
            "copies": copies,
            "output_mode": "summary",
            "row_count": int(summary["overlap_pair_count"]) if app == "pair_overlap" else 1,
            "candidate_row_count": candidate_row_count,
            "summary": summary,
            "rt_core_accelerated": False,
            "rt_core_candidate_discovery_active": True,
        },
        chunk_count,
        candidate_sec,
        refinement_sec,
    )


def run_profile(
    *,
    app: str,
    mode: str,
    copies: int,
    output_mode: str = "rows",
    validation_mode: str = "full_reference",
    chunk_copies: int = 100,
) -> dict[str, Any]:
    if app not in {"pair_overlap", "jaccard"}:
        raise ValueError("app must be 'pair_overlap' or 'jaccard'")
    if mode not in {"dry-run", "optix"}:
        raise ValueError("mode must be 'dry-run' or 'optix'")
    if copies < 1:
        raise ValueError("copies must be >= 1")
    if output_mode not in {"rows", "summary"}:
        raise ValueError("output_mode must be 'rows' or 'summary'")
    if validation_mode not in {"full_reference", "analytic_summary", "none"}:
        raise ValueError("validation_mode must be full_reference, analytic_summary, or none")
    if output_mode == "rows" and validation_mode == "analytic_summary":
        raise ValueError("analytic_summary validation is only valid with summary output")
    if chunk_copies < 1:
        raise ValueError("chunk_copies must be >= 1")
    chunk_policy = _jaccard_chunk_policy(app, output_mode, chunk_copies)

    phases: dict[str, float | None] = {}
    chunk_count: int | None = None
    cpu_payload = None
    if validation_mode == "analytic_summary":
        phases["input_build_sec"] = 0.0
        phases["cpu_reference_sec"] = None
        cpu_payload = _expected_payload(app, copies)
    elif validation_mode == "full_reference":
        start = time.perf_counter()
        cpu_payload = _cpu_payload(app, copies, output_mode)
        phases["input_build_sec"] = None
        phases["cpu_reference_sec"] = time.perf_counter() - start
    else:
        phases["input_build_sec"] = None
        phases["cpu_reference_sec"] = None

    optix_payload = None
    error = None
    if mode == "optix":
        try:
            start = time.perf_counter()
            if output_mode == "summary":
                optix_payload, chunk_count, candidate_sec, refinement_sec = _optix_summary_payload(
                    app,
                    copies,
                    chunk_copies,
                )
                candidate_pairs = None
                phases["optix_candidate_discovery_sec"] = candidate_sec
                phases["cpu_exact_refinement_sec"] = refinement_sec
                phases["native_exact_continuation_sec"] = refinement_sec
            else:
                case = (
                    pair_app.make_authored_polygon_pair_overlap_case(copies=copies)
                    if app == "pair_overlap"
                    else jaccard_app.make_authored_polygon_set_jaccard_case(copies=copies)
                )
                candidate_pairs = _candidate_pairs(app, case)
                phases["optix_candidate_discovery_sec"] = time.perf_counter() - start

            start = time.perf_counter()
            if output_mode == "summary":
                pass
            elif app == "pair_overlap":
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
                    "native_continuation_active": True,
                    "native_continuation_backend": "oracle_cpp",
                }
            else:
                refined = _jaccard_refine_from_pairs(case, candidate_pairs)
                rows = refined[0]
                optix_payload = {
                    "app": "polygon_set_jaccard",
                    "backend": "optix",
                    "backend_mode": "optix_native_assisted",
                    "copies": copies,
                    "output_mode": "rows",
                    "left_polygon_count": len(case["left"]),
                    "right_polygon_count": len(case["right"]),
                    "row_count": len(rows),
                    "candidate_row_count": len(candidate_pairs),
                    "summary": dict(rows[0]) if rows else {},
                    "rows": rows,
                    "rt_core_accelerated": False,
                    "rt_core_candidate_discovery_active": True,
                    "native_continuation_active": True,
                    "native_continuation_backend": "oracle_cpp",
                }
            if output_mode != "summary":
                phases["cpu_exact_refinement_sec"] = time.perf_counter() - start
                phases["native_exact_continuation_sec"] = phases["cpu_exact_refinement_sec"]
        except Exception as exc:  # noqa: BLE001 - optional backend profiler records absence.
            error = {"type": type(exc).__name__, "message": str(exc)}
            phases.setdefault("optix_candidate_discovery_sec", None)
            phases.setdefault("cpu_exact_refinement_sec", None)
            phases.setdefault("native_exact_continuation_sec", phases["cpu_exact_refinement_sec"])
    else:
        phases["optix_candidate_discovery_sec"] = None
        phases["cpu_exact_refinement_sec"] = None
        phases["native_exact_continuation_sec"] = None

    parity = optix_payload is not None and cpu_payload is not None and _canonical(optix_payload) == _canonical(cpu_payload)
    expected_positive_pair_count = (
        cpu_payload.get("row_count") if isinstance(cpu_payload, dict) else None
    )
    optix_positive_pair_count = (
        optix_payload.get("row_count") if isinstance(optix_payload, dict) else None
    )
    expected_candidate_count = (
        cpu_payload.get("candidate_row_count") if isinstance(cpu_payload, dict) else None
    )
    optix_candidate_count = (
        optix_payload.get("candidate_row_count") if isinstance(optix_payload, dict) else None
    )
    candidate_diagnostics = {
        "expected_or_cpu_candidate_row_count": expected_candidate_count,
        "optix_candidate_row_count": optix_candidate_count,
        "candidate_count_matches_expected": (
            None
            if not isinstance(cpu_payload, dict)
            or not isinstance(optix_payload, dict)
            or expected_candidate_count is None
            else cpu_payload.get("candidate_row_count") == optix_payload.get("candidate_row_count")
        ),
        "candidate_count_delta_vs_expected": (
            None
            if expected_candidate_count is None or optix_candidate_count is None
            else optix_candidate_count - expected_candidate_count
        ),
        "expected_positive_pair_count": expected_positive_pair_count,
        "optix_positive_pair_count": optix_positive_pair_count,
        "positive_pair_count_matches_expected": (
            None
            if expected_positive_pair_count is None or optix_positive_pair_count is None
            else expected_positive_pair_count == optix_positive_pair_count
        ),
        "comparison_note": (
            "candidate_count_matches_expected compares against a conservative "
            "candidate upper-bound/counting model; positive_pair_count_matches_expected "
            "compares final positive overlap rows."
        ),
    }
    if error is not None:
        status = "needs_optix_runtime"
    elif chunk_policy is not None and not chunk_policy["public_safe"]:
        status = "diagnostic_chunk_config"
    elif mode == "dry-run" or validation_mode == "none" or parity:
        status = "pass"
    else:
        status = "fail"
    return {
        "goal": GOAL,
        "date": DATE,
        "schema_version": SCHEMA_VERSION,
        "source_commit": _source_commit(),
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
        "output_mode": output_mode,
        "validation_mode": validation_mode,
        "chunk_copies": chunk_copies if output_mode == "summary" else None,
        "chunk_count": chunk_count,
        "chunk_policy": chunk_policy,
        "phases": phases,
        "cpu_digest": _canonical(cpu_payload) if cpu_payload is not None else None,
        "optix_digest": _canonical(optix_payload) if optix_payload is not None else None,
        "candidate_diagnostics": candidate_diagnostics,
        "optix_metadata": (
            {
                "rt_core_accelerated": bool(optix_payload["rt_core_accelerated"]),
                "rt_core_candidate_discovery_active": bool(optix_payload["rt_core_candidate_discovery_active"]),
                "native_continuation_active": bool(optix_payload.get("native_continuation_active", False)),
                "native_continuation_backend": optix_payload.get("native_continuation_backend"),
                "backend_mode": str(optix_payload["backend_mode"]),
            }
            if optix_payload is not None
            else None
        ),
        "parity_vs_cpu": parity if optix_payload is not None else None,
        "error": error,
        "status": status,
        "boundary": (
            "This profiler separates OptiX LSI/PIP candidate discovery from native C++ exact "
            "area/Jaccard continuation. It does not authorize full polygon-overlap RTX speedup claims."
        ),
        "cloud_claim_contract": {
            "claim_scope": (
                "OptiX native-assisted LSI/PIP candidate discovery for bounded polygon-pair overlap"
                if app == "pair_overlap"
                else "OptiX native-assisted LSI/PIP candidate discovery for bounded polygon-set Jaccard"
            ),
            "non_claim": (
                "not a monolithic GPU polygon-area kernel and not a full app RTX speedup claim"
                if app == "pair_overlap"
                else "not a monolithic GPU Jaccard kernel and not a full app RTX speedup claim"
            ),
            "required_phase_groups": (
                "input_build_sec",
                "cpu_reference_sec",
                "optix_candidate_discovery_sec",
                "cpu_exact_refinement_sec",
                "native_exact_continuation_sec",
                "parity_vs_cpu",
                "rt_core_candidate_discovery_active",
                "validation_mode",
                "output_mode",
            ),
            "chunk_policy": (
                "polygon-set Jaccard public evidence requires chunk_policy.public_safe=true"
                if app == "jaccard" and output_mode == "summary"
                else "not_applicable"
            ),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Profile polygon overlap/Jaccard OptiX native-assisted phases.")
    parser.add_argument("--app", choices=("pair_overlap", "jaccard"), required=True)
    parser.add_argument("--mode", choices=("dry-run", "optix"), default="dry-run")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--output-mode", choices=("rows", "summary"), default="rows")
    parser.add_argument(
        "--validation-mode",
        choices=("full_reference", "analytic_summary", "none"),
        default="full_reference",
    )
    parser.add_argument(
        "--chunk-copies",
        type=int,
        default=1024,
        help=(
            "Copies per OptiX chunk. Goal1260 RTX evidence showed that "
            "polygon-set Jaccard at 8192 copies is safe at 1024-4096, while "
            "512 can miss candidates and 8192 can overflow output capacity."
        ),
    )
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = run_profile(
        app=args.app,
        mode=args.mode,
        copies=args.copies,
        output_mode=args.output_mode,
        validation_mode=args.validation_mode,
        chunk_copies=args.chunk_copies,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "status": payload["status"]}, sort_keys=True))
    return 0 if payload["status"] in {"pass", "needs_optix_runtime", "diagnostic_chunk_config"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
