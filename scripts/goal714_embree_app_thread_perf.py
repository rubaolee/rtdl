#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AppCase:
    app: str
    args: tuple[str, ...]
    group: str
    scalable: bool
    boundary: str


APP_CASES: tuple[AppCase, ...] = (
    AppCase("database_analytics", ("examples/rtdl_database_analytics_app.py",), "db", False, "small public app fixture"),
    AppCase("graph_analytics", ("examples/rtdl_graph_analytics_app.py",), "graph", False, "small public app fixture"),
    AppCase(
        "service_coverage_gaps",
        ("examples/rtdl_service_coverage_gaps.py", "--copies", "{copies}"),
        "spatial_point",
        True,
        "copy-scaled fixed-radius app fixture",
    ),
    AppCase(
        "event_hotspot_screening",
        ("examples/rtdl_event_hotspot_screening.py", "--copies", "{copies}"),
        "spatial_point",
        True,
        "copy-scaled fixed-radius app fixture",
    ),
    AppCase(
        "facility_knn_assignment",
        ("examples/rtdl_facility_knn_assignment.py", "--copies", "{copies}"),
        "spatial_point",
        True,
        "copy-scaled KNN app fixture",
    ),
    AppCase("road_hazard_screening", ("examples/rtdl_road_hazard_screening.py",), "segment_polygon", False, "small public app fixture"),
    AppCase("segment_polygon_hitcount", ("examples/rtdl_segment_polygon_hitcount.py",), "segment_polygon", False, "small public app fixture"),
    AppCase(
        "segment_polygon_anyhit_rows",
        ("examples/rtdl_segment_polygon_anyhit_rows.py", "--output-mode", "segment_counts"),
        "segment_polygon",
        False,
        "small public app fixture in compact output mode",
    ),
    AppCase(
        "polygon_pair_overlap_area_rows",
        ("examples/rtdl_polygon_pair_overlap_area_rows.py",),
        "polygon_overlap",
        False,
        "native-assisted candidate discovery plus CPU exact area refinement",
    ),
    AppCase(
        "polygon_set_jaccard",
        ("examples/rtdl_polygon_set_jaccard.py",),
        "polygon_overlap",
        False,
        "native-assisted candidate discovery plus CPU exact Jaccard refinement",
    ),
    AppCase(
        "hausdorff_distance",
        ("examples/rtdl_hausdorff_distance_app.py", "--copies", "{copies}"),
        "spatial_point",
        True,
        "copy-scaled nearest-neighbor app fixture",
    ),
    AppCase(
        "ann_candidate_search",
        ("examples/rtdl_ann_candidate_app.py", "--copies", "{copies}"),
        "spatial_point",
        True,
        "copy-scaled KNN app fixture",
    ),
    AppCase(
        "outlier_detection",
        ("examples/rtdl_outlier_detection_app.py", "--copies", "{copies}"),
        "spatial_point",
        True,
        "copy-scaled fixed-radius app fixture",
    ),
    AppCase(
        "dbscan_clustering",
        ("examples/rtdl_dbscan_clustering_app.py", "--copies", "{copies}"),
        "spatial_point",
        True,
        "copy-scaled fixed-radius app fixture plus Python cluster expansion",
    ),
    AppCase(
        "robot_collision_screening",
        ("examples/rtdl_robot_collision_screening_app.py", "--output-mode", "hit_count"),
        "ray",
        False,
        "small public app fixture in compact output mode",
    ),
    AppCase("barnes_hut_force", ("examples/rtdl_barnes_hut_force_app.py",), "spatial_point", False, "small public app fixture"),
)


def _format_args(args: tuple[str, ...], copies: int) -> list[str]:
    return [item.format(copies=str(copies)) for item in args]


def _canonical_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _canonical_payload(item)
            for key, item in value.items()
            if key
            not in {
                "backend",
                "requested_backend",
                "data_flow",
                "prepared_dataset",
                "backend_mode",
                "candidate_row_count",
                "embree_performance",
                "optix_performance",
            }
        }
    if isinstance(value, list):
        items = [_canonical_payload(item) for item in value]
        return sorted(items, key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    if isinstance(value, float):
        return round(value, 12)
    return value


def _payload_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(_canonical_payload(payload), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _python_env(threads: str | None) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join((str(ROOT / "src"), str(ROOT)))
    if threads is not None:
        env["RTDL_EMBREE_THREADS"] = threads
    return env


def _effective_threads(requested: str) -> int:
    if requested.strip().lower() == "auto":
        return max(1, os.cpu_count() or 1)
    return int(requested)


def _run_once(case: AppCase, backend: str, copies: int, threads: str | None, timeout: float) -> dict[str, Any]:
    command = [sys.executable, *_format_args(case.args, copies), "--backend", backend]
    start = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=_python_env(threads),
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    elapsed = time.perf_counter() - start
    payload: dict[str, Any] | None = None
    error: str | None = None
    if completed.returncode == 0:
        try:
            loaded = json.loads(completed.stdout)
            if isinstance(loaded, dict):
                payload = loaded
            else:
                error = "stdout_json_not_object"
        except json.JSONDecodeError as exc:
            error = f"json_decode_error: {exc}"
    else:
        error = f"returncode_{completed.returncode}"
    return {
        "command": command,
        "elapsed_sec": elapsed,
        "returncode": completed.returncode,
        "json_valid": payload is not None,
        "payload": payload,
        "payload_hash": _payload_hash(payload) if payload is not None else None,
        "stdout_head": completed.stdout[:512],
        "stderr_head": completed.stderr[:512],
        "error": error,
    }


def _measure_embree_case(
    case: AppCase,
    cpu_hash: str | None,
    copies: int,
    thread_value: str,
    warmups: int,
    min_sample_sec: float,
    max_repeats: int,
    timeout: float,
) -> dict[str, Any]:
    warmup_errors: list[str | None] = []
    for _ in range(warmups):
        warmup = _run_once(case, "embree", copies, thread_value, timeout)
        warmup_errors.append(warmup["error"])
        if warmup["returncode"] != 0 or not warmup["json_valid"]:
            break
    samples: list[float] = []
    hashes: list[str | None] = []
    errors: list[str | None] = []
    total = 0.0
    repeats = 0
    while not any(warmup_errors) and repeats < max_repeats and (repeats == 0 or total < min_sample_sec):
        result = _run_once(case, "embree", copies, thread_value, timeout)
        repeats += 1
        samples.append(float(result["elapsed_sec"]))
        total += float(result["elapsed_sec"])
        hashes.append(result["payload_hash"])
        errors.append(result["error"])
        if result["returncode"] != 0 or not result["json_valid"]:
            break
    ok = all(error is None for error in warmup_errors) and all(error is None for error in errors)
    parity = ok and cpu_hash is not None and all(item == cpu_hash for item in hashes)
    return {
        "threads": thread_value,
        "effective_threads": _effective_threads(thread_value),
        "ok": ok,
        "canonical_payload_match": parity,
        "warmups": warmups,
        "warmup_errors": [error for error in warmup_errors if error is not None],
        "repeat_count": repeats,
        "samples_sec": samples,
        "total_sample_sec": total,
        "median_sec": statistics.median(samples) if samples else None,
        "min_sec": min(samples) if samples else None,
        "max_sec": max(samples) if samples else None,
        "errors": [error for error in errors if error is not None],
    }


def _select_cases(apps: str, groups: str) -> list[AppCase]:
    app_filter = {item.strip() for item in apps.split(",") if item.strip()}
    group_filter = {item.strip() for item in groups.split(",") if item.strip()}
    selected = []
    for case in APP_CASES:
        if app_filter and "all" not in app_filter and case.app not in app_filter:
            continue
        if group_filter and "all" not in group_filter and case.group not in group_filter:
            continue
        selected.append(case)
    return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal", type=int, default=714)
    parser.add_argument("--host-label", default=platform.node() or platform.system())
    parser.add_argument("--apps", default="all", help="comma-separated app names or all")
    parser.add_argument("--groups", default="all", help="comma-separated groups or all")
    parser.add_argument("--copies", type=int, default=256)
    parser.add_argument("--threads", default="1,auto")
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--min-sample-sec", type=float, default=0.2)
    parser.add_argument("--max-repeats", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    selected = _select_cases(args.apps, args.groups)
    thread_values = [item.strip() for item in args.threads.split(",") if item.strip()]
    payload: dict[str, Any] = {
        "goal": args.goal,
        "host": {
            "label": args.host_label,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python": sys.version.split()[0],
            "os_cpu_count": os.cpu_count(),
        },
        "methodology": {
            "copies_for_scalable_apps": args.copies,
            "threads": thread_values,
            "warmups_before_sample_window": args.warmups,
            "min_sample_sec": args.min_sample_sec,
            "max_repeats": args.max_repeats,
            "timeout_sec": args.timeout,
            "boundary": (
                "This is app-level wall-clock timing. It includes Python CLI startup, JSON "
                "materialization, and app postprocess; it is not pure native traversal timing."
            ),
        },
        "apps": [],
    }
    valid = True
    for case in selected:
        copies = args.copies if case.scalable else 1
        cpu = _run_once(case, "cpu_python_reference", copies, None, args.timeout)
        app_result: dict[str, Any] = {
            "app": case.app,
            "group": case.group,
            "scalable": case.scalable,
            "copies": copies,
            "boundary": case.boundary,
            "cpu_reference": {
                "ok": cpu["returncode"] == 0 and cpu["json_valid"],
                "elapsed_sec": cpu["elapsed_sec"],
                "payload_hash": cpu["payload_hash"],
                "error": cpu["error"],
            },
            "embree": [],
        }
        cpu_hash = cpu["payload_hash"] if app_result["cpu_reference"]["ok"] else None
        for thread_value in thread_values:
            app_result["embree"].append(
                _measure_embree_case(
                    case,
                    cpu_hash,
                    copies,
                    thread_value,
                    args.warmups,
                    args.min_sample_sec,
                    args.max_repeats,
                    args.timeout,
                )
            )
        baseline = next((item for item in app_result["embree"] if item["threads"] == "1"), None)
        if baseline and baseline["median_sec"]:
            base = float(baseline["median_sec"])
            for item in app_result["embree"]:
                item["speedup_vs_1_thread"] = base / float(item["median_sec"]) if item["median_sec"] else None
        app_valid = bool(
            app_result["cpu_reference"]["ok"]
            and all(item["ok"] and item["canonical_payload_match"] for item in app_result["embree"])
        )
        app_result["valid"] = app_valid
        valid = valid and app_valid
        payload["apps"].append(app_result)
    payload["valid"] = valid

    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
