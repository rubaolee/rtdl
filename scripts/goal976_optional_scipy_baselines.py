#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_dbscan_clustering_app as dbscan_app
from examples import rtdl_event_hotspot_screening as event_app
from examples import rtdl_outlier_detection_app as outlier_app
from examples import rtdl_service_coverage_gaps as service_app
from scripts.goal839_baseline_artifact_schema import build_baseline_artifact
from scripts.goal839_baseline_artifact_schema import load_goal835_row
from scripts.goal839_baseline_artifact_schema import write_baseline_artifact
from scripts.goal859_spatial_summary_baseline import _event_summary_from_count_rows
from scripts.goal859_spatial_summary_baseline import _event_summary_from_rows
from scripts.goal859_spatial_summary_baseline import _service_summary_from_count_rows
from scripts.goal859_spatial_summary_baseline import _service_summary_from_rows


GOAL = "Goal976 optional SciPy/reference-neighbor baseline collector"
DATE = "2026-04-26"


def _median(samples: list[float]) -> float:
    return float(statistics.median(samples)) if samples else 0.0


def _time(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    return fn(), time.perf_counter() - start


def _artifact_path(app: str, path_name: str, baseline_name: str) -> Path:
    return ROOT / "docs" / "reports" / f"goal835_baseline_{app}_{path_name}_{baseline_name}_2026-04-23.json"


def _outlier_summary(rows: tuple[dict[str, object], ...]) -> dict[str, Any]:
    outlier_count = sum(1 for row in rows if bool(row["is_outlier"]))
    return {
        "point_count": len(rows),
        "threshold_reached_count": len(rows) - outlier_count,
        "outlier_count": outlier_count,
    }


def _dbscan_summary(rows: tuple[dict[str, object], ...]) -> dict[str, Any]:
    core_count = sum(1 for row in rows if bool(row["is_core"]))
    return {
        "point_count": len(rows),
        "threshold_reached_count": core_count,
        "core_count": core_count,
    }


def _profile_outlier_scipy(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time(lambda: outlier_app.make_outlier_case(copies=copies))
    query_samples: list[float] = []
    post_samples: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    for _ in range(iterations):
        neighbor_rows, query_sec = _time(lambda: outlier_app._run_rows("scipy", case))
        last_rows, post_sec = _time(lambda: outlier_app.density_rows_from_neighbor_rows(case["points"], neighbor_rows))
        query_samples.append(query_sec)
        post_samples.append(post_sec)
    expected = outlier_app.expected_tiled_density_rows(copies=copies)
    parity = tuple(last_rows) == tuple(expected)
    return {
        "summary": _outlier_summary(last_rows),
        "phase_seconds": {
            "point_pack": input_sec,
            "backend_prepare": 0.0,
            "native_threshold_query": _median(query_samples),
            "scalar_copyback": 0.0,
            "python_postprocess": _median(post_samples),
        },
        "correctness_parity": parity,
        "validation": {
            "method": "SciPy cKDTree fixed-radius neighbor rows reduced to the outlier density summary",
            "copies": copies,
            "matches_reference": parity,
        },
        "notes": [
            "Optional SciPy/reference-neighbor baseline for the same compact outlier threshold-count contract.",
            "This artifact does not authorize public RTX speedup claims.",
        ],
    }


def _profile_dbscan_scipy(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time(lambda: dbscan_app.make_dbscan_case(copies=copies))
    query_samples: list[float] = []
    post_samples: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    for _ in range(iterations):
        neighbor_rows, query_sec = _time(lambda: dbscan_app._run_rows("scipy", case))
        last_rows, post_sec = _time(lambda: dbscan_app.cluster_from_neighbor_rows(case["points"], neighbor_rows))
        query_samples.append(query_sec)
        post_samples.append(post_sec)
    expected = dbscan_app.expected_tiled_core_flag_rows(copies=copies)
    parity = _dbscan_summary(last_rows) == _dbscan_summary(expected)
    return {
        "summary": _dbscan_summary(last_rows),
        "phase_seconds": {
            "point_pack": input_sec,
            "backend_prepare": 0.0,
            "native_threshold_query": _median(query_samples),
            "scalar_copyback": 0.0,
            "python_postprocess": _median(post_samples),
        },
        "correctness_parity": parity,
        "validation": {
            "method": "SciPy cKDTree fixed-radius neighbor rows reduced to DBSCAN core-flag summary",
            "copies": copies,
            "matches_reference": parity,
        },
        "notes": [
            "Optional SciPy/reference-neighbor baseline for the same compact DBSCAN scalar core-count contract.",
            "This artifact does not authorize a full DBSCAN or public RTX speedup claim.",
        ],
    }


def _fixed_radius_artifact(*, app_name: str, copies: int, iterations: int) -> dict[str, Any]:
    if app_name == "outlier_detection":
        path_name = "prepared_fixed_radius_density_summary"
        baseline_name = "scipy_or_reference_neighbor_baseline_when_used_in_app_report"
        profiler = _profile_outlier_scipy
    elif app_name == "dbscan_clustering":
        path_name = "prepared_fixed_radius_core_flags"
        baseline_name = "scipy_or_reference_neighbor_baseline_when_used_in_app_report"
        profiler = _profile_dbscan_scipy
    else:
        raise ValueError(f"unsupported fixed-radius app `{app_name}`")
    row = load_goal835_row(app=app_name, path_name=path_name, baseline_name=baseline_name)
    profile = profiler(copies, iterations)
    return build_baseline_artifact(
        row=row,
        baseline_name=baseline_name,
        source_backend="scipy_ckdtree",
        benchmark_scale={"copies": copies, "iterations": iterations},
        repeated_runs=iterations,
        correctness_parity=profile["correctness_parity"],
        phase_seconds=profile["phase_seconds"],
        summary=profile["summary"],
        notes=profile["notes"],
        validation=profile["validation"],
    )


def _spatial_phase(input_sec: float, query_samples: list[float], post_samples: list[float]) -> dict[str, float]:
    return {
        "input_build": input_sec,
        "optix_prepare": 0.0,
        "optix_query": _median(query_samples),
        "python_postprocess": _median(post_samples),
    }


def _profile_service_scipy(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time(lambda: service_app.make_service_coverage_case(copies=copies))
    query_samples: list[float] = []
    post_samples: list[float] = []
    last_summary: dict[str, Any] = {}
    for _ in range(iterations):
        rows, query_sec = _time(lambda: service_app._run_rows("scipy", case))
        last_summary, post_sec = _time(lambda: _service_summary_from_rows(case, rows))
        query_samples.append(query_sec)
        post_samples.append(post_sec)
    reference_rows = service_app._run_embree_gap_summary(case)
    reference_summary = _service_summary_from_count_rows(case, reference_rows)
    parity = last_summary == reference_summary
    return {
        "summary": last_summary,
        "phase_seconds": _spatial_phase(input_sec, query_samples, post_samples),
        "correctness_parity": parity,
        "validation": {
            "method": "SciPy fixed-radius rows summarized to service-gap payload and compared with existing Embree compact summary semantics",
            "copies": copies,
            "matches_reference": parity,
            "reference_backend": "embree_gap_summary",
            "reference_summary": reference_summary,
        },
        "notes": [
            "Optional SciPy baseline is bounded to compact service-gap summary semantics.",
            "The parity reference uses Embree compact summary to avoid the O(N*M) CPU row path at 20k-copy scale.",
            "This artifact does not authorize public RTX speedup claims.",
        ],
    }


def _profile_event_scipy(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time(lambda: event_app.make_event_hotspot_case(copies=copies))
    query_samples: list[float] = []
    post_samples: list[float] = []
    last_summary: dict[str, Any] = {}
    for _ in range(iterations):
        rows, query_sec = _time(lambda: event_app._run_rows("scipy", case))
        last_summary, post_sec = _time(lambda: _event_summary_from_rows(case, rows))
        query_samples.append(query_sec)
        post_samples.append(post_sec)
    reference_rows = event_app._run_embree_count_summary(case)
    reference_summary = _event_summary_from_count_rows(case, reference_rows)
    parity = last_summary == reference_summary
    return {
        "summary": last_summary,
        "phase_seconds": _spatial_phase(input_sec, query_samples, post_samples),
        "correctness_parity": parity,
        "validation": {
            "method": "SciPy fixed-radius rows summarized to event-hotspot payload and compared with existing Embree compact summary semantics",
            "copies": copies,
            "matches_reference": parity,
            "reference_backend": "embree_count_summary",
            "reference_summary": reference_summary,
        },
        "notes": [
            "Optional SciPy baseline is bounded to compact event-hotspot summary semantics.",
            "The parity reference uses Embree compact summary to avoid the O(N*M) CPU row path at 20k-copy scale.",
            "This artifact does not authorize public RTX speedup claims.",
        ],
    }


def _spatial_artifact(*, app_name: str, copies: int, iterations: int) -> dict[str, Any]:
    if app_name == "service_coverage_gaps":
        path_name = "prepared_gap_summary"
        baseline_name = "scipy_baseline_when_available"
        profiler = _profile_service_scipy
    elif app_name == "event_hotspot_screening":
        path_name = "prepared_count_summary"
        baseline_name = "scipy_baseline_when_available"
        profiler = _profile_event_scipy
    else:
        raise ValueError(f"unsupported spatial app `{app_name}`")
    row = load_goal835_row(app=app_name, path_name=path_name, baseline_name=baseline_name)
    profile = profiler(copies, iterations)
    return build_baseline_artifact(
        row=row,
        baseline_name=baseline_name,
        source_backend="scipy_ckdtree",
        benchmark_scale={"copies": copies, "iterations": iterations},
        repeated_runs=iterations,
        correctness_parity=profile["correctness_parity"],
        phase_seconds=profile["phase_seconds"],
        summary=profile["summary"],
        notes=profile["notes"],
        validation=profile["validation"],
    )


def collect(*, fixed_copies: int, spatial_copies: int, iterations: int) -> dict[str, Any]:
    outputs: list[dict[str, Any]] = []
    for app_name in ("outlier_detection", "dbscan_clustering"):
        artifact = _fixed_radius_artifact(app_name=app_name, copies=fixed_copies, iterations=iterations)
        path = _artifact_path(artifact["app"], artifact["path_name"], artifact["baseline_name"])
        write_baseline_artifact(path, artifact)
        outputs.append({"path": str(path), "status": artifact["status"], "app": artifact["app"], "baseline": artifact["baseline_name"]})
    for app_name in ("service_coverage_gaps", "event_hotspot_screening"):
        artifact = _spatial_artifact(app_name=app_name, copies=spatial_copies, iterations=iterations)
        path = _artifact_path(artifact["app"], artifact["path_name"], artifact["baseline_name"])
        write_baseline_artifact(path, artifact)
        outputs.append({"path": str(path), "status": artifact["status"], "app": artifact["app"], "baseline": artifact["baseline_name"]})
    return {
        "goal": GOAL,
        "date": DATE,
        "fixed_copies": fixed_copies,
        "spatial_copies": spatial_copies,
        "iterations": iterations,
        "artifact_count": len(outputs),
        "artifacts": outputs,
        "status": "ok" if all(item["status"] == "ok" for item in outputs) else "invalid",
        "boundary": "SciPy/reference-neighbor baselines are optional external baselines. These artifacts do not authorize public RTX speedup claims.",
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal976 Optional SciPy/Reference-Neighbor Baselines",
        "",
        f"Status: `{payload['status']}`",
        "",
        payload["boundary"],
        "",
        f"- fixed-radius copies: `{payload['fixed_copies']}`",
        f"- spatial copies: `{payload['spatial_copies']}`",
        f"- iterations: `{payload['iterations']}`",
        f"- artifacts: `{payload['artifact_count']}`",
        "",
        "| App | Baseline | Artifact | Status |",
        "|---|---|---|---|",
    ]
    for artifact in payload["artifacts"]:
        lines.append(f"| `{artifact['app']}` | `{artifact['baseline']}` | `{artifact['path']}` | `{artifact['status']}` |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect remaining optional SciPy/reference-neighbor Goal835 baselines.")
    parser.add_argument("--fixed-copies", type=int, default=20000)
    parser.add_argument("--spatial-copies", type=int, default=20000)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--output-json", default=str(ROOT / "docs" / "reports" / "goal976_optional_scipy_baselines_2026-04-26.json"))
    parser.add_argument("--output-md", default=str(ROOT / "docs" / "reports" / "goal976_optional_scipy_baselines_2026-04-26.md"))
    args = parser.parse_args(argv)
    payload = collect(fixed_copies=args.fixed_copies, spatial_copies=args.spatial_copies, iterations=args.iterations)
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
