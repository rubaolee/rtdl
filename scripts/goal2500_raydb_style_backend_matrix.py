from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app


DEFAULT_BACKENDS = ("cpu_python_reference", "embree", "optix")
AVAILABLE_BACKENDS = app.BACKENDS
CLAIM_BOUNDARY = (
    "Backend matrix for the generic columnar grouped aggregate contract only. "
    "Timings are diagnostic and do not authorize public speedup, whole-app, "
    "authors-code, true zero-copy, SQL-engine, or DBMS claims."
)


def run_matrix(*, backends: tuple[str, ...] = DEFAULT_BACKENDS, repeats: int = 5) -> dict[str, Any]:
    if repeats < 1:
        raise ValueError("repeats must be >= 1")
    cases = {backend: _run_backend(backend, repeats=repeats) for backend in backends}
    return {
        "goal": "goal2500_raydb_style_backend_matrix",
        "app": "raydb_style_columnar_aggregate",
        "repeats": repeats,
        "cases": cases,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _run_backend(backend: str, *, repeats: int) -> dict[str, Any]:
    try:
        _require_backend(backend)
        modes = _backend_modes(backend)
    except Exception as exc:
        return {
            "backend": backend,
            "status": "skipped",
            "reason": str(exc),
            "claim_boundary": CLAIM_BOUNDARY,
        }

    mode_results: dict[str, Any] = {}
    backend_elapsed: list[float] = []
    for mode in modes:
        samples: list[float] = []
        payload: dict[str, Any] | None = None
        for _ in range(repeats):
            start = time.perf_counter()
            payload = app.run_result_mode(mode, backend=backend)
            elapsed = time.perf_counter() - start
            samples.append(elapsed)
            backend_elapsed.append(elapsed)
        assert payload is not None
        mode_results[mode] = {
            "status": "ok",
            "median_elapsed_sec": statistics.median(samples),
            "min_elapsed_sec": min(samples),
            "max_elapsed_sec": max(samples),
            "samples_elapsed_sec": samples,
            "matches_cpu_reference": bool(payload.get("matches_cpu_reference", True)),
            "row_count": len(payload["rows"]),
            "lowering_plan": payload["metadata"]["lowering_plan"],
        }

    return {
        "backend": backend,
        "status": "ok",
        "modes": mode_results,
        "median_elapsed_sec": statistics.median(backend_elapsed),
        "all_match_cpu_reference": all(result["matches_cpu_reference"] for result in mode_results.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _backend_modes(backend: str) -> tuple[str, ...]:
    if backend == "cpu_python_reference":
        return app.CPU_RESULT_MODES
    if backend == "embree":
        return app.EMBREE_RESULT_MODES
    if backend == "optix":
        return app.OPTIX_RESULT_MODES
    if backend == app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND:
        return app.OPTIX_PARTNER_RESIDENT_RESULT_MODES
    raise ValueError(f"unsupported backend: {backend}")


def _require_backend(backend: str) -> None:
    if backend == "cpu_python_reference":
        return
    if backend == "embree":
        rt.embree_version()
        return
    if backend == "optix":
        rt.optix_version()
        return
    if backend == app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND:
        app.require_optix_partner_resident_experimental_backend()
        return
    raise ValueError(f"unsupported backend: {backend}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Goal2500 RayDB-style backend matrix.")
    parser.add_argument("--backends", nargs="+", default=list(DEFAULT_BACKENDS), choices=AVAILABLE_BACKENDS)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    payload = run_matrix(backends=tuple(args.backends), repeats=args.repeats)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
