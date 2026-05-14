#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2037_embree_cpu_partner_all_thread_local_linux"


def _cmd(app: str, continuation: str, *args: str, timeout_sec: int = 900, smoke_timeout_sec: int = 180) -> dict[str, Any]:
    return {
        "app": app,
        "backend": "embree",
        "cpu_partner_continuation": continuation,
        "command": [sys.executable, *args],
        "timeout_sec": timeout_sec,
        "smoke_timeout_sec": smoke_timeout_sec,
    }


ROWS: tuple[dict[str, Any], ...] = (
    _cmd("database_analytics", "numpy-columnar-predicate-reduction-target", "examples/rtdl_database_analytics_app.py", "--backend", "embree", "--copies", "20000", "--output-mode", "compact_summary"),
    _cmd("graph_analytics", "numpy-or-numba-graph-continuation-target", "examples/rtdl_graph_analytics_app.py", "--backend", "embree", "--scenario", "visibility_edges", "--copies", "20000", "--output-mode", "summary"),
    _cmd("service_coverage_gaps", "numpy-threshold-count-target", "examples/rtdl_service_coverage_gaps.py", "--backend", "embree", "--copies", "20000", "--embree-summary-mode", "gap_summary"),
    _cmd("event_hotspot_screening", "numpy-threshold-count-target", "examples/rtdl_event_hotspot_screening.py", "--backend", "embree", "--copies", "20000", "--embree-summary-mode", "count_summary"),
    _cmd("facility_knn_assignment", "generic-prepared-fixed-radius-threshold-count-target", "examples/rtdl_facility_knn_assignment.py", "--backend", "embree", "--copies", "20000", "--output-mode", "summary", "--optix-summary-mode", "coverage_threshold_prepared"),
    _cmd("road_hazard_screening", "numpy-grouped-count-flags-target", "examples/rtdl_road_hazard_screening.py", "--backend", "embree", "--copies", "20000", "--output-mode", "summary"),
    _cmd("segment_polygon_hitcount", "numpy-grouped-count-target", "examples/rtdl_segment_polygon_hitcount.py", "--backend", "embree", "--copies", "512"),
    _cmd("segment_polygon_anyhit_rows", "numpy-compact-row-materialization-target", "examples/rtdl_segment_polygon_anyhit_rows.py", "--backend", "embree", "--copies", "512", "--output-mode", "rows", "--output-capacity", "8192"),
    _cmd("polygon_pair_overlap_area_rows", "cpu-partner-bbox-candidate-plus-native-exact-summary-target", "examples/rtdl_polygon_pair_overlap_area_rows.py", "--backend", "embree", "--copies", "20000", "--output-mode", "summary", "--candidate-mode", "partner_bbox"),
    _cmd("polygon_set_jaccard", "cpu-partner-bbox-candidate-plus-native-jaccard-summary-target", "examples/rtdl_polygon_set_jaccard.py", "--backend", "embree", "--copies", "2000", "--output-mode", "summary", "--candidate-mode", "partner_bbox"),
    _cmd("hausdorff_distance", "generic-prepared-fixed-radius-threshold-count-target", "examples/rtdl_hausdorff_distance_app.py", "--backend", "embree", "--copies", "20000", "--optix-summary-mode", "directed_threshold_prepared"),
    _cmd("ann_candidate_search", "generic-prepared-fixed-radius-threshold-count-target", "examples/rtdl_ann_candidate_app.py", "--backend", "embree", "--copies", "20000", "--output-mode", "rerank_summary", "--optix-summary-mode", "candidate_threshold_prepared"),
    _cmd("outlier_detection", "numpy-threshold-count-target", "examples/rtdl_outlier_detection_app.py", "--backend", "embree", "--copies", "20000", "--output-mode", "density_count"),
    _cmd("dbscan_clustering", "numpy-threshold-count-target", "examples/rtdl_dbscan_clustering_app.py", "--backend", "embree", "--copies", "20000", "--output-mode", "core_count"),
    _cmd("robot_collision_screening", "numpy-compact-flag-target", "examples/rtdl_robot_collision_screening_app.py", "--backend", "embree", "--pose-count", "20000", "--obstacle-count", "1024", "--output-mode", "hit_count"),
    _cmd("barnes_hut_force_app", "numpy-or-numba-node-coverage-target", "examples/rtdl_barnes_hut_force_app.py", "--backend", "embree", "--body-count", "200000", "--output-mode", "candidate_summary"),
)


def _progress(message: str) -> None:
    print(f"[goal2037-embree-cpu] {message}", flush=True)


def _logical_cpu_count() -> int:
    try:
        completed = subprocess.run(["nproc"], check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        value = int(completed.stdout.strip())
        if value > 0:
            return value
    except Exception:
        pass
    return os.cpu_count() or 1


def _git_commit() -> str:
    completed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return completed.stdout.strip() or "unknown"


def _module_version(module_name: str) -> str | None:
    try:
        module = __import__(module_name)
        return str(getattr(module, "__version__", "unknown"))
    except Exception:
        return None


def environment_packet(thread_count: int) -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "python": sys.version,
        "logical_cpu_count": thread_count,
        "machine": platform.machine(),
        "processor": platform.processor(),
        "git_commit": _git_commit(),
        "tools": {
            "nproc": shutil.which("nproc"),
            "make": shutil.which("make"),
            "gcc": shutil.which("gcc"),
            "g++": shutil.which("g++"),
        },
        "python_modules": {
            "numpy": _module_version("numpy"),
            "torch": _module_version("torch"),
            "numba": _module_version("numba"),
        },
        "thread_env": {
            "OMP_NUM_THREADS": str(thread_count),
            "TBB_NUM_THREADS": str(thread_count),
            "MKL_NUM_THREADS": str(thread_count),
            "OPENBLAS_NUM_THREADS": str(thread_count),
            "NUMEXPR_NUM_THREADS": str(thread_count),
            "RTDL_EMBREE_THREADS": str(thread_count),
        },
    }


def _row_with_scale(row: dict[str, Any], scale: str) -> dict[str, Any]:
    if scale == "large" and row["app"] == "robot_collision_screening":
        return {**row, "command": [*row["command"], "--skip-validation"]}
    if scale != "smoke":
        return row
    command = list(row["command"])
    replacements = {
        "--copies": "128",
        "--body-count": "4096",
        "--pose-count": "512",
        "--obstacle-count": "128",
        "--output-capacity": "2048",
    }
    for index, part in enumerate(command[:-1]):
        if part in replacements:
            command[index + 1] = replacements[part]
    return {**row, "command": command, "timeout_sec": row["smoke_timeout_sec"]}


def run_row(row: dict[str, Any], *, artifact_dir: Path, env: dict[str, str], repeats: int) -> dict[str, Any]:
    row_dir = artifact_dir / "rows"
    row_dir.mkdir(parents=True, exist_ok=True)
    row_artifact = row_dir / f"{row['app']}.json"
    timings: list[float] = []
    attempts: list[dict[str, Any]] = []
    parsed_payload: dict[str, Any] | None = None
    status = "pass"
    for repeat in range(repeats):
        _progress(f"start app={row['app']} repeat={repeat + 1}/{repeats} continuation={row['cpu_partner_continuation']}")
        start = time.perf_counter()
        try:
            completed = subprocess.run(
                row["command"],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=int(row["timeout_sec"]),
                check=False,
            )
            elapsed = time.perf_counter() - start
            timings.append(elapsed)
            parsed = None
            if completed.returncode == 0:
                try:
                    parsed = json.loads(completed.stdout)
                    parsed_payload = parsed
                except json.JSONDecodeError:
                    parsed = None
            if completed.returncode != 0 or parsed is None:
                status = "failed"
            attempts.append(
                {
                    "repeat": repeat + 1,
                    "elapsed_sec": elapsed,
                    "returncode": completed.returncode,
                    "stdout_json": parsed is not None,
                    "stdout_tail": "" if parsed is not None else completed.stdout[-2000:],
                    "stderr_tail": completed.stderr[-2000:],
                }
            )
            _progress(f"done app={row['app']} repeat={repeat + 1}/{repeats} rc={completed.returncode} json={parsed is not None} elapsed_s={elapsed:.6f}")
        except subprocess.TimeoutExpired as exc:
            elapsed = time.perf_counter() - start
            timings.append(elapsed)
            status = "timeout"
            attempts.append(
                {
                    "repeat": repeat + 1,
                    "elapsed_sec": elapsed,
                    "returncode": None,
                    "timeout": True,
                    "stdout_json": False,
                    "stdout_tail": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "",
                    "stderr_tail": (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else "",
                }
            )
            _progress(f"timeout app={row['app']} repeat={repeat + 1}/{repeats} elapsed_s={elapsed:.6f}")
            break
    timing = {
        "min_s": min(timings) if timings else None,
        "median_s": sorted(timings)[len(timings) // 2] if timings else None,
        "max_s": max(timings) if timings else None,
    }
    payload = {
        "app": row["app"],
        "backend": row["backend"],
        "cpu_partner_continuation": row["cpu_partner_continuation"],
        "command": row["command"],
        "timeout_sec": row["timeout_sec"],
        "repeats": repeats,
        "status": status,
        "timing": timing,
        "attempts": attempts,
        "last_payload_summary_keys": sorted(parsed_payload.keys()) if isinstance(parsed_payload, dict) else [],
        "claim_boundary": {
            "v2_0_release_authorized": False,
            "true_host_zero_copy_authorized": False,
            "broad_speedup_claim_authorized": False,
        },
    }
    row_artifact.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload | {"artifact": str(row_artifact.relative_to(ROOT))}


def build_summary(*, artifact_dir: Path, rows: list[dict[str, Any]], environment: dict[str, Any], scale: str) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    continuation_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
        continuation = row["cpu_partner_continuation"]
        continuation_counts[continuation] = continuation_counts.get(continuation, 0) + 1
    return {
        "goal": "Goal2037",
        "status": "embree-cpu-partner-local-linux-artifact",
        "scale": scale,
        "environment": environment,
        "row_count": len(rows),
        "status_counts": status_counts,
        "continuation_counts": continuation_counts,
        "rows": rows,
        "claim_boundary": {
            "v2_0_release_authorized": False,
            "true_host_zero_copy_for_every_row_authorized": False,
            "broad_all_app_speedup_claim_authorized": False,
        },
        "artifact_dir": str(artifact_dir.relative_to(ROOT)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run v2.0 Embree CPU-partner all-thread local Linux matrix.")
    parser.add_argument("--artifact-dir", default=str(DEFAULT_ARTIFACT_DIR))
    parser.add_argument("--scale", choices=("smoke", "large"), default="smoke")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--apps", default="all")
    args = parser.parse_args()

    if args.repeats <= 0:
        raise ValueError("--repeats must be positive")
    artifact_dir = Path(args.artifact_dir)
    if not artifact_dir.is_absolute():
        artifact_dir = ROOT / artifact_dir
    artifact_dir.mkdir(parents=True, exist_ok=True)
    selected = list(ROWS) if args.apps == "all" else [row for row in ROWS if row["app"] in set(args.apps.split(","))]
    if not selected:
        raise ValueError("no matching apps selected")

    thread_count = _logical_cpu_count()
    environment = environment_packet(thread_count)
    env = os.environ.copy()
    env["PYTHONPATH"] = "src:."
    env["LD_LIBRARY_PATH"] = str(ROOT / "build") + ":" + env.get("LD_LIBRARY_PATH", "")
    env.update(environment["thread_env"])

    (artifact_dir / "environment.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _progress(f"environment logical_cpu_count={thread_count} scale={args.scale} repeats={args.repeats} apps={len(selected)}")
    rows = [
        run_row(_row_with_scale(row, args.scale), artifact_dir=artifact_dir, env=env, repeats=args.repeats)
        for row in selected
    ]
    summary = build_summary(artifact_dir=artifact_dir, rows=rows, environment=environment, scale=args.scale)
    (artifact_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
