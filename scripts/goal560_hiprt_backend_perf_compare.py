from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import time
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from scripts.goal547_hiprt_correctness_matrix import cases


BACKENDS: dict[str, Callable[..., tuple[dict[str, object], ...]]] = {
    "cpu_python_reference": rt.run_cpu_python_reference,
    "embree": rt.run_embree,
    "optix": rt.run_optix,
    "vulkan": rt.run_vulkan,
    "hiprt": rt.run_hiprt,
}


def _measure(fn: Callable[[], tuple[dict[str, object], ...]], repeats: int) -> dict[str, object]:
    rows = None
    timings = []
    for _ in range(repeats):
        started = time.perf_counter()
        rows = fn()
        timings.append(time.perf_counter() - started)
    assert rows is not None
    return {
        "rows": tuple(rows),
        "seconds": timings,
        "median_seconds": statistics.median(timings),
        "min_seconds": min(timings),
        "max_seconds": max(timings),
    }


def run_perf_compare(*, repeats: int, backends: tuple[str, ...]) -> dict[str, object]:
    selected = tuple(backends)
    unknown = [backend for backend in selected if backend not in BACKENDS]
    if unknown:
        raise ValueError(f"unknown backends: {', '.join(unknown)}")

    results = []
    summary = {"pass": 0, "backend_unavailable": 0, "fail": 0}
    for case in cases():
        workload = str(case["workload"])
        kernel = case["kernel"]
        inputs = dict(case["inputs"])
        reference = _measure(lambda: rt.run_cpu_python_reference(kernel, **inputs), repeats)
        backend_results = {}
        for backend in selected:
            runner = BACKENDS[backend]
            try:
                measured = _measure(lambda runner=runner: runner(kernel, **inputs), repeats)
            except (FileNotFoundError, OSError, NotImplementedError) as exc:
                summary["backend_unavailable"] += 1
                backend_results[backend] = {
                    "status": "UNAVAILABLE",
                    "error_type": type(exc).__name__,
                    "message": str(exc).splitlines()[0],
                }
                continue
            except Exception as exc:  # noqa: BLE001 - report all backend failures explicitly.
                summary["fail"] += 1
                backend_results[backend] = {
                    "status": "FAIL",
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }
                continue
            parity = measured["rows"] == reference["rows"]
            summary["pass" if parity else "fail"] += 1
            backend_results[backend] = {
                "status": "PASS" if parity else "FAIL",
                "row_count": len(measured["rows"]),
                "parity_vs_cpu_reference": parity,
                "median_seconds": measured["median_seconds"],
                "min_seconds": measured["min_seconds"],
                "max_seconds": measured["max_seconds"],
                "seconds": measured["seconds"],
            }
        results.append(
            {
                "workload": workload,
                "cpu_reference_row_count": len(reference["rows"]),
                "cpu_reference_median_seconds": reference["median_seconds"],
                "backends": backend_results,
            }
        )

    return {
        "goal": 560,
        "description": "v0.9 HIPRT performance comparison against CPU reference, Embree, OptiX, and Vulkan where available",
        "repeats": repeats,
        "backends": selected,
        "summary": summary,
        "results": results,
        "honesty_boundary": (
            "Small-fixture timing includes backend startup/JIT/build overhead and is intended as a release smoke "
            "comparison, not a throughput or RT-core speedup claim."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run v0.9 HIPRT backend performance comparison.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument(
        "--backends",
        default="hiprt,embree,optix,vulkan",
        help="Comma-separated backend list. Valid: cpu_python_reference,embree,optix,vulkan,hiprt",
    )
    args = parser.parse_args(argv)
    if args.repeats <= 0:
        raise ValueError("--repeats must be positive")
    backends = tuple(item.strip() for item in args.backends.split(",") if item.strip())
    payload = run_perf_compare(repeats=args.repeats, backends=backends)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 1 if payload["summary"]["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
