from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_ann_candidate_app
from examples import rtdl_dbscan_clustering_app
from examples import rtdl_outlier_detection_app


APP_RUNNERS = {
    "ann_candidate": rtdl_ann_candidate_app.run_app,
    "outlier_detection": rtdl_outlier_detection_app.run_app,
    "dbscan_clustering": rtdl_dbscan_clustering_app.run_app,
}

BACKENDS = ("cpu_python_reference", "cpu", "embree", "optix", "vulkan", "scipy")


def backend_available(backend: str) -> tuple[bool, str | None]:
    if backend in ("cpu_python_reference", "cpu"):
        return True, None
    if backend == "scipy":
        try:
            import scipy  # noqa: F401
        except Exception as exc:  # pragma: no cover - host dependent
            return False, f"{type(exc).__name__}: {exc}"
        return True, None
    probe_name = "embree_version" if backend == "embree" else f"{backend}_version"
    try:
        getattr(rt, probe_name)()
    except Exception as exc:  # pragma: no cover - host dependent
        return False, f"{type(exc).__name__}: {exc}"
    return True, None


def _correctness_summary(app: str, payload: dict[str, object]) -> dict[str, object]:
    if app == "ann_candidate":
        return {
            "recall_at_1": payload["recall_at_1"],
            "mean_distance_ratio": payload["mean_distance_ratio"],
            "exact_match_count": payload["exact_match_count"],
            "query_count": payload["query_count"],
        }
    return {"matches_oracle": payload["matches_oracle"]}


def time_case(app: str, backend: str, copies: int, repeats: int) -> dict[str, object]:
    runner = APP_RUNNERS[app]
    available, skip_reason = backend_available(backend)
    if not available:
        return {
            "app": app,
            "backend": backend,
            "copies": copies,
            "status": "skipped",
            "skip_reason": skip_reason,
        }

    durations: list[float] = []
    payload: dict[str, object] | None = None
    try:
        payload = runner(backend, copies=copies)
        for _ in range(repeats):
            start = time.perf_counter()
            payload = runner(backend, copies=copies)
            durations.append(time.perf_counter() - start)
    except Exception as exc:
        return {
            "app": app,
            "backend": backend,
            "copies": copies,
            "status": "failed",
            "error": f"{type(exc).__name__}: {exc}",
        }

    assert payload is not None
    return {
        "app": app,
        "backend": backend,
        "copies": copies,
        "status": "passed",
        "repeats": repeats,
        "seconds_min": min(durations),
        "seconds_median": statistics.median(durations),
        "seconds_max": max(durations),
        "correctness": _correctness_summary(app, payload),
    }


def run_matrix(copies: int, repeats: int) -> dict[str, object]:
    results = [
        time_case(app, backend, copies, repeats)
        for app in APP_RUNNERS
        for backend in BACKENDS
    ]
    return {
        "goal": "524",
        "copies": copies,
        "repeats": repeats,
        "apps": tuple(APP_RUNNERS),
        "backends": BACKENDS,
        "summary": {
            "passed": sum(1 for item in results if item["status"] == "passed"),
            "failed": sum(1 for item in results if item["status"] == "failed"),
            "skipped": sum(1 for item in results if item["status"] == "skipped"),
            "total": len(results),
        },
        "results": results,
        "honesty_boundary": (
            "This is a bounded in-process timing harness for RTDL Stage-1 proximity apps. "
            "It is not a claim of general ANN, anomaly-detection, or clustering performance."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Time v0.8 Stage-1 proximity apps across available backends.")
    parser.add_argument("--copies", type=int, default=128)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    payload = run_matrix(copies=args.copies, repeats=args.repeats)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 1 if payload["summary"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
