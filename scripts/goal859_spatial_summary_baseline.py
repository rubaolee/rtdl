#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_event_hotspot_screening as event_app
from examples import rtdl_service_coverage_gaps as service_app
from scripts.goal839_baseline_artifact_schema import build_baseline_artifact
from scripts.goal839_baseline_artifact_schema import load_goal835_row
from scripts.goal839_baseline_artifact_schema import write_baseline_artifact
import rtdsl as rt


def _stats(samples: list[float]) -> dict[str, float]:
    if not samples:
        return {"min_sec": 0.0, "median_sec": 0.0, "max_sec": 0.0}
    return {
        "min_sec": min(samples),
        "median_sec": statistics.median(samples),
        "max_sec": max(samples),
    }


def _time_call(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


def _service_summary_from_rows(case: dict[str, tuple[rt.Point, ...]], rows: tuple[dict[str, object], ...]) -> dict[str, Any]:
    covered_household_ids = {int(row["query_id"]) for row in rows}
    uncovered_household_ids = [
        int(point.id)
        for point in case["households"]
        if int(point.id) not in covered_household_ids
    ]
    return {
        "household_count": len(case["households"]),
        "clinic_count": len(case["clinics"]),
        "covered_household_count": len(covered_household_ids),
        "uncovered_household_count": len(uncovered_household_ids),
        "uncovered_household_ids": uncovered_household_ids,
    }


def _service_summary_from_count_rows(case: dict[str, tuple[rt.Point, ...]], rows: tuple[dict[str, object], ...]) -> dict[str, Any]:
    covered_household_ids = {
        int(row["query_id"])
        for row in rows
        if int(row.get("threshold_reached", 0)) != 0
    }
    uncovered_household_ids = [
        int(point.id)
        for point in case["households"]
        if int(point.id) not in covered_household_ids
    ]
    return {
        "household_count": len(case["households"]),
        "clinic_count": len(case["clinics"]),
        "covered_household_count": len(covered_household_ids),
        "uncovered_household_count": len(uncovered_household_ids),
        "uncovered_household_ids": uncovered_household_ids,
    }


def _event_summary_from_rows(case: dict[str, tuple[rt.Point, ...]], rows: tuple[dict[str, object], ...]) -> dict[str, Any]:
    neighbor_counts = {int(point.id): 0 for point in case["events"]}
    for row in rows:
        query_id = int(row["query_id"])
        neighbor_id = int(row["neighbor_id"])
        if query_id != neighbor_id:
            neighbor_counts[query_id] = neighbor_counts.get(query_id, 0) + 1
    hotspots = [
        {"event_id": event_id, "neighbor_count": neighbor_count}
        for event_id, neighbor_count in neighbor_counts.items()
        if neighbor_count >= event_app.HOTSPOT_THRESHOLD
    ]
    hotspots.sort(key=lambda item: (-int(item["neighbor_count"]), int(item["event_id"])))
    return {
        "event_count": len(case["events"]),
        "hotspot_count": len(hotspots),
        "hotspots": hotspots,
    }


def _event_summary_from_count_rows(case: dict[str, tuple[rt.Point, ...]], rows: tuple[dict[str, object], ...]) -> dict[str, Any]:
    neighbor_counts = {
        int(row["query_id"]): int(row["neighbor_count"])
        for row in rows
    }
    hotspots = [
        {"event_id": event_id, "neighbor_count": neighbor_count}
        for event_id, neighbor_count in neighbor_counts.items()
        if neighbor_count >= event_app.HOTSPOT_THRESHOLD
    ]
    hotspots.sort(key=lambda item: (-int(item["neighbor_count"]), int(item["event_id"])))
    return {
        "event_count": len(case["events"]),
        "hotspot_count": len(hotspots),
        "hotspots": hotspots,
    }


def _profile_service_cpu(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time_call(lambda: service_app.make_service_coverage_case(copies=copies))
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    last_summary: dict[str, Any] = {}
    for _ in range(iterations):
        last_rows, query_sec = _time_call(lambda: service_app._run_rows("cpu_python_reference", case))
        last_summary, post_sec = _time_call(lambda: _service_summary_from_rows(case, last_rows))
        query_samples.append(query_sec)
        postprocess_samples.append(post_sec)
    expected = service_app.run_case("cpu_python_reference", copies=copies)
    parity = {
        "household_count": expected["household_count"],
        "clinic_count": expected["clinic_count"],
        "covered_household_count": expected["covered_household_count"],
        "uncovered_household_count": len(expected["uncovered_household_ids"]),
        "uncovered_household_ids": expected["uncovered_household_ids"],
    } == last_summary
    return {
        "summary": last_summary,
        "phase_seconds": {
            "input_build": input_sec,
            "optix_prepare": 0.0,
            "optix_query": _stats(query_samples)["median_sec"],
            "python_postprocess": _stats(postprocess_samples)["median_sec"],
        },
        "correctness_parity": parity,
        "validation": {
            "method": "compare compact CPU summary against service_coverage_gaps cpu_python_reference app payload",
            "copies": copies,
            "matches_reference": parity,
        },
        "notes": [
            "CPU oracle baseline uses the same generated case as the prepared OptiX path.",
            "The comparable metric stays bounded to compact service-gap summary semantics, not nearest-row output.",
        ],
    }


def _profile_service_embree(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time_call(lambda: service_app.make_service_coverage_case(copies=copies))
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    last_summary_rows: tuple[dict[str, object], ...] = ()
    last_summary: dict[str, Any] = {}
    for _ in range(iterations):
        last_summary_rows, query_sec = _time_call(lambda: service_app._run_embree_gap_summary(case))
        last_summary, post_sec = _time_call(lambda: _service_summary_from_count_rows(case, last_summary_rows))
        query_samples.append(query_sec)
        postprocess_samples.append(post_sec)
    expected = service_app.run_case("embree", copies=copies, embree_summary_mode="gap_summary")
    parity = {
        "household_count": expected["household_count"],
        "clinic_count": expected["clinic_count"],
        "covered_household_count": expected["covered_household_count"],
        "uncovered_household_count": len(expected["uncovered_household_ids"]),
        "uncovered_household_ids": expected["uncovered_household_ids"],
    } == last_summary
    return {
        "summary": last_summary,
        "phase_seconds": {
            "input_build": input_sec,
            "optix_prepare": 0.0,
            "optix_query": _stats(query_samples)["median_sec"],
            "python_postprocess": _stats(postprocess_samples)["median_sec"],
        },
        "correctness_parity": parity,
        "validation": {
            "method": "compare Embree compact service-gap summary against embree gap_summary app payload",
            "copies": copies,
            "matches_reference": parity,
        },
        "notes": [
            "Embree baseline uses the compact threshold-summary path rather than row output.",
        ],
    }


def _profile_service_scipy(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time_call(lambda: service_app.make_service_coverage_case(copies=copies))
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    last_summary: dict[str, Any] = {}
    for _ in range(iterations):
        last_rows, query_sec = _time_call(lambda: service_app._run_rows("scipy", case))
        last_summary, post_sec = _time_call(lambda: _service_summary_from_rows(case, last_rows))
        query_samples.append(query_sec)
        postprocess_samples.append(post_sec)
    expected = service_app.run_case("cpu_python_reference", copies=copies)
    parity = {
        "household_count": expected["household_count"],
        "clinic_count": expected["clinic_count"],
        "covered_household_count": expected["covered_household_count"],
        "uncovered_household_count": len(expected["uncovered_household_ids"]),
        "uncovered_household_ids": expected["uncovered_household_ids"],
    } == last_summary
    return {
        "summary": last_summary,
        "phase_seconds": {
            "input_build": input_sec,
            "optix_prepare": 0.0,
            "optix_query": _stats(query_samples)["median_sec"],
            "python_postprocess": _stats(postprocess_samples)["median_sec"],
        },
        "correctness_parity": parity,
        "validation": {
            "method": "SciPy fixed-radius baseline summarized to the same compact service-gap payload",
            "copies": copies,
            "matches_reference": parity,
        },
        "notes": [
            "SciPy baseline is optional and remains bounded to the compact summary contract.",
        ],
    }


def _profile_event_cpu(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time_call(lambda: event_app.make_event_hotspot_case(copies=copies))
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    last_summary: dict[str, Any] = {}
    for _ in range(iterations):
        last_rows, query_sec = _time_call(lambda: event_app._run_rows("cpu_python_reference", case))
        last_summary, post_sec = _time_call(lambda: _event_summary_from_rows(case, last_rows))
        query_samples.append(query_sec)
        postprocess_samples.append(post_sec)
    expected = event_app.run_case("cpu_python_reference", copies=copies)
    parity = {
        "event_count": expected["event_count"],
        "hotspot_count": len(expected["hotspots"]),
        "hotspots": expected["hotspots"],
    } == last_summary
    return {
        "summary": last_summary,
        "phase_seconds": {
            "input_build": input_sec,
            "optix_prepare": 0.0,
            "optix_query": _stats(query_samples)["median_sec"],
            "python_postprocess": _stats(postprocess_samples)["median_sec"],
        },
        "correctness_parity": parity,
        "validation": {
            "method": "compare compact CPU summary against event_hotspot_screening cpu_python_reference app payload",
            "copies": copies,
            "matches_reference": parity,
        },
        "notes": [
            "CPU oracle baseline stays bounded to compact hotspot summary semantics, not neighbor-row output.",
        ],
    }


def _profile_event_embree(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time_call(lambda: event_app.make_event_hotspot_case(copies=copies))
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    last_summary_rows: tuple[dict[str, object], ...] = ()
    last_summary: dict[str, Any] = {}
    for _ in range(iterations):
        last_summary_rows, query_sec = _time_call(lambda: event_app._run_embree_count_summary(case))
        last_summary, post_sec = _time_call(lambda: _event_summary_from_count_rows(case, last_summary_rows))
        query_samples.append(query_sec)
        postprocess_samples.append(post_sec)
    expected = event_app.run_case("embree", copies=copies, embree_summary_mode="count_summary")
    parity = {
        "event_count": expected["event_count"],
        "hotspot_count": len(expected["hotspots"]),
        "hotspots": expected["hotspots"],
    } == last_summary
    return {
        "summary": last_summary,
        "phase_seconds": {
            "input_build": input_sec,
            "optix_prepare": 0.0,
            "optix_query": _stats(query_samples)["median_sec"],
            "python_postprocess": _stats(postprocess_samples)["median_sec"],
        },
        "correctness_parity": parity,
        "validation": {
            "method": "compare Embree compact hotspot summary against embree count_summary app payload",
            "copies": copies,
            "matches_reference": parity,
        },
        "notes": [
            "Embree baseline uses the compact count-summary path rather than neighbor-row output.",
        ],
    }


def _profile_event_scipy(copies: int, iterations: int) -> dict[str, Any]:
    case, input_sec = _time_call(lambda: event_app.make_event_hotspot_case(copies=copies))
    query_samples: list[float] = []
    postprocess_samples: list[float] = []
    last_rows: tuple[dict[str, object], ...] = ()
    last_summary: dict[str, Any] = {}
    for _ in range(iterations):
        last_rows, query_sec = _time_call(lambda: event_app._run_rows("scipy", case))
        last_summary, post_sec = _time_call(lambda: _event_summary_from_rows(case, last_rows))
        query_samples.append(query_sec)
        postprocess_samples.append(post_sec)
    expected = event_app.run_case("cpu_python_reference", copies=copies)
    parity = {
        "event_count": expected["event_count"],
        "hotspot_count": len(expected["hotspots"]),
        "hotspots": expected["hotspots"],
    } == last_summary
    return {
        "summary": last_summary,
        "phase_seconds": {
            "input_build": input_sec,
            "optix_prepare": 0.0,
            "optix_query": _stats(query_samples)["median_sec"],
            "python_postprocess": _stats(postprocess_samples)["median_sec"],
        },
        "correctness_parity": parity,
        "validation": {
            "method": "SciPy fixed-radius baseline summarized to the same compact hotspot payload",
            "copies": copies,
            "matches_reference": parity,
        },
        "notes": [
            "SciPy baseline is optional and remains bounded to the compact summary contract.",
        ],
    }


def build_artifact(*, app_name: str, backend: str, copies: int, iterations: int) -> dict[str, Any]:
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    if copies <= 0:
        raise ValueError("copies must be positive")

    mapping = {
        ("service_coverage_gaps", "cpu"): ("prepared_gap_summary", "cpu_oracle_summary", "cpu_oracle", _profile_service_cpu),
        ("service_coverage_gaps", "embree"): ("prepared_gap_summary", "embree_summary_path", "embree", _profile_service_embree),
        ("service_coverage_gaps", "scipy"): ("prepared_gap_summary", "scipy_baseline_when_available", "scipy", _profile_service_scipy),
        ("event_hotspot_screening", "cpu"): ("prepared_count_summary", "cpu_oracle_summary", "cpu_oracle", _profile_event_cpu),
        ("event_hotspot_screening", "embree"): ("prepared_count_summary", "embree_summary_path", "embree", _profile_event_embree),
        ("event_hotspot_screening", "scipy"): ("prepared_count_summary", "scipy_baseline_when_available", "scipy", _profile_event_scipy),
    }
    if (app_name, backend) not in mapping:
        raise ValueError(f"unsupported app/backend combination: {app_name}/{backend}")
    path_name, baseline_name, source_backend, profiler = mapping[(app_name, backend)]
    row = load_goal835_row(app=app_name, path_name=path_name, baseline_name=baseline_name)
    profile = profiler(copies, iterations)
    return build_baseline_artifact(
        row=row,
        baseline_name=baseline_name,
        source_backend=source_backend,
        benchmark_scale={"copies": copies, "iterations": iterations},
        repeated_runs=iterations,
        correctness_parity=profile["correctness_parity"],
        phase_seconds=profile["phase_seconds"],
        summary=profile["summary"],
        notes=profile["notes"],
        validation=profile["validation"],
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write Goal835-valid local spatial prepared-summary baseline artifacts.")
    parser.add_argument("--app", choices=("service_coverage_gaps", "event_hotspot_screening"), required=True)
    parser.add_argument("--backend", choices=("cpu", "embree", "scipy"), required=True)
    parser.add_argument("--copies", type=int, default=20000)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args(argv)
    artifact = build_artifact(
        app_name=args.app,
        backend=args.backend,
        copies=args.copies,
        iterations=args.iterations,
    )
    write_baseline_artifact(args.output_json, artifact)
    print(json.dumps(artifact, indent=2, sort_keys=True))
    return 0 if artifact["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
