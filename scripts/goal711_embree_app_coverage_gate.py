#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

APP_COMMANDS = (
    ("database_analytics", ("examples/rtdl_database_analytics_app.py",)),
    ("graph_analytics", ("examples/rtdl_graph_analytics_app.py",)),
    ("service_coverage_gaps", ("examples/rtdl_service_coverage_gaps.py", "--copies", "16")),
    ("event_hotspot_screening", ("examples/rtdl_event_hotspot_screening.py", "--copies", "16")),
    ("facility_knn_assignment", ("examples/rtdl_facility_knn_assignment.py", "--copies", "16")),
    ("road_hazard_screening", ("examples/rtdl_road_hazard_screening.py",)),
    ("segment_polygon_hitcount", ("examples/rtdl_segment_polygon_hitcount.py",)),
    (
        "segment_polygon_anyhit_rows",
        ("examples/rtdl_segment_polygon_anyhit_rows.py", "--output-mode", "segment_counts"),
    ),
    ("polygon_pair_overlap_area_rows", ("examples/rtdl_polygon_pair_overlap_area_rows.py",)),
    ("polygon_set_jaccard", ("examples/rtdl_polygon_set_jaccard.py",)),
    ("hausdorff_distance", ("examples/rtdl_hausdorff_distance_app.py", "--copies", "16")),
    ("ann_candidate_search", ("examples/rtdl_ann_candidate_app.py", "--copies", "16")),
    ("outlier_detection", ("examples/rtdl_outlier_detection_app.py", "--copies", "16")),
    ("dbscan_clustering", ("examples/rtdl_dbscan_clustering_app.py", "--copies", "16")),
    (
        "robot_collision_screening",
        ("examples/rtdl_robot_collision_screening_app.py", "--output-mode", "hit_count"),
    ),
    ("barnes_hut_force", ("examples/rtdl_barnes_hut_force_app.py",)),
)


def _run_command(app: str, base_args: tuple[str, ...], backend: str, timeout: float) -> dict[str, object]:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT / 'src'}:{ROOT}"
    env.setdefault("RTDL_EMBREE_THREADS", "auto")
    command = [sys.executable, *base_args, "--backend", backend]
    start = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    elapsed = time.perf_counter() - start
    json_valid = False
    payload_app = None
    payload_backend = None
    canonical_sha256 = None
    if completed.returncode == 0:
        try:
            payload = json.loads(completed.stdout)
            json_valid = isinstance(payload, dict)
            payload_app = payload.get("app")
            payload_backend = payload.get("backend") or payload.get("requested_backend")
            canonical = json.dumps(_canonical_payload(payload), sort_keys=True, separators=(",", ":"))
            canonical_sha256 = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        except json.JSONDecodeError:
            json_valid = False
    return {
        "app": app,
        "backend": backend,
        "command": command,
        "returncode": completed.returncode,
        "elapsed_sec": elapsed,
        "json_valid": json_valid,
        "payload_app": payload_app,
        "payload_backend": payload_backend,
        "canonical_sha256": canonical_sha256,
        "stdout_head": completed.stdout[:512],
        "stderr_head": completed.stderr[:512],
    }


def _canonical_payload(value):
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
            }
        }
    if isinstance(value, list):
        items = [_canonical_payload(item) for item in value]
        return sorted(items, key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    if isinstance(value, float):
        return round(value, 12)
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal", type=int, default=711)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    runs = []
    for app, base_args in APP_COMMANDS:
        runs.append(_run_command(app, base_args, "cpu_python_reference", args.timeout))
        runs.append(_run_command(app, base_args, "embree", args.timeout))

    by_app = {}
    for app, _ in APP_COMMANDS:
        cpu = next(item for item in runs if item["app"] == app and item["backend"] == "cpu_python_reference")
        embree = next(item for item in runs if item["app"] == app and item["backend"] == "embree")
        by_app[app] = {
            "cpu_python_reference_ok": cpu["returncode"] == 0 and cpu["json_valid"],
            "embree_ok": embree["returncode"] == 0 and embree["json_valid"],
            "canonical_payload_match": cpu["canonical_sha256"] == embree["canonical_sha256"],
            "cpu_python_reference_elapsed_sec": cpu["elapsed_sec"],
            "embree_elapsed_sec": embree["elapsed_sec"],
            "embree_vs_cpu_elapsed_ratio": (
                embree["elapsed_sec"] / cpu["elapsed_sec"] if cpu["elapsed_sec"] > 0.0 else None
            ),
        }

    payload = {
        "goal": args.goal,
        "commands_valid": all(item["returncode"] == 0 and item["json_valid"] for item in runs),
        "thread_policy": "RTDL_EMBREE_THREADS=auto unless externally overridden",
        "app_count": len(APP_COMMANDS),
        "run_count": len(runs),
        "canonical_payloads_match": all(item["canonical_payload_match"] for item in by_app.values()),
        "by_app": by_app,
        "runs": runs,
    }
    payload["valid"] = bool(payload["commands_valid"] and payload["canonical_payloads_match"])
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
