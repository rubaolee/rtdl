from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.triangle_counting import (  # noqa: E402
    rtdl_triangle_counting_benchmark_app as triangle_app,
)
from examples.v2_0.research_benchmarks.triangle_counting.rt_graph_contract import (  # noqa: E402
    write_binary_edges,
)


GOAL2797_HARNESS_VERSION = "rtdl.goal2797.triangle_counting_v2_5_canonical_harness.v1"
DEFAULT_METHODS = ("rt_graph_2a1_generic_rt", "rt_graph_1a2_generic_rt")
DEFAULT_BACKENDS = ("optix",)
CLAIM_BOUNDARY = {
    "canonical_harness": True,
    "public_speedup_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "triton_speedup_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
    "paper_reproduction_claim_authorized": False,
    "native_engine_customization": False,
}


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _run_metadata() -> dict[str, Any]:
    return {
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
    }


def disjoint_triangle_edges(triangle_count: int) -> tuple[tuple[int, int], ...]:
    count = int(triangle_count)
    if count < 1:
        raise ValueError("triangle_count must be positive")
    edges: list[tuple[int, int]] = []
    for triangle_index in range(count):
        base = 3 * triangle_index
        edges.extend(((base, base + 1), (base, base + 2), (base + 1, base + 2)))
    return tuple(edges)


def run_goal2797_triangle_counting_harness(
    *,
    triangle_counts: tuple[int, ...],
    methods: tuple[str, ...] = DEFAULT_METHODS,
    backends: tuple[str, ...] = DEFAULT_BACKENDS,
    warmup: int = 2,
    repeat: int = 5,
    use_cupy_for_2a1_optix: bool = True,
    work_dir: Path | None = None,
    fail_fast: bool = False,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    generated_files: list[str] = []
    started = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="goal2797_triangles_") as temp_name:
        temp_root = Path(temp_name) if work_dir is None else Path(work_dir)
        temp_root.mkdir(parents=True, exist_ok=True)
        for triangle_count in triangle_counts:
            edge_path = temp_root / f"disjoint_triangles_{int(triangle_count)}.edgebin"
            write_binary_edges(edge_path, disjoint_triangle_edges(int(triangle_count)))
            generated_files.append(str(edge_path))
            for method in methods:
                if method not in DEFAULT_METHODS:
                    raise ValueError(f"unsupported Goal2797 method: {method}")
                for backend in backends:
                    partner = (
                        "cupy"
                        if use_cupy_for_2a1_optix
                        and str(backend) == "optix"
                        and method == "rt_graph_2a1_generic_rt"
                        else "none"
                    )
                    row_started = time.perf_counter()
                    try:
                        payload = triangle_app.run_app(
                            method,
                            backend=str(backend),
                            edge_file=str(edge_path),
                            edge_format="binary",
                            detail="summary",
                            partner=partner,
                            warmup=int(warmup),
                            repeat=int(repeat),
                        )
                        matches = bool(payload["triangle_count_matches_oracle"])
                        row = _row_from_payload(
                            payload,
                            triangle_count=int(triangle_count),
                            method=method,
                            backend=str(backend),
                            partner=partner,
                            elapsed_sec=time.perf_counter() - row_started,
                            status="pass" if matches else "mismatch",
                        )
                    except Exception as exc:
                        if fail_fast:
                            raise
                        row = {
                            "triangle_count": int(triangle_count),
                            "method": method,
                            "backend": str(backend),
                            "partner": partner,
                            "status": "error",
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                            "elapsed_sec": time.perf_counter() - row_started,
                        }
                    rows.append(row)

    status = "pass" if rows and all(row["status"] == "pass" for row in rows) else "fail"
    return {
        "goal": "Goal2797",
        "harness_version": GOAL2797_HARNESS_VERSION,
        "status": status,
        "triangle_counts": tuple(int(value) for value in triangle_counts),
        "methods": methods,
        "backends": backends,
        "warmup": int(warmup),
        "repeat": int(repeat),
        "generated_edge_files": tuple(generated_files),
        "rows": tuple(rows),
        "row_count": len(rows),
        "elapsed_sec": time.perf_counter() - started,
        **_run_metadata(),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _row_from_payload(
    payload: dict[str, Any],
    *,
    triangle_count: int,
    method: str,
    backend: str,
    partner: str,
    elapsed_sec: float,
    status: str,
) -> dict[str, Any]:
    summary = payload.get("generic_rt_summary") or {}
    result_count = (
        payload.get("generic_rt_weighted_triangle_count")
        if method == "rt_graph_2a1_generic_rt"
        else payload.get("generic_rt_triangle_count", summary.get("triangle_count"))
    )
    timing = dict(payload.get("timing_ms") or {})
    return {
        "triangle_count": int(triangle_count),
        "method": method,
        "backend": backend,
        "partner": partner,
        "status": status,
        "oracle_triangle_count": int(payload["oracle_triangle_count"]),
        "result_triangle_count": int(result_count),
        "triangle_count_matches_oracle": bool(payload["triangle_count_matches_oracle"]),
        "ray_count": int(payload["ray_count"]),
        "primitive_count": int(payload["primitive_count"]),
        "rt_core_accelerated": bool(payload.get("rt_core_accelerated")),
        "ray_tracing_accelerated": bool(payload.get("ray_tracing_accelerated")),
        "same_contract_native_timing": bool(payload.get("same_contract_native_timing")),
        "query_median_ms": timing.get("query_median_ms"),
        "query_min_ms": timing.get("query_min_ms"),
        "query_max_ms": timing.get("query_max_ms"),
        "prepare_scene_ms": timing.get("prepare_scene_ms"),
        "run_backend_ms": timing.get("run_backend"),
        "total_ms": timing.get("total"),
        "v2_4_phase_timing": payload.get("v2_4_phase_timing"),
        "elapsed_sec": float(elapsed_sec),
    }


def _parse_csv_ints(value: str) -> tuple[int, ...]:
    return tuple(int(part.strip()) for part in value.split(",") if part.strip())


def _parse_csv_strings(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal2797 Triangle Counting v2.5 canonical harness.")
    parser.add_argument("--triangle-counts", default="16,1024,5000")
    parser.add_argument("--methods", default=",".join(DEFAULT_METHODS))
    parser.add_argument("--backends", default=",".join(DEFAULT_BACKENDS))
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument(
        "--no-cupy-2a1-optix",
        action="store_true",
        help="Use host-packed geometry for the RT-2A1 OptiX lowering instead of the CuPy device-column builder.",
    )
    args = parser.parse_args(argv)

    payload = run_goal2797_triangle_counting_harness(
        triangle_counts=_parse_csv_ints(args.triangle_counts),
        methods=_parse_csv_strings(args.methods),
        backends=_parse_csv_strings(args.backends),
        warmup=args.warmup,
        repeat=args.repeat,
        use_cupy_for_2a1_optix=not args.no_cupy_2a1_optix,
        work_dir=args.work_dir,
        fail_fast=args.fail_fast,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
